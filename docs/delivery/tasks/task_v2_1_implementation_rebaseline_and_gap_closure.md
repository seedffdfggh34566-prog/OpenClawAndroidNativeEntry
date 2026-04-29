# Task: V2.1 Implementation Rebaseline And Gap Closure

更新时间：2026-04-28

## 1. 任务定位

- 任务名称：V2.1 Implementation Rebaseline And Gap Closure
- 建议路径：`docs/delivery/tasks/task_v2_1_implementation_rebaseline_and_gap_closure.md`
- 当前状态：`done`
- 优先级：P0
- 任务类型：`delivery`
- 是否属于 delivery package：`yes`
- 所属 package：`V2.1 Implementation Rebaseline And Gap Closure`

---

## 1.1 队列衔接

- 当前 task 是否允许执行 agent 自主推进：`yes`
- 当前 task 内部 steps 是否允许连续执行：`yes`
- 完成后是否允许自动进入下游任务：`no`
- 建议上游入口：`docs/delivery/tasks/_active.md`
- 建议下游任务：
  1. `docs/delivery/handoffs/handoff_2026_04_28_v2_1_implementation_rebaseline.md`
  2. 由规划层决定是否开放 V2.2 docs-level planning 或 V2.1 LLM prompt quality follow-up。
- 自动继续条件：
  - 工作保持在 V2.1 PRD acceptance / prototype reproduction 范围内。
  - 不新增 search、ContactPoint、CRM、formal LangGraph 或 production hardening。
  - 只修复已验证的 V2.1 阻断 bug。
- 停止条件：
  - 需要改变 V2.1 成功标准或产品方向。
  - 需要新增 API surface、migration、provider、密钥或部署假设。
  - 需要进入 V2.2 evidence/search/contact implementation。
  - 需要 Android 大规模 UI 重写。

---

## 1.2 自动化契约

- 本任务允许编辑：
  - `docs/delivery/tasks/*`
  - `docs/delivery/handoffs/*`
  - `docs/delivery/README.md`
  - `README.md`
  - V2.1 相关 backend source / tests，仅限阻断 bug 修复
  - V2.1 相关 Android workspace source，仅限阻断 bug 修复
- 本任务禁止编辑：
  - V2.2 search / ContactPoint / CRM implementation
  - formal LangGraph graph
  - schema migration 或 persistence baseline 变更
  - production hardening、云部署、多用户、租户、权限
  - unrelated refactor
- 可在任务内连续完成的 steps：
  1. 复核 V2.1 acceptance 与当前实现。
  2. 运行最小 backend 验证。
  3. 修复 V2.1 阻断 bug。
  4. 更新 task outcome 和 package handoff。
- 不应拆成独立 task 的小步骤：
  - 修正文档入口中的 package 状态。
  - 修复测试发现的小型 V2.1 demo reproduction bug。
  - 补充 handoff 验证记录。
- 必须拆出独立 task 或停止确认的情况：
  - 任何 V2.2 implementation。
  - formal LangGraph / search provider / ContactPoint。
  - 新 migration、public API contract 变更或生产化部署假设。

---

## 2. 任务目标

本任务用于执行 V2.1 implementation rebaseline：

1. 将“V2.1 已完成 prototype acceptance”的文档结论和当前代码现实重新核对。
2. 用最小验证确认 V2.1 chat-first、Draft Review、structured writeback 和 LLM runtime fake-client path 仍可工作。
3. 修复阻断 V2.1 demo / prototype 复现的严重问题。
4. 输出新的 package handoff，说明 V2.1 当前实现状态和剩余边界。

---

## 3. 当前背景

当前 repo 已完成 V2.1 closeout，但用户明确要求“现在先实现 V2.1”。因此本任务不重新定义 V2.1，而是把实现动作限定为：

- 重新验收 V2.1 implementation。
- 修复复现阻断项。
- 保持 V2.2 implementation blocked。

这符合当前 PRD / roadmap / ADR 口径：

- V2.1 是 Sales Workspace Kernel + chat-first product experience prototype。
- V2.2 才进入 evidence/search/contact。
- Backend / Sales Workspace Kernel 是 formal truth layer。
- Runtime / Product Sales Agent execution layer 只能产出 draft payload。

---

## 4. 范围

本任务 In Scope：

- V2.1 PRD acceptance re-check。
- Backend V2.1 chat-first tests。
- Draft Review route tests。
- LLM runtime fake-client tests。
- 必要的 Postgres store tests。
- V2.1 demo runbook / delivery handoff consistency check。
- V2.1 阻断 bug 的最小修复。

本任务 Out of Scope：

- V2.2 search / evidence / ContactPoint。
- formal LangGraph implementation。
- production-ready LLM quality guarantee。
- Android automatic workspace onboarding，除非现有 V2.1 demo 完全无法复现且修复非常小。
- Android trace history browser。
- DB hardening、backup、migration redesign。
- cloud deployment / user / tenant / permission。

---

## 5. 涉及文件

高概率涉及：

