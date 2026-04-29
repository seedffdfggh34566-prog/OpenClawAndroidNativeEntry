# OpenClaw Context Management Reference And Borrowing Plan

更新时间：2026-04-29

## 1. 文档定位

本文档记录对 upstream OpenClaw 上下文管理系统的代码分析，并给出本仓库
V2 Sales Workspace / Product Sales Agent 可以借鉴的方案。

本文件是方案层参考，不是 active implementation task，不声明当前 V2.1 或 V2.2
milestone 完成，也不授权直接实现 LangGraph、MCP、搜索、联系人、CRM 或完整
context engine 插件系统。

本次分析参考：

- upstream repo：`https://github.com/openclaw/openclaw`
- 本地只读参考目录：`/tmp/openclaw-reference`
- 参考提交：`d130a77a fix(parallels): default OpenAI smokes to gpt-5.5`
- 官方文档：
  - `docs/concepts/context.md`
  - `docs/concepts/context-engine.md`
  - `docs/concepts/compaction.md`
  - `docs/concepts/session.md`
  - `docs/concepts/system-prompt.md`

## 2. 与本项目边界

本项目的正式边界保持不变：

```text
ConversationMessage
-> AgentRun
-> ContextPack
-> Runtime / Product Sales Agent execution layer
-> WorkspacePatchDraft
-> WorkspacePatchDraftReview
-> human accept / apply
-> WorkspacePatch
-> Sales Workspace Kernel
-> formal workspace objects
```

因此，OpenClaw upstream 的上下文管理只能作为 Runtime 输入编译、预算控制、诊断
和长对话治理的参考。不能把 upstream session、prompt、checkpoint、memory file、
LangGraph state 或插件 context engine 当作本项目的 formal workspace truth layer。

当前允许借鉴：

- ContextPack 编译生命周期。
- prompt / context 预算报告。
- recent messages 裁剪策略。
- tool result / runtime output 裁剪策略。
- future compaction summary 的对象边界。
- context diagnostics / inspection 视图。

当前不允许自动引入：

- upstream OpenClaw gateway/session store 作为本项目主存。
- 完整插件式 context engine registry。
- durable LangGraph checkpoint / resume lifecycle。
- MCP 内部服务化。
- V2.2 evidence/search/contact implementation。
- 个人助理式 `AGENTS.md` / `SOUL.md` 文件作为 Product Sales Agent 长期记忆主存。

## 3. Upstream OpenClaw 上下文系统拆解

OpenClaw 的上下文管理不是单一模块，而是一条从 workspace 文件、会话历史、工具输出、
上下文引擎、压缩和诊断共同组成的链路。

### 3.1 Context 定义

OpenClaw 将 context 定义为每次模型运行实际发送给模型的全部内容，包括：

- system prompt。
- conversation history。
- tool calls / tool results。
- attachments。
- compaction summaries。
- provider wrapper / hidden headers。

它明确区分：

- context：当前模型窗口内的内容。
- memory：可持久化、可后续重新装载的内容。
- session transcript：会话历史记录。

这个定义对本项目非常重要：`ContextPack` 也应被视为 Runtime 输入快照，而不是业务主存。

### 3.2 System Prompt 和 Project Context

OpenClaw 每轮重建 system prompt，并把 workspace bootstrap files 注入 Project Context。

