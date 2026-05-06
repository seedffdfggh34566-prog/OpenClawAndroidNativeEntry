# 跨 Turn Tool Loop 持久化机制研究：V3 Sandbox vs Letta / Codex / Claude Code

- 文档日期：2026-05-05
- 关联文档：
  - `docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`
  - `docs/adr/ADR-010-letta-as-reference-architecture.md`
  - `docs/architecture/v3/letta-comparison.md`（第 8 行"In-context 与历史消息"）
- 性质：Research-only / 分析结论 / 不自动开放实现授权

---

## 1. 问题定义：V3 当前发生了什么

在 V3 Sandbox 的 sales agent 对话中，**单个 turn 内部的 tool loop 详情（模型发出的 tool_calls + 各 tool 的返回结果）在跨 turn 后完全丢失**。下一 turn 的 prompt 里，模型只能看到历史消息的 `[role] content` 文本拼接，看不到之前 turn 中它曾经调用过哪些 memory tool、传了什么参数、得到了什么结果。

### 1.1 根因定位

| 位置 | 代码表现 | 后果 |
|---|---|---|
| `backend/runtime/v3_sandbox/schemas.py:107-111` | `V3SandboxMessage` 只有 `id/role/content/created_at`，**没有 `tool_calls` / `tool_call_id` 字段** | 工具调用元数据在 schema 层就无处存放 |
| `backend/runtime/v3_sandbox/graph.py:151-156` | `_load_state` 把 `user_message` append 进 `session.messages` | 正确写入了用户消息 |
| `backend/runtime/v3_sandbox/graph.py:225-373` | `_call_agent_with_tools` / `_execute_tool_calls` 在局部状态里循环，tool_messages 只在函数内部流转 | turn 内各 step 的 tool 结果没有写回 `session.messages` |
| `backend/runtime/v3_sandbox/graph.py:499-513` | `_build_tool_loop_messages` 把 `session.messages` 渲染成 `[role] content` 文本列表 | 即使未来存了 tool 信息，这里也只提取 content |
| `backend/runtime/v3_sandbox/graph.py:1118-1131` | `_return_turn` 只把 `send_message` 的最终文本作为 assistant_message append | 整个 tool loop 过程消息被丢弃 |
| `backend/runtime/v3_sandbox/graph.py:1134-1156` | `tool_events` 写入 `V3SandboxTraceEvent`（调试用 trace） | trace 只在 `/lab` 可见，不进 LLM prompt |

### 1.2 一句话总结

> V3 把 tool loop 当成"单次 turn 内部的黑盒"：只保留最终 send_message 的文本输出，不把中间的 `assistant(tool_calls)` 和 `tool(results)` 写进 session 消息历史。因此下一 turn 的模型完全不知道上一 turn 里自己做过什么 tool 操作。

---

## 2. Letta (0.16.7, commit f3332476) 的机制

### 2.1 消息 schema：tool 信息是一等字段

`letta/schemas/message.py:252-310` 定义了 `Message` 模型，关键字段：

```python
role: Literal["system", "assistant", "user", "tool", "approval", "summary"]
tool_calls: Optional[List[ToolCall]]        # assistant 发 tool_calls 时填写
tool_call_id: Optional[str]                 # tool role 消息回指 assistant 的 call
tool_returns: Optional[List[ToolReturn]]    # tool 执行结果
```

Letta 把 tool 调用和 tool 结果都视为消息流中的正式角色（`assistant` 带 `tool_calls`，`tool` 带 `tool_call_id` 和 `tool_returns`）。

### 2.2 In-context 指针 vs 全量消息

`letta/schemas/agent.py:78`：

```python
message_ids: Optional[List[str]]  # 仅保存 in-context message 引用
```

全量历史在 `message` 表，但 agent 状态里通过 `message_ids` 精确控制哪些消息进入下一次 LLM 调用。当需要压缩时，Letta 不需要丢弃整段对话，而是可以：

- 把旧消息替换成 `summary` role 的摘要消息
- 保留 `tool` 结果但替换 `assistant` 的 reasoning

