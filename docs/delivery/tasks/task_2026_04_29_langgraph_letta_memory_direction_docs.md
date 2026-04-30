# Task：LangGraph + Letta-style Memory 方向轻量文档沉淀

更新时间：2026-04-29

## 1. 任务定位

- 任务名称：LangGraph + Letta-style Memory 方向轻量文档沉淀
- 建议路径：`docs/delivery/tasks/task_2026_04_29_langgraph_letta_memory_direction_docs.md`
- 当前状态：`done`
- 优先级：P0
- 任务类型：`planning`
- 是否属于 delivery package：`no`
- 所属 package：`none`
- 文档同步级别：`Level 1 task`

---

## 2. 任务目标

将 2026-04-29 关于 Product Sales Agent runtime 的方向调整沉淀到项目文档中：

- 优先采用 LangGraph / LangChain 作为自研 runtime 路线。
- 借鉴 Letta 的可自编辑 memory 模式。
- 放开 runtime memory 的推断、假设、策略和纠错能力。
- 保留 backend / Sales Workspace Kernel 对正式业务对象的写回治理。

---

## 3. 范围

In Scope：

- 新增轻量 runtime 方向文档。
- 新增轻量 ADR。
- 小幅更新 V2 PRD 和文档索引。
- 记录本次任务和 handoff。

Out of Scope：

- 代码实现。
- LangGraph / LangChain 依赖接入。
- Letta server 接入。
- DB schema / migration。
- API contract 变更。
- V2.2 search / ContactPoint 实现。

---

## 4. 涉及文件

本任务产出：

- `docs/architecture/runtime/langgraph-letta-style-sales-agent-memory.md`
- `docs/adr/ADR-008-v2-langgraph-letta-style-memory-direction.md`
- `docs/delivery/handoffs/handoff_2026_04_29_langgraph_letta_memory_direction_docs.md`

同步更新：

- `docs/product/prd/ai_sales_assistant_v2_prd.md`
- `docs/architecture/runtime/README.md`
- `docs/adr/README.md`
- `docs/README.md`
- `docs/delivery/tasks/_active.md`

---

## 5. 验收标准

满足以下条件即完成：

1. 文档明确记录“LangGraph / LangChain 自研 runtime + Letta-style memory”方向。
2. 文档允许 Product Sales Agent runtime memory 保存推断、假设、策略和纠错。
3. 文档未将 schema、API、graph 节点或实现任务提前冻结。
4. 文档未声明 implementation done、milestone done 或 production-ready。
5. 后续 implementation task 未自动开放。

---

## 6. 实际结果说明

本任务已完成轻量文档沉淀。后续如需实现 LangGraph / LangChain runtime、memory tools 或持久化 memory schema，需要单独创建 implementation task。

---

## 7. 已做验证

- `git diff --check`
- `rg "LangGraph \\+ Letta-style|Letta-style|ADR-008|self-edit memory|自编辑" docs`
