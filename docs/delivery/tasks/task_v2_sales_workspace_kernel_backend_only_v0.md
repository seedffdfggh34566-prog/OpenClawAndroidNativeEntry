# Task：V2 Sales Workspace Kernel backend-only v0

更新时间：2026-04-26

## 1. 任务定位

- 任务名称：V2 Sales Workspace Kernel backend-only v0
- 建议路径：`docs/delivery/tasks/task_v2_sales_workspace_kernel_backend_only_v0.md`
- 当前状态：`done`
- 优先级：P0

---

## 2. 任务目标

实现 Sales Workspace Kernel 的第一版 backend-only prototype。

本任务只验证 kernel 核心闭环：

```text
创建 workspace
-> 添加产品理解
-> 添加获客方向
-> 添加两轮候选客户研究结果
-> 生成候选评分
-> 第二轮新候选超过第一轮旧候选
-> 生成 ranking delta
-> 渲染 Markdown workspace
-> 编译 ContextPack
```

本任务不是：

- API 实现任务
- 数据库 migration 任务
- Android UI 任务
- LangGraph runtime 任务
- 联网搜索任务
- LLM prompt 任务

---

## 3. In Scope

允许新增：

```text
backend/sales_workspace/__init__.py
backend/sales_workspace/schemas.py
backend/sales_workspace/store.py
backend/sales_workspace/patches.py
backend/sales_workspace/ranking.py
backend/sales_workspace/projection.py
backend/sales_workspace/context_pack.py
backend/tests/sales_workspace/test_workspace_patch.py
backend/tests/sales_workspace/test_candidate_ranking.py
backend/tests/sales_workspace/test_markdown_projection.py
backend/tests/sales_workspace/test_context_pack.py
backend/tests/sales_workspace/test_sales_workspace_kernel_e2e.py
```

允许使用：

- Pydantic
- Python stdlib
- JSON fixture
- pytest

---

## 4. Out of Scope

本任务明确不做：

- FastAPI endpoint
- SQLAlchemy ORM
- Alembic migration
- SQLite schema change
- Android UI
- LangGraph graph
- 真实 LLM
- 联网搜索
- 搜索 provider
- CRM pipeline
- ContactPoint
- 自动触达
- 用户 / 权限 / 多租户
- 真实 Git commit / rollback / branch
- Markdown parse-back
- embedding / pgvector
- source URL fetch verification
- 复杂候选 fuzzy merge
- 正式 AnalysisReport
- ConversationMessage 持久化
- AgentRun 集成

---

## 5. 必须实现对象

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

`CandidateScoreSnapshot` 不做独立对象，先内嵌在 ranking item 的 score breakdown 中。

---

## 6. 核心规则

1. `WorkspacePatch` 是唯一写入口。
2. `CandidateRankingBoard` 不能被 patch 直接写入，必须由 `RankingEngine` 派生。
3. `CandidateObservation` 必须绑定合法 `ResearchSource`。
4. `base_workspace_version` 不匹配时必须拒绝 patch。
5. Markdown projection 只渲染，不 parse back。
6. ContextPack 从结构化 `SalesWorkspace` state 编译，不读 Markdown。
7. 不允许 LLM 或 fixture 直接决定最终 ranking。

---

## 7. 核心验收测试

必须实现并通过：

```text
test_workspace_kernel_v0_two_round_research_reranks_candidate
```

测试必须验证：

1. 创建 workspace。
2. 添加 product profile revision。
3. 添加 lead direction version。
4. Round 1 添加候选 A / B。
5. A 排第一。
6. Round 2 添加候选 D。
7. D 基于更强 evidence-backed observations 排到第一。
8. RankingDelta 解释 D 为什么超过 A。
9. Markdown `rankings/current.md` 包含 D。
10. ContextPack `top_candidates[0]` 是 D。

---

## 8. 推荐实现顺序

1. `schemas.py`
2. `store.py`
3. `patches.py`
4. `ranking.py`
5. `projection.py`
6. `context_pack.py`
7. e2e pytest

---

## 9. 验收命令

固定命令：

```bash
backend/.venv/bin/python -m pytest backend/tests/sales_workspace -q
backend/.venv/bin/python -m pytest backend/tests -q
```

本任务不运行 Android build；本次不改 Android。

---

## 10. 实际完成记录

完成日期：2026-04-26

已实现：

- `backend/sales_workspace/` backend-only kernel package。
- Pydantic workspace object model。
- in-memory store 与 JSON fixture load/save helper。
- WorkspacePatch apply 与 `base_workspace_version` 乐观校验。
- evidence-backed deterministic RankingEngine。
- Markdown projection renderer。
- ContextPack compiler。
- `backend/tests/sales_workspace/` pytest 覆盖。

实际验证：

```bash
backend/.venv/bin/python -m pytest backend/tests/sales_workspace -q
backend/.venv/bin/python -m pytest backend/tests -q
git diff --check
```

保持未实现：

- FastAPI endpoint。
- SQLAlchemy ORM / Alembic migration / SQLite schema change。
- Android UI。
- LangGraph / Runtime integration。
- LLM / search provider。
- CRM / ContactPoint / 自动触达。

---

## 11. 停止条件

命中以下情况时停止并回到规划层：

- 需要修改数据库 schema。
- 需要新增 API route。
- 需要接入 Android。
- 需要接入 LangGraph。
- 需要接入 LLM 或搜索。
- 需要引入新的外部依赖。
- 对象模型与 `workspace-object-model.md` 冲突。
- 无法用单个 e2e 测试证明两轮重排闭环。
