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
    blocks["product"] = blocks["product"].model_copy(
        update={
            "value": "产品是销售助手。",
            "metadata": {"category": "saas"},
            "tags": ["lead", "high"],
        }
    )
    session = V3SandboxSession(id="v3s_json", core_memory_blocks=blocks)

    store.create_session(session)
    reloaded = JsonFileV3SandboxStore(tmp_path).get_session("v3s_json")

    assert reloaded.id == session.id
    assert reloaded.core_memory_blocks["product"].value == "产品是销售助手。"
    assert reloaded.core_memory_blocks["product"].metadata == {"category": "saas"}
    assert reloaded.core_memory_blocks["product"].tags == ["lead", "high"]


def test_database_store_round_trips_session_and_normalized_events(tmp_path, monkeypatch) -> None:
    from backend.api.config import get_settings

    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    reset_database_state()
    init_db()

    blocks = default_core_memory_blocks()
    blocks["product"] = blocks["product"].model_copy(
        update={
            "metadata": {"category": "saas"},
            "tags": ["lead", "high"],
        }
    )
    session = V3SandboxSession(id="v3s_db_store", core_memory_blocks=blocks)

    first = run_v3_sandbox_turn(
        settings=get_settings(),
        session=session,
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
    assert reloaded.core_memory_blocks["product"].metadata == {"category": "saas"}
    assert reloaded.core_memory_blocks["product"].tags == ["lead", "high"]

    with get_session_factory()() as db:
        # 3 turns × 4 messages each (user + assistant with tool_calls + 2 tool results)
        assert db.query(V3SandboxMessageRecord).filter_by(session_id="v3s_db_store").count() == 12
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
    # 2 replayed turns × 4 messages each (user + assistant with tool_calls + 2 tool results)
    assert len(payload["session"]["messages"]) == 8
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
    # 1 replayed turn × 5 messages (seed user + assistant with tool_calls + 2 tool results + final assistant)
    # plus 1 failed-turn user message = 5 total visible after partial failure
    assert len(payload["session"]["messages"]) == 5
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

    messages, _summary_info = _build_tool_loop_messages(session, user_message)

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


def test_memory_rethink_replaces_block_value(backend_env, monkeypatch) -> None:
    from backend.api.config import get_settings

    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    blocks = default_core_memory_blocks()
    blocks["product"] = blocks["product"].model_copy(
        update={"value": "旧产品信息第一行\n旧产品信息第二行"}
    )
    session = V3SandboxSession(id="v3s_rethink", core_memory_blocks=blocks)

    rethink_call = _tool_call(
        "call_rethink",
        "memory_rethink",
        {
            "label": "product",
            "new_memory": "产品是面向苏州小企业的销售管理培训，线下课为主。",
        },
    )
    send_after = _tool_call(
        "call_send_after",
        "send_message",
        {"message": "已更新产品理解。"},
    )
    client = _SequenceLlmClient([[rethink_call, send_after]])

    result = run_v3_sandbox_turn(
        settings=get_settings(),
        session=session,
        user_message=V3SandboxMessage(id="msg_user_1", role="user", content="重新整理一下产品信息。"),
        client=client,
    )

    assert result.session.core_memory_blocks["product"].value == "产品是面向苏州小企业的销售管理培训，线下课为主。"
    rethink_events = [e for e in result.trace_event.tool_events if e.tool_name == "memory_rethink"]
    assert len(rethink_events) == 1
    assert rethink_events[0].status == "applied"
    assert rethink_events[0].before_value == "旧产品信息第一行\n旧产品信息第二行"


def test_memory_rethink_rejects_line_number_prefix(backend_env, monkeypatch) -> None:
    from backend.api.config import get_settings

    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    session = V3SandboxSession(id="v3s_rethink_defense", core_memory_blocks=default_core_memory_blocks())

    bad_rethink = _tool_call(
        "call_bad_rethink",
        "memory_rethink",
        {
            "label": "product",
            "new_memory": "Line 1: 产品信息\nLine 2: 详细信息",
        },
    )
    fallback_send = _tool_call(
        "call_fallback_send",
        "send_message",
        {"message": "记录失败，已跳过。"},
    )
    client = _SequenceLlmClient([[bad_rethink, fallback_send]])

    result = run_v3_sandbox_turn(
        settings=get_settings(),
        session=session,
        user_message=V3SandboxMessage(id="msg_user_1", role="user", content="更新产品信息。"),
        client=client,
    )

    rethink_events = [e for e in result.trace_event.tool_events if e.tool_name == "memory_rethink"]
    assert len(rethink_events) == 1
    assert rethink_events[0].status == "error"
    assert "line number prefix" in rethink_events[0].error["message"].lower()


def test_step_limit_respects_max_steps(backend_env, monkeypatch) -> None:
    from backend.api.config import get_settings

    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()

    append_1 = _tool_call("call_1", "core_memory_append", {"label": "product", "content": "A"})
    append_2 = _tool_call("call_2", "core_memory_append", {"label": "product", "content": "B"})
    append_3 = _tool_call("call_3", "core_memory_append", {"label": "product", "content": "C"})
    append_4 = _tool_call("call_4", "core_memory_append", {"label": "product", "content": "D"})

    # With max_steps=4 (minimum), only 4 assistant calls are allowed.
    # After the 4th call, _continue_or_return raises v3_tool_loop_exhausted
    # before a 5th LLM call can happen.
    client_exhaust = _SequenceLlmClient([[append_1], [append_2], [append_3], [append_4]])
    with pytest.raises(ValueError, match="v3_tool_loop_exhausted"):
        run_v3_sandbox_turn(
            settings=get_settings(),
            session=V3SandboxSession(id="v3s_step_limit_4"),
            user_message=V3SandboxMessage(id="msg_user_2", role="user", content="测试。"),
            client=client_exhaust,
            max_steps=4,
        )

    # With max_steps=16 (default), the agent gets enough room for multiple assistant calls.
    # Provide two turns: first appends, second send_message to terminate.
    send_msg = _tool_call("call_send", "send_message", {"message": "done"})
    client_ok = _SequenceLlmClient([[append_1, append_2], [send_msg]])
    result_ok = run_v3_sandbox_turn(
        settings=get_settings(),
        session=V3SandboxSession(id="v3s_step_limit_16"),
        user_message=V3SandboxMessage(id="msg_user_3", role="user", content="测试。"),
        client=client_ok,
        max_steps=16,
    )
    assert "A" in result_ok.session.core_memory_blocks["product"].value
    assert result_ok.trace_event.error is None


def test_runtime_config_max_steps_api(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    reset_settings_cache()
    reset_database_state()

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        # Valid update
        response = client.patch("/v3/sandbox/runtime-config", json={"max_steps": 24})
        assert response.status_code == 200
        assert response.json()["runtime_config"]["max_steps"] == 24

        # Invalid: too low
        bad_low = client.patch("/v3/sandbox/runtime-config", json={"max_steps": 3})
        assert bad_low.status_code == 422

        # Invalid: too high
        bad_high = client.patch("/v3/sandbox/runtime-config", json={"max_steps": 51})
        assert bad_high.status_code == 422

        # Reset
        reset_resp = client.post("/v3/sandbox/runtime-config/reset")
        assert reset_resp.status_code == 200
        assert reset_resp.json()["runtime_config"]["max_steps"] == 16

    reset_database_state()
    reset_settings_cache()


def _make_long_session(n_messages: int = 40, words_per_message: int = 2000) -> V3SandboxSession:
    """Build a session whose token count clearly exceeds the 0.75 threshold
    on a 200k-window model (minimax-m2.5 default). Each message ≈ 10k tokens."""
    long_text = " ".join(["sales automation platform"] * words_per_message)
    messages = [
        V3SandboxMessage(
            id=f"msg_{i}",
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}: {long_text}",
        )
        for i in range(n_messages)
    ]
    return V3SandboxSession(id=f"v3s_compress_{n_messages}", messages=messages)


def _mock_summary_completion(text: str) -> TokenHubCompletion:
    return TokenHubCompletion(
        content=text,
        usage={"total_tokens": 20},
        tool_calls=[],
        finish_reason="stop",
        raw_message={"role": "assistant", "content": text},
    )


def test_context_compression_persists_summary_and_advances_cursor(backend_env, monkeypatch) -> None:
    from unittest.mock import patch
    from backend.api.config import get_settings

    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    settings = get_settings()

    session = _make_long_session()
    user_message = V3SandboxMessage(id="msg_user", role="user", content="Final message.")
    messages_before = len(session.messages)

    with patch("backend.runtime.v3_sandbox.graph.TokenHubClient") as MockClient:
        MockClient.return_value.complete_with_tools.return_value = _mock_summary_completion(
            "Summary: seller sells sales automation; targets SMBs; pricing TBD."
        )
        built_messages, _summary_info = _build_tool_loop_messages(session, user_message, settings=settings)

    # Summary banner should appear in the LLM payload.
    summary_msgs = [
        m for m in built_messages
        if m.get("role") == "user" and "Summary of older conversation" in (m.get("content") or "")
    ]
    assert len(summary_msgs) == 1
    assert "Summary: seller sells sales automation" in summary_msgs[0]["content"]

    # Summary state should now be persisted on the session.
    assert session.context_summary is not None
    assert "Summary: seller sells sales automation" in session.context_summary
    assert session.summary_recursion_count == 1
    # Cursor should land on the last absorbed message. This test bypasses
    # _load_state, so session.messages stays at 40 entries (msg_0..msg_39);
    # historical = messages[:-1] = msg_0..msg_38 (39 entries); the recent
    # window keeps the last 32 (msg_7..msg_38) and the cursor is msg_6.
    assert session.summary_cursor_message_id == "msg_6"
    # Original messages must NOT be modified or augmented.
    assert len(session.messages) == messages_before


def test_context_compression_recent_window_after_summary_is_32_originals(backend_env, monkeypatch) -> None:
    from unittest.mock import patch
    from backend.api.config import get_settings

    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    settings = get_settings()

    session = _make_long_session()
    user_message = V3SandboxMessage(id="msg_user", role="user", content="Final message.")

    with patch("backend.runtime.v3_sandbox.graph.TokenHubClient") as MockClient:
        MockClient.return_value.complete_with_tools.return_value = _mock_summary_completion("Summary v1.")
        _, _ = _build_tool_loop_messages(session, user_message, settings=settings)

    # After summary, the in-context payload contains the remaining 32 raw
    # messages as native-format entries between system/summary and the final
    # user instruction message.
    payload, _ = _build_tool_loop_messages(session, user_message, settings=settings)
    # Find the final user instruction message (the one with "Process the current sales-agent turn")
    final_user_index = next(
        (i for i, m in enumerate(payload) if m["role"] == "user" and "Process the current sales-agent turn" in m.get("content", "")),
        None,
    )
    assert final_user_index is not None
    # Messages between system/summary and the final user message = after_cursor.
    history_part = payload[1:final_user_index]  # skip system; may include summary user message
    # Exclude the summary banner message (it starts with the "Note:" prefix).
    history_messages = [
        m for m in history_part
        if m.get("role") in ("user", "assistant", "tool")
        and not m.get("content", "").startswith("Note: earlier messages have been hidden")
    ]
    # Bypassing _load_state, historical = msg_0..msg_38; cursor = msg_6;
    # recent window = msg_7..msg_38 = 32 entries.
    assert len(history_messages) == 32
    # First history message corresponds to msg_7 (index 7 in original session.messages)
    assert "Message 7" in history_messages[0].get("content", "")


def test_context_compression_recursive_uses_prior_summary(backend_env, monkeypatch) -> None:
    from unittest.mock import patch
    from backend.api.config import get_settings

    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    settings = get_settings()

    # Pre-seed a session with an existing summary + cursor as if a previous
    # turn had already triggered summarization.
    session = _make_long_session()
    session.context_summary = "Prior summary: seller sells X."
    session.summary_cursor_message_id = "msg_7"
    session.summary_recursion_count = 1
    # Append more messages so that after_cursor is well over 32, forcing a
    # second summarization this turn.
    long_text = " ".join(["additional context payload"] * 2000)
    for i in range(40, 80):
        session.messages.append(
            V3SandboxMessage(
                id=f"msg_{i}",
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}: {long_text}",
            )
        )
    user_message = V3SandboxMessage(id="msg_user", role="user", content="Final.")

    captured_prompt: dict[str, str] = {}

    def capture(messages, **kwargs):
        captured_prompt["text"] = messages[0]["content"]
        return _mock_summary_completion("Summary v2 merged.")

    with patch("backend.runtime.v3_sandbox.graph.TokenHubClient") as MockClient:
        MockClient.return_value.complete_with_tools.side_effect = capture
        _, _ = _build_tool_loop_messages(session, user_message, settings=settings)

    # The summarizer prompt should include the prior summary as authoritative.
    assert "Previous summary" in captured_prompt["text"]
    assert "Prior summary: seller sells X." in captured_prompt["text"]
    # And recursion count advanced.
    assert session.summary_recursion_count == 2
    assert session.context_summary == "Summary v2 merged."


