# Task: V2.1 Completion Closeout

状态：done

更新时间：2026-04-27

## Objective

将 V2.1 从功能分支完成推进到 `main` 上的正式 baseline closeout，并明确下一阶段不自动开放。

## Completion Definition

本任务中的 V2.1 completion 指：

- Sales Workspace Kernel 已可通过 API 使用。
- Android 已能走 workspace / Draft Review ID demo flow。
- Workspace 与 Draft Review 已具备显式 Postgres-backed persistence path。
- Draft Review lifecycle 具备 append-only audit event baseline。
- V2.1 验证命令已在 main 上重新跑通。
- 文档入口明确 V2.1 已完成，且 V2.2 / Runtime / Android / search 任务未自动开放。

这不是完整 V2 产品上线，也不是 V2.2。

## Scope

- 合并 PR #24。
- 同步根 README、docs 入口、delivery 入口、backend README 和 roadmap 状态。
- 补 V2.1 closeout handoff。
- 创建 V2.2 planned task placeholders。
- 运行 backend / Postgres / Android build-level 验证。

## Out Of Scope

- 不接真实 LangGraph / LLM。
- 不接 search provider。
- 不接 CRM / contact。
- 不扩 Android UI。
- 不新增 backend route。
- 不做 production hardening。
- 不实现多用户 / 权限。

## Result

已完成：

- PR #24 已 merge 到 `main`。
- V2.1 Postgres persistence chain 已进入 `main`。
- V2.1 closeout 文档已补齐。
- `_active.md` 保持暂无自动排定。
- 下一阶段 task 仅作为 planned placeholder 存在。

## Actual Validation

本任务使用 backend-local-verify、android-build-verify、task-handoff-sync 对应验证层级收口。实际命令记录见 handoff。

## Recommended Next Step

下一阶段建议先执行 docs-only：

- `task_v2_2_runtime_langgraph_design.md`

目标是先冻结真实 Runtime / LangGraph 如何产出 `WorkspacePatchDraft`，再进入任何 LLM、search 或 Android 扩展实现。
