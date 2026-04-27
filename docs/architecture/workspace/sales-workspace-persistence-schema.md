# Sales Workspace Persistence Schema

更新时间：2026-04-27

## 1. Purpose

本文档定义 V2 Sales Workspace 的正式 persistence schema design。

本设计基于：

- V2 MVP persistence baseline：Postgres / Alembic。
- 当前 Sales Workspace Kernel Pydantic object model。
- Draft Review ID flow 与 backend-managed review routes prototype。

本文档只定义 schema 形状和边界，不实现 SQLAlchemy ORM、Alembic migration、backend route、Android UI 或 Runtime / LangGraph。

---

## 2. Design Summary

V2 Sales Workspace persistence schema 采用：

> **relational core + JSONB payload snapshots**

含义：

- relational core 保存对象身份、归属、状态、版本、时间、外键和常用查询字段。
- JSONB payload snapshots 保存当前 Pydantic object payload，降低早期 schema 变更成本。
- Postgres constraint / index 负责基础完整性；复杂业务校验仍由 Sales Workspace Kernel 执行。
- Alembic migration 后续必须以本文档为首版 schema 输入，但本任务不写 migration。

设计目标：

- 支持 multi-workspace。
- 支持 `workspace_version` optimistic concurrency。
- 支持 WorkspacePatch append-only audit。
- 支持 Draft Review 长期 audit history。
- 保持 RankingBoard、Markdown projection、ContextPack 为 derived outputs。

---

## 3. Naming And Object Mapping

当前 Python object 与首版表名映射：

| Python / contract object | Persistence table |
|---|---|
| `SalesWorkspace` | `sales_workspaces` |
| `ProductProfileRevision` | `sales_workspace_product_profile_revisions` |
| `LeadDirectionVersion` | `sales_workspace_lead_directions` |
| `CompanyCandidate` | `sales_workspace_lead_candidates` |
| `ResearchRound` | persisted through patch commits initially; dedicated table deferred |
| `ResearchSource` | `sales_workspace_research_sources` |
| `CandidateObservation` | `sales_workspace_research_observations` |
| `WorkspacePatch` / `WorkspaceCommit` | `sales_workspace_patch_commits` |
| `WorkspacePatchDraftReview` | `sales_workspace_draft_reviews` |
| Draft review lifecycle transition | `sales_workspace_draft_review_events` |

`ResearchRound` remains a formal kernel object, but first persistence migration should avoid adding a dedicated table unless route / query requirements need it. Its payload can be preserved through `patch_json` and object payload snapshots. A later migration may add `sales_workspace_research_rounds` if reporting or history views require direct queries by round.

---

## 4. Tables

### 4.1 `sales_workspaces`

Root table for one Sales Workspace.

Core columns:

```text
workspace_id text primary key
workspace_key text not null
owner_id text null
tenant_id text null
name text not null
goal text not null default ''
status text not null
workspace_version integer not null
current_product_profile_revision_id text null
current_lead_direction_id text null
latest_research_round_id text null
payload_json jsonb not null
created_by text null
updated_by text null
created_at timestamptz not null
updated_at timestamptz not null
```

Rules:

- `workspace_version` starts at `0`.
- every successful formal write increments `workspace_version` by one.
- `status` v0 values: `active`, `archived`.
- `tenant_id`, `created_by`, `updated_by` are nullable metadata only; they do not implement auth, RBAC, or tenant isolation.

Recommended indexes:

```text
(workspace_key)
(owner_id)
(tenant_id)
(status)
(updated_at)
```

### 4.2 `sales_workspace_product_profile_revisions`

Stores product profile revisions for a workspace.

Core columns:

```text
workspace_id text not null references sales_workspaces(workspace_id)
revision_id text not null
version integer not null
product_name text not null
one_liner text not null default ''
payload_json jsonb not null
created_at timestamptz not null
primary key (workspace_id, revision_id)
```

Rules:

- `revision_id` matches `ProductProfileRevision.id`.
- `payload_json` stores the full Pydantic payload.
- active revision pointer lives on `sales_workspaces.current_product_profile_revision_id`.

