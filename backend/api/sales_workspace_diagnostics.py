from __future__ import annotations

from typing import Any

from fastapi import Request

from backend.sales_workspace.projection import render_markdown_projection
from backend.sales_workspace.store import WorkspaceNotFound


def _model_json(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [_model_json(item) for item in value]
    if isinstance(value, dict):
        return {key: _model_json(item) for key, item in value.items()}
    return value


def _preview(value: str, limit: int = 180) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "..."


def _workspace_store(request: Request) -> Any:
    return request.app.state.sales_workspace_store


def _chat_trace_store(request: Request) -> Any:
    return request.app.state.sales_workspace_chat_trace_store


def _draft_review_store(request: Request) -> Any:
    return request.app.state.sales_workspace_draft_review_store


def list_sales_workspace_diagnostics(request: Request) -> dict[str, Any]:
    workspaces = _workspace_store(request).list_workspaces()
    chat_store = _chat_trace_store(request)
    summaries = []
    for workspace in workspaces:
        threads = chat_store.list_threads(workspace.id, ensure_default=False)
        summaries.append(
            {
                "id": workspace.id,
                "name": workspace.name,
                "status": workspace.status,
                "workspace_version": workspace.workspace_version,
                "updated_at": workspace.updated_at,
                "current_product_profile_revision_id": workspace.current_product_profile_revision_id,
                "current_lead_direction_version_id": workspace.current_lead_direction_version_id,
                "current_candidate_ranking_board_id": workspace.current_candidate_ranking_board_id,
                "latest_research_round_id": workspace.latest_research_round_id,
                "thread_count": len(threads),
                "latest_thread_title": threads[0].title if threads else "",
            }
        )
    return {
        "workspaces": summaries
    }


def get_sales_workspace_diagnostics(request: Request, workspace_id: str) -> dict[str, Any]:
    workspace = _workspace_store(request).get(workspace_id)
    chat_store = _chat_trace_store(request)
    draft_store = _draft_review_store(request)

    threads = chat_store.list_threads(workspace_id, ensure_default=False)
    thread_summaries = []
    recent_messages: dict[str, list[dict[str, Any]]] = {}
    for thread in threads:
        messages = chat_store.list_messages(workspace_id, thread.id)
        thread_summaries.append(
            {
                "id": thread.id,
                "title": thread.title,
                "status": thread.status,
                "message_count": len(messages),
                "latest_message_preview": _preview(messages[-1].content) if messages else "",
                "created_at": thread.created_at,
                "updated_at": thread.updated_at,
            }
        )
        recent_messages[thread.id] = [
            {
                "id": message.id,
                "thread_id": message.thread_id,
                "role": message.role,
                "message_type": message.message_type,
                "content_preview": _preview(message.content),
                "linked_object_refs": message.linked_object_refs,
                "created_by_agent_run_id": message.created_by_agent_run_id,
                "created_at": message.created_at,
            }
            for message in messages[-20:]
        ]

    agent_runs = chat_store.list_agent_runs(workspace_id)
    context_packs = chat_store.list_context_packs(workspace_id)
    draft_reviews = draft_store.list_draft_reviews(workspace_id)
    projection = render_markdown_projection(workspace)

    return {
        "workspace": {
            "id": workspace.id,
            "workspace_key": workspace.workspace_key,
            "owner_id": workspace.owner_id,
            "name": workspace.name,
            "goal": workspace.goal,
            "status": workspace.status,
            "workspace_version": workspace.workspace_version,
            "current_product_profile_revision_id": workspace.current_product_profile_revision_id,
            "current_lead_direction_version_id": workspace.current_lead_direction_version_id,
            "current_candidate_ranking_board_id": workspace.current_candidate_ranking_board_id,
            "latest_research_round_id": workspace.latest_research_round_id,
            "created_at": workspace.created_at,
            "updated_at": workspace.updated_at,
        },
        "object_counts": {
            "product_profile_revisions": len(workspace.product_profile_revisions),
            "lead_direction_versions": len(workspace.lead_direction_versions),
            "research_rounds": len(workspace.research_rounds),
            "research_sources": len(workspace.research_sources),
            "company_candidates": len(workspace.company_candidates),
            "candidate_observations": len(workspace.candidate_observations),
            "commits": len(workspace.commits),
            "threads": len(threads),
            "agent_runs": len(agent_runs),
            "context_packs": len(context_packs),
            "draft_reviews": len(draft_reviews),
            "projection_files": len(projection),
        },
        "formal_objects": {
            "product_profile_revisions": _model_json(workspace.product_profile_revisions),
            "lead_direction_versions": _model_json(workspace.lead_direction_versions),
            "research_rounds": _model_json(workspace.research_rounds),
            "research_sources": _model_json(workspace.research_sources),
            "company_candidates": _model_json(workspace.company_candidates),
            "candidate_observations": _model_json(workspace.candidate_observations),
            "ranking_board": _model_json(workspace.ranking_board),
            "commits": _model_json(workspace.commits),
        },
        "chat": {
            "threads": thread_summaries,
            "recent_messages_by_thread": recent_messages,
            "agent_runs": _model_json(agent_runs),
            "context_packs": _model_json(context_packs),
        },
        "draft_reviews": _model_json(draft_reviews),
        "projection": {
            "files": projection,
            "file_keys": sorted(projection.keys()),
        },
        "raw_workspace": _model_json(workspace),
    }


def workspace_not_found_payload(workspace_id: str) -> dict[str, Any]:
    return {
        "error": {
            "code": "not_found",
            "message": "sales workspace not found",
            "details": {"workspace_id": workspace_id},
        }
    }


def is_workspace_not_found(exc: Exception) -> bool:
    return isinstance(exc, WorkspaceNotFound)


def sales_workspace_inspector_html() -> str:
    return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>OpenClaw Sales Workspace Diagnostics</title>
  <style>
    body { font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 24px; color: #1f2937; background: #f8fafc; }
    main { display: grid; grid-template-columns: minmax(280px, 420px) minmax(0, 1fr); gap: 16px; }
    button { display: block; width: 100%; padding: 10px 12px; margin: 0 0 8px; text-align: left; border: 1px solid #cbd5e1; background: #fff; border-radius: 6px; cursor: pointer; }
    button:hover { border-color: #2563eb; }
    pre { padding: 16px; overflow: auto; background: #0f172a; color: #e2e8f0; border-radius: 6px; white-space: pre-wrap; word-break: break-word; }
    .meta { color: #64748b; font-size: 13px; margin: 4px 0 0; }
    .toolbar { margin-bottom: 16px; display: flex; gap: 8px; align-items: center; }
    .toolbar button { width: auto; margin: 0; }
    .detail-grid { display: grid; gap: 14px; }
    .panel { background: #fff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 14px; }
    .panel h3 { margin: 0 0 10px; font-size: 18px; }
    .kv { display: grid; grid-template-columns: 190px minmax(0, 1fr); gap: 6px 12px; font-size: 14px; }
    .kv div:nth-child(odd) { color: #64748b; }
    .pill { display: inline-block; border: 1px solid #cbd5e1; border-radius: 999px; padding: 2px 8px; margin: 0 6px 6px 0; font-size: 12px; color: #334155; background: #f8fafc; }
    .json-content { max-height: 420px; }
  </style>
</head>
<body>
  <h1>OpenClaw Sales Workspace Diagnostics</h1>
  <div class="toolbar">
    <button type="button" onclick="loadWorkspaces()">Refresh</button>
    <span class="meta">Dev-only read-only workspace state viewer</span>
  </div>
  <main>
    <section>
      <h2>Workspaces</h2>
      <div id="workspaces">Loading...</div>
    </section>
    <section>
      <h2>Detail</h2>
      <div id="detail" class="detail-grid">
        <pre>Select a workspace.</pre>
      </div>
    </section>
  </main>
  <script>
    async function loadWorkspaces() {
      const container = document.getElementById("workspaces");
      container.textContent = "Loading...";
      const response = await fetch("/dev/sales-workspaces");
      const payload = await response.json();
      const workspaces = payload.workspaces || [];
      if (!workspaces.length) {
        container.textContent = "No workspaces found.";
        return;
      }
      container.innerHTML = "";
      for (const workspace of workspaces) {
        const button = document.createElement("button");
        button.innerHTML = `<strong>${workspace.name}</strong><div class="meta">${workspace.id} - v${workspace.workspace_version} - ${workspace.status}</div>`;
        button.onclick = () => loadDetail(workspace.id);
        container.appendChild(button);
      }
    }

    async function loadDetail(workspaceId) {
      const response = await fetch(`/dev/sales-workspaces/${encodeURIComponent(workspaceId)}/diagnostics`);
      const payload = await response.json();
      renderDetail(payload);
    }

    function appendPanel(container, title, content) {
      const panel = document.createElement("section");
      panel.className = "panel";
      const heading = document.createElement("h3");
      heading.textContent = title;
      const pre = document.createElement("pre");
      pre.className = "json-content";
      pre.textContent = typeof content === "string" ? content : JSON.stringify(content, null, 2);
      panel.appendChild(heading);
      panel.appendChild(pre);
      container.appendChild(panel);
    }

    function renderDetail(payload) {
      const container = document.getElementById("detail");
      container.innerHTML = "";
      if (payload.error) {
        appendPanel(container, "Error", payload.error);
        return;
      }

      const summary = document.createElement("section");
      summary.className = "panel";
      const heading = document.createElement("h3");
      heading.textContent = "Workspace Summary";
      const kv = document.createElement("div");
      kv.className = "kv";
      const workspace = payload.workspace || {};
      const fields = [
        ["workspace_id", workspace.id],
        ["name", workspace.name],
        ["status", workspace.status],
        ["workspace_version", workspace.workspace_version],
        ["current_product_profile_revision_id", workspace.current_product_profile_revision_id || "-"],
        ["current_lead_direction_version_id", workspace.current_lead_direction_version_id || "-"],
        ["current_candidate_ranking_board_id", workspace.current_candidate_ranking_board_id || "-"],
        ["latest_research_round_id", workspace.latest_research_round_id || "-"],
        ["updated_at", workspace.updated_at],
      ];
      for (const [label, value] of fields) {
        const key = document.createElement("div");
        key.textContent = label;
        const val = document.createElement("div");
        val.textContent = value == null ? "-" : String(value);
        kv.appendChild(key);
        kv.appendChild(val);
      }
      summary.appendChild(heading);
      summary.appendChild(kv);
      container.appendChild(summary);

      const counts = document.createElement("section");
      counts.className = "panel";
      const countsHeading = document.createElement("h3");
      countsHeading.textContent = "Object Counts";
      counts.appendChild(countsHeading);
      for (const [key, value] of Object.entries(payload.object_counts || {})) {
        const pill = document.createElement("span");
        pill.className = "pill";
        pill.textContent = `${key}: ${value}`;
        counts.appendChild(pill);
      }
      container.appendChild(counts);

      appendPanel(container, "Formal Objects", payload.formal_objects || {});
      appendPanel(container, "Threads and Recent Messages", payload.chat || {});
      appendPanel(container, "Draft Reviews", payload.draft_reviews || []);
      appendPanel(container, "Projection Files", payload.projection || {});
      appendPanel(container, "Raw Diagnostics JSON", payload);
    }

    loadWorkspaces();
  </script>
</body>
</html>"""
