# Hermes Agent Context Management Reference And Borrowing Plan

更新时间：2026-04-29

## 1. 文档定位

本文档记录对 upstream Hermes Agent 上下文管理系统的代码分析，并对比前一份
OpenClaw context management reference，给出本仓库 V2 Sales Workspace /
Product Sales Agent 可以借鉴和不能照搬的方案。

本文件是方案层参考，不是 active implementation task，不声明当前 V2.1 或 V2.2
milestone 完成，也不授权直接实现 LangGraph、MCP、V2.2 search/contact、CRM、
完整 Hermes gateway、个人助理式 memory 文件，或完整 skills / plugin 平台。

本次分析参考：

- upstream repo：`https://github.com/NousResearch/hermes-agent`
- 本地只读参考目录：`/tmp/hermes-agent-reference`
- 参考提交：`6e9691f Merge pull request #17237 from NousResearch/bb/tui-paste-watchdog`
- 官方文档：
  - `https://hermes-agent.nousresearch.com/docs/developer-guide/context-compression-and-caching/`
  - `https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files`
  - `https://hermes-agent.nousresearch.com/docs/user-guide/features/memory`
  - `https://hermes-agent.nousresearch.com/docs/user-guide/features/skills`
  - `https://hermes-agent.nousresearch.com/docs/developer-guide/session-storage`

相关本项目文档：

- `docs/architecture/runtime/openclaw-context-management-reference.md`
- `docs/architecture/workspace/context-pack-compiler.md`
- `docs/architecture/runtime/v2-1-chat-first-runtime-design.md`
- `docs/architecture/runtime/v2-1-llm-runtime-boundary.md`

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

因此，Hermes 的上下文管理只能作为 Runtime 输入治理、长对话压缩、诊断、按需知识加载
和开发者体验的参考。不能把 Hermes 的 `MEMORY.md`、`USER.md`、SQLite session
store、skills、gateway transcript、plugin context engine 或个人助理 identity 当作本项目
formal workspace truth layer。

当前允许借鉴：

- frozen system prompt snapshot 的稳定性思路。
- context compression 的 head / middle / tail 分段策略。
- tool result cheap pruning 和 tool-call pair sanitizer。
- context pressure / budget diagnostics。
- session_search 的开发诊断和历史召回思路。
- skills progressive disclosure 的按需知识加载模式。

当前不允许自动引入：

- Hermes gateway / multi-platform session store 作为本项目正式主存。
- `MEMORY.md` / `USER.md` 作为 Product Sales Agent 长期记忆主存。
- skills 自我创建 / 自我修改作为产品销售知识库主流程。
- 完整 `ContextEngine` plugin registry。
- full SQLite FTS5 session store 替换当前 backend persistence。
- MCP 或外部 memory provider 作为内部 backend service architecture。
- `waiting_for_user`、resume、checkpoint、queue-worker 等未授权 runtime lifecycle。
- V2.2 search/contact/evidence implementation。

## 3. Hermes 上下文系统核心

Hermes 的核心不是单一压缩模块，而是一个长期个人 Agent 的记忆闭环：

```text
Context files / SOUL.md / MEMORY.md / USER.md / Skills index
        ↓
frozen system prompt snapshot
        ↓
current session transcript
        ↓
ContextEngine / ContextCompressor
        ↓
SQLite session store + FTS5 session_search
        ↓
memory / skills self-improvement
```

它的设计目标是让同一个个人 Agent 在 CLI、Telegram、Discord、Slack、WhatsApp
等入口之间保持身份、记忆、技能和会话连续性。这一点与本项目的 Product Sales Agent
不同：本项目的长期状态必须沉淀为结构化 Sales Workspace 对象，而不是个人助理记忆文件。

### 3.1 ContextEngine 插槽

核心代码：

- `/tmp/hermes-agent-reference/agent/context_engine.py`
- `/tmp/hermes-agent-reference/run_agent.py`
- `/tmp/hermes-agent-reference/tests/agent/test_context_engine.py`
- `/tmp/hermes-agent-reference/tests/gateway/test_compress_plugin_engine.py`