- `backend/tests/test_sales_workspace_chat_first_api.py`
- `backend/tests/test_sales_workspace_chat_first_llm_runtime.py`
- `backend/tests/test_sales_workspace_draft_reviews_api.py`
- `backend/tests/test_sales_workspace_api_postgres_store.py`
- `backend/tests/test_sales_workspace_draft_reviews_postgres_store.py`
- `backend/api/sales_workspace.py`
- `backend/sales_workspace/*`
- `backend/runtime/sales_workspace_chat_turn_llm.py`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/workspace/SalesWorkspaceScreen.kt`
- `docs/delivery/tasks/task_v2_1_implementation_rebaseline_and_gap_closure.md`
- `docs/delivery/handoffs/handoff_2026_04_28_v2_1_implementation_rebaseline.md`

参考文件：

- `docs/product/prd/ai_sales_assistant_v2_prd.md`
- `docs/product/roadmap.md`
- `docs/product/research/v2_1_prd_acceptance_final_review_2026_04_27.md`
- `docs/product/research/v2_1_llm_sales_agent_eval_2026_04_28.md`
- `docs/architecture/runtime/v2-1-llm-runtime-boundary.md`
- `docs/reference/api/sales-workspace-chat-first-runtime-contract.md`
- `docs/reference/api/sales-workspace-chat-first-llm-runtime-contract.md`
- `docs/how-to/operate/v2-1-product-experience-demo-runbook.md`
- `docs/how-to/operate/v2-1-llm-runtime-dev-runbook.md`

---

## 6. 产出要求

至少应产出：

1. V2.1 implementation rebaseline 结论。
2. 最小验证记录。
3. 若存在 bug，修复说明和验证结果。
4. package handoff。
5. `_active.md` 中的下一步状态更新。

---

## 7. 验收标准

满足以下条件可认为完成：

1. 已复核 V2.1 PRD acceptance final review 中的 success criteria。
2. 已运行最小 backend 验证，或明确说明无法运行的环境原因。
3. 没有发现未处理的 V2.1 阻断 bug。
4. 所有修复都未越过 V2.1 边界。
5. handoff 已记录 changed files、validation、known limits 和 recommended next step。

---

## 8. 推荐执行顺序

建议执行顺序：

1. 读取 package 文件和本任务文件。
2. 读取 V2 PRD、roadmap、V2.1 final review、LLM eval、runtime boundary。
3. 运行 docs consistency check。
4. 运行 backend V2.1 targeted tests。
5. 若失败，定位并修复最小阻断 bug。
6. 若触碰 Android，读取 `app/AGENTS.md` 并运行 Android 最小验证。
7. 更新本任务实际产出。
8. 更新 package handoff。
9. 将 `_active.md` 调整为 package completed 或下一个由规划层开放的 task。

---

## 9. 风险与注意事项

- 不要把 V2.1 closeout 改写成 V2.2 implementation 授权。
- 不要把 LLM prototype 说成 production-ready Product Sales Agent。
- 不要读取或记录 backend secrets。
- 不要用本任务引入正式 LangGraph、search provider、ContactPoint 或 CRM。
- 不要新增 DB migration；若确实需要，停止并创建独立 task。

---

## 10. 下一步衔接

本任务完成后，推荐继续：

1. 若 V2.1 rebaseline 通过，关闭 package 并交回规划层。
2. 若发现 V2.1 prompt quality 问题但不阻断 demo，创建 V2.1 LLM prompt quality follow-up。
3. 若准备进入 V2.2，先创建 V2.2 evidence/search/contact docs-level planning task。

---

## 11. 实际产出

已完成 V2.1 implementation rebaseline：

1. 复核 V2.1 PRD Acceptance Final Review，确认当前 package 不改变 V2.1 成功标准。
2. 运行 V2.1 targeted backend tests。
3. 未发现新的 V2.1 阻断 bug。
4. 未修改 backend / Android 代码。
5. 新增 package closeout handoff：`docs/delivery/handoffs/handoff_2026_04_28_v2_1_implementation_rebaseline.md`。

---

## 12. 本次定稿边界

本次只关闭 V2.1 implementation rebaseline / gap closure。

仍不属于 V2.1：

- formal LangGraph
- V2.2 evidence / search / ContactPoint
- CRM / automatic outreach
- production-ready SaaS
- Android full trace history UI
- Android automatic workspace onboarding

---

## 13. 已做验证

1. `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py backend/tests/test_sales_workspace_chat_first_llm_runtime.py backend/tests/test_sales_workspace_draft_reviews_api.py -q`
   - 结果：`30 passed, 1 skipped in 16.86s`
   - skip：Postgres chat-first verification 需要 `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL`。
2. `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_api_postgres_store.py backend/tests/test_sales_workspace_draft_reviews_postgres_store.py -q`
   - 结果：`6 skipped in 0.29s`
   - skip：Postgres Sales Workspace / Draft Review verification 需要 `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL`。

---

## 14. 实际结果说明

V2.1 targeted backend path 仍可通过本地验证；Postgres 专项验证因缺少显式验证 URL 未运行。当前没有发现需要代码修复的 V2.1 demo / prototype 复现阻断项。
