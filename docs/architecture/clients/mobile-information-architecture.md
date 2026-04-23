# V1 信息架构与入口重定义

更新时间：2026-04-21

## 1. 文档定位

本文档用于定义 **AI 销售助手 V1** 在手机端控制入口上的最小信息架构基线。

它服务于以下后续工作：

- Android 控制壳层重构
- 首页与流程页骨架设计
- 对象查看与状态入口收口

本文档不是：

- 高保真视觉设计稿
- Android 代码实现文档
- 后端 API 设计文档

关联文档：

- `docs/product/overview.md`
- `docs/product/prd/ai_sales_assistant_v1_prd.md`
- `docs/architecture/system-context.md`
- `docs/reference/schemas/v1-domain-model-baseline.md`
- `docs/delivery/tasks/task_v1_information_architecture.md`

---

## 2. 当前结论

V1 手机端应被重新定义为：

> **AI 销售助手的控制入口，而不是 OpenClaw 宿主控制台。**

因此，V1 信息架构应围绕以下用户目标组织：

1. 立刻开始一轮分析
2. 继续完成当前流程
3. 查看最近结果和报告
4. 在必要时进入运维/诊断入口

当前不应再让以下内容占据产品主入口中心：

- Gateway 状态面板
- 启动 OpenClaw 按钮
- Dashboard/WebView 聊天入口
- Termux 诊断信息

这些能力在 V1 仍可保留，但应降级为运维支持入口。

---

## 3. 现状与问题

基于当前 Android 代码，现有入口结构大致为：

- 首页：`OpenClaw Native Entry` 标题 + Gateway 状态 + 启动 OpenClaw + 进入聊天
- 主导航：`Home` / `Logs` / `Settings`
- 隐藏页：`Chat`，本质为本机 Dashboard WebView 容器

当前结构的主要问题：

1. 首页主叙事是“宿主是否能启动”，不是“用户现在可以完成什么销售任务”
2. 主导航围绕运维与诊断组织，缺少 `ProductProfile`、分析结果、报告等对象入口
3. “进入聊天”在当前实现中更接近 Dashboard 技术入口，而不是产品学习流程页
4. 历史结果和流程状态没有形成面向 V1 的信息骨架

---

## 4. V1 页面结构

## 4.1 页面清单

V1 建议采用以下最小页面结构：

1. 首页 / 开始分析
2. 产品学习页
3. 产品画像确认页
4. 获客分析结果页
5. 分析报告页
6. 历史与状态页
7. 运维与诊断页
8. 设置页

## 4.2 页面职责

### 首页 / 开始分析

作用：

- 说明产品价值
- 提供“开始分析”主入口
- 展示当前任务摘要
- 提供最近一次结果快捷入口

首页重点是“立刻开始”和“继续当前工作”，不是功能目录。

### 产品学习页

作用：

- 承载产品学习对话或问答过程
- 显示当前信息收集进度
- 在最低完整度达到后，引导进入 `ProductProfile` 确认

### 产品画像确认页

作用：

- 展示 `ProductProfile` 的 draft 或 confirmed 形态
- 让用户理解 AI 当前对产品的结构化认识
- 提供确认、返回补充、轻量编辑入口

### 获客分析结果页

作用：

- 展示 `LeadAnalysisResult`
- 解释为什么推荐这些方向
- 提供重新分析或继续生成报告入口

### 分析报告页

作用：

- 展示 `AnalysisReport`
- 提供稳定复看入口
- 作为更正式的输出页承接复制、导出或后续迭代

### 历史与状态页

作用：

- 承接 `AgentRun` 状态查看
- 展示最近的 `ProductProfile` / `LeadAnalysisResult` / `AnalysisReport`
- 让用户知道当前流程处于哪一步

V1 不做完整工作台，只做轻量历史与状态聚合页。

### 运维与诊断页

作用：

- 放置 Gateway 状态、启动 OpenClaw、Dashboard 技术入口、日志诊断
- 服务开发、调试、排障

它是支持页，不是默认产品主入口。

### 设置页

作用：

- 放置少量应用设置、环境说明、版本信息

---

## 5. 首页信息优先级

首页建议按以下优先级组织内容：

### P0：立即行动区

- 产品一句话价值说明
- 主按钮：开始分析
- 次按钮：继续当前流程（仅在存在未完成流程时显示）

### P1：当前工作摘要

- 当前 `AgentRun` 状态
- 当前处于哪一阶段
- 最近更新时间
- 若当前有 `ProductProfile` draft，直接进入确认页