Hermes 的 `ContextEngine` 是一个可插拔槽位，默认实现是 `ContextCompressor`。
配置入口是 `context.engine`。接口重点包括：

- `update_from_response(usage)`：用 provider 返回的 usage 更新 token 状态。
- `should_compress(prompt_tokens)`：判断是否需要压缩。
- `compress(messages, current_tokens, focus_topic)`：返回压缩后的 OpenAI-format message list。
- `should_compress_preflight(messages)`：可选的 API 前粗估。
- `has_content_to_compress(messages)`：给手动 `/compress` 做低成本 guard。
- `on_session_start` / `on_session_end` / `on_session_reset`：session 边界回调。
- `get_tool_schemas` / `handle_tool_call`：给 context engine 暴露可选工具。

可借鉴点：

- 本项目可以把 `SalesWorkspaceContextPipeline` 做成内部稳定接口，但暂不需要插件化。
- 可以记录 context engine / compiler version，方便后续诊断和回放。
- `update_from_response` 的 usage 反馈可映射到本项目 `AgentRun.runtime_metadata` 的
  `context_budget_report`，但不应由 Runtime 直接写 formal workspace objects。

不建议照搬：

- 完整 plugin resolution。
- context engine 自带工具。
- session lifecycle 回调驱动正式业务状态。

### 3.2 默认 ContextCompressor

核心代码：

- `/tmp/hermes-agent-reference/agent/context_compressor.py`
- `/tmp/hermes-agent-reference/run_agent.py`
- `/tmp/hermes-agent-reference/gateway/run.py`

Hermes 默认压缩算法是四段式：

1. Cheap pre-pass：裁剪旧 tool result，不调用 LLM。
2. Protect head：保护 system prompt 和开头几条消息。
3. Protect tail：按 token budget 从尾部保留最近上下文，并强制保留最新 user message。
4. Summarize middle：用辅助模型生成结构化 handoff summary。

关键细节：

- 默认 compression threshold 约为模型 context window 的 50%。
- `protect_first_n` 默认 3，`protect_last_n` 默认 20。
- tail budget 来自 `threshold_tokens * summary_target_ratio`。
- summary budget 按被压缩内容比例计算，有最小值和上限。
- 压缩前会把旧 tool output 替换成一行摘要，例如 terminal 命令、read_file 路径、
  web_extract URL、search_files query。
- 会去重重复 tool result，避免同一文件多次读取造成 token bloat。
- 会缩短 assistant tool_call arguments，同时保持 JSON 有效。
- summary 失败时会插入 fallback marker，避免静默丢失上下文。
- 多次压缩时会迭代更新上一版 summary，而不是从零摘要。
- 压缩后会修复 orphan tool_call / tool_result pair，避免 provider 拒绝 message history。
- 有 anti-thrashing：连续压缩收益过低时跳过，提示用户开启新 session 或 guided compression。

特别值得本项目借鉴的是 latest user message anchoring。Hermes 专门修复了一个风险：
如果最新 user ask 被压进 middle summary，而 summary prefix 又要求模型只回答 summary 之后的
最新 user message，当前任务会被丢失。本项目做 recent-message fitting 时也必须保证：

- 当前 user message 永远不可裁剪。
- active draft review / pending ask 不可只存在于 summary。
- 被裁剪内容必须有 derived summary 或 explicit omitted marker。

不建议照搬：

- 直接用 LLM summary 替代结构化 ProductProfileRevision / LeadDirectionVersion。
- 用压缩后的 transcript 作为业务事实。
- 在没有明确任务时加入 manual `/compress` 产品功能。

### 3.3 双层压缩

Hermes 官方文档将上下文压缩分成两层：

- Gateway Session Hygiene：pre-agent 安全阀，约 85% context window 触发。
- Agent ContextCompressor：agent loop 内主压缩器，默认约 50% context window 触发。

核心代码：

- `/tmp/hermes-agent-reference/gateway/run.py`
- `/tmp/hermes-agent-reference/run_agent.py`

