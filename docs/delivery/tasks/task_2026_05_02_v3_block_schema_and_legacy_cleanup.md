# Task：V3 Block Schema 扩字段 + Legacy Memory Path 清理（合并 (A) #1 + #2）

更新时间：2026-05-02

## 1. 任务定位

- 任务名称：V3 Block Schema 扩字段 + Legacy Memory Path 清理
- 当前状态：`done`
- 优先级：P1
- 任务类型：`backend runtime / schema / persistence / web inspection / docs`
- 是否属于 delivery package：`no`

对应 [ADR-010 §6](../../adr/ADR-010-letta-as-reference-architecture.md) 推荐缺口的 **#1（Block schema 扩字段 + memory tool 描述对齐）+ #2（死代码清理）合并**。

## 2. 授权来源

用户在当前线程明确指示：

- 项目阶段方向：先复刻 Letta（D2 已交付，参见 `docs/adr/ADR-010-letta-as-reference-architecture.md`、`docs/architecture/v3/letta-comparison.md`）。
- (A) 第一刀：合并 #1 + #2。
- legacy 数据兼容：选 (b) 一次性 Alembic 迁移（理由：长期更干净；POC opt-in store 没有生产数据）。
- 6 个子决策：Q2a/b/d/e/f 按推荐采纳；Q2c memory_rethink 暂不加，但**作为最终产品关键能力**留待后续 task 完成。

## 3. 范围

### 3.1 In scope

#### 3.1.1 Block schema 扩字段（来自 #1）

- `backend/runtime/v3_sandbox/schemas.py::CoreMemoryBlock` 新增字段：
  - `description: str` —— 给模型看的 block 职责描述
  - `metadata: dict[str, Any]` —— 任意 dict，default `{}`
  - `tags: list[str]` —— 可选标签，default `[]`
- `limit` 字段：`Field(default=2000, ge=1, le=100000)`（上限从 20000 提到 100000）
- `default_core_memory_blocks()` 5 个 block 的 default `limit` 与 `description` 按 Q2d/Q2e 设置：

  | label | limit | description |
  |---|---|---|
  | persona | 2000 | Sales Agent 自身的工作风格、语气与边界。修改要保守，避免与用户冲突。 |
  | human | 5000 | 当前对话用户的角色、所属公司、关注点、偏好与已知约束。用户主动纠正后必须更新。 |
  | product | 10000 | Agent 对所销售产品的理解：能力、定位、典型用户、限制与常见反对意见。基于用户输入和 agent 推断同时维护，写明状态（observed / inferred）。 |
  | sales_strategy | 5000 | 针对当前对话和客户画像的销售策略：当前阶段、下一步动作、需要验证的假设。 |
  | customer_intelligence | 20000 | 正在跟进的潜在客户/线索的草稿信息：行业、角色、关键信号、排序理由。仅 sandbox 草稿，不代表已写入 CRM 或对外触达。 |

#### 3.1.2 Memory tool 描述对齐（来自 #1）

`backend/runtime/v3_sandbox/graph.py::_core_memory_tools()`：

- **`memory_insert` 保留 substring 语义**（`insert_after`），但参考 Letta `function_sets/base.py:391` 在 docstring 中加防御提示："不要在 anchor / content 中包含 line number 前缀或行号警告横幅"（Q2a）。
- **`memory_replace` 改为 unique-or-raise**：移除 `replace_all` 参数；`old_content` 必须在 block 中唯一出现，多于一次则 raise，错误信息包含每个匹配行的行号（Q2b）。
- 工具 docstring 风格对齐 Letta（清晰的 Examples 段、对 line-number 的显式警告），但措辞针对销售场景调整。
- `_build_tool_loop_messages` 在 system prompt 中**渲染每个 block 的 `description`**（让模型理解每个 block 的职责），而不是裸 dump JSON。

#### 3.1.3 Legacy 死代码清理（来自 #2）

代码层删除：

