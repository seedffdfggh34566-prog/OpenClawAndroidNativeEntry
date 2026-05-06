# Task：V3 Smoke 可观测性与鲁棒性改进（第 1~4 批合并）

更新时间：2026-05-05

## 1. 任务定位

- 任务名称：V3 Smoke 可观测性与鲁棒性改进
- 当前状态：`completed`
- 优先级：P1
- 任务类型：`backend runtime / test / observability`
- 是否属于 delivery package：`no`
- 上游：`docs/delivery/tasks/task_2026_05_04_v3_context_threshold_and_guard.md`（已 completed）

## 2. 授权来源

用户在当前线程明确授权：

1. **1.2 + 1.3（runtime metadata 上报）**：将 LLM usage 与上下文三档阈值的实际数值写入 `runtime_metadata`，并在 smoke 脚本消费。三个数值的计算范围必须带注释：
   - `context_pressure_tokens` = turn 开始时的初始 payload token 数（不含 tool loop）
   - `summarization_token_count` = 同上，触发 summarization 检查时的 token 数
   - `guard_tool_tokens` = 当前时刻的完整 tool_messages token 数（含 tool loop）
2. **1.1 + 1.4 + 1.5（脚本可观测性）**：`token_count` 字段拆分为 `summary_chars` + `prompt_tokens_estimate`；删除 `_detect_warning_in_prompt` 的字符串 grep；失败 turn 也写 memory snapshot。
3. **3.1 + 3.3 + 3.4（失败处理与流程）**：四级 outcome 分类（success / runtime_seam / platform_error / quota_error）；402 差异化处理（quota 立即终止 / rate limit 退避重试）；JSONL flush + 收尾验证。
4. **4.1 + 4.4（预检与预算）**：`--preflight` 1-turn 预检模式；`--max-tokens-budget` graceful stop。
5. **3.2（孤儿消息）**：不在脚本或 runtime 做回滚，仅在 docstring / handoff 中补充说明“失败 turn 的 user message 保留在 session.messages 中是预期行为，与主流 agent 平台一致”。
6. **2.4（ACT-8）**：暂不执行，预算过高。

## 3. 范围

### 3.1 Runtime 侧（graph.py）metadata 上报

在 `_build_tool_loop_messages`（75% check）写入：
- `runtime_metadata["context_pressure_tokens"]`
- `runtime_metadata["context_pressure_threshold"]`
- `runtime_metadata["context_pressure_triggered"]`（bool）

在 `_maybe_run_summarization`（90% check）写入：
- `runtime_metadata["summarization_token_count"]`
- `runtime_metadata["summarization_action"]`（来自 return dict 的 action 字段）

在 `_continue_or_return`（95% guard）写入：
- `runtime_metadata["guard_tool_tokens"]`
- `runtime_metadata["guard_tool_threshold"]`

注释要求：在每个写入点加 1-2 行注释，说明该 token 数的计算范围（参考 §2 的三个定义）。

**注意**：`runtime_metadata["llm_usage"]` 已在 `_return_turn` 的 `trace_event` 组装时写入（`state.get("usage_total")`），本次任务只需确认 smoke 脚本能正确消费，无需新增 runtime 代码。

### 3.2 Smoke 脚本侧（v3_comprehensive_live_smoke.py）

**字段重命名与新增**：
- 删除 `token_count_from_metadata`，拆分为 `summary_chars`（读 `context_summary_chars`）和 `prompt_tokens_estimate`（脚本端自算）。
- 新增 `llm_usage`（读 `runtime_metadata["llm_usage"]`）。
- 新增 `context_pressure_tokens`、`context_pressure_threshold`、`context_pressure_triggered`（读对应 metadata）。
- 新增 `summarization_token_count`、`summarization_action`（读对应 metadata）。
- 新增 `guard_tool_tokens`、`guard_tool_threshold`（读对应 metadata）。
- 删除 `_detect_warning_in_prompt` 函数；`prompt_included_warning` 改为直接读 `context_pressure_triggered`。

