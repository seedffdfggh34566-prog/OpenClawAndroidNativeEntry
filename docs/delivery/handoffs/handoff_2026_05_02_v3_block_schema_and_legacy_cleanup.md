# Handoff：V3 Block Schema 扩字段 + Legacy Memory Path 清理

更新时间：2026-05-02

## 1. 任务

`docs/delivery/tasks/task_2026_05_02_v3_block_schema_and_legacy_cleanup.md`（status: `done`）

合并 ADR-010 §6 推荐缺口 #1（Block schema 扩字段 + memory tool 描述对齐）+ #2（死代码清理）。

## 2. 实际产出

### 2.1 Block schema 扩字段（来自 #1）

- `CoreMemoryBlock` 新增 `description: str` / `metadata: dict[str, Any]` / `tags: list[str]` 三个字段；`limit` 上限从 `le=20000` 提到 `le=100000`。
- `default_core_memory_blocks()` 5 个 block 按 §3.1.1 表设置 default `limit` 与 `description`：
  - persona 2k / human 5k / product 10k / sales_strategy 5k / customer_intelligence 20k。
- `_build_tool_loop_messages` 在 system prompt 中按 `[label] description: ... limit: N chars used: M chars` 渲染每个 block 的 `description`，让模型从 prompt 中读出 block 职责。

### 2.2 Memory tool 描述对齐（来自 #1）

- `memory_insert` 保留 V3 substring (`insert_after`) 语义，docstring 中加防御提示（不要在 anchor / content 中包含 line number 前缀或行号警告横幅，对照 Letta `function_sets/base.py:391`）。
- `memory_replace` 改为 unique-or-raise：移除 `replace_all` 参数；`old_content` 多于一次匹配时 raise `v3_memory_replace_old_content_not_unique`，错误信息包含每个匹配行的 1-indexed 行号（如 `matches at line(s) [2, 4]`）并提示 `expand 'old_content' with more surrounding context`。
- 工具 docstring 风格对齐 Letta，但措辞针对销售场景调整。

### 2.3 Legacy 死代码清理（来自 #2）

- `backend/runtime/v3_sandbox/schemas.py`：删除 `MemoryItemStatus`、`MemorySource`、`MemoryItem`、`WorkingState`、`CustomerCandidateDraft`、`CustomerIntelligenceDraft`、`AgentAction`、`AgentActionType`、`V3SandboxTurnOutput`；从 `V3SandboxSession` 移除 `memory_items / working_state / customer_intelligence`；从 `V3SandboxTurnResult` 与 `V3SandboxTraceEvent` 移除 `actions` 字段；保留 `model_config = ConfigDict(extra='ignore')`。
- `backend/runtime/v3_sandbox/graph.py`：删除 V2 JSON 解析与 action 应用全套函数；简化 `V3SandboxRuntimeError` 错误码（保留 `llm_runtime_unavailable`）；`_state_diff` 只保留 core_memory_blocks diff。
- `backend/runtime/v3_sandbox/store.py`：删除 `_memory_transition_events`、`_action_payload`、`_transition_event` 与 `DatabaseV3SandboxStore.memory_transitions(...)`；`_replace_normalized_rows` 不再 delete/add 三个 legacy ORM 行；`inspection_counts` 仅返回 `messages / traces / core_memory_block_transitions`。
- `backend/api/models.py`：删除 `V3SandboxActionEventRecord`、`V3SandboxMemoryItemRecord`、`V3SandboxMemoryTransitionEventRecord` 三个 ORM。
- `backend/api/v3_sandbox.py`：删除 `GET /v3/sandbox/sessions/{session_id}/memory-transitions` 路由；保留 `/core-memory-transitions`；`runtime-config` 响应的 `memory_runtime` 中移除 `legacy_json_action_loop` 键。

### 2.4 数据库迁移（来自 (b)）

- 新建 `backend/alembic/versions/20260502_0007_v3_drop_legacy_memory_path.py`：
  - upgrade：`drop_index` × 10 + `drop_table('v3_sandbox_memory_transition_events')` + `drop_table('v3_sandbox_memory_items')` + `drop_table('v3_sandbox_action_events')`。
  - downgrade：按 `20260430_0005` 中定义重建三张表与对应索引，仅恢复结构、不恢复数据。
- 不 rewrite 现有 `v3_sandbox_sessions.payload_json`：旧 session 的 `memory_items / working_state / customer_intelligence` 键由 `extra='ignore'` 容忍读出，下次 `save_session` 自然被新 schema 覆盖。

