# 开发者工作流手册

更新时间：2026-04-23

## 1. 文档定位

本文档是给**开发者本人**看的当前工作流手册。

它不负责定义产品方向，也不替代仓库级 agent 规则；它的作用是说明：

- 进入仓库后先看什么
- 什么时候改方向文档，什么时候新建 task
- 什么时候让 Codex 开工
- 一个任务做完后必须收口哪些文件

本文档不是：

- 产品 PRD
- 仓库级 agent 规则文件
- 单个技术方案文档
- 单个任务文档

仓库级 agent 规则以 [AGENTS.md](/home/yulin/projects/OpenClawAndroidNativeEntry/AGENTS.md) 为准。

---

## 2. 当前工作方式总原则

当前项目采用以下工作方式：

- 唯一工作区：`jianglab:/home/yulin/projects/OpenClawAndroidNativeEntry`
- 主控制台：Codex app
- 辅助终端：FinalShell
- 正式代码与文档事实源：`jianglab` 上的 Git 仓库
- 正式工作流：文档驱动 + task 驱动 + handoff 驱动

当前不维护 Windows 本地的第二份主工作副本。

---

## 3. 当前标准入口

进入仓库后，开发者与 agent 都应优先按下面顺序读取：

1. [AGENTS.md](/home/yulin/projects/OpenClawAndroidNativeEntry/AGENTS.md)
2. [docs/README.md](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/README.md)
3. [docs/product/overview.md](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/product/overview.md)
4. [docs/product/prd/ai_sales_assistant_v1_prd.md](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/product/prd/ai_sales_assistant_v1_prd.md)
5. [docs/adr/ADR-001-backend-deployment-baseline.md](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/adr/ADR-001-backend-deployment-baseline.md)
6. [docs/delivery/tasks/_active.md](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/delivery/tasks/_active.md)
7. 当前 task 引用的 spec / runbook / handoff

如果这条入口链没有跑通，不要直接开始改代码。

---

## 4. 先把变化分成三类

每次有新想法、新需求或新问题时，先不要直接让 Codex 改代码。先判断它属于哪一类：

### A. 方向变化

影响“项目现在到底做什么”的变化，例如：

- 主线变化
- V1 范围变化
- 非目标清单变化
- 目标用户或目标场景变化
- 关键部署 / 分层决策变化

### B. 新任务

在当前方向不变前提下，一个可以独立完成的小闭环，例如：

- 新增一个正式后端接口实现
- 新做一个页面或联调任务
- 新补一个 contract / schema / runbook
- 新增一个 follow-up 修复任务

### C. 细节修订

当前方向不变、当前功能也基本不变，只调整局部细节，例如：

- 文案修改
- 标题修改
- 信息顺序调整
- 某个字段命名优化
- 某个已完成任务后的局部修补

---

## 5. 三类变化分别怎么处理

### 5.1 方向变化：先改方向层文档

如果属于方向变化，不要先动代码。正确顺序：

1. 更新 [docs/product/overview.md](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/product/overview.md)
2. 更新 [docs/product/](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/product)
3. 必要时新增或更新 [docs/adr/](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/adr)
4. 明确哪些旧 task 失效或需要冻结
5. 再拆新的 task
6. 最后再让 Codex 开始执行

重要原则：

> **方向变了，先改文档，不先改代码。**

### 5.2 新任务：先写 task，再开线程

如果属于新任务，标准顺序是：

1. 明确目标
2. 在 [docs/delivery/tasks/](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/delivery/tasks) 中新建 task
3. 必要时更新 [_active.md](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/delivery/tasks/_active.md)
4. 再开一个 Codex 线程
5. 让 Codex 只做这个 task
6. 做完后更新 task 状态与 handoff
7. review 后再进入下一个任务

一个合格 task 至少应说明：

- 目标
- 范围
- out of scope
- 涉及文件
- 验收标准

重要原则：

> **没有 task，就不要直接让 Codex 做正式开发任务。**

### 5.3 细节修订：默认按 follow-up task 管

