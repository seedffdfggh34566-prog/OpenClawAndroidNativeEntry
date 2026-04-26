# AI 销售助手 V2 PRD

- 文档状态：Draft v0.3
- 更新日期：2026-04-26
- 阶段定位：V2 workspace-native sales agent prototype 定义，尚未冻结为 implementation task
- 关联文档：
  - `docs/product/prd/ai_sales_assistant_v1_prd.md`
  - `docs/product/research/v1_closeout_2026_04_25.md`
  - `docs/architecture/data/v2-sales-agent-data-model.md`
  - `docs/architecture/data/v2-lead-research-data-model.md`
  - `docs/adr/ADR-005-v2-lead-research-scope-and-search-boundary.md`
  - `docs/adr/ADR-006-v2-conversational-sales-agent-baseline.md`
- 用途：定义 V2 的产品北极星、阶段拆分、边界、关键能力、待决问题和后续拆解前提。

---

## 1. 文档目的

本文档用于承接 V1 closeout 之后的下一阶段规划，并将 V2 的产品北极星从“对话式专属销售 agent prototype”进一步升级为：

> **面向中小企业老板 / 销售负责人的 workspace-native sales agent prototype。**

V1 已经证明：

```text
产品学习 -> 产品画像确认 -> LeadAnalysis LLM -> 结构化报告 -> Android 真机复看
```

可以跑通，并且具备 demo-ready release candidate / learning milestone 价值。

但 V2 不应继续被 V1 的“生成一次获客分析报告”主路径牵引。V2 要回答的问题不是“如何 polish V1”，而是：

1. 用户是否愿意把“理解产品、判断获客方向、研究潜在客户、沉淀销售信息”持续交给一个专属销售 agent。
2. 系统是否能像软件工程 workspace 一样，把产品侧信息、客户挖掘侧信息、来源证据、候选排序、用户反馈和报告输出分层沉淀。
3. agent 是否能在不依赖单次 LLM 上下文窗口的情况下，通过结构化对象、Markdown projection 和 context pack 持续迭代客户挖掘质量。
4. 多轮研究后，如果后续候选客户比前序候选更可行，系统是否能更新 workspace 内的优先级榜单，并解释排序变化。
5. 最终结果是否能通过获客报告、候选卡片、验证任务或下一步建议，以用户容易理解的方式呈现。

本文档不是：

- 已冻结的开发任务
- 完整商业计划书
- 正式数据库 schema
- 完整 API contract
- 合规政策文件
- CRM / 自动触达 / 联系人抓取系统 PRD

---

## 2. 当前结论

V2 当前产品北极星调整为：

> **中小企业专属销售工作区 Agent：用户只管聊天和反馈，agent 负责理解产品、沉淀信息、研究候选客户、维护优先级，并持续提升获客质量。**

V2 不再只定义为“对话式销售分析 agent”，也不应退化为“获客报告生成器”。更准确地说：

- **Sales Workspace** 是 V2 的产品主形态。
- **Chat-first agent** 是用户入口和交互方式。
- **Structured objects + Markdown projection** 是长期信息沉淀方式。
- **Evidence-based research** 是 V2.2 的关键 agent 能力。
- **Candidate ranking board** 是客户挖掘结果的核心承载，而报告只是发布视图之一。
- **Feedback loop** 是让 agent 越用越懂该用户获客偏好的关键机制。

核心变化：

1. V1 的 `ProductProfile`、`LeadAnalysisResult`、`AnalysisReport`、`AgentRun` 不再决定 V2 产品主路径，只作为可复用资产。
2. V2 需要新增 `SalesWorkspace` 作为根对象，承载产品侧信息、获客方向、研究轮次、候选客户、来源证据、排序榜和用户反馈。
3. 对话仍然重要，但对话不是业务主存；对话应驱动 workspace 对象变化。
4. Markdown 不作为唯一主存，而是 agent-readable workspace projection；结构化对象仍是后端正式主真相。
5. 每次 agent 执行不应只生成一段回答，而应尽量生成可验证的 `WorkspacePatchDraft`，由 backend services / workspace kernel 裁决写回。
6. V2 先做 prototype，不直接进入 MVP。

当前仍未冻结：

- V2 是否最终进入 MVP。
- 是否需要正式云部署。
- 是否需要账号、多用户、租户隔离和权限。
- `SalesWorkspace` 正式 schema 和迁移策略。
- Markdown projection 的具体目录和同步规则。
- `ContextPack` / `WorkspacePatch` 的最小 schema。
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
- 个人 BD / 业务拓展负责人