- `backend/runtime/v3_sandbox/schemas.py`：
  - 删除 `MemoryItemStatus`、`MemorySource`、`MemoryItem`、`WorkingState`、`CustomerCandidateDraft`、`CustomerIntelligenceDraft`、`AgentAction`、`AgentActionType`、`V3SandboxTurnOutput`
  - 从 `V3SandboxSession` 移除字段：`memory_items`、`working_state`、`customer_intelligence`
  - 从 `V3SandboxTurnResult` 移除 `actions` 字段（保留 `assistant_message`、`session`、`trace_event`）
  - `V3SandboxTraceEvent.actions` 字段移除（已在 native FC loop 中始终为空）
- `backend/runtime/v3_sandbox/graph.py`：
  - 删除 `_call_llm`、`_parse_actions`、`_apply_actions`、`_apply_action`、`_build_messages`、`_list_updates`、`_strings`、`_merge_list`、`_require_str`、`_action_payload`、`_is_valid_turn_output`、`_parse_json_object`、`_strip_thinking_and_fences`、`_memory_diff`（行号在 graph.py 中 ~750-1050、1200-1300、1340-1380）
  - 简化 `V3SandboxRuntimeError` 错误码：保留 `llm_runtime_unavailable`，移除 `llm_structured_output_invalid`（V2 JSON 路径已下线）
  - `_state_diff` 移除对 `memory_items / working_state / customer_intelligence` 的 diff，只保留 core_memory_blocks diff
- `backend/runtime/v3_sandbox/store.py`：
  - 删除 `_memory_transition_events`、`_action_payload`、`_transition_event` 函数
  - `DatabaseV3SandboxStore.memory_transitions(...)` 整个方法删除
  - `_replace_normalized_rows` 中删除对 `V3SandboxActionEventRecord`、`V3SandboxMemoryItemRecord`、`V3SandboxMemoryTransitionEventRecord` 的 delete + add 分支
  - `inspection_counts` 移除 `memory_items`、`transitions` 字段（保留 `core_memory_block_transitions`）
- `backend/api/models.py`：删除 `V3SandboxActionEventRecord`、`V3SandboxMemoryItemRecord`、`V3SandboxMemoryTransitionEventRecord` 三个 ORM 类
- `backend/api/v3_sandbox.py`：删除 `GET /v3/sandbox/sessions/{session_id}/memory-transitions` 路由（保留 `/core-memory-transitions`）

数据库迁移（来自 (b)）：

- 新建 `backend/alembic/versions/20260502_0007_v3_drop_legacy_memory_path.py`：
  - upgrade：`op.drop_table('v3_sandbox_action_events')`、`op.drop_table('v3_sandbox_memory_items')`、`op.drop_table('v3_sandbox_memory_transition_events')`
  - downgrade：`op.create_table(...)` 三表（仅恢复结构，不恢复数据；与 `20260430_0005` 中定义对齐）
- **不**rewrite `v3_sandbox_sessions.payload_json`：旧 session 的 `memory_items / working_state / customer_intelligence` 键由 Pydantic `extra='ignore'` 容忍读出，下次 `save_session` 自然被新 schema 覆盖。`V3SandboxModel` 已配置 `model_config = ConfigDict(extra='ignore')`（启动时 spot-check）。

Web 前端清理：

- `web/src/api.ts`：删除调用 `memory-transitions` 的函数（保留 `core-memory-transitions`）；删除 inspection_counts 相关的 `memory_items / transitions` 字段引用。
- `web/src/App.tsx`：删除 Memory Items / Memory Transitions 的 UI block（如果存在）；保留 Core Memory Blocks / Core Memory Transitions / Trace Inspector。
- 实际 web 代码改动量待 spot-check 后确定，但不超出本节范围。

测试清理 / 改写：

