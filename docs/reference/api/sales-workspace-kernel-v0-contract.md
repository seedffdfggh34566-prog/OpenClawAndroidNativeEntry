# Sales Workspace Kernel API Contract v0

更新时间：2026-04-27

## 1. 文档定位

本文档定义 V2.1 Sales Workspace Kernel 的最小 backend API contract。

本 contract 服务于后续 FastAPI implementation、Android read-only workspace view、Runtime / LangGraph integration 的边界对齐。

本文档不是：

- FastAPI route implementation
- SQLAlchemy ORM / Alembic migration
- Android UI contract
- Runtime / LangGraph graph contract
- LLM / search provider contract
- CRM / ContactPoint / 自动触达 contract

关联实现基线：

- `backend/sales_workspace/schemas.py`
- `backend/sales_workspace/patches.py`
- `backend/sales_workspace/ranking.py`
- `backend/sales_workspace/projection.py`
- `backend/sales_workspace/context_pack.py`

关联任务：

- `docs/delivery/tasks/task_v2_sales_workspace_api_contract_v0.md`
- `docs/delivery/tasks/task_v2_sales_workspace_persistence_decision.md`

---

## 2. 总体原则

### 2.1 后端是 formal truth layer

Sales Workspace 的正式业务对象以后端结构化对象为准。

Android、Runtime、LangGraph checkpoint、LLM session、Markdown projection 都不是正式主存。

### 2.2 WorkspacePatch 是唯一写入口

所有 workspace 状态变更必须通过：

```text
WorkspacePatch -> backend validation -> SalesWorkspace structured state
```

API v0 不提供按对象直接写入 ranking board、Markdown projection、ContextPack 的接口。

### 2.3 Derived views 只读

以下对象由 Sales Workspace Kernel 从结构化 state 派生：

- `CandidateRankingBoard`
- Markdown projection
- `ContextPack`

客户端只能读取或请求编译，不能直接写入这些 derived views。

### 2.4 v0 不定义 persistence

本 contract 不承诺具体 persistence baseline。

后续由 `task_v2_sales_workspace_persistence_decision.md` 决定：

- 继续 in-memory / JSON fixture
- SQLite / Alembic
- 延后 DB persistence

---

## 3. 通用响应与错误

### 3.1 JSON 与时间

- 请求和响应使用 JSON。
- 时间字段使用 ISO 8601 string。
- 对象字段语义对齐 `backend/sales_workspace` Pydantic models。

### 3.2 Error envelope

错误响应最小结构：

```json
{
  "error": {
    "code": "workspace_version_conflict",
    "message": "base_workspace_version does not match current workspace_version",
    "details": {
      "workspace_id": "ws_demo",
      "current_workspace_version": 3,
      "base_workspace_version": 2
    }
  }
}
```

### 3.3 Error codes

| HTTP status | code | 触发条件 |
|---:|---|---|
| 400 | `unsupported_workspace_operation` | `WorkspaceOperation.type` 不在 v0 支持列表 |
| 404 | `not_found` | workspace 或必要引用对象不存在 |
| 409 | `workspace_version_conflict` | `base_workspace_version` 与当前 `workspace_version` 不匹配 |
| 422 | `validation_error` | 请求体结构、字段类型、枚举值或引用关系校验失败 |

v0 不定义 auth error、rate limit error、tenant permission error。

---

## 4. Object Shape

### 4.1 `SalesWorkspace`

响应 shape 对齐 `SalesWorkspace` Pydantic model，最小字段包括：

```text
id
workspace_key
owner_id
name
goal
status
workspace_version
current_product_profile_revision_id
current_lead_direction_version_id
current_candidate_ranking_board_id
latest_research_round_id
product_profile_revisions
lead_direction_versions
research_rounds
research_sources
company_candidates
candidate_observations
ranking_board
commits
created_at
updated_at
```

### 4.2 `WorkspacePatch`

请求 shape 对齐 `WorkspacePatch` Pydantic model：

```text
id
workspace_id
base_workspace_version
operations[]
author
message
created_at
```

`operations[]` item：

```text
type
payload
```

v0 支持 operation types：

- `upsert_product_profile_revision`
- `upsert_lead_direction_version`
- `upsert_research_round`
- `upsert_research_source`
- `upsert_company_candidate`
- `upsert_candidate_observation`
- `archive_candidate`
- `set_active_lead_direction`

### 4.3 `CandidateRankingBoard`

响应 shape 对齐 `CandidateRankingBoard` Pydantic model。

`ranked_items[]` 最小字段：

```text
candidate_id
candidate_name
rank
score
status
reason
supporting_observation_ids
score_breakdown
```

`deltas[]` 最小字段：

```text
candidate_id
previous_rank
new_rank
previous_score
new_score
reason
supporting_observation_ids
```

### 4.4 Markdown projection

Projection response 是 map：

```json
{
  "workspace_id": "ws_demo",
  "workspace_version": 4,
  "files": {
    "product/current.md": "...",
    "directions/current.md": "...",
    "rankings/current.md": "..."
  }
}
```

Markdown projection 只从 structured state 渲染，不支持 parse-back。

### 4.5 `ContextPack`

响应 shape 对齐 `ContextPack` Pydantic model。

v0 只支持：

