# Android 客户端实现约束说明

更新时间：2026-04-23

## 1. 文档定位

本文档用于说明当前仓库为什么对 Android 客户端采用一组偏克制的默认实现约束。

它回答的问题包括：

- Android 客户端在当前系统里到底扮演什么角色
- 为什么当前优先采用轻量 UDF / 现代 MVI 风格
- 为什么 `ViewModel` / state holder 是默认优先项
- 为什么 domain layer 是可选而不是必选
- 为什么当前优先轻量模块化，而不是立刻改成重型多模块结构
- 哪些 Android 架构变化需要额外审批

本文档不是：

- Android 代码风格清单
- 根仓库 agent 规则文件
- 产品 PRD
- 具体功能任务文档

Android agent 的执行性规则以 `app/AGENTS.md` 为准；本文档负责解释这些约束为什么成立。

---

## 2. 当前结论

当前 Android 客户端应被理解为：

> **AI 销售助手 V1 的控制入口，而不是产品主真相层。**

因此当前 Android 侧最重要的目标不是“建立一套大而全的 Android 架构样板”，而是：

1. 稳定承接控制入口职责
2. 清晰表达页面状态与流程状态
3. 便于与后端主真相层联调
4. 避免过早引入超出当前阶段的工程复杂度

---

## 3. Android 在总体架构中的角色

根据当前仓库的主线，系统分层是：

- Android：控制入口
- backend：正式业务后端与权威对象主存
- OpenClaw runtime：执行层

这意味着 Android 当前应重点承担：

- 发起流程
- 查看状态
- 查看结果
- 轻量编辑与确认
- 运维和诊断入口的有限承接

Android 当前不应承担：

- 业务主真相
- 主要任务编排
- 独立于 backend 的对象生命周期裁决
- 为未来所有可能场景提前铺好过重的架构层级

---

## 4. 为什么当前采用轻量 UDF / 现代 MVI 风格

当前推荐的默认方向是：

- 单向数据流
- 明确的 screen state
- 事件驱动的状态更新
- UI 与状态生产逻辑分离

这样做的原因是：

1. 当前 Android 主要承担“控制入口 + 状态展示”职责，最需要的是清晰、稳定、易联调的状态表达
2. 现有工程已经是 Compose-first，更适合围绕 screen state 组织代码
3. 这类结构既足够现代，又不会把当前项目推向重型框架依赖
4. 对后续接入真实 backend 数据更友好，能减少 UI 与临时实现耦合

这里说的“现代 MVI 风格”是指：

- 接受事件
- 由状态持有者处理
- 产出单一方向的 UI state

它不是要求引入完整的重型 MVI 框架。

---

## 5. 为什么 `ViewModel` / state holder 是默认优先项

当前默认优先使用 screen-level `ViewModel` 或等价 state holder，原因包括：

- 屏幕级状态需要跨重组稳定存在
- 后续与 backend 交互时，需要有明确的状态生产入口
- 能把 UI 展示与状态处理分开，减少页面直接堆逻辑
- 更便于测试和替换占位数据 / 真实数据

但这并不意味着所有状态都必须进 `ViewModel`。

当前推荐的边界是：

- 涉及屏幕级、较长生命周期、与数据读取相关的状态：优先放 `ViewModel` / screen state holder
- 纯 UI 行为、依赖 `Context`、导航、snackbar 等 UI 细节：留在 UI 层或 UI 作用域的简单 state holder

---

## 6. 为什么 domain layer 是可选而不是必选

当前不把 domain layer 作为 Android 侧的默认必需层，原因是：

1. 当前 Android 客户端不是业务真相层
2. 现阶段很多业务复杂度在 backend，而不是 Android 端
3. 如果为了“架构完整”强行引入大量 use case class，反而会放大样板代码和维护成本
4. 当前更需要清晰的状态流与联调边界，而不是额外的概念层数

因此当前建议是：

- 当某段业务逻辑确实复杂、复用明确、跨多个 state holder 重复出现时，再按需引入 domain/use case
- 在没有明确收益时，不默认展开成重型 Clean Architecture

---

## 7. 为什么当前优先轻量模块化

当前仓库里的 Android 工程仍较轻，且项目主复杂度不只在 Android。

因此当前更合理的方向是：

- 先保持单 `app/` 模块或极轻量扩展
- 优先把代码边界、状态边界和联调边界理顺
- 只有在出现明确收益时，再引入模块化

明确收益通常包括：

- 明显的团队并行开发需求
- 清晰的复用边界
- 明确的构建性能收益
- 平台或功能边界已经稳定

当前不推荐因为“Android 最佳实践模板”就立即做：

- 大规模 feature modules
- api / impl 大拆分
- 复杂共享 UI 基础库拆分

---

## 8. 哪些变化需要额外审批

以下 Android 方向变化应视为额外审批事项，而不是默认演进：

- 引入重型 MVI 框架
- 引入强 Clean Architecture 分层并大规模改写现有结构
- 引入 Hilt、Room、Retrofit、WorkManager 等广泛基础设施并扩散到多处
- 把单 `app/` 工程改造成大型多模块结构
- 改写 Android 与 backend 当前约定的职责边界
- 把 Android 从控制入口静默升级成业务主真相层

---

## 9. 与 backend-first / 多端入口主架构的关系

这些 Android 约束的本质目标，是让 Android 客户端与当前仓库的总架构保持一致：

- backend-first
- 多端入口
- runtime 与产品层解耦
- Android 负责入口与状态承接，而不是承担全部系统复杂度

换句话说：

> **当前 Android 侧的克制，不是保守，而是为了让整体架构边界更稳定。**

在这个阶段，优先选择轻量、可联调、可维护的 Android 实现方向，比追求“看起来更完整”的重型架构更符合仓库目标。

---

## 10. Android Knowledge Base 在当前仓库里的定位

当前仓库推荐把 Android Knowledge Base 视为：

- Android 相关问题的优先官方参考层
- 用于确认最新 Android guidance 的外部依据
- 帮助避免 agent 依赖过时 Android 经验的补强机制

它最适合优先用于：

- Compose / Navigation / `AndroidManifest.xml` / 权限问题
- Android 测试、截图测试与验证建议
- SDK / AGP / library 升级判断
- 新 API、最新平台行为或最近新增能力判断

它不应直接决定：

- 当前 task 的优先级
- 产品方向与 V1 范围
- backend 与 Android 的职责边界
- 仓库内自定义 Skills 的事实定义

如果官方 Android 文档与当前仓库文档、task 或 handoff 的边界发生冲突，应先回到：

1. 当前 task
2. 当前 handoff
3. `docs/`
4. 人工确认

而不是让外部官方资料直接改写仓库约束。