Gateway hygiene 的作用是防止跨平台消息堆积后，下一次 agent 调用直接超过 provider
context limit。它会粗估历史消息，必要时创建临时 `AIAgent` 执行压缩，并把压缩后的
transcript 写回新 session。

本项目不应直接复制 gateway hygiene，因为 Android / backend 当前不是 Hermes 式多入口个人
Agent gateway。但可以借鉴双层思想：

- API / service 层：对 `ConversationThread` 做 deterministic context fitting，不让 runtime 输入无界增长。
- Runtime 层：基于 provider usage 和 `ContextPack` 体积记录真实 context pressure。

### 3.4 Frozen system prompt snapshot 和 prompt caching

核心代码：

- `/tmp/hermes-agent-reference/run_agent.py`
- `/tmp/hermes-agent-reference/agent/prompt_caching.py`
- `/tmp/hermes-agent-reference/agent/anthropic_adapter.py`

Hermes 的 system prompt 在 session 开始时构建一次，后续 turn 复用同一份 snapshot。
内存写入、插件注入、subdirectory hints 等内容不会随意改写 system prompt，尽量放到 user
message 或 tool result 中，以保护 provider prefix cache。

Anthropic prompt caching 采用 `system_and_3`：

- breakpoint 1：system prompt。
- breakpoint 2-4：最近 3 条非 system message。
- 默认 cache TTL 5m，可配置 1h。

可借鉴点：

- 本项目的 Product Sales Agent prompt 应减少同一 thread 内非必要漂移。
- `SalesAgentTurnContextPack` 应承载变动上下文，system instruction 应尽量稳定。
- 未来接入 provider caching 时，应避免把易变数据塞入 system prompt。

不建议照搬：

- 因 prompt cache 而牺牲结构化 context freshness。
- 将 Product Sales Agent 的业务事实写入 system prompt 文件。

### 3.5 Context files 和 progressive subdirectory hints

核心代码：

- `/tmp/hermes-agent-reference/agent/prompt_builder.py`
- `/tmp/hermes-agent-reference/agent/subdirectory_hints.py`
- `/tmp/hermes-agent-reference/website/docs/user-guide/features/context-files.md`

Hermes 支持：

- `.hermes.md` / `HERMES.md`
- `AGENTS.md`
- `CLAUDE.md`
- `SOUL.md`
- `.cursorrules`
- `.cursor/rules/*.mdc`

启动时按优先级加载一个 project context type。进入子目录后，通过 tool call 参数中的 path
懒加载子目录 `AGENTS.md` / `CLAUDE.md` / `.cursorrules`，并把 hint 附加到 tool result，
而不是改写 system prompt。

可借鉴点：

- 本项目 Dev Agent workflow 可以继续保留 repo `AGENTS.md` / subtree `AGENTS.md`。
- Product Sales Agent 不能直接把 repo `AGENTS.md` 当产品记忆。
- 未来如需要销售行业 playbook，可采用按需加载的知识包，而不是一次性注入所有文档。

### 3.6 Persistent memory

核心代码：

- `/tmp/hermes-agent-reference/tools/memory_tool.py`
- `/tmp/hermes-agent-reference/agent/memory_manager.py`
- `/tmp/hermes-agent-reference/agent/memory_provider.py`

Hermes 内建两类文件记忆：

- `MEMORY.md`：agent 的环境事实、项目约定、工具经验。
- `USER.md`：用户偏好、身份、沟通风格。

设计特点：

- 字符上限很小，默认约 2200 chars / 1375 chars。
- session start 时注入 frozen snapshot。
- mid-session 写文件立即持久化，但当前 system prompt 不变。
- `add` / `replace` / `remove` 使用短 substring 匹配。
- 写入前做 prompt injection / exfiltration scan。
- 工具 schema 明确提示不要保存 temporary task state，task progress 应靠 session_search。

本项目不能把这个设计作为 Product Sales Agent 主记忆。原因：

- 销售工作区的业务事实必须是结构化对象。
- 用户对产品、线索方向、研究证据的修改需要版本、审计、draft review 和 kernel writeback。
- `MEMORY.md` / `USER.md` 更适合个人助理，而不是产品正式状态。