如果功能已经基本完成，但还有细节要改，不要把新需求继续塞进旧 task。

建议分情况处理：

- 小修订：可以新建一个很小的 follow-up task
- 中等修订：新建独立 task，不污染已完成任务
- 影响方向或边界的修订：退回方向层文档处理

重要原则：

> **功能完成后的细节修改，默认按新 task 或 follow-up task 管理。**

---

## 6. 日常标准工作流

日常推进项目，尽量按下面顺序进行：

### Step 1：先看当前项目状态

先确认：

- 当前主线是什么
- 当前阶段是什么
- 当前唯一推荐任务是什么
- 是否已有正在进行中的正式 task

优先参考：

- [docs/product/overview.md](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/product/overview.md)
- [docs/README.md](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/README.md)
- [docs/delivery/tasks/_active.md](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/delivery/tasks/_active.md)

### Step 2：判断当前问题属于哪一类

先问自己：

- 这是方向变化？
- 这是一个新任务？
- 还是一个细节修订？

如果没分清，不要直接开始改。

### Step 3：更新对应层级文档

根据分类处理：

- 方向变化：改 `product/` 与必要的 `adr/`
- 新任务：改 `delivery/tasks/`
- 细节修订：新建 follow-up task，必要时补 `reference/` 或 `how-to/`

### Step 4：再让 Codex 执行

只有在任务边界清楚后，才开 Codex 线程。提示里至少要明确：

- 先读 `AGENTS.md`
- 先读 `docs/README.md`
- 先读 `_active.md` 和当前 task
- 不得超范围修改
- 做完后更新 task 和 handoff

### Step 5：review

Codex 做完后，你至少检查：

- 改了哪些文件
- 是否超出范围
- 文档是否同步更新
- 是否提供了 handoff
- 是否做了最基本的验证

### Step 6：收口

任务确认完成后：

1. 更新 task 状态
2. 更新或新增 handoff
3. 必要时更新 `reference/`、`architecture/`、`how-to/`
4. 再决定下一个任务
5. 不在同一个线程里无限追加新需求

---

## 7. 文档怎么配合工作流使用

### 7.1 `AGENTS.md`

用途：

- 给 Codex 的仓库级规则文件

你怎么用：

- 低频修改
- 主要用于约束 agent 工作方式
- 不在这里写产品细节和单个 task 细节

### 7.2 `docs/README.md`

用途：

- 当前 docs 总入口

你怎么用：

- 每次进入仓库先读
- 用它确认正式文档结构和当前推荐阅读顺序

### 7.3 `docs/product/`

用途：

- 方向层
- 写总览、PRD、研究与路线图

你怎么用：

- 当项目主线、V1 边界、目标用户或关键流程变化时更新

### 7.4 `docs/adr/`

用途：

- 记录关键决策

你怎么用：

- 只在真正重要的取舍时记录
- 不写零碎临时决定

### 7.4.1 Android 官方资料怎么接入当前工作流

当问题属于 Android 平台知识判断，而不是仓库事实判断时，优先参考：

- 官方 Android 文档
- Android Knowledge Base

当前建议优先这样做的场景包括：

- Compose / Navigation / `AndroidManifest.xml` / 权限
- Android 测试与 screenshot testing
- SDK / AGP / library 升级判断
- 新 API / 最新最佳实践判断

当前仍然必须以仓库文档为准的场景包括：

- 当前 task 优先级
- 产品方向与 V1 范围
- backend / Android 角色边界
- 仓库内自定义 Skills 的事实定义

如果官方 Android 文档与当前仓库现状冲突，处理顺序应为：

1. 先停下，不直接按外部资料改动仓库
2. 回到当前 task / handoff / `docs/`
3. 如涉及边界变化，再补方向层或方案层文档
4. 必要时由开发者明确确认后再继续

### 7.5 `docs/architecture/` 与 `docs/reference/`

用途：

- 方案层
- 记录系统分层、contract、schema、仓库结构和正式技术边界

