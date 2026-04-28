# Handoff: V2.1 Milestone Acceptance Review

更新时间：2026-04-28

## 1. 本次改了什么

- 开放 `V2.1 Milestone Acceptance And Gap Closure` package。
- 创建并完成 `task_v2_1_milestone_acceptance_review.md`。
- 新增 `docs/product/research/v2_1_milestone_acceptance_review_2026_04_28.md`。
- 更新 `docs/product/project_status.md`，初始将 V2.1 product milestone 调整为 `partial / gap_closure_open`。
- 更新 `_active.md`，初始开放 V2.1 gap closure task。
- 后续产品决策已将该 gap closure task 调整为 lightweight start button product entry polish。
- 创建 `task_v2_1_chat_first_workspace_start_gap_closure.md`。

---

## 2. 为什么这么定

用户明确要求判断并推进 V2.1 是否实现。按新的 evidence model，本次不能只凭历史 task / handoff closeout 宣称 V2.1 done。

Review 结论：

- 大部分 V2.1 backend / Android / runtime / persistence 能力已有实现和验证。
- PRD 的“一句话启动 SalesWorkspace”在本 review 当时被判为 gap；后续产品决策已将其弱化为轻量按钮“开始销售工作区”。
- 因此 V2.1 product milestone 仍不能判为 done。

---

## 3. 本次验证了什么

使用了本轮已运行验证：

1. `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py backend/tests/test_sales_workspace_chat_first_llm_runtime.py backend/tests/test_sales_workspace_draft_reviews_api.py -q`
   - 结果：`35 passed, 1 skipped in 20.28s`
   - skip 原因：`OPENCLAW_BACKEND_POSTGRES_VERIFY_URL` 未设置。
2. `git diff --check`
   - 结果：通过。

使用了已记录验证：

- P5 Postgres verification：`30 passed in 11.97s`。
- P2/P3 Android `:app:assembleDebug`。
- V2.1 device acceptance evidence。
- Tencent TokenHub live smoke：`6 passed in 97.19s`。

---

## 4. 已知限制

- 本次没有修改 backend / Android / runtime code。
- 本次没有重跑 Android build、Postgres live verification 或 live LLM smoke。
- 后续产品决策已将该 task 从 implementation gap closure 调整为 product entry polish task；当前状态以 `docs/product/project_status.md` 为准。
- V2.2 search / ContactPoint / CRM、formal LangGraph、production SaaS 仍 blocked。

---

## 5. 推荐下一步

执行：

- `docs/delivery/tasks/task_v2_1_chat_first_workspace_start_gap_closure.md`

完成后更新 milestone review addendum 和 `docs/product/project_status.md`，再判断 V2.1 product milestone 是否可升级。
