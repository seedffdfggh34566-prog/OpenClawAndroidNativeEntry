# V2 Sales Workspace Kernel Architecture

- 文档状态：Draft v0.1
- 更新日期：2026-04-26
- 阶段定位：V2 workspace-native sales agent 的核心架构草案；不是 ORM、API、runtime graph 或 Android 实现规格
- 建议路径：`docs/architecture/workspace/sales-workspace-kernel.md`
- 关联文档：
  - `docs/product/prd/ai_sales_assistant_v2_prd.md`
  - `docs/architecture/workspace/workspace-object-model.md`
  - `docs/architecture/workspace/workspace-kernel-v0-scope.md`
  - `docs/architecture/workspace/markdown-projection.md`
  - `docs/architecture/workspace/context-pack-compiler.md`
  - `docs/architecture/runtime/langgraph-runtime-architecture.md`

---

## 1. 一句话结论

V2 的主架构应是：

> **Sales Workspace Kernel = 结构化 workspace 状态机 + WorkspacePatch 写回门禁 + 证据驱动候选排序 + Markdown projection + ContextPack Compiler。**

LangGraph 继续保留，但只作为 runtime execution layer。它不再是 V2 的主架构，也不能成为业务主存、长期记忆或候选排序决策中心。

---

## 2. 架构目标

Sales Workspace Kernel 的目标不是做 CRM，也不是做普通聊天机器人，而是支撑一个面向中小企业老板 / 创始人 / 销售负责人的 **workspace-native sales agent**。

它必须支持：

1. 产品侧信息长期沉淀。
2. 客户挖掘侧信息长期沉淀。
3. 多轮 ResearchRound。
4. 候选客户跨轮次积累、去重、评分和重新排序。
5. 来源证据与候选判断绑定。
6. 用户反馈进入下一轮研究上下文。
7. Markdown workspace projection，让 agent 像读软件工程仓库一样读取销售工作区。
8. ContextPack Compiler，在有限 token budget 下编译当前任务需要的最小上下文。
9. 所有 agent 产生的状态变更必须先成为 patch draft，再经过 kernel 校验后才能写入正式对象。

---

## 3. 总体架构图

```text
Android / future UI
    |
    | user message / user feedback / read workspace state
    v
FastAPI API Layer
    |
    v
backend/api/services.py
    |
    | create ConversationMessage / AgentRun in future phases
    | call Sales Workspace Kernel
    v
Sales Workspace Kernel
    |
    |-- WorkspaceState / Object Store
    |     structured truth: ProductProfileRevision, LeadDirectionVersion,
    |     ResearchRound, ResearchSource, CompanyCandidate,
    |     CandidateObservation, CandidateRankingBoard
    |
    |-- WorkspacePatch Gate
    |     validate, normalize, apply, reject unsafe or invalid changes
    |
    |-- Candidate Ranking Engine
    |     derive CandidateRankingBoard from evidence-backed observations
    |
    |-- Markdown Projection Renderer
    |     render structured truth into agent-readable workspace docs
    |
    |-- ContextPack Compiler
    |     compile task-specific, token-budgeted context for future runtime
    |
    |-- WorkspaceCommit Log
    |     append simple change record; no real Git in v0
    |
    v
Runtime Gateway              (future, not v0)
    |
    v
backend/runtime/             (future)
    |
    | LangGraph graphs receive ContextPack
    | LangGraph returns WorkspacePatchDraft / MessageDraft
    v
LLM / Search / Tool Adapters (future)
```

---

## 4. 分层边界

### 4.1 FastAPI / services.py

职责：

- 接收 API 请求。
- 鉴别用户动作类型。
- 未来创建 `ConversationMessage` 和 `AgentRun`。
- 调用 Sales Workspace Kernel。
- 返回 UI 需要的 view model。

不负责：

- 候选评分。
- Markdown 渲染细节。
- ContextPack 编译策略。
- LangGraph 节点内部逻辑。

### 4.2 Sales Workspace Kernel

职责：

- 维护 workspace 结构化状态。
- 应用 WorkspacePatch。
- 校验引用关系和版本。
- 从 evidence-backed observations 派生候选排名。
- 生成 RankingDelta。
- 渲染 Markdown projection。
- 编译 ContextPack。
- 生成 WorkspaceCommit。

不负责：

- 直接调用 LLM。
- 直接联网搜索。
- Android UI。
- CRM pipeline。
- 自动触达。

### 4.3 backend/runtime / LangGraph

职责：

- 未来接收 ContextPack。
- 未来生成 `WorkspacePatchDraft`、`MessageDraft`、`ToolResultDraft`。
- 编排 LLM / search / tool 调用。

不得：

