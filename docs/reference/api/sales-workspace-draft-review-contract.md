# Sales Workspace Draft Review Contract

更新时间：2026-04-27

## 1. 文档定位

本文档定义 V2 Sales Workspace 的 `WorkspacePatchDraft` review contract。

本 contract 是下一阶段的接口与对象语义基线，用于把当前 prototype 中“Android 临时持有 raw draft 并回传 apply”的流程，升级为 backend-managed review object 语义。

本文档不是：

- production FastAPI route implementation
- SQLAlchemy / Alembic migration
- Android UI implementation
- LangGraph graph implementation
- real LLM / search / contact / CRM contract
- production persistence baseline

当前已有 prototype：

- `POST /sales-workspaces/{workspace_id}/runtime/patch-drafts/prototype/preview`
- `POST /sales-workspaces/{workspace_id}/runtime/patch-drafts/prototype/apply`

当前已实现 Draft review routes prototype：

- `POST /sales-workspaces/{workspace_id}/draft-reviews`
- `GET /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}`
- `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/review`
- `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/apply`
- `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/reject`

这些 endpoint 仍是 prototype routes。它们不表示 production persistence baseline、正式 Runtime / LangGraph 集成或 Android draft review id flow 已完成。

---

## 2. 总体原则

### 2.1 Runtime 只产出 draft

Runtime / Product Sales Agent execution layer 只能产出 `WorkspacePatchDraft`。

Runtime 不直接写：

- formal workspace objects
- `WorkspacePatch`
- ranking board
- Markdown projection
- ContextPack

### 2.2 Backend 管理 review object

下一阶段目标是引入 backend-managed review object：

```text
WorkspacePatchDraft
-> WorkspacePatchDraftReview
-> reviewed / rejected / applied
-> materialized WorkspacePatch
-> Sales Workspace Kernel apply
```

`WorkspacePatchDraftReview` 是审阅状态对象，不是 workspace 主存对象。

### 2.3 Sales Workspace Kernel 仍是正式写回裁决层

正式业务对象写回仍必须经过：

```text
WorkspacePatch -> backend validation -> SalesWorkspace structured state
```

Draft review object 不绕过 kernel，也不直接修改 generated Markdown、ranking board 或 ContextPack。

### 2.4 本 contract 不改变 persistence baseline

本文档允许定义 draft review object 语义，但不承诺：

- DB-backed persistence
- SQLAlchemy ORM
- Alembic migration
- SQLite schema
- Postgres / pgvector

当前 `JSON file store` 可继续支撑 prototype demo，但不是正式 persistence baseline。

---

## 3. Object Shape

### 3.1 `WorkspacePatchDraft`

`WorkspacePatchDraft` 是 Runtime output payload。

最小字段：

```text
id
workspace_id
base_workspace_version
operations[]
author
instruction
runtime_metadata
```

约束：

- `operations[]` 必须非空。
- `workspace_id` 必须匹配 target workspace。
- `base_workspace_version` 用于 optimistic version check。
- `runtime_metadata` 可记录 provider、mode、trace id、tool run id，但不能作为正式 workspace 主存。

### 3.2 `WorkspacePatchDraftReview`

`WorkspacePatchDraftReview` 是 backend-managed review object。

建议字段：

```text
id
workspace_id
draft
status
base_workspace_version
created_by
created_at
instruction
runtime_metadata
preview
review
apply_result
expires_at
updated_at
```

字段说明：

| field | meaning |
|---|---|
| `id` | review object id，例如 `draft_review_runtime_v4` |
| `workspace_id` | target workspace |
| `draft` | original `WorkspacePatchDraft` payload |
| `status` | lifecycle status |
| `base_workspace_version` | copied from draft |
| `created_by` | `runtime_patchdraft_prototype` or future runtime id |
| `created_at` | backend create time |
| `instruction` | user / runtime instruction snapshot |
| `runtime_metadata` | copied runtime metadata |
| `preview` | materialized patch preview and derived ranking preview |
| `review` | reviewer decision metadata |
| `apply_result` | apply success / failure metadata |
| `expires_at` | optional stale review cutoff |
| `updated_at` | latest backend update time |

### 3.3 Lifecycle Status

Allowed status values:

| status | meaning | allowed next |
|---|---|---|
| `previewed` | draft was generated and previewed, no human decision yet | `reviewed`, `rejected`, `expired` |
| `reviewed` | human or client explicitly accepted the draft for apply | `applied`, `expired` |
| `applied` | materialized patch was applied by Sales Workspace Kernel | terminal |
| `rejected` | reviewer rejected the draft | terminal |
| `expired` | draft can no longer be applied because workspace version or time window is stale | terminal |

