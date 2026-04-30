# 当前活跃任务

更新时间：2026-04-30

## 1. 使用说明

本文件是当前执行授权入口。它只说明当前是否有开放 task、是否允许 auto-continue、以及哪些内容不得自动实现。

产品阶段状态以 `docs/product/project_status.md` 为准。历史 task / handoff 只作为 evidence。

---

## 2. 当前状态

### Current delivery package

暂无。

### Current task

`docs/delivery/tasks/task_2026_04_30_agents_product_neutral_entry.md`

### Current task status

`done`

### Next queued task

暂无下游 implementation task 自动开放。

### Auto-continue

`no`。

---

## 3. 当前方向

当前项目主线已定为：

> **V3 Memory-native Sales Agent**

当前 V3 是 accepted direction / implementation not started。

最新入口：

- `docs/product/prd/ai_sales_assistant_v3_prd.md`
- `docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`
- `docs/architecture/v3/memory-native-sales-agent.md`
- `docs/architecture/v3/web-dual-entry-prototype.md`

---

## 4. Recently completed

- `docs/delivery/tasks/task_2026_04_30_agents_product_neutral_entry.md`（done）
- `docs/delivery/handoffs/handoff_2026_04_30_agents_product_neutral_entry.md`（done）
- `docs/delivery/tasks/task_2026_04_30_v3_web_dual_entry_direction.md`（done）
- `docs/delivery/handoffs/handoff_2026_04_30_v3_web_dual_entry_direction.md`（done）
- `docs/delivery/tasks/task_2026_04_29_v3_repo_skill_guardrail_refresh.md`（done）
- `docs/delivery/handoffs/handoff_2026_04_29_v3_repo_skill_guardrail_refresh.md`（done）
- `docs/delivery/tasks/task_2026_04_29_agents_compression_skill_migration.md`（done）
- `docs/delivery/handoffs/handoff_2026_04_29_agents_compression_skill_migration.md`（done）
- `docs/delivery/tasks/task_2026_04_29_v3_docs_rebaseline.md`（done）
- `docs/delivery/handoffs/handoff_2026_04_29_v3_docs_rebaseline.md`（done）
- `docs/delivery/tasks/task_2026_04_29_langgraph_letta_memory_direction_docs.md`（done / transitional record）
- `docs/delivery/handoffs/handoff_2026_04_29_langgraph_letta_memory_direction_docs.md`（done / transitional record）
- `docs/delivery/tasks/task_v2_1_context_defect_device_deep_test_memory_pipeline.md`（done）

---

## 5. 当前禁止自动实现

除非后续 task 明确开放，不得自动实现：

- LangGraph / LangChain runtime。
- Letta server 接入。
- memory DB schema / migration。
- Web scaffold / Web UI implementation。
- Android UI 重写。
- V2.2 search / ContactPoint。
- CRM / outreach / bulk contact。
- production SaaS / auth / tenant。

---

## 6. 推荐下游候选

以下仅为候选，不代表已开放：

1. `V3 runtime POC planning`
2. `V3 Web dual-entry scaffold planning`
3. `V3 memory model minimal design`

执行 agent 不得自行从候选项中开工。
