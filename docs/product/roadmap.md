# Product Roadmap

更新时间：2026-04-27

## 当前阶段

当前路线已从 V1 implementation 切换为：

> **V2 planning baseline：workspace-native sales agent**

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
- V2.1：Sales Workspace Kernel prototype 已完成 backend-only v0；下一步进入 API contract 与 persistence decision。
- V2.2：Evidence-based Research Round，确认方向后进入联网 / 中文公开网页搜索，生成候选客户、来源证据、候选观察事实、评分快照和 ranking delta。
- V2.3：Persistent Sales Workspace MVP gate，验证长期记忆、历史研究复用、候选状态管理、用户反馈闭环和是否进入 MVP。
- 输出形态：会话消息、产品画像版本、获客方向版本、研究轮次、候选客户、来源证据、候选排序榜、报告 / 验证建议。
- 联系方式：V2.2 才进入，受控展示、必须可溯源、默认人工验证、不自动触达。

---

## 近期推荐顺序

1. 完成 post-v0 文档入口同步。
2. 冻结 Sales Workspace Kernel backend API contract v0。
3. 决策 persistence baseline：继续 in-memory / JSON fixture、进入 SQLite / Alembic，或延后 DB。
4. contract 与 persistence 决策完成后，再实现 backend API v0。
5. backend API 可用后，再实现 Android read-only workspace view。
6. API、写回边界和 persistence 稳定后，再接 Runtime / LangGraph WorkspacePatchDraft。
7. V2.2 再恢复 lead research provider、来源证据、候选评分和联系方式实现讨论。
8. V2.2 用 5 到 10 个真实中文业务样例评估候选质量、来源质量、排序解释、成本和耗时。

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
- 未冻结 API contract / persistence decision 前直接做 V2 schema / migration
- 未定义来源证据和候选评分前直接做候选客户库

上述内容只有在 V2 PRD、ADR 和 task queue 明确后才能重新进入讨论。

---

## Phase Exit Criteria

V2 planning baseline 退出条件：

- V2 PRD v0.3 明确 workspace-native sales agent 北极星。
- ADR-006 更新为 workspace-native sales agent baseline。
- `docs/architecture/workspace/sales-workspace-kernel.md` 明确 Sales Workspace Kernel 分层。
- `docs/architecture/workspace/workspace-object-model.md` 明确 `SalesWorkspace`、`ResearchRound`、`CompanyCandidate`、`CandidateObservation`、`CandidateScoreSnapshot`、`CandidateRankingBoard`、`WorkspacePatch`、`ContextPack` 等最小对象边界。
- `docs/architecture/workspace/markdown-projection.md` 明确 Markdown projection 不是主存，并定义最小目录结构。
- `docs/architecture/workspace/context-pack-compiler.md` 明确 context pack 编译策略和 token budget 原则。
- `_active.md` 明确 post-v0 task queue：API contract -> persistence decision -> backend API -> Android read-only -> Runtime integration。

在 API contract 与 persistence decision 完成前，不应自动开始后端 route、DB migration、Android 或 Runtime integration。
