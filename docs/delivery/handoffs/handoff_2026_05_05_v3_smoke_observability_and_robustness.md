# Handoff — V3 Smoke 可观测性与鲁棒性改进（2026-05-05）

## 1. 范围

执行 `task_2026_05_05_v3_smoke_observability_and_robustness`，合并完成第 1~4 批改进：

- **P0 可观测性**：runtime 侧上报 75%/90%/95% 三档阈值的实际 token 数值；smoke 脚本侧正确消费并展示
- **P2 失败处理**：四级 outcome 分类（success / runtime_seam / platform_error / quota_error）、402 差异化处理、JSONL flush
- **P3 预检与预算**：`--preflight` 1-turn 预检模式、`--max-tokens-budget` graceful stop

**未包含**（按用户修正）：
- ACT-8 memory block self-compaction 场景（预算过高，暂不执行）
- 孤儿消息回滚（确认为预期行为，仅在文档中说明）

## 2. 改动文件

| 文件 | 变更类型 | 说明 |
|---|---|---|
| `backend/runtime/v3_sandbox/graph.py` | 修改 | 四处 metadata 写入 + `_continue_or_return` guard 提前执行 |
| `backend/scripts/v3_comprehensive_live_smoke.py` | 修改 | 字段重命名、outcome 分类、CLI flag、retry 逻辑、JSONL flush |
| `backend/tests/test_v3_sandbox_runtime.py` | 修改 | 新增 4 个单元测试 |
| `docs/delivery/tasks/_active.md` | 修改 | 标记当前 task 为 in_progress |
| `docs/delivery/tasks/task_2026_05_05_v3_smoke_observability_and_robustness.md` | 新增 | 任务定义 |

## 3. Runtime 侧改动详情

### 3.1 Metadata 上报

在 `backend/runtime/v3_sandbox/graph.py` 中，以下字段现在写入 `state["runtime_metadata"]`，最终通过 `trace_event.runtime_metadata` 暴露给 smoke 脚本：

| 字段 | 写入位置 | 计算范围注释 |
|---|---|---|
| `context_pressure_tokens` | `_build_tool_loop_messages` | turn 开始时初始 payload（system prompt + memory blocks + summary + after_cursor + user_message），**不含 tool loop** |
| `context_pressure_threshold` | 同上 | 0.75 × context_window |
| `context_pressure_triggered` | 同上 | bool |
| `summarization_token_count` | `_maybe_run_summarization` | 同上（与 pressure 同一 payload，独立 encode） |
| `summarization_action` | 同上 | created / refreshed / noop_below_threshold / ... |
| `guard_tool_tokens` | `_continue_or_return` | 当前累积 tool_messages 的 token 数（**含 tool loop**） |
| `guard_tool_threshold` | 同上 | 0.95 × context_window |

**注意**：`llm_usage` 已在 `_return_turn` 中通过 `state.get("usage_total")` 写入 trace event metadata，本次任务只需消费，无需新增 runtime 代码。

### 3.2 `_continue_or_return` 执行顺序修正

原实现先检查 `final_message` 再检查 95% guard，导致正常回合的 `guard_tool_tokens` 永远不被写入（因为 `final_message` 存在时直接 `return`，跳过 guard 块）。

**修正**：将 guard 块移到 `final_message` 检查之前，确保每一轮都会记录 guard 指标。即使 `final_message` 已设置，如果 tool_messages 意外超过 95% 阈值，也会优先触发 `context_budget_exhausted` 返回，提升安全性。

## 4. Smoke 脚本改动详情

### 4.1 字段重命名与新增

`TurnMetrics` 中以下字段替换/新增：

- 删除 `token_count_from_metadata`（语义错位，原读的是 `context_summary_chars`）
- 新增 `summary_chars`：真正的 `context_summary_chars`
- 新增 `prompt_tokens_estimate`：脚本端 tiktoken 估算（fallback）
- 新增 `llm_usage`：读 `runtime_metadata["llm_usage"]`
- 新增 `context_pressure_tokens` / `context_pressure_threshold` / `context_pressure_triggered`
- 新增 `summarization_token_count` / `summarization_action`
- 新增 `guard_tool_tokens` / `guard_tool_threshold`
- 新增 `outcome`：四级分类结果

删除 `_detect_warning_in_prompt` 的字符串 grep 逻辑；`prompt_included_warning` 改为直接读 `context_pressure_triggered`。

### 4.2 失败 turn 也写 memory snapshot

except 分支现在调用 `_extract_memory_lengths(session)` 和 `_extract_memory_snapshots(session)`，让 errors 列表中的 turn 也有完整的 memory 状态，而不是空 dict。