可借鉴点：

- 小容量 curated memory 的纪律。
- 明确区分 always-in-context facts 和 on-demand recall。
- 写入前安全扫描。
- 当前 session snapshot 不随意改变，避免 prompt 漂移。

### 3.7 SQLite session store 和 session_search

核心代码：

- `/tmp/hermes-agent-reference/hermes_state.py`
- `/tmp/hermes-agent-reference/tools/session_search_tool.py`
- `/tmp/hermes-agent-reference/gateway/session.py`

Hermes 使用 `~/.hermes/state.db` 保存：

- `sessions`：session metadata、token counts、system prompt snapshot、parent_session_id。
- `messages`：完整 message history。
- `messages_fts`：FTS5 full-text search。
- `messages_fts_trigram`：CJK substring search。

关键机制：

- SQLite WAL 支持多入口并发读和单写。
- session split 使用 `parent_session_id` 建 lineage。
- context compression 会结束旧 session，创建 child session，保留可搜索历史。
- `session_search` 先 FTS 命中 message，再按 session 聚合，最后用辅助模型生成 focused summary。
- 当前 session lineage 会从搜索结果排除，避免重复召回当前上下文。

可借鉴点：

- 本项目已有 `ConversationThread`、`ConversationMessage`、`AgentRun`、`ContextPack`
  persistence，更适合成为主线。
- 可在开发诊断 inspector 中增加基于 thread/message/run 的只读搜索和 summary。
- CJK trigram / LIKE fallback 对中文销售场景有参考价值。

不建议照搬：

- 用 Hermes `state.db` 替换项目 backend persistence。
- 把 session transcript 搜索结果直接写入 formal lead results。
- 让 Runtime 任意搜索历史并自动改写正式业务对象。

### 3.8 Skills progressive disclosure

核心代码：

- `/tmp/hermes-agent-reference/tools/skills_tool.py`
- `/tmp/hermes-agent-reference/agent/prompt_builder.py`
- `/tmp/hermes-agent-reference/tools/skill_manager_tool.py`
- `/tmp/hermes-agent-reference/website/docs/user-guide/features/skills.md`

Hermes 的 skills 是 on-demand procedural memory：

```text
Level 0: skills_list()          -> name / description / category
Level 1: skill_view(name)       -> SKILL.md full content
Level 2: skill_view(name,path)  -> specific reference / template / script
```

system prompt 只注入 skill index。模型判断相关后再加载完整 skill。Skills 可以声明：

- platform compatibility。
- fallback / required toolset。
- required environment variables。
- config settings。
- references / templates / scripts / assets。

可借鉴点：

- 未来销售方法论、行业研究流程、线索评分 rubric 可以做成按需加载的 knowledge modules。
- ContextPack 中只放命中的 module summary / reference id，不一次性注入全部知识。
- `skill_view(name, file_path)` 类似的按需读取，可减少 prompt bloat。

不建议照搬：

- 让 Product Sales Agent 自主创建/修改项目产品知识库。
- 把 skills 当业务对象版本库。
- 在未设计权限、审核和来源边界前允许 runtime 自动安装外部 skills。

## 4. Hermes 与 OpenClaw 对比

| 维度 | Hermes Agent | OpenClaw |
| --- | --- | --- |
| 核心定位 | 长期个人 / 多平台 / 自我学习 Agent | 更偏 workspace/session/runtime context pipeline |
| 上下文抽象 | `ContextEngine` 聚焦压缩、缓存、可替换压缩器 | `ContextEngine` 生命周期更完整：bootstrap / ingest / assemble / compact / afterTurn / maintain |
| 记忆模型 | `MEMORY.md` / `USER.md` / skills / session_search 是核心卖点 | 更强调 session transcript、project context、compaction、tool result guard |
| 压缩策略 | 双层压缩：gateway hygiene + agent compressor | runtime 内 compact / successor transcript / pruning 更突出 |
| prompt 管理 | frozen system prompt，强依赖 prompt caching | 每轮 context assembly 和 bootstrap budget 更突出 |
| 长期召回 | SQLite + FTS5 + auxiliary summary | session transcript / context engine maintenance |
| 技能/知识 | skills progressive disclosure，支持自我创建 | workspace/project context 与工具运行时更突出 |
| 本项目适配度 | 适合作为补充经验 | 更适合作为主参考框架 |

