# Letta ↔ V3 Sandbox 子系统对照表

更新时间：2026-05-02

## 1. 文档定位

本文档是 V3 Letta Reference Study (Phase D2) 的子系统对照表，配合 [ADR-010](../../adr/ADR-010-letta-as-reference-architecture.md) 使用。

本文档**不**冻结实现，**不**承诺后续 (A) 阶段开 task 的具体顺序，**不**复制 Letta 源码。它只在子系统粒度上记录 Letta 与当前 V3 sandbox 的对应位置和行为差异，让后续每个 (A) task 都能从本表直接索引到 Letta 源码以及当前 V3 待改造文件。

## 2. 引用版本

- **Letta release**：`0.16.7`
- **Letta commit**：`f33324768950e6752f80d6c725873cc92d22f8b2`
- **本地阅读副本**：`~/projects/_references/letta/`（仓库外 sibling 目录，**未** vendor、**未** 作为 submodule、**未**进 git）
- **License**：Apache-2.0（仅阅读，不复制代码）

V3 当前对位代码以 `backend/runtime/v3_sandbox/`、`backend/api/v3_sandbox.py`、`backend/alembic/versions/` 中 V3 相关版本为准。

## 3. 子系统对照

| # | 子系统 | Letta 源码位置 | 当前 V3 对应位置 | 行为差异 | (A) 优先级 |
|---|---|---|---|---|---|
| 1 | **Agent loop / step 上限** | `letta/agent.py:1758` 主类；`letta/agents/letta_agent_v3.py:222` `step(max_steps=DEFAULT_MAX_STEPS)`；`letta/constants.py:75` `DEFAULT_MAX_STEPS=50` | `backend/runtime/v3_sandbox/graph.py:62` `run_v3_sandbox_turn`；五节点 LangGraph：`load_state → compose_context → call_agent_with_tools → execute_tool_calls → return_turn` | Letta 单 turn 默认允许 50 step；V3 在 `graph.py:367` `_continue_or_return` 硬上限为 4 个 assistant call / 16 个 tool event，超出抛 `v3_tool_loop_exhausted`。Letta 用 `request_heartbeat` 让 agent 显式决定是否继续；V3 用 `send_message` 出现作为终止条件 | 中 |
| 2 | **Heartbeat / 多 step 控制** | `letta/agent.py:563` 解析 `request_heartbeat` kwarg；`letta/agent.py:336` 强制 heartbeat 路径；错误情况 `letta/agent.py:629/666/687` `return messages, False, True` | 无；V3 当前由 `send_message` 是否被调用决定终止 | Letta 让模型自己声明"还要再来一步"；V3 是被动循环到 `send_message` 出现。两者各有道理，Letta 的好处是模型可在 tool call 中显式 yield 控制权 | 低（先稳住 step 上限，再考虑 heartbeat） |
| 3 | **Memory 工具集** | `letta/functions/function_sets/base.py:71` `send_message`；`:87` `conversation_search`（hybrid 文本+语义）；`:164` `archival_memory_insert`；`:194` `archival_memory_search`；`:246` `core_memory_append`；`:263` `core_memory_replace`；`:311` `memory_replace`（带 line-number 防御）；`:391` `memory_insert`（line-based）；`:488` `memory_rethink`；`:520` `memory_finish_edits` | `backend/runtime/v3_sandbox/graph.py:425` `_core_memory_tools()`：`core_memory_append`、`memory_insert`（substring anchor，非 line-number）、`memory_replace`、`send_message` | V3 缺 `archival_memory_*`、`conversation_search`、`memory_rethink`、`memory_finish_edits`。`memory_insert` 语义不同：Letta 按行号 `insert_line`；V3 按 substring `insert_after`。Letta 工具描述里有大量 line-number 防御（`CORE_MEMORY_LINE_NUMBER_WARNING`），V3 无类似机制 | 高（archival 是最大单缺口） |
| 4 | **Block schema 字段** | `letta/schemas/block.py:13` `BaseBlock`：`value/limit/label/read_only/description/metadata/hidden/tags/template_*/preserve_on_migration/project_id/deployment_id` | `backend/runtime/v3_sandbox/schemas.py:91` `CoreMemoryBlock`：`label/value/limit/read_only/updated_at` | V3 缺 `description`、`metadata`、`tags`、`template_*`、`hidden`。`description` 在 Letta 里是给模型看的"这个 block 是干什么的"提示，对 prompt 质量影响显著。`metadata` 是任意 dict，可承载用户/agent 自定义属性 | 中（`description` 应优先补） |
| 5 | **Block limit 默认值** | `letta/constants.py:433-435`：persona/human=20000、其他=100000 | `backend/runtime/v3_sandbox/schemas.py:94` `limit: int = Field(default=2000, ge=1, le=20000)` | V3 默认 2000 char、上限 20000；Letta 默认大一个数量级。短上限在长会话和细粒度 customer_intelligence 场景会快速触顶 | 中（与 (A) archival 同期评估） |
| 6 | **Block 共享 / multi-agent** | `letta/orm/block.py:65-72` `agents` 反向关系经 `blocks_agents` 多对多；`letta/orm/block.py:56` `version` 乐观锁；`letta/orm/block_history.py` 记录历史；`letta/orm/blocks_agents.py` junction 表 | V3 block 内嵌在 `V3SandboxSession` 内；`backend/alembic/versions/20260430_0006_*.py` 记录 transition events 但 block 本身不独立成表 | V3 当前 block 与 session 1:1 绑定；Letta block 是独立实体，可被多个 agent 引用、有版本号、有完整历史。这是"跨 session agent 持久化"的基础设施 | 中（与 (A) cross-session 一并设计） |
| 7 | **Agent 一等实体** | `letta/schemas/agent.py:67` `AgentState`：`id/name/system/llm_config/blocks/tools/sources/tags/identities/message_buffer_autoclear/enable_sleeptime/compaction_settings`；`letta/orm/agent.py:523` ORM 主表 | 无；V3 当前最大持久化单元是 `V3SandboxSession`（`backend/runtime/v3_sandbox/schemas.py`） | Letta agent 跨 session 持久；V3 session 即终点。复刻 (A) 需要在 ORM 与 schema 层引入 agent 概念，并把 blocks/messages 反向到 agent | 高（"跨 session agent 持久化身份"是 ADR-010 圈定的三大缺口之一） |
| 8 | **In-context 与历史消息** | `letta/schemas/agent.py:78` `message_ids: List[str]` 仅保存 in-context message 引用；全量历史在 `message` 表 | `backend/runtime/v3_sandbox/graph.py:386` `recent_messages: messages[-8:]`；session 自身保存全量 messages 到内存与 DB | Letta in-context 是 agent state 的一部分（指针列表），全量在 message manager；V3 是切片。当上下文超限时 Letta 走压缩路径，V3 直接抛错 | 高（与 (A) 压缩同 task） |
| 9 | **Context 压缩 / 摘要** | `letta/agent.py:1107` `summarize_messages_inplace`；`letta/agent.py:436` 触发条件 `total_tokens > context_window`；递归摘要 → 包成 user message → `prepend_to_in_context_messages` | 无；`graph.py:374` `if call_count >= 4: raise ValueError("v3_tool_loop_exhausted")`，`graph.py:386` `messages[-8:]` 截断 | V3 缺真摘要，靠硬截断 + 上限。短期可能"够用"，长期销售对话场景下会丢失客户信息 | 中（archival 优先于压缩，但二者后续耦合） |
| 10 | **Recall memory（对话历史检索）** | `letta/services/message_manager.py:1147` `search_mode="hybrid"` 支持 `vector/fts/hybrid/timestamp`；`function_sets/base.py:87` `conversation_search` 工具 | 无；session 内消息全部内嵌、不可工具检索 | V3 没有"agent 主动查历史"的能力。这是 Letta 三层内存的中间层，弥补 core memory 容量限制 | 低（先 archival，再考虑） |
| 11 | **Archival memory（长期向量库）** | `letta/services/passage_manager.py:543` `insert_passage`：通过 `LLMClient` 拿 embedding，写 `ArchivalPassage` SQL，可选双写 Turbopuffer；`letta/orm/passage.py` schema | 无 | V3 缺 archival 整层。`_active.md` §5 当前禁止"超出 sandbox POC 的 memory DB schema"，所以即便要补 archival，也需要先开 ADR / 单独 task 授权 | 高（ADR-010 推荐 (A) 第一刀切此处） |
| 12 | **Tool registry / 动态工具** | `letta/orm/tool.py` Tool 表；`letta/services/tool_*` 服务；agent 持有 `tools: List[Tool]`；支持 Python source / pip / MCP / sandbox 执行 | `graph.py:425` `_core_memory_tools()` 硬编码工具列表 | V3 工具集固定在四件套；Letta 工具是 agent state 的一部分，可挂卸 | 低（销售场景四件套足够，且 sandbox executor 被 §5 排除） |
| 13 | **System prompt 组装** | `letta/agent.py` 与 `letta/system.py` 共同负责：system + memory blocks（带 description）+ recall context hint + archival hint | `graph.py:401-422` `_build_tool_loop_messages`：单 system message 直接 dump JSON 形式的 blocks/working_state/customer_intelligence | Letta prompt 经多年迭代，块结构清晰、有 line-number 视图（带防御）；V3 是 JSON dump，模型解析负担大 | 中（与 #4 block description 一起重排） |
| 14 | **Pydantic schema 边界** | `letta/schemas/`：`agent.py / block.py / message.py / passage.py / memory.py / tool.py / llm_config.py / embedding_config.py` 拆得很细 | `backend/runtime/v3_sandbox/schemas.py` 单文件汇总；混有 `MemoryItem`（status: observed/inferred/...）、`WorkingState`、`CustomerIntelligenceDraft` 等 V2 残留概念 | V3 残留的 `memory_items` / `working_state` / `customer_intelligence` draft 与 core memory blocks 在职责上重叠（同样是"agent 维护的认知状态"），且对应的 `apply_action` 路径（`graph.py:887` `_apply_action`）在当前 native tool loop 中不再被调用 —— 是死代码 | 中（"保留 / 替换 / 抛弃"决策见 ADR-010 §5） |
| 15 | **持久化 / Alembic 迁移** | `letta/alembic/versions/` 大量 migration；ORM 覆盖 agent / block / block_history / message / passage / archive / source / tool / organization / user 等 | `backend/alembic/versions/20260430_0006_*.py` 等若干 V3 migration；只覆盖 sessions、trace events、core memory transition events | V3 持久化是"trace + transition" 取向；Letta 是"实体 + 关系" 取向。补 archival / agent 一等实体都要新建多张表 | 高（被 §5 显式禁止自动开放，必须单独授权 task） |
| 16 | **LLM provider 抽象** | `letta/llm_api/llm_client.py` LLMClient 工厂，按 `model_endpoint_type` 分发；agent 持 `llm_config + embedding_config` | `graph.py:219` `TokenHubClient(...)` 写死 Tencent TokenHub | V3 provider 单一；Letta 多 provider。V3 维持单一对销售场景与"native FC 已 smoke"是合理的，**不**建议在 (A) 阶段强行抽象 | 不开（除非未来要接非 TokenHub） |
| 17 | **Embedding** | `letta/services/passage_manager.py:572` 通过 `LLMClient.create(provider_type=embedding_endpoint_type)` 获取 embedding；`AgentState.embedding_config` 配置；可选 dual-write Turbopuffer | 无 | archival 开了即需要决定 embedding provider。TokenHub 是否提供 embedding endpoint，需在 (A) archival task 起步时验证 | 高（archival 前置） |
| 18 | **Web 调试入口** | ADE（独立 webapp/cloud），仓库根目录 `assets/` 提供素材 | `web/src/App.tsx`、`web/src/api.ts` 已实现 `/lab` Settings、Trace Inspector、Core Memory Blocks/Transitions 可视化 | V3 `/lab` 已能覆盖大部分单 agent 调试需求；ADE 偏 agent 设计与多 agent 管理。**不**建议参考 ADE 重做前端 | 不开 |
| 19 | **Sleeptime / 后台 agent** | `letta/schemas/agent.py:143` `enable_sleeptime`；`letta/agents/letta_agent_v3.py` 相关分支 | 无 | 被 `_active.md` §5 排除（"sleeptime agent / background worker"） | 不开 |
| 20 | **多 agent / agent-to-agent** | `letta/orm/group.py` Group + `groups_agents` + `groups_blocks`；agent 间 `send_message_to_agent_async` 等 | 无 | 被 §5 排除（"多 agent / agent-to-agent"） | 不开 |
| 21 | **Tool sandbox executor** | `sandbox/`、`letta/services/sandbox_*` 目录；E2B / 本地 subprocess | 无 | V3 销售场景的工具是 deterministic memory / send_message，不需要外部沙箱执行 | 不开 |

