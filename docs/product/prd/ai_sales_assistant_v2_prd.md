# AI 销售助手 V2 PRD

- 文档状态：Draft v0.2
- 更新日期：2026-04-25
- 阶段定位：V2 对话式专属销售 agent prototype 定义，尚未冻结为 implementation task
- 关联文档：
  - `docs/product/prd/ai_sales_assistant_v1_prd.md`
  - `docs/product/research/v1_closeout_2026_04_25.md`
  - `docs/architecture/data/v2-sales-agent-data-model.md`
  - `docs/architecture/data/v2-lead-research-data-model.md`
  - `docs/adr/ADR-005-v2-lead-research-scope-and-search-boundary.md`
  - `docs/adr/ADR-006-v2-conversational-sales-agent-baseline.md`
- 用途：定义 V2 的产品方向、阶段拆分、边界、关键能力、待决问题和后续拆解前提。

---

## 1. 文档目的

本文档用于承接 V1 closeout 之后的下一阶段规划。

V1 已经证明：

```text
产品学习 -> 产品画像确认 -> LeadAnalysis LLM -> 结构化报告 -> Android 真机复看
```

可以跑通，并且具备 demo-ready release candidate / learning milestone 价值。

V2 要回答的问题不是“继续 polish V1”，而是：

1. 用户是否需要一个能持续理解业务的专属销售 agent。
2. 用户是否能通过对话完成产品理解、获客方向分析和方向调整。
3. 系统是否能把对话沉淀为结构化业务对象，而不是一次性聊天记录。
4. 在确认方向后，系统是否能进一步做带来源证据的轻量线索研究。

本文档不是：

- 已冻结的开发任务
- 完整商业计划书
- 正式数据库 schema
- 完整 API contract
- 合规政策文件
- CRM / 自动触达 / 联系人抓取系统 PRD

---

## 2. 当前结论

V2 暂定方向调整为：

> **面向中小企业老板 / 销售负责人的对话式专属销售 agent prototype。**

V2 不再只定义为“轻量线索研究工具”。更准确地说：

- 对话式专属销售 agent 是 V2 的产品形态。
- 轻量线索研究是 agent 在 V2.2 阶段具备的一项核心能力。
- 来源证据、候选公司和联系方式边界仍沿用 ADR-005。
- V2 先做 prototype，不直接进入 MVP。

核心变化：

1. 用户通过 Android 内的对话框与销售 agent 交互。
2. agent 主动追问产品、客户、场景、地区、客单价、交付方式和成交约束。
3. 用户可以实时通过对话调整获客方向。
4. 系统将对话沉淀为 `ProductProfileRevision`、获客方向版本和分析结果，而不是只保存聊天文本。
5. 在确认方向后，后续阶段再进入带来源证据的联网线索研究。

当前仍未冻结：

- V2 是否最终进入 MVP。
- 是否需要正式云部署。
- 是否需要账号、多用户、租户隔离和权限。
- 搜索 provider。
- 个人联系方式的展示、保存、删除和脱敏策略。
- V2 API contract。
- V2 implementation task queue。

---

## 3. 目标用户

### 3.1 核心用户

V2 优先服务：

- 中小企业老板
- 创始人
- 销售负责人
- 商务负责人

这些用户通常具备以下特点：

- 对自己的业务熟，但不一定有系统化获客方法。
- 想知道“我应该先找哪些客户方向”以及“为什么”。
- 会在沟通中不断修正自己的目标，例如排除行业、限定地区、调整客户规模。
- 没有成熟的数据团队或销售运营团队。
- 更需要一个能持续理解上下文的销售助手，而不是一次性报告生成器。

### 3.2 暂不优先用户

V2 暂不优先覆盖：

- 大型企业复杂销售组织
- 强 CRM 工作流团队
- 以大规模联系人采集为核心诉求的团队
- 以自动外呼、自动邮件、自动企微触达为核心诉求的团队
- 需要严格法务、审计、权限和数据保留策略的企业客户

---

## 4. V2 核心问题

V1 能回答：

- 我的产品适合哪些行业。
- 哪些客户类型可能优先。
- 有哪些场景、风险和下一步建议。

V2.1 要先回答：

