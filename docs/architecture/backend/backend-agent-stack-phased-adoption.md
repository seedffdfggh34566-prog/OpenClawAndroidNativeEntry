# 后端 Agent 技术栈与分阶段落地方案

更新时间：2026-04-23

## 1. 文档定位

本文档用于把当前仓库针对后端 agent 技术栈的推荐结论收口为一份**方案层说明**。

它回答的问题包括：

- LangGraph 是否适合当前后端
- MCP 是否适合作为后端工具协议
- `Pydantic` 应该扮演什么角色
- 可观测性应该先选 `Langfuse` 还是 `LangSmith`
- 何时从 `SQLite` 走向 `Postgres + pgvector`
- `MCP Toolbox for Databases` 应放在什么边界内使用

本文档不是：

- 当前活跃开发 task
- 产品方向文档
- 一次性要求全部立即落地的实施清单

---

## 2. 当前仓库现实

当前仓库后端已经完成最小正式实现，现实基线是：

- API 层：`FastAPI`
- schema 层：`Pydantic v2`
- persistence 层：`SQLAlchemy + SQLite + Alembic`
- runtime 层：`backend/runtime/adapter.py` 中的可预测 stub
- 测试层：`pytest` 作为默认 runner
- 日志层：标准 `logging` + JSON 风格 structured logging

当前尚未进入：

- 真实 runtime 编排
- 正式向量检索
- 正式 observability 平台接入
- 正式工具协议统一层

因此，本轮最合理的目标不是“六件套一起落地”，而是：

> **先把后端 guardrails、边界和分阶段 adoption 路线说清楚，再按 task 分步引入。**

---

## 3. 当前推荐结论

### 3.1 API 与产品后端主干

当前应继续保留：

- `FastAPI` 作为 API edge
- `backend/api/services.py` 作为产品后端协调层
- `backend/runtime/` 作为执行层边界

不要把 agent/runtime 工具栈反向扩展成整个后端的主骨架。

### 3.2 `Pydantic`

当前应继续把 `Pydantic` 作为统一 schema 核心。

推荐覆盖范围：

- API request / response
- runtime step input / output
- tool input / output
- persisted JSON payload
- 后续 MCP tool schema

这是当前最应继续强化、且几乎没有争议的选择。

### 3.3 `LangGraph`

当前建议使用 `LangGraph`，但只在未来真实 runtime/orchestration 接入时使用，并限制在：

- `backend/runtime/`
- `AgentRun` 相关执行图
- checkpoint / resume / human-in-the-loop 场景

不建议：

- 用 `LangGraph` 重写整个后端
- 把 API 层、持久化层、产品服务层都改造成 graph runtime

### 3.4 `MCP`

当前建议使用 `MCP`，但只把它当作：

- 外部工具接入协议
- 外部资源 / 文档 / schema / log 暴露协议
- 受控工具调用边界

不建议：

- 用 `MCP` 替代 backend 内部 Python service 调用
- 把产品后端主流程重写成 MCP server-to-server 架构

### 3.5 可观测性：`Langfuse` 优先

当前建议优先选择 `Langfuse`，原因是：

- 更适合当前 repo 的轻量正式后端阶段
- 更适合后续 `MCP` tracing 与自托管思路
- 不要求仓库先全面押注 LangChain/LangGraph 平台化

当前不建议默认同时引入 `Langfuse + LangSmith`。

若未来后端已经深度围绕 LangGraph / LangSmith datasets / evaluation 演进，再单独评估是否切换。

### 3.6 `Postgres + pgvector`

当前建议把数据库方向拆开看：

- `Postgres`：下一阶段应尽快规划替代 `SQLite`
- `pgvector`：只有当检索 / embedding / 相似召回进入正式 scope 时再启用

也就是说：

- `Postgres` 是正式后端演进的合理下一步
- `pgvector` 不是当前最小后端闭环的 blocker

### 3.7 `MCP Toolbox for Databases`

当前建议把它定位为：

- 开发 / 运维增强层
- schema 巡检与受控查询工具层
- 后续只读资源或 least-privilege custom tools 的实现候选

当前不建议：

- 让生产 runtime agent 直接拥有 arbitrary SQL 执行权
- 在没有权限边界、审计和最小权限用户前，把 DB 工具暴露给自动 agent

---

## 4. 推荐的后端分层关系

当前推荐的关系为：

```text
FastAPI API layer
    ↓
Product backend services
    ↓
Runtime orchestration boundary
    ↓
Persistence / observability / tool integrations
```

对应技术角色应为：

- `FastAPI`：API 边界
- `Pydantic`：结构化 schema 与 payload 核心
- `LangGraph`：未来 runtime 编排层
- `MCP`：未来工具协议层
- `Langfuse`：运行观测层
- `Postgres`：正式结构化主存
- `pgvector`：按需启用的检索增强层

---

## 5. 当前不建议的做法

当前不建议：

1. 把 `LangGraph` 当成整个后端框架
2. 把 `MCP` 当成产品后端内部服务协议
3. 在没有 task / spec 的前提下直接做 `SQLite -> Postgres` 迁移
4. 因为“以后可能会做检索”就提前强上 `pgvector`
5. 同时接入多个 observability 平台
6. 把 `MCP Toolbox for Databases` 直接给生产 agent 放开任意 SQL

这些做法都会明显超出当前仓库“控制风险、逐步演进”的原则。

---

## 6. 推荐的分阶段路线

### Phase 0：当前已完成基线

当前已经具备：

- 最小正式 backend
- formal object truth
- stub runtime boundary
- 最小后端测试与本地运行方式

### Phase 1：规则与工作流补强

本阶段优先补：

- `backend/AGENTS.md`
- backend skill specs
- backend stack adoption 方案文档
- `pytest` 默认测试入口
- 结构化日志基础设施

目标是把“后端该怎么演进”先固定住。

### Phase 2：正式后端基线升级

建议下一批正式后端能力优先考虑：

- `Alembic` baseline 与迁移命令
- `SQLite -> Postgres` 迁移方案
- API / object contract 稳定化
- 后端本地验证与风险分级补强

本阶段仍不强求 `pgvector`、`LangGraph`、`MCP` 一次性全部进入实现。

### Phase 3：真实 runtime 与观测

当真实 runtime 接入进入正式 scope 时，建议引入：

- `LangGraph` 负责执行编排
- `Langfuse` 负责 traces / runs / observations

此时仍应保持：

- product backend truth 不属于 runtime
- runtime 结果必须通过正式对象写回边界进入主真相

### Phase 4：受控工具协议与数据库工具层

当 runtime 需要更正式的外部工具边界时，建议引入：

- 只读或受控的 `MCP resources`
- 明确输入输出 schema 的 `MCP tools`
- 只读优先、least-privilege 优先的 DB 工具

此时才考虑：

- `MCP Toolbox for Databases`
- `pgvector`
- 更系统化的 tool server 治理

---

## 7. 与当前仓库任务体系的关系

本文档是方案层事实源，不直接替代 task。

如果后续要真正实施以下任一项，仍应先新建 follow-up task：

- 引入 `LangGraph`
- 引入 `MCP`
- 切换 `SQLite -> Postgres`
- 引入 `pgvector`
- 接入 `Langfuse`
- 接入 `MCP Toolbox for Databases`

换句话说：

> **本文件先定义“应该怎么分步做”，而不是宣布“这些技术现在已经全部启用”。**