典型注入文件包括：

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md`
- `MEMORY.md`

核心代码：

- `/tmp/openclaw-reference/src/agents/system-prompt.ts`
- `/tmp/openclaw-reference/src/agents/pi-embedded-runner/system-prompt.ts`
- `/tmp/openclaw-reference/src/agents/pi-embedded-helpers/bootstrap.ts`
- `/tmp/openclaw-reference/src/agents/bootstrap-budget.ts`

关键机制：

- per-file budget：`bootstrapMaxChars`，默认约 12000 chars。
- total budget：`bootstrapTotalMaxChars`，默认约 60000 chars。
- raw vs injected 统计。
- truncated / near-limit 报告。
- truncation signature 去重，避免重复提示。
- 被截断时在 prompt 中注入 warning，提醒模型直接读取源文件。

可借鉴点：

- 本项目不应注入任意 Markdown 文件作为 Product Sales Agent 主记忆。
- 但可以借鉴 `raw/injected/truncated/nearLimit` 诊断模型，给
  `SalesAgentTurnContextPack` 增加可审计的 `context_budget_report`。

### 3.3 Session 和 Transcript

OpenClaw 的 session 由 gateway 管理，session store 保存 session metadata，
transcript JSONL 保存会话历史。

核心代码：

- `/tmp/openclaw-reference/src/config/sessions/types.ts`
- `/tmp/openclaw-reference/src/config/sessions/store.ts`
- `/tmp/openclaw-reference/src/config/sessions/transcript.ts`
- `/tmp/openclaw-reference/src/config/sessions/paths.ts`

关键机制：

- session key 归一化。
- DM / group / channel / cron 的隔离策略。
- sessionStartedAt、lastInteractionAt、updatedAt 分离。
- session maintenance：pruneAfter、maxEntries、warn/enforce。
- transcript 和 session metadata 分层。

可借鉴点：

- 本项目已经有 `ConversationThread`、`ConversationMessage`、`AgentRun`、
  `ContextPack` persistence，这是更符合 Sales Workspace 的结构化路径。
- 可以借鉴 session lifecycle 字段分离思想，但不应把 OpenClaw JSONL transcript
  移植为本项目正式业务主存。

### 3.4 Context Engine 接口

OpenClaw 把上下文生命周期抽象为 `ContextEngine`：

```text
bootstrap -> ingest / ingestBatch -> assemble -> compact -> afterTurn -> maintain
```

核心代码：

- `/tmp/openclaw-reference/src/context-engine/types.ts`
- `/tmp/openclaw-reference/src/context-engine/legacy.ts`
- `/tmp/openclaw-reference/src/context-engine/registry.ts`
- `/tmp/openclaw-reference/src/context-engine/delegate.ts`
- `/tmp/openclaw-reference/src/agents/harness/context-engine-lifecycle.ts`

关键接口含义：

- `bootstrap`：首次看到 session 时导入历史或初始化状态。
- `ingest` / `ingestBatch`：把单条消息或一轮消息纳入引擎。
- `assemble`：按 token budget 输出本轮模型可见消息，可附加 system prompt addition。
- `compact`：把旧上下文摘要 / 缩减。
- `afterTurn`：一轮完成后持久化或触发后台维护。
- `maintain`：安全 rewrite transcript entry 或执行后台维护。

可借鉴点：

- 本项目暂不需要插件 registry。
- 但可以采用同样的生命周期术语定义 Sales Workspace context pipeline：

```text
collect_sources
-> assemble_context_pack
-> fit_budget
-> record_budget_report
-> execute_runtime
-> persist_trace
-> optional_summary_maintenance
```

这比直接把 prompt 拼接逻辑散落在 runtime 文件里更可维护。

### 3.5 Tool Result Guard 和 Context Pruning

OpenClaw 对工具输出使用两层轻量保护：

- 单个 tool result 超过窗口比例时先裁剪。
- 整体估算超过安全阈值时抛出 preemptive overflow，让上层 compaction/retry 介入。

核心代码：

- `/tmp/openclaw-reference/src/agents/pi-embedded-runner/tool-result-context-guard.ts`
- `/tmp/openclaw-reference/src/agents/pi-hooks/context-pruning/pruner.ts`

关键机制：

- tool result 与普通消息区别估算。
- 保留 head / tail，中间用 truncation marker。
- hard clear 只针对可裁剪工具。
- 不修改 transcript 主存，只影响当前 prompt context。

可借鉴点：

- V2.2 search 后，中文网页搜索结果、网页正文、候选公司列表很容易挤爆上下文。
- 应先设计 `SourceEvidenceExcerpt` / `SearchResultSnippet` 的 budget 和裁剪策略。
- 不应让 Runtime 直接把完整网页正文塞进 prompt。

### 3.6 Compaction

OpenClaw compaction 用于长会话窗口治理：

- 旧消息被摘要为 compaction entry。
- 最近消息保持原文。
- 可在 context overflow 或 timeout 后触发重试。
- 可创建 successor transcript，避免原地重写完整历史。

核心代码：

- `/tmp/openclaw-reference/src/agents/pi-embedded-runner/compact.ts`
- `/tmp/openclaw-reference/src/agents/pi-embedded-runner/compact.runtime.ts`
- `/tmp/openclaw-reference/src/agents/pi-embedded-runner/compaction-successor-transcript.ts`
- `/tmp/openclaw-reference/src/agents/pi-embedded-runner/manual-compaction-boundary.ts`

可借鉴点：

- 本项目未来长对话不应无限读取所有 `ConversationMessage`。
- 可以设计 `ConversationThreadSummary` 或 `ContextCompactionSummary`，但它必须是
  derived context artifact，不得替代正式 workspace objects。
- 如果实现 summary，应记录：
  - source message range。
  - summary prompt version。
  - source workspace version。
  - first_kept_message_id。
  - tokens/chars before and after。
  - whether summary is safe for runtime use only。

## 4. 本项目现状对比

当前本项目已有基础：

- `SalesAgentTurnContextPack`：`backend/sales_workspace/chat_first.py`
- research round `ContextPack`：`backend/sales_workspace/context_pack.py`
- LLM runtime prompt：`backend/runtime/sales_workspace_chat_turn_llm.py`
- chat-first trace persistence：`sales_workspace_conversation_messages`,
  `sales_workspace_agent_runs`, `sales_workspace_context_packs`
- dev LLM trace：`backend/runtime/llm_trace.py`

当前缺口：

1. `research_round` ContextPack 和 `sales_agent_turn` ContextPack 分散，没有统一编译生命周期。
2. `SalesAgentTurnContextPack` 缺少明确 budget report。
3. recent messages 的保留 / 裁剪规则需要更显式。
4. LLM prompt 中 runtime_input 仍偏整包 JSON，未来长上下文会变重。
5. LLM trace 已有，但 context budget / truncation / omitted source 诊断还不完整。
6. 暂无 conversation summary / compaction artifact；当前短对话可接受，但长对话会累积风险。

## 5. 借鉴方案：Sales Workspace Context Pipeline

建议把本项目的上下文管理定义为一条 backend-owned pipeline，而不是直接引入
OpenClaw context engine。

### 5.1 目标

```text
Structured SalesWorkspace truth
+ current ConversationThread
+ active DraftReview state
+ latest AgentRun trace
    -> SalesWorkspaceContextPipeline
    -> SalesAgentTurnContextPack
    -> Runtime / LLM
    -> assistant_message_draft + WorkspacePatchDraft?
