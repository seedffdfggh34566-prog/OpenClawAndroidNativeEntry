from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.api.config import reset_settings_cache
from backend.api.database import get_session_factory, init_db, reset_database_state
from backend.api.models import (
    V3SandboxActionEventRecord,
    V3SandboxMemoryItemRecord,
    V3SandboxMemoryTransitionEventRecord,
    V3SandboxMessageRecord,
    V3SandboxTraceEventRecord,
)
from backend.runtime.llm_client import TokenHubClientError, TokenHubCompletion
from backend.runtime.v3_sandbox import (
    DatabaseV3SandboxStore,
    InMemoryV3SandboxStore,
    JsonFileV3SandboxStore,
    V3SandboxStoreConfigError,
    run_v3_sandbox_turn,
)
from backend.runtime.v3_sandbox.schemas import MemoryItem, V3SandboxMessage, V3SandboxSession


def test_memory_item_rejects_unknown_status() -> None:
    with pytest.raises(ValidationError):
        MemoryItem(id="mem_bad", status="draft", content="bad status")


def test_json_store_round_trips_session(tmp_path: Path) -> None:
    store = JsonFileV3SandboxStore(tmp_path)
    session = V3SandboxSession(
        id="v3s_json",
        memory_items={
            "mem_product": MemoryItem(
                id="mem_product",
                status="observed",
                content="产品是销售助手。",
                source="user",
            )
        },
    )

    store.create_session(session)
    reloaded = JsonFileV3SandboxStore(tmp_path).get_session("v3s_json")

    assert reloaded.id == session.id
    assert reloaded.memory_items["mem_product"].content == "产品是销售助手。"


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
        client=_SequenceLlmClient([_product_turn_output()]),
    )
    second = run_v3_sandbox_turn(
        settings=get_settings(),
        session=first.session,
        user_message=V3SandboxMessage(id="msg_user_2", role="user", content="我的客户是谁？"),
        client=_SequenceLlmClient([_hypothesis_turn_output()]),
    )
    third = run_v3_sandbox_turn(
        settings=get_settings(),
        session=second.session,
        user_message=V3SandboxMessage(id="msg_user_3", role="user", content="纠正一下，不是财务负责人，是老板本人。"),
        client=_SequenceLlmClient([_correction_turn_output()]),
    )

    store = DatabaseV3SandboxStore()
    store.save_session(third.session)
    store.save_session(third.session)

    reloaded = DatabaseV3SandboxStore().get_session("v3s_db_store")
    assert reloaded.memory_items["mem_target_hypothesis"].status == "superseded"
    assert reloaded.memory_items["mem_target_corrected"].status == "confirmed"

    with get_session_factory()() as db:
        assert db.query(V3SandboxMessageRecord).filter_by(session_id="v3s_db_store").count() == 6
        assert db.query(V3SandboxTraceEventRecord).filter_by(session_id="v3s_db_store").count() == 3
        assert db.query(V3SandboxActionEventRecord).filter_by(session_id="v3s_db_store").count() == 8
        assert db.query(V3SandboxMemoryItemRecord).filter_by(session_id="v3s_db_store").count() == 3
        transitions = db.query(V3SandboxMemoryTransitionEventRecord).filter_by(session_id="v3s_db_store").all()
        assert len(transitions) == 4
        assert {item.transition_type for item in transitions} >= {"write_memory", "supersede_memory"}

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