### 4.3 `sales_workspace_lead_directions`

Stores lead direction versions for a workspace.

Core columns:

```text
workspace_id text not null references sales_workspaces(workspace_id)
direction_id text not null
version integer not null
change_reason text not null default ''
payload_json jsonb not null
created_at timestamptz not null
primary key (workspace_id, direction_id)
```

Rules:

- `direction_id` maps to current code's `LeadDirectionVersion.id`.
- active direction pointer lives on `sales_workspaces.current_lead_direction_id`.
- industry, customer type, region, size, and exclusion arrays stay in `payload_json` for v0; generated columns or normalized child tables are deferred until query requirements justify them.

### 4.4 `sales_workspace_lead_candidates`

Stores company / organization candidates.

Core columns:

```text
workspace_id text not null references sales_workspaces(workspace_id)
candidate_id text not null
name text not null
industry text not null default ''
region text not null default ''
company_size text not null default ''
status text not null
payload_json jsonb not null
created_at timestamptz not null
updated_at timestamptz not null
primary key (workspace_id, candidate_id)
```

Rules:

- `candidate_id` maps to current code's `CompanyCandidate.id`.
- `status` v0 values: `active`, `archived`.
- candidate dedupe, merge, and evidence completeness are service / kernel responsibilities, not a single DB constraint.

Recommended indexes:

```text
(workspace_id, status)
(workspace_id, name)
(workspace_id, updated_at)
```

### 4.5 `sales_workspace_research_sources`

Stores source evidence used by observations.

Core columns:

```text
workspace_id text not null references sales_workspaces(workspace_id)
source_id text not null
round_id text not null
title text not null
url text null
source_type text not null
reliability text not null
excerpt text not null default ''
payload_json jsonb not null
collected_at timestamptz not null
primary key (workspace_id, source_id)
```

Rules:

- observations must reference a source in the same workspace.
- public web URL evidence remains source-bound.
- contact / CRM source expansion remains out of scope.

Recommended indexes:

```text
(workspace_id, round_id)
(workspace_id, url)
```

### 4.6 `sales_workspace_research_observations`

Stores evidence-backed candidate observations.

Core columns:

```text
workspace_id text not null references sales_workspaces(workspace_id)
observation_id text not null
candidate_id text not null
source_id text not null
round_id text not null
signal_type text not null
polarity text not null
strength integer not null
summary text not null
payload_json jsonb not null
created_at timestamptz not null
primary key (workspace_id, observation_id)
foreign key (workspace_id, candidate_id) references sales_workspace_lead_candidates(workspace_id, candidate_id)
foreign key (workspace_id, source_id) references sales_workspace_research_sources(workspace_id, source_id)
```

Rules:

- `strength` v0 range remains `1..5`.
- `signal_type` v0 values follow kernel schema: `fit`, `pain`, `timing`, `region`, `source_quality`, `exclusion`, `other`.
- evidence completeness for formal ranking remains enforced by backend service / kernel validation.

Recommended indexes:

```text
(workspace_id, candidate_id)
(workspace_id, source_id)
(workspace_id, round_id)
(workspace_id, signal_type)
```

### 4.7 `sales_workspace_patch_commits`

Append-only record of formal workspace writes.

Core columns:

```text
workspace_id text not null references sales_workspaces(workspace_id)
commit_id text not null
patch_id text not null
base_workspace_version integer not null
resulting_workspace_version integer not null
author text not null
message text not null default ''
operation_count integer not null
changed_object_refs jsonb not null
patch_json jsonb not null
commit_json jsonb not null
created_at timestamptz not null
primary key (workspace_id, commit_id)
unique (workspace_id, patch_id)
unique (workspace_id, resulting_workspace_version)
```

Rules:

- This table is append-only.
- successful patch apply creates exactly one row.
- `base_workspace_version` must match the workspace version observed before apply.
- `resulting_workspace_version` must equal `base_workspace_version + 1` for v0.
- version conflict is rejected before insert.

Recommended indexes:

```text
(workspace_id, created_at)
(workspace_id, base_workspace_version)
```

