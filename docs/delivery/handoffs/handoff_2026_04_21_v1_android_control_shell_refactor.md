# 阶段性交接：Android 控制入口壳层重构

更新时间：2026-04-21

## 1. 本次改了什么

本次完成了 Android 控制入口壳层的第一轮最小重构：

- 首页主叙事从 `OpenClaw Native Entry` 切换为 `AI 销售助手 V1`
- 顶层导航调整为 `Home` / `History` / `Ops` / `Settings`
- 新增产品学习、产品画像、分析结果、分析报告、历史状态占位页
- 旧 Gateway / Dashboard / Logs / 启动能力统一收纳到 `Ops`
- `LogsScreen` 保留为 `Ops` 下的详细诊断页
- 现有 `OpenClawChatScreen` 保留为 Dashboard 技术入口

代码侧新增了 UI-only 占位数据模型，用于在不接后端的前提下跑通新的页面壳层。

---

## 2. 为什么这么改

此前 Android App 的默认叙事仍然围绕：

- Gateway 状态
- 启动 OpenClaw
- 进入 Dashboard
- 查看日志

这与当前 V1 的产品方向不一致，会让技术入口压过产品入口。

因此，本次采用“小改动、低 blast radius”的方式处理：

1. 不重写 Termux / WebView 底层链路
2. 不做后端联调
3. 通过新增占位层和调整导航，把产品入口、对象入口和运维入口分层

这样既能保留现有可运行能力，也能让 App 首屏先呈现 AI 销售助手 V1。

---

## 3. 本次验证了什么

本次已完成以下验证：

1. 对照任务文档、对象基线和信息架构文档，确认实现没有越权扩展到后端、数据库或 CRM
2. 保留现有 Gateway 检测、启动 OpenClaw、Dashboard 技术入口和详细诊断能力
3. 运行 `./gradlew :app:assembleDebug`
   - 结果：`BUILD SUCCESSFUL`
   - 说明：存在 compileSdk 35 与 AGP 8.5.2 的已知告警，但不影响本任务构建通过

---

## 4. 已知限制

本次仍然有以下限制：

- 产品学习、产品画像、分析结果、分析报告页面当前仍为占位壳层
- 没有接入正式后端对象
- 没有实现真实编辑、确认或重跑流程
- `OpenClawChatScreen` 仍是 Dashboard 技术入口，不是正式产品学习对话页

---

## 5. 推荐下一步

推荐下一步从以下两个方向中选择其一：

1. 先拆后端最小 API contract task
2. 继续细化 `ProductProfile` / `AnalysisResult` / `AnalysisReport` 占位流转与展示任务

如果继续保持低 blast radius，优先建议先拆 API contract，再逐步替换当前 UI 占位数据。
