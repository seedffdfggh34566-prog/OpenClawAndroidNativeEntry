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
- 本文档维护当前事实状态、capability matrix 和 gap backlog。
- `_active.md` 只维护当前执行授权、current package / task、auto-continue 和 stop conditions。
- task / handoff 只能作为证据来源，不能自行定义产品阶段完成。

---

## 2. 当前阶段摘要

| Area | Status | Notes |
|---|---|---|
| V1 demo baseline | `frozen` | V1 已冻结为 demo-ready release candidate / learning milestone。 |
| V2.1 workspace/kernel engineering baseline | `done` | Sales Workspace Kernel、Draft Review ID flow、Postgres / Alembic persistence chain、Draft Review audit persistence 已验证。 |
| V2.1 validated prototype path | `done` | deterministic chat-first path、backend 5-sample acceptance、Android demo path 和 explicit-flag Tencent TokenHub LLM runtime prototype 已验证。 |
| V2.1 product milestone | `partial / in_progress` | prototype path 已验证，但不等于 V2.1 产品阶段完整完成。后续实现仍需由规划层开放 package。 |
| V2.2 evidence / search / ContactPoint | `blocked` | 仅允许后续 docs-level planning；implementation 仍需单独 PRD / ADR / task gate。 |
| MVP / production SaaS | `not_started` | 不在当前默认实现范围。 |

当前解释：

> **V2.1 validated prototype path completed；V2.1 product milestone remains open under planning control.**

---

## 3. Capability Matrix

| Capability | Status | Evidence | Gap / Next Need |
|---|---|---|---|
| Sales Workspace Kernel | `done` | Kernel docs、API contract、WorkspacePatch、ContextPack、Markdown projection、tests。 | 无当前阻断项。 |
| Draft Review gate | `done` | Draft Review contract、routes prototype、Android Draft Review ID flow、audit persistence。 | 后续可补 history / detail UX。 |
| Postgres persistence baseline | `done` | Alembic migration、repository layer、API Postgres store、Draft Review persistence。 | production-grade backup / migration hardening 不在当前范围。 |
| Chat-first backend flow | `done` | ConversationMessage -> AgentRun -> WorkspacePatchDraft -> DraftReview -> WorkspaceCommit backend path。 | 更复杂多轮协商与质量 polish 仍可继续。 |
| Backend 5-sample conversational acceptance | `done` | V2.1 conversation acceptance e2e task 与 tests。 | 样例库可扩展，但不阻断 validated prototype path。 |
| Android workspace demo path | `partial` | Android chat-first UI、Draft Review apply、device acceptance evidence。 | 自动创建 workspace / onboarding、完整 history / trace view 仍未完成。 |
| Tencent TokenHub LLM runtime prototype | `partial` | explicit dev flag、fake-client tests、live smoke / eval。 | prompt quality、稳定性、真实环境验收仍需 follow-up；不等于 production-ready Product Sales Agent。 |
| Postgres environment verification | `done` | 2026-04-28 P5 verification：compose Postgres、Alembic head、Sales Workspace / Draft Review / chat-first trace Postgres tests `30 passed`。 | production-grade backup / migration hardening 不在当前范围。 |
| V2.2 evidence/search/contact | `blocked` | ADR-005 与 V2 PRD 将其放入后续阶段。 | 先做 docs-level planning，不直接实现 provider / ContactPoint。 |

---

## 4. 当前执行授权

当前执行状态以 `docs/delivery/tasks/_active.md` 为准。

当前口径：

- Current delivery package：暂无自动开放。
- Current task：暂无自动排定。
- Auto-continue：`no`。
- V2.2 implementation：blocked。

---

## 5. Next Candidate Packages

以下是规划候选，不代表已开放执行：

最近完成的状态修正：

- **V2.1 completion semantics correction**：已通过本文档和 `docs/product/research/v2_1_completion_semantics_correction_2026_04_28.md` 落地。

后续候选：

1. **V2.1 demo reproducibility hardening**
   - 目标：补强 demo seed、runbook、失败排查和最小 smoke。
2. **V2.1 Android onboarding / workspace creation**
   - 目标：减少 Android 依赖预置 backend workspace 的演示限制。
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
