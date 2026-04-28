# Delivery Package: V2.1 Implementation Rebaseline And Gap Closure

更新时间：2026-04-28

> Current interpretation note：本文仍作为 V2.1 implementation rebaseline evidence 保留，但不得被解读为完整 V2.1 product milestone 已关闭。当前阶段状态以 `docs/product/project_status.md` 和 `docs/product/research/v2_1_completion_semantics_correction_2026_04_28.md` 为准。

## 1. Package 定位

- Package 名称：V2.1 Implementation Rebaseline And Gap Closure
- 建议路径：`docs/delivery/packages/package_v2_1_implementation_rebaseline.md`
- 当前状态：`done`
- 优先级：P0
- Package 类型：`delivery`
- 是否允许执行 agent 自主推进：`yes`
- 是否允许 package 内部 steps 连续执行：`yes`
- 完成后是否允许自动进入 V2.2：`no`

---

## 2. 为什么现在创建这个 package

用户明确要求“现在先实现 V2.1”。当前仓库文档已经将 V2.1 标记为：

- V2.1 workspace/kernel engineering baseline validated
- V2.1 conversational backend acceptance validated
- V2.1 conversational product experience prototype path validated
- V2.1 Tencent TokenHub LLM runtime prototype available behind explicit dev flag

因此，本 package 不重新定义 V2.1 阶段状态，也不能把 V2.1 扩展成 V2.2 / MVP / production SaaS。正确执行口径是：

> 按 V2.1 PRD acceptance 和现有 closeout 重新复核实现状态，修复阻断 V2.1 demo / prototype 复现的严重缺口，并留下新的 package closeout 证据。

这是一轮实现复核与缺口收敛 package，不是产品方向重定义 package。

---

## 3. V2.1 当前实现分析

### 3.1 已完成基线

当前已完成的 V2.1 实现基线包括：

1. Sales Workspace Kernel backend-only v0。
2. Sales Workspace API contract / examples。
3. Draft Review contract、routes prototype 和 Android Draft Review ID flow。
4. Postgres / Alembic persistence baseline、repository layer、API Postgres store。
5. Draft Review audit persistence。
6. Chat-first Runtime design、contract examples 和 trace persistence。
7. Backend chat-first prototype：`ConversationMessage -> AgentRun -> ContextPack -> WorkspacePatchDraft -> DraftReview -> WorkspacePatch -> WorkspaceCommit`。
8. Android chat-first workspace UI prototype。
9. Clarifying questions、workspace explanation、product profile extraction、lead direction adjustment。
10. Backend-level 5-sample conversational acceptance。
11. Android polish、sample smoke 和真机端到端验收。
12. Tencent TokenHub LLM runtime prototype behind explicit dev flag。

### 3.2 V2.1 prototype acceptance 已关闭

按现有 PRD Acceptance Final Review，V2.1 prototype acceptance 可宣称完成。该结论不等于：

- formal LangGraph completed
- V2.2 evidence / search / ContactPoint completed
- production-ready SaaS
- CRM / automatic outreach completed
- Android full trace browser completed

### 3.3 仍值得复核的实现风险

本 package 重点复核以下风险：

1. 当前分支上的文档、task queue 与代码是否仍一致。
2. Backend V2.1 chat-first API、Draft Review、Postgres store 和 LLM runtime fake-client tests 是否仍通过。
3. Demo runbook 是否仍能指导复现 V2.1 path。
4. Android workspace 入口是否仍能构建，或至少在未触碰 Android 时保持既有验收口径。
5. 是否存在阻断 V2.1 demo / prototype 复现的严重 bug。

---

## 4. Package Scope

In Scope：

- 复核 V2.1 PRD acceptance 与当前实现的一致性。
- 运行 V2.1 相关 backend tests 和必要 docs checks。
- 如果发现 V2.1 demo / prototype 阻断 bug，做最小修复。
- 更新当前 task、package handoff 和必要 delivery 入口。
- 必要时补充 V2.1 implementation rebaseline 说明。

Out of Scope：

- V2.2 evidence/search/contact implementation。
- 正式 LangGraph graph。
- 新 search provider。
- ContactPoint、CRM、自动触达、批量抓取、批量导出。
- 新增或扩展 API surface，除非是修复已存在 V2.1 endpoint 的阻断 bug。
- 新增 Alembic migration、SQLAlchemy model 或 persistence baseline 变更。
- Android 大规模聊天 UI 改造。
- production hardening、云部署、多用户、租户、权限。
- 将 Tencent TokenHub LLM runtime prototype 包装为 production-ready agent。