这些用户通常具备以下特点：

- 对自己的业务熟，但不一定有系统化获客方法。
- 不想学习复杂 CRM、销售自动化系统或 prompt 工程。
- 想知道“我应该先找哪些客户方向”“为什么是这些客户”“下一步怎么验证”。
- 会在沟通中不断修正目标，例如排除行业、限定地区、调整客户规模、提高客单价要求。
- 没有成熟的数据团队或销售运营团队。
- 需要一个能持续理解上下文、沉淀信息并反复迭代的销售工作区，而不是一次性报告生成器。

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

V2 要进一步回答：

- 用户是否能用一句自然语言启动销售工作区。
- agent 是否能主动追问并形成结构化产品理解。
- agent 是否能维护当前获客方向、排除方向和假设。
- agent 是否能进行多轮客户挖掘，并把每轮研究结果沉淀到 workspace。
- agent 是否能把候选客户、来源证据、匹配理由和不确定性拆成可追踪对象。
- 如果后续挖掘出更可行的客户，系统是否能更新候选优先级榜，并解释为什么升降级。
- 用户反馈是否能进入下一轮研究和排序策略，而不是只停留在聊天记录里。
- 系统是否能生成适合用户复看的报告、候选卡片或人工验证任务。

也就是说，V2 的重点是：

> **把销售获客过程 workspace 化：产品理解、获客方向、客户挖掘、来源证据、候选排序、用户反馈和报告输出都应成为可迭代、可追踪、可复用的资产。**

---

## 5. 阶段划分

### 5.1 V2.1 Sales Workspace Kernel Prototype

目标：

> 验证最小销售工作区内核：用户通过 chat-first 入口表达业务，系统能形成产品理解、获客方向、候选排序雏形和可恢复 workspace 状态。

In Scope：

- `SalesWorkspace`
- `ConversationMessage`
- `ProductProfileRevision`
- `LeadDirectionVersion`
- `CandidateRankingBoard` 的最小雏形
- `ContextPack` 的最小雏形
- `WorkspacePatch` / `WorkspacePatchDraft` 的最小雏形
- `AgentRun(run_type = sales_agent_turn)`
- agent 主动追问
- 用户通过对话调整获客方向
- agent 基于 workspace 对象回答解释性问题
- Markdown workspace projection 的最小目录规则

Out of Scope：

- 主动联网 / 搜索
- 大规模具体公司候选
- 联系方式
- Web 前端
- 自动触达
- 正式云端 SaaS
- 完整 CRM

### 5.2 V2.2 Evidence-based Research Round

目标：

> 在用户确认获客方向后，agent 进行一轮或多轮轻量联网研究，生成有来源证据的候选客户，并更新候选优先级榜。

In Scope：

- `ResearchRound`
- `ResearchSource`
- `CompanyCandidate`
- `CandidateObservation`
- `CandidateScoreSnapshot`
- `CandidateRankingBoard`
- `FeedbackEvent` 的最小闭环
- `lead_research_graph` 或等价研究执行图
- 受控中文公开网页搜索
- 来源证据和不确定性
- 候选升降级解释

Out of Scope：

- 批量联系人抓取
- 批量联系人导出
- 自动邮件 / 短信 / 企微 / 电话触达
- 大规模爬虫系统
- 第三方客户数据库采购接入

### 5.3 V2.3 Persistent Sales Workspace MVP Gate

目标：

> 验证 persistent sales workspace 是否值得进入 MVP：agent 是否能长期复用历史研究、用户偏好、排除方向、候选状态和反馈，不断提高获客质量。

可能进入：

- `WorkspaceCommit`
- `AgentMemorySnapshot`
- 用户偏好
- 历史研究复用
- 候选状态管理
- 更强报告与销售动作建议
- 更稳定的 context pack compiler
- 是否进入 MVP 的正式判断

V2.3 不是“可有可无的后续功能”，而是 V2 的产品北极星验证点；V2.1 / V2.2 只是走向该北极星的最小闭环。

---

## 6. 产品范围

### 6.1 V2.1 In Scope

V2.1 必须覆盖：

1. **chat-first 销售工作区入口**
   - 用户通过对话框输入自然语言。
   - agent 可以追问、回答、总结、建议下一步。
   - 每轮消息应被持久化。

2. **产品侧信息沉淀**
   - 对话内容不直接等于业务真相。
   - 后端应沉淀 `ProductProfileRevision`，并能形成当前产品理解卡。