### 2.3 Step 内消息追加路径

`letta/agent.py:927-1004`（`inner_step`）：

每次 LLM 返回后，Letta 把 `all_new_messages`（包含 assistant 的 tool_calls 消息和后续 tool 结果消息）通过 `append_to_in_context_messages` 追加到 agent 的当前 in-context 列表。这意味着**同一个 turn 内多次 tool call 的所有中间步骤都会成为下一轮 prompt 的一部分**。

### 2.4 Tool 结果消息构造

`letta/agent.py:696-709`：

```python
# 伪代码示意
for tool_call in assistant_message.tool_calls:
    result = execute_tool(tool_call)
    tool_message = Message(
        role="tool",
        tool_call_id=tool_call.id,
        tool_returns=[ToolReturn(name=..., value=...)],
    )
    all_new_messages.append(tool_message)
```

`tool_call_id` 是关联 assistant call 与 tool result 的关键——LLM provider（OpenAI/Anthropic）要求 tool result 必须带对应的 `tool_call_id`。

### 2.5 Context 压缩时保留结构

`letta/agent.py:1107-1187`（`summarize_messages_inplace`）：

当 `total_tokens > context_window` 时，Letta 不是简单截断，而是：

1. 把待压缩的旧消息序列传给摘要模型
2. 生成一段 summary 文本
3. 把 summary 包装成 `role="summary"` 的消息
4. 通过 `prepend_to_in_context_messages` 放到消息列表前端

**关键**：被压缩的原始消息可以从 `message_ids` 中移除，但 trace/DB 里仍然保留。如果未来需要"展开"查看，可以通过 `message` 表恢复。

---

## 3. OpenAI Codex CLI 的机制

### 3.1 ContextManager：统一 Vec<ResponseItem>

`codex-rs/core/src/context_manager/history.rs`：

```rust
pub struct ContextManager {
    pub items: Vec<ResponseItem>,
    pub history_version: u64,
    pub token_info: TokenInfo,
    pub reference_context_item: Option<usize>,
}
```

Codex 的历史不是"消息列表"，而是 `ResponseItem` 的统一向量。其中包含两种与 tool loop 相关的变体：

- `FunctionCall { call_id, name, arguments }` —— 模型请求调用工具
- `FunctionCallOutput { call_id, output }` —— 工具执行结果

### 3.2 normalize_history 不变式

在把 `items` 转换为 prompt 前，Codex 会调用 `normalize_history`，核心逻辑：

1. ** pairing 检查**：每个 `FunctionCallOutput` 必须能找到同 `call_id` 的前置 `FunctionCall`
2. **顺序保证**：`FunctionCall` 和对应的 `FunctionCallOutput` 必须相邻或保持合理间距
3. ** orphaned call 清理**：如果 `FunctionCall` 没有对应的 `FunctionCallOutput`（比如执行 crash），会被移除或标记

这确保了**跨 turn 时 tool loop 的因果链不会断裂**——模型不会看到"有结果但没调用"或"有调用但没结果"的畸形历史。

### 3.3 SessionState 持久化

`codex-rs/core/src/state/session.rs`：

```rust
pub struct SessionState {
    pub history: ContextManager,
    pub environment: Environment,
    // ...
}
```

`SessionState` 把整个 `ContextManager`（含 `FunctionCall` / `FunctionCallOutput`）持久化到本地 `.rollout` 文件。重启 Codex 后恢复对话，模型仍能看到完整的 tool loop 历史。

### 3.4 与 V3 的差异

Codex 不区分"turn 内"和"turn 间"——所有 `ResponseItem` 在同一个线性历史中。V3 的 `session.messages` 试图按 turn 划分，但结果是把 turn 内的 tool loop 细节排除在外。

---

## 4. Claude Code / Anthropic Messages API 的机制

### 4.1 JSONL 本地持久化

Claude Code 的会话历史存储在：

```
~/.claude/projects/<encoded-cwd>/<uuid>.jsonl
```