- 直接写正式业务对象。
- 直接修改 Markdown projection。
- 直接生成正式 CandidateRankingBoard。
- 把 checkpoint、SDK session 或 graph state 当成业务主存。

### 4.4 Markdown workspace

职责：

- 作为 agent-readable projection。
- 作为人工审阅和 debug 的可读视图。
- 作为未来 Codex / agent 操作 workspace 的文本界面。

v0 明确不允许：

- 从 Markdown parse 回正式结构化对象。
- 让 Product Sales Agent / Runtime 直接修改 generated Markdown 后污染主存。
- 把 Markdown 当成唯一 truth。

---

## 5. 核心原则

### 5.1 结构化对象是 truth

V2 的正式业务状态必须在结构化对象中表达。Markdown、prompt、runtime state、checkpoint、SDK session 都不是业务 truth。

### 5.2 Markdown 是 projection

Markdown 是由结构化对象渲染出来的可读视图。v0 只支持：

```text
structured state -> markdown projection
```

v0 不支持：

```text
markdown -> structured state
```

### 5.3 Patch 是唯一写入口

所有 workspace 状态变更都必须通过：

```text
WorkspacePatch -> validate -> apply -> WorkspaceCommit
```

未来 agent 输出必须先成为：

```text
WorkspacePatchDraft
```

再由 kernel 校验为正式 `WorkspacePatch`。

### 5.4 CandidateRankingBoard 是派生结果

`CandidateRankingBoard` 不能由 agent 或 fixture 直接写入。它必须由 `RankingEngine` 根据：

- `CompanyCandidate`
- `ResearchSource`
- `CandidateObservation`
- `LeadDirectionVersion`

派生生成。

### 5.5 LLM 不决定最终排名

未来 LLM 可以用于：

- 来源摘要。
- 候选抽取。
- observation 草稿。
- 风险解释。
- 自然语言 reason。

但最终分数、排名和是否进入 ranking board 必须由 kernel / ranking rules 决定。

---

## 6. v0 的核心闭环

v0 只证明一个闭环：

```text
创建 workspace
-> 添加产品理解
-> 添加获客方向
-> Round 1 添加候选 A/B
-> A 排第一
-> Round 2 添加候选 D
-> D 因更强 evidence-backed observations 超过 A
-> 生成 RankingDelta
-> 渲染 Markdown workspace
-> 编译 ContextPack
```

v0 不证明：

- LLM 能不能生成好 patch。
- 搜索 provider 是否好用。
- Android UI 是否好看。
- 数据库 schema 是否最终稳定。
- 联系方式是否可用。

---

## 7. v0 模块

v0 只实现这些模块：

```text
backend/sales_workspace/schemas.py
backend/sales_workspace/store.py
backend/sales_workspace/patches.py
backend/sales_workspace/ranking.py
backend/sales_workspace/projection.py
backend/sales_workspace/context_pack.py
```

每个模块职责：

| 模块 | 职责 | 明确不做 |
|---|---|---|
| `schemas.py` | Pydantic schema | SQLAlchemy ORM |
| `store.py` | in-memory / JSON fixture workspace state | DB session / Alembic |
| `patches.py` | patch validate + apply + commit | agent draft normalization |
| `ranking.py` | scoring + ranking board + delta | LLM ranking |
| `projection.py` | render markdown tree | parse markdown back |
| `context_pack.py` | compile task context | embedding / retrieval |

---

## 8. 状态变更规则

`WorkspacePatch` 可以做：

- `add_product_profile_revision`
- `add_lead_direction_version`
- `add_research_round`
- `add_research_source`
- `upsert_company_candidate`
- `add_candidate_observation`

`WorkspacePatch` 不能做：

- `add_ranking_board`
- `add_context_pack`
- `add_markdown_file`
- `add_agent_run`
- `add_contact_point`

后者均由系统派生或后续阶段实现。

---

## 9. 和 LangGraph 的未来关系

未来推荐 LangGraph graph：

```text
sales_agent_turn_graph
research_round_graph
candidate_observation_graph
report_generation_graph
feedback_interpretation_graph
```

但 graph 的输出必须遵守：

```text
ContextPack -> LangGraph -> WorkspacePatchDraft -> Kernel validation -> WorkspacePatch -> WorkspaceCommit
```

v0 不实现 LangGraph graph。

---

## 10. 进入后续阶段的条件

只有当 v0 端到端测试通过，才允许进入：

1. FastAPI workspace API。
2. SQLite / Alembic 持久化。
3. LangGraph runtime graph。
4. 真实 LLM patch draft。
5. 联网搜索和来源验证。
6. Android workspace UI。

v0 的唯一核心验收：

```text
test_workspace_kernel_v0_two_round_research_reranks_candidate
```
