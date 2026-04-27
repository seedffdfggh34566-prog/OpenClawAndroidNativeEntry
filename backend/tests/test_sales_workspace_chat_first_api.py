from __future__ import annotations

import copy
import json
import os
from collections.abc import Generator
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from backend.api.config import reset_settings_cache
from backend.api.database import get_session_factory, reset_database_state
from backend.api.main import create_app

POSTGRES_VERIFY_ENV = "OPENCLAW_BACKEND_POSTGRES_VERIFY_URL"

EXAMPLE_DIR = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "reference"
    / "api"
    / "examples"
    / "sales_workspace_kernel_v0"
)


def test_chat_first_product_turn_creates_review_without_workspace_mutation(client) -> None:
    _create_workspace(client, "ws_demo")

    message = _post_message(
        client,
        workspace_id="ws_demo",
        message_id="msg_user_product_001",
        message_type="product_profile_update",
        content="我们做 FactoryOps AI，帮助制造企业协同排产、库存和 ERP。",
    )
    assert message["id"] == "msg_user_product_001"

    response = client.post(
        "/sales-workspaces/ws_demo/agent-runs/sales-agent-turns",
        json={
            "message_id": "msg_user_product_001",
            "base_workspace_version": 0,
            "instruction": "update product profile from chat",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["agent_run"]["id"] == "run_sales_turn_product_001"
    assert payload["agent_run"]["status"] == "succeeded"
    assert payload["context_pack"]["task_type"] == "sales_agent_turn"
    assert payload["patch_draft"]["operations"][0]["type"] == "upsert_product_profile_revision"
    assert payload["draft_review"]["status"] == "previewed"
    assert payload["draft_review"]["preview"]["would_mutate"] is False
    assert payload["assistant_message"]["message_type"] == "draft_summary"

    workspace_response = client.get("/sales-workspaces/ws_demo")
    assert workspace_response.status_code == 200
    workspace = workspace_response.json()["workspace"]
    assert workspace["workspace_version"] == 0
    assert workspace["product_profile_revisions"] == {}

    messages_response = client.get("/sales-workspaces/ws_demo/messages")
    assert messages_response.status_code == 200
    assert [message["id"] for message in messages_response.json()["messages"]] == [
        "msg_user_product_001",
        "msg_assistant_run_sales_turn_product_001",
    ]

    run_response = client.get("/sales-workspaces/ws_demo/agent-runs/run_sales_turn_product_001")
    assert run_response.status_code == 200
    assert "WorkspacePatchDraftReview:draft_review_sales_turn_product_profile_update_v1" in run_response.json()[
        "agent_run"
    ]["output_refs"]


def test_chat_first_review_apply_updates_product_and_direction(client) -> None:
    _create_workspace(client, "ws_demo")
    _run_chat_turn(
        client,
        workspace_id="ws_demo",
        message_id="msg_user_product_001",
        message_type="product_profile_update",
        content="FactoryOps AI 帮助制造企业协同排产、库存和 ERP。",
        base_workspace_version=0,
    )
    _accept_and_apply(client, "ws_demo", "draft_review_sales_turn_product_profile_update_v1", expected_version=1)

    _run_chat_turn(
        client,
        workspace_id="ws_demo",
        message_id="msg_user_direction_001",
        message_type="lead_direction_update",
        content="先找华东地区 100 到 500 人、有 ERP 但排产库存协同弱的制造企业。",
        base_workspace_version=1,
    )
    applied = _accept_and_apply(
        client,
        "ws_demo",
        "draft_review_sales_turn_lead_direction_update_v2",
        expected_version=2,
    )

    workspace = applied["workspace"]
    assert workspace["workspace_version"] == 2
    assert workspace["current_product_profile_revision_id"] == "ppr_chat_v1"
    assert workspace["current_lead_direction_version_id"] == "dir_chat_v2"
    assert workspace["commits"][-1]["changed_object_refs"] == [
        "LeadDirectionVersion:dir_chat_v2",
        "LeadDirectionVersion:dir_chat_v2",
    ]


def test_chat_first_out_of_scope_v2_2_does_not_create_draft(client) -> None:
    _create_workspace(client, "ws_demo")
    _post_message(
        client,
        workspace_id="ws_demo",
        message_id="msg_user_search_001",
        message_type="out_of_scope_v2_2",
        content="现在直接帮我联网搜索公司和联系人。",
    )

    response = client.post(
        "/sales-workspaces/ws_demo/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_search_001", "base_workspace_version": 0},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["patch_draft"] is None
    assert payload["draft_review"] is None
    assert payload["assistant_message"]["message_type"] == "out_of_scope_v2_2"
    assert payload["agent_run"]["output_refs"] == ["ConversationMessage:msg_assistant_run_sales_turn_search_001"]

    workspace_response = client.get("/sales-workspaces/ws_demo")
    assert workspace_response.status_code == 200
    assert workspace_response.json()["workspace"]["workspace_version"] == 0


def test_chat_first_version_conflict_records_failed_run_without_mutation(client) -> None:
    _create_workspace(client, "ws_demo")
    _post_message(
        client,
        workspace_id="ws_demo",
        message_id="msg_user_product_001",
        message_type="product_profile_update",
        content="FactoryOps AI 帮制造企业协同排产库存。",
    )

    response = client.post(
        "/sales-workspaces/ws_demo/agent-runs/sales-agent-turns",
        json={"message_id": "msg_user_product_001", "base_workspace_version": 1},
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "workspace_version_conflict"

    run_response = client.get("/sales-workspaces/ws_demo/agent-runs/run_sales_turn_product_001")
    assert run_response.status_code == 200
    run = run_response.json()["agent_run"]
    assert run["status"] == "failed"
    assert run["error"]["code"] == "workspace_version_conflict"

    workspace_response = client.get("/sales-workspaces/ws_demo")
    assert workspace_response.status_code == 200
    assert workspace_response.json()["workspace"]["workspace_version"] == 0


def test_chat_first_missing_workspace_and_message(client) -> None:
    missing_workspace = client.post(
        "/sales-workspaces/ws_missing/messages",
        json={
            "id": "msg_user_product_001",
            "message_type": "product_profile_update",
            "content": "missing workspace",
        },
    )
    assert missing_workspace.status_code == 404
    assert missing_workspace.json()["error"]["code"] == "not_found"

    _create_workspace(client, "ws_demo")
    missing_message = client.post(
        "/sales-workspaces/ws_demo/agent-runs/sales-agent-turns",
        json={"message_id": "msg_missing", "base_workspace_version": 0},
    )
    assert missing_message.status_code == 404
    assert missing_message.json()["error"]["details"]["object_type"] == "conversation_message"


@pytest.fixture
def postgres_chat_first_client(monkeypatch) -> Generator[TestClient, None, None]:
    database_url = os.environ.get(POSTGRES_VERIFY_ENV)
    if not database_url:
        pytest.skip(f"set {POSTGRES_VERIFY_ENV} to run Postgres chat-first verification")

    monkeypatch.setenv("OPENCLAW_BACKEND_DATABASE_URL", database_url)
    monkeypatch.setenv("OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_BACKEND", "postgres")
    monkeypatch.delenv("OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR", raising=False)
    reset_settings_cache()
    reset_database_state()
    with TestClient(create_app()) as client:
        yield client
    reset_database_state()
    reset_settings_cache()


def test_chat_first_postgres_trace_persists(postgres_chat_first_client) -> None:
    workspace_id = f"ws_chat_pg_{uuid4().hex[:12]}"
    _create_workspace(postgres_chat_first_client, workspace_id)

    _run_chat_turn(
        postgres_chat_first_client,
        workspace_id=workspace_id,
        message_id="msg_user_product_001",
        message_type="product_profile_update",
        content="FactoryOps AI 帮助制造企业协同排产库存。",
        base_workspace_version=0,
    )

    messages_response = postgres_chat_first_client.get(f"/sales-workspaces/{workspace_id}/messages")
    assert messages_response.status_code == 200
    assert len(messages_response.json()["messages"]) == 2

    run_response = postgres_chat_first_client.get(
        f"/sales-workspaces/{workspace_id}/agent-runs/run_sales_turn_product_001"
    )
    assert run_response.status_code == 200
    assert run_response.json()["agent_run"]["status"] == "succeeded"

    session = get_session_factory()()
    try:
        counts = {
            "messages": session.execute(
                text(
                    "select count(*) from sales_workspace_conversation_messages where workspace_id = :workspace_id"
                ),
                {"workspace_id": workspace_id},
            ).scalar_one(),
            "agent_runs": session.execute(
                text("select count(*) from sales_workspace_agent_runs where workspace_id = :workspace_id"),
                {"workspace_id": workspace_id},
            ).scalar_one(),
            "context_packs": session.execute(
                text("select count(*) from sales_workspace_context_packs where workspace_id = :workspace_id"),
                {"workspace_id": workspace_id},
            ).scalar_one(),
        }
    finally:
        session.close()

    assert counts == {"messages": 2, "agent_runs": 1, "context_packs": 1}


def _create_workspace(client: TestClient, workspace_id: str) -> None:
    response = client.post(
        "/sales-workspaces",
        json={
            **_example("01_create_workspace_request.json"),
            "workspace_id": workspace_id,
        },
    )
    assert response.status_code == 201


def _post_message(
    client: TestClient,
    *,
    workspace_id: str,
    message_id: str,
    message_type: str,
    content: str,
) -> dict:
    response = client.post(
        f"/sales-workspaces/{workspace_id}/messages",
        json={
            "id": message_id,
            "message_type": message_type,
            "content": content,
        },
    )
    assert response.status_code == 201
    return response.json()["message"]


def _run_chat_turn(
    client: TestClient,
    *,
    workspace_id: str,
    message_id: str,
    message_type: str,
    content: str,
    base_workspace_version: int,
) -> dict:
    _post_message(
        client,
        workspace_id=workspace_id,
        message_id=message_id,
        message_type=message_type,
        content=content,
    )
    response = client.post(
        f"/sales-workspaces/{workspace_id}/agent-runs/sales-agent-turns",
        json={
            "message_id": message_id,
            "base_workspace_version": base_workspace_version,
            "instruction": f"handle {message_type}",
        },
    )
    assert response.status_code == 200
    return response.json()


def _accept_and_apply(client: TestClient, workspace_id: str, draft_review_id: str, *, expected_version: int) -> dict:
    review_response = client.post(
        f"/sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/review",
        json={"decision": "accept", "reviewed_by": "android_demo_user", "client": "android"},
    )
    assert review_response.status_code == 200
    assert review_response.json()["draft_review"]["status"] == "reviewed"

    apply_response = client.post(
        f"/sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/apply",
        json={"requested_by": "android_demo_user"},
    )
    assert apply_response.status_code == 200
    payload = apply_response.json()
    assert payload["workspace"]["workspace_version"] == expected_version
    return payload


def _example(filename: str) -> dict:
    return json.loads((EXAMPLE_DIR / filename).read_text(encoding="utf-8"))


def _patch_example(filename: str, workspace_id: str) -> dict:
    payload = copy.deepcopy(_example(filename))
    payload["patch"]["workspace_id"] = workspace_id
    payload["patch"]["id"] = f'{payload["patch"]["id"]}_{workspace_id}'
    return payload