```

Pipeline 目标：

- 控制每轮 Runtime 输入大小。
- 明确哪些来源进入上下文，哪些被裁剪或省略。
- 保证当前产品理解和获客方向优先。
- 保证 Draft Review / kernel boundary 不丢失。
- 为后续 V2.2 search evidence 留出 source evidence budget 机制。
- 不让 Runtime 自行遍历 DB 或 Markdown projection 拼 prompt。

### 5.2 建议生命周期

建议定义内部函数或服务层对象：

```text
collect_context_sources(workspace_id, thread_id, user_message_id)
assemble_sales_agent_turn_context_pack(sources, budget)
fit_sales_agent_turn_context_budget(pack, budget)
build_context_budget_report(raw_sources, fitted_pack)
persist_context_pack(pack, report)
```

对应 OpenClaw 映射：

| OpenClaw concept | 本项目对应物 | 是否现在实现 |
|---|---|---|
| bootstrap Project Context | structured workspace current objects | 已有局部 |
| session transcript | ConversationMessage / ConversationThread | 已有 |
| context engine assemble | ContextPack compiler | 应强化 |
| tool result pruning | future search/source excerpt pruning | V2.2 前只设计 |
| compaction | future ConversationThreadSummary | 暂不实现 |
| /context diagnostics | dev diagnostics inspector / trace endpoint | 可强化 |

### 5.3 Source priority

`sales_agent_turn` ContextPack 推荐优先级：

1. `kernel_boundary`
2. `workspace_id`, `workspace_version`, `thread_id`, `agent_run_id`
3. 当前 `ProductProfileRevision`
4. 当前 `LeadDirectionVersion`
5. active / latest `WorkspacePatchDraftReview` 摘要
6. 本轮 user message
7. 最近 N 条同 thread conversation messages
8. 最近 AgentRun outcome 摘要
9. open questions
10. blocked capabilities
11. future source evidence excerpts

当预算不足时，不得裁剪：

- kernel boundary。
- 当前 product profile 的核心摘要。
- 当前 lead direction 的核心摘要。
- 本轮 user message。
- source_versions / input_refs。

可以优先裁剪：

- older assistant wording。
- older rejected draft details。
- verbose runtime metadata。
- candidate reason long text。
- future raw source excerpts。

### 5.4 Budget report

建议新增 derived metadata，而不是新增 formal object 语义：

```json
{
  "token_budget_chars": 6000,
  "raw_chars": 8420,
  "injected_chars": 5980,
  "truncated_chars": 2440,
  "sections": [
    {
      "name": "current_product_profile_revision",
      "raw_chars": 1280,
      "injected_chars": 1280,
      "truncated": false,
      "priority": "must_keep"
    },
    {
      "name": "recent_messages",
      "raw_chars": 4200,
      "injected_chars": 1900,
      "truncated": true,
      "strategy": "keep_latest_user_and_assistant_pairs"
    }
  ],
  "omitted_sources": [
    {
      "source_ref": "ConversationMessage:msg_old_001",
      "reason": "outside_recent_window"
    }
  ]
}
```

该 report 可以存入：

- `SalesAgentTurnContextPack.source_versions` 的扩展字段，或
- `AgentRun.runtime_metadata.context_budget_report`，或
- dev-only diagnostics payload。

优先建议放在 `AgentRun.runtime_metadata`，因为它是运行诊断，不是正式 workspace 主存。

### 5.5 Recent message 策略

建议先采用 deterministic 策略，不引入 LLM summary：

```text
must_keep:
  - current user message
  - latest assistant draft summary if it produced active review
  - last 4 same-thread user/assistant turns

