# Handoff: V3 跨 Turn Tool Loop 持久化改造

- 日期：2026-05-06
- 关联 task：`docs/delivery/tasks/task_2026_05_06_v3_cross_turn_tool_loop_persistence.md`
- 关联研究：`docs/research/cross_turn_tool_loop_persistence.md`（已更新 Implementation status）

---

## 1. 改了什么

### 1.1 Schema 扩展

**文件**：`backend/runtime/v3_sandbox/schemas.py`

- `V3SandboxMessage.role`：从 `Literal["user", "assistant"]` 扩展为 `Literal["user", "assistant", "tool"]`
- `V3SandboxMessage.content`：放宽 `min_length=1` 为 `str = ""`（tool 消息可能为 JSON 或空）
- 新增 `tool_calls: list[dict[str, Any]] | None = None`
- 新增 `tool_call_id: str | None = None`
- 向后兼容：现有 message 的 `tool_calls`/`tool_call_id` 自然为 null

### 1.2 写路径：Tool Loop 消息写回 Session

**文件**：`backend/runtime/v3_sandbox/graph.py`

- **`_call_agent_with_tools`**：每次 LLM 返回 assistant message（含 `tool_calls`）后，将其转换为 `V3SandboxMessage` 并 `append` 到 `session.messages`
- **`_execute_tool_calls`**：每个 tool 执行完成后，将其结果转换为 `role="tool"` 的 `V3SandboxMessage`（含 `tool_call_id`）并 `append` 到 `session.messages`
- **`_return_turn`**：从后往前找到该 turn 最后一条 assistant message（tool results 已 append 在其后），将其 content 更新为 `send_message` 的 final text。如果 assistant 已有非空 content（reasoning text），则保留并追加新的 final assistant message

### 1.3 读路径：原生 Message List 输出

**文件**：`backend/runtime/v3_sandbox/graph.py`

- **`_build_tool_loop_messages`**：不再把 `session.messages` 渲染成 `[role] content` 文本拼接塞进单个 user message
- 改为直接映射为 OpenAI/TokenHub 原生 message format：
  - `system prompt` 仍作为第一条消息动态构造
  - `after_cursor` 中的消息按 `user` / `assistant`（含 `tool_calls`） / `tool`（含 `tool_call_id`）直接转换
  - 最后一条为当前 turn 的 user message（含指令 + 用户输入）

### 1.4 配对安全截断

**文件**：`backend/runtime/v3_sandbox/graph.py`

- **`_maybe_run_summarization`**：在 `to_absorb = after_cursor[:-max_context_messages]` 后增加配对安全检查
- 如果截断点落在 `assistant(tool_calls)` 和对应的 `tool` 结果之间，把对应的结果消息一并吸收进摘要，禁止拆开
- 摘要输入格式化：把 `tool_calls` 信息序列化为摘要模型的输入文本

### 1.5 DB 约束放宽

**文件**：`backend/alembic/versions/20260430_0005_v3_sandbox_memory_persistence.py`

- `ck_v3_sandbox_messages_role` CHECK 约束从 `role in ('user', 'assistant')` 扩展为 `role in ('user', 'assistant', 'tool')`

### 1.6 测试更新

**文件**：`backend/tests/test_v3_sandbox_runtime.py`

- 更新 message 数量断言（每 turn 从 2 条变为 4 条：user + assistant with tool_calls + 2 tool results）
- `test_context_compression_recent_window_after_summary_is_32_originals`：改为验证原生 message list 中的历史消息数量（32 条），而非查找 "Recent conversation" 文本块

---

## 2. 验证结果

- `backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py`：**49 passed**
- `backend/.venv/bin/python -m pytest backend/tests/`：**181 passed, 18 skipped**（skipped 为需要 Postgres/Live LLM 的环境相关测试）

---

## 3. 已知限制

- `normalize_history` 不变式（参考 Codex CLI）本次未实现，留作后续 context 压缩策略扩展时的安全网
- `V3SandboxMessage` 仍嵌套在 `V3SandboxSession.messages` JSON 中，未引入独立 message 表
- 不引入 archival_memory、Letta server、LLMClient 工厂改造

---

## 4. 推荐下一步

1. 在 `/lab` trace inspector 中验证跨 turn 的 tool loop 可见性
2. 评估 `_build_tool_loop_messages` 改为原生 message list 后 LLM 行为是否稳定（prompt 结构变化）
3. 当 context 压缩策略进一步扩展时，引入 `normalize_history` 不变式
