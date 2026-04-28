# Product Roadmap

更新时间：2026-04-28

## 当前阶段

当前路线已从 V1 implementation 切换为：

> **V2.1 validated prototype path completed；V2.1 product milestone remains open under planning control**

V1 已冻结为 demo-ready release candidate / learning milestone，不继续追加 V1 功能，不包装为 MVP。

当前 V2 不再只以“对话式销售分析 agent”为北极星，而是升级为：

> **中小企业专属销售工作区 Agent：用户只管聊天和反馈，agent 负责理解产品、沉淀信息、研究候选客户、维护优先级，并持续提升获客质量。**

---

## V2 产品北极星

V2 的核心产品形态为：

> **Sales Workspace + Chat-first Agent + Structured Cards + Evidence-based Candidate Ranking**

当前假设：

- 目标用户：中小企业老板 / 销售负责人 / 商务负责人。
- 前端方向：Android 控制入口，不做 Web 前端。
- V2.1 workspace/kernel engineering baseline：Sales Workspace Kernel、Draft Review ID flow、Postgres / Alembic persistence chain、Draft Review audit persistence 已完成。
- V2.1 validated prototype path：chat-first Runtime design、contract examples、trace persistence、backend prototype、Android chat-first UI、demo runbook、backend-level 5-sample conversational acceptance 和 Tencent TokenHub LLM runtime prototype 已验证；这不等于完整 V2.1 product milestone 已关闭。
- V2.2：Evidence-based Research Round，确认方向后进入联网 / 中文公开网页搜索，生成候选客户、来源证据、候选观察事实、评分快照和 ranking delta。
- V2.3：Persistent Sales Workspace MVP gate，验证长期记忆、历史研究复用、候选状态管理、用户反馈闭环和是否进入 MVP。
- 输出形态：会话消息、产品画像版本、获客方向版本、研究轮次、候选客户、来源证据、候选排序榜、报告 / 验证建议。
- 联系方式：V2.2 才进入，受控展示、必须可溯源、默认人工验证、不自动触达。

---

## 近期推荐顺序

1. V2.1 workspace/kernel engineering baseline closeout 已完成。
2. V2.1 deterministic chat-first demo flow closeout 已完成，但不等于完整 V2.1 conversational product experience。
3. PRD Acceptance Traceability、V2.1 conversational completion scope、5 个中文验收样例和 implementation queue 已补齐。
4. Backend-level V2.1 conversational acceptance、Android polish、真机端到端验收和 PRD Acceptance final review 已完成，但仅证明 validated prototype path。
5. 当前项目状态以 `docs/product/project_status.md` 为准；V2.1 continuation package 可由规划层继续开放。
6. V2.2 implementation 前，不直接接正式 LangGraph、联网搜索、ContactPoint 或 Android 扩展；V2.1 LLM runtime 仅作为 explicit-flag prototype。
7. 后续若进入 V2.2，应先做 evidence/search/contact 的 docs-level boundary planning。

---

## 当前不排入路线

- Web 前端
- 完整 CRM
- 自动触达
- 批量联系人抓取
- 批量联系人导出
- 大规模爬虫系统
- 正式云端 SaaS 部署
- 多用户 / 租户 / 权限实现
- Android 大规模聊天 UI 改造
- 未冻结正式 Runtime / LangGraph design 前把 LLM prototype 升级为 production runtime
- 未定义来源证据和候选评分前直接做候选客户库

上述内容只有在 V2 PRD、ADR 和 task queue 明确后才能重新进入讨论。

---

## Phase Exit Criteria

V2.1 engineering baseline 退出条件：

- V2 PRD v0.3 明确 workspace-native sales agent 北极星。
- ADR-006 更新为 workspace-native sales agent baseline。
- `docs/architecture/workspace/sales-workspace-kernel.md` 明确 Sales Workspace Kernel 分层。
- `docs/architecture/workspace/workspace-object-model.md` 明确 `SalesWorkspace`、`ResearchRound`、`CompanyCandidate`、`CandidateObservation`、`CandidateScoreSnapshot`、`CandidateRankingBoard`、`WorkspacePatch`、`ContextPack` 等最小对象边界。
- `docs/architecture/workspace/markdown-projection.md` 明确 Markdown projection 不是主存，并定义最小目录结构。
- `docs/architecture/workspace/context-pack-compiler.md` 明确 context pack 编译策略和 token budget 原则。
- `_active.md` 明确 post-v0 task queue：API contract -> persistence decision -> backend API -> Android read-only -> Runtime integration。
- Postgres / Alembic persistence chain、Draft Review audit persistence 和 Android Draft Review ID flow 已进入 main。

上述工程基线已完成。以下条目证明 V2.1 validated prototype path 已通过，不应被解释为完整 V2.1 product milestone 已关闭：

- chat-first 输入如何进入 Runtime 已定义。（done）
- Product Sales Agent 如何基于 ContextPack 生成 `WorkspacePatchDraft` 已定义。（done）
- `ProductProfileRevision` 与 `LeadDirectionVersion` 的最小 chat-first flow 已定义。（done）
- `ConversationMessage`、`AgentRun`、`DraftReview`、`WorkspaceCommit` 的追踪关系已定义。（done）
- chat-first contract examples 已补齐。（done）
- backend prototype 已能形成 ConversationMessage / AgentRun / DraftReview / WorkspaceCommit trace。（done）
- Android 已能承接 chat-first 输入与审阅闭环。（done）
- V2.1 product experience demo runbook 已补齐。（done，deterministic demo flow）
- V2.1 product experience early closeout 已完成。（done / corrected）
- PRD Acceptance Traceability 已完成。（done）
- V2.1 conversational completion scope 已完成。（done）
- 5 个中文业务验收样例已完成。（done）
- V2.1 conversational implementation queue 已完成。（done）
- 主动追问 3 到 5 个关键问题 backend prototype。（done）
- 基于 workspace objects 的解释型回答 backend prototype。（done）
- 5 个中文业务样例 product profile extraction。（done）
- 中文获客方向调整 deterministic runtime。（done）
- 5 个中文业务样例 backend e2e acceptance。（done）
- Android conversation polish / device acceptance。（done）
- PRD Acceptance final review。（done）
- V2.1 product experience final closeout。（done）
- Tencent TokenHub LLM runtime boundary、provider baseline、structured output contract、backend prototype、live eval、docs sync 和 closeout。（done，explicit dev flag）

V2.1 product milestone 仍开放于规划控制下。V2.2 可以进入 docs-level planning；implementation 前仍不应直接接正式 LangGraph、search provider、Android 扩展或 CRM/contact。
