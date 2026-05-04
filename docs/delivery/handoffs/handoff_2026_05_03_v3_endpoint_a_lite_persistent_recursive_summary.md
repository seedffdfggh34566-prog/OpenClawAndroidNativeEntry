# Handoff: V3 端点 A-lite 持久化递归摘要

## 1. 变更内容

### 1.1 Schema：V3SandboxSession 新增 3 字段

| 字段 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `context_summary` | `str \| None` | `None` | 递归摘要文本 |
| `summary_cursor_message_id` | `str \| None` | `None` | 已被吸收的最后一条消息 id |
| `summary_recursion_count` | `int` | `0` | 递归次数计数（γ 兜底机制留位，本期不消费） |

**无 Alembic migration**：session 已以 Pydantic JSON 整体存于 `v3_sandbox_sessions.payload_json`；新字段随 dump/validate 自动进出 JSON blob。老 payload 缺这些 key 时 Pydantic 用默认值填充。

### 1.2 Runtime：摘要从"每 turn 重算"改为"持久化递归"

`backend/runtime/v3_sandbox/graph.py`：

- `_build_tool_loop_messages` 重构：用 `summary_cursor_message_id` 切分 historical → after_cursor，构建 LLM payload。
- 新增 `_find_cursor_index`：在 historical 中按 message_id 查 cursor 位置；找不到时 fallback 到无 cursor。
- 新增 `_summary_message_for_payload`：从 `session.context_summary` 派生 LLM payload 中的 summary 消息（每 turn 都生效，不再依赖触发）。
- 新增 `_maybe_run_summarization`（替换原 `_maybe_summarize_older_messages`）：
  - 只有 `len(after_cursor) > 32` 才考虑触发（保证 recent 段至少能保留 32 条）
  - token 计数包含 system prompt + 已存 summary + after_cursor 全部 + 当前 user
  - 阈值 `0.75 * context_window`
  - 摘要输入 = `(已存 context_summary) + (after_cursor[:-32] 原文)` —— **真正的递归**
  - 摘要 prompt 重写为销售员-agent 角色版本，明确保留：销售员对自家产品的原话/数字/人名/约束/纠正/理想客户画像
  - 写回 `session.context_summary`、推进 `summary_cursor_message_id`、`summary_recursion_count += 1`

### 1.3 LLM payload 形状（恒定）

```
[system, summary_msg(if context_summary存在), user_msg_with_recent_history]
```

- 触发摘要后，recent 段恒为 32 条原文（cursor+1..end-1）
- 触发之前，recent 段 = 全部 historical
- summary 持久化跨 turn 复用，**不**每 turn 重新调 LLM

### 1.4 Trace：runtime_metadata 新增 4 字段

`backend/runtime/v3_sandbox/graph.py::_return_turn`：

```python
"context_summary_present": bool,
"context_summary_chars": int,
"summary_cursor_message_id": str | None,
"summary_recursion_count": int,
```

/lab trace inspector 自动展示，无需前端改动。

### 1.5 测试

`backend/tests/test_v3_sandbox_runtime.py` 新增/调整：

| 测试 | 验证点 |
|---|---|
| `test_context_compression_persists_summary_and_advances_cursor` | 触发后 3 个新字段被写入；session.messages 不变 |
| `test_context_compression_recent_window_after_summary_is_32_originals` | 摘要后 LLM payload 中 recent 段恰为 32 条 |
| `test_context_compression_recursive_uses_prior_summary` | 第二次触发时 prompt 含上次 summary（递归证据） |
| `test_fresh_session_has_no_summary_state` | Pydantic 默认值正确 |
| `test_summary_state_round_trips_through_json_store` | 字段经 JSON 存取无损（验证免 migration 正确性）|

## 2. 文件改动

