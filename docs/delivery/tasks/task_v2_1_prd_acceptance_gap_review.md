# Task: V2.1 PRD Acceptance Gap Review

状态：planned

更新时间：2026-04-27

## Objective

将 V2.1 PRD 成功标准逐项映射到当前实现、测试、真机证据和缺口，修正此前仅依据 task closeout / deterministic demo flow 宣称 V2.1 product experience completed 的口径。

本任务不写代码，不启动 V2.2，只为后续 V2.1 conversational product experience completion task 提供准确缺口清单。

## Scope

- 读取 `docs/product/prd/ai_sales_assistant_v2_prd.md`、`docs/product/roadmap.md`、`docs/architecture/runtime/v2-1-chat-first-runtime-design.md` 和当前实现 / 测试证据。
- 输出 `PRD Acceptance Traceability` 表。
- 每条 PRD 成功标准必须标注为 `done`、`partial`、`missing` 或 `out of scope`。
- 明确哪些能力属于 V2.1 conversational product experience，哪些能力属于 V2.2 evidence / search / ContactPoint。
- 给出后续 V2.1 completion task queue 建议，但不自动开放 implementation task。

## Initial Acceptance Items

| PRD success criterion | Current expected status before review |
|---|---|
| 用户能通过对话完成第一版产品理解 | partial |
| Product Sales Agent 能主动提出 3 到 5 个关键追问 | missing |
| 用户能通过对话调整获客方向 | partial |
| 调整沉淀为 `LeadDirectionVersion` 或等价结构化版本 | partial |
| Product Sales Agent 能解释推荐方向原因 | missing |
| `ConversationMessage`、`AgentRun`、`WorkspacePatch` 和正式对象变更可追溯 | partial |
| Postgres 重启后可恢复当前 workspace、messages、AgentRun、Draft Review 和 formal objects | partial |
| Android 真机端到端证据覆盖产品理解和获客方向 | partial |
| 真实 LLM / 正式 LangGraph / search / ContactPoint / CRM | out of scope |

## Out Of Scope

- 不改 backend code。
- 不改 Android code。
- 不新增 API route。
- 不写 migration。
- 不接真实 LLM、LangGraph、search provider、ContactPoint 或 CRM。
- 不宣称 V2.1 completed。
- 不启动 V2.2 implementation。

## Required Output

本任务完成时应新增或更新一份 review 文档，至少包含：

- `PRD Acceptance Traceability` 表。
- 当前实现证据引用。
- 当前测试 / 真机证据引用。
- 缺口清单。
- 后续 V2.1 completion task 建议。
- 明确结论：是否允许宣称完整 V2.1 completed。

## Validation

```bash
rg "PRD Acceptance Traceability|done|partial|missing|out of scope" docs/delivery docs/product docs/architecture
rg "V2.1 conversational product experience remains incomplete|task_v2_1_prd_acceptance_gap_review.md" README.md docs
git diff --check
git status --short
```

不运行 backend / Android build；本任务是 docs-only acceptance review。