def test_fresh_session_has_no_summary_state() -> None:
    """A new session must default to no persistent summary, no cursor, and
    zero recursions — Pydantic field defaults guarantee A-lite is opt-in."""
    session = V3SandboxSession(id="v3s_fresh")
    assert session.context_summary is None
    assert session.summary_cursor_message_id is None
    assert session.summary_recursion_count == 0


def test_summary_state_round_trips_through_json_store(tmp_path: Path) -> None:
    """A-lite summary fields must survive Pydantic JSON dump/validate so they
    persist via the existing v3_sandbox_sessions.payload_json column without
    a schema migration."""
    store = JsonFileV3SandboxStore(tmp_path)
    session = V3SandboxSession(
        id="v3s_summary_persist",
        context_summary="Stored summary text.",
        summary_cursor_message_id="msg_42",
        summary_recursion_count=3,
    )
    store.create_session(session)
    reloaded = store.get_session("v3s_summary_persist")
    assert reloaded.context_summary == "Stored summary text."
    assert reloaded.summary_cursor_message_id == "msg_42"
    assert reloaded.summary_recursion_count == 3


def test_replay_does_not_reuse_persisted_summary(tmp_path, monkeypatch) -> None:
    """Replay must derive summary from scratch rather than inheriting the
    source session's persisted context_summary."""
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", "database")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    reset_database_state()
    init_db()

    from unittest.mock import patch
    from backend.api.config import get_settings
    from backend.api.main import create_app

    # Build a long session that triggers summarization.
    session = _make_long_session()
    settings = get_settings()

    with patch("backend.runtime.v3_sandbox.graph.TokenHubClient") as MockClient:
        MockClient.return_value.complete_with_tools.return_value = _mock_summary_completion(
            "Summary: seller sells sales automation; targets SMBs; pricing TBD."
        )
        _build_tool_loop_messages(
            session,
            V3SandboxMessage(id="msg_user", role="user", content="Final."),
            settings=settings,
        )

    assert session.context_summary is not None
    assert session.summary_recursion_count == 1

    store = DatabaseV3SandboxStore()
    store.save_session(session)

    with TestClient(create_app()) as client:
        response = client.post(f"/v3/sandbox/sessions/{session.id}/replay")

    assert response.status_code == 200
    replay_session = response.json()["session"]
    # Replay creates a fresh V3SandboxSession — summary fields must start empty.
    assert replay_session["context_summary"] is None
    assert replay_session["summary_cursor_message_id"] is None
    assert replay_session["summary_recursion_count"] == 0

    reset_database_state()
    reset_settings_cache()