### 4.3 四级 outcome 分类

| outcome | 判定条件 | 是否计入失败 |
|---|---|---|
| `success` | 无 error，有 tool_calls | 否 |
| `runtime_seam` | `v3_tool_loop_no_tool_call` | **否** |
| `platform_error` | HTTP 4xx/5xx，排除 quota | 是 |
| `quota_error` | `FREE_QUOTA_EXHAUSTED` 或 quota 耗尽 | 是（立即终止） |

退出码：
- `0`：全部 success / runtime_seam
- `2`：存在 platform_error
- `3`：存在 quota_error（incomplete）

### 4.4 402 / 429 差异化处理

- `FREE_QUOTA_EXHAUSTED` → `quota_error`，**立刻终止整次 smoke**
- 429 或 body 含 "rate" / "limit" → 指数退避重试（最多 3 次，间隔 1s / 2s / 4s）
- 其它 HTTP 错误 → `platform_error`

### 4.5 JSONL flush + 收尾验证

每写一行 JSONL 后 `f.flush()`，确保崩溃前保留已跑轮次。
收尾处检查 `final_jsonl_path` 是否存在；若缺失打印 warning 并保留 `current_smoke.jsonl`。

### 4.6 CLI 新 flag

- `--preflight`：只跑 1-turn 自我介绍，< 30 秒，验证 API key 和连通性
- `--max-tokens-budget N`：累加 `total_tokens`，超限后 graceful stop

### 4.7 孤儿消息说明

脚本 docstring 新增段落，明确说明"失败 turn 的 user message 保留在 session.messages 中是预期行为，与主流 agent / LLM 平台一致"。

## 5. 单元测试

新增 4 个测试，全部通过：

| 测试 | 验证点 |
|---|---|
| `test_pressure_warning_metadata_fields_written` | mock tiktoken 超 75%，验证 `context_pressure_tokens` / `threshold` / `triggered` |
| `test_summarization_metadata_fields_written` | mock tiktoken 超 90%，验证 `summarization_token_count` 和 `summarization_action` |
| `test_guard_tool_tokens_written` | mock tiktoken 超 95%，验证 `guard_tool_tokens` / `threshold` 以及 `early_return_reason` |
| `test_smoke_outcome_classifier` | 通过 `importlib.util` 加载 smoke 脚本，验证四级分类逻辑和辅助函数 |

## 6. 验证结果

- `backend/tests/test_v3_sandbox_runtime.py`：**46 passed**（原 42 + 新增 4）
- `backend/tests` 全量：**178 passed, 18 skipped**（0 regression）
- **Preflight live smoke**（minimax-m2.7, 1 turn）：成功，新字段全部正确填充：
  - `llm_usage`: {"prompt_tokens": 6203, "completion_tokens": 344, "total_tokens": 6547}
  - `context_pressure_tokens`: 522, `threshold`: 150000, `triggered`: false
  - `summarization_action`: "noop_insufficient_messages"
  - `guard_tool_tokens`: 1398, `threshold`: 190000
  - `outcome`: "success"

## 7. 已知限制

- `prompt_tokens_estimate` 是脚本端 tiktoken 重算，与 runtime 真实计费口径有差异（preflight 中 219 vs 522）。这是因为脚本端用简化 system prompt（只含 block values，不含 description/limit 行）估算。该字段仅用于趋势观察，不应作为计费依据。
- `summarization_token_count` 与 `context_pressure_tokens` 在多数回合中数值相同（同一 payload 独立 encode），后续可优化为只 encode 一次。
- Guard 块提前执行后，正常回合也会多做一次 tiktoken encode（tool_messages JSON）。开销极小（几毫秒），但如需极致优化可改为只在 `_execute_tool_calls` 中写一次。
- Smoke 脚本仍为 untracked（`backend/scripts/` 目录整体未进 git），这是历史状态，本次未改变。

## 8. 推荐后续动作

1. **第 5~6 批（threshold 触发场景）**：在 `task_2026_05_05_v3_smoke_observability_and_robustness` 完成后，可独立立项设计 ACT-6 / ACT-7，专门在 live 中打出 75% / 90% 触发。
2. **第 7~8 批（ACT 模块化 + baseline diff + 严格断言）**：等第 5~6 批跑通后再做，避免过早抽象。
3. **prompt_tokens_estimate 精度提升**：如果需要更准确的脚本端估算，可以让 `_build_tool_loop_messages` 把实际 `system_prompt` 也写进 metadata，脚本直接消费，而不是自己重拼。