---

## 5. Package 内任务

当前开放任务：

1. `docs/delivery/tasks/task_v2_1_implementation_rebaseline_and_gap_closure.md`

Package 内不预先开放更多 implementation task。若当前任务发现需要拆分的新高风险 work，应停止并新建明确 follow-up，而不是在本 package 内静默扩展。

---

## 6. 允许编辑范围

允许编辑：

- `docs/delivery/tasks/*`
- `docs/delivery/handoffs/*`
- `docs/delivery/README.md`
- `README.md`
- V2.1 相关 backend source / tests，仅限修复已验证的 V2.1 阻断 bug
- V2.1 相关 Android workspace source，仅限修复已验证的 V2.1 阻断 bug

禁止编辑：

- `docs/product/*` 的产品含义，除非先明确提出方向层变更
- `docs/adr/*` 的决策含义，除非先明确提出 ADR 变更
- search / contact / CRM 相关实现
- backend secrets、`.env` 内容、本地 DB 手工修改
- unrelated refactor 或格式化 churn

---

## 7. 推荐执行顺序

1. 读取当前 task、V2 PRD、roadmap、V2.1 PRD acceptance final review、LLM eval 和相关 handoff。
2. 对照 V2.1 success criteria，确认当前实现与 closeout 是否一致。
3. 运行最小 backend 验证：
   - `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py backend/tests/test_sales_workspace_chat_first_llm_runtime.py backend/tests/test_sales_workspace_draft_reviews_api.py -q`
4. 若涉及 persistence / Postgres store，追加：
   - `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_api_postgres_store.py backend/tests/test_sales_workspace_draft_reviews_postgres_store.py -q`
5. 若触碰 Android，先读取 `app/AGENTS.md`，再运行最小 Android 验证。
6. 修复发现的 V2.1 阻断 bug。
7. 更新 task outcome 和 package handoff。
8. 不自动进入 V2.2。

---

## 8. Stop Conditions

命中以下任一条件时停止并交回规划层：

- 需要改变 V2 产品方向或 V2.1 成功标准。
- 需要新增 V2.2 evidence/search/contact 能力。
- 需要正式 LangGraph graph 或 durable checkpoint / resume lifecycle。
- 需要新增 schema migration、public API surface 或 persistence baseline 变更。
- 需要新增外部 provider、密钥、部署假设或环境依赖。
- 需要 Android 大规模 UI 重写。
- 需要把 prototype 口径升级为 MVP / production-ready 口径。

---

## 9. Package 验收标准

满足以下条件可关闭 package：

1. V2.1 PRD success criteria 被重新核对，没有发现新的 `missing` 阻断项。
2. 最小 backend 验证已运行并记录结果；若未运行，必须说明原因。
3. 若有代码修复，修复范围只覆盖 V2.1 阻断 bug，并有对应验证。
4. `_active.md`、当前 task 和 handoff 状态一致。
5. V2.2 implementation 仍保持 blocked。

---

## 10. 推荐 package closeout

Package 完成后新增或更新 handoff：

- `docs/delivery/handoffs/handoff_2026_04_28_v2_1_implementation_rebaseline.md`

handoff 必须说明：

- 实际验证了什么。
- 是否发现并修复 bug。
- 哪些能力仍不是 V2.1。
- 下一步是否进入 V2.2 docs-level planning 或 V2.1 prompt quality follow-up。

---

## 11. Package Closeout

状态：`done`

本次 rebaseline 未发现新的 V2.1 阻断 bug，未修改 backend / Android 代码。

验证结果：

1. `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py backend/tests/test_sales_workspace_chat_first_llm_runtime.py backend/tests/test_sales_workspace_draft_reviews_api.py -q`
   - 结果：`30 passed, 1 skipped in 16.86s`
   - skip 原因：`OPENCLAW_BACKEND_POSTGRES_VERIFY_URL` 未设置，Postgres chat-first verification 按测试门禁跳过。
2. `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_api_postgres_store.py backend/tests/test_sales_workspace_draft_reviews_postgres_store.py -q`
   - 结果：`6 skipped in 0.29s`
   - skip 原因：`OPENCLAW_BACKEND_POSTGRES_VERIFY_URL` 未设置，Postgres Sales Workspace / Draft Review verification 按测试门禁跳过。

本 package 不开放 V2.2 implementation。后续由规划层决定是否开放 V2.2 docs-level planning 或 V2.1 LLM prompt quality follow-up。