| 文件 | 变更 |
|---|---|
| `backend/runtime/v3_sandbox/schemas.py` | `V3SandboxSession` 加 3 字段 |
| `backend/runtime/v3_sandbox/graph.py` | `_build_tool_loop_messages` 重构、新增 3 helper、`_return_turn` trace 字段 |
| `backend/tests/test_v3_sandbox_runtime.py` | 改写 1 旧测试，加 4 新测试 |
| `docs/delivery/tasks/_active.md` | current task 指向新 task，状态 `in_progress`（本 handoff 提交后改 `completed`）|
| `docs/delivery/tasks/task_2026_05_03_v3_endpoint_a_lite_persistent_recursive_summary.md` | 新建 |

## 3. 验证结果

- `backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -x -q`：**33 passed**（原 29 + 新 4）
- `backend/.venv/bin/python -m pytest backend/tests -q`：**165 passed, 18 skipped**（与上 task 比 +4 测试，0 regression）
- `alembic upgrade head`：通过（无新 migration，仅 regression 检查）
- `web build`：通过

未跑：Postgres alembic（无 docker daemon）、real LLM smoke（需 `OPENCLAW_BACKEND_RUN_LIVE_LLM_SMOKE=1`）。

## 4. 已知限制

- **Summary 劣化**：每次递归压缩都损失细节；β prompt 工程化只能减缓不能根除。短会话（POC 通常 ≤ 50 turn）下递归深度 0–1，影响小。`summary_recursion_count` 仅作为 observability 字段暴露给 trace，**不触发任何硬刷新动作**；γ 周期性硬刷新机制已决定不实现（前沿框架亦未采用同类机制，且与递归架构冲突）。
  - 压缩阈值已从 0.75 提升至 **0.90**（Letta 实践对齐），在移除所有 128k 窗口模型后，最低窗口为 200k，90% 阈值仍留有 response headroom。
  - 新增 **75% memory-pressure warning**：system prompt 中注入中文警告，推荐 agent 使用增量操作（memory_insert / memory_replace / core_memory_append）主动整理 memory，避免在高压下使用 memory_rethink。
  - 新增 **95% tool-loop guard**：`_continue_or_return` 中通过 tiktoken 精确计数，若 tool_messages 超过 95% 预算则优雅结束 loop，防止 turn 内溢出。
- **Replay 行为**：~~未显式禁用复用持久化 summary……未单独写 replay 测试~~ **已验证并闭环**。
  - `test_replay_does_not_reuse_persisted_summary`：通过 API replay 创建的新 session，`context_summary` / `summary_cursor_message_id` / `summary_recursion_count` 均从默认值开始，不会继承源 session 的 persisted summary。
  - `test_session_reset_clears_summary_fields`：通过 store 覆盖保存（reset）后，三个 summary 字段回归默认值。
- **tiktoken 计数偏差**：与 Tencent 模型实际 tokenizer ±20% 偏差，用于阈值判断够用。
- **summary 写入失败时静默跳过**：若 LLM 返回空或 raise，不持久化、不计数；下一 turn 会再尝试。无 retry 机制。
- **空 final_message 兜底**：若 tool loop 因 95% guard 或其他原因结束时 agent 未调用 send_message，`_return_turn` 自动填充默认中文消息，避免前端展示空回复。

## 5. 推荐下一步

候选（需用户显式授权）：

1. ~~γ 周期性硬刷新（每 K 次递归全量重摘要）~~ **已否决**：非行业标准、无法根本解决递归劣化、与递归架构冲突。`summary_recursion_count` 保留为纯 observability。
2. ~~75% memory-pressure warning + 90% 压缩阈值 + 95% tool-loop guard~~ **已完成**（本 handoff 后续变更）。
3. ADR-010 §6 #4 archival memory
4. ~~从 allowlist 移除 deepseek-v3.2~~ **已完成**（v3 docs cleanup task）。
5. ~~Replay-不复用-summary 的显式测试（覆盖§4 中标记的观察项）~~ **已完成**（`test_replay_does_not_reuse_persisted_summary` + `test_session_reset_clears_summary_fields`）
