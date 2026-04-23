# Task：Android 控制入口壳层重构

更新时间：2026-04-21

## 1. 任务定位

- 任务名称：Android 控制入口壳层重构
- 建议路径：`docs/delivery/tasks/task_v1_android_control_shell_refactor.md`
- 当前状态：`done`
- 优先级：P2

本任务用于在不引入大规模架构重写的前提下，将现有 Android App 从“OpenClaw Native Entry”形态，重构为“AI 销售助手 V1 控制入口壳层”。

---

## 2. 任务目标

在 Android 端完成第一轮最小方向对齐，至少实现以下结果：

- 首页主叙事切换为 AI 销售助手 V1
- 导航围绕产品学习、分析结果、报告查看组织
- 旧 Gateway / Termux / Dashboard 能力降级为辅助诊断入口
- 暂不接入正式后端时，仍可用占位数据跑通页面壳层

---

## 3. 当前背景

当前 Android 工程是可运行、可迭代的，但其页面和行为仍然主要服务旧目标：

- 本机 Gateway 探测
- 启动 OpenClaw
- 进入 WebView Dashboard
- 查看日志和设置

直接在这套旧结构上继续叠加新产品功能，容易造成：

- 页面主叙事混乱
- 导航职责冲突
- 旧技术入口压过新产品入口

因此，先做壳层级重构更稳妥。

---

## 4. 范围

本任务 In Scope：

- 调整首页文案、信息分区与主操作
- 调整导航层级与页面入口
- 新增 V1 占位页或占位组件
- 将旧运维入口降级到次级位置
- 保持现有工程可编译

本任务 Out of Scope：

- 正式后端联调
- 完整领域模型实现
- 正式报告编辑器
- 大规模 UI 重设计
- 重写 Termux / WebView 底层实现

---

## 5. 涉及文件

高概率涉及：

- `app/src/main/java/com/openclaw/android/nativeentry/ui/OpenClawApp.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/navigation/`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/home/`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/`
- `app/src/main/res/values/strings.xml`
- `docs/delivery/tasks/task_v1_android_control_shell_refactor.md`
- `docs/delivery/handoffs/` 下对应 handoff

参考文件：

- `docs/product/overview.md`
- `docs/product/prd/ai_sales_assistant_v1_prd.md`
- `docs/architecture/system-context.md`
- `docs/delivery/tasks/task_v1_domain_model_baseline.md`
- `docs/delivery/tasks/task_v1_information_architecture.md`

---

## 6. 产出要求

至少产出以下内容：

1. 调整后的首页结构
2. 新的 top-level 页面关系
3. V1 占位页面或占位组件
4. 旧诊断入口的降级方案
5. 最小验证记录

---

## 7. 验收标准

满足以下条件可认为完成：

1. 打开 App 后，用户首先感知到的是 AI 销售助手而不是 OpenClaw 宿主控制台
2. Android 端仍保持“控制入口”定位，没有承担正式主存职责
3. 旧 Gateway/Termux 能力仍可进入，但不再作为主产品主线
4. 工程仍能通过最小构建校验

---

## 8. 推荐执行顺序

建议执行顺序：

1. 先读取领域对象基线和信息架构任务
2. 梳理当前导航与首页状态
3. 实施最小 UI 和导航重构
4. 运行最小构建验证
5. 更新 task 状态与 handoff

---

## 9. 风险与注意事项

- 不要把该任务扩展成完整产品开发
- 不要一并重写 runtime 集成层
- 不要一边改壳层一边擅自定义后端 contract
- 若旧代码耦合过深，优先加占位层而不是大拆

---

## 10. 下一步衔接

本任务完成后，可继续拆分：

1. 后端最小 API contract task
2. ProductProfile 占位流转 task
3. AnalysisResult / Report 展示 task

---

## 11. 实际产出

本次已完成以下产出：

1. 调整 Android 顶层导航为 `Home` / `History` / `Ops` / `Settings`
2. 重写首页主叙事与区块结构，使首屏指向 AI 销售助手 V1
3. 新增产品学习、产品画像、分析结果、分析报告、历史状态等占位页面
4. 将 Gateway / Dashboard / Logs / 启动能力收纳到 `Ops`
5. 保持现有 Termux / WebView 链路可进入且工程可编译

---

## 12. 本次定稿边界

本次明确采用以下边界：

- Android 端继续作为控制入口，不承担正式主存
- 占位数据仅用于 UI 壳层演示，不引入后端联调
- `OpenClawChatScreen` 保留为 Dashboard 技术入口，不重写为真实产品学习聊天页
- `LogsScreen` 保留为详细诊断页，但不再作为顶层主导航

本次未扩展到：

- 后端实现
- API contract
- 数据库 schema
- 完整 CRM 工作台
- Termux / WebView 底层重写

---

## 13. 已做验证

本次已完成以下验证：

1. 对照 `docs/reference/schemas/v1-domain-model-baseline.md` 与 `docs/architecture/clients/mobile-information-architecture.md`，确认页面壳层与已冻结对象边界一致
2. 保留并复用现有 Gateway 检测、启动、Dashboard 技术入口和详细诊断能力
3. 运行 `./gradlew :app:assembleDebug`，确认工程通过最小构建校验

---

## 14. 实际结果说明

当前该任务已满足原验收目标：

1. App 首屏首先呈现 AI 销售助手 V1，而不是 OpenClaw 宿主控制台
2. Android 端仍保持“控制入口”定位，没有承担正式主存职责
3. 旧 Gateway / Termux / Dashboard 能力仍可进入，但已降级为辅助入口
4. 工程通过最小构建校验