- `backend/tests/test_v3_sandbox_runtime.py`、`backend/tests/test_v3_sandbox_runtime_*.py`：删除 `_apply_action` / V2 action 路径相关用例；保留 / 改写 native FC + core memory 用例；新增 ≥ 2 个用例覆盖：(a) `memory_replace` unique-or-raise 行为，(b) block `description` 出现在 system prompt 中。
- 其他 backend 测试如有 `memory_items / working_state / customer_intelligence` 引用，同步删除。
- `web/tests/`（Playwright e2e）：spot-check 是否有断言 memory_items / memory_transitions UI；如有则删除。

### 3.2 Out of scope（**不**做）

- 引入 `memory_rethink` 工具 —— **作为最终产品关键能力，留待后续 task**（见 §7 后续建议）。
- 引入 `archival_memory_*`、`conversation_search` 工具（属 (A) #4 / #6）。
- Context 压缩 / step 上限调整（属 (A) #3）。
- 跨 session agent 一等实体持久化（属 (A) #5，需 `_active.md` §5 松绑）。
- LangGraph Studio adapter spike。
- Android 改动。
- LLM provider 抽象层。
- 任何 Letta server 或 SDK 接入。
- `memory_insert` 切到 line-number 语义（保留 substring）。
- 加 `memory_finish_edits` 工具。
- Block multi-agent 共享 / `block_history` / `version` 乐观锁。
- 触碰被 `_active.md` §5 显式禁止的方向。

### 3.3 关键文件清单

修改：

- `backend/runtime/v3_sandbox/schemas.py`
- `backend/runtime/v3_sandbox/graph.py`
- `backend/runtime/v3_sandbox/store.py`
- `backend/api/models.py`
- `backend/api/v3_sandbox.py`
- `backend/tests/`（具体用例 spot-check 后定）
- `web/src/api.ts`
- `web/src/App.tsx`
- `web/tests/`（如有引用）
- `docs/delivery/tasks/_active.md`（设置 Current task = 本 task）

新增：

- `backend/alembic/versions/20260502_0007_v3_drop_legacy_memory_path.py`
- `docs/delivery/handoffs/handoff_2026_05_02_v3_block_schema_and_legacy_cleanup.md`

参考但不修改：

- `~/projects/_references/letta/letta/functions/function_sets/base.py`（`core_memory_replace:263`、`memory_insert:391`、`memory_replace:311`）
- `~/projects/_references/letta/letta/schemas/block.py:13`（BaseBlock 字段参考）
- `docs/adr/ADR-010-letta-as-reference-architecture.md`、`docs/architecture/v3/letta-comparison.md`

## 4. 决策记录（grill 收敛后的最终口径）

| ID | 决策 | 选定值 | 理由 |
|---|---|---|---|
| **Q2a** | `memory_insert` 语义 | 保留 V3 substring (`insert_after`) + 加 line-number 防御 docstring | 模型对 substring anchor 理解更稳；切 line-based 需先造 line-numbered view，是另一档改动 |
| **Q2b** | `memory_replace` 多匹配行为 | 切 Letta unique-or-raise；移除 `replace_all` 参数；多匹配时 raise 并报每行行号 | 替换错位是销售场景高风险点；让模型显式提供更多上下文比静默替换第一处更安全 |
| **Q2c** | 是否加 `memory_rethink` | **本 task 不加**；**留待后续 task** | (1) 当前 4 步上限下 agent 几乎不会主动重写整块；(2) 与 (A) #3 context 压缩 / step 上限提升耦合；(3) **用户明确这是最终产品关键能力，必须做，但应在后续 task 与 step 上限提升一同评估** |
| **Q2d** | Block default `limit` | 上限 `le=100000`；5 个 block default 差异化（persona 2k / human 5k / product 10k / sales_strategy 5k / customer_intelligence 20k） | 销售场景下 customer_intelligence 增长最快，2k 几条线索就触顶；其他按职责量级合理化 |
| **Q2e** | Block `description` 内容 | 5 段中文（见 §3.1.1 表） | 与现有 system prompt 风格一致；让模型从 prompt 中读出"这个 block 是干什么的"，提升 tool 选择准确率 |
| **Q2f** | legacy 持久化清理方式 | (b) 一次性 Alembic drop migration + 配套删 6 处代码；**不** rewrite 现有 session payload_json | POC opt-in 没有生产数据；rewrite 引入额外风险；新 schema `extra='ignore'` 已能容忍旧 JSON 读出 |