你怎么用：

- 当任务需要权威技术边界时先看这里
- 当实现改变了正式 contract / 结构时更新这里

### 7.6 `docs/how-to/`

用途：

- 运行、构建、运维、工作流和排障说明

你怎么用：

- 查怎么做
- 固化方法
- 把重复出现的操作沉淀成 runbook

### 7.7 `docs/delivery/tasks/`

用途：

- 执行层的任务控制面

你怎么用：

- 正式开发任务都先写 task
- `_active.md` 用来标识当前推荐任务
- `_template.md` 用于统一 task 结构

### 7.8 `docs/delivery/handoffs/`

用途：

- 记录任务结果、验证和下一步建议

你怎么用：

- 每个重要任务完成后都更新
- 未来的你和未来的 agent 都通过这里接力

### 7.9 `docs/archive/`

用途：

- 历史资料归档

你怎么用：

- 只作背景参考
- 不作为当前正式导航入口

---

## 8. 什么时候不应该直接让 Codex 开工

下面这些情况，不要一上来就让 Codex 改代码：

1. 你自己还没想清楚这是方向变化还是细节修订
2. 你只是在脑暴，还没有任务边界
3. 这个变化会影响版本范围
4. 你只是想参考市面产品
5. 当前线程已经完成原任务，你又临时想加几个新需求
6. `_active.md` 还没有明确当前唯一推荐任务

---

## 9. 一个任务完成后的最小收口标准

一个任务在被认为“完成”之前，至少应满足：

1. 任务目标已实现
2. 没有明显超出范围
3. task 状态已更新
4. handoff 已写
5. 至少做了最小可行验证
6. 若结构、contract 或运行方式变化，相关文档已同步

如果这些没做完，不要轻易把任务当成真正完成。

---

## 10. 当前阶段最推荐的推进方式

当前阶段最推荐的方式不是并行铺很多功能，而是：

1. 用 [_active.md](/home/yulin/projects/OpenClawAndroidNativeEntry/docs/delivery/tasks/_active.md) 明确当前唯一推荐任务
2. 让 Codex 只围绕该任务推进
3. 任务结束后写 handoff
4. 再切下一个任务

当前不建议：

- 一开始就并行很多功能线程
- 一开始就大改 Android 或 backend 架构
- 一边改方向一边写实现
- 一开始就扩到自动触达 / CRM

---

## 11. 典型工作场景示例

### 场景 A：产品需要改方向

例如：“V1 范围要缩小，先不做某块。”

处理方式：

1. 更新 `docs/product/overview.md`
2. 更新 `docs/product/`
3. 必要时写 `docs/adr/`
4. 暂停或冻结旧 task
5. 重拆新 task
6. 再让 Codex 开工

### 场景 B：要做一个新功能

例如：“让 Android 接真实 `/history`。”

处理方式：

1. 新建 task
2. 明确范围和验收标准
3. 更新 `_active.md`
4. 开 Codex 线程执行
5. 完成后更新 handoff

### 场景 C：功能做完了，但细节不满意

例如：“首页主按钮文案还想改。”

处理方式：

- 新建 follow-up task
- 不要继续往旧 task 里无限追加

### 场景 D：还没想清楚细节，先想参考市面产品

处理方式：

1. 不急着让 Codex 改代码
2. 先写研究笔记
3. 提炼设计原则
4. 再进入 PRD 和 task

---

## 12. 当前最重要的开发纪律

### 纪律 1

**方向变化先改文档，不先改代码。**

### 纪律 2

**新功能先有 task，再开线程。**

### 纪律 3

**细节修订默认按 follow-up task 管理。**

### 纪律 4

**一个线程尽量只做一个任务。**

### 纪律 5

**任务做完必须收口，不要无限续接。**

---

## 13. 一句话工作流总结

当前项目的标准推进方式是：

> **先判断是方向、任务还是细节，再更新对应层级文档，最后让 Codex 在明确 task 边界内执行，并用 handoff 收口。**