Rules:

- Only `reviewed` draft reviews may be applied.
- `applied`, `rejected`, and `expired` are terminal.
- `previewed` may not mutate workspace state.
- A stale `previewed` or `reviewed` draft must not be applied.

### 3.4 `preview`

`preview` captures derived, non-mutating outputs.

Suggested shape:

```json
{
  "materialized_patch": {
    "id": "patch_runtime_v4",
    "workspace_id": "ws_demo",
    "base_workspace_version": 3,
    "operations": []
  },
  "preview_workspace_version": 4,
  "preview_ranking_board": {
    "ranked_items": []
  },
  "would_mutate": false,
  "generated_at": "2026-04-27T00:00:00Z"
}
```

Rules:

- `preview` is derived from structured workspace state plus draft.
- `preview` must not save workspace changes.
- `preview_ranking_board` is a derived view, not a writable object.

### 3.5 `review`

`review` captures explicit reviewer decision metadata.

Suggested shape:

```json
{
  "reviewed_by": "android_demo_user",
  "reviewed_at": "2026-04-27T00:00:00Z",
  "decision": "accept",
  "comment": "Looks good for demo apply.",
  "client": "android"
}
```

Allowed decisions:

- `accept`
- `reject`

### 3.6 `apply_result`

`apply_result` captures the result of kernel apply.

Suggested success shape:

```json
{
  "status": "applied",
  "materialized_patch_id": "patch_runtime_v4",
  "workspace_version": 4,
  "ranking_impact_summary": {
    "top_candidate_id": "cand_runtime_001",
    "top_candidate_name": "Runtime Draft Co"
  },
  "applied_at": "2026-04-27T00:00:00Z"
}
```

Suggested failure shape:

```json
{
  "status": "failed",
  "error_code": "workspace_version_conflict",
  "error_message": "base_workspace_version does not match current workspace_version",
  "failed_at": "2026-04-27T00:00:00Z"
}
```

Rules:

- Failed apply must not partially mutate workspace.
- `apply_result` failure does not make the draft valid for retry unless the contract explicitly creates a new draft review.

---

## 4. Prototype API Contract

这些 endpoints 已作为 prototype routes 实现，用于验证 backend-managed draft review object 语义。

当前实现边界：

- 使用 app-local in-memory store 或可选 JSON file store。
- 不使用 SQLAlchemy ORM。
- 不新增 Alembic migration。
- 不改变正式 persistence baseline。
- 不接正式 LangGraph graph、真实 LLM、search、contact 或 CRM。

### 4.1 `POST /sales-workspaces/{workspace_id}/draft-reviews`

Create a backend-managed draft review object from a `WorkspacePatchDraft`.

Request:

```json
{
  "patch_draft": {
    "id": "draft_runtime_v4",
    "workspace_id": "ws_demo",
    "base_workspace_version": 3,
    "operations": []
  }
}
```

Response `201`:

```json
{
  "draft_review": {
    "id": "draft_review_runtime_v4",
    "workspace_id": "ws_demo",
    "status": "previewed",
    "base_workspace_version": 3,
    "draft": {
      "id": "draft_runtime_v4"
    },
    "preview": {
      "preview_workspace_version": 4,
      "would_mutate": false
    }
  }
}
```

Errors:

- `404 not_found`
- `409 workspace_version_conflict`
- `422 patchdraft_validation_error`
- `422 validation_error`

### 4.2 `GET /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}`

Read a draft review object.

Response `200`:

```json
{
  "draft_review": {
    "id": "draft_review_runtime_v4",
    "status": "previewed"
  }
}
```

Errors:

- `404 not_found`

### 4.3 `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/review`

Record explicit reviewer decision.

Accept request:

```json
{
  "decision": "accept",
  "reviewed_by": "android_demo_user",
  "comment": "Looks good."
}
```

Reject request:

```json
{
  "decision": "reject",
  "reviewed_by": "android_demo_user",
  "comment": "Candidate evidence is not enough."
}
```

Response `200`:

```json
{
  "draft_review": {
    "id": "draft_review_runtime_v4",
    "status": "reviewed"
  }
}
```

Rules:

- `decision=accept` changes status from `previewed` to `reviewed`.
- `decision=reject` changes status from `previewed` to `rejected`.
- Terminal statuses cannot be reviewed again.

Errors:

- `404 not_found`
- `409 draft_review_state_conflict`
- `409 workspace_version_conflict`
- `422 validation_error`

### 4.4 `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/apply`

Apply a reviewed draft through Sales Workspace Kernel.

Request:

```json
{
  "requested_by": "android_demo_user"
}
```

Response `200`:

```json
{
  "draft_review": {
    "id": "draft_review_runtime_v4",
    "status": "applied"
  },
  "patch": {
    "id": "patch_runtime_v4"
  },
  "workspace": {
    "id": "ws_demo",
    "workspace_version": 4
  },
  "ranking_board": {
    "ranked_items": [
      {
        "candidate_id": "cand_runtime_001",
        "rank": 1
      }
    ]
  }
}
```

Rules:

- Only `reviewed` draft reviews may be applied.
- Apply must check current workspace version against `base_workspace_version`.
- Apply must materialize `WorkspacePatch` server-side.
- Apply must use Sales Workspace Kernel validation and writeback.
- Apply must update `apply_result`.

Errors:

- `404 not_found`
- `409 draft_review_state_conflict`
- `409 workspace_version_conflict`
- `400 unsupported_workspace_operation`
- `422 patchdraft_validation_error`

### 4.5 `POST /sales-workspaces/{workspace_id}/draft-reviews/{draft_review_id}/reject`

Convenience endpoint to reject a draft without using the generic review endpoint.

Request:

```json
{
  "rejected_by": "android_demo_user",
  "reason": "Not enough source evidence."
}
```

Response `200`:

```json
{
  "draft_review": {
    "id": "draft_review_runtime_v4",
    "status": "rejected"
  }
}
```

Errors:

- `404 not_found`
- `409 draft_review_state_conflict`
- `422 validation_error`

---

## 5. Error Semantics

| HTTP status | code | meaning |
|---:|---|---|
| 400 | `unsupported_workspace_operation` | materialized patch contains unsupported operation |
| 404 | `not_found` | workspace or draft review not found |
| 409 | `workspace_version_conflict` | draft base version does not match current workspace version |
| 409 | `draft_review_state_conflict` | requested transition is not allowed |
| 409 | `draft_review_expired` | draft review is expired and cannot be applied |
| 422 | `patchdraft_validation_error` | draft payload is invalid |
| 422 | `validation_error` | request body or path/body relationship is invalid |

Stale draft rule:

- If current workspace version differs from `base_workspace_version`, apply must fail with `workspace_version_conflict`.
- A stale draft may be marked `expired`.
- Clients should create a new draft review from a fresh workspace version.

Rejected draft rule:

- `rejected` draft reviews are terminal.
- Applying a rejected draft returns `409 draft_review_state_conflict`.

Applied draft rule:

- `applied` draft reviews are terminal.
- Re-applying an applied draft returns `409 draft_review_state_conflict`.

---

## 6. Android / Runtime Responsibility Boundary

### Android

Future Android should prefer:

```text
GET / draft review id
-> display preview
-> POST review accept / reject
-> POST apply by draft_review_id
```

Android should not:

- construct formal workspace objects
- construct `WorkspacePatch`
- write ranking board
- write Markdown projection
- write ContextPack

Current Android prototype may continue to pass raw `patch_draft` back to the prototype apply endpoint until a separate Android task switches it to the `draft_review_id` flow.

### Runtime / LangGraph Runtime

Runtime may produce:

- `WorkspacePatchDraft`
- runtime metadata
- tool outputs
- trace ids

Runtime must not own:

- formal workspace writeback
- review status
- apply result
- DB transaction
- generated Markdown writeback

### Backend / Sales Workspace Kernel

Backend owns:

- draft review object lifecycle
- materializing draft into `WorkspacePatch`
- validating operations
- optimistic version check
- formal workspace writeback
- derived ranking / projection / ContextPack

---

## 7. Persistence Decision

This contract requires backend-managed review object semantics.

It does not require immediate DB-backed persistence.

Allowed next prototype path:

- Store draft review objects in the existing optional JSON file store for local demo continuity.
- Keep this clearly marked as prototype storage.

Before production persistence, refresh `ADR-007` and decide:

- SQLite / Alembic
- Postgres
- continued prototype JSON store
- another persistence baseline

---

## 8. Non-Goals

This contract does not open:

- production backend route implementation
- SQLAlchemy ORM
- Alembic migration
- SQLite schema
- Postgres / pgvector
- Android UI changes
- formal LangGraph graph
- real LLM / search / contact / CRM
- production persistence baseline