3. **获客方向沉淀**
   - agent 能生成初始获客方向。
   - 用户能通过对话排除行业、限定地区、调整客户规模或改变优先方向。
   - 调整应形成 `LeadDirectionVersion` 或等价结构化版本，而不是只存在于聊天记录。

4. **workspace projection**
   - 系统应能把当前产品理解、当前获客方向、待补充问题和用户偏好渲染为 agent-readable Markdown。
   - Markdown 是 projection，不是唯一主存。

5. **context pack**
   - 每次 agent turn 应基于当前任务生成最小上下文包。
   - context pack 应能避免把全部历史聊天塞进 LLM 上下文。

6. **解释型回答**
   - 用户可以问“为什么推荐这个方向”“哪个方向先做”“风险是什么”。
   - 回答应基于已沉淀对象，而不是每次从零自由发挥。

7. **Android 控制入口**
   - Android 仍是主控制入口。
   - V2.1 不做 Web 前端。

### 6.2 V2.2 In Scope

V2.2 才进入：

- 联网搜索
- 具体公司 / 机构候选
- 来源证据保存
- 候选公司卡片
- 候选观察事实
- 候选评分快照
- 候选优先级榜更新
- 用户反馈反哺下一轮研究
- 受控联系方式展示

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

> **chat-first + structured cards + workspace state**

不是纯聊天，也不是纯表单，也不是传统 CRM。

建议 Android 交互结构：

```text
主区域：用户与销售 agent 的对话
辅助区域：当前产品理解卡片
辅助区域：当前获客方向卡片
辅助区域：待回答问题 / 建议补充信息
辅助区域：候选客户优先级榜
V2.2 辅助区域：候选公司卡片、来源证据、排序变化和人工验证建议
```

关键原则：

- 对话是输入通道和交互界面。
- `SalesWorkspace` 是用户销售资产的容器。
- `ProductProfileRevision` 是正式产品理解版本。
- `LeadDirectionVersion` 是正式获客方向版本。
- `CandidateRankingBoard` 是客户挖掘结果的当前优先级视图。
- `AnalysisReport` 是发布视图，不是唯一结果载体。
- 用户必须能看到 agent 当前理解。
- 用户必须能通过对话纠正关键字段。
- agent 必须能解释当前方向和候选排序如何产生。

---

## 8. 数据与主真相原则

V2 继续沿用 V1 架构原则，但主对象从“报告链路”升级为“workspace 内核”：

- Android 是控制入口。
- 后端是正式业务系统。
- Runtime / Product Sales Agent execution layer 负责 draft payload、工具调用和中间推理。
- Backend services / workspace kernel 负责正式对象写回。
- 正式对象以结构化数据库对象为主真相。
- Markdown 作为 agent-readable workspace projection、报告或调试视图，不作为唯一主存。
- 每次 agent 执行应尽量产生 `WorkspacePatchDraft`，由后端校验后写入正式对象。

V2.1 首批建议对象：

- `SalesWorkspace`
- `ConversationMessage`
- `ProductProfileRevision`
- `LeadDirectionVersion`
- `CandidateRankingBoard` 的最小雏形
- `WorkspacePatch` / `WorkspacePatchDraft`
- `ContextPack`
- `AgentRun(run_type = sales_agent_turn)`

V2.2 再进入：

- `ResearchRound`
- `ResearchSource`
- `CompanyCandidate`
- `CandidateObservation`
- `CandidateScoreSnapshot`
- `ContactPoint`
- `FeedbackEvent`

V1 对象的定位：

- `ProductProfile`：可继续作为产品主档或 current projection，但不再单独代表完整 sales workspace。
- `LeadAnalysisResult`：可继续作为方向分析结果，但不承载客户候选库和排序历史。
- `AnalysisReport`：作为发布 / 复盘 / 导出视图，不作为客户挖掘主存。
- `AgentRun`：继续记录执行过程和输入输出谱系。

---

## 9. Runtime / Product Sales Agent 原则

V2 可以继续使用 LangGraph 作为当前默认 runtime 编排方向，但 LangGraph 不是产品主架构。

V2 的主架构应是：

```text
Sales Workspace Kernel
    -> ContextPack Compiler
    -> Agent Runtime / LangGraph
    -> WorkspacePatchDraft
    -> Backend validation / writeback
    -> Structured objects + Markdown projection
```

V2.1 建议新增或调整：

```text
sales_agent_turn_graph
```

职责：