def test_session_reset_clears_summary_fields(tmp_path: Path) -> None:
    """Overwriting a session in the store with a fresh instance (reset) must
    clear the three A-lite summary fields back to defaults."""
    store = JsonFileV3SandboxStore(tmp_path)
    session = V3SandboxSession(
        id="v3s_reset",
        context_summary="Old summary.",
        summary_cursor_message_id="msg_old",
        summary_recursion_count=5,
    )
    store.create_session(session)

    # Simulate reset by saving a fresh session with the same ID.
    reset_session = V3SandboxSession(id="v3s_reset")
    store.save_session(reset_session)

    reloaded = store.get_session("v3s_reset")
    assert reloaded.context_summary is None
    assert reloaded.summary_cursor_message_id is None
    assert reloaded.summary_recursion_count == 0


def test_summarization_llm_exception_does_not_mutate_session(backend_env, monkeypatch) -> None:
    """LLM call raising an exception must leave session fields untouched and
    return action='failed_llm_exception'."""
    from unittest.mock import patch
    from backend.api.config import get_settings

    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    settings = get_settings()

    session = _make_long_session()
    user_message = V3SandboxMessage(id="msg_user", role="user", content="Final message.")

    with patch("backend.runtime.v3_sandbox.graph.TokenHubClient") as MockClient:
        MockClient.return_value.complete_with_tools.side_effect = RuntimeError("LLM unavailable")
        _, summary_info = _build_tool_loop_messages(session, user_message, settings=settings)

    assert summary_info is not None
    assert summary_info["action"] == "failed_llm_exception"
    assert session.context_summary is None
    assert session.summary_recursion_count == 0
    assert session.summary_cursor_message_id is None