- 用户能否通过对话让 agent 理解自己的产品和销售目标。
- agent 能否主动追问缺失信息。
- 用户能否通过对话实时调整获客方向。
- agent 能否基于当前已沉淀对象回答“为什么推荐这个方向”。
- 每次调整是否能形成可追溯版本，而不是覆盖掉历史。

V2.2 再进一步回答：

- 在确认方向后，第一批可以研究的具体公司是谁。
- 为什么这些公司可能匹配。
- 这个判断来自哪些公开来源。
- 下一步人工验证动作是什么。

也就是说，V2 的重点是：

> **把销售思考过程对象化、版本化、证据化、可对话迭代化。**

---

## 5. 阶段划分

### 5.1 V2.1 Conversational Sales Agent Prototype

目标：

> 用户可以通过对话完成产品理解、获客方向分析和方向迭代。

In Scope：

- `SalesAgentSession`
- `ConversationMessage`
- `ProductProfileRevision`
- 获客方向版本或等价结构化分析版本
- `AgentRun(run_type = sales_agent_turn)`
- agent 主动追问
- 用户通过对话调整获客方向
- agent 基于已有对象回答解释性问题

Out of Scope：

- 主动联网 / 搜索
- 具体公司候选
- 联系方式
- Web 前端
- 自动触达
- 正式云端 SaaS

### 5.2 V2.2 Evidence-based Lead Research

目标：

> 在用户确认获客方向后，agent 进行轻量联网研究，生成带来源证据的候选公司。

In Scope：

- `LeadResearchResult`
- `ResearchSource`
- `CompanyCandidate`
- `ContactPoint`
- `lead_research_graph`
- 受控中文公开网页搜索
- 来源证据和不确定性

Out of Scope：

- 批量联系人抓取
- 批量联系人导出
- 自动邮件 / 短信 / 企微 / 电话触达
- 大规模爬虫系统

### 5.3 V2.3 Persistent Sales Agent Workspace

目标：

> agent 具备长期工作区能力，可以复用历史研究、用户偏好、排除方向和候选状态。

可能进入：

- `AgentMemorySnapshot`
- 用户偏好
- 历史研究复用
- 候选状态管理
- 更强报告与销售动作建议
- 是否进入 MVP 的正式判断

---

## 6. 产品范围

### 6.1 V2.1 In Scope

V2.1 必须覆盖：

1. **对话式销售 agent 会话**
   - 用户通过对话框输入自然语言。
   - agent 可以追问、回答、总结、建议下一步。
   - 每轮消息应被持久化。

2. **产品理解沉淀**
   - 对话内容不直接等于业务真相。
   - 后端应沉淀 `ProductProfile` 和 `ProductProfileRevision`。

3. **获客方向分析与调整**
   - agent 能生成初始获客方向。
   - 用户能通过对话排除行业、限定地区、调整客户规模或改变优先方向。
   - 调整应形成版本或可追溯结构，而不是只存在于聊天记录。

4. **解释型回答**
   - 用户可以问“为什么推荐这个方向”、“哪个方向先做”、“风险是什么”。
   - 回答应基于已沉淀对象，而不是每次从零自由发挥。

5. **Android 控制入口**
   - Android 仍是主控制入口。
   - V2.1 不做 Web 前端。

### 6.2 V2.2 In Scope

V2.2 才进入：

- 联网搜索
- 具体公司 / 机构候选
- 来源证据保存
- 受控联系方式展示
- 候选公司卡片

### 6.3 Out of Scope

V2 全阶段当前不进入：

- Web 前端
- 完整 CRM
- 自动邮件 / 短信 / 企微 / 电话触达
- 自动外呼
- 批量联系人抓取
- 批量导出联系人库
- 购买第三方客户数据库
- 大规模爬虫系统
- 团队协作审批流
- 企业权限和审计体系
- 完整商业化计费系统

---

## 7. 交互形态

V2 应采用：

> **chat-first + structured cards**

不是纯聊天，也不是纯表单。

建议 Android 交互结构：

```text
主区域：用户与销售 agent 的对话
辅助区域：当前产品理解卡片
辅助区域：当前获客方向卡片
辅助区域：待回答问题 / 建议补充信息
V2.2 辅助区域：候选公司卡片和来源证据
```

关键原则：

