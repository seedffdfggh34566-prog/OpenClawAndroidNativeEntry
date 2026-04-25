# 项目总览（当前阶段）

更新时间：2026-04-25

## 1. 文档定位

本文档用于说明本仓库的当前主线、当前阶段、当前范围、当前系统分层与当前工作方式，供人工和 AI agent 快速接手。

本文档只记录当前已经明确的共识。后续如产品方向、版本范围、系统分层、部署基线或工作方式发生变化，应优先更新本文件。

---

## 2. 当前项目是什么

当前项目已经不再以早期 OpenClaw Android Native Entry / 原生控制入口实验为主要目标。

当前项目主线为：

> **AI 销售助手 App**

V1 已正式收口为 demo-ready release candidate / learning milestone。当前阶段进入：

> **V2 planning baseline：定义对话式专属销售 agent prototype、销售会话数据模型、后续轻量线索研究能力和 contract。**

当前不是 V1 继续开发阶段，也不是 V2 MVP 实现阶段。

---

## 3. V1 已完成基线

V1 已验证以下主闭环：

```text
产品学习 -> 产品画像确认 -> LeadAnalysis LLM -> 结构化报告 -> Android 真机复看
```

V1 可复用资产包括：

- `ProductProfile`
- `LeadAnalysisResult`
- `AnalysisReport`
- `AgentRun`
- ProductLearning LLM draft 生成经验
- LeadAnalysis LLM draft 生成经验
- TokenHub provider 接入经验
- runtime metadata 与 token usage 观测
- Developer LLM Run Inspector
- Android 控制入口和真机 demo 路径
- 真实中文业务样例库和 eval 记录

V1 不进入 MVP，原因见：

- `docs/product/research/v1_closeout_2026_04_25.md`

---

## 4. 当前 V2 方向

V2 暂定方向为：

> **面向中小企业老板 / 销售负责人的对话式专属销售 agent prototype。**

V2 当前规划重点：

- V2.1 先验证对话式产品理解、获客方向分析和方向迭代。
- 用户通过 Android 内对话框与销售 agent 交互。
- agent 主动追问产品、客户、地区、客单价、交付方式和成交约束。
- 用户可通过对话实时调整获客方向。
- 对话必须沉淀为结构化业务对象，而不是一次性聊天记录。
- V2.2 再进入联网 / 中文公开网页搜索、具体公司候选、来源证据和受控联系方式展示。

当前 V2 草案入口：

- `docs/product/prd/ai_sales_assistant_v2_prd.md`
- `docs/architecture/data/v2-sales-agent-data-model.md`
- `docs/architecture/data/v2-lead-research-data-model.md`
- `docs/adr/ADR-006-v2-conversational-sales-agent-baseline.md`
- `docs/adr/ADR-005-v2-lead-research-scope-and-search-boundary.md`

---

## 5. 当前明确不做

当前阶段不做：

- Web 前端
- 完整 CRM
- 自动邮件 / 短信 / 企微 / 电话触达
- 自动外呼
- 批量联系人抓取
- 批量联系人导出
- 大规模爬虫系统
- 企业级团队协作审批流
- 正式商业化计费系统
- 未经任务排定的后端 schema / migration / API 实现
- 未经任务排定的 Android 大改

---

## 6. 当前系统路线

当前继续沿用 V1 已验证的系统路线：

> **本地服务器承载正式后端 + Android 作为控制入口 + 架构按未来可迁云设计**

其含义是：

- Android 端不是权威主存，只负责控制入口、状态查看、任务发起、结果查看和轻量编辑。
- 正式后端负责业务对象主存、任务执行编排、结果沉淀与后续协作能力预留。
- 当前默认 runtime 方向仍为 `backend/runtime/` 内的 LangGraph direct orchestration。
- Runtime / agent 只产出 draft payload 和工具执行结果，不直接写正式业务对象。
- Backend services 负责正式对象写回和业务边界裁决。
- 本地部署是当前工程基线，不代表长期耦合到本地路径或单机脚本。

---

## 7. 当前阶段

当前处于：

> **V2 planning baseline 阶段**

已经明确：

- V1 已冻结，不继续追加 V1 功能。
- V2 方向是对话式专属销售 agent prototype。
- V2.1 先做对话式产品理解、获客方向分析和方向迭代。
- V2.2 允许主动联网 / 中文公开网页搜索。
- V2.2 可以产出具体公司候选。
- V2 不做 Web 前端。
- V2 不做自动触达或联系人抓取产品。
- 后端仍是 formal truth layer。

尚未冻结：

- V2 是否作为 MVP。
- 是否需要正式云部署。
- 是否需要账号、多用户、租户隔离和权限。
- 搜索 provider。
- 数据保留策略。
- 个人联系方式展示和删除策略。
- SalesAgentSession / ConversationMessage API contract。
- LeadDirectionVersion 是否独立建表。
- V2 domain/schema baseline。
- V2 backend API contract。
- V2 task queue。

---

## 8. 当前文档体系

当前 `docs/` 目录继续作为唯一正式文档入口：

- `product/`：产品方向、PRD、研究与路线图
- `architecture/`：系统分层、仓库结构与 backend / runtime / data / clients 方案
- `reference/`：API contract、领域模型与其他权威参考
- `how-to/`：运行、运维、协作和排障手册
- `adr/`：关键架构与部署决策
- `delivery/`：任务与交接文档
- `archive/`：历史资料归档

历史 OpenClaw 相关文档只作参考，不作为当前产品主线。

---

## 9. 当前工作原则

### 原则 1：先定义，再实现

V2 方向变化、搜索边界、数据模型、API contract 或运行规则变化应先进入 docs / ADR / task，再进入代码。

### 原则 2：先证据，再候选

V2.2 线索研究中，无来源候选不能进入正式结果。

### 原则 3：联系方式保守处理

公司联系方式和个人联系方式必须分开建模。联系方式必须有来源，默认人工验证，不自动触达。

### 原则 4：后端是主真相

Android 是控制入口，runtime 是执行层，backend services 是正式对象写回裁决层。

### 原则 5：小步任务化

V2 进入实现前，应先冻结 conversational sales agent contract、data model v0.2、ADR 和 backend contract，再创建 implementation task queue。

---

## 10. 推荐下一步

当前推荐顺序：

1. 冻结 V2.1 conversational sales agent backend contract 草案。
2. 冻结 V2 sales agent data model v0.2。
3. 设计 `sales_agent_turn_graph` draft schema。
4. 创建 V2.1 backend-only prototype task。
5. 完成 V2.1 后，再恢复 V2.2 lead research provider、来源证据和联系方式实现讨论。

当前不建议直接实现后端 schema、API、搜索 provider 或 Android UI。

---

## 11. 一句话总结

当前项目已经从 V1 demo baseline 转入：

> **AI 销售助手 V2 planning baseline：在不扩成 CRM 或自动触达产品的前提下，定义对话式专属销售 agent prototype。**
