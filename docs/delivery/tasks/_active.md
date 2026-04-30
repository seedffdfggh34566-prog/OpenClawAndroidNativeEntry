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

`docs/delivery/tasks/task_2026_04_30_v3_lab_settings_trace_inspector.md`

### Current task status

`done`

### Next queued task

暂无下游 implementation task 自动开放。

### Auto-continue

`no`。

---

## 3. 当前方向

当前项目主线已定为：

> **V3 Agent Sandbox-first Memory-native Sales Agent**

当前 V3 已有 backend-only sandbox runtime POC；更完整的 V3 product implementation、Web、Android 和 production SaaS 仍未开放。

最新入口：

- `docs/product/prd/ai_sales_assistant_v3_prd.md`
- `docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`
- `docs/architecture/v3/memory-native-sales-agent.md`
- `docs/architecture/v3/web-dual-entry-prototype.md`

---

## 4. Recently completed

- `docs/delivery/tasks/task_2026_04_30_v3_lab_settings_trace_inspector.md`（done）
- `docs/delivery/handoffs/handoff_2026_04_30_v3_lab_settings_trace_inspector.md`（done）
- `docs/delivery/tasks/task_2026_04_30_v3_lab_full_trace_visualization.md`（done）
- `docs/delivery/handoffs/handoff_2026_04_30_v3_lab_full_trace_visualization.md`（done）
- `docs/delivery/tasks/task_2026_04_30_v3_lab_db_persistence_inspection.md`（done）
- `docs/delivery/handoffs/handoff_2026_04_30_v3_lab_db_persistence_inspection.md`（done）
- `docs/delivery/tasks/task_2026_04_30_v3_sandbox_memory_persistence.md`（done）
- `docs/delivery/handoffs/handoff_2026_04_30_v3_sandbox_memory_persistence.md`（done）
- `docs/delivery/tasks/task_2026_04_30_v3_lab_seed_reset_replay.md`（done）
- `docs/delivery/handoffs/handoff_2026_04_30_v3_lab_seed_reset_replay.md`（done）
- `docs/delivery/tasks/task_2026_04_30_v3_sandbox_runtime_poc.md`（done）
- `docs/delivery/handoffs/handoff_2026_04_30_v3_sandbox_runtime_poc.md`（done）
- `docs/delivery/tasks/task_2026_04_30_v3_web_lab_scaffold.md`（done）
- `docs/delivery/handoffs/handoff_2026_04_30_v3_web_lab_scaffold.md`（done）
- `docs/delivery/tasks/task_2026_04_30_v3_sandbox_first_docs_rebaseline.md`（done）
- `docs/delivery/handoffs/handoff_2026_04_30_v3_sandbox_first_docs_rebaseline.md`（done）
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

- 超出 V3 sandbox runtime POC 的 LangGraph / LangChain runtime。
- Letta server 接入。
- 超出 opt-in V3 sandbox persistence 的 memory DB schema / migration。
- 正式 customer intelligence schema / 自动建档 / 候选客户排序或打分实现。
- 超出 `/lab` DB persistence inspection 内部测试能力的 Web UI implementation。
- 超出 `/lab` full trace visualization 内部调试能力的 Web UI implementation。
- Android UI 重写。
- V2.2 search / ContactPoint。
- CRM / outreach / bulk contact / 不可逆导出。
- production SaaS / auth / tenant。

---

## 6. 推荐下游候选

以下仅为候选，不代表已开放：

1. `V3 workspace user prototype planning`
2. `V3 archival memory design`
3. `V3 /lab trace playback`
4. `V3 LangGraph Studio adapter spike`

执行 agent 不得自行从候选项中开工。