结论：

- OpenClaw 更适合做本项目 `ContextPack` / runtime 输入编译主参考。
- Hermes 更适合补充借鉴 frozen prompt、压缩摘要质量、session_search 诊断、skills 渐进加载。
- 两者都不能替代 Sales Workspace Kernel 的 formal truth layer。

## 5. 本项目借鉴方案

推荐把前一份 OpenClaw 方案作为主线，形成：

```text
Structured SalesWorkspace truth
+ current ConversationThread
+ active DraftReview state
+ latest AgentRun trace
+ optional knowledge module refs
        ↓
SalesWorkspaceContextPipeline
        ↓
SalesAgentTurnContextPack
        ↓
Runtime / Product Sales Agent execution layer
        ↓
assistant_message_draft + WorkspacePatchDraft?
```

在这个主线下，吸收 Hermes 的四个补充设计。

### 5.1 Frozen runtime instruction + variable ContextPack

推荐原则：

- Product Sales Agent 的稳定行为规则放在 runtime instruction version 中。
- 产品事实、线程历史、active review、recent messages、open questions 放在
  `SalesAgentTurnContextPack`。
- 同一 thread 中尽量减少 system instruction 漂移。
- `ContextPack` 记录 `compiler_version`、`instruction_version`、`source_versions`。

这可以兼顾 Hermes 的 prompt caching 经验和本项目的结构化事实边界。

### 5.2 Deterministic context fitting

本项目应优先做 deterministic fitting，而不是先上 LLM summary。

必须保留：

- kernel boundary。
- `workspace_id`、`workspace_version`、`thread_id`、`agent_run_id`。
- current user message。
- current `ProductProfileRevision` core summary。
- current `LeadDirectionVersion` core summary。
- active/latest `WorkspacePatchDraftReview` summary。
- `source_versions` 和 `input_refs`。

可裁剪：

- older assistant wording。
- old rejected draft payload detail。
- verbose runtime metadata。
- old failed AgentRun detail。
- future raw search result body。
- long candidate reason text。

应记录：

```json
{
  "context_budget_report": {
    "budget_chars": 60000,
    "raw_chars": 84200,
    "injected_chars": 59800,
    "truncated_chars": 24400,
    "strategy": "deterministic_recent_messages_v1",
    "sections": [
      {
        "name": "recent_messages",
        "raw_chars": 32000,
        "injected_chars": 12000,
        "truncated": true
      }
    ],
    "omitted_sources": [
      {
        "type": "conversation_message",
        "reason": "older_than_recent_window"
      }
    ]
  }
}
```

### 5.3 Derived summary artifact

当 deterministic fitting 不够时，再设计 `ConversationThreadSummary` 或
`ContextCompactionSummary`。

它必须是 derived runtime artifact，而不是业务主真相。建议字段：

- `thread_id`
- `workspace_id`
- `source_message_start_id`
- `source_message_end_id`
- `first_kept_message_id`
- `source_workspace_version`
- `summary_prompt_version`
- `summary_text`
- `raw_chars`
- `summary_chars`
- `runtime_only: true`
- `created_by_agent_run_id`

Hermes 的 summary template 可以借鉴：

- active task。
- completed actions。
- active state。
- pending asks。
- relevant files / objects。
- remaining work。
- critical context。

但对本项目应替换为销售工作区语义：

- current user ask。
- product profile deltas。
- lead direction deltas。
- pending clarification questions。
- active draft review status。
- workspace object refs。
- evidence/source refs。

### 5.4 On-demand sales knowledge modules

借鉴 Hermes skills progressive disclosure，但不引入完整 skills 自管理平台。