每个 `.jsonl` 文件包含完整的对话 turn，包括：

- `assistant` 消息中的 `thinking` 块和 `tool_use` 块
- `user` 消息中的 `tool_result` 块（对应前序 `tool_use`）

### 4.2 Tool use / Tool result 配对协议

Anthropic Messages API 要求严格的 request/response 配对：

```json
// assistant 消息
{"role": "assistant", "content": [
  {"type": "thinking", "thinking": "..."},
  {"type": "tool_use", "id": "tu_01xxx", "name": "core_memory_append", "input": {"label": "human", "content": "..."}}
]}

// user 消息（必须紧随其后）
{"role": "user", "content": [
  {"type": "tool_result", "tool_use_id": "tu_01xxx", "content": "..."}
]}
```

### 4.3 跨 turn 的连续性

Claude Code 的 `messages` 列表会完整保留所有 `tool_use` / `tool_result` 对。即使对话经过多轮，模型在每一轮都能看到：

- 自己曾经调过哪些工具（`tool_use`）
- 工具返回了什么（`tool_result`）
- 自己当时的 reasoning（`thinking`）

### 4.4 与 V3 的对比

V3 的 `_build_tool_loop_messages` 当前生成的是简化文本：

```
[system] ...
[assistant] 最终回复文本（send_message 的 content）
[user] 用户新输入
```

而 Claude Code / Anthropic API 保持结构化：

```
[system] ...
[assistant] <thinking>...</thinking> <tool_use id=... name=... input=... />
[user] <tool_result tool_use_id=...> ... </tool_result>
[assistant] <thinking>...</thinking> <text>最终回复</text>
[user] 用户新输入
```

---

## 5. 四路对比表

| 维度 | V3 Sandbox (当前) | Letta (0.16.7) | Codex CLI | Claude Code / Anthropic API |
|---|---|---|---|---|
| **消息模型** | `V3SandboxMessage` 仅 `role/content`，无 tool 字段 | `Message` 含 `tool_calls/tool_call_id/tool_returns` | `ResponseItem::FunctionCall/FunctionCallOutput` | `assistant.tool_use` + `user.tool_result` |
| **Tool loop 位置** | Turn 内部黑盒，不进 session.messages | 全部进 `message_ids` / `message` 表 | 全部进 `ContextManager.items` | 全部进 `messages` 数组 |
| **跨 turn 可见性** | 不可见（仅 send_message 文本保留） | 可见（in-context 指针控制可见范围） | 可见（统一历史流） | 可见（完整 message 历史） |
| **Call/Result 配对** | 无（trace_event 里存 tool_events，但无 call_id 关联） | `tool_call_id` 关联 | `call_id` 关联 | `tool_use_id` / `tool_use_id` 关联 |
| **Context 超限处理** | `messages[-8:]` 硬截断 + 4 步上限抛错 | `summarize_messages_inplace` + `message_ids` 调整 | ContextManager 的 token 计算 + 裁剪 | 依赖 Claude 长上下文（200K） |
| **持久化粒度** | Session 级（含 trace） | Agent 级（message 表独立） | Rollout 文件（SessionState 序列化） | JSONL 本地文件 |
| **调试可见性** | `/lab` trace inspector 可见 tool_events | ADE / API 可见完整 message 历史 | `--show-raw` 可见原始 items | `/transcript` 可见完整 JSONL |

---

## 6. 对 V3 销售场景的具体影响

### 6.1 场景 A：多轮 memory 维护

用户第一轮说"我们是做 SaaS 的"，Agent 调用 `core_memory_append(human, "用户公司做 SaaS")`。

第二轮用户说"刚才说的你能记住吧"，Agent 回答"当然"——**但这不是因为 prompt 里有 tool loop 记录，而是因为 `human` block 的 value 被修改了**。如果用户问"你刚才做了什么操作来记住的"，Agent 无法从 prompt 中重建自己的行为，只能 hallucinate 一个回答。

### 6.2 场景 B：Tool 失败后的恢复