def test_summarization_llm_empty_response_does_not_mutate_session(backend_env, monkeypatch) -> None:
    """LLM returning empty content must leave session fields untouched and
    return action='failed_llm_empty_response'."""
    from unittest.mock import patch
    from backend.api.config import get_settings

    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    settings = get_settings()

    session = _make_long_session()
    user_message = V3SandboxMessage(id="msg_user", role="user", content="Final message.")

    empty_completion = _mock_summary_completion("")

    with patch("backend.runtime.v3_sandbox.graph.TokenHubClient") as MockClient:
        MockClient.return_value.complete_with_tools.return_value = empty_completion
        _, summary_info = _build_tool_loop_messages(session, user_message, settings=settings)

    assert summary_info is not None
    assert summary_info["action"] == "failed_llm_empty_response"
    assert session.context_summary is None
    assert session.summary_recursion_count == 0
    assert session.summary_cursor_message_id is None


def test_summarization_tiktoken_failure_does_not_mutate_session(backend_env, monkeypatch) -> None:
    """tiktoken import failure must leave session fields untouched and
    return action='failed_tiktoken'."""
    from unittest.mock import patch
    from backend.api.config import get_settings
    import sys

    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    settings = get_settings()

    session = _make_long_session()
    user_message = V3SandboxMessage(id="msg_user", role="user", content="Final message.")

    # Force tiktoken import to fail by temporarily hiding the module.
    real_tiktoken = sys.modules.get("tiktoken")
    sys.modules["tiktoken"] = None  # type: ignore[assignment]
    try:
        _, summary_info = _build_tool_loop_messages(session, user_message, settings=settings)
    finally:
        if real_tiktoken is not None:
            sys.modules["tiktoken"] = real_tiktoken
        else:
            del sys.modules["tiktoken"]

    assert summary_info is not None
    assert summary_info["action"] == "failed_tiktoken"
    assert session.context_summary is None
    assert session.summary_recursion_count == 0
    assert session.summary_cursor_message_id is None


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


