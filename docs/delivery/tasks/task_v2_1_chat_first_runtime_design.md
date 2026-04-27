# Task: V2.1 Chat-first Runtime Design

状态：done

更新时间：2026-04-27

## Objective

补齐 V2.1 product experience 设计，明确 chat-first 输入如何驱动 Product Sales Agent / Runtime 生成可审阅的 `WorkspacePatchDraft`，再由 Draft Review 与 Sales Workspace Kernel 进入正式 workspace。

本任务只做 design，不实现代码。

## Background

V2.1 engineering baseline 已完成：

- Sales Workspace Kernel。
- FastAPI prototype。
- Android Workspace / Draft Review ID demo。
- Postgres / Alembic persistence baseline。
- Sales Workspace Postgres store。
- Draft Review audit persistence。

但 V2.1 product experience 尚未完成。当前缺口是：

- 用户通过 chat-first 入口表达产品信息、获客方向和修改意见时，系统如何形成 `ConversationMessage`。
- Product Sales Agent / Runtime 如何读取 `ContextPack` 和当前 workspace state。
- Runtime 如何生成覆盖 `ProductProfileRevision` 与 `LeadDirectionVersion` 的 `WorkspacePatchDraft`。
- Draft Review、WorkspaceCommit 与 AgentRun 如何串起可追踪闭环。

## Scope

- 设计 chat-first input -> `ConversationMessage` -> `AgentRun` 的最小流。
- 设计 Runtime 输入：workspace snapshot、ContextPack、active draft review context、user instruction。
- 设计 Runtime 输出：`WorkspacePatchDraft`，覆盖产品理解和获客方向迭代。
- 设计最小 ProductProfileRevision chat-first flow。
- 设计最小 LeadDirectionVersion chat-first flow。
- 明确 `ConversationMessage`、`AgentRun`、`DraftReview`、`WorkspaceCommit` 的 trace relationship。
- 明确失败、版本冲突、用户拒绝、重新生成 draft 的状态语义。
- 明确哪些内容属于 V2.1 product experience，哪些必须留到 V2.2 evidence/search。

## Out Of Scope

- 不实现 LangGraph graph。
- 不接真实 LLM。
- 不改 Android。
- 不新增 backend route。
- 不改 SQLAlchemy model 或 Alembic migration。
- 不接 search provider。
- 不实现 ContactPoint / CRM。
- 不实现自动触达。
- 不实现 Android review history view。

## Expected Deliverables

- 一份 V2.1 chat-first runtime design 文档，建议放在 `docs/architecture/runtime/` 或 `docs/architecture/workspace/`。
- 如需要，补充 reference contract，说明 chat-first Runtime 与 `WorkspacePatchDraft` 的最小 schema 边界。
- 更新 `_active.md`、delivery README 和 handoff。
- 明确后续是否开放 V2.1 runtime implementation task。

## Result

已完成：

- `docs/architecture/runtime/v2-1-chat-first-runtime-design.md`
- `docs/reference/api/sales-workspace-chat-first-runtime-contract.md`
- `docs/delivery/handoffs/handoff_2026_04_27_v2_1_chat_first_runtime_design.md`

后续不直接开放 implementation。先创建并规划 docs / examples-only task：

- `task_v2_1_chat_first_runtime_contract_examples.md`

Backend prototype 仍 blocked：

- `task_v2_1_chat_first_runtime_backend_prototype.md`

## Acceptance Criteria

- 文档明确 V2.1 engineering baseline completed 与 V2.1 product experience not completed yet 的区别。
- 文档定义 chat-first 产品理解和获客方向迭代的最小端到端流。
- 文档明确 Runtime 只产出 `WorkspacePatchDraft`，backend / Sales Workspace Kernel 仍是正式写回裁决层。
- 文档明确 `ConversationMessage`、`AgentRun`、`DraftReview`、`WorkspaceCommit` 的追踪关系。
- 文档明确 V2.2 evidence/search/contact 仍 blocked。
- 不产生代码变更。

## Validation

- `rg "ConversationMessage|AgentRun|WorkspacePatchDraft|ProductProfileRevision|LeadDirectionVersion" docs/architecture docs/reference docs/delivery`
- `rg "V2.1 product experience|V2.2.*blocked|不接真实 LLM|不实现 LangGraph" docs`
- `git diff --check`

## Stop Conditions

- 需要改变 V2 PRD 的产品方向。
- 需要开放真实 LLM、LangGraph implementation、search、ContactPoint 或 Android 新 UI。
- 需要新增 backend route、DB migration 或 API contract implementation。
