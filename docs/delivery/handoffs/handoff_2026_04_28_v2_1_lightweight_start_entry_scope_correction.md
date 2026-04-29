# Handoff: V2.1 Lightweight Start Entry Scope Correction

更新时间：2026-04-28

## 1. 本次改了什么

- 修正 V2.1 首次进入产品口径：
  - 不再要求用户首句自然语言自动创建 `SalesWorkspace` 并触发同一轮 agent turn。
  - 改为用户无需理解 workspace，可点击轻量按钮“开始销售工作区”，进入聊天后再用自然语言表达业务。
- 更新 `docs/product/prd/ai_sales_assistant_v2_prd.md`。
- 更新 `docs/product/project_status.md`，将 V2.1 product milestone 状态调整为 `partial / product_entry_polish_open`。
- 更新 `docs/product/research/v2_1_milestone_acceptance_review_2026_04_28.md`，将该项从 implementation blocker 改为 product entry polish。
- 更新当前 package / task / `_active.md` / docs navigation，使当前 task scope 变为 lightweight start button entry polish。

---

## 2. 为什么这么定

用户明确确认产品偏好：

> 用户无需理解 workspace，但可以有一个轻量开始按钮。首屏按钮叫“开始销售工作区”，点完后进入聊天。

因此原先的“一句话启动 SalesWorkspace”不应继续作为 V2.1 implementation blocker。SalesWorkspace 仍是后台结构化容器，但不作为用户首次操作时必须理解的产品概念。

---

## 3. 本次验证了什么

本次为 docs-only scope correction，未改 backend / Android / runtime code。

已验证：

- `rg "一句自然语言启动|one-sentence workspace start|gap_closure_open|开始销售工作区" docs`
  - 结果：通过；当前 source-of-truth 已使用“开始销售工作区”轻量入口口径，旧 `gap_closure_open` 仅保留在历史 review / handoff 的初始状态说明中。
- `git diff --check`
  - 结果：通过。

---

## 4. 已知限制

- 本次不实现 Android 按钮文案或 UI 改动。
- 当前 task 文件名仍为 `task_v2_1_chat_first_workspace_start_gap_closure.md`，但 task 标题和 scope 已重定义为 lightweight entry polish。
- V2.1 product milestone 仍不直接宣称 done；entry polish 完成后需要 review addendum。
- V2.2 search / ContactPoint / CRM、formal LangGraph、production SaaS 仍 blocked。

---

## 5. 推荐下一步

执行当前 task 的新 scope：

- Android 首屏或 workspace onboarding 按钮文案改为“开始销售工作区”。
- 点击后创建或进入默认 workspace，并展示 chat-first 输入。
- 不实现首句自然语言自动创建并提交 agent turn。
