# 阶段性交接：V2 planning baseline update

更新时间：2026-04-25

## 1. 本次改了什么

- 将仓库入口状态从 V1 当前主线调整为 V1 已冻结、当前进入 V2 planning baseline。
- 更新 `AGENTS.md`，补充 V2 搜索、来源证据、联系方式和后端主真相 guardrails。
- 更新 `docs/README.md`、`docs/product/overview.md` 和 `docs/product/roadmap.md`，使阅读顺序和路线图指向 V2 planning baseline。
- 新增 `ADR-005-v2-lead-research-scope-and-search-boundary.md`，冻结 V2 轻量线索研究的最小搜索和联系方式边界。
- 新增 `task_v2_planning_baseline_update.md`，记录本次是规划基线任务，不是实现任务。
- 更新 `_active.md`，记录 V2 planning baseline update 已完成，同时保留无 current task / 无 implementation queue 状态。

---

## 2. 为什么这么定

- V1 已通过 closeout 收口为 demo-ready release candidate / learning milestone，不应继续作为当前开发主线。
- V2 已有 PRD 草案和 data model 草案，但旧入口仍显示“下一阶段尚未定义”，容易造成 agent 执行歧义。
- V2 涉及主动联网、具体公司候选和联系方式，需要先通过 ADR 明确范围和非目标，再进入任何实现。

---

## 3. 本次验证了什么

1. `git diff --check`

本次为 docs-only 变更，未运行 backend / Android 测试。

---

## 4. 已知限制

- V2 仍不是 MVP。
- 未冻结搜索 provider。
- 未冻结数据库 schema、migration 或 API contract。
- 未冻结个人联系方式保留、删除和脱敏策略。
- 未创建 V2 implementation task queue。

---

## 5. 推荐下一步

1. 已由 `handoff_2026_04_25_v2_conversational_sales_agent_definition_update.md` 接续。
2. 后续以 ADR-006 的 V2.1 对话式专属销售 agent 路线为准。
3. 不再直接进入后端-only lead research spike。