第一轮 Agent 调用 `memory_insert` 但传错了参数（比如 `label="humna"`），系统返回 error。第一轮末 Agent 用 `send_message` 说"抱歉让我再试一次"。

第二轮 prompt 里**完全没有 `memory_insert` 失败的那次调用**。Agent 可能：

1. 再次犯同样的拼写错误（因为看不到之前的 error）
2. 认为自己已经成功执行了（因为 block 可能被其他路径修改）

### 6.3 场景 C：多 step 策略执行

销售场景中 Agent 需要：先 append 客户信息 → 再 replace 产品定位 → 最后 send_message。V3 的 4 步上限已经让这种策略紧张；而如果用户在下个 turn 追问"你为什么换了产品定位描述"，Agent 看不到之前 `memory_replace` 的调用历史，只能基于当前 block value 反向推断。

---

## 7. 建议：Adapt（改造而非复刻）

### 7.1 不做的事（被 _active.md §5 禁止或 over-engineering）

- **不接 Letta server**：Letta 的完整 message 表 + agent 实体 ORM 属于跨 session 持久化，被 `_active.md` §5 禁止。
- **不引入 archival_memory**：虽然 Letta 的 `message` 表具备 archival 能力，但当前 scope 是修复"跨 turn tool loop 丢失"，不是补全三层 memory。
- **不引入 request_heartbeat**：V3 的 `send_message` 终止机制已足够，不需要 Letta 式的模型自主声明"再一步"。
- **不做 Provider 抽象**：继续用 Tencent TokenHub native FC，不改 LLMClient 工厂。

### 7.2 要做的最小改造（sandbox runtime POC 边界内）

1. **扩展 `V3SandboxMessage` schema**
   - 增加 `tool_calls: list[dict] | None`
   - 增加 `tool_call_id: str | None`
   - 保持向后兼容（现有 message 可自然为 null）

2. **修改 `_execute_tool_calls` 写路径**
   - 在 turn 内每次 tool call 执行后，把 `assistant(tool_calls)` 和 `tool(result)` 消息 append 到 `session.messages`
   - 生成 `tool_call_id`（UUID 或单调字符串）用于配对

3. **修改 `_build_tool_loop_messages` 读路径**
   - 不再把 `session.messages` 渲染成 `[role] content` 文本拼接
   - 而是直接把消息转换成 TokenHub / OpenAI 的 message format（含 `tool_calls` / `tool_call_id`）

4. **（可选）引入 normalize 不变式**
   - 参考 Codex 的 `normalize_history`：在每次构建 prompt 前检查所有 `tool_use` 都有对应的 `tool_result`
   - 发现 orphaned call 时移除或标记，避免 malformed prompt

5. **考虑 `_return_turn` 的 final message**
   - 如果最后一轮 assistant 消息包含 `send_message` + 可能的其他 tool_calls，确保 send_message 的 text 作为 `assistant` role content 保留
   - 或者更完整地保留最后一轮 assistant 的 `tool_calls` 结构

### 7.3 Schema 变更的持久化影响

V3 的 DB 持久化是 opt-in（`backend/alembic/versions/20260430_0006_*.py`）。`V3SandboxMessage` 当前以 JSON 形式嵌套在 `V3SandboxSession` 的 `messages` 字段中。增加 `tool_calls` / `tool_call_id`：

- **不需要新 DB 表**：现有 JSONB/array 列可以容纳新增字段
- **需要 Alembic migration**：如果 `V3SandboxSession` 表有 schema 校验（如 Pydantic 序列化后存 JSON），需要确认旧数据加载时新字段为 null 不会报错
- **与 `_active.md` §5 的关系**：本次变更属于"sandbox runtime POC 自然延伸"，不触碰"超出 opt-in V3 sandbox persistence 的 memory DB schema"红线

---

## 8. 与 ADR-010 / letta-comparison.md 的对位