def test_threshold_changed_to_ninety() -> None:
    from backend.runtime.v3_sandbox.graph import _CONTEXT_COMPRESSION_THRESHOLD_RATIO

    assert _CONTEXT_COMPRESSION_THRESHOLD_RATIO == 0.90


def test_ninety_five_percent_guard_returns_early(monkeypatch) -> None:
    from backend.runtime.v3_sandbox.graph import _continue_or_return

    class _HugeEncoder:
        def encode(self, _text: str) -> list[int]:
            return [0] * 200_000

    monkeypatch.setattr("tiktoken.get_encoding", lambda _name: _HugeEncoder())

    settings = type("Settings", (), {"llm_model": "minimax-m2.5"})()
    state = {
        "settings": settings,
        "final_message": "",
        "tool_events": [],
        "tool_messages": [{"role": "assistant", "content": "x"}],
        "max_steps": 16,
        "runtime_metadata": {},
    }

    result = _continue_or_return(state)
    assert result == "return"
    assert state["runtime_metadata"]["early_return_reason"] == "context_budget_exhausted"


def test_pressure_warning_injected_above_threshold(monkeypatch) -> None:
    from unittest.mock import patch
    from backend.api.config import get_settings, reset_settings_cache
    from backend.runtime.v3_sandbox.graph import _build_tool_loop_messages

    class _HugeEncoder:
        def encode(self, _text: str) -> list[int]:
            return [0] * 200_000

    monkeypatch.setattr("tiktoken.get_encoding", lambda _name: _HugeEncoder())
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    settings = get_settings()

    session = _make_long_session(n_messages=40)
    user_message = V3SandboxMessage(id="msg_user", role="user", content="Final message.")

    with patch("backend.runtime.v3_sandbox.graph.TokenHubClient") as MockClient:
        MockClient.return_value.complete_with_tools.return_value = _mock_summary_completion(
            "Summary: test."
        )
        built_messages, _summary_info = _build_tool_loop_messages(session, user_message, settings=settings)

    system_prompt = built_messages[0]["content"]
    assert "Memory pressure warning" in system_prompt or "memory pressure warning" in system_prompt.lower()


def test_empty_final_message_fallback() -> None:
    from backend.runtime.v3_sandbox.graph import _return_turn
    from backend.runtime.v3_sandbox.schemas import V3SandboxSession, V3SandboxDebugTraceOptions

    session = V3SandboxSession(id="v3s_fallback")
    state = {
        "session": session,
        "turn_id": "turn_1",
        "final_message": "",
        "runtime_metadata": {},
        "started_perf": 0.0,
        "tool_events": [],
        "usage": {},
        "debug_trace": None,
        "debug_options": V3SandboxDebugTraceOptions(
            verbose=False,
            include_prompt=False,
            include_raw_llm_output=False,
            include_repair_attempts=False,
            include_node_io=False,
            include_state_diff=False,
        ),
    }

    result = _return_turn(state)
    assistant_message = result["assistant_message"]
    expected = "（Agent 在本轮执行了多个内部操作，但未发送最终回复。）"
    assert assistant_message.content == expected
    assert result["trace_event"].parsed_output["assistant_message"] == expected


