# Handoff — V3 Smoke 上下文阈值触发场景（第 5~6 批）（2026-05-05）

## 1. 范围

执行 `task_2026_05_05_v3_smoke_threshold_trigger_scenarios`，完成第 5~6 批改进：

- **上下文饱和预填充**：在不修改 graph.py 的前提下，通过预填充大量合成消息到 `session.messages`，让 75%/90% 阈值在 live smoke 中真实触发。
- **摘要后早期信息回忆验证**：在 saturation mode 下，若触发了 summarization，追加一轮 recall turn 验证早期事实是否被保留。
- **Pressure Warning Effectiveness Check**：统计 warning 前后各 5 轮的 `memory_rethink` 调用次数，验证 warning 不会导致 rethink 激增。
- **报告增强**：在 `report_data` 中新增 saturation 相关字段。

**未包含**（按用户修正）：
- ACT-8 memory block self-compaction 场景（预算过高，暂不执行）
- 修改 graph.py 或 75/90/95 阈值比例

## 2. 改动文件

| 文件 | 变更类型 | 说明 |
|---|---|---|
| `backend/scripts/v3_comprehensive_live_smoke.py` | 修改 | 新增预填充、recall verification、pressure effectiveness、报告字段 |
| `backend/tests/test_v3_sandbox_runtime.py` | 修改 | 新增 3 个 prefill 单元测试 |
| `docs/delivery/tasks/_active.md` | 修改 | 标记当前 task 为 completed |
| `docs/delivery/tasks/task_2026_05_05_v3_smoke_threshold_trigger_scenarios.md` | 已存在 | 任务定义 |
| `docs/delivery/handoffs/handoff_2026_05_05_v3_smoke_threshold_trigger_scenarios.md` | 新增 | 本 handoff |

## 3. Smoke 脚本改动详情

### 3.1 上下文饱和预填充

新增 `_prefill_saturation_history(session, n_messages=60, chars_per_message=3000)`：

- 预填充 60 条消息（约 3K chars/条），总 token 量约 45K-60K，首轮可触发 75% pressure warning（取决于 model 的 75% threshold）。由于 rate limit 限制，90% summarization 在 36 轮内可能不会被触发。
- 消息角色为 user/assistant 交替，模拟真实对话历史。
- 前 4 条消息嵌入早期事实（姓名、公司、产品、价格），用于 recall verification。
- 预填充**不消耗 LLM token**，仅在脚本端本地生成。

新增 CLI flag `--context-saturation`：启用预填充模式。

### 3.2 Recall Verification

当 `--context-saturation` 启用时：
- `turns` 列表追加 `RECALL_TURN`（在 ACT-5 的 15 轮之后）。
- ACT 名称逻辑显示 `RECALL`（turn_idx >= 35）。
- Post-run 中检查：
  - 若 `context_summary_present=True`（即 summarization 触发过），检查 recall turn 的 assistant 回复中是否包含早期事实关键词（"李明"、"云算智能"、"财税"/"发票"、"399"）。
  - 若 summarization 未触发，跳过但不失败。
  - 结果写入 `report_data["recall_verification"]`。

### 3.3 Pressure Warning Effectiveness Check

Post-run 中新增：
- 找到第一个 `context_pressure_triggered=True` 的 turn。
- 统计 warning turn 前后各 5 轮中 `memory_rethink` 的调用次数。
- Soft check：若 `rethink_after > rethink_before + 1`，打印 WARN 但不阻塞退出码。
- 结果写入 `report_data["pressure_warning_effectiveness"]`。

### 3.4 报告增强

`report_data` 新增字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `saturation_mode` | bool | 是否启用了上下文饱和 |
| `prefill_message_count` | int | 预填充消息数量（60） |
| `recall_verification` | dict | `attempted`, `passed` |
| `pressure_warning_effectiveness` | dict | `warning_turn`, `rethink_before`, `rethink_after` |

## 4. 单元测试

新增 3 个测试，全部通过：

| 测试 | 验证点 |
|---|---|
| `test_prefill_saturation_history_appends_messages` | 预填充追加 60 条消息，角色交替正确 |
| `test_prefill_saturation_history_embeds_early_facts` | 前 4 条消息包含 `PREFILL_EARLY_FACTS` |
| `test_prefill_saturation_history_message_length` | 每条消息长度约 5000-10000 chars |

## 5. 验证结果

- `backend/tests/test_v3_sandbox_runtime.py`：**49 passed**（原 46 + 新增 3）
- `backend/tests` 全量：**181 passed, 18 skipped**（0 regression）

## 6. 已知限制

- 预填充消息会增加首轮 prompt 的 tiktoken encode 时间（约 45K-60K tokens ≈ 0.2-0.5s）。
- `chars_per_message` 已从 10K 下调至 3K，以规避 minimax-m2.7 的 `input_tpm` rate limit（首轮 150K+ tokens 触发 429）。下调后 90% summarization 在 36 轮内可能不会被触发。
- 预填充消息中的早期事实能否被摘要正确保留，取决于 minimax-m2.7 的摘要能力。
- 完整 saturation run 预估耗时 15-25 分钟，消耗约 150-250K 输入 tokens。
- Smoke 脚本仍为 untracked（`backend/scripts/` 目录整体未进 git），这是历史状态，本次未改变。

## 7. 推荐后续动作

1. **Live 验证**：在用户授权且 quota 充足时，跑一次 `--context-saturation --preflight`（1 轮）验证 75% 触发逻辑；再跑完整 saturation run（36 轮）。
2. **第 7~8 批（ACT 模块化 + baseline diff + 严格断言）**：等 saturation run 跑通后再做，避免过早抽象。
