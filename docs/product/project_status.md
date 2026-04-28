# Project Status

更新时间：2026-04-28

## 1. 文档定位

本文档是当前项目阶段状态的权威入口。

它用于回答：

- 项目当前处于哪个产品阶段
- 哪些能力已验证
- 哪些能力仍是 `partial / missing / blocked`
- 后续可由规划层开放哪些 delivery package

本文档不替代 PRD、roadmap、ADR 或 `_active.md`：

- PRD / roadmap / ADR 定义产品方向、阶段边界和成功标准。
- 本文档维护当前事实状态、capability matrix 和 gap backlog；多 Agent 工作流中默认由 Status / Planning Agent 负责评估和建议更新。
- `_active.md` 只维护当前执行授权、current package / task、auto-continue 和 stop conditions。
- task / handoff 只能作为证据来源，不能自行定义产品阶段完成。

---

## 2. 当前阶段摘要

| Area | Status | Notes |
|---|---|---|
| V1 demo baseline | `frozen` | V1 已冻结为 demo-ready release candidate / learning milestone。 |
| V2.1 workspace/kernel engineering baseline | `done` | Sales Workspace Kernel、Draft Review ID flow、Postgres / Alembic persistence chain、Draft Review audit persistence 已验证。 |
| V2.1 validated prototype path | `done` | deterministic chat-first path、backend 5-sample acceptance、Android demo path 和 explicit-flag Tencent TokenHub LLM runtime prototype 已验证。 |
| V2.1 product milestone | `partial / product_entry_polish_open` | milestone acceptance review 已完成；首次入口标准已调整为轻量“开始销售工作区”按钮，不再要求首句自然语言自动创建 workspace。当前开放 product entry polish task。 |
| V2.2 evidence / search / ContactPoint | `blocked` | 仅允许后续 docs-level planning；implementation 仍需单独 PRD / ADR / task gate。 |
| MVP / production SaaS | `not_started` | 不在当前默认实现范围。 |

当前解释：

> **V2.1 validated prototype path completed；V2.1 product milestone remains partial with lightweight product entry polish open.**

---

## 3. Capability Matrix

| Capability | Status | Evidence | Gap / Next Need |
|---|---|---|---|
| Sales Workspace Kernel | `done` | Kernel docs、API contract、WorkspacePatch、ContextPack、Markdown projection、tests。 | 无当前阻断项。 |
| Draft Review gate | `done` | Draft Review contract、routes prototype、Android Draft Review ID flow、audit persistence。 | 后续可补 history / detail UX。 |
| Postgres persistence baseline | `done` | Alembic migration、repository layer、API Postgres store、Draft Review persistence。 | production-grade backup / migration hardening 不在当前范围。 |
| Chat-first backend flow | `done` | ConversationMessage -> AgentRun -> WorkspacePatchDraft -> DraftReview -> WorkspaceCommit backend path。 | 更复杂多轮协商与质量 polish 仍可继续。 |
| Backend 5-sample conversational acceptance | `done` | V2.1 conversation acceptance e2e task 与 tests。 | 样例库可扩展，但不阻断 validated prototype path。 |
| Android workspace demo path | `partial` | Android chat-first UI、Draft Review apply、device acceptance evidence、default workspace creation、ConversationMessage history。 | 产品入口仍需 polish：按钮文案应产品化为“开始销售工作区”，点击后创建或进入默认 workspace 并展示聊天入口；完整 AgentRun / DraftReview / WorkspaceCommit trace browser 仍是 follow-up。 |
| Tencent TokenHub LLM runtime prototype | `done` | explicit dev flag、fake-client tests、live smoke / eval。 | 仅代表 explicit dev flag prototype，不等于 production-ready Product Sales Agent、formal LangGraph 或 V2.2 search/contact。 |
| Postgres environment verification | `done` | 2026-04-28 P5 verification：compose Postgres、Alembic head、Sales Workspace / Draft Review / chat-first trace Postgres tests `30 passed`。 | production-grade backup / migration hardening 不在当前范围。 |
| V2.2 evidence/search/contact | `blocked` | ADR-005 与 V2 PRD 将其放入后续阶段。 | 先做 docs-level planning，不直接实现 provider / ContactPoint。 |