**失败 turn 也写 memory snapshot**：
- 在 except 分支里补 `_extract_memory_lengths(session)` 和 `_extract_memory_snapshots(session)`。

**四级 outcome 分类**：
- `success`：LLM 正常，至少一次 send_message
- `runtime_seam`：LLM 返回 content 但无 tool_call（本次 turn 7 的类型），**不计入失败**
- `platform_error`：HTTP 4xx/5xx，排除 402 quota，可退避重试
- `quota_error`：HTTP 402 FREE_QUOTA_EXHAUSTED 或 paid plan 余额耗尽，**立刻终止**

**退出码**：
- 0 = 全部 success（含 runtime_seam）
- 2 = 有 platform_error
- 3 = quota_error（incomplete）

**402 差异化**：
- `FREE_QUOTA_EXHAUSTED` → `quota_error`
- 429 或 body 含 "rate" / "limit" → 退避重试（最多 3 次，指数退避）
- 其它 4xx/5xx → `platform_error`

**JSONL 增量输出**：
- 每写完一行 `f.write(...)` 后立刻 `f.flush()`
- 在 `main()` 收尾处检查 `final_jsonl_path` 是否存在；若不存在但 `current_smoke.jsonl` 存在，打印 warning 并保留 `current_smoke.jsonl`

**CLI 新 flag**：
- `--preflight`：只跑 1 个最简单的 turn（自我介绍），< 30 秒，用于验证 API key 与连通性
- `--max-tokens-budget N`：每轮累加 `total_tokens`，超过 N 时 graceful stop（打印预算用尽信息并保存已跑轮的报告）

**文档注释**：
- 脚本顶部 docstring 加一段说明孤儿消息保留在上下文中的预期行为。

### 3.3 单元测试

新增或更新 `backend/tests/test_v3_sandbox_runtime.py`：

| 测试 | 验证点 |
|---|---|
| `test_pressure_warning_metadata_fields_written` | mock tiktoken 超 75%，验证 `runtime_metadata["context_pressure_tokens"]`, `context_pressure_threshold`, `context_pressure_triggered` |
| `test_summarization_metadata_fields_written` | mock tiktoken 超 90%，验证 `runtime_metadata["summarization_token_count"]` 和 `summarization_action` |
| `test_guard_tool_tokens_written` | mock tiktoken 超 95%，验证 `runtime_metadata["guard_tool_tokens"]` |
| `test_runtime_seam_classified_not_error` | 验证 no_tool_call 场景被 `runtime_metadata` 正确标记（如果 runtime 不标记，则至少验证脚本端 outcome 分类逻辑） |
| `test_smoke_outcome_classifier` | 对 smoke 脚本的 outcome 分类函数做纯单元测试 |

### 3.4 验证

- `backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -x -q`
- `backend/.venv/bin/python -m pytest backend/tests`（全量无 regression）
- 若用户授权 live key：跑一次 `--preflight` 验证连通性

## 4. 已知限制

- 本次任务**不引入新 ACT**，不修改 75/90/95 阈值比例，不修改 graph.py 决策逻辑。
- `prompt_tokens_estimate` 在脚本端用 tiktoken 重算，与 runtime 的真实计费口径可能有几百 tokens 差异，仅用于趋势观察。
- 95 % guard 的 `guard_tool_tokens` 只有在 tool loop 运行时才有值；对于未进入 tool loop 的 turn（如 no_tool_call），该字段为 0 或未写。

## 5. 边界约束

- runtime 改动仅限 `backend/runtime/v3_sandbox/graph.py`
- smoke 改动仅限 `backend/scripts/v3_comprehensive_live_smoke.py`
- 测试改动仅限 `backend/tests/test_v3_sandbox_runtime.py`
- 不得修改 `backend/api/services.py`、`backend/api/models.py`、`backend/api/schemas.py` 等 product truth 层文件
