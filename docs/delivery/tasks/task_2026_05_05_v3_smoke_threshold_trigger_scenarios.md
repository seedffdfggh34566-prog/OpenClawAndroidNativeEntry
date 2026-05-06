# Task：V3 Smoke 上下文阈值触发场景（第 5~6 批）

更新时间：2026-05-05

## 1. 任务定位

- 任务名称：V3 Smoke 上下文阈值触发场景
- 当前状态：`in_progress`
- 优先级：P1
- 任务类型：`test / scenario design`
- 是否属于 delivery package：`no`
- 上游：`docs/delivery/tasks/task_2026_05_05_v3_smoke_observability_and_robustness.md`（已 completed）

## 2. 授权来源

用户在当前线程明确授权：

1. 继续执行第 5~6 批，让 75%/90% 阈值在 live smoke 中真实触发。
2. 2.4（ACT-8 memory block self-compaction）暂不执行。
3. 方案选择以"不改 graph.py"为优先；如果必须改，需单点说明。

## 3. 范围

### 3.1 Smoke 脚本侧：上下文饱和预填充（不改 graph.py）

核心思路：通过预填充大量大消息到 `session.messages`，在不改变 `max_context_messages=32` 的前提下，让 `after_cursor` 的 token 量自然超过 150K/180K 阈值。

- 新增 `_prefill_saturation_history(session, n_messages=60, chars_per_message=3000)`
- 预填充消息内容嵌入早期事实（姓名、公司、产品），用于后续"摘要后回忆"验证
- 预填充消息为 user/assistant 交替，模拟真实对话历史
- 预填充本身**不消耗 LLM token**，仅在脚本端生成

### 3.2 CLI 新 flag

- `--context-saturation`：启用预填充模式
- 当该标志启用时，session 创建后立即预填充 60 条大消息
- 然后正常跑 ACT-1~ACT-5（35 轮）
- 预期：第 1 轮可触发 75% pressure warning（受 rate limit 约束，90% 摘要在 36 轮内可能不触发）

### 3.3 摘要后早期信息回忆验证

在 ACT-5 结束后，若 `context_summary_present=True`，追加一轮：

```
请帮我回忆一下我们之前的对话：
1）我叫什么名字？
2）我的公司叫什么？
3）我们产品的核心功能是什么？
```

Soft assertions：
- 回答中必须包含预填充中嵌入的早期事实（"李明"、"云算智能"、"财税" 或 "发票"）
- 若 `context_summary_present=False`（摘要未触发），本轮跳过但不失败

### 3.4 Pressure Warning Effectiveness Check（2.5）

在 post-run assertions 中增加：

- 若 `context_pressure_triggered=True`，统计 warning 前后各 5 轮的 `memory_rethink` 调用次数
- 断言：warning 后的 rethink 次数不应显著增加（`<= before + 1`）
- 该断言为 soft，不阻塞退出码

### 3.5 报告增强

`report_data` 中新增：

- `"saturation_mode": true/false`
- `"prefill_message_count"`
- `"recall_verification": {"attempted": bool, "passed": bool}`
- `"pressure_warning_effectiveness": {"warning_turn": int, "rethink_before": int, "rethink_after": int}`

## 4. 范围外

- 不修改 `backend/runtime/v3_sandbox/graph.py`
- 不修改 `backend/api/config.py`（settings）
- 不引入 ACT-8（memory block self-compaction）
- 不修改 75/90/95 阈值比例

## 5. 验证

- `backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -x -q`
- `backend/.venv/bin/python -m pytest backend/tests`（全量无 regression）
- 若用户授权且 quota 充足：跑一次 `--context-saturation` preflight（1 轮）验证 75% 触发
- 完整 saturation run 因 quota/时长原因，可在用户授权后执行

## 6. 已知限制

- 预填充消息会显著增加首轮 prompt 的 tiktoken encode 时间（约 150K tokens ≈ 0.5-1s）
- 90% 摘要触发时，`to_absorb` 可能包含大量预填充消息，摘要 LLM 调用成本较高
- 预填充消息中的早期事实能否被摘要正确保留，取决于 minimax-m2.7 的摘要能力
- 完整 saturation run 预估耗时 25-40 分钟，消耗约 300-500K 输入 tokens