def test_v3_sandbox_memory_transitions_api_requires_database_store(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.delenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", raising=False)
    reset_settings_cache()
    reset_database_state()

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        seed = client.post("/v3/sandbox/demo-seeds", json={"scenario": "sales_training_correction"}).json()["session"]
        response = client.get(f"/v3/sandbox/sessions/{seed['id']}/memory-transitions")

    assert response.status_code == 200
    payload = response.json()
    assert payload["available"] is False
    assert payload["reason"] == "database_store_required"
    assert payload["transitions"] == []
    assert payload["store"]["backend"] == "memory"

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
        assert initial_payload["danger_readonly"]["database_url_status"] == "configured"

        updated = client.patch(
            "/v3/sandbox/runtime-config",
            json={
                "llm_model": "deepseek-v3.1",
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
        assert runtime_config["llm_model"] == "deepseek-v3.1"
        assert runtime_config["llm_timeout_seconds"] == 180
        assert runtime_config["default_debug_trace"] is True
        assert runtime_config["trace_max_bytes"] == 200_000

        reset = client.post("/v3/sandbox/runtime-config/reset")
        assert reset.status_code == 200
        reset_config = reset.json()["runtime_config"]
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
        bad_timeout = client.patch("/v3/sandbox/runtime-config", json={"llm_timeout_seconds": 30})
        bad_max_bytes = client.patch("/v3/sandbox/runtime-config", json={"trace_max_bytes": 1_000})

    assert bad_model.status_code == 422
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
        "backend.runtime.llm_client.TokenHubClient.complete",
        _SequenceLlmClient([_product_turn_output()]).complete,
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
    call_llm = next(event for event in debug_trace["events"] if event["node"] == "call_llm")
    assert "messages" in call_llm
    assert "raw_output" in call_llm
    apply_actions = next(event for event in debug_trace["events"] if event["node"] == "apply_actions")
    assert "state_diff" in apply_actions
    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_runtime_config_can_trace_replay(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    reset_database_state()
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete",
        _SequenceLlmClient([_product_turn_output(), _correction_turn_output()]).complete,
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
    assert any(event["node"] == "call_llm" for event in replay_trace[0]["debug_trace"]["events"])
    reset_database_state()
    reset_settings_cache()


def test_langgraph_runtime_applies_actions_with_mocked_llm(backend_env, monkeypatch) -> None:
    from backend.api.config import get_settings

    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    client = _SequenceLlmClient([_product_turn_output()])
    result = run_v3_sandbox_turn(
        settings=get_settings(),
        session=V3SandboxSession(id="v3s_runtime"),
        user_message=V3SandboxMessage(id="msg_user_1", role="user", content="我们做中小企业财税 SaaS。"),
        client=client,
    )

    assert result.session.memory_items["mem_product"].status == "observed"
    assert result.trace_event.runtime_metadata["graph_name"] == "v3_sandbox_runtime_poc"
    assert result.trace_event.debug_trace is None
    assert result.actions[0].type == "write_memory"


def test_langgraph_runtime_records_verbose_debug_trace_with_prompt_and_raw_output(backend_env, monkeypatch) -> None:
    from backend.api.config import get_settings

    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    result = run_v3_sandbox_turn(
        settings=get_settings(),
        session=V3SandboxSession(id="v3s_runtime_debug"),
        user_message=V3SandboxMessage(id="msg_user_1", role="user", content="我们做中小企业财税 SaaS。"),
        client=_SequenceLlmClient([_product_turn_output()]),
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
    assert debug_trace["graph"]["nodes"] == ["load_state", "call_llm", "parse_actions", "apply_actions", "return_turn"]
    node_names = [event["node"] for event in debug_trace["events"]]
    assert node_names == ["load_state", "call_llm", "parse_actions", "apply_actions", "return_turn"]
    call_llm = next(event for event in debug_trace["events"] if event["node"] == "call_llm")
    assert call_llm["messages"][0]["role"] == "system"
    assert "raw_output" in call_llm
    apply_actions = next(event for event in debug_trace["events"] if event["node"] == "apply_actions")
    assert apply_actions["action_results"][0]["type"] == "write_memory"
    assert apply_actions["state_diff"]["memory_items"][0]["change"] == "added"


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

    call_llm = next(event for event in result.trace_event.debug_trace["events"] if event["node"] == "call_llm")
    assert call_llm["output"]["initial_output_valid"] is False
    assert call_llm["repair_attempts"][0]["output_valid"] is True
    assert call_llm["repair_attempts"][0]["messages"][-1]["role"] == "user"
    assert "raw_output" in call_llm["repair_attempts"][0]


def test_langgraph_runtime_accepts_action_type_nested_payload(backend_env, monkeypatch) -> None:
    from backend.api.config import get_settings

    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    output = _product_turn_output()
    output["actions"][0]["payload"] = {"write_memory": output["actions"][0]["payload"]}
    client = _SequenceLlmClient([output])
    result = run_v3_sandbox_turn(
        settings=get_settings(),
        session=V3SandboxSession(id="v3s_runtime_nested"),
        user_message=V3SandboxMessage(id="msg_user_1", role="user", content="我们做中小企业财税 SaaS。"),
        client=client,
    )

    assert result.session.memory_items["mem_product"].content == "产品是中小企业财税 SaaS"


def test_v3_sandbox_api_runs_memory_correction_loop(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    monkeypatch.delenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_DIR", raising=False)
    reset_settings_cache()
    reset_database_state()
    outputs = [
        _product_turn_output(),
        _hypothesis_turn_output(),
        _correction_turn_output(),
        _followup_turn_output(),
    ]
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete",
        _SequenceLlmClient(outputs).complete,
    )

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        create_response = client.post("/v3/sandbox/sessions", json={"session_id": "v3s_demo", "title": "Demo"})
        assert create_response.status_code == 201

        first = client.post("/v3/sandbox/sessions/v3s_demo/turns", json={"content": "我们做中小企业财税 SaaS。"})
        assert first.status_code == 200
        assert first.json()["session"]["memory_items"]["mem_product"]["status"] == "observed"

        second = client.post("/v3/sandbox/sessions/v3s_demo/turns", json={"content": "我的客户是谁？"})
        assert second.status_code == 200
        second_payload = second.json()
        assert second_payload["session"]["memory_items"]["mem_target_hypothesis"]["status"] == "hypothesis"
        assert second_payload["session"]["customer_intelligence"]["candidates"][0]["id"] == "cand_sme_owner"

        third = client.post(
            "/v3/sandbox/sessions/v3s_demo/turns",
            json={"content": "纠正一下，不是财务负责人，是老板本人。"},
        )
        assert third.status_code == 200
        third_payload = third.json()
        assert third_payload["session"]["memory_items"]["mem_target_hypothesis"]["status"] == "superseded"
        assert third_payload["session"]["memory_items"]["mem_target_corrected"]["status"] == "confirmed"

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
        assert session["working_state"]["correction_summary"] == ["目标联系人已从财务负责人纠正为老板本人"]

    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_api_uses_database_store_when_configured(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", "database")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    reset_database_state()
    outputs = [_product_turn_output(), _hypothesis_turn_output(), _correction_turn_output()]
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete",
        _SequenceLlmClient(outputs).complete,
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
    assert reloaded.memory_items["mem_target_hypothesis"].status == "superseded"
    with get_session_factory()() as db:
        assert db.query(V3SandboxMemoryTransitionEventRecord).filter_by(session_id="v3s_db_api").count() == 4

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
        assert session["memory_items"]["mem_seed_product"]["status"] == "observed"
        assert session["memory_items"]["mem_seed_target_hypothesis"]["status"] == "superseded"
        assert session["memory_items"]["mem_seed_target_confirmed"]["status"] == "confirmed"
        assert session["customer_intelligence"]["candidates"][0]["id"] == "cand_seed_owner"
        assert len(session["trace"]) == 2

        stored = client.get(f"/v3/sandbox/sessions/{session['id']}").json()["session"]
        assert stored["working_state"]["correction_summary"] == ["目标联系人已从 HR/培训负责人纠正为老板本人"]

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
    assert stored["memory_items"]["mem_seed_target_confirmed"]["status"] == "confirmed"
    with get_session_factory()() as db:
        assert db.query(V3SandboxActionEventRecord).filter_by(session_id=seed["id"]).count() == 5
        transitions = db.query(V3SandboxMemoryTransitionEventRecord).filter_by(session_id=seed["id"]).all()
        assert {item.transition_type for item in transitions} >= {"write_memory", "update_memory_status"}

    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_memory_transitions_api_returns_database_events(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", "database")
    reset_settings_cache()
    reset_database_state()

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        seed = client.post("/v3/sandbox/demo-seeds", json={"scenario": "sales_training_correction"}).json()["session"]
        response = client.get(f"/v3/sandbox/sessions/{seed['id']}/memory-transitions")

    assert response.status_code == 200
    payload = response.json()
    assert payload["available"] is True
    assert payload["store"]["backend"] == "database"
    assert payload["counts"]["transitions"] == len(payload["transitions"])
    assert {item["transition_type"] for item in payload["transitions"]} >= {
        "write_memory",
        "update_memory_status",
    }
    assert {item["memory_id"] for item in payload["transitions"]} >= {
        "mem_seed_product",
        "mem_seed_target_confirmed",
    }
    assert "sqlite:///" not in json.dumps(payload)

    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_replay_runs_user_turns_into_new_session(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    reset_database_state()
    outputs = [_product_turn_output(), _correction_turn_output()]
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete",
        _SequenceLlmClient(outputs).complete,
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
    assert payload["session"]["memory_items"]["mem_product"]["status"] == "observed"

    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_replay_success_persists_database_store(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", "database")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    reset_database_state()
    outputs = [_product_turn_output(), _correction_turn_output()]
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete",
        _SequenceLlmClient(outputs).complete,
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
        assert db.query(V3SandboxActionEventRecord).filter_by(session_id=replay_session_id).count() == 5

    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_replay_persists_partial_failure_in_database_store(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", "database")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    reset_database_state()
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete",
        _FailSecondTurnClient().complete,
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
        "backend.runtime.llm_client.TokenHubClient.complete",
        _FailSecondTurnClient().complete,
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


def test_v3_sandbox_api_returns_structured_error_for_bad_llm_json(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    reset_database_state()
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete",
        lambda *args, **kwargs: TokenHubCompletion(content="not json", usage={}),
    )

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        assert client.post("/v3/sandbox/sessions", json={"session_id": "v3s_bad_json"}).status_code == 201
        response = client.post("/v3/sandbox/sessions/v3s_bad_json/turns", json={"content": "你好"})
        trace = client.get("/v3/sandbox/sessions/v3s_bad_json/trace").json()["trace"]

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "llm_structured_output_invalid"
    assert trace[0]["error"]["code"] == "llm_structured_output_invalid"
    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_api_debug_trace_is_opt_in_and_persists_in_database_store(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND", "database")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    reset_database_state()
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete",
        _SequenceLlmClient([_product_turn_output(), _hypothesis_turn_output()]).complete,
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
        assert debug_trace["events"][1]["node"] == "call_llm"
        assert "messages" in debug_trace["events"][1]
        assert "raw_output" in debug_trace["events"][1]

    reloaded = DatabaseV3SandboxStore().get_session("v3s_debug_api")
    assert reloaded.trace[0].debug_trace is None
    assert reloaded.trace[1].debug_trace["events"][1]["node"] == "call_llm"

    reset_database_state()
    reset_settings_cache()


def test_v3_sandbox_api_failed_debug_trace_records_parse_error(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("OPENCLAW_BACKEND_LLM_API_KEY", "test-key")
    reset_settings_cache()
    reset_database_state()
    monkeypatch.setattr(
        "backend.runtime.llm_client.TokenHubClient.complete",
        lambda *args, **kwargs: TokenHubCompletion(content="not json", usage={}),
    )

    from backend.api.main import create_app

    with TestClient(create_app()) as client:
        assert client.post("/v3/sandbox/sessions", json={"session_id": "v3s_bad_json_debug"}).status_code == 201
        response = client.post(
            "/v3/sandbox/sessions/v3s_bad_json_debug/turns",
            json={
                "content": "你好",
                "debug_trace": {
                    "verbose": True,
                    "include_raw_llm_output": True,
                    "include_repair_attempts": True,
                    "include_node_io": True,
                },
            },
        )
        trace = client.get("/v3/sandbox/sessions/v3s_bad_json_debug/trace").json()["trace"]

    assert response.status_code == 422
    debug_trace = trace[0]["debug_trace"]
    assert debug_trace is not None
    assert any(event["node"] == "parse_actions" and event["status"] == "error" for event in debug_trace["events"])
    call_llm = next(event for event in debug_trace["events"] if event["node"] == "call_llm")
    assert call_llm["repair_attempts"][0]["output_valid"] is False

    reset_database_state()
    reset_settings_cache()


class _SequenceLlmClient:
    def __init__(self, outputs: list[dict[str, object]]) -> None:
        self.outputs = list(outputs)

    def complete(self, messages) -> TokenHubCompletion:
        if not self.outputs:
            raise TokenHubClientError("no_more_mock_outputs")
        return TokenHubCompletion(
            content=json.dumps(self.outputs.pop(0), ensure_ascii=False),
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        )


class _FailSecondTurnClient:
    def __init__(self) -> None:
        self.calls = 0

    def complete(self, messages) -> TokenHubCompletion:
        self.calls += 1
        if self.calls == 1:
            return TokenHubCompletion(
                content=json.dumps(_product_turn_output(), ensure_ascii=False),
                usage={"total_tokens": 30},
            )
        raise TokenHubClientError("test_replay_failure")


class _RepairLlmClient:
    def __init__(self) -> None:
        self.calls = 0

    def complete(self, messages) -> TokenHubCompletion:
        self.calls += 1
        if self.calls == 1:
            return TokenHubCompletion(content="not json", usage={"total_tokens": 4})
        return TokenHubCompletion(
            content=json.dumps(_product_turn_output(), ensure_ascii=False),
            usage={"prompt_tokens": 11, "completion_tokens": 12, "total_tokens": 23},
        )


def _product_turn_output() -> dict[str, object]:
    return {
        "assistant_message": "我已记录产品理解：你们做中小企业财税 SaaS。",
        "actions": [
            {
                "type": "write_memory",
                "payload": {
                    "id": "mem_product",
                    "status": "observed",
                    "content": "产品是中小企业财税 SaaS",
                    "source": "user",
                    "evidence": ["我们做中小企业财税 SaaS。"],
                    "confidence": 0.95,
                    "tags": ["product"],
                },
            },
            {
                "type": "update_working_state",
                "payload": {"product_understanding": ["产品是中小企业财税 SaaS"]},
            },
        ],
        "reasoning_summary": "用户给出产品信息。",
        "confidence": 0.95,
    }


def _hypothesis_turn_output() -> dict[str, object]:
    return {
        "assistant_message": "当前假设是先找中小企业老板和财务负责人验证需求。",
        "actions": [
            {
                "type": "write_memory",
                "payload": {
                    "id": "mem_target_hypothesis",
                    "status": "hypothesis",
                    "content": "可能优先找中小企业老板和财务负责人",
                    "source": "agent",
                    "confidence": 0.62,
                    "tags": ["customer_intelligence"],
                },
            },
            {
                "type": "update_working_state",
                "payload": {"current_hypotheses": ["可能优先找中小企业老板和财务负责人"]},
            },
            {
                "type": "update_customer_intelligence",
                "payload": {
                    "target_industries": ["中小企业服务"],
                    "target_roles": ["老板", "财务负责人"],
                    "candidates": [
                        {
                            "id": "cand_sme_owner",
                            "name": "华东中小企业老板",
                            "segment": "中小企业",
                            "target_roles": ["老板", "财务负责人"],
                            "ranking_reason": "直接感知财税 SaaS 的经营价值",
                            "score": 70,
                            "validation_signals": ["是否有财税合规压力"],
                        }
                    ],
                    "ranking_reasons": ["老板和财务负责人可能共同参与财税软件决策"],
                    "scoring_draft": {"cand_sme_owner": 70},
                    "validation_signals": ["是否有财税合规压力"],
                },
            },
        ],
        "reasoning_summary": "形成客户情报假设。",
        "confidence": 0.7,
    }


def _correction_turn_output() -> dict[str, object]:
    return {
        "assistant_message": "收到，目标联系人改为老板本人，旧的财务负责人假设已废弃。",
        "actions": [
            {
                "type": "write_memory",
                "payload": {
                    "id": "mem_target_corrected",
                    "status": "confirmed",
                    "content": "目标联系人是老板本人，不是财务负责人",
                    "source": "user",
                    "evidence": ["纠正一下，不是财务负责人，是老板本人。"],
                    "confidence": 0.98,
                    "supersedes": ["mem_target_hypothesis"],
                    "tags": ["correction", "customer_intelligence"],
                },
            },
            {
                "type": "update_working_state",
                "payload": {"correction_summary": ["目标联系人已从财务负责人纠正为老板本人"]},
            },
            {
                "type": "update_customer_intelligence",
                "payload": {
                    "target_roles": ["老板本人"],
                    "ranking_reasons": ["用户纠正后优先围绕老板本人验证"],
                    "validation_signals": ["老板是否直接负责财税 SaaS 采购"],
                },
            },
        ],
        "reasoning_summary": "用户纠正目标联系人。",
        "confidence": 0.98,
    }


def _followup_turn_output() -> dict[str, object]:
    return {
        "assistant_message": "下一步建议只围绕老板本人设计首轮访谈，先验证采购触发点和预算判断。",
        "actions": [{"type": "no_op", "payload": {}}],
        "reasoning_summary": "根据纠错后的 active memory 给出建议。",
        "confidence": 0.86,
    }
