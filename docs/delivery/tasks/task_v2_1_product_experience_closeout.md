# Task: V2.1 Product Experience Closeout

状态：done

更新时间：2026-04-27

## Objective

在 chat-first backend prototype、Android UI prototype 和 demo runbook 验证完成后，正式收口 V2.1 product experience，并决定是否可以进入 V2.2 evidence/search 规划。

## Required Precondition

- `task_v2_1_chat_first_runtime_contract_examples.md`
- `task_v2_1_chat_first_runtime_trace_persistence_schema_design.md`
- `task_v2_1_chat_first_runtime_trace_persistence_migration_v0.md`
- `task_v2_1_chat_first_runtime_backend_prototype.md`
- `task_v2_1_android_chat_first_workspace_ui_prototype.md`
- `task_v2_1_product_experience_demo_runbook.md`

## Scope

- 更新 README、docs/README、delivery README、roadmap、overview。
- 明确 V2.1 product experience 是否达到 closeout。
- 记录实际验证命令和限制。
- 决定后续是否只开放 V2.2 docs-only planning task。

## Out Of Scope

- 不直接启动 V2.2 search implementation。
- 不接真实 LLM。
- 不接 search provider。
- 不实现 ContactPoint / CRM。
- 不做 production hardening。

## Acceptance Criteria

- 文档可以准确说明 V2.1 engineering baseline 与 product experience 均已完成。
- Chat-first 产品理解和获客方向迭代有可重复 demo。
- V2.2 evidence/search/contact 仍需独立 task 明确开放。

## Outcome

- V2.1 product experience prototype closeout 已完成。
- 文档入口已更新为：V2.1 engineering baseline completed；V2.1 product experience prototype completed。
- `_active.md` 保持暂无自动排定任务。
- V2.2 evidence/search/contact 可进入 docs-level planning，但 implementation 仍 blocked。

## Validation

```bash
rg "V2.1 product experience prototype completed|task_v2_1_product_experience_closeout.md|V2.2.*blocked" README.md docs
git diff --check
```

Additional smoke evidence:

```text
health: {"status":"ok"}
workspace_id: ws_v21_smoke
product_draft_review: draft_review_sales_turn_product_profile_update_v1
direction_draft_review: draft_review_sales_turn_lead_direction_update_v2
final_workspace_version: 2
```
