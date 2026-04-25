# 决策记录：V2 Lead Research Scope And Search Boundary

- 文档路径建议：`docs/adr/ADR-005-v2-lead-research-scope-and-search-boundary.md`
- 文档状态：Approved V2.2 planning baseline v0.1
- 决策日期：2026-04-25
- 关联文档：
  - `docs/product/overview.md`
  - `docs/product/prd/ai_sales_assistant_v2_prd.md`
  - `docs/architecture/data/v2-lead-research-data-model.md`
  - `docs/product/research/v1_closeout_2026_04_25.md`
  - `docs/delivery/tasks/task_v2_planning_baseline_update.md`

---

## 1. 决策目的

本文档用于冻结 V2.2 lead research 的最小边界，避免后续 agent 或开发线程把 V2 直接扩展成 CRM、联系人抓取、自动触达或大规模爬虫系统。

V2 当前产品形态已由 ADR-006 调整为“对话式专属销售 agent prototype”。因此本文档继续有效，但定位为 V2.2 联网线索研究、来源证据和联系方式边界。

本文档只冻结规划边界，不冻结数据库 schema、API contract、搜索 provider 或 implementation task queue。

---

## 2. 最终决策

### 2.1 V2.2 方向

V2.2 暂定为：

> **带来源证据的轻量线索研究**

目标用户为：

- 中小企业老板
- 销售负责人
- 商务负责人

V2.2 的目标是在 V2.1 对话式获客方向明确后，把“获客方向分析”推进到第一批可核验的候选公司 / 机构，而不是替用户自动销售。

### 2.2 允许主动联网 / 搜索

V2.2 允许系统主动联网 / 搜索。

当前默认搜索范围：

- 中文公开网页优先。
- 允许使用企业官网、政府 / 园区 / 协会公开页面、招投标 / 采购公告、新闻稿、行业媒体、招聘信息、公开平台页等来源。
- 搜索 provider 尚未冻结。

约束：

- 搜索过程必须能追踪 query、source、retrieved_at 和使用结果。
- 搜索失败时必须暴露失败原因，不能编造候选。
- 搜索 provider、缓存和数据保留策略后续需单独冻结。

### 2.3 允许具体公司 / 机构候选

V2.2 允许生成具体公司 / 机构候选。

候选进入正式结果前必须满足：

- 有名称。
- 至少有一个可追踪公开来源。
- 有匹配理由。
- 有置信度或不确定性说明。
- 有下一步人工验证动作。

无来源候选只能作为 runtime draft，不允许进入正式 `LeadResearchResult`。

### 2.4 联系方式受控展示

V2.2 可以处理公开来源中的联系方式，但联系方式不是核心卖点。

公司联系方式允许范围：

- 公司公开电话
- 公司公开邮箱
- 官网联系页
- 公司公开地址
- 公开客服入口

个人联系方式属于高风险信息。若后续展示，必须满足：

- 来源为公开页面。
- 记录来源 URL。
- 标记 `is_personal = true`。
- 标记人工验证要求。
- 不做批量抓取。
- 不做批量导出。
- 不做自动触达。

### 2.5 明确不做

V2.2 planning baseline 下明确不做：

- Web 前端
- 完整 CRM
- 自动邮件 / 短信 / 企微 / 电话触达
- 自动外呼
- 批量联系人抓取
- 批量联系人导出
- 大规模爬虫系统
- 第三方客户数据库采购接入
- 企业级团队协作审批流
- 正式商业化计费系统

### 2.6 后端 / runtime 边界保持不变

V2.2 继续沿用 V1 已验证的系统分层：

- Android 是控制入口。
- Backend 是正式业务系统和主真相层。
- Runtime / agent 负责 draft payload、搜索、工具调用和中间推理。
- Backend services 负责正式对象写回和业务边界裁决。

Runtime 不得绕过 backend services 直接写正式对象。

---

## 3. 原因

V1 已证明产品学习、获客分析和报告生成主闭环可行，但未达到 MVP。

V2.2 若继续只做抽象分析，差异化不足；若直接进入联系人抓取和自动触达，范围、合规和工程风险过高。

因此选择中间路线：

> **先做带来源证据的轻量线索研究。**

这条路线可以复用 V1 的 ProductProfile / LeadAnalysisResult / AnalysisReport / AgentRun 基线，同时新增来源证据、候选公司和联系方式的可追踪数据模型。

---

## 4. 后果

### 正向后果

- V2.2 与通用 LLM 客户端形成更清晰差异：结构化对象、来源证据、候选卡片和研究历史。
- 后续实现可以先做后端-only spike，不必先大改 Android。
- 搜索和联系方式风险被显式关进边界内。

### 代价

- V2.2 数据模型会明显比 V1 复杂。
- 搜索、来源质量、成本和延迟需要单独评估。
- 联系方式展示和保留策略仍需后续冻结。
- V2.2 仍不能直接视为 MVP。

---

## 5. 后续必须单独冻结

进入实现前，还需要单独冻结：

- V2 是否以 MVP 为目标。
- 搜索 provider。
- V2 domain/schema baseline。
- V2 backend API contract。
- 搜索结果和网页摘录的数据保留策略。
- ContactPoint 的个人信息展示、删除和脱敏策略。
- 成本上限、超时和 fallback 策略。
