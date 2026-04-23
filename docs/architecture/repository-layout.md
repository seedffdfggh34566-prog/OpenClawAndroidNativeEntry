# 后端优先的仓库与文档对齐方案

更新时间：2026-04-23

## 1. 文档定位

本文档用于正式记录当前项目在进入“后端优先阶段”后，对仓库结构、文档结构与 agent 工作流的调整方案。

本文档回答的问题包括：

1. 当前仓库现在到底是什么类型的仓库
2. 后端应如何加入当前项目
3. OpenClaw runtime 与产品后端如何分层
4. 数据层应放在哪里开发
5. 当前旧文档结构还是否继续有效
6. 后续 agent 工作流应如何调整

本文档不是：

- PRD
- 单个任务文档
- 具体数据库 schema
- 具体后端框架选型说明

---

## 2. 本次调整的核心结论

当前项目已从“Android 原生入口实验”正式转入：

> **AI 销售助手 V1 的后端优先、多端入口、agent 驱动开发阶段**

本次调整包含以下关键结论：

1. 当前仓库应被视为**产品主仓库**，而不是 Android 专仓
2. 正式业务后端应作为仓库内的独立一层加入，而不是并入 `app/`
3. Android 继续保留为当前入口，但未来允许出现 iOS 与 PC 入口
4. OpenClaw runtime 属于 backend 边界内的执行层，不等于正式业务后端
5. 数据层应在 backend 侧开发，而不是落在客户端本地
6. 文档系统应从“编号目录”逐步升级为“产品 / 架构 / 参考 / 交付”式结构
7. agent 工作流应从“依赖聊天上下文”转向“依赖 repo 内 task / handoff / runbook”

---

## 3. 当前仓库的正确理解

当前仓库虽然仍名为 `OpenClawAndroidNativeEntry`，但从项目主线和正式文档来看，它现在更应被理解为：

> **AI 销售助手 V1 的单一权威仓库**

当前仓库内应逐步承载：

- 正式产品文档
- 后端代码
- Android 客户端
- 后续多端共享 contract
- runtime 集成代码
- 运维与 agent 工作流文档

因此，当前最稳妥的策略不是立即拆仓，而是：

- **短期继续单仓推进**
- **中期做目录去 Android 中心化**
- **长期再视需要调整仓库命名与多应用目录**

---

## 4. 后端优先的目标仓库结构

## 4.1 当前建议的过渡结构

当前最建议采用的低 blast radius 结构为：

```text
repo/
├─ app/                  # 现有 Android 工程，短期保留
├─ backend/              # 正式后端
│  ├─ api/               # 正式业务 API 层
│  ├─ runtime/           # OpenClaw / Agents runtime 适配层
│  ├─ worker/            # 后台任务与异步执行
│  └─ tests/
├─ packages/             # 共享领域、contract、prompt、工具
│  ├─ domain/
│  ├─ contracts/
│  ├─ prompts/
│  └─ tooling/
├─ infra/
├─ docs/
└─ scripts/
```

## 4.2 为什么当前不直接大迁移

当前不建议立刻把仓库整体改成 `apps/android` / `apps/backend-api` / `apps/backend-runtime` 的原因包括：

- 当前 Android 工程已存在，直接搬迁会扩大 blast radius
- 当前优先级是后端落地，不是目录美化
- 当前更需要 agent 工作流稳定，而不是先做大规模结构重排

因此当前原则是：

> **先加 backend，再慢慢去 Android 中心化。**

---

## 5. 后端、runtime 与数据层边界

## 5.1 正式业务后端

正式业务后端负责：

- `ProductProfile`
- `LeadAnalysisResult`
- `AnalysisReport`
- `AgentRun`
- 正式 API
- 业务状态与版本
- 历史记录与对象沉淀

它是正式业务真相层。

## 5.2 OpenClaw runtime

OpenClaw runtime 在当前系统中应归入 backend 边界，但职责不同于正式业务后端。

它负责：

- 模型调用
- 工具调用
- agent 流程执行
- 中间结果生成
- runtime 级日志

它不负责：

- 业务对象主数据库
- 正式对象生命周期裁决
- 最终产品 API 真相

