# Task：V1 产品学习交互基线冻结

更新时间：2026-04-24

## 1. 任务定位

- 任务名称：V1 产品学习交互基线冻结
- 建议路径：`docs/delivery/tasks/task_v1_product_learning_interaction_baseline.md`
- 当前状态：`done`
- 优先级：P0

本任务用于在进入真实 product learning runtime 实现前，先冻结 V1 的产品学习交互形态、阶段状态、最低完整度门槛与确认边界，避免后续 Android / backend / runtime 各自推进时语义漂移。

---

## 1.1 队列衔接

- 当前 task 是否允许执行 agent 自主推进：`yes`
- 建议上游入口：`docs/delivery/tasks/_active.md`
- 建议下游任务：
  1. `docs/delivery/tasks/task_v1_real_runtime_integration_phase1.md`
- 停止条件：
  - 需要改变 V1 scope 或主路径
  - 需要新增未在现有 domain model 中定义的核心对象
  - 产品文档、系统分层文档与现有 Android 控制流出现冲突
  - 需要把产品学习页扩大成完整聊天客户端重写

---

## 2. 任务目标

明确并冻结 V1 产品学习的交互基线，至少回答以下问题：

1. 产品学习页是纯聊天、纯表单，还是混合形态
2. 当前页面至少包含哪些信息区块
3. 系统何时认为信息达到最低完整度
4. 何时允许进入 `ProductProfile` 确认页
5. 确认前后分别由哪个页面承担什么职责

---

## 3. 当前背景

当前仓库已经完成：

- `ProductProfile` 创建
- `ProductProfile` 确认
- `lead_analysis` 触发与结果读取
- `report_generation` 触发与结果读取

但产品学习阶段仍未进入真实 runtime，也还没有冻结正式交互形态。当前实现更接近“对象控制流闭环”，而不是“AI 产品学习体验闭环”。

PRD 已明确 V1 必须覆盖：

- 产品学习对话
- 产品画像确认
- 获客分析生成
- 结构化分析报告输出

因此，在开始真实 product learning runtime 实现前，必须先把产品学习交互基线冻结为正式任务边界。

---

## 4. 范围

本任务 In Scope：

- 冻结 V1 产品学习页的交互形态为“聊天优先 + 结构化摘要辅助 + 阶段门控确认”
- 明确产品学习页的最小页面构成
- 明确最低完整度门槛与缺失字段规则
- 明确页面阶段状态与主路径跳转条件
- 补齐任务文档、decision 记录与 `_active.md` 队列

本任务 Out of Scope：

- 真实 product learning runtime 编码实现
- 新增独立 product learning public endpoint
- Android 页面重写与真机联调
- CRM、联系人抓取、自动触达、完整工作台
- 完整多轮记忆系统或长期 profile memory 机制

---

## 5. 涉及文件

高概率涉及：

- `docs/product/prd/ai_sales_assistant_v1_prd.md`
- `docs/architecture/system-context.md`
- `docs/architecture/clients/mobile-information-architecture.md`
- `docs/adr/ADR-002-v1-runtime-and-product-learning-baseline.md`

参考文件：

- `docs/reference/schemas/v1-domain-model-baseline.md`
- `docs/delivery/tasks/task_v1_product_profile_confirmation_flow.md`
- `docs/delivery/tasks/task_v1_information_architecture.md`

---

## 6. 产出要求

至少应产出：

1. 一份冻结产品学习交互基线的 task 文档
2. 一份记录 runtime 与产品学习基线选择的 decision 文档
3. `_active.md` 中明确的当前 task / next queued task / stop conditions
4. 对最低完整度门槛、阶段状态、确认边界的文字化定义

---

## 7. 验收标准

满足以下条件可认为完成：

1. 文档明确 V1 产品学习采用混合式，而不是纯聊天或纯表单
2. 文档明确产品学习页至少包含：
   - AI 问答区
   - 当前产品理解摘要
   - 缺失字段提示
   - 当前阶段状态
3. 文档明确最低完整度门槛：
   - `name`
   - `one_line_description`
   - `target_customers` 至少 1 条
   - `typical_use_cases` 至少 1 条
   - `pain_points_solved` 至少 1 条
   - `core_advantages` 至少 1 条
4. 文档明确产品学习阶段状态至少包括：
   - `collecting`
   - `ready_for_confirmation`
   - `confirmed`
5. 文档明确只有达到最低完整度或用户显式要求先生成草稿时，才进入确认页
6. `git diff --check` 通过

---

## 8. 推荐执行顺序

建议执行顺序：

1. 回读 PRD 与 system-context，确认 V1 主路径与对象边界
2. 冻结产品学习交互形态与最低完整度门槛
3. 记录 decision，避免后续 runtime 与 Android 各自解释
4. 把后续真实 runtime 接入 task 接到当前队列下游

---

## 9. 风险与注意事项

- 不要把“产品学习交互基线冻结”扩大成完整 UX 设计稿
- 不要在未定义新 API 前先假设 mobile 端会变成完整 chat client
- `ProductProfile` 仍是正式输入对象，聊天线程不能取代正式对象
- 若需要新增核心对象，应先回到 product / ADR 层，不要在 task 内静默扩 scope

---

## 10. 下一步衔接

本任务完成后，推荐继续：

1. `docs/delivery/tasks/task_v1_real_runtime_integration_phase1.md`

---

## 11. 实际产出

- `docs/product/prd/ai_sales_assistant_v1_prd.md`：回写产品学习交互基线、最低完整度门槛与阶段状态
- `docs/architecture/system-context.md`：回写 runtime 默认方向与 product learning 阶段状态
- `docs/architecture/clients/mobile-information-architecture.md`：补产品学习页与首页状态叙事
- `docs/product/overview.md`：收紧“仍未冻结”的旧表述
- `docs/delivery/handoffs/handoff_2026_04_24_product_learning_interaction_baseline.md`：补交接记录

---

## 12. 本次定稿边界

- 只冻结产品学习交互与门控，不新增 API、不改 backend write path、不做 Android UI 重写
- 运行对象、阶段判定与接口承载的冻结，明确留给后续 runtime boundary 决策任务

---

## 13. 已做验证

1. `git diff --check` 通过

---

## 14. 实际结果说明

- V1 产品学习当前正式采用“聊天优先 + 结构化摘要辅助 + 阶段门控确认”
- 最低完整度门槛、missing 字段与 `collecting / ready_for_confirmation / confirmed` 已写回主文档
