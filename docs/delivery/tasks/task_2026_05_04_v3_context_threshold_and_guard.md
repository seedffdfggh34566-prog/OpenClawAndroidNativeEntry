# Task：V3 上下文阈值提升、Pressure Warning、Tool Loop Guard 与前端暴露

更新时间：2026-05-04

## 1. 任务定位

- 任务名称：V3 上下文阈值提升、Pressure Warning、Tool Loop Guard 与前端暴露
- 当前状态：`completed`
- 优先级：P1
- 任务类型：`backend runtime / memory / context management / web frontend / test`
- 是否属于 delivery package：`no`
- 上游：`docs/delivery/tasks/task_2026_05_03_v3_endpoint_a_lite_persistent_recursive_summary.md`（已 completed）

## 2. 授权来源

用户在当前线程（plan mode session 2026-05-04）通过 approved plan (`/home/yulin/.claude/plans/curious-twirling-lemur.md`) 明确授权：

1. 从 allowlist 移除 `deepseek-v3.1-terminus`（128k 窗口过紧）。
2. 统一强制压缩阈值至 **90%**（对齐 Letta ~0.9 实践）。
3. 在 **75%** 时注入 pressure warning，提示 agent 主动整理 memory。
4. 在 tool loop 循环中增加 tiktoken 精确检查（**95%** 时优雅结束 loop）。
5. 空 `final_message` 默认中文兜底消息。
6. 在 system prompt 中补充 `memory_rethink` 使用场景引导。
7. 将 95% guard 的触发信息暴露给前端 `/lab`。
8. 为上述新增功能补写单元测试。

## 3. 范围

### 3.1 模型 allowlist 清理

- `backend/api/v3_sandbox.py`：移除 `"deepseek-v3.1-terminus"`
- `backend/runtime/v3_sandbox/graph.py`：`_MODEL_CONTEXT_WINDOWS` 移除 `"deepseek-v3.1-terminus": 128_000`
- `backend/runtime/tokenhub_native_fc.py`：移除 allowlist 和 policies 中的 `deepseek-v3.1-terminus` 条目

### 3.2 压缩阈值提升

- `_CONTEXT_COMPRESSION_THRESHOLD_RATIO`：`0.75` → `0.90`

### 3.3 Pressure Warning（75%）

- 在 `_build_tool_loop_messages` 中，构建完 `system_prompt` 后计算当前 token 数
- 若 `token_count > context_window * 0.75`：在 `system_lines` 末尾追加 pressure warning（英文）
- Warning 推荐增量操作（`memory_insert` / `memory_replace` / `core_memory_append`），不推荐 `memory_rethink`

### 3.4 Tool Loop Guard（95%）

- 在 `_continue_or_return` 中增加 tiktoken 精确检查
- 若 `token_count > context_window * 0.95`：返回 `"return"`，优雅结束 tool loop
- 在 `runtime_metadata` 中记录 `"early_return_reason": "context_budget_exhausted"`
- 使用 `try/except` 保护 tiktoken 不可用的情况

### 3.5 空 final_message 兜底

- 在 `_return_turn` 中，若 `state.get("final_message", "")` 为空：
  - 设为 `"（Agent 在本轮执行了多个内部操作，但因上下文预算耗尽未发送最终回复。）"`

### 3.6 memory_rethink 引导

- 在 `_build_tool_loop_messages` 的 `user_lines` 末尾补充说明：
  - "Use memory_rethink only for large sweeping reorganizations of a memory block; for small precise edits, prefer memory_insert or memory_replace."

### 3.7 前端暴露

- `web/src/App.tsx`：在 `TraceList` 和 `TraceInspector` sidebar 中，当 `runtime_metadata.early_return_reason === "context_budget_exhausted"` 时显示警告
- `web/src/styles.css`：新增 `.trace-warning` 和 `.trace-warning-badge` 样式

### 3.8 单元测试补写

新增 4 个测试：

| 测试 | 验证点 |
|---|---|
| `test_threshold_changed_to_ninety` | 阈值常量 == 0.90 |
| `test_ninety_five_percent_guard_returns_early` | mock tiktoken 超 95%，验证返回 `"return"` 且记录 `early_return_reason` |
| `test_pressure_warning_injected_above_threshold` | mock tiktoken 超 75%，验证 system prompt 包含 warning |
| `test_empty_final_message_fallback` | 验证空 `final_message` 被填充为中文兜底消息 |

## 4. 验证结果

- `backend/tests/test_v3_sandbox_runtime.py`：**42 passed**
- `backend/tests` 全量：**174 passed, 18 skipped**（0 regression）
- `web build`：通过
- `alembic upgrade head`：通过（无 schema 变更）

## 5. 已知限制

- pressure warning 和 loop guard 均依赖 tiktoken；tiktoken 不可用时静默跳过（符合预期）
- 前端未写自动化测试（web 目录无测试套件）
- 未验证 pressure warning 在真实 LLM 下的行为效果（需 live LLM smoke）