### 4.8 `sales_workspace_draft_reviews`

Stores the current backend-managed Draft Review object.

Core columns:

```text
workspace_id text not null references sales_workspaces(workspace_id)
draft_review_id text not null
draft_id text not null
status text not null
base_workspace_version integer not null
instruction text not null default ''
created_by text not null
reviewed_by text null
applied_commit_id text null
failure_code text null
failure_reason text null
draft_json jsonb not null
preview_json jsonb not null
review_json jsonb null
apply_result_json jsonb null
runtime_metadata jsonb not null
expires_at timestamptz null
created_at timestamptz not null
updated_at timestamptz not null
primary key (workspace_id, draft_review_id)
```

Rules:

- `status` v0 values: `previewed`, `reviewed`, `applied`, `rejected`, `expired`.
- `draft_json` stores `WorkspacePatchDraft`.
- `preview_json` stores materialized patch preview and preview ranking.
- `reviewed_by` is nullable metadata, not auth enforcement.
- `applied_commit_id` links to `sales_workspace_patch_commits.commit_id` after successful apply.

Recommended indexes:

```text
(workspace_id, status)
(workspace_id, base_workspace_version)
(workspace_id, updated_at)
```

### 4.9 `sales_workspace_draft_review_events`

Append-only lifecycle event log for Draft Review audit history.

Core columns:

```text
workspace_id text not null
draft_review_id text not null
event_id text not null
event_type text not null
from_status text null
to_status text not null
actor_type text not null
actor_id text null
reason text not null default ''
event_json jsonb not null
created_at timestamptz not null
primary key (workspace_id, event_id)
foreign key (workspace_id, draft_review_id) references sales_workspace_draft_reviews(workspace_id, draft_review_id)
```

Rules:

- This table is append-only.
- v0 event types: `created`, `reviewed`, `rejected`, `applied`, `expired`, `apply_failed`.
- stale apply should update the review to `expired` and insert an `expired` or `apply_failed` event.

Recommended indexes:

```text
(workspace_id, draft_review_id, created_at)
(workspace_id, event_type)
```

---

## 5. Transaction Boundary

Formal workspace writeback should use one database transaction:

```text
load workspace row for update
check workspace_version == patch.base_workspace_version
validate WorkspacePatch through Sales Workspace Kernel
upsert affected formal object rows
insert sales_workspace_patch_commits row
update sales_workspaces.workspace_version
commit transaction
```

Failure behavior:

- version conflict returns `workspace_version_conflict` and does not mutate state.
- unsupported operation returns `unsupported_workspace_operation` and does not mutate state.
- validation error returns `validation_error` or `patchdraft_validation_error` and does not mutate state.

Runtime / Product Sales Agent execution layer remains outside this transaction boundary. It may produce `WorkspacePatchDraft`, but backend / Sales Workspace Kernel owns formal writeback.

---

## 6. Derived Outputs

The following are derived outputs, not v0 formal truth tables:

- `CandidateRankingBoard`
- Markdown projection
- `ContextPack`

Rules:

- Ranking board is recomputed from candidates and observations.
- Markdown projection is generated from structured workspace state and never parsed back.
- ContextPack is compiled from structured workspace state, not from Markdown, LangGraph checkpoint, or SDK session.
- Future cache tables are allowed only if they can be invalidated or regenerated from formal state.

---

## 7. First Migration Candidate

The first Alembic migration should include only:

- the tables listed in Section 4.
- primary keys, core foreign keys, status/check constraints, and basic indexes.
- no pgvector.
- no ContactPoint / CRM / outreach tables.
- no Android-specific table.
- no LangGraph checkpoint table.

The first repository layer task should map this schema to current Pydantic objects without changing API contract behavior.

---

## 8. Explicit Non-goals

This schema design does not implement:

- SQLAlchemy ORM.
- Alembic migration.
- DB-backed Sales Workspace API.
- Android review history UI.
- formal Runtime / LangGraph integration.
- real LLM / search / CRM / contact.
- multi-user permissions or tenant isolation.