def test_pressure_warning_metadata_fields_written(monkeypatch) -> None:
    from backend.api.config import get_settings, reset_settings_cache
    from backend.runtime.v3_sandbox.graph import _build_tool_loop_messages

    class _HugeEncoder:
        def encode(self, _text: str) -> list[int]:
            return [0] * 200_000

    monkeypatch.setattr("tiktoken.get_encoding", lambda _name: _HugeEncoder())
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    settings = get_settings()

    session = _make_long_session(n_messages=40)
    user_message = V3SandboxMessage(id="msg_user", role="user", content="Final message.")
    runtime_metadata: dict[str, Any] = {}

    messages, _summary_info = _build_tool_loop_messages(
        session, user_message, settings=settings, runtime_metadata=runtime_metadata
    )

    assert runtime_metadata["context_pressure_tokens"] == 200_000
    assert runtime_metadata["context_pressure_threshold"] > 0
    assert runtime_metadata["context_pressure_triggered"] is True
    system_prompt = messages[0]["content"]
    assert "Memory pressure warning" in system_prompt or "memory pressure warning" in system_prompt.lower()


def test_summarization_metadata_fields_written(monkeypatch) -> None:
    from unittest.mock import patch
    from backend.api.config import get_settings, reset_settings_cache
    from backend.runtime.v3_sandbox.graph import _maybe_run_summarization

    class _HugeEncoder:
        def encode(self, _text: str) -> list[int]:
            return [0] * 200_000

    monkeypatch.setattr("tiktoken.get_encoding", lambda _name: _HugeEncoder())
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    settings = get_settings()

    session = _make_long_session(n_messages=40)
    runtime_metadata: dict[str, Any] = {}

    with patch("backend.runtime.v3_sandbox.graph.TokenHubClient") as MockClient:
        MockClient.return_value.complete_with_tools.return_value = _mock_summary_completion(
            "Summary: test."
        )
        result = _maybe_run_summarization(
            session=session,
            settings=settings,
            system_prompt="System prompt",
            current_user_content="User message",
            historical=session.messages[:-1],
            after_cursor=session.messages[1:],
            max_context_messages=32,
            runtime_metadata=runtime_metadata,
        )

    assert runtime_metadata["summarization_token_count"] == 200_000
    assert result["action"] in ("created", "refreshed")
    assert runtime_metadata["summarization_action"] == result["action"]


def test_guard_tool_tokens_written(monkeypatch) -> None:
    from backend.runtime.v3_sandbox.graph import _continue_or_return

    class _HugeEncoder:
        def encode(self, _text: str) -> list[int]:
            return [0] * 200_000

    monkeypatch.setattr("tiktoken.get_encoding", lambda _name: _HugeEncoder())

    settings = type("Settings", (), {"llm_model": "minimax-m2.5"})()
    state = {
        "settings": settings,
        "final_message": "",
        "tool_events": [],
        "tool_messages": [{"role": "assistant", "content": "x"}],
        "max_steps": 16,
        "runtime_metadata": {},
    }

    result = _continue_or_return(state)
    assert result == "return"
    assert state["runtime_metadata"]["early_return_reason"] == "context_budget_exhausted"
    assert state["runtime_metadata"]["guard_tool_tokens"] == 200_000
    assert state["runtime_metadata"]["guard_tool_threshold"] == 190_000


def test_smoke_outcome_classifier() -> None:
    import importlib.util
    from pathlib import Path

    smoke_path = Path(__file__).resolve().parents[2] / "backend" / "scripts" / "v3_comprehensive_live_smoke.py"
    spec = importlib.util.spec_from_file_location("smoke", str(smoke_path))
    assert spec is not None and spec.loader is not None
    smoke = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(smoke)

    assert smoke._classify_outcome(None, ["send_message"], "hello") == "success"
    assert smoke._classify_outcome("ValueError: v3_tool_loop_no_tool_call", [], "") == "runtime_seam"
    assert smoke._classify_outcome(
        "V3SandboxRuntimeError: tokenhub_http_error:402:FREE_QUOTA_EXHAUSTED", [], ""
    ) == "quota_error"
    assert smoke._classify_outcome(
        "V3SandboxRuntimeError: tokenhub_http_error:429:rate limit", [], ""
    ) == "platform_error"
    assert smoke._classify_outcome("ConnectionError: something else", [], "") == "platform_error"
    assert smoke._is_quota_error("FREE_QUOTA_EXHAUSTED") is True
    assert smoke._is_rate_limit_error("429 rate limit") is True


