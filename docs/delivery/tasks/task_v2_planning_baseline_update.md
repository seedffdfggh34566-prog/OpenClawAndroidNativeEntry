# Task：V2 planning baseline update

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V2 planning baseline update
- 建议路径：`docs/delivery/tasks/task_v2_planning_baseline_update.md`
- 当前状态：`done`
- 优先级：P0

---

## 1.1 队列衔接

- 当前 task 是否允许执行 agent 自主推进：`yes`
- 建议上游入口：`docs/delivery/tasks/_active.md`
- 建议下游任务：暂无自动排定
- 停止条件：
  - 需要进入后端 / Android / 数据库实现
  - 需要冻结 V2 MVP 目标
  - 需要选择搜索 provider
  - 需要决定个人联系方式保留或删除策略

---

## 2. 任务目标

将仓库从“V1 已冻结、下一阶段未定义”的状态，调整为“V1 已冻结，当前进入 V2 planning baseline 阶段”。

本任务只对齐文档入口、运行规则、ADR 和任务状态，不实现后端、Android、数据库 migration、搜索 provider 或 API。

---

## 3. 当前背景

V1 已通过 closeout 收口为 demo-ready release candidate / learning milestone，不进入 MVP。

用户已选择 V2 初始方向：

- 轻量线索研究
- 允许主动联网 / 搜索
- 目标用户为中小企业老板 / 销售负责人
- 不做 Web 前端
- 产品学习未来应转向 AI 引导式对话
- 数据层需要比 V1 更复杂，并可借鉴仓库 docs 骨架

仓库此前已新增 V2 PRD 草案和 V2 data model 草案，但根入口规则、总览、roadmap、ADR 和 `_active.md` 仍带有 V1 已收口后“下一阶段未定义”的状态。

---

## 4. 范围

本任务 In Scope：

- 更新 `AGENTS.md`
- 更新 `docs/README.md`
- 更新 `docs/product/overview.md`
- 更新 `docs/product/roadmap.md`
- 新增 ADR-005
- 新增本 task
- 更新 `_active.md`
- 新增 handoff

本任务 Out of Scope：

- 后端代码
- Android 代码
- 数据库 schema / migration
- 搜索 provider 接入
- API contract 实现
- V2 MVP 定义
- 成本治理实现
- 多用户 / 权限 / 正式部署实现

---

## 5. 涉及文件

高概率涉及：

- `AGENTS.md`
- `docs/README.md`
- `docs/product/overview.md`
- `docs/product/roadmap.md`
- `docs/adr/ADR-005-v2-lead-research-scope-and-search-boundary.md`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/handoffs/handoff_2026_04_25_v2_planning_baseline_update.md`

参考文件：

- `docs/product/prd/ai_sales_assistant_v2_prd.md`
- `docs/architecture/data/v2-lead-research-data-model.md`
- `docs/product/research/v1_closeout_2026_04_25.md`

---

## 6. 产出要求

至少应产出：

1. V2 planning baseline 入口规则。
2. V2 搜索 / 来源证据 / 联系方式边界 ADR。
3. `_active.md` 与 handoff 对齐。
4. 明确当前仍不自动创建 V2 implementation queue。

---

## 7. 验收标准

满足以下条件可认为完成：

1. `AGENTS.md`、`docs/README.md`、`docs/product/overview.md` 不再把 V1 描述为当前开发主线。
2. `_active.md` 不再说“下一阶段尚未定义”而忽略 V2 草案。
3. `_active.md` 仍不自动排 V2 实现任务。
4. ADR-005 与 V2 PRD / data model 不冲突。
5. `git diff --check` 通过。

---

## 8. 推荐执行顺序

建议执行顺序：

1. 更新入口规则和导航。
2. 更新产品总览和 roadmap。
3. 新增 ADR-005。
4. 新增 task 与 handoff。
5. 更新 `_active.md`。
6. 运行 docs-only 校验。

---

## 9. 风险与注意事项

- 不要把 V2 草案升级为 schema baseline。
- 不要创建 V2 implementation queue。
- 不要承诺 V2 是 MVP。
- 不要选择搜索 provider。
- 不要扩大到 CRM、自动触达或联系人抓取。

---

## 10. 下一步衔接

本任务完成后，推荐继续：

1. 冻结 V2 PRD v0.2。
2. 冻结 V2 data model v0.2。
3. 设计 V2 backend contract 草案。

---

## 11. 实际产出

- 已更新仓库入口规则和文档导航。
- 已更新产品总览和 roadmap。
- 已新增 ADR-005。
- 已新增 V2 planning baseline task。
- 已更新 `_active.md`，保留“无 current task / 不自动排实现任务”状态。
- 已新增 handoff。

---

## 12. 本次定稿边界

本次只冻结 V2 planning baseline 的文档入口和最小边界，不冻结数据库 schema、API contract、搜索 provider、MVP 范围或 implementation queue。

---

## 13. 已做验证

- `git diff --check`