```text
task_type = research_round
```

---

## 5. Endpoint Contract

## 5.1 `POST /sales-workspaces`

创建一个 workspace。

### Request

```json
{
  "workspace_id": "ws_demo",
  "name": "Demo sales workspace",
  "goal": "Find source-backed manufacturing ERP candidates",
  "owner_id": "local_user",
  "workspace_key": "local_default"
}
```

### Response `201`

```json
{
  "workspace": {
    "id": "ws_demo",
    "workspace_key": "local_default",
    "owner_id": "local_user",
    "name": "Demo sales workspace",
    "goal": "Find source-backed manufacturing ERP candidates",
    "status": "active",
    "workspace_version": 0
  }
}
```

### Notes

- v0 不定义 auth / tenant resolution。
- `workspace_id` 可以由客户端传入或由后续 implementation 生成；implementation 必须在 API 文档中固定其选择。

---

## 5.2 `GET /sales-workspaces/{workspace_id}`

读取完整 workspace structured state。

### Response `200`

```json
{
  "workspace": {
    "id": "ws_demo",
    "workspace_version": 4,
    "current_product_profile_revision_id": "prod_v1",
    "current_lead_direction_version_id": "dir_v1",
    "current_candidate_ranking_board_id": "board_v4",
    "ranking_board": {}
  }
}
```

### Errors

- `404 not_found`

---

## 5.3 `POST /sales-workspaces/{workspace_id}/patches`

应用 `WorkspacePatch`，并返回更新后的 workspace、commit 和 derived ranking board。

### Request

```json
{
  "patch": {
    "id": "patch_round_2",
    "workspace_id": "ws_demo",
    "base_workspace_version": 3,
    "author": "local_user",
    "message": "Round 2 stronger candidate",
    "operations": [
      {
        "type": "upsert_company_candidate",
        "payload": {
          "id": "cand_d",
          "name": "D Company",
          "summary": "Zhejiang manufacturer with urgent operations pressure.",
          "round_ids": ["rr_002"]
        }
      }
    ]
  }
}
```

### Response `200`

```json
{
  "workspace": {
    "id": "ws_demo",
    "workspace_version": 4
  },
  "commit": {
    "id": "commit_v4",
    "workspace_id": "ws_demo",
    "patch_id": "patch_round_2",
    "workspace_version": 4
  },
  "ranking_board": {
    "id": "board_v4",
    "workspace_id": "ws_demo",
    "workspace_version": 4
  }
}
```

### Errors

- `400 unsupported_workspace_operation`
- `404 not_found`
- `409 workspace_version_conflict`
- `422 validation_error`

### Notes

- `workspace_id` path parameter and `patch.workspace_id` must match.
- `base_workspace_version` mismatch must not mutate workspace state.
- `CandidateRankingBoard` is regenerated by backend after successful patch.

---

## 5.4 `GET /sales-workspaces/{workspace_id}/ranking-board/current`

读取当前 derived ranking board。

### Response `200`

```json
{
  "ranking_board": {
    "id": "board_v4",
    "workspace_id": "ws_demo",
    "workspace_version": 4,
    "ranked_items": [],
    "deltas": []
  }
}
```

### Errors

- `404 not_found`

---

## 5.5 `GET /sales-workspaces/{workspace_id}/projection`

渲染并返回 Markdown projection。

### Response `200`

```json
{
  "workspace_id": "ws_demo",
  "workspace_version": 4,
  "files": {
    "product/current.md": "---\ngenerated: true\n---\n# Product\n",
    "rankings/current.md": "---\ngenerated: true\n---\n# Current Rankings\n"
  }
}
```

### Errors

- `404 not_found`

### Notes

- v0 不支持 Markdown parse-back。
- Product Sales Agent / Runtime 不得直接编辑 generated Markdown 来污染主存。

---

## 5.6 `POST /sales-workspaces/{workspace_id}/context-packs`

从 structured workspace state 编译 ContextPack。

### Request

```json
{
  "task_type": "research_round",
  "token_budget_chars": 6000,
  "top_n_candidates": 5
}
```

### Response `200`

```json
{
  "context_pack": {
    "id": "ctx_ws_demo_v4",
    "workspace_id": "ws_demo",
    "task_type": "research_round",
    "token_budget_chars": 6000,
    "product_summary": "...",
    "current_direction": "...",
    "top_candidates": [],
    "recent_ranking_delta": [],
    "open_questions": [],
    "kernel_boundary": "Runtime / Product Sales Agent execution layer returns WorkspacePatchDraft; Sales Workspace Kernel validates and writes formal objects."
  }
}
```

### Errors

- `404 not_found`
- `422 validation_error`

### Notes

- v0 only supports `task_type = research_round`.
- ContextPack is compiled from structured state, not Markdown projection.

---

## 6. Implementation Gates

Before implementing backend API v0:

1. Complete `task_v2_sales_workspace_persistence_decision.md`.
2. Decide whether API v0 uses in-memory / JSON fixture or SQLite / Alembic.
3. Keep `backend/sales_workspace` as the object and validation source.
4. Add route tests for success, validation error, not found, unsupported operation and version conflict.

Do not implement Android read-only view or Runtime / LangGraph integration before backend API v0 is available.