def test_prefill_saturation_history_appends_messages() -> None:
    import importlib.util
    from pathlib import Path

    smoke_path = Path(__file__).resolve().parents[2] / "backend" / "scripts" / "v3_comprehensive_live_smoke.py"
    spec = importlib.util.spec_from_file_location("smoke", str(smoke_path))
    assert spec is not None and spec.loader is not None
    smoke = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(smoke)

    session = V3SandboxSession(id="v3s_prefill_test")
    initial_count = len(session.messages)
    smoke._prefill_saturation_history(session, n_messages=60, chars_per_message=10000)

    assert len(session.messages) == initial_count + 60
    # Roles alternate user/assistant
    for i, msg in enumerate(session.messages):
        expected_role = "user" if i % 2 == 0 else "assistant"
        assert msg.role == expected_role
        assert msg.id == f"prefill_{i:03d}"


def test_prefill_saturation_history_embeds_early_facts() -> None:
    import importlib.util
    from pathlib import Path

    smoke_path = Path(__file__).resolve().parents[2] / "backend" / "scripts" / "v3_comprehensive_live_smoke.py"
    spec = importlib.util.spec_from_file_location("smoke", str(smoke_path))
    assert spec is not None and spec.loader is not None
    smoke = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(smoke)

    session = V3SandboxSession(id="v3s_prefill_facts")
    smoke._prefill_saturation_history(session, n_messages=60, chars_per_message=10000)

    # First N messages should contain the early facts
    for i, fact in enumerate(smoke.PREFILL_EARLY_FACTS):
        assert fact in session.messages[i].content


def test_prefill_saturation_history_message_length() -> None:
    import importlib.util
    from pathlib import Path

    smoke_path = Path(__file__).resolve().parents[2] / "backend" / "scripts" / "v3_comprehensive_live_smoke.py"
    spec = importlib.util.spec_from_file_location("smoke", str(smoke_path))
    assert spec is not None and spec.loader is not None
    smoke = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(smoke)

    session = V3SandboxSession(id="v3s_prefill_len")
    target_chars = 5000
    smoke._prefill_saturation_history(session, n_messages=10, chars_per_message=target_chars)

    for msg in session.messages:
        # Allow small tolerance due to string slicing
        assert len(msg.content) >= target_chars - 100
        assert len(msg.content) <= target_chars + 100


def test_tool_loop_messages_persisted_to_session() -> None:
    """After a turn with tool calls, session.messages must contain the assistant
    message with tool_calls and the corresponding tool result messages with
    tool_call_id."""
    from backend.runtime.v3_sandbox.graph import run_v3_sandbox_turn
    from backend.api.config import get_settings, reset_settings_cache

    reset_settings_cache()
    session = V3SandboxSession(id="v3s_tool_persist")

    result = run_v3_sandbox_turn(
        settings=get_settings(),
        session=session,
        user_message=V3SandboxMessage(id="msg_user_1", role="user", content="我们做中小企业财税 SaaS。"),
        client=_SequenceLlmClient([_product_turn_calls()]),
    )

    msgs = result.session.messages
    # user + assistant with tool_calls + 2 tool results = 4 messages
    assert len(msgs) == 4

    assert msgs[0].role == "user"
    assert msgs[1].role == "assistant"
    assert msgs[1].tool_calls is not None
    assert len(msgs[1].tool_calls) == 2
    assert msgs[1].tool_calls[0]["function"]["name"] == "core_memory_append"
    assert msgs[1].tool_calls[1]["function"]["name"] == "send_message"

    assert msgs[2].role == "tool"
    assert msgs[2].tool_call_id == msgs[1].tool_calls[0]["id"]
    assert "ok" in msgs[2].content

    assert msgs[3].role == "tool"
    assert msgs[3].tool_call_id == msgs[1].tool_calls[1]["id"]
    assert "message" in msgs[3].content


