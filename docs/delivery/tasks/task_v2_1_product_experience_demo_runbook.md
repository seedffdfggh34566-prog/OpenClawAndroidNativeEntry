# Task: V2.1 Product Experience Demo Runbook

状态：done

更新时间：2026-04-27

## Objective

固化 V2.1 product experience 的可重复 demo 流程，证明 chat-first 产品理解和获客方向迭代可以经过 Draft Review 写入 Sales Workspace。

## Required Precondition

- `task_v2_1_chat_first_runtime_backend_prototype.md`
- `task_v2_1_android_chat_first_workspace_ui_prototype.md`

## Scope

- 新增或更新 how-to runbook。
- 记录 backend Postgres 启动、migration、seed、Android 启动、chat-first 输入、Draft Review、apply、workspace refresh 的完整步骤。
- 固定两条 demo script：
  - 产品理解输入 -> `ProductProfileRevision`
  - 获客方向输入 -> `LeadDirectionVersion`
- 记录 expected state transition 和 validation commands。

## Out Of Scope

- 不新增产品能力。
- 不接真实 LLM。
- 不接 search / ContactPoint / CRM。
- 不做 production deployment。

## Validation

- backend tests。
- Android build。
- runbook command smoke where environment allows。
- `git diff --check`。

## Recommended Next

- `task_v2_1_product_experience_closeout.md`

## Outcome

- 新增 `docs/how-to/operate/v2-1-product-experience-demo-runbook.md`。
- runbook 固定 Postgres backend、chat-first 产品理解、chat-first 获客方向、Draft Review accept/apply 和 Android UI demo steps。
- 本任务未新增产品能力、真实 LLM、search、ContactPoint、CRM 或 deployment。

## Validation

```bash
rg "v2-1-product-experience-demo-runbook.md|ProductProfileRevision|LeadDirectionVersion|ConversationMessage|AgentRun" docs/how-to docs/delivery
git diff --check
```