---

## 4. 当前执行授权

当前执行状态以 `docs/delivery/tasks/_active.md` 为准。

当前口径：

- Current delivery package：`docs/delivery/packages/package_v2_1_milestone_acceptance_and_gap_closure.md`。
- Current task：`docs/delivery/tasks/task_v2_1_chat_first_workspace_start_gap_closure.md`。
- Auto-continue：`yes`，仅限当前 V2.1 product entry polish。
- V2.2 implementation：blocked。

---

## 5. Next Candidate Packages

以下是规划候选，不代表已开放执行：

最近完成的状态修正：

- **V2.1 completion semantics correction**：已通过本文档和 `docs/product/research/v2_1_completion_semantics_correction_2026_04_28.md` 落地。
- **V2.1 milestone acceptance review**：原 one-sentence workspace start blocker 已按产品决策调整为 lightweight start button polish，不再要求首句自然语言自动创建 workspace。

当前开放：

1. **V2.1 lightweight workspace start entry polish**
   - 目标：将首次入口产品化为“开始销售工作区”；点击后创建或进入默认 workspace，并展示 chat-first 输入。

后续候选：

1. **V2.1 milestone acceptance review addendum**
   - 目标：entry polish 后重新判断 V2.1 product milestone 是否仍为 `partial`。
2. **V2.1 demo reproducibility hardening**
   - 目标：补强 demo seed、runbook、失败排查和最小 smoke。
3. **V2.1 LLM prompt quality follow-up**
   - 目标：扩大 fake / live eval，改进 prompt quality 和可解释性。
4. **V2.1 trace / history visibility**
   - 目标：继续补 AgentRun、DraftReview、WorkspaceCommit trace 复看；ConversationMessage history 已在 Android 展示。
5. **V2.2 evidence/search/contact docs-level planning**
   - 目标：先定义 source evidence、CompanyCandidate、ContactPoint 边界和人工验证规则，不直接实现 provider。

---

## 6. 状态判断规则

后续 Dev Agent 做项目进度评估时，应按以下顺序读取：

1. PRD / roadmap / ADR
2. architecture baseline
3. 本文档
4. `_active.md`
5. task / handoff evidence

普通 task / handoff 只能说明任务完成、验证通过或提供 milestone evidence，不能自行声明产品阶段、版本或 product experience 完成。

Capability Matrix 更新必须使用 evidence class：

- **Acceptance source**：PRD、roadmap、ADR 或 architecture baseline，用于定义验收标准。
- **Implementation evidence**：backend、Android、runtime、migration、API、UI 或脚本代码，用于证明仓库实际实现。
- **Validation evidence**：pytest、Gradle、adb、smoke、eval、migration check 或记录过的命令结果，用于证明实现经过验证。
- **Delivery evidence**：task、package、handoff，只能作为索引和历史记录。

状态更新规则：

- `done`：必须至少有 acceptance source、implementation evidence 和 validation evidence。
- `partial`：可以有部分 implementation / validation evidence，但 gap 必须回到 PRD、roadmap、ADR 或 architecture baseline。
- `missing`：必须说明缺少的 acceptance item 或实现对象。
- `blocked`：必须引用阻断来源，例如 PRD、ADR、roadmap、`_active.md` 或当前 package stop condition。

如果只读取了 task / package / handoff，最多输出低置信度 recommendation，不能提升 capability 或 milestone status。

Milestone closeout 必须单独生成 `PRD Acceptance Traceability`，并逐项列出 acceptance source、code evidence、validation evidence、delivery evidence、gap 和 confidence。