推荐未来设计为只读、版本化、项目内可审核的知识模块：

```text
SalesKnowledgeModule
  id
  version
  title
  trigger_summary
  content_ref
  allowed_runtime_use
  source
```

ContextPack 中只注入：

- module id。
- short trigger summary。
- selected excerpts。
- module version。

禁止：

- Runtime 自动安装外部 skills。
- Runtime 自动改写知识模块。
- 知识模块直接写 formal workspace objects。

## 6. 推荐实施顺序

### Phase A：ContextPack budget diagnostics

优先级最高。目标：

- 给 `SalesAgentTurnContextPack` 增加 context budget report。
- recent messages 采用 deterministic fitting。
- 把 report 写入 `AgentRun.runtime_metadata` 或 context pack metadata。
- dev diagnostics inspector 可以只读显示。

不涉及：

- DB schema migration，除非现有 JSON metadata 放不下。
- LangGraph。
- MCP。
- LLM compaction summary。
- V2.2 search/contact。

### Phase B：Stable prompt / instruction versioning

目标：

- 明确 Product Sales Agent runtime instruction version。
- 区分 stable instruction 与 variable ContextPack。
- trace 中记录 instruction version。
- 为未来 provider caching 和 eval 回放做准备。

### Phase C：Runtime-only summary artifact design

目标：

- 设计 `ConversationThreadSummary` / `ContextCompactionSummary`。
- 明确它不是 formal workspace truth。
- 记录 source range、workspace version、summary prompt version。
- 只在长对话和 context pressure 明确出现后实现。

### Phase D：On-demand sales knowledge module

目标：

- 把销售方法论、行业分析流程、线索筛选 rubric 做成只读 knowledge module。
- ContextPack 按需引用。
- 先文档和 fixture，后实现。

## 7. 不建议照搬的部分

不建议把以下 Hermes 能力直接搬进本项目：

1. 完整 gateway / multi-platform session system。
2. `MEMORY.md` / `USER.md` 作为 Product Sales Agent 记忆。
3. Agent-managed skills 作为销售知识库。
4. 完整 plugin context engine registry。
5. SQLite `state.db` 替换 backend persistence。
6. prompt caching 先于 ContextPack 结构化治理。
7. external memory provider 或 MCP provider 作为内部主架构。
8. session resume / suspend / restart_pending 作为 V2.1 runtime lifecycle。

## 8. 决策建议

综合 OpenClaw 与 Hermes，当前最值得本项目借鉴的顺序是：

1. OpenClaw 的 ContextPack / context pipeline 主框架。
2. OpenClaw 的 context budget diagnostics。
3. Hermes 的 deterministic head/middle/tail compression guard 细节。
4. Hermes 的 latest user message anchoring。
5. Hermes 的 frozen prompt snapshot 思路。
6. Hermes 的 session_search 作为 dev diagnostics / future recall 参考。
7. Hermes 的 skills progressive disclosure 作为 future knowledge module 参考。

下一步若要实现，建议新开 dedicated task：

```text
V2.1 Sales Workspace ContextPack Budget Diagnostics
```

第一阶段只做：

- context budget report。
- deterministic recent-message fitting。
- AgentRun / ContextPack metadata 诊断沉淀。
- dev inspector 只读展示。

不做：

- LLM summary。
- LangGraph。
- MCP。
- V2.2 search/contact。
- Hermes memory/skills/gateway。

## 9. Boundary Check

- backend/runtime boundary 未改变：Runtime 仍是执行层。
- formal writeback 仍经 Draft Review 和 Sales Workspace Kernel。
- `ContextPack` 仍是 Runtime 输入快照，不是 formal workspace truth。
- Hermes 的 `MEMORY.md`、`USER.md`、skills、session_search 不应成为本项目业务主存。
- 错误和诊断应记录在 `AgentRun.error`、`runtime_metadata` 或 context pack metadata，
  不新增未授权 run state。
- 不假设 `waiting_for_user`、durable checkpoint、resume、queue-worker lifecycle 已存在。
- 不引入 V2.2 evidence/search/contact formal object。