optional_keep:
  - additional older user turns by newest-first order
  - rejected draft summaries if directly related to current message

drop_or_summarize_later:
  - verbose assistant text with no object refs
  - old failed AgentRun details
  - old draft operation payloads after they are applied/rejected
```

这是低风险路径：不需要 schema migration，也不改变 runtime lifecycle。

### 5.6 Future summary artifact

当同一 thread 消息变长时，再考虑新增：

```text
ConversationThreadSummary
```

最小字段：

```text
workspace_id
thread_id
summary_id
source_message_start_id
source_message_end_id
first_kept_message_id
summary_text
summary_kind = runtime_context_only
prompt_version
source_workspace_version
created_by_agent_run_id
created_at
```

约束：

- summary 只能服务 Runtime 上下文。
- summary 不得写回 `ProductProfileRevision` / `LeadDirectionVersion`。
- summary 不得替代 Draft Review。
- summary 生成失败不得影响正式 workspace state。

这一步需要 dedicated task 和 persistence design，不应混入当前短期优化。

## 6. 推荐实施路线

### Phase A：文档和契约强化

目标：

- 更新 ContextPack compiler spec，覆盖 `sales_agent_turn`。
- 定义 `context_budget_report`。
- 定义 recent messages 裁剪策略。
- 定义 future compaction summary 非目标。

验证：

- docs consistency。
- existing tests 不要求变更。

### Phase B：ContextPack compiler 代码整理

目标：

- 拆出 `sales_agent_turn` context compiler。
- 把 context source collection、budget fit、report build 分开。
- 为 long recent messages 加单元测试。

建议文件：

- `backend/sales_workspace/context_pack.py`
- `backend/sales_workspace/chat_first.py`
- `backend/tests/test_sales_workspace_chat_first_api.py`
- `backend/tests/test_sales_workspace_chat_first_llm_runtime.py`

验证：

- targeted backend pytest。
- `git diff --check`。

### Phase C：Diagnostics 强化

目标：

- 在 dev diagnostics inspector 中展示 context pack size、truncation、omitted sources。
- 在 LLM trace 中保留 context pack id、source refs、budget report summary。
- 避免记录 secrets、Authorization header 或完整 provider request body。

验证：

- diagnostics tests。
- trace secret redaction tests。

### Phase D：Long-thread summary 设计

只有当真实长对话和上下文溢出成为已验证问题时再开放。

目标：

- 设计 `ConversationThreadSummary` 或 equivalent derived artifact。
- 明确 migration、persistence、failure path。
- 明确 summary 与 formal objects 的边界。

这一步属于 backend/runtime boundary work，需要 dedicated task。

## 7. 不建议照搬的 upstream 能力

不建议直接照搬：

1. 完整 plugin `ContextEngine` registry。
   - 本项目当前没有多引擎切换需求。
   - 过早引入会扩大 runtime boundary。

2. `AGENTS.md` / `SOUL.md` 作为 Product Sales Agent 记忆主存。
   - 本项目 Product Sales Agent memory 必须落结构化 backend objects。

3. full transcript compaction rotation。
   - 本项目已采用 DB trace tables。
   - 如需 summary，应设计 DB artifact，而不是复制 JSONL successor transcript。

4. MCP / tool server 参与内部 context assembly。
   - 当前 backend Python service 直接编译 ContextPack 更简单、更可控。

5. V2.2 evidence/search/contact 同步引入。
   - search/contact 仍 blocked。
   - 只能预留 source evidence excerpt budget，不实现能力本身。

## 8. 决策建议

近期最值得做的是：

> 将 OpenClaw 的 context diagnostics 和 lifecycle 思路，收敛成本项目的
> `SalesWorkspaceContextPipeline`，先强化 `ContextPack` 编译、预算报告和
> recent message 裁剪，而不是引入完整 context engine。

推荐下一个可执行 task：

```text
Task: V2.1 Sales Workspace ContextPack Budget Diagnostics

Scope:
- define context_budget_report shape
- add deterministic recent_messages budget fitting
- record budget report in AgentRun runtime_metadata
- expose summary in dev diagnostics
- no schema migration unless explicitly approved
- no LangGraph / MCP / V2.2 search/contact
```

该 task 完成后，再根据真实长对话或 V2.2 source evidence 压力决定是否进入
conversation summary / compaction artifact 设计。

## 9. Boundary Check

本方案不改变 backend/runtime 边界：

- Runtime 仍只产出 assistant draft 和 `WorkspacePatchDraft`。
- 正式对象写回仍经过 Draft Review 和 Sales Workspace Kernel。
- `ContextPack` 仍是 Runtime 输入快照，不是 formal workspace truth。
- errors 仍应记录在 `AgentRun.error` 或 runtime metadata，而不是部分 mutate workspace。
- 不新增 `waiting_for_user`、resume、durable checkpoint 或 queue-worker lifecycle。
- 不引入 V2.2 search/contact formal object。

