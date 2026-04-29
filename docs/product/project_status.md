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
| V2.1 validated prototype path | `partial / android_entry_regression` | backend、persistence、runtime prototype evidence 仍可作为局部证据；但 2026-04-28 人工验收反馈指出 Android app 未看到聊天入口，因此 Android product path 不能继续按 done 使用。 |
| V2.1 product milestone | `partial / android_chat_surface_missing` | 入口和 workspace 已可见，但 Android 页面仍是工程调试式 workspace 面板；缺少接近真实产品的聊天界面、上下文对话流和可验收的代表性 chat-first 路径。 |
| V2.2 evidence / search / ContactPoint | `blocked` | 仅允许后续 docs-level planning；implementation 仍需单独 PRD / ADR / task gate。 |
| MVP / production SaaS | `not_started` | 不在当前默认实现范围。 |

当前解释：

> **V2.1 remains not implemented at product-experience level because the Android app does not yet present a usable chat-first Sales Workspace surface with visible conversation context.**

---

## 3. Capability Matrix

| Capability | Status | Evidence | Gap / Next Need |
|---|---|---|---|
| Sales Workspace Kernel | `done` | Kernel docs、API contract、WorkspacePatch、ContextPack、Markdown projection、tests。 | 无当前阻断项。 |
| Draft Review gate | `done` | Draft Review contract、routes prototype、Android Draft Review ID flow、audit persistence。 | 后续可补 history / detail UX。 |
| Postgres persistence baseline | `done` | Alembic migration、repository layer、API Postgres store、Draft Review persistence。 | production-grade backup / migration hardening 不在当前范围。 |
| Chat-first backend flow | `done` | ConversationMessage -> AgentRun -> WorkspacePatchDraft -> DraftReview -> WorkspaceCommit backend path。 | 更复杂多轮协商与质量 polish 仍可继续。 |
| Backend 5-sample conversational acceptance | `done` | V2.1 conversation acceptance e2e task 与 tests。 | 样例库可扩展，但不阻断 validated prototype path。 |
| Android workspace demo path | `partial / chat surface missing` | 当前真机反馈确认“销售工作区入口”和 Sales Workspace 页面已存在；但页面仍过于工程化，缺少像 OpenClaw 前端那样的对话上下文、明显聊天输入和 assistant / Draft Review 结果流。 | 必须把 Workspace 页面产品化为 chat-first surface：可读 conversation history、明显 composer、assistant response / draft review result card、弱化 workspace id/version/raw debug 信息，并用真机验证。 |
| Tencent TokenHub LLM runtime prototype | `done` | explicit dev flag、fake-client tests、live smoke / eval。 | 仅代表 explicit dev flag prototype，不等于 production-ready Product Sales Agent、formal LangGraph 或 V2.2 search/contact。 |
| Postgres environment verification | `done` | 2026-04-28 P5 verification：compose Postgres、Alembic head、Sales Workspace / Draft Review / chat-first trace Postgres tests `30 passed`。 | production-grade backup / migration hardening 不在当前范围。 |
| V2.2 evidence/search/contact | `blocked` | ADR-005 与 V2 PRD 将其放入后续阶段。 | 先做 docs-level planning，不直接实现 provider / ContactPoint。 |

---

## 4. 当前执行授权

当前执行状态以 `docs/delivery/tasks/_active.md` 为准。

当前口径：

- Current delivery package：`docs/delivery/packages/package_v2_1_android_chat_entry_recovery.md`。
- Current task：`docs/delivery/tasks/task_v2_1_android_chat_entry_recovery_and_demo_path.md`。
- Auto-continue：`yes`，仅限 V2.1 Android chat surface productization package 内部。
- V2.2 implementation：blocked。

---

## 5. Next Candidate Packages

以下是规划候选，不代表已开放执行：

最近完成的状态修正：

- **V2.1 completion semantics correction**：已通过本文档和 `docs/product/research/v2_1_completion_semantics_correction_2026_04_28.md` 落地。
- **V2.1 milestone acceptance review**：原 one-sentence workspace start blocker 已按产品决策调整为 lightweight start button polish，不再要求首句自然语言自动创建 workspace。

状态纠偏：

- **V2.1 lightweight workspace start entry polish** 历史 task / handoff 只能证明代码和 build/install 尝试；后续人工反馈确认入口和 workspace 已出现，但页面仍不像真实聊天产品。
- V2.1 product milestone 仍为 `partial / android_chat_surface_missing`；不得升级为 implemented。

当前开放 package：

1. **V2.1 Android chat surface productization**
   - 目标：把当前 Sales Workspace 页面从工程调试面板收敛为可用的 chat-first 产品界面：能看到对话上下文、明显输入框、assistant / Draft Review 结果，并能跑代表性 V2.1 demo path。
   - 范围：Android Workspace screen 信息架构、conversation history 展示、composer、loading/error/result 状态、existing backend API integration、真机可见 evidence。
   - 禁止：新增 V2.2 search / ContactPoint / CRM、formal LangGraph、auth/tenant、多 workspace 产品化、新 backend public API 或 migration，除非停止并回到人工决策。

后续候选：

1. **V2.1 milestone acceptance review addendum / status decision**
   - 目标：仅在 Android chat entry recovery 完成并有人工可见证据后，再重新判断 V2.1 product milestone。
2. **V2.2 evidence/search/contact docs-level planning**
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
