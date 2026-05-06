# Task: V3 跨 Turn Tool Loop 持久化改造

- 创建日期：2026-05-06
- 关联研究：`docs/research/cross_turn_tool_loop_persistence.md`
- 关联 handoff（完成后创建）：`docs/delivery/handoffs/handoff_2026_05_06_v3_cross_turn_tool_loop_persistence.md`

---

## 1. 目标

修复 V3 Sandbox 中"跨 turn 丢失 tool loop"的 runtime prompt 组装缺陷。让下一 turn 的模型能看到上一 turn 中完整的 tool 调用历史（assistant 的 tool_calls + tool 的执行结果）。

## 2. 范围

局限在 sandbox runtime POC 边界内，不触碰：
- Letta server 接入
- archival_memory
- 超出 opt-in V3 sandbox persistence 的 memory DB schema
- LLMClient 工厂改造

## 3. 改造清单

### 3.1 Schema 扩展（`backend/runtime/v3_sandbox/schemas.py`）

- `V3SandboxMessage.role`：从 `Literal["user", "assistant"]` 扩展为 `Literal["user", "assistant", "tool"]`
- `V3SandboxMessage.content`：放宽 `min_length=1` 约束为 `str = ""`（tool 消息可能为 JSON 或空）
- 新增 `tool_calls: list[dict[str, Any]] | None = None`
- 新增 `tool_call_id: str | None = None`
- 保持向后兼容：现有 message 的 `tool_calls`/`tool_call_id` 自然为 null

### 3.2 写路径改造（`backend/runtime/v3_sandbox/graph.py`）

#### 3.2.1 `_execute_tool_calls`
- 在 turn 内每次 tool call 执行后，把 `assistant(tool_calls)` 消息 append 到 `session.messages`
- 把 `tool(result)` 消息也 append 到 `session.messages`
- 使用 tool_call.id 作为 `tool_call_id` 配对

#### 3.2.2 `_return_turn`
- 调整 final message 处理：如果 turn 内已有 assistant message（含 tool_calls）写入 `session.messages`，不再追加新的纯文本 assistant message
- `final_message`（send_message 的结果）作为该 turn 最后一个 assistant message 的 content 保留

### 3.3 读路径改造（`backend/runtime/v3_sandbox/graph.py`）

#### 3.3.1 `_build_tool_loop_messages`
- 不再把 `session.messages` 渲染成 `[role] content` 文本拼接塞进单个 user message
- 改为直接映射为 OpenAI/TokenHub 原生 message format：
  - `role="system"`：动态构造的 system prompt（第一消息）
  - `role="user"` / `role="assistant"` / `role="tool"`：直接从 `session.messages` 转换
  - assistant 消息含 `tool_calls` 时保留结构化字段
  - tool 消息保留 `tool_call_id` 字段

### 3.4 配对安全截断（`backend/runtime/v3_sandbox/graph.py`）

#### 3.4.1 `_maybe_run_summarization`
- `to_absorb = after_cursor[:-max_context_messages]` 后增加配对安全检查
- 如果截断点落在 `assistant(tool_calls)` 和对应的 `tool` 结果之间，把对应的结果消息也一并吸收进摘要，禁止拆开
- 摘要输入格式化：把 tool_calls 信息序列化为文本摘要模型的输入

### 3.5 研究文档更新（`docs/research/cross_turn_tool_loop_persistence.md`）

- 追加 "Implementation status" 小节，标注：
  - `messages[-8:]` 硬截断描述已过时（当前为 `max_context_messages=32` + recursive summary）
  - 本次改造已完成的结论项
  - 尚未完成的 deferred 项（如 normalize 不变式、独立 message 表）

## 4. 验证

- `backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -v`
- 新增/更新测试用例验证：
  - 跨 turn 后 `session.messages` 包含完整的 tool_calls + tool_call_id 配对
  - `_build_tool_loop_messages` 输出符合原生 message format
  - summary 截断不会拆开 tool_use/tool_result 对
  - 旧 session 数据加载的向后兼容性

## 5. 已知限制（预先声明）

- `normalize_history` 不变式（参考 Codex CLI）本次不实现，留作后续 context 压缩策略扩展时的安全网
- `V3SandboxMessage` 仍嵌套在 `V3SandboxSession.messages` JSON 中，未引入独立 message 表
- 不修改 DB schema（无需新 migration），但需确认旧 JSON 加载时新字段为 null 的行为

---

当前状态：completed（2026-05-06）