## 5. 验证清单

按 `backend-local-verify` + `web-build-verify` + `db-migration-verify` 风格组合：

### 5.1 强制必跑

```bash
# Schema / native runtime 单元测试
backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py backend/tests/test_tokenhub_client.py -q

# 全量 backend 测试
backend/.venv/bin/python -m pytest backend/tests -q

# Alembic 双向迁移（SQLite）
OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_v3_block_schema_cleanup.db backend/.venv/bin/alembic -c alembic.ini upgrade head
OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_v3_block_schema_cleanup.db backend/.venv/bin/alembic -c alembic.ini downgrade -1
OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_v3_block_schema_cleanup.db backend/.venv/bin/alembic -c alembic.ini upgrade head

# Web build + e2e
cd web && npm run build && npm run test:e2e
```

### 5.2 强制必跑（Postgres，如本地有 docker）

```bash
docker compose -f compose.postgres.yml up -d
OPENCLAW_BACKEND_DATABASE_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/alembic -c alembic.ini upgrade head
OPENCLAW_BACKEND_DATABASE_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/alembic -c alembic.ini downgrade -1
OPENCLAW_BACKEND_DATABASE_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/alembic -c alembic.ini upgrade head
docker compose -f compose.postgres.yml down
```

### 5.3 选做（Real TokenHub smoke）

仅当 `backend/.env` 已配置且用户明确允许跑：

- DB-mode backend + native FC 单 turn，确认：
  - core memory block `description` 出现在 system prompt
  - tool events 包含 `core_memory_append` 和 `send_message`
  - `memory_replace` 多匹配场景 raise 出包含行号的错误并被 agent 处理

不读取 `.env` 内容；只 `test -f backend/.env` 与 `git check-ignore -v backend/.env`。

### 5.4 不触发

- Android `./gradlew` 任何 task（无 Android 改动）
- Letta 仓库任何运行（仅引用源码）

## 6. 风险与已知限制

- **Q2b unique-or-raise 在多匹配场景下增加 agent 重试成本**：模型可能要再发一次更长的 `old_content`。预期影响小，但需在 5.3 smoke 时观察。
- **(b) 迁移 downgrade 不恢复数据**：与 `_active.md` POC 边界一致；如果未来需要历史 V2 action 数据，唯一回退是从备份恢复，本 task 不提供数据备份能力。
- **`description` 占 system prompt token**：5 段加起来约 300 中文字符 ≈ 600 token；当前没有压缩，无碍。
- **`metadata` 字段未在本 task 使用，仅预留**：避免后续 (A) task 再做一次 schema 迁移。
- **Web 前端清理量未 spot-check**：实施时先 grep `memory_items / memory_transitions / memoryItems / memoryTransitions`，按结果决定改动范围。

## 7. 后续建议

仅候选，**不**自动开工：

1. **`memory_rethink` 工具 + step 上限提升 + context 摘要**（合并为后续 task；用户已确认 `memory_rethink` 是最终产品关键能力，必须做） —— 对应 ADR-010 §6 #3 与 Q2c。
2. ADR-010 §6 #4 archival memory（需 `_active.md` §5 松绑 + ADR-011 圈定 schema / embedding provider）。
3. ADR-010 §6 #5 跨 session agent 一等实体（需 §5 松绑；与 #4 schema 设计耦合）。
4. ADR-010 §6 #6 recall memory（在 #4 之后再评估）。

执行 agent **不得**自行从候选中开工 —— 须由用户在 `_active.md` 显式开放。