## 5.3 数据层

数据层应在 backend 一侧开发，至少包括：

- 正式业务数据库
- 文件或对象存储
- 检索索引
- 运行日志

客户端可以有缓存，但不能承担正式主存职责。

---

## 6. 文档结构调整方案

## 6.1 当前正式文档结构

当前仓库正式采用以下文档结构：

```text
docs/
├─ README.md
├─ product/
├─ architecture/
├─ reference/
├─ how-to/
├─ adr/
├─ delivery/
└─ archive/
```

## 6.2 当前使用原则

当前使用原则为：

1. `docs/README.md` 是统一入口
2. `docs/delivery/tasks/_active.md` 是当前执行入口
3. `product / architecture / reference / how-to / adr / delivery / archive` 是正式分类
4. 不再继续新增旧编号目录

---

## 7. agent 工作流调整方案

## 7.1 总原则

agent 工作流的核心不再是“在聊天里记住所有上下文”，而是：

> **把方向、边界、任务、交接都沉淀到仓库中，作为 agent 可读的系统事实源。**

## 7.2 方向、方案、执行三层模型

当前建议把文档与工作流分成三层：

### A. 方向层

主要包括：

- `docs/product/overview.md`
- `docs/product/*`
- `docs/adr/*`

作用：

- 定义项目做什么
- 定义版本做什么与不做什么
- 定义关键架构和部署基线

### B. 方案层

主要包括：

- `docs/architecture/*`
- `docs/reference/*`
- `docs/how-to/*`

作用：

- 定义技术边界
- 定义工程执行方式
- 定义仓库、文档与 agent 协作规则

### C. 执行层

主要包括：

- `docs/delivery/tasks/*`
- `docs/delivery/handoffs/*`

作用：

- 承接正式任务
- 记录当前状态
- 为下一轮执行保留连续性

## 7.3 标准执行顺序

后续 agent 的标准执行顺序建议为：

1. 读取 `AGENTS.md`
2. 读取 `docs/README.md`
3. 查看 `docs/delivery/tasks/_active.md`
4. 读取对应 task
5. 回看 task 引用的 PRD / spec / decision
6. 只在 task 边界内做最小实现
7. 完成后更新 task、handoff、必要的 runbook / spec

---

## 8. 人与 agent 的维护边界

### 8.1 人优先维护

- `docs/product/overview.md`
- `docs/product/*`
- `docs/adr/*`

原因：

- 这些文件定义产品意图与关键取舍
- agent 不应静默改写版本含义

### 8.2 agent 应主动维护

- `docs/architecture/*`
- `docs/reference/*`
- `docs/delivery/tasks/*`
- `docs/how-to/*`
- `docs/delivery/handoffs/*`

原因：

- 这些文件直接服务执行与交接
- 是保持 agent 连续推进能力的关键

---

## 9. 分阶段实施建议

## 9.1 Phase 1：文档控制平面对齐

目标：

- 建立总导航
- 建立 active task 入口
- 建立模板
- 明确后端优先工作流

## 9.2 Phase 2：后端最小实现立项

目标：

- 新建正式 backend 实现 task
- 明确最小服务范围
- 明确实现顺序与验证标准

## 9.3 Phase 3：新增 `backend/` 骨架

目标：

- 在不影响 Android 现有工程的前提下，加入独立后端目录

## 9.4 Phase 4：最小 API 落地

建议最小实现顺序：

1. 服务骨架
2. 配置 / 日志 / 健康检查
3. 最小持久化
4. `POST /product-profiles`
5. `GET /product-profiles/{id}`
6. `GET /history`
7. `POST /analysis-runs`
8. `GET /analysis-runs/{id}`
9. `GET /reports/{id}`
10. runtime 接入

---

## 10. 当前推荐的下一步

当前最推荐的下一步正式开发任务为：

> **进入 V1 后端最小实现线程**

原因：

- 对象基线已经冻结
- 信息架构已经冻结
- Android 壳层已经对齐
- API contract 已完成文档冻结
- 当前最缺的是正式后端落地，而不是继续扩展入口壳层