## 4. 缺口汇总（按 ADR-010 优先级）

下表只供 (A) 阶段开 task 时索引，**不**预先承诺顺序：

| 缺口 | 主要对照行 | (A) 阶段需要授权才能开 |
|---|---|---|
| **Archival memory 三层模型补齐** | #11、#3、#17、#15 | 是（被 §5 显式排除） |
| **跨 session agent 一等实体持久化** | #7、#6、#8、#15 | 是 |
| **Context 压缩 / 摘要** | #9、#8、#1 | 否（属 sandbox runtime POC 自然延伸；仍建议显式开 task） |
| **Block schema 扩字段（description / metadata）** | #4、#13 | 否（局部、可逆） |
| **Memory tool 描述对齐与 line-number 防御** | #3、#13 | 否（仅 prompt / tool description 改动） |
| **死代码清理（`memory_items` / `working_state` / `_apply_action`）** | #14 | 否（机械重构） |

## 5. 不在本对照表内的 Letta 子系统

明确**不**列入对照（ADR-010 已说明理由）：ADE 前端、Tool sandbox executor、多 agent / agent-to-agent、Sleeptime agent、CLI / SDK 客户端层、Cloud / org / billing / auth、Composio / MCP 集成、Identity / Group / 模板化 deployment 体系。

## 6. 维护规则

- 每次 (A) 阶段 task 完成后，只更新 **行为差异** 列对应行，并在 ADR-010 §6 追加变更记录。
- 不在本对照表里复制 Letta 源码片段；引用一律走 `letta/...:行号` + commit SHA。
- 升级 Letta pin 版本时，同步更新 §2 的 release tag / commit SHA，并 spot-check 行号。
