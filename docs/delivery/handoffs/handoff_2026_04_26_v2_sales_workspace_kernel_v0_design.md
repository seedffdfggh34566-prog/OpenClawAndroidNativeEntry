# 阶段性交接：V2 Sales Workspace Kernel backend-only v0 design

更新时间：2026-04-26

## 1. 本次推进内容

基于三轮架构研究、红队评审和最小实现切片，已将 Sales Workspace Kernel 收敛为可执行的 backend-only v0 方案。

新增文档建议：

- `docs/architecture/workspace/sales-workspace-kernel.md`
- `docs/architecture/workspace/workspace-kernel-v0-scope.md`
- `docs/architecture/workspace/markdown-projection.md`
- `docs/architecture/workspace/context-pack-compiler.md`
- `docs/delivery/tasks/task_v2_sales_workspace_kernel_backend_only_v0.md`

## 2. 关键架构结论

1. V2 主架构是 Sales Workspace Kernel，不是 LangGraph。
2. LangGraph 后续只作为 runtime execution layer。
3. 结构化对象是 truth。
4. Markdown 是 projection，不是主存。
5. WorkspacePatch 是唯一写入口。
6. CandidateRankingBoard 是 RankingEngine 派生结果，不能被 agent 直接写。
7. ContextPackCompiler 是核心模块，用于避免上下文窗口限制。
8. v0 不接 DB、API、Android、LangGraph、LLM、搜索。

## 3. v0 唯一核心验收

```text
Round 1: A 排第一
Round 2: D 因更强 evidence-backed observations 超过 A
系统生成 RankingDelta
Markdown projection 和 ContextPack 都反映 D 为当前第一优先级
```

## 4. 已明确后置

- 数据库 migration
- FastAPI API
- Android UI
- LangGraph graph
- 真实 LLM
- 联网搜索
- ContactPoint
- CRM
- 自动触达
- 真实 Git
- Markdown parse-back

## 5. 推荐下一步

创建正式任务分支后执行：

```text
docs/delivery/tasks/task_v2_sales_workspace_kernel_backend_only_v0.md
```

优先实现：

```text
backend/sales_workspace/schemas.py
backend/sales_workspace/patches.py
backend/sales_workspace/ranking.py
backend/tests/sales_workspace/test_sales_workspace_kernel_e2e.py
```
