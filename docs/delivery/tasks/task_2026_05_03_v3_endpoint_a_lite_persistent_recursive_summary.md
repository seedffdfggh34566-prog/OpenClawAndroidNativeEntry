# Task：V3 端点 A-lite 持久化递归摘要

更新时间：2026-05-03

## 1. 任务定位

- 任务名称：V3 端点 A-lite 持久化递归摘要
- 当前状态：`completed`
- 优先级：P1
- 任务类型：`backend runtime / memory / context management / db schema`
- 是否属于 delivery package：`no`
- 上游：`docs/delivery/tasks/task_2026_05_02_v3_memory_rethink_step_limit_context_compression.md`（已 completed，附录 C 含本任务的设计推导）

## 2. 授权来源

用户在当前线程（grill-me session 2026-05-03）明确：

1. 摆脱上一 task 附录 C.3.3 的"迭代式重摘要"折中。
2. 选择**端点 A-lite**：summary 持久化在 session 上、跨 turn 复用、真正递归压缩；不引入 archival_memory / conversation_search（销售场景不必要 + 触碰 ADR-010 §6 #4 禁区）。
3. 摘要后 LLM payload 形状恒为 `[system, summary_msg, 最近 32 条原文]`（Letta 模式 / Option II）。
4. summary 劣化兜底机制本期只做 **β（prompt 工程化保留清单）**；**γ（周期性硬刷新）**留位记录但不实现。
5. 销售场景的角色模型澄清：**user = 销售员（用 OpenClaw 的人）**；agent 帮其厘清自家产品 + 挖掘候选客户线索。β 保留清单据此调整。

## 3. 范围

### 3.1 Schema 变更

`V3SandboxSession` 新增三个字段：

| 字段 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `context_summary` | `str \| None` | `None` | 持久化的递归摘要文本 |
| `summary_cursor_message_id` | `str \| None` | `None` | 已被摘要吸收的最后一条消息的 id；`None` 表示尚未发生过摘要 |
| `summary_recursion_count` | `int` | `0` | 递归次数计数；为 γ 兜底机制留位，本期不消费 |

### 3.2 持久化（无 Alembic migration）

`V3SandboxSession` 已经以 Pydantic JSON 整体写入 `v3_sandbox_sessions.payload_json`（见 `backend/runtime/v3_sandbox/store.py`）。新增 3 个字段会自动随 dump/validate 进出 JSON blob：

- 老 payload 缺这 3 个 key 时，Pydantic 用 schema 默认值（`None / None / 0`）填充
- 不需要 Alembic 列变更
- 不需要 upgrade / downgrade 脚本

### 3.3 Runtime 行为（`backend/runtime/v3_sandbox/graph.py`）

**触发条件**：与上一 task 一致，`total_tokens >= context_window * 0.75`。`total_tokens` 包括 system prompt、cursor 之后的全部历史、当前 user turn、（如有）已存的 `context_summary`。

**触发后行为**（Option II / Letta 式）：

1. 算"摘要输入" = `(已存的 context_summary 文本，如有) + (cursor 之后到 messages[-33] 之间的原文)`
2. LLM 调用，prompt 见 §3.4
3. 把返回的新摘要写回 `session.context_summary`
4. 把 `summary_cursor_message_id` 推进到 `messages[-(32+1)]` 的 id（让 recent 段恒为 32 条原文）
5. `summary_recursion_count += 1`
6. 当前 turn 的 LLM payload = `[system, summary_msg(from context_summary), recent_history(cursor 之后的 32 条)]`

**未触发时**：

- 若 `context_summary` 已存在：LLM payload 仍含 `summary_msg`（因为消息原文已被 cursor 截断）
- 若 `context_summary` 不存在：维持当前行为

**重要**：`session.messages` 全量保留在 DB（不物理 trim），只是 LLM 视野中 cursor 之前的原文不再可见。

### 3.4 摘要 prompt（β 保留清单）

替换当前 prompt（"Summarize the following conversation into 1-2 sentences..."）为销售员-agent 角色模型对应版本：

```
You are summarizing the older portion of a conversation between a salesperson
(the user — they sell a product/service via OpenClaw) and the V3 sales-agent
assistant. The seller is using the agent to clarify their own product and
identify candidate customer leads.

Compress conversational flow but PRESERVE VERBATIM:
- The seller's exact wording about what they sell (positioning, capabilities,
  constraints, pricing tiers, units of measurement)
- Numbers the seller mentioned (prices, headcount, dates, market size, deal sizes)
- Names the seller mentioned (competitors, partners, channels, candidate leads)
- The seller's stated constraints, hesitations, and explicit corrections to
  the agent's prior interpretations
- The seller's description of the ideal customer profile (industry, role,
  geography, signals)

If a previous summary is provided, treat it as authoritative for content
older than the new messages, and merge the new messages into it.

Output: 1-3 sentences for narrative continuity, followed by a "Key facts:"
bullet list of preserved verbatim items.
```

### 3.5 Replay / Reset 语义

