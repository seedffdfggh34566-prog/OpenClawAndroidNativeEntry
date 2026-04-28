# 阶段性交接：V2.1 Implementation Rebaseline

更新时间：2026-04-28

> Current interpretation note：本文仍作为 V2.1 implementation rebaseline evidence 保留，但不得被解读为完整 V2.1 product milestone 已关闭。当前阶段状态以 `docs/product/project_status.md` 和 `docs/product/research/v2_1_completion_semantics_correction_2026_04_28.md` 为准。

## 1. 本次改了什么

- 执行 `package_v2_1_implementation_rebaseline.md`。
- 执行并关闭 `task_v2_1_implementation_rebaseline_and_gap_closure.md`。
- 更新 package / task 状态为 `done`。
- 更新 `_active.md`、delivery README 和 root README，恢复为暂无自动开放 implementation task。

---

## 2. 为什么这么定

- V2.1 已按 PRD Acceptance Final Review 验证 prototype acceptance，本次不重新定义 V2.1 阶段状态。
- 用户要求先执行当前 delivery package，因此本次只做 implementation rebaseline、最小验证和阻断 bug 检查。
- 验证未发现新的 V2.1 阻断 bug，因此不做 backend / Android 代码改动。

---

## 3. 本次验证了什么

1. `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py backend/tests/test_sales_workspace_chat_first_llm_runtime.py backend/tests/test_sales_workspace_draft_reviews_api.py -q`
   - 结果：`30 passed, 1 skipped in 16.86s`
   - skip 原因：`OPENCLAW_BACKEND_POSTGRES_VERIFY_URL` 未设置，Postgres chat-first verification 跳过。
2. `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_api_postgres_store.py backend/tests/test_sales_workspace_draft_reviews_postgres_store.py -q`
   - 结果：`6 skipped in 0.29s`
   - skip 原因：`OPENCLAW_BACKEND_POSTGRES_VERIFY_URL` 未设置，Postgres Sales Workspace / Draft Review verification 跳过。

---

## 4. 已知限制

- 本次没有运行 Android build 或真机 smoke，因为未触碰 Android 代码，且 package 目标是 backend-targeted rebaseline。
- Postgres 专项 tests 未实际连接 Postgres；它们按测试门禁跳过。
- Tencent TokenHub live smoke 未运行；本次覆盖的是 fake-client / local backend path，不读取或使用任何 LLM secret。
- V2.2 evidence/search/ContactPoint、formal LangGraph、CRM、自动触达、生产化部署仍 blocked。

---

## 5. 推荐下一步

1. 若需要更强环境验收，单独开放 Postgres verification task，并提供 `OPENCLAW_BACKEND_POSTGRES_VERIFY_URL`。
2. 若继续提升 V2.1，优先开放 V2.1 LLM prompt quality follow-up。
3. 若进入 V2.2，先开放 evidence/search/contact docs-level planning，不直接实现 search/contact。
