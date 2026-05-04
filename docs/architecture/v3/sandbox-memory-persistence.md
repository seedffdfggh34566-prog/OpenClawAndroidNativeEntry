# V3 Sandbox Memory Persistence

更新时间：2026-04-30

## 1. 定位

本文档记录 V3 sandbox memory persistence 第一版实现边界。

当前目标是让 `/v3/sandbox` 的 POC state 可以在显式配置下写入 SQLAlchemy / Alembic 管理的数据库，便于 `/lab`、replay、trace 和 memory correction 调试。它不是正式 CRM、正式 customer intelligence schema、Letta server 接入或 production SaaS persistence。

当前 `/lab` 已可显示 store backend，并在 database store 下展示 memory transition events。

---

## 2. 核心决策

第一版采用：

```text
session-scoped Snapshot + Event
```

含义：

- **Snapshot**：完整 `V3SandboxSession` JSON snapshot 是 API round-trip 主读取来源。
- **Event**：messages、trace events、action events、memory transition events 是 audit / debug / query evidence。
- **Session-scoped**：memory 只属于 sandbox session，不跨 session 共享，不引入 agent identity、tenant 或 user account。
- **Opt-in**：默认仍是 in-memory；只有 `OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND=database` 时启用 DB store。

---

## 3. Persisted Objects

第一版新增以下 V3 sandbox 表：

- `v3_sandbox_sessions`
  - 保存完整 session snapshot。
  - API `GET /v3/sandbox/sessions/{session_id}` 从这里重建 Pydantic session。

- `v3_sandbox_messages`
  - 保存 user / assistant message normalized rows。
  - 用于按 session、role、created_at 查询。

- `v3_sandbox_trace_events`
  - 保存每个 runtime trace event snapshot。
  - 包含 runtime metadata、parsed output 和 error。

- `v3_sandbox_action_events`
  - 保存 trace 中每个 `AgentAction` 的 normalized row。
  - 用于观察 `write_memory`、`update_memory_status`、`update_working_state`、`update_customer_intelligence`。

- `v3_sandbox_memory_items`
  - 保存当前 memory item 状态。
  - 用于后续按 status/source/tag-like payload 查询 active / inactive memory。

- `v3_sandbox_memory_transition_events`
  - 从 memory actions 派生。
  - 覆盖 `write_memory`、`update_memory_status` 和 `supersedes` 产生的 `supersede_memory`。
  - 用于解释 memory lineage 和用户纠错如何影响旧 memory。

---

## 4. Store Behavior

`create_session`、`save_session` 和 `get_session` 对外行为与现有 in-memory / JSON store 对齐。

DB store 写入策略：

- `save_session` 写完整 session snapshot。
- 同步替换该 session 的 normalized rows，保持 repeated save 幂等。
- normalized rows 不反向重建 session；它们是可查询 evidence。
- replay partial failure 必须保存 partial replay session 和 failed trace。

Store selection：

```text
OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND=memory    -> in-memory
OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND=json      -> JSON store，要求 store dir
OPENCLAW_BACKEND_V3_SANDBOX_STORE_BACKEND=database  -> DB store
未配置 backend + 有 store dir                         -> JSON store
未配置 backend + 无 store dir                         -> in-memory
```

---

## 5. 边界

本实现不做：

- cross-session memory。
- agent-scoped long-term memory。
- archival memory / retrieval / embedding / pgvector。
- compaction。
- LangGraph durable checkpoint / resume lifecycle。
- Letta server 接入或完整 Letta 复现。
- `/workspace` 用户体验。
- Android 接入。
- formal CRM / outreach / contact export。
- auth / tenant / production SaaS。

LangGraph checkpoint 仍不是业务 memory 主存。V3 sandbox persistence 只把 POC memory/state/trace 持久化为 backend-managed evidence。

---

## 6. 后续方向

如果 `/lab` 观察结果稳定，后续可以单独开放：

- agent-scoped memory identity。
- archival memory / retrieval。
- memory compaction summary。
- `/workspace` 用户可理解 memory 摘要。
- formal customer intelligence schema 与 CRM 安全边界。