- **Replay**：`/v3/sandbox/replay` 重新派生 summary，不复用持久化值。Replay 必须可从原文确定性重建。
- **Session reset**：清空 3 个新字段。
- **Runtime-config reset**：不动 session 字段。

### 3.6 Trace / /lab 暴露

- `V3SandboxTraceEvent.runtime_metadata` 增加：`context_summary_present`、`summary_cursor_message_id`、`summary_recursion_count`、`summary_chars`、（如本 turn 有摘要动作）`summary_action: "created" | "refreshed" | "noop"`
- 摘要动作发生时 `runtime_metadata.summary_llm_usage` 记录该次摘要 LLM 调用的 token 用量
- /lab Settings panel 不需要新控件；trace inspector 自动展示新字段

### 3.7 测试覆盖

新增/调整测试（`backend/tests/test_v3_sandbox_runtime.py`）：

1. **`test_context_compression_persists_summary_and_cursor`**：触发首次摘要后，session 上 3 个新字段被写入；下一次构建 LLM payload 时 cursor 之前的原文不出现在 messages 列表里。
2. **`test_context_compression_recursive_uses_prior_summary`**：第二次触发时，摘要输入包含上次的 `context_summary`（mock LLM call，断言 prompt 含上次 summary 文本）。
3. **`test_context_compression_recent_window_is_always_32_after_summary`**：摘要后 LLM payload 中 recent 段恒为 32 条原文。
4. **`test_replay_does_not_reuse_persisted_summary`**：replay 时 `context_summary` 被重新派生而非读旧值。
5. **`test_session_reset_clears_summary_fields`**：reset session 后 3 个字段回到默认。
6. **改写 `test_context_compression_triggers_on_token_threshold`**：增加"summary 持久化到 session"断言；移除"len(session.messages) == messages_before"（现在 summary 作为 session 字段持久化，但不再混入 session.messages 数组）。

### 3.8 Out of scope（**不**做）

- archival memory（ADR-010 §6 #4 禁区）
- conversation_search 工具
- γ 周期性硬刷新（仅文档记录，预留 `summary_recursion_count` 字段）
- 60% warn 层
- 移除 deepseek-v3.2 from allowlist
- partial-evict 模式
- Android / web UI 重写

## 4. 决策记录

| ID | 决策 | 选定值 | 理由 |
|---|---|---|---|
| **D1** | 端点选择 | A-lite（持久化 summary，不引入 archival/search） | 销售场景下 archival/search 是过度设计；core memory blocks 已承担事实库角色 |
| **D2** | 摘要后 LLM 视野形状 | Option II（`[system, summary, last 32 raw]`） | 形状恒定便于调试；保留连续上下文；与 max_steps 节奏匹配 |
| **D3** | Cursor 类型 | message_id（字符串） | 比 index 更稳健；message 数组若有插入/编辑不至于错位 |
| **D4** | 劣化兜底 | β prompt 必做；γ 仅文档预留 | POC 单 session ≤ 50 turn 时累积漂移基本不存在；γ 提前实现属过度工程 |
| **D5** | 角色模型 | user = 销售员，非 end-customer | 调整 β 保留清单方向 |
| **D6** | Replay 语义 | 重新派生 | replay 需从原文确定性重建 |
| **D7** | 物理 trim | 不做（session.messages 全量保留 in DB） | /lab 调试需要 + recovery 兜底（万一 summary 写坏可手工重建） |

## 5. 验证清单

### 5.1 强制必跑

```bash
backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -x -q
backend/.venv/bin/python -m pytest backend/tests -q
OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_v3_a_lite.db backend/.venv/bin/alembic -c alembic.ini upgrade head
cd web && npm run build
```

（无 schema 变更，alembic upgrade 仅作 regression 检查；无需 downgrade 验证）

### 5.3 选做（real LLM smoke）

- 配 `backend/.env`，跑 30+ turn 长会话，确认：
  - 首次摘要触发时 cursor 推进、summary 持久化
  - 后续 turn 不再重复 LLM 摘要调用
  - 第二次触发时 prompt 含上次 summary
  - /lab trace inspector 显示 summary_recursion_count 增长

## 6. 风险与已知限制

- **Summary 劣化**：β 只能减缓不能根除；超过 100+ turn 的会话需要触发 §C.6 退出条件（来自上一 task 附录），届时考虑 γ 或迁移到完整端点 A
- **Replay 行为变化**：原 replay 无 summary 状态，新 replay 会重新派生 → 若 mock LLM 不够稳定可能产生不同 summary 文本，但 trace 形状仍可对比
- **Migration 顺序敏感**：若先升级代码再 alembic upgrade，运行时会读到不存在的字段。规范操作顺序：alembic upgrade → 启动新代码

## 7. 后续建议

仅候选，**不**自动开工：

1. γ 周期性硬刷新（每 K 次递归全量重摘要）—— 等长会话场景出现
2. 60% warn 层 —— agent 自主预防
3. ADR-010 §6 #4 archival memory —— 跨 session 长期记忆
4. 从 allowlist 移除 deepseek-v3.2