- 对话是输入通道和交互界面。
- ProductProfile / ProductProfileRevision 是正式产品理解。
- 获客方向版本或 LeadAnalysisResult 是正式分析沉淀。
- 用户必须能看到 agent 当前理解。
- 用户必须能通过对话纠正关键字段。
- agent 必须能解释当前方向如何产生。

---

## 8. 数据与主真相原则

V2 继续沿用 V1 架构原则：

- Android 是控制入口。
- 后端是正式业务系统。
- Runtime / agent 负责 draft payload、工具调用和中间推理。
- Backend services 负责正式对象写回。
- 正式对象以结构化数据库对象为主真相。
- Markdown 只作为 agent-friendly context projection、报告或导出视图，不作为主存。

V2.1 首批建议对象：

- `SalesAgentSession`
- `ConversationMessage`
- `ProductProfileRevision`
- `LeadDirectionVersion` 或等价结构化方向版本
- `AgentRun(run_type = sales_agent_turn)`
- 可选 `AgentContextPack`

V2.2 再进入：

- `LeadResearchResult`
- `ResearchSource`
- `CompanyCandidate`
- `ContactPoint`

---

## 9. Runtime / Agent 原则

V2 继续使用 LangGraph 作为当前默认 runtime 编排方向。

V2.1 建议新增：

```text
sales_agent_turn_graph
```

职责：

- 读取会话上下文和结构化对象。
- 判断用户意图。
- 决定是追问、回答、更新产品画像、调整获客方向，还是准备进入研究。
- 返回 typed draft payload。

V2.2 建议新增：

```text
lead_research_graph
```

职责：

- 基于确认方向生成搜索 query。
- 调用受控搜索工具。
- 选择来源。
- 生成候选草稿。
- 校验候选来源覆盖。

边界：

- LangGraph 不直接写正式数据库对象。
- LangGraph checkpoint 不是业务记忆主存。
- Runtime 不自行决定联系方式合规策略。
- 正式写回仍由 backend services 裁决。

---

## 10. Prototype 存储路线

V2 已明确先做 prototype，不直接做 MVP。

当前建议：

- V2.1 prototype 继续本地后端沉淀。
- SQLite 可继续作为 prototype 存储基线。
- schema 设计必须按未来可迁云设计。
- 不允许把 agent memory 只存在 prompt、Markdown 文件、runtime checkpoint 或 SDK session 中。

MVP 前必须重新评估：

- 云端部署
- Postgres
- 用户 / 工作区 / 权限
- 数据保留和删除
- 成本治理和监控

---

## 11. 成功标准草案

V2.1 prototype 成功应满足：

- 用户能通过对话完成第一版产品理解。
- agent 能主动提出 3 到 5 个关键追问。
- 用户能通过对话调整获客方向。
- 系统能把调整沉淀为结构化版本。
- agent 能解释当前推荐方向的原因。
- 对话、AgentRun 和正式对象变更可追溯。

V2.2 prototype 成功应满足：

- 在确认方向后生成 10 到 20 个候选公司 / 机构。
- 每个候选至少有 1 个可追踪公开来源。
- 每个候选有匹配理由和不确定性。
- 无来源候选不进入正式结果。
- 联系方式默认人工验证，不自动触达。

---

## 12. 待决问题

进入实现前至少需要明确：

1. V2.1 是否采用 `LeadDirectionVersion` 独立对象，还是复用 `LeadAnalysisResult` 版本。
2. `SalesAgentSession` 的状态集合。
3. `ConversationMessage.message_type` 枚举。
4. `sales_agent_turn_graph` 的最小 draft schema。
5. 是否首批持久化 `AgentContextPack`。
6. V2.1 是否继续 SQLite。
7. V2.2 搜索 provider。
8. 个人联系方式是否进入 V2.2 正式对象。
9. V2.3 是否作为 MVP 前置阶段。

---

## 13. 推荐下一步

推荐顺序：

1. 冻结 V2.1 conversational sales agent backend contract 草案。
2. 冻结 V2 sales agent data model v0.2。
3. 设计 `sales_agent_turn_graph` draft schema。
4. 创建 V2.1 backend-only prototype task。
5. 完成 V2.1 后，再恢复 V2.2 lead research provider 和来源证据实现讨论。