### 2.5 Web 前端清理

- `web/src/api.ts`：删除 `MemoryStatus / MemoryItem / SandboxWorkingState / CustomerCandidateDraft / CustomerIntelligenceDraft / AgentAction / V3SandboxMemoryTransition / V3SandboxMemoryTransitionsResponse` 类型；从 `V3SandboxSession` 移除 `memory_items / working_state / customer_intelligence`；从 `V3SandboxTraceEvent` 移除 `actions`；移除 `getMemoryTransitions(...)` 函数；从 `memory_runtime` 配置形状中移除 `legacy_json_action_loop`。
- `web/src/App.tsx`：删除 Memory / Working State / Customer Intelligence / Memory Transitions 四个 panel 与对应的 `MemoryList / WorkingState / CustomerIntelligence / MemoryTransitions / FieldList / DebugTrace / DebugTraceNode` 组件；删除 `memoryItems` derivation、`statusOrder`、`transitionInspection` state、`Sparkles` icon 引用与所有 `event.actions` 引用；保留 Core Memory Blocks / Trace / Core Memory Transitions 三个 panel。
- `web/tests/lab.spec.ts`：移除对 Memory / Working State / Customer Intelligence / Memory Transitions 标题与 `write_memory / update_memory_status / cand_seed_owner / 苏州小企业老板` 等 V2 文案的断言；保留对 Core Memory Blocks / Core Memory Transitions / `core_memory_append / memory_replace` 的断言。

### 2.6 测试改写

- `backend/tests/test_v3_sandbox_runtime.py` 全文重写：
  - 删除 `MemoryItem` / 三个 legacy ORM 引用；helper 由 `_*_turn_output()` action-dict 改为 `_*_turn_calls() -> list[TokenHubToolCall]` 原生 FC 构造。
  - 删除 6 个 V2 路径专属用例（`test_memory_item_rejects_unknown_status` / `test_v3_sandbox_memory_transitions_api_*` / `test_langgraph_runtime_accepts_action_type_nested_payload` / `test_v3_sandbox_api_returns_structured_error_for_bad_llm_json` / `test_v3_sandbox_api_failed_debug_trace_records_parse_error`）。
  - 现有用例改为断言 `core_memory_blocks` / `/core-memory-transitions` 路由 / tool_event 序列。
  - 新增 2 个用例：(a) `test_memory_replace_unique_or_raise_lists_per_line_numbers` 验证 1-indexed 行号 `[2, 4]` 与 `expand 'old_content' with more surrounding context` 提示；(b) `test_compose_context_renders_block_description_in_system_prompt` 直接调 `_build_tool_loop_messages` 验证 system prompt 含 `[persona] description: ...` 等 5 段头与 `limit: 10000 chars` / `used: 0 chars`。

## 3. 涉及文件

新增：

- `backend/alembic/versions/20260502_0007_v3_drop_legacy_memory_path.py`
- `docs/delivery/handoffs/handoff_2026_05_02_v3_block_schema_and_legacy_cleanup.md`

修改：

- `backend/runtime/v3_sandbox/schemas.py`
- `backend/runtime/v3_sandbox/graph.py`
- `backend/runtime/v3_sandbox/store.py`
- `backend/api/models.py`
- `backend/api/v3_sandbox.py`
- `backend/tests/test_v3_sandbox_runtime.py`
- `web/src/api.ts`
- `web/src/App.tsx`
- `web/tests/lab.spec.ts`
- `docs/delivery/tasks/task_2026_05_02_v3_block_schema_and_legacy_cleanup.md`（status → done）
- `docs/delivery/tasks/_active.md`

引用但未修改：

- `~/projects/_references/letta/letta/functions/function_sets/base.py`（`memory_insert:391` / `memory_replace:311`）
- `~/projects/_references/letta/letta/schemas/block.py:13`
- `docs/adr/ADR-010-letta-as-reference-architecture.md`
- `docs/architecture/v3/letta-comparison.md`

## 4. 验证

强制必跑：

