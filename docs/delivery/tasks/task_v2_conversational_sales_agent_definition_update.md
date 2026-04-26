# Task：V2 conversational sales agent definition update

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V2 conversational sales agent definition update
- 建议路径：`docs/delivery/tasks/task_v2_conversational_sales_agent_definition_update.md`
- 当前状态：`done`
- 优先级：P0

---

## 1.1 队列衔接

- 当前 task 是否允许执行 agent 自主推进：`yes`
- 建议上游入口：`docs/delivery/tasks/_active.md`
- 建议下游任务：暂无自动排定
- 停止条件：
  - 需要进入后端 / Android / 数据库实现
  - 需要冻结 V2.1 API contract
  - 需要决定 `LeadDirectionVersion` 是否独立建表
  - 需要实现 `sales_agent_turn_graph`

---

## 2. 任务目标

将 V2 定义从“轻量线索研究工具”调整为“对话式专属销售 agent prototype”。

本任务只更新文档定义，不实现后端、Android、数据库 migration、runtime graph、搜索 provider 或 API。

---

## 3. 当前背景

用户明确：

- V2 先做 prototype。
- 用户希望通过对话框进行获客分析。
- agent 应能基于用户信息主动询问并回答。
- 获客分析方向应能通过对话实时调整和迭代。
- 最终目标是用户拥有一个专属销售 agent。

因此，V2.1 应先验证对话式销售 agent，V2.2 再进入带来源证据的轻量线索研究。

---

## 4. 范围

本任务 In Scope：

- 更新 V2 PRD 到 Draft v0.2。
- 新增 V2 sales agent data model 草案。
- 新增 ADR-006。
- 调整 V2 lead research data model 为 V2.2 子模型。
- 更新 overview、roadmap、README、runtime spec、_active、delivery README。
- 新增 handoff。

本任务 Out of Scope：

- 后端代码
- Android 代码
- 数据库 schema / migration
- runtime graph 实现
- 搜索 provider 接入
- API contract 实现
- MVP 定义

---

## 5. 产出要求

至少应产出：

1. V2 PRD 明确 V2.1 / V2.2 / V2.3 阶段。
2. V2.1 首批对象提升为 `SalesAgentSession`、`ConversationMessage`、`ProductProfileRevision`、获客方向版本和 `AgentRun(run_type=sales_agent_turn)`。
3. ADR-006 冻结 prototype、本地后端沉淀、继续 LangGraph、会话消息首批持久化和 lead research 后置。
4. `_active.md` 明确当前仍不自动创建 V2 implementation queue。

---

## 6. 验收标准

满足以下条件可认为完成：

1. V2 PRD 不再把 V2.1 定义为 lead research first。
2. `v2-sales-agent-data-model.md` 存在并记录 V2.1 首批对象。
3. ADR-006 存在并与 ADR-005 不冲突。
4. runtime spec 记录 `sales_agent_turn_graph` 边界。
5. `_active.md` 不排实现任务。
6. `git diff --check` 通过。

---

## 7. 实际产出

- 已更新 V2 PRD 到 Draft v0.2。
- 已新增 V2 sales agent data model 草案。
- 已新增 ADR-006。
- 已将 V2 lead research data model 调整为 V2.2 子模型。
- 已更新入口与路线图文档。
- 已更新 runtime spec 的 V2 graph 边界。
- 已更新 `_active.md` 和 handoff。

---

## 8. 本次定稿边界

本次只冻结 V2 对话式专属销售 agent 的 planning baseline，不冻结 schema、API、runtime implementation、搜索 provider 或 Android UI。

---

## 9. 已做验证

- `git diff --check`
