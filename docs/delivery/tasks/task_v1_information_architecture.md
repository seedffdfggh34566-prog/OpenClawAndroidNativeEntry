# Task：V1 信息架构与入口重定义

更新时间：2026-04-21

## 1. 任务定位

- 任务名称：V1 信息架构与入口重定义
- 建议路径：`docs/delivery/tasks/task_v1_information_architecture.md`
- 当前状态：`done`
- 优先级：P1

本任务用于明确 AI 销售助手 V1 在手机端控制入口上的页面结构、信息分组和最小用户闭环，避免继续沿用旧的 OpenClaw Native Entry 信息组织方式。

---

## 2. 任务目标

定义一份面向 V1 的手机端信息架构草案，至少回答以下问题：

1. 首页现在应该展示什么，不该展示什么
2. 产品学习入口如何进入
3. `ProductProfile` 在手机端如何查看与确认
4. 分析结果和报告如何组织
5. 最近任务、历史结果、状态查看如何放置

---

## 3. 当前背景

当前仓库中的 Android 代码仍然主要围绕以下旧入口能力组织：

- Gateway 状态
- 启动 OpenClaw
- 进入 Dashboard/WebView 聊天
- Termux 运行诊断

这套结构与当前 V1 主线已经不一致。

因此，需要先在文档层明确新的页面结构，再决定代码如何最小重构。

---

## 4. 范围

本任务 In Scope：

- 定义手机端首页、产品学习、结果查看、报告查看的页面骨架关系
- 明确 top-level navigation 是否需要调整
- 明确哪些旧页面继续保留为运维/诊断能力，哪些降级处理
- 给出 V1 最小用户操作路径

本任务 Out of Scope：

- Android 代码实现
- WebView 细节处理
- 正式后端 API 实现
- 高保真视觉设计

---

## 5. 涉及文件

高概率涉及：

- `docs/architecture/clients/` 下新增或补充信息架构说明
- `docs/delivery/tasks/task_v1_information_architecture.md`
- `docs/delivery/handoffs/` 下对应 handoff

参考文件：

- `docs/product/overview.md`
- `docs/product/prd/ai_sales_assistant_v1_prd.md`
- `docs/architecture/system-context.md`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/`

---

## 6. 产出要求

至少产出以下内容：

1. 页面结构清单
2. 首页信息优先级
3. V1 最小闭环流程
4. 导航层级建议
5. Android 旧入口能力的去留建议

---

## 7. 验收标准

满足以下条件可认为完成：

1. 后续 Android 重构 task 可以直接引用该结构，不再从零定义页面关系
2. 首页内容明显对齐 AI 销售助手 V1，而不是旧 OpenClaw 宿主入口
3. 保留必要运维入口，但不再让其占据产品主导航中心

---

## 8. 推荐执行顺序

建议执行顺序：

1. 先参考 V1 领域对象基线
2. 梳理当前 Android 页面和导航
3. 新增信息架构说明文档
4. 更新本 task 状态
5. 写 handoff

---

## 9. 风险与注意事项

- 不要把首页重新做成“技术诊断面板”
- 不要把 V1 扩展成完整 CRM 导航体系
- 不要过早依赖真实后端返回结构
- 保持“控制入口”定位，不把手机端做成权威主存

---

## 10. 下一步衔接

本任务完成后，优先衔接：

1. `task_v1_android_control_shell_refactor.md`

---

## 11. 实际产出

本次已完成以下产出：

1. 新增 `docs/architecture/clients/mobile-information-architecture.md`
2. 基于现有 Android 页面与导航代码，明确了 V1 页面结构、首页优先级、主导航与旧入口降级策略
3. 更新当前 task 状态与结果记录
4. 新增对应 handoff 文档

本次形成的核心结论包括：

- 手机端主叙事应从“OpenClaw 宿主入口”切换为“AI 销售助手控制入口”
- top-level navigation 建议调整为 `Home` / `History` / `Ops` / `Settings`
- `ProductProfile`、`LeadAnalysisResult`、`AnalysisReport` 应作为流程页或对象详情页入口，而不是诊断页附属内容
- Gateway、Dashboard、Logs、Termux 相关能力保留，但降级到 `Ops`

---

## 12. 本次定稿边界

本次明确采用以下边界：

- 首页重点是“开始分析”“继续当前流程”“查看最近结果”
- 历史与状态要作为独立轻量入口存在
- 运维与诊断入口保留，但不再占据主导航中心

本次未扩展到：

- Android 代码实现
- WebView 交互细节重写
- 后端 API 设计
- CRM 工作台或完整销售导航体系

---

## 13. 已做验证

本次已完成以下验证：

1. 对照 `docs/product/prd/ai_sales_assistant_v1_prd.md` 中首页、产品学习、结果页、报告页、历史入口的要求，确认新信息架构没有偏离 V1 主线
2. 对照 `docs/reference/schemas/v1-domain-model-baseline.md`，确认页面结构与正式对象边界一致
3. 对照当前 Android 代码中的 `Home` / `Logs` / `Settings` / `Chat` 结构，确认新文档准确反映了现状与改造方向
4. 确认本次没有越权进入 Android 实现、后端实现或 PRD 改写

---

## 14. 实际结果说明

当前该任务已满足原验收目标：

1. 后续 Android 重构 task 可以直接引用该结构，不再从零定义页面关系
2. 首页主叙事已被重新定义为 AI 销售助手 V1 控制入口，而不是旧 OpenClaw 宿主入口
3. 必要运维入口被保留，但已从产品主入口中降级