### P2：最近结果入口

- 最近一次 `AnalysisReport`
- 最近一次 `LeadAnalysisResult`
- 最近一次已确认 `ProductProfile`

### P3：辅助入口

- 查看历史与状态
- 查看示例报告（可选）
- 进入运维与诊断

首页不建议默认展示：

- 大面积 Gateway 诊断信息
- 启动命令细节
- WebView 调试信息
- Termux 命令反馈原文

---

## 6. 导航层级建议

## 6.1 Top-level navigation

V1 建议的 top-level navigation 为：

1. `Home`
2. `History`
3. `Ops`
4. `Settings`

说明：

- `Home`：主工作入口
- `History`：历史与状态聚合入口
- `Ops`：原有 Gateway / Logs / Dashboard / Termux 相关能力的收纳入口
- `Settings`：保留设置

不建议把 `ProductProfile`、分析结果、报告分别做成 top-level tab。

这些页面更适合作为流程内页面或对象详情页，由首页和历史页进入。

## 6.2 流程内导航

建议采用如下流程内跳转关系：

```text
Home
  -> 产品学习页
  -> 产品画像确认页
  -> 获客分析结果页
  -> 分析报告页
  -> 历史与状态页

History
  -> ProductProfile 详情
  -> LeadAnalysisResult 详情
  -> AnalysisReport 详情
  -> AgentRun 状态详情

Ops
  -> Gateway 状态
  -> 启动 OpenClaw
  -> Dashboard 技术入口
  -> Logs / 诊断
```

---

## 7. V1 最小用户闭环

V1 建议默认主路径为：

```text
首页
  ↓
开始分析
  ↓
产品学习页
  ↓
产品画像确认页
  ↓
获客分析结果页
  ↓
分析报告页
```

历史回访路径为：

```text
首页 / History
  ↓
最近结果或历史记录
  ↓
ProductProfile / LeadAnalysisResult / AnalysisReport
```

运维路径为：

```text
Home 或 Settings
  ↓
Ops
  ↓
Gateway / Dashboard / Logs
```

---

## 8. 对象到页面的映射

### `ProductProfile`

- 首页展示当前摘要或待确认提示
- 产品画像确认页作为主查看入口
- 历史页展示最近已确认版本和可继续编辑项

### `LeadAnalysisResult`

- 结果页作为主查看入口
- 首页可展示“最近一次分析结果”快捷入口
- 历史页提供版本回看

### `AnalysisReport`

- 报告页作为主查看入口
- 首页展示最近一次报告快捷入口
- 历史页承接复看

### `AgentRun`

- 首页只显示当前进行中的摘要状态
- 历史与状态页作为主要查看入口
- 不建议把完整运行细节直接暴露在首页

---

## 9. 旧入口能力的去留建议

### 保留，但降级到 Ops

- Gateway 状态检测
- 启动 OpenClaw
- Dashboard / WebView 技术入口
- 日志查看
- Termux 诊断链路

### 从首页降级移除

- Gateway 状态卡片作为首页主块
- “启动 OpenClaw”作为首页主 CTA
- “进入聊天”作为首页主路径

### 暂不删除

这些入口当前仍有工程价值，尤其对远程调试和宿主稳定性验证仍然有用。

但它们不再代表 V1 的产品信息架构中心。

---

## 10. Android 壳层重构的直接指导

后续 `task_v1_android_control_shell_refactor.md` 建议按以下原则落地：

1. 先保留现有 Gateway / Logs / Dashboard 能力，但迁入 `Ops` 叙事
2. 用新的 `Home` 叙事替换当前 `OpenClaw Native Entry` 宿主首页
3. 新增 `History` 作为历史与状态入口
4. 将 `Chat` 从“直接产品入口”调整为“产品学习流程页”或临时技术承接页
5. 在没有正式后端前，可先用静态占位或本地假数据承接 `ProductProfile`、分析结果和报告入口，但不改变其信息架构角色

---

## 11. 当前默认原则

- 手机端是控制入口，不是权威主存
- 首页服务当前任务，不服务宿主技术细节
- V1 优先呈现正式对象入口，而不是运行技术入口
- 历史与状态要轻量，但必须存在
- 运维入口保留，但不抢主导航中心
- 不扩展为 CRM 导航体系

---

## 12. 后续引用建议

后续如涉及以下主题，应优先引用本文档：

- 首页骨架
- 导航调整
- 产品学习页和对象详情页关系
- 历史与状态入口设计
- 旧 OpenClaw 宿主入口的降级策略