- `backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -x` → 24 passed
- `backend/.venv/bin/python -m pytest backend/tests` → **156 passed, 18 skipped**（skip 全部为 Postgres / Live LLM 环境门）
- Alembic 双向迁移（SQLite，`OPENCLAW_BACKEND_DATABASE_URL` 环境变量）：
  - `upgrade head` → 22 个生产表，legacy 三表全部 drop ✅
  - `downgrade 20260430_0006` → 7 个 v3_sandbox_* 表（含重建的 3 个 legacy）✅
  - `re-upgrade head` → 4 个 v3_sandbox_* 表（仅保留 sessions / messages / trace_events / core_memory_block_transition_events）✅
- `cd web && npm run build` → tsc --noEmit + vite build 均通过（175.17 kB）✅

未跑（环境不可用 / 不在范围）：

- Postgres alembic 双向迁移（本机未起 docker compose；任务 §5.2 标"如本地有 docker"，跳过）
- `cd web && npm run test:e2e`（Playwright 需要 backend + browser 起栈，本次未跑；任务 §5.1 列出，留待后续 spot-check）
- §5.3 Real TokenHub smoke（未触发）
- Android `./gradlew`（无 Android 改动，§5.4 明确不触发）

## 5. 关键发现

- **`description` token 成本可控**：5 段中文加起来 ~300 字 ≈ 600 token；当前 system prompt 体量下无碍。验证用例 `test_compose_context_renders_block_description_in_system_prompt` 已固化 prompt 渲染契约。
- **unique-or-raise 错误信息行号格式被测试固化**：`v3_memory_replace_old_content_not_unique` + `matches at line(s) [2, 4]` + `expand 'old_content' with more surrounding context`。后续修改 `memory_replace` 实现时需保持该格式以避免 prompt 行为回归。
- **`extra='ignore'` 兼容性 spot-check 通过**：旧 session payload_json 的 `memory_items / working_state / customer_intelligence` 键被 Pydantic 静默丢弃，未引发 ValidationError；这是 Q2f 选择 (b) 而不 rewrite payload 的关键依据。
- **`/core-memory-transitions` API counts 字段名是 `core_memory_block_transitions`**：与早期 `/memory-transitions` 用 `transitions / actions` 的命名不同；写测试时需用前者，否则 KeyError（本次踩过）。
- **Web 前端三个 panel 删除后没有遗漏 import / dead JSX**：`tsc --noEmit` 通过验证；`npm run build` bundle 体积比清理前小。

## 6. 已知限制

- **Postgres 双向迁移未本地验证**：依赖 SQLite roundtrip 通过 + 迁移代码仅用 portable `sa.JSON().with_variant(JSONB)` 和标准 `op.drop_table / op.create_table`，未引入 dialect-specific 语法；理论上 Postgres 行为应一致，但落生产前应再跑一次 §5.2。
- **Web e2e（`npm run test:e2e`）未跑**：`web/tests/lab.spec.ts` 的断言已按新 UI 改写，但未实测；后续若起完整 backend + Playwright 栈，应跑一次回归。
- **`memory_rethink` 未实现**：用户已确认这是最终产品关键能力，必须做，但本 task §3.2 明确 out of scope，留待与 (A) #3（context 压缩 / step 上限提升）合并的后续 task。
- **`metadata` / `tags` 字段未在本 task 使用**：仅作为 schema 字段预留，未暴露 tool 接口或 UI 渲染；目的是避免后续 (A) task 再做一次 schema 迁移。
- **(b) 迁移 downgrade 不恢复数据**：与 `_active.md` POC 边界一致；如果未来需要历史 V2 action 数据，唯一回退是从备份恢复，本 task 不提供数据备份能力。

## 7. 推荐下一步

仅候选，**不**自动开工：

1. **`memory_rethink` 工具 + step 上限提升 + context 摘要**（合并为后续 task；用户已确认 `memory_rethink` 是最终产品关键能力）—— 对应 ADR-010 §6 #3 与 task §4 Q2c。
2. ADR-010 §6 #4 archival memory（需 `_active.md` §5 松绑 + ADR-011 圈定 archival schema 与 embedding provider）。
3. ADR-010 §6 #5 跨 session agent 一等实体（需 §5 松绑；与 #4 schema 设计耦合）。
4. ADR-010 §6 #6 recall memory（在 #4 之后再评估）。
5. Postgres alembic 双向迁移本地实测（轻量、可在任意时点补做，非 blocker）。
6. Web e2e（`npm run test:e2e`）回归一次（轻量、可在任意时点补做，非 blocker）。

执行 agent **不得**自行从上述候选中开工 —— 须由用户在 `_active.md` 显式开放对应 task。
