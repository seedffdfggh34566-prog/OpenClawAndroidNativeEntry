# V2.1 Completion Semantics Correction

日期：2026-04-28

## 1. 目的

本文修正 V2.1 相关文档中的完成口径，避免将 prototype path acceptance 误读为完整 V2.1 product milestone completion。

当前权威状态入口为：

- `docs/product/project_status.md`

---

## 2. 修正后的当前口径

当前可声明：

> **V2.1 validated prototype path completed；V2.1 product milestone remains open under planning control.**

含义：

- V2.1 workspace/kernel engineering baseline 已验证。
- V2.1 deterministic chat-first backend / Android demo path 已验证。
- V2.1 explicit-flag Tencent TokenHub LLM runtime prototype 已验证。
- 这些结论不等于完整 V2.1 product milestone 已完成。
- 后续 V2.1 implementation continuation 可由规划层通过 delivery package / task 继续开放。

---

## 3. 对历史文档的解释

以下历史文件继续作为 evidence 保留：

- `docs/product/research/v2_1_prd_acceptance_final_review_2026_04_27.md`
- `docs/delivery/tasks/task_v2_1_product_experience_final_closeout.md`
- `docs/delivery/tasks/package_v2_1_implementation_rebaseline.md`
- `docs/delivery/handoffs/handoff_2026_04_28_v2_1_implementation_rebaseline.md`

这些文件中的 `completed`、`closeout` 或 `final` 结论应理解为：

- 对当时定义的 prototype path / acceptance gate 的收口；
- 对已有 demo / backend / device evidence 的记录；
- 不应被解释为完整 V2.1 product milestone 已关闭。

---

## 4. 仍然开放的 V2.1 实现空间

后续可由规划层单独开放的 V2.1 continuation package 包括但不限于：

- demo reproducibility hardening
- Android onboarding / workspace creation
- LLM prompt quality follow-up
- trace / history visibility
- Postgres verification hardening
- richer conversational polishing within V2.1 boundary

这些 package 不应自动进入 V2.2 search / evidence / ContactPoint implementation。

---

## 5. 仍然 blocked 的内容

除非后续 PRD / ADR / task gate 明确开放，以下内容仍 blocked：

- V2.2 evidence / search / ContactPoint implementation
- search provider integration
- formal LangGraph graph
- CRM pipeline
- automatic outreach
- production SaaS hardening
- multi-user / tenant / permission model

---

## 6. 后续规则

普通 task / handoff 只能声明 task 或 package 本身完成，或说明其为 milestone 提供 evidence。

产品阶段、版本、product experience 或 milestone 是否完成，必须由明确的 milestone acceptance review 或 `docs/product/project_status.md` 维护，不得由普通 task / handoff 推导。
