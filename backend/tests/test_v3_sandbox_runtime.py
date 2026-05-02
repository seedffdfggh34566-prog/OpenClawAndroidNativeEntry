from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.api.config import reset_settings_cache
from backend.api.database import get_session_factory, init_db, reset_database_state
from backend.api.models import (
    V3SandboxCoreMemoryBlockTransitionEventRecord,
    V3SandboxMessageRecord,
    V3SandboxTraceEventRecord,
)
from backend.runtime.llm_client import (
    TokenHubClientError,
    TokenHubCompletion,
    TokenHubToolCall,
    TokenHubToolCallFunction,
)
from backend.runtime.v3_sandbox import (
    DatabaseV3SandboxStore,
    InMemoryV3SandboxStore,
    JsonFileV3SandboxStore,
    V3SandboxStoreConfigError,
    run_v3_sandbox_turn,
)
from backend.runtime.v3_sandbox.graph import _build_tool_loop_messages
from backend.runtime.v3_sandbox.schemas import (
    CoreMemoryBlock,
    V3SandboxMessage,
    V3SandboxSession,
    default_core_memory_blocks,
)


def test_json_store_round_trips_session(tmp_path: Path) -> None:
    store = JsonFileV3SandboxStore(tmp_path)
    blocks = default_core_memory_blocks()
    blocks["product"] = blocks["product"].model_copy(update={"value": "产品是销售助手。"})
    session = V3SandboxSession(id="v3s_json", core_memory_blocks=blocks)

    store.create_session(session)
    reloaded = JsonFileV3SandboxStore(tmp_path).get_session("v3s_json")

    assert reloaded.id == session.id
    assert reloaded.core_memory_blocks["product"].value == "产品是销售助手。"


