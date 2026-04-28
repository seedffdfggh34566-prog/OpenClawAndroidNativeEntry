# Delivery Package: V2.1 Implementation Continuation

更新时间：2026-04-28

## 1. Package 定位

- Package 名称：V2.1 Implementation Continuation
- 建议路径：`docs/delivery/packages/package_v2_1_implementation_continuation.md`
- 当前状态：`done`
- 优先级：P0
- Package 类型：`delivery`
- 是否允许执行 agent 自主推进：`yes`
- 是否允许 package 内部 tasks 连续执行：`yes`
- 完成后是否允许自动进入 V2.2：`no`

---

## 2. 目标

本 package 用于把已验证的 V2.1 prototype path 推进为更稳定、可复现、可验收的 V2.1 product milestone 候选。

本 package 不重新定义 V2.1 PRD，不把 prototype 升级为 production SaaS，也不开放 V2.2 evidence / search / ContactPoint implementation。

---

## 3. Package 内任务

固定顺序：

1. P0：收束当前 V2.1 状态修正文档为基线。（done，commit `69dd004`）
2. P1：`task_v2_1_demo_reproducibility_hardening.md`。（done）
3. P2：`task_v2_1_android_workspace_onboarding.md`。（done）
4. P3：`task_v2_1_trace_message_history_visibility.md`。（done）
5. P4：`task_v2_1_llm_prompt_quality_followup.md`。（done）
6. P5：`task_v2_1_postgres_verification_hardening.md`。（done）

每个任务必须单独 closeout、记录验证、创建 handoff，并保持原子提交。

---

## 4. 允许范围

允许编辑：

- V2.1 delivery task / handoff / runbook。
- Android Workspace 页面与 Sales Workspace backend client 的最小 onboarding / message history。
- V2.1 LLM runtime tests / eval docs。
- Postgres verification runbook / handoff。

禁止编辑：

- V2.2 search / evidence / ContactPoint implementation。
- formal LangGraph graph。
- CRM / 自动触达 / 批量联系人。
- production SaaS、多用户、租户、权限。
- 新增 backend API endpoint。
- 新增 Alembic migration 或 schema baseline 变更。

---

## 5. Stop Conditions

命中以下情况时停止并交回规划层：

- 需要新增 V2.2 search / ContactPoint / CRM 能力。
- 需要新增 backend public API endpoint 或 migration。
- Android onboarding 需要扩展成多 workspace / 账号系统。
- LLM runtime 需要升级为 production-ready Product Sales Agent。
- Postgres verification 暴露 destructive migration 或环境依赖变化。

---

## 6. Package 验收标准

满足以下条件可关闭 package：

1. P0-P5 均有 task closeout 和 handoff。
2. Android onboarding 和 message history 已通过最小 Android build 验证。
3. V2.1 backend targeted tests 通过。
4. LLM fake-client quality follow-up tests 通过。
5. Postgres targeted verification 已实际运行，或记录明确环境阻断。
6. `_active.md` 恢复为暂无自动开放 implementation task。
7. V2.2 implementation 仍 blocked。

---

## 7. Package Closeout

状态：`done`

实际完成：

1. P0 baseline commit：`69dd004 docs: establish v2.1 continuation baseline`。
2. P1 demo reproducibility hardening：`fe95400 docs: harden v2.1 demo reproducibility`。
3. P2 Android workspace onboarding：`1b1abaf feat: add v2.1 workspace onboarding`。
4. P3 message history visibility：`b89356e feat: show v2.1 workspace message history`。
5. P4 LLM runtime quality coverage：`94e0aa6 test: expand v2.1 llm runtime quality coverage`。
6. P5 Postgres verification hardening：completed in this closeout commit。

Validation summary：

- Android `:app:assembleDebug` passed for P2 and P3.
- LLM runtime fake-client tests：`10 passed`.
- Postgres targeted tests：`30 passed in 11.97s`.
- Final closeout still requires `git diff --check`.

本 package 不关闭 V2.1 product milestone；milestone closeout 需要单独 PRD Acceptance Traceability review。
