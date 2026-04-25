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

> **V2 planning baseline：定义轻量线索研究方向、搜索 / 来源证据边界、联系方式边界、数据模型和后续 contract。**

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

> **面向中小企业老板 / 销售负责人的 AI 销售助手，从 V1 的“获客方向分析”升级为“带来源证据的轻量线索研究”。**

V2 当前规划重点：

- AI 引导式产品学习，而不是纯表单录入。
- 基于产品画像进行轻量线索研究。
- 允许系统主动联网 / 中文公开网页搜索。
- 允许产出具体公司 / 机构候选。
- 候选必须有来源证据、匹配理由、不确定性和下一步人工验证动作。
- 联系方式必须可溯源、受控展示，默认人工验证，不自动触达。

当前 V2 草案入口：

- `docs/product/prd/ai_sales_assistant_v2_prd.md`
- `docs/architecture/data/v2-lead-research-data-model.md`
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
- V2 方向是轻量线索研究。
- V2 允许主动联网 / 中文公开网页搜索。
- V2 可以产出具体公司候选。
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

V2 线索研究中，无来源候选不能进入正式结果。

### 原则 3：联系方式保守处理

公司联系方式和个人联系方式必须分开建模。联系方式必须有来源，默认人工验证，不自动触达。

### 原则 4：后端是主真相

Android 是控制入口，runtime 是执行层，backend services 是正式对象写回裁决层。

### 原则 5：小步任务化

V2 进入实现前，应先冻结 PRD v0.2、data model v0.2、ADR 和 backend contract，再创建 implementation task queue。

---

## 10. 推荐下一步

当前推荐顺序：

1. 冻结 V2 PRD v0.2。
2. 冻结 V2 data model v0.2。
3. 补 V2 backend contract 草案。
4. 决定搜索 provider、数据保留和联系方式边界。
5. 再创建后端-only lead research spike task。

当前不建议直接实现后端 schema、API、搜索 provider 或 Android UI。

---

## 11. 一句话总结

当前项目已经从 V1 demo baseline 转入：

> **AI 销售助手 V2 planning baseline：在不扩成 CRM 或自动触达产品的前提下，定义带来源证据的轻量线索研究。**