def test_build_tool_loop_messages_preserves_tool_metadata() -> None:
    """_build_tool_loop_messages must emit native LLM message format with
    tool_calls and tool_call_id preserved."""
    from backend.runtime.v3_sandbox.graph import _build_tool_loop_messages

    session = V3SandboxSession(id="v3s_native_fmt")
    # _build_tool_loop_messages assumes session.messages ends with the current
    # user message (appended by _load_state). historical = session.messages[:-1].
    session.messages = [
        V3SandboxMessage(id="m1", role="user", content="Hello"),
        V3SandboxMessage(
            id="m2",
            role="assistant",
            content="",
            tool_calls=[
                {"id": "call_1", "type": "function", "function": {"name": "core_memory_append", "arguments": "{}"}}
            ],
        ),
        V3SandboxMessage(id="m3", role="tool", content='{"ok": true}', tool_call_id="call_1"),
        V3SandboxMessage(id="m4", role="user", content="Previous turn user"),
    ]
    user_message = V3SandboxMessage(id="m5", role="user", content="Next")

    payload, _ = _build_tool_loop_messages(session, user_message)

    # payload[0] = system
    # payload[1] = assistant with tool_calls
    # payload[2] = tool with tool_call_id
    # payload[-1] = current user message
    assert payload[0]["role"] == "system"

    assistant_msg = next(m for m in payload if m.get("role") == "assistant")
    assert "tool_calls" in assistant_msg
    assert assistant_msg["tool_calls"][0]["id"] == "call_1"

    tool_msg = next(m for m in payload if m.get("role") == "tool")
    assert tool_msg["tool_call_id"] == "call_1"
    assert tool_msg["content"] == '{"ok": true}'

    assert payload[-1]["role"] == "user"
    assert "Next" in payload[-1]["content"]


def test_summarization_does_not_split_tool_pairs(monkeypatch) -> None:
    """When summarization absorbs older messages, it must not leave an
    assistant tool_calls block orphaned from its tool results."""
    from unittest.mock import patch
    from backend.api.config import get_settings, reset_settings_cache
    from backend.runtime.v3_sandbox.graph import _maybe_run_summarization

    class _HugeEncoder:
        def encode(self, _text: str) -> list[int]:
            return [0] * 200_000

    monkeypatch.setattr("tiktoken.get_encoding", lambda _name: _HugeEncoder())
    reset_settings_cache()
    settings = get_settings()

    # Construct a controlled case: after_cursor = [assistant_with_calls, tool1, tool2, user, assistant]
    # max_context_messages=2 -> to_absorb = after_cursor[:-2] = [assistant_with_calls, tool1, tool2]
    # The pairing guard should keep tool1+tool2 together with assistant_with_calls.
    session = V3SandboxSession(id="v3s_pair_guard")
    session.messages = [
        V3SandboxMessage(
            id="a1",
            role="assistant",
            content="",
            tool_calls=[
                {"id": "c1", "type": "function", "function": {"name": "core_memory_append", "arguments": "{}"}},
                {"id": "c2", "type": "function", "function": {"name": "send_message", "arguments": "{}"}},
            ],
        ),
        V3SandboxMessage(id="t1", role="tool", content='{"ok": true}', tool_call_id="c1"),
        V3SandboxMessage(id="t2", role="tool", content='{"ok": true}', tool_call_id="c2"),
        V3SandboxMessage(id="u1", role="user", content="User msg"),
        V3SandboxMessage(id="a2", role="assistant", content="Reply"),
    ]
    after_cursor = list(session.messages)

    with patch("backend.runtime.v3_sandbox.graph.TokenHubClient") as MockClient:
        MockClient.return_value.complete_with_tools.return_value = _mock_summary_completion("Summary.")
        result = _maybe_run_summarization(
            session=session,
            settings=settings,
            system_prompt="System",
            current_user_content="Final",
            historical=after_cursor,
            after_cursor=after_cursor,
            max_context_messages=2,
            runtime_metadata=None,
        )

    # Summarization should have run because after_cursor (5) > max_context_messages (2)
    # and token count is huge (mocked to 200k).
    assert result["action"] in ("created", "refreshed")
    # The cursor should have advanced past the assistant + both tool results,
    # not stopped in the middle.
    assert session.summary_cursor_message_id in {"t1", "t2", "a2"}
    # Remaining after_cursor should contain at least the last 2 messages.
    remaining_ids = {m.id for m in session.messages}
    assert "u1" in remaining_ids
    assert "a2" in remaining_ids


def test_schema_backwards_compatibility() -> None:
    """Old V3SandboxMessage JSON without tool_calls/tool_call_id must load
    without errors, with new fields defaulting to None."""
    from backend.runtime.v3_sandbox.schemas import V3SandboxMessage

    old_data = {
        "id": "msg_old",
        "role": "user",
        "content": "Hello",
        "created_at": "2026-01-01T00:00:00Z",
    }
    msg = V3SandboxMessage.model_validate(old_data)
    assert msg.tool_calls is None
    assert msg.tool_call_id is None
    assert msg.role == "user"
    assert msg.content == "Hello"