def test_database_store_round_trips_session_and_normalized_events(tmp_path, monkeypatch) -> None:
    from backend.api.config import get_settings

    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    reset_database_state()
    init_db()

    first = run_v3_sandbox_turn(
        settings=get_settings(),
        session=V3SandboxSession(id="v3s_db_store"),
        user_message=V3SandboxMessage(id="msg_user_1", role="user", content="我们做中小企业财税 SaaS。"),
        client=_SequenceLlmClient([_product_turn_calls()]),
    )
    second = run_v3_sandbox_turn(
        settings=get_settings(),
        session=first.session,
        user_message=V3SandboxMessage(id="msg_user_2", role="user", content="我的客户是谁？"),
        client=_SequenceLlmClient([_hypothesis_turn_calls()]),
    )
    third = run_v3_sandbox_turn(
        settings=get_settings(),
        session=second.session,
        user_message=V3SandboxMessage(id="msg_user_3", role="user", content="纠正一下，不是财务负责人，是老板本人。"),
        client=_SequenceLlmClient([_correction_turn_calls()]),
    )

    store = DatabaseV3SandboxStore()
    store.save_session(third.session)
    store.save_session(third.session)

    reloaded = DatabaseV3SandboxStore().get_session("v3s_db_store")
    assert "产品是中小企业财税 SaaS" in reloaded.core_memory_blocks["product"].value
    assert "目标联系人是老板本人" in reloaded.core_memory_blocks["customer_intelligence"].value

    with get_session_factory()() as db:
        assert db.query(V3SandboxMessageRecord).filter_by(session_id="v3s_db_store").count() == 6
        assert db.query(V3SandboxTraceEventRecord).filter_by(session_id="v3s_db_store").count() == 3
        core_transitions = db.query(V3SandboxCoreMemoryBlockTransitionEventRecord).filter_by(session_id="v3s_db_store").all()
        assert len(core_transitions) >= 3
        assert {item.tool_name for item in core_transitions} >= {"core_memory_append"}

    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_store_backend_config_precedence(tmp_path, monkeypatch) -> None:
    from backend.api.v3_sandbox import create_v3_sandbox_store

    monkeypatch.delenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", raising=False)
    monkeypatch.delenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_DIR", raising=False)
    reset_settings_cache()
    assert isinstance(create_v3_sandbox_store(), InMemoryV3SandboxStore)

    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_DIR", str(tmp_path / "json"))
    reset_settings_cache()
    assert isinstance(create_v3_sandbox_store(), JsonFileV3SandboxStore)

    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", "memory")
    reset_settings_cache()
    assert isinstance(create_v3_sandbox_store(), InMemoryV3SandboxStore)

    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", "json")
    reset_settings_cache()
    assert isinstance(create_v3_sandbox_store(), JsonFileV3SandboxStore)

    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", "database")
    reset_settings_cache()
    assert isinstance(create_v3_sandbox_store(), DatabaseV3SandboxStore)

    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", "bad")
    reset_settings_cache()
    with pytest.raises(V3SandboxStoreConfigError):
        create_v3_sandbox_store()

    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_store_inspection_api_is_safe_across_backends(tmp_path, monkeypatch) -> None:
    from backend.api.main import create_app

    monkeypatch.delenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", raising=False)
    monkeypatch.delenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_DIR", raising=False)
    reset_settings_cache()
    reset_database_state()
    with TestClient(create_app()) as client:
        memory_payload = client.get("/v3/sandbox/store").json()
    assert memory_payload == {
        "backend": "memory",
        "database_enabled": False,
        "json_enabled": False,
        "transition_events_supported": False,
    }

    store_dir = tmp_path / "json-store"
    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", "json")
    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_DIR", str(store_dir))
    reset_settings_cache()
    reset_database_state()
    with TestClient(create_app()) as client:
        json_payload = client.get("/v3/sandbox/store").json()
    assert json_payload["backend"] == "json"
    assert str(store_dir) not in json.dumps(json_payload)

    db_url = f"sqlite:///{tmp_path / 'inspect.db'}"
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", db_url)
    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", "database")
    monkeypatch.delenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_DIR", raising=False)
    reset_settings_cache()
    reset_database_state()
    with TestClient(create_app()) as client:
        db_payload = client.get("/v3/sandbox/store").json()
    assert db_payload["backend"] == "database"
    assert db_payload["database_enabled"] is True
    assert db_url not in json.dumps(db_payload)

    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_runtime_config_api_is_safe_and_mutable(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'safe.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", "database")
    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_DIR", str(tmp_path / "json-store"))
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    reset_database_state()

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        initial = client.get("/v3/sandbox/runtime-config")
        assert initial.status_code == 200
        initial_payload = initial.json()
        dumped = json.dumps(initial_payload)
        assert "test-key" not in dumped
        assert str(tmp_path / "safe.db") not in dumped
        assert str(tmp_path / "json-store") not in dumped
        assert initial_payload["backend_status"]["llm_api_key_status"] == "configured"
        assert initial_payload["backend_status"]["llm_model"] == "minimax-m2.7"
        assert initial_payload["backend_status"]["native_fc_supported"] is True
        assert initial_payload["danger_readonly"]["database_url_status"] == "configured"
        assert "minimax-m2.7" in initial_payload["allowlists"]["llm_models"]
        assert "deepseek-v3.1" not in initial_payload["allowlists"]["llm_models"]
        assert "deepseek-r1" not in initial_payload["allowlists"]["llm_models"]
        assert initial_payload["native_fc"]["default_model"] == "minimax-m2.7"
        assert initial_payload["native_fc"]["effective_model_policy"]["recommended_role"] == "default"
        assert initial_payload["native_fc"]["model_policies"]["kimi-k2.6"]["thinking_policy"]

        updated = client.patch(
            "/v3/sandbox/runtime-config",
            json={
                "llm_model": "deepseek-v4-flash",
                "llm_timeout_seconds": 180,
                "default_debug_trace": True,
                "default_include_prompt": True,
                "default_include_raw_llm_output": True,
                "default_include_state_diff": True,
                "replay_debug_trace": True,
                "trace_max_bytes": 200_000,
            },
        )
        assert updated.status_code == 200
        runtime_config = updated.json()["runtime_config"]
        assert runtime_config["llm_model"] == "deepseek-v4-flash"
        assert runtime_config["llm_timeout_seconds"] == 180
        assert runtime_config["default_debug_trace"] is True
        assert runtime_config["trace_max_bytes"] == 200_000
        assert updated.json()["native_fc"]["effective_model_policy"]["recommended_role"] == "low_cost"

        reset = client.post("/v3/sandbox/runtime-config/reset")
        assert reset.status_code == 200
        reset_config = reset.json()["runtime_config"]
        assert reset_config["llm_model"] == "minimax-m2.7"
        assert reset_config["default_debug_trace"] is False
        assert reset_config["replay_debug_trace"] is False

    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_runtime_config_rejects_unsupported_values(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    reset_settings_cache()
    reset_database_state()

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        bad_model = client.patch("/v3/sandbox/runtime-config", json={"llm_model": "bad-model"})
        retired_model = client.patch("/v3/sandbox/runtime-config", json={"llm_model": "deepseek-v3.1"})
        bad_timeout = client.patch("/v3/sandbox/runtime-config", json={"llm_timeout_seconds": 30})
        bad_max_bytes = client.patch("/v3/sandbox/runtime-config", json={"trace_max_bytes": 1_000})

    assert bad_model.status_code == 422
    assert retired_model.status_code == 422
    assert bad_timeout.status_code == 422
    assert bad_max_bytes.status_code == 422
    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_runtime_config_defaults_debug_trace_for_turns(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    reset_database_state()
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete_with_tools",
        _SequenceLlmClient([_product_turn_calls()]).complete_with_tools,
    )

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        assert client.post("/v3/sandbox/sessions", json={"session_id": "v3s_runtime_config_debug"}).status_code == 201
        assert (
            client.patch(
                "/v3/sandbox/runtime-config",
                json={
                    "default_debug_trace": True,
                    "default_include_prompt": True,
                    "default_include_raw_llm_output": True,
                    "default_include_state_diff": True,
                    "trace_max_bytes": 200_000,
                },
            ).status_code
            == 200
        )
        response = client.post(
            "/v3/sandbox/sessions/v3s_runtime_config_debug/turns",
            json={"content": "我们做中小企业财税 SaaS。"},
        )

    assert response.status_code == 200
    debug_trace = response.json()["trace_event"]["debug_trace"]
    assert debug_trace is not None
    call_llm = next(event for event in debug_trace["events"] if event["node"] == "call_agent_with_tools")
    assert "messages" in call_llm
    assert "raw_output" in call_llm
    execute_tools = next(event for event in debug_trace["events"] if event["node"] == "execute_tool_calls")
    assert "state_diff" in execute_tools
    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_runtime_config_can_trace_replay(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    reset_database_state()
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete_with_tools",
        _SequenceLlmClient([_product_turn_calls(), _correction_turn_calls()]).complete_with_tools,
    )

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        seed = client.post("/v3/sandbox/demo-seeds", json={"scenario": "sales_training_correction"}).json()["session"]
        assert (
            client.patch(
                "/v3/sandbox/runtime-config",
                json={
                    "replay_debug_trace": True,
                    "default_include_prompt": True,
                    "default_include_raw_llm_output": True,
                    "default_include_state_diff": True,
                },
            ).status_code
            == 200
        )
        response = client.post(f"/v3/sandbox/sessions/{seed['id']}/replay")

    assert response.status_code == 200
    replay_trace = response.json()["session"]["trace"]
    assert replay_trace[0]["debug_trace"] is not None
    assert any(event["node"] == "call_agent_with_tools" for event in replay_trace[0]["debug_trace"]["events"])
    reset_database_state()
    reset_settings_cache()


def test_langgraph_runtime_executes_core_memory_tools_with_mocked_llm(backend_env, monkeypatch) -> None:
    from backend.api.config import get_settings

    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    client = _SequenceLlmClient([_product_turn_calls()])
    result = run_v3_sandbox_turn(
        settings=get_settings(),
        session=V3SandboxSession(id="v3s_runtime"),
        user_message=V3SandboxMessage(id="msg_user_1", role="user", content="我们做中小企业财税 SaaS。"),
        client=client,
    )

    assert "产品是中小企业财税 SaaS" in result.session.core_memory_blocks["product"].value
    assert result.trace_event.runtime_metadata["graph_name"] == "v3_sandbox_core_memory_tool_loop_poc"
    assert result.trace_event.debug_trace is None
    assert result.trace_event.tool_events[0].tool_name == "core_memory_append"


def test_langgraph_runtime_records_verbose_debug_trace_with_prompt_and_raw_output(backend_env, monkeypatch) -> None:
    from backend.api.config import get_settings

    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    result = run_v3_sandbox_turn(
        settings=get_settings(),
        session=V3SandboxSession(id="v3s_runtime_debug"),
        user_message=V3SandboxMessage(id="msg_user_1", role="user", content="我们做中小企业财税 SaaS。"),
        client=_SequenceLlmClient([_product_turn_calls()]),
        debug_options={
            "verbose": True,
            "include_prompt": True,
            "include_raw_llm_output": True,
            "include_repair_attempts": True,
            "include_node_io": True,
            "include_state_diff": True,
        },
    )

    debug_trace = result.trace_event.debug_trace
    assert debug_trace is not None
    assert debug_trace["graph"]["nodes"] == [
        "load_state",
        "compose_context",
        "call_agent_with_tools",
        "execute_tool_calls",
        "return_turn",
    ]
    node_names = [event["node"] for event in debug_trace["events"]]
    assert node_names == ["load_state", "compose_context", "call_agent_with_tools", "execute_tool_calls", "return_turn"]
    call_llm = next(event for event in debug_trace["events"] if event["node"] == "call_agent_with_tools")
    assert call_llm["messages"][0]["role"] == "system"
    assert "raw_output" in call_llm
    execute_tools = next(event for event in debug_trace["events"] if event["node"] == "execute_tool_calls")
    assert execute_tools["tool_results"][0]["tool_name"] == "core_memory_append"
    assert execute_tools["state_diff"]["core_memory_blocks"][0]["change"] == "updated"


def test_langgraph_runtime_records_repair_attempt_in_debug_trace(backend_env, monkeypatch) -> None:
    from backend.api.config import get_settings

    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    result = run_v3_sandbox_turn(
        settings=get_settings(),
        session=V3SandboxSession(id="v3s_runtime_repair_debug"),
        user_message=V3SandboxMessage(id="msg_user_1", role="user", content="我们做中小企业财税 SaaS。"),
        client=_RepairLlmClient(),
        debug_options={
            "verbose": True,
            "include_prompt": True,
            "include_raw_llm_output": True,
            "include_repair_attempts": True,
            "include_node_io": True,
            "include_state_diff": True,
        },
    )

    events = result.trace_event.debug_trace["events"]
    execute_events = [event for event in events if event["node"] == "execute_tool_calls"]
    assert execute_events[0]["tool_results"][0]["status"] == "error"
    assert execute_events[-1]["tool_results"][-1]["tool_name"] == "send_message"
    assert "产品是中小企业财税 SaaS" in result.session.core_memory_blocks["product"].value


def test_v3_sandbox_api_runs_memory_correction_loop(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    monkeypatch.delenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_DIR", raising=False)
    reset_settings_cache()
    reset_database_state()
    turns = [
        _product_turn_calls(),
        _hypothesis_turn_calls(),
        _correction_turn_calls(),
        _followup_turn_calls(),
    ]
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete_with_tools",
        _SequenceLlmClient(turns).complete_with_tools,
    )

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        create_response = client.post("/v3/sandbox/sessions", json={"session_id": "v3s_demo", "title": "Demo"})
        assert create_response.status_code == 201

        first = client.post("/v3/sandbox/sessions/v3s_demo/turns", json={"content": "我们做中小企业财税 SaaS。"})
        assert first.status_code == 200
        assert "产品是中小企业财税 SaaS" in first.json()["session"]["core_memory_blocks"]["product"]["value"]

        second = client.post("/v3/sandbox/sessions/v3s_demo/turns", json={"content": "我的客户是谁？"})
        assert second.status_code == 200
        second_payload = second.json()
        assert "可能优先找中小企业老板和财务负责人" in second_payload["session"]["core_memory_blocks"]["customer_intelligence"]["value"]

        third = client.post(
            "/v3/sandbox/sessions/v3s_demo/turns",
            json={"content": "纠正一下，不是财务负责人，是老板本人。"},
        )
        assert third.status_code == 200
        third_payload = third.json()
        assert "目标联系人是老板本人" in third_payload["session"]["core_memory_blocks"]["customer_intelligence"]["value"]

        fourth = client.post("/v3/sandbox/sessions/v3s_demo/turns", json={"content": "那下一步怎么做？"})
        assert fourth.status_code == 200
        assert "老板本人" in fourth.json()["assistant_message"]["content"]
        assert "财务负责人" not in fourth.json()["assistant_message"]["content"]

        trace_response = client.get("/v3/sandbox/sessions/v3s_demo/trace")
        assert trace_response.status_code == 200
        assert len(trace_response.json()["trace"]) == 4

        session_response = client.get("/v3/sandbox/sessions/v3s_demo")
        assert session_response.status_code == 200
        session = session_response.json()["session"]
        assert "老板本人" in session["core_memory_blocks"]["customer_intelligence"]["value"]

    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_api_uses_database_store_when_configured(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", "database")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    reset_database_state()
    turns = [_product_turn_calls(), _hypothesis_turn_calls(), _correction_turn_calls()]
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete_with_tools",
        _SequenceLlmClient(turns).complete_with_tools,
    )

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        assert client.post("/v3/sandbox/sessions", json={"session_id": "v3s_db_api"}).status_code == 201
        assert client.post("/v3/sandbox/sessions/v3s_db_api/turns", json={"content": "我们做中小企业财税 SaaS。"}).status_code == 200
        assert client.post("/v3/sandbox/sessions/v3s_db_api/turns", json={"content": "我的客户是谁？"}).status_code == 200
        response = client.post(
            "/v3/sandbox/sessions/v3s_db_api/turns",
            json={"content": "纠正一下，不是财务负责人，是老板本人。"},
        )
        assert response.status_code == 200

    reloaded = DatabaseV3SandboxStore().get_session("v3s_db_api")
    assert "目标联系人是老板本人" in reloaded.core_memory_blocks["customer_intelligence"].value
    with get_session_factory()() as db:
        assert db.query(V3SandboxCoreMemoryBlockTransitionEventRecord).filter_by(session_id="v3s_db_api").count() >= 3

    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_demo_seed_returns_deterministic_correction_state(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    reset_settings_cache()
    reset_database_state()

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        response = client.post("/v3/sandbox/demo-seeds", json={"scenario": "sales_training_correction"})
        assert response.status_code == 201
        payload = response.json()
        session = payload["session"]
        assert payload["scenario"] == "sales_training_correction"
        assert "面向苏州小企业老板" in session["core_memory_blocks"]["product"]["value"]
        assert "应优先找小企业老板本人" in session["core_memory_blocks"]["customer_intelligence"]["value"]
        assert "围绕老板本人" in session["core_memory_blocks"]["sales_strategy"]["value"]
        assert len(session["trace"]) == 2
        tool_names_per_turn = [
            [event["tool_name"] for event in trace["tool_events"]]
            for trace in session["trace"]
        ]
        assert tool_names_per_turn == [
            ["core_memory_append", "core_memory_append", "send_message"],
            ["memory_replace", "core_memory_append", "send_message"],
        ]

        stored = client.get(f"/v3/sandbox/sessions/{session['id']}").json()["session"]
        assert "围绕老板本人" in stored["core_memory_blocks"]["sales_strategy"]["value"]

    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_demo_seed_database_store_survives_app_restart(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", "database")
    reset_settings_cache()
    reset_database_state()

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        seed = client.post("/v3/sandbox/demo-seeds", json={"scenario": "sales_training_correction"}).json()["session"]

    with TestClient(create_app()) as client:
        response = client.get(f"/v3/sandbox/sessions/{seed['id']}")

    assert response.status_code == 200
    stored = response.json()["session"]
    assert "应优先找小企业老板本人" in stored["core_memory_blocks"]["customer_intelligence"]["value"]
    with get_session_factory()() as db:
        transitions = (
            db.query(V3SandboxCoreMemoryBlockTransitionEventRecord)
            .filter_by(session_id=seed["id"])
            .all()
        )
        assert len(transitions) >= 4
        assert {item.tool_name for item in transitions} >= {"core_memory_append", "memory_replace"}
        assert {item.block_label for item in transitions} >= {"product", "customer_intelligence", "sales_strategy"}

    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_core_memory_transitions_api_returns_database_events(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", "database")
    reset_settings_cache()
    reset_database_state()

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        seed = client.post("/v3/sandbox/demo-seeds", json={"scenario": "sales_training_correction"}).json()["session"]
        response = client.get(f"/v3/sandbox/sessions/{seed['id']}/core-memory-transitions")

    assert response.status_code == 200
    payload = response.json()
    assert payload["available"] is True
    assert payload["store"]["backend"] == "database"
    assert payload["counts"]["core_memory_block_transitions"] == len(payload["transitions"])
    assert {item["transition_type"] for item in payload["transitions"]} >= {
        "core_memory_append",
        "memory_replace",
    }
    assert {item["block_label"] for item in payload["transitions"]} >= {
        "product",
        "customer_intelligence",
        "sales_strategy",
    }
    assert "sqlite:///" not in json.dumps(payload)

    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_replay_runs_user_turns_into_new_session(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    reset_database_state()
    turns = [_product_turn_calls(), _correction_turn_calls()]
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete_with_tools",
        _SequenceLlmClient(turns).complete_with_tools,
    )

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        seed = client.post("/v3/sandbox/demo-seeds", json={"scenario": "sales_training_correction"}).json()["session"]
        response = client.post(f"/v3/sandbox/sessions/{seed['id']}/replay")

    assert response.status_code == 200
    payload = response.json()
    assert payload["replay"]["status"] == "completed"
    assert payload["replay"]["source_session_id"] == seed["id"]
    assert payload["replay"]["replayed_turns"] == 2
    assert payload["session"]["id"].startswith("v3s_replay_")
    assert len(payload["session"]["messages"]) == 4
    assert "产品是中小企业财税 SaaS" in payload["session"]["core_memory_blocks"]["product"]["value"]

    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_replay_success_persists_database_store(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", "database")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    reset_database_state()
    turns = [_product_turn_calls(), _correction_turn_calls()]
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete_with_tools",
        _SequenceLlmClient(turns).complete_with_tools,
    )

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        seed = client.post("/v3/sandbox/demo-seeds", json={"scenario": "sales_training_correction"}).json()["session"]
        response = client.post(f"/v3/sandbox/sessions/{seed['id']}/replay")

    assert response.status_code == 200
    payload = response.json()
    replay_session_id = payload["replay"]["replay_session_id"]
    assert payload["replay"]["status"] == "completed"
    assert DatabaseV3SandboxStore().get_session(replay_session_id).id == replay_session_id
    with get_session_factory()() as db:
        assert db.query(V3SandboxTraceEventRecord).filter_by(session_id=replay_session_id).count() == 2
        assert db.query(V3SandboxCoreMemoryBlockTransitionEventRecord).filter_by(session_id=replay_session_id).count() >= 2

    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_replay_persists_partial_failure_in_database_store(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", "database")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    reset_database_state()
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete_with_tools",
        _FailSecondTurnClient().complete_with_tools,
    )

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        seed = client.post("/v3/sandbox/demo-seeds", json={"scenario": "sales_training_correction"}).json()["session"]
        response = client.post(f"/v3/sandbox/sessions/{seed['id']}/replay")

    assert response.status_code == 200
    payload = response.json()
    replay_session_id = payload["replay"]["replay_session_id"]
    assert payload["replay"]["status"] == "failed"

    reloaded = DatabaseV3SandboxStore().get_session(replay_session_id)
    assert reloaded.trace[-1].error["code"] == "llm_runtime_unavailable"
    with get_session_factory()() as db:
        assert db.query(V3SandboxTraceEventRecord).filter_by(session_id=replay_session_id).count() == 2

    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_replay_reports_partial_failure(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    reset_database_state()
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete_with_tools",
        _FailSecondTurnClient().complete_with_tools,
    )

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        seed = client.post("/v3/sandbox/demo-seeds", json={"scenario": "sales_training_correction"}).json()["session"]
        response = client.post(f"/v3/sandbox/sessions/{seed['id']}/replay")

    assert response.status_code == 200
    payload = response.json()
    assert payload["replay"]["status"] == "failed"
    assert payload["replay"]["replayed_turns"] == 1
    assert payload["replay"]["failed_turn_index"] == 2
    assert payload["replay"]["error"]["code"] == "llm_runtime_unavailable"
    assert len(payload["session"]["messages"]) == 3
    assert payload["session"]["trace"][-1]["error"]["code"] == "llm_runtime_unavailable"

    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_api_returns_unavailable_when_llm_missing(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "")
    reset_settings_cache()
    reset_database_state()

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        assert client.post("/v3/sandbox/sessions", json={"session_id": "v3s_missing_key"}).status_code == 201
        response = client.post("/v3/sandbox/sessions/v3s_missing_key/turns", json={"content": "你好"})
        trace = client.get("/v3/sandbox/sessions/v3s_missing_key/trace").json()["trace"]

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "llm_runtime_unavailable"
    assert trace[0]["error"]["code"] == "llm_runtime_unavailable"
    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_api_debug_trace_is_opt_in_and_persists_in_database_store(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", "database")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    reset_database_state()
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete_with_tools",
        _SequenceLlmClient([_product_turn_calls(), _hypothesis_turn_calls()]).complete_with_tools,
    )

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        assert client.post("/v3/sandbox/sessions", json={"session_id": "v3s_debug_api"}).status_code == 201
        first = client.post("/v3/sandbox/sessions/v3s_debug_api/turns", json={"content": "我们做中小企业财税 SaaS。"})
        assert first.status_code == 200
        assert first.json()["trace_event"]["debug_trace"] is None

        second = client.post(
            "/v3/sandbox/sessions/v3s_debug_api/turns",
            json={
                "content": "我的客户是谁？",
                "debug_trace": {
                    "verbose": True,
                    "include_prompt": True,
                    "include_raw_llm_output": True,
                    "include_repair_attempts": True,
                    "include_node_io": True,
                    "include_state_diff": True,
                },
            },
        )
        assert second.status_code == 200
        debug_trace = second.json()["trace_event"]["debug_trace"]
        assert debug_trace["events"][2]["node"] == "call_agent_with_tools"
        assert "messages" in debug_trace["events"][2]
        assert "raw_output" in debug_trace["events"][2]

    reloaded = DatabaseV3SandboxStore().get_session("v3s_debug_api")
    assert reloaded.trace[0].debug_trace is None
    assert reloaded.trace[1].debug_trace["events"][2]["node"] == "call_agent_with_tools"

    reset_database_state()
    reset_settings_cache()


def test_memory_replace_unique_or_raise_lists_per_line_numbers(backend_env, monkeypatch) -> None:
    """When ``old_content`` matches multiple positions in the block, the tool error must list the
    1-indexed line numbers of all matches so the LLM can disambiguate by expanding context."""
    from backend.api.config import get_settings

    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()

    blocks = default_core_memory_blocks()
    blocks["product"] = blocks["product"].model_copy(
        update={
            "value": "产品要点 A\n产品要点 X\n产品要点 B\n产品要点 X\n产品要点 C",
        }
    )
    session = V3SandboxSession(id="v3s_memreplace_dup", core_memory_blocks=blocks)

    duplicate_replace = _tool_call(
        "call_replace_dup",
        "memory_replace",
        {"label": "product", "old_content": "产品要点 X", "new_content": "产品要点 X(更新)"},
    )
    send_after = _tool_call(
        "call_send_after",
        "send_message",
        {"message": "尝试更新失败，已上报。"},
    )
    client = _SequenceLlmClient([[duplicate_replace, send_after]])

    result = run_v3_sandbox_turn(
        settings=get_settings(),
        session=session,
        user_message=V3SandboxMessage(id="msg_user_1", role="user", content="把产品要点 X 全部更新一下。"),
        client=client,
    )

    replace_events = [
        event
        for event in result.trace_event.tool_events
        if event.tool_name == "memory_replace"
    ]
    assert len(replace_events) == 1
    failed = replace_events[0]
    assert failed.status == "error"
    error_message = failed.error["message"]
    assert "v3_memory_replace_old_content_not_unique" in error_message
    assert "matches at line(s) [2, 4]" in error_message
    assert "expand 'old_content' with more surrounding context" in error_message

    assert result.session.core_memory_blocks["product"].value == blocks["product"].value


def test_compose_context_renders_block_description_in_system_prompt() -> None:
    """The system prompt must surface each block's description (Letta-style block header), not a
    raw JSON dump, so the model can reason about what to write into which block."""
    blocks = default_core_memory_blocks()
    session = V3SandboxSession(id="v3s_prompt_desc", core_memory_blocks=blocks)
    user_message = V3SandboxMessage(id="msg_user_1", role="user", content="把产品理解告诉我一下。")

    messages = _build_tool_loop_messages(session, user_message)

    assert messages[0]["role"] == "system"
    system_prompt = messages[0]["content"]
    assert "[persona] description: Sales Agent 自身的工作风格、语气与边界" in system_prompt
    assert "[product] description:" in system_prompt
    assert "Agent 对所销售产品的理解" in system_prompt
    assert "[customer_intelligence] description:" in system_prompt
    assert "正在跟进的潜在客户/线索的草稿信息" in system_prompt
    assert "limit: 10000 chars" in system_prompt
    assert "limit: 20000 chars" in system_prompt
    assert "used: 0 chars" in system_prompt


def _tool_call(call_id: str, name: str, arguments: dict[str, object]) -> TokenHubToolCall:
    return TokenHubToolCall(
        id=call_id,
        type="function",
        function=TokenHubToolCallFunction(name=name, arguments=json.dumps(arguments, ensure_ascii=False)),
    )


def _product_turn_calls() -> list[TokenHubToolCall]:
    return [
        _tool_call(
            "call_product_append",
            "core_memory_append",
            {"label": "product", "content": "产品是中小企业财税 SaaS"},
        ),
        _tool_call(
            "call_product_send",
            "send_message",
            {"message": "我已记录产品理解：你们做中小企业财税 SaaS。"},
        ),
    ]


def _hypothesis_turn_calls() -> list[TokenHubToolCall]:
    return [
        _tool_call(
            "call_hypothesis_append",
            "core_memory_append",
            {"label": "customer_intelligence", "content": "可能优先找中小企业老板和财务负责人"},
        ),
        _tool_call(
            "call_hypothesis_send",
            "send_message",
            {"message": "当前假设是先找中小企业老板和财务负责人验证需求。"},
        ),
    ]


def _correction_turn_calls() -> list[TokenHubToolCall]:
    return [
        _tool_call(
            "call_correction_append",
            "core_memory_append",
            {
                "label": "customer_intelligence",
                "content": "目标联系人是老板本人",
            },
        ),
        _tool_call(
            "call_correction_send",
            "send_message",
            {"message": "收到，目标联系人改为老板本人，旧的假设已废弃。"},
        ),
    ]


def _followup_turn_calls() -> list[TokenHubToolCall]:
    return [
        _tool_call(
            "call_followup_send",
            "send_message",
            {"message": "下一步建议只围绕老板本人设计首轮访谈，先验证采购触发点和预算判断。"},
        ),
    ]


class _SequenceLlmClient:
    def __init__(self, turn_calls: list[list[TokenHubToolCall]]) -> None:
        self.turn_calls = list(turn_calls)

    def complete_with_tools(self, messages, *, tools, tool_choice="auto", model_policy=None) -> TokenHubCompletion:
        if not self.turn_calls:
            raise TokenHubClientError("no_more_mock_outputs")
        tool_calls = self.turn_calls.pop(0)
        return TokenHubCompletion(
            content="",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            tool_calls=tool_calls,
            finish_reason="tool_calls",
            raw_message={
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": item.id,
                        "type": item.type,
                        "function": {"name": item.function.name, "arguments": item.function.arguments},
                    }
                    for item in tool_calls
                ],
            },
        )


class _FailSecondTurnClient:
    def __init__(self) -> None:
        self.calls = 0

    def complete_with_tools(self, messages, *, tools, tool_choice="auto", model_policy=None) -> TokenHubCompletion:
        self.calls += 1
        if self.calls == 1:
            tool_calls = _product_turn_calls()
            return TokenHubCompletion(
                content="",
                usage={"total_tokens": 30},
                tool_calls=tool_calls,
                finish_reason="tool_calls",
            )
        raise TokenHubClientError("test_replay_failure")


class _RepairLlmClient:
    """First call returns a doomed memory_replace (block is empty so nothing matches); second call
    succeeds with a normal product append + send_message. Verifies the runtime captures the failed
    tool_event and lets the loop retry until send_message terminates."""

    def __init__(self) -> None:
        self.calls = 0

    def complete_with_tools(self, messages, *, tools, tool_choice="auto", model_policy=None) -> TokenHubCompletion:
        self.calls += 1
        if self.calls == 1:
            return TokenHubCompletion(
                content="",
                usage={"total_tokens": 4},
                tool_calls=[
                    _tool_call(
                        "call_bad_replace",
                        "memory_replace",
                        {"label": "product", "old_content": "missing", "new_content": "产品是中小企业财税 SaaS"},
                    )
                ],
                finish_reason="tool_calls",
            )
        tool_calls = _product_turn_calls()
        return TokenHubCompletion(
            content="",
            usage={"prompt_tokens": 11, "completion_tokens": 12, "total_tokens": 23},
            tool_calls=tool_calls,
            finish_reason="tool_calls",
        )
