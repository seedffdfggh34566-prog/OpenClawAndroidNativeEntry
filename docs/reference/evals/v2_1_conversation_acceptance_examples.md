# V2.1 Conversation Acceptance Examples

日期：2026-04-27

## 1. Purpose

本文件定义 V2.1 conversational product experience 的 5 个中文验收样例。

这些样例用于后续 backend-first deterministic implementation。它们不是 LLM eval，也不要求 V2.2 search / ContactPoint。

每个样例都必须验证：

- 初始 chat input。
- Product Sales Agent 追问 3 到 5 个关键问题。
- 可审阅的 `ProductProfileRevision` draft。
- 可审阅的 `LeadDirectionVersion` draft。
- 基于 workspace objects 的解释型回答。
- ConversationMessage / AgentRun / ContextPack / DraftReview / WorkspaceCommit / formal object refs。

## 2. Sample A: 工业设备维保软件

Initial input:

```text
我们做工业设备维保软件，帮工厂减少停机时间，想找第一批客户。
```

Expected clarifying questions:

1. 主要覆盖哪些设备类型，例如 CNC、注塑机、空压机还是产线设备？
2. 目标客户是工厂设备部、维保服务商，还是设备厂商售后团队？
3. 当前优先服务哪个地区？
4. 客户通常多大规模，是否已有 ERP / MES / 设备台账？
5. 哪些行业或客户类型暂时不想优先做？

Expected `ProductProfileRevision`:

- product category: 工业设备维保 / 预测性维护软件
- target customers: 制造业工厂设备部、维保服务商
- pain points: 停机损失、维修响应慢、设备台账分散
- value props: 降低停机时间、提高维保计划性

Expected `LeadDirectionVersion`:

- priority industries: 制造业、设备密集型工厂
- regions: 用户回答中的地区；未回答时标记 open question
- company sizes: 中小制造企业 / 多设备产线
- excluded industries: 用户指定的排除项

Expected explanation:

- 说明为什么优先设备密集型制造企业。
- 引用当前 product profile 的停机时间痛点和当前 lead direction 的行业 / 规模字段。

Expected refs:

- `ConversationMessage:<user>`
- `AgentRun:<sales_agent_turn>`
- `ContextPack:<id>`
- `WorkspacePatchDraftReview:<id>`
- `WorkspaceCommit:<id>`
- `ProductProfileRevision:<id>`
- `LeadDirectionVersion:<id>`

## 3. Sample B: 本地企业培训服务

Initial input:

```text
我们给本地企业做销售和管理培训，主要是线下课，想知道先找什么客户。
```

Expected clarifying questions:

1. 课程更偏销售技能、管理能力、还是新员工培训？
2. 目前服务哪个城市或省份？
3. 客户通常是老板、HR、销售负责人还是培训负责人？
4. 客单价和交付周期大概是多少？
5. 哪些行业或企业规模不适合优先做？

Expected product profile:

- product category: 企业培训服务
- target customers: 本地中小企业、HR、销售负责人、老板
- pain points: 销售转化低、管理能力不足、培训体系不稳定
- constraints: 线下交付、地域半径明显

Expected lead direction:

- regions: 本地城市 / 省份
- priority industries: 高人员流动或销售团队驱动行业
- company sizes: 20-300 人企业
- excluded customer types: 超大型集团、纯线上培训需求

Expected explanation:

- 说明为什么地域和决策人是优先筛选条件。
- 引用线下交付约束和目标客户类型。

## 4. Sample C: 中小企业财税 SaaS

Initial input:

```text
我们做中小企业财税 SaaS，帮老板看现金流、发票和税务风险。
```

Expected clarifying questions:

1. 产品主要面向老板、财务负责人，还是代账公司？
2. 是否已有发票、银行流水或 ERP 对接能力？
3. 目标客户年营收或员工规模大概是多少？
4. 优先覆盖哪些地区？
5. 是否排除强监管行业或已有大型财务系统的企业？

Expected product profile:

- product category: 财税 / 现金流 SaaS
- target customers: 中小企业老板、财务负责人、代账服务商
- pain points: 现金流不透明、发票管理分散、税务风险难以及时发现

Expected lead direction:

- customer types: 有基础财务数字化但缺少经营视角的中小企业
- priority constraints: 发票 / 流水数据可接入
- excluded customer types: 已重度使用大型 ERP 的集团客户

Expected explanation:

- 说明为什么老板和财务负责人是优先访谈对象。
- 引用现金流和税务风险痛点。

## 5. Sample D: 园区招商服务

Initial input:

```text
我们帮产业园区做招商运营，想找有扩租和选址需求的企业。
```

Expected clarifying questions:

1. 园区主打什么产业，例如智能制造、生物医药、软件服务还是跨境电商？
2. 当前可招商区域在哪里？
3. 目标企业更看重租金、政策、人才，还是供应链配套？
4. 想优先找初创企业、成长型企业，还是成熟企业分支机构？
5. 是否有排除行业或最低面积 / 人数要求？

Expected product profile:

- product category: 产业园区招商运营服务
- target customers: 有选址、扩租、政策匹配需求的企业
- pain points: 选址成本高、政策不清、配套不匹配

Expected lead direction:

- regions: 园区所在区域
- priority industries: 园区主导产业
- company sizes: 有扩租 / 选址需求的成长型企业
- priority constraints: 匹配园区产业定位和空间条件

Expected explanation:

- 说明为什么必须先限定园区产业定位和空间条件。
- 引用 product profile 的政策 / 配套价值。

## 6. Sample E: 制造业外包服务

Initial input:

```text
我们给制造企业提供外包生产和装配服务，适合小批量、多品种订单。
```

Expected clarifying questions:

1. 主要外包能力是装配、机加工、钣金、电子制造还是包装？
2. 最适合的订单量和交付周期是什么？
3. 目前服务地区和可承接产能在哪里？
4. 目标客户是品牌方、贸易商，还是制造企业的供应链部门？
5. 哪些产品类型、行业或质量要求暂时不承接？

Expected product profile:

- product category: 制造业外包生产 / 装配服务
- target customers: 小批量多品种订单的品牌方、贸易商、制造企业
- pain points: 自建产能成本高、订单波动、交付弹性不足

Expected lead direction:

- priority industries: 小批量多品种硬件 / 设备 / 消费品制造
- company sizes: 有稳定订单但不适合自建完整产线的企业
- excluded industries: 用户回答中的不承接类型

Expected explanation:

- 说明为什么小批量多品种客户更匹配。
- 引用产能弹性和交付周期约束。

## 7. Acceptance Rules

For each sample, a passing V2.1 conversational implementation must:

- return 3 to 5 useful Chinese clarifying questions before over-committing when input is incomplete;
- generate a reviewable `ProductProfileRevision` draft when product information is sufficient;
- generate or update a `LeadDirectionVersion` when direction information is supplied;
- return an explanation grounded in current workspace objects;
- preserve trace refs across message, run, context pack, draft review, patch commit, and changed objects;
- avoid generating V2.2 `ResearchSource`, `CompanyCandidate`, `ContactPoint`, CRM, or search payloads.
