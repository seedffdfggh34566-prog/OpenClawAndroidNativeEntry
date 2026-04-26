# V2 Sales Workspace Kernel v0 Scope

- 文档状态：Draft v0.1
- 更新日期：2026-04-26
- 阶段定位：Sales Workspace Kernel backend-only prototype 的强制范围收敛文档
- 建议路径：`docs/architecture/workspace/workspace-kernel-v0-scope.md`

---

## 1. 目的

本文档用于防止 Sales Workspace Kernel 第一版实现范围失控。

v0 不是 MVP，不是 API contract，不是数据库 schema，不是 Android UI，也不是 agent runtime 实现。

v0 只做一个 backend-only 状态机，用最小代码证明：

> 多轮客户挖掘后，第二轮更优候选可以基于证据超过第一轮候选，并生成可解释 ranking delta，同时被 Markdown projection 和 ContextPack 正确反映。

---

## 2. v0 In Scope

v0 允许实现：

1. Pydantic schema。
2. in-memory / JSON fixture workspace state。
3. WorkspacePatch apply。
4. WorkspaceCommit 简单记录。
5. ResearchSource。
6. CompanyCandidate。
7. CandidateObservation。
8. deterministic RankingEngine。
9. CandidateRankingBoard 派生生成。
10. RankingDelta。
11. Markdown projection，只渲染，不回写。
12. ContextPackCompiler，只支持 `task_type = research_round`。
13. pytest 端到端验证。

---

## 3. v0 Out of Scope

v0 明确不做：

- FastAPI endpoint。
- SQLAlchemy ORM。
- Alembic migration。
- SQLite schema change。
- Postgres。
- pgvector。
- Android UI。
- LangGraph graph。
- 真实 LLM。
- 联网搜索。
- 搜索 provider。
- URL fetch verification。
- source content hash。
- CRM pipeline。
- ContactPoint。
- 自动触达。
- 邮件 / 电话 / 企微 / 短信。
- 多用户 / 权限 / 租户。
- 真实 Git commit / branch / rollback。
- Markdown parse-back。
- embedding / semantic retrieval。
- 复杂 fuzzy candidate merge。
- 正式 AnalysisReport。
- ConversationMessage 持久化。
- AgentRun 集成。

---

## 4. v0 必须实现的对象

v0 必须实现：

```text
SalesWorkspace
ProductProfileRevision
LeadDirectionVersion
ResearchRound
ResearchSource
CompanyCandidate
CandidateObservation
CandidateRankingBoard
WorkspacePatch
WorkspaceCommit
ContextPack
```

v0 不单独实现：

```text
CandidateScoreSnapshot
FeedbackEvent
ConversationMessage
AgentRun
AnalysisReport
ContactPoint
```

说明：

- `CandidateScoreSnapshot` 暂时内嵌到 `CandidateRankingBoard.ranked_items[].score_breakdown`。
- `FeedbackEvent` 可在后续 v0.1 增补，不进入第一版强制闭环。
- `ConversationMessage`、`AgentRun`、`AnalysisReport` 等到 API / runtime 集成阶段再接入。

---

## 5. v0 唯一核心测试场景

测试名建议：

```text
test_workspace_kernel_v0_two_round_research_reranks_candidate
```

测试流程：

```text
1. 创建 SalesWorkspace。
2. 添加 ProductProfileRevision。
3. 添加 LeadDirectionVersion。
4. Round 1 添加候选 A / B。
5. A 因 fit + pain signal 暂列第一。
6. Round 2 添加候选 D。
7. D 具备 fit + pain + timing + region + source quality signal。
8. RankingEngine 重新计算。
9. D 升至 #1。
10. RankingDelta 解释 D 为什么超过 A。
11. Markdown projection 中 rankings/current.md 显示 D 为 #1。
12. ContextPack top_candidates[0] 是 D。
```

---

## 6. 强制约束

### 6.1 RankingBoard 不允许 patch 直接写入

`CandidateRankingBoard` 是派生对象，只能由 `RankingEngine` 生成。

### 6.2 Observation 必须绑定 source

除后续明确引入 user feedback signal 外，v0 的 `CandidateObservation` 必须有合法 `source_id`。

### 6.3 Markdown 不允许回写

v0 只支持：

```text
structured state -> markdown projection
```

不支持：

```text
markdown -> structured state
```

### 6.4 ContextPack 从结构化 state 编译

`ContextPackCompiler` 不读 Markdown，不读 LangGraph checkpoint，不读 SDK session。

### 6.5 WorkspacePatch 必须检查 base version

每个 patch 必须包含 `base_workspace_version`。版本不匹配时必须拒绝。

---

## 7. v0 完成标准

v0 完成必须满足：

1. `pytest backend/tests/sales_workspace/` 通过。
2. 端到端测试证明 D 在第二轮超过 A。
3. ranking delta 包含 supporting observation ids。
4. markdown projection 渲染至少 5 个文件。
5. ContextPack 包含当前产品、当前方向、top candidates 和 ranking delta。
6. 未新增 API、DB migration、Android、runtime graph。
