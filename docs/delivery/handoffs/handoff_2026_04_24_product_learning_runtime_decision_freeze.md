# 阶段性交接：product learning runtime decision freeze

更新时间：2026-04-24

## 1. 本次改了什么

- 新增 `ADR-003`，正式冻结 product learning runtime 的对象边界、阶段判定与接口承载
- 新增 docs-only task：`task_v1_product_learning_runtime_decision_freeze.md`
- 将 `task_v1_product_learning_runtime_followup.md` 改写为纯实现任务
- 同步 PRD、system-context、mobile IA、API contract、domain model 与 runtime architecture

---

## 2. 为什么这么定

- 当前最大风险不再是“缺 task”，而是 product learning runtime 仍有几项高风险语义未冻结
- 若先写实现，backend、runtime 与 Android 很容易在 run object、阶段字段和第一版实现形态上各自收口
- 因此先做 docs-only freeze，能把下一步实现 task 收成无开放决策的最小闭环

---

## 3. 本次冻结的结论

- V1 继续只保留 4 个正式业务对象
- product learning 执行继续复用 `AgentRun`
- `ready_for_confirmation` 由 backend services 判定
- backend 显式暴露 `learning_stage`
- 第一版 product learning runtime 采用 single-turn enrich，并复用现有 8 个 public API

---

## 4. 本次验证了什么

1. `git diff --check` 通过
2. 全仓搜索已去掉本轮要消除的未定表述
3. 主文档、reference、task、handoff 与导航已对齐到同一套基线

---

## 5. 推荐下一步

1. 进入 `task_v1_product_learning_runtime_followup.md`
2. 先在 backend 侧补 `product_learning` run type、`learning_stage` 与 `current_run` 非空语义
3. 再补 Android 最小接线，不扩大成完整聊天客户端