- 读取 workspace context pack，而不是直接读取全部历史消息。
- 判断用户意图。
- 决定是追问、回答、更新产品理解、调整获客方向，还是准备进入研究。
- 返回 typed draft payload / `WorkspacePatchDraft`。

V2.2 建议新增：

```text
lead_research_graph
```

职责：

- 基于确认方向生成搜索 query。
- 调用受控搜索工具。
- 选择来源。
- 生成候选草稿。
- 生成候选 observation。
- 给候选评分并提出 ranking delta。
- 校验候选来源覆盖。
- 返回 `WorkspacePatchDraft`。

边界：

- LangGraph 不直接写正式数据库对象。
- LangGraph checkpoint 不是业务记忆主存。
- Runtime 不自行决定联系方式合规策略。
- 正式写回仍由 backend services / workspace kernel 裁决。

---

## 10. Prototype 存储路线

V2 已明确先做 prototype，不直接做 MVP。

当前建议：

- V2.1 先做 backend-only Sales Workspace Kernel prototype。
- 第一阶段可以先用 Pydantic schema + JSON fixture / file-backed store + Markdown projection 验证对象关系。
- 对象关系稳定后再进入 SQLite / Alembic migration。
- schema 设计必须按未来可迁云设计。
- 不允许把 agent memory 只存在 prompt、Markdown 文件、runtime checkpoint 或 SDK session 中。

MVP 前必须重新评估：

- 云端部署
- Postgres
- 用户 / 工作区 / 权限
- 数据保留和删除
- 成本治理和监控
- search / crawl provider
- 联系方式展示和保留策略

---

## 11. 成功标准草案

V2.1 prototype 成功应满足：

- 用户能通过一句自然语言启动一个 `SalesWorkspace`。
- agent 能主动提出 3 到 5 个关键追问。
- 系统能形成第一版产品理解和获客方向。
- 用户能通过对话调整获客方向。
- 系统能把调整沉淀为结构化版本。
- 系统能生成当前 workspace 的 Markdown projection。
- 系统能生成面向当前任务的 context pack。
- agent 能解释当前推荐方向的原因。
- 对话、AgentRun、WorkspacePatch 和正式对象变更可追溯。

V2.2 prototype 成功应满足：

- 在确认方向后生成一轮 `ResearchRound`。
- 生成 10 到 20 个候选公司 / 机构。
- 每个正式候选至少有 1 个可追踪公开来源。
- 每个候选有匹配理由、不确定性和观察事实。
- 系统能对候选生成评分快照。
- 系统能维护候选优先级榜。
- 如果新候选优于旧候选，系统能更新排序并解释升降级原因。
- 无来源候选不进入正式结果。
- 联系方式默认人工验证，不自动触达。

V2.3 MVP gate 成功应满足：

- 用户愿意第二天回来继续使用同一个 sales workspace。
- 用户反馈能影响下一轮客户挖掘方向和候选排序。
- 历史研究可以被复用，而不是每轮从零开始。
- agent 的客户挖掘质量随 workspace 信息沉淀而提升。

---

## 12. 待决问题

进入实现前至少需要明确：

1. `SalesWorkspace` 的最小字段和生命周期。
2. `WorkspacePatchDraft` 的最小 schema。
3. `ContextPack` 的最小 schema 和 token budget 策略。
4. Markdown projection 的目录结构、frontmatter 和同步规则。
5. V2.1 是否先采用 file-backed prototype，再进入 SQLite。
6. `LeadDirectionVersion` 是否独立对象。
7. `CandidateRankingBoard` 和 `CandidateScoreSnapshot` 是否进入 V2.1 最小雏形。
8. `sales_agent_turn_graph` 的最小 draft schema。
9. V2.2 搜索 provider。
10. 个人联系方式是否进入 V2.2 正式对象。
11. V2.3 是否作为 MVP 前置阶段。

---

## 13. 推荐下一步

推荐顺序：

1. 创建并完成 `task_v2_sales_workspace_direction_update.md`，将 V2 北极星更新为 workspace-native sales agent。
2. 新增 `docs/architecture/workspace/sales-workspace-kernel.md`。
3. 新增 `docs/architecture/workspace/workspace-object-model.md`。
4. 新增 `docs/architecture/workspace/markdown-projection.md`。
5. 新增 `docs/architecture/workspace/context-pack-compiler.md`。
6. 创建 V2.1 backend-only Sales Workspace Kernel prototype task。
7. 先实现 Pydantic schema、ranking engine、Markdown projection 和 context pack compiler 的无 DB 原型。
8. 原型跑通后，再决定 SQLite migration、API 和 Android 最小接入。