| 本文档章节 | 对位 ADR-010 章节 | 对位 letta-comparison.md 行号 |
|---|---|---|
| §1 根因（messages[-8:] 截断） | §5 "`messages[-8:]` 硬截断 → 替换" | #9 Context 压缩 / 摘要 |
| §2 Letta message_ids / append 路径 | §5 "`message_ids` 是 in-context 指针" | #8 In-context 与历史消息 |
| §2 Letta summarize | §4.1 "Context 压缩 / 摘要：必要" | #9 Context 压缩 / 摘要 |
| §3 Codex normalize_history | §4.2 "可选：视用户反馈再开" | — |
| §7.2 建议改造 | §6 优先级 #3 "Context 压缩 / step 上限调整" | #1、#8、#9 |
| §7.3 Schema 变更边界 | §7 "不修改 ADR 与对照表外的代码" | — |

---

## 9. 结论

**V3 当前"跨 turn 丢失 tool loop"是一个 runtime prompt 组装层面的缺陷，不是一个需要引入 Letta server 或重新设计 persistence 架构的大缺口。**

修复路径明确且局限在 `schemas.py` + `graph.py` 的读写路径上：

1. 让 `V3SandboxMessage` 能容纳 tool 元数据
2. 让 turn 内的 tool loop 消息流写回 `session.messages`
3. 让 `_build_tool_loop_messages` 把这些元数据传给 LLM

这一改造与 ADR-010 §6 推荐的优先级 #3（Context 压缩 / step 上限调整）天然耦合——一旦 tool loop 消息成为历史的一部分，`messages[-8:]` 硬截断会变得更加危险（可能截断掉关键的 tool_result）。因此建议**在同一 task 中同时处理 tool loop 持久化和 in-context window 管理策略**。

---

## 10. Implementation status

> 更新时间：2026-05-06

### 10.1 已修正的过时描述

- **§5 对比表中 "`messages[-8:]` 硬截断"**：当前代码（截至 `graph.py` 2026-05-05）已替换为 `max_context_messages = 32` + `_maybe_run_summarization` 递归摘要机制。研究文档中的 `messages[-8:]` 描述基于较早版本，现已过时。
- **§1.1 根因定位**：`_build_tool_loop_messages`（`graph.py:410-523`）当前已使用 `after_cursor` 而非直接 `messages[-8:]`，但核心问题不变——仍然只提取 `[role] content` 文本，tool 元数据不进入 prompt。

### 10.2 已落地改造

| 章节 | 结论 | 状态 |
|---|---|---|
| §7.2 改造 #1：扩展 `V3SandboxMessage` schema | 增加 `tool_calls`、`tool_call_id`，扩展 `role` 为 `user/assistant/tool` | **进行中** — `task_2026_05_06_v3_cross_turn_tool_loop_persistence.md` |
| §7.2 改造 #2：修改 `_execute_tool_calls` 写路径 | turn 内 tool loop 消息写回 `session.messages` | **进行中** |
| §7.2 改造 #3：修改 `_build_tool_loop_messages` 读路径 | 从文本拼接改为原生 message list | **进行中** |
| §7.2 改造 #4：normalize 不变式 | 参考 Codex CLI | **deferred** — 本次 task 不实现，留作后续 context 压缩扩展时的安全网 |
| §7.2 改造 #5：`_return_turn` final message | 调整 final message 处理逻辑 | **进行中** |
| §9 建议（同时处理 tool loop 持久化 + in-context window） | `_maybe_run_summarization` 增加配对安全截断 | **进行中** |

### 10.3 未落地 / deferred

- **独立 message 表 + `message_ids` in-context 指针**：需要超出当前 opt-in JSON persistence 的 DB schema 变更，被 `_active.md` §5 禁止。
- **`normalize_history` 不变式**：Codex CLI 式两遍扫描 orphan 清理，当前 sandbox runtime POC 中暂不实现。
- **archival_memory / 三层 memory**：超出当前 scope。
- **Letta server 接入**：被 `_active.md` §5 明确禁止。

---

*本研究文档只提供分析结论，不自动开放实现授权。如需实施 §7.2 的改造，仍需通过 `docs/delivery/tasks/_active.md` 显式开 task。*
