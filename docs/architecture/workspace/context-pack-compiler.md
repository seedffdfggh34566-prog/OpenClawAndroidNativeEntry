# V2 Sales Workspace ContextPack Compiler

- 文档状态：Draft v0.1
- 更新日期：2026-04-26
- 阶段定位：Sales Workspace Kernel v0 的 ContextPack 编译规范
- 建议路径：`docs/architecture/workspace/context-pack-compiler.md`

---

## 1. 目的

ContextPack Compiler 的目标是解决 LLM 上下文窗口限制：

> 不把整个 workspace 塞进 prompt，而是按任务类型从结构化 truth 中编译最小必要上下文。

ContextPack 不是业务主存，不是 LangGraph state，不是 checkpoint，也不是 SDK session。

---

## 2. v0 支持范围

v0 只支持：

```text
task_type = research_round
```

v0 不做：

- embedding retrieval。
- semantic search。
- LLM summarization。
- 多 task type。
- 历史长文压缩。
- ContextPack 持久化到数据库。

---

## 3. 输入

```text
workspace: SalesWorkspace
request:
  workspace_id: str
  task_type: research_round
  token_budget_chars: int = 6000
  top_n_candidates: int = 5
```

v0 使用字符预算近似 token budget。后续接入 LLM 后再替换为真实 tokenizer。

---

## 4. 输出

`ContextPack` 最小字段：

```text
id
workspace_id
task_type
token_budget_chars
product_summary
current_direction
top_candidates
recent_ranking_delta
open_questions
generated_at
```

---

## 5. 编译策略

v0 按固定顺序选择内容：

1. 当前 `ProductProfileRevision`。
2. 当前 `LeadDirectionVersion`。
3. 当前 `CandidateRankingBoard`。
4. Top N candidates。
5. 最近 `RankingDelta`。
6. 简单 open questions。

当超过 `token_budget_chars`：

1. 先裁剪 candidate reason。
2. 再减少 top candidates 数量。
3. 再裁剪 ranking delta explanation。
4. 最后保留 product summary 和 current direction。

---

## 6. 与 Runtime 的边界

未来 runtime 调用链：

```text
SalesWorkspace structured state
    -> ContextPackCompiler
    -> ContextPack
    -> LangGraph / Runtime
    -> WorkspacePatchDraft
    -> Kernel validation
```

LangGraph 不应自行遍历 workspace，也不应读取 Markdown projection 来拼 prompt。v0 不实现 LangGraph，但要保留这个边界。

---

## 7. 与 Markdown Projection 的边界

ContextPack 从结构化对象编译，不从 Markdown 文件读取。

Markdown projection 可以帮助人类和 agent 审阅，但 v0 的 ContextPack source of truth 只能是 `SalesWorkspace` state。

---

## 8. v0 验收

v0 ContextPack 必须在端到端测试中证明：

1. 包含当前产品理解。
2. 包含当前获客方向。
3. 包含当前排名第一的候选。
4. 在第二轮研究后，top candidate 变为新候选 D。
5. 包含简短 ranking delta。
