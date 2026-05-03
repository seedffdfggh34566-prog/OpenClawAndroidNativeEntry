# Task：V3 memory_rethink + Step 上限提升 + Context 压缩/摘要

更新时间：2026-05-02

## 1. 任务定位

- 任务名称：V3 memory_rethink + Step 上限提升 + Context 压缩/摘要
- 当前状态：`completed`
- 优先级：P1
- 任务类型：`backend runtime / memory tools / context management`
- 是否属于 delivery package：`no`
- 对应 ADR-010 §6 推荐缺口：**#3（Context 压缩 / step 上限调整）+ memory_rethink（Q2c 留待后续）**

## 2. 授权来源

用户在当前线程（grill-me session）明确确认：

1. 将 (A) #3 与 `memory_rethink` **合并为同一个 task**。
2. Step 上限从 4 提升到 **16**，并在 **Web lab 上可由人调节**，默认 16，调节范围 **4–50**。
3. Context 压缩策略选 **B（轻量摘要）**，按 **token 数触发**。
4. `memory_rethink` **完整复刻 Letta 语义**：独立工具，接受 `label` + `new_memory`，完全替换 block value，用于大范围整理/压缩。
5. 摘要插入位置 **参考 Letta 方法**（作为 user message 插入 context）。
6. **先通过文档落实再进行代码执行**（避免工作中断后 scope 丢失）。

## 3. 范围

### 3.1 `memory_rethink` 工具

新增 `memory_rethink` 到 `backend/runtime/v3_sandbox/graph.py::_core_memory_tools()`。

- **参数**：`label: str`（目标 block 标签），`new_memory: str`（新的完整内容）。
- **行为**：完全替换 `core_memory_blocks[label].value`。
- **limit 检查**：替换后的内容长度必须 `<= block.limit`，否则 raise `core_memory_block_value_exceeds_limit`。
- **docstring**：复刻 Letta `function_sets/base.py:488` 风格，明确说明：
  - "用于大范围整理/压缩/重组 memory block"
  - "不用于小编辑（如 add/remove/replace 单条内容）"
  - 中文措辞，针对销售场景调整。
- **防御**：检查 `new_memory` 中是否包含 line-number prefix（`\nLine \d+: `）或 `CORE_MEMORY_LINE_NUMBER_WARNING`，如有则 raise（复刻 Letta 防御）。
- **不引入 `memory_finish_edits`**：V3 没有 Letta 的"编辑会话"概念。

### 3.2 Step 上限提升

修改 `backend/runtime/v3_sandbox/graph.py::_continue_or_return()`：

- 将 `call_count >= 4` 的硬编码改为读取 **runtime config 中的 `max_steps`**。
- 默认值：**16**。
- 保留 `tool_events >= 16` 作为 fallback 硬上限（或同步提升为 `max_steps * 4`，在 task 实施时决定）。
- 当 `call_count >= max_steps` 时，抛 `v3_tool_loop_exhausted`。

### 3.3 Context 压缩/摘要

**触发条件**：按 **token 数**。

- **Token 计数方案**：引入 `tiktoken`（`cl100k_base`）作为近似 tokenizer。V3 使用 Tencent 模型，无标准 tokenizer，tiktoken 作为阈值判断足够准确。
- **阈值**：当 in-context messages 的 token 数超过 **model context window 的 75%** 时触发摘要。
  - V3 当前主要模型 context window：minimax-m2.7 / deepseek-v3.2 / kimi-k2.6 等均为 128k 或更高，可统一按 **96k tokens** 作为摘要触发阈值（留 25% 余量给 response）。
  - 或更保守：固定阈值 **8000 tokens**（当前 POC 阶段对话不太可能超过此值，但随着 step 上限提升会逐渐承压）。
- **摘要范围**：超出最近 `max_context_messages`（默认 32 条，即 `max_steps * 2`）的旧消息。
- **摘要生成**：调用 LLM（复用 `TokenHubClient`）生成 1-2 句话摘要，prompt 类似：
  > "Summarize the following conversation into 1-2 sentences, preserving key facts about the user's product, needs, and corrections."
- **摘要插入**：参考 Letta `agent.py:1155-1169`：
  - 删除被摘要的旧消息（从 `session.messages` 中移除）。
  - 将摘要打包为一条 `role="user"` 的消息，插入到 system prompt 之后、recent history 之前。
  - 格式参考 Letta `system.py:191`："Note: prior messages (X of Y total) have been hidden... Summary: ..."
- **不保存摘要到 DB**：摘要是 in-context 的临时产物，不写入 `session.messages` 的持久化存储（即 `save_session` 时只保存原始消息，不保存摘要消息）。

### 3.4 Web lab 可调节 Step 上限

扩展 `backend/api/v3_sandbox.py` 的 runtime config 系统：

- **`V3SandboxRuntimeConfigPatch`** 新增字段：`max_steps: int | None = None`。
- **允许值范围**：4–50（与 `_TIMEOUT_ALLOWLIST` 类似，定义 `_MAX_STEPS_ALLOWLIST = [4, 8, 16, 24, 32, 50]`，或直接用 `ge=4, le=50` 的 int range）。
- **`_RUNTIME_OVERRIDE_KEYS`** 新增 `"max_steps"`。
- **`_effective_settings`** 或 `_runtime_overrides` 暴露 `max_steps`。
- **前端 `web/src/api.ts`**：同步类型定义。
- **前端 `web/src/App.tsx`**：在 Settings panel 中增加 `max_steps` 调节控件（slider 或 select）。

### 3.5 测试覆盖

新增测试用例（`backend/tests/test_v3_sandbox_runtime.py`）：

1. **`test_memory_rethink_replaces_block_value`**：验证 `memory_rethink` 完全替换 block value，且受 limit 约束。
2. **`test_memory_rethink_rejects_line_number_prefix`**：验证防御机制。
3. **`test_step_limit_respects_runtime_config`**：验证 `max_steps=8` 时，agent 在 8 轮后被掐断；`max_steps=16` 时允许到 16 轮。
4. **`test_context_compression_triggers_on_token_threshold`**：构造超长对话（>32 条消息），验证摘要被生成并插入。
5. **`test_runtime_config_max_steps_api`**：验证 PATCH `/v3/sandbox/runtime-config` 可修改 `max_steps`，且超出 4-50 范围返回 422。

### 3.6 Out of scope（**不**做）

- `memory_finish_edits` 工具。
- 精确 tokenizer（为每个模型引入专用 tokenizer）。
- 摘要保存到 archival memory 或 core memory block。
- `conversation_search` / recall memory（属 ADR-010 §6 #6）。
- 跨 session agent 一等实体（属 #5）。
- 修改 Android。
- 生产 SaaS / auth / tenant。

## 4. 决策记录

| ID | 决策 | 选定值 | 理由 |
|---|---|---|---|
| **Q1** | Task 合并 | 合并 `memory_rethink` + step 上限 + context 压缩为同一个 task | 三者强耦合：`memory_rethink` 在 4 步下无价值；context 压缩在步数提升后才承压 |
| **Q2** | Step 上限默认值 | **16** | 足够完成 append + append + replace + rethink + send_message（约 5-8 轮），比 Letta 50 保守（无 heartbeat） |
| **Q3** | Step 上限调节范围 | **4–50** | 4 是当前值，50 是 Letta 默认值；Web lab slider/select 覆盖 |
| **Q4** | Context 压缩策略 | **B（轻量摘要）** | 用户确认；主流 agent 标准做法 |
| **Q5** | 摘要触发条件 | **按 token 数**，阈值 **8000 tokens**（或 context window 75%） | 用户确认按 token 数；tiktoken 近似计数；8000 是保守 POC 阈值 |
| **Q6** | Token 计数方案 | **tiktoken (cl100k_base)** | 行业标准近似方法；虽模型不完全匹配，但阈值判断足够 |
| **Q7** | `memory_rethink` 语义 | **完整复刻 Letta**：`label` + `new_memory`，完全替换 block value | 用户确认；与 `memory_replace`（unique-or-raise）分工明确 |
| **Q8** | `memory_finish_edits` | **不引入** | V3 无"编辑会话"概念 |
| **Q9** | 摘要插入位置 | **参考 Letta**：作为 `role="user"` 消息插入 system prompt 之后 | 用户确认 |
| **Q10** | 摘要持久化 | **不持久化** | 摘要是 in-context 临时产物 |

## 5. 验证清单

### 5.1 强制必跑

```bash
# Schema / native runtime 单元测试
backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -x -q

# 全量 backend 测试
backend/.venv/bin/python -m pytest backend/tests -q

# Alembic（本 task 不改 DB schema，但需验证无 regression）
OPENCLAW_BACKEND_DATABASE_URL=sqlite:////tmp/openclaw_v3_rebaseline.db backend/.venv/bin/alembic -c alembic.ini upgrade head

# Web build
 cd web && npm run build
```

### 5.2 强制必跑（Postgres，如本地有 docker）

```bash
docker compose -f compose.postgres.yml up -d
OPENCLAW_BACKEND_DATABASE_URL=postgresql+psycopg://openclaw:openclaw_dev_password@127.0.0.1:55432/openclaw_dev backend/.venv/bin/alembic -c alembic.ini upgrade head
# 如有 schema 变更需 downgrade + re-upgrade
```

### 5.3 选做（Real TokenHub smoke）

- 配置 `backend/.env` 后跑单 turn，确认：
  - `memory_rethink` 能完整替换 block 内容
  - step 上限 16 时 agent 能在复杂 turn 内完成多步操作
  - 长对话（>32 条消息）触发摘要后 agent 仍能正确引用早期上下文

## 6. 风险与已知限制

- **tiktoken 计数是近似值**：Tencent 模型（minimax/deepseek/kimi）的 tokenizer 与 cl100k_base 不同，token 数可能偏差 ±20%。作为阈值判断足够，但不精确。
- **摘要质量依赖 LLM**：摘要可能遗漏关键细节，导致 agent"失忆"。缓解：保留最近 32 条消息不进入摘要，只摘要更旧的消息。
- **`memory_rethink` 误用风险**：模型可能用 `memory_rethink` 做小编辑（应该用 `memory_replace`）。缓解：docstring 明确区分，测试用例固化期望行为。
- **Step 上限提升增加 token 成本**：每多一轮都是一次完整 LLM API 调用。默认 16 是平衡值。
- **本 task 不改 DB schema**：摘要不持久化，token 计数是运行时计算，不新增表。

## 7. 后续建议

仅候选，**不**自动开工：

1. **ADR-010 §6 #4 archival memory**（需 `_active.md` §5 松绑 + ADR-011 圈定 schema / embedding provider）。
2. **ADR-010 §6 #5 跨 session agent 一等实体**（需 §5 松绑）。
3. **精确 tokenizer**：如实测 tiktoken 偏差过大，可引入各模型专用 tokenizer。
4. **Web e2e 回归**（`npm run test:e2e`）。

执行 agent **不得**自行从候选中开工 —— 须由用户在 `_active.md` 显式开放对应 task。

---

# 附录：Layer B 讨论记录（grill-me 2026-05-02）

> 以下记录供用户在独立会话中继续分析，**不**作为已确认的实现 spec。
> Layer B 包含：#4 Block schema 扩字段、#6 tokenizer/动态阈值、#7 递归摘要、#8 heartbeat。

---

## B.1 模型上下文窗口实测

V3 当前 allowlist（`backend/runtime/tokenhub_native_fc.py`）：

| 模型 | 实际窗口（tokens）| 来源 |
|---|---|---|
| minimax-m2.7 | ~196k–205k | [MiniMax Official](https://platform.minimax.io/docs/guides/models-intro) |
| deepseek-v4-flash | **1,000,000 (1M)** | [DeepInfra](https://deepinfra.com/blog/deepseek-v4-flash-api-launch-guide-en.html) |
| deepseek-v3.2 | 128k | [arXiv paper](https://arxiv.org/pdf/2512.02556) |
| kimi-k2.6 | 262k (256K) | [Moonshot Official](https://www.kimi.com/blog/kimi-k2-6) |
| glm-5.1 | ~200k | [Z.ai Docs](https://docs.z.ai/guides/llm/glm-5.1) |
| deepseek-v3.1-terminus | 128k | 与 v3.2 同系列 |

用户倾向：**不使用 deepseek-v3.2**（128k 窗口对分层预算太紧张）。

---

## B.2 动态阈值方案（#6，已部分实现）

**当前实现**：`backend/runtime/v3_sandbox/graph.py` 已引入 `_MODEL_CONTEXT_WINDOWS` 映射 + `_CONTEXT_COMPRESSION_THRESHOLD_RATIO = 0.50`。

**推荐公式**：
```python
threshold = min(absolute_cap, int(context_window * ratio))
```

**待定项**：
- `absolute_cap`：用户倾向 200k，但对 128k 模型（deepseek-v3.2）会超限
- `ratio`：推荐 50%（Hermes 标准），但对 1M 模型意味着 500k 阈值（已被 cap 截断）
- 是否需要按模型动态调整 ratio？

---

## B.3 Core Memory Token 预算分析（关键实测数据）

用 tiktoken (`cl100k_base`) 实测 `_build_tool_loop_messages` 的 system prompt token 占用：

| 场景 | System prompt tokens |
|---|---|
| 空 blocks（默认值） | **497** |
| 所有 block 写满中文（按当前 chars limit） | **44,192** |

**Per-block 写满中文时的 token 占用**：

| Block | chars limit | 写满中文 tokens |
|---|---|---|
| persona | 2000 (英文) | ~307 |
| human | 5000 (中文) | ~6,481 |
| product | 10000 (中文) | ~12,963 |
| sales_strategy | 5000 (中文) | ~6,481 |
| customer_intelligence | 20000 (中文) | ~17,500+ |

**结论**：当前默认值如果全部写满中文，system prompt  alone 就占 **44k+ tokens**。

**预算分配讨论（待定）**：

| 方案 | core memory | 对话上下文 | 特点 |
|---|---|---|---|
| A（紧缩） | 30k | 70k | 需大幅下调 chars limit（customer_intelligence 20k→12k 等） |
| B（对齐现状） | 45k | 55k | 容纳当前默认值写满；对话上下文稍紧 |
| C（弹性软预算，推荐） | 不设 hard cap | `min(70k, int(window*0.35))` | 运行时监控，超预算时警告 agent 自行压缩 |

用户态度：**待定**。

---

## B.4 递归摘要（#7，已部分实现）

**已确认**：
- 用户选 **B（递归摘要）**，非单次摘要
- 触发条件从"双条件（消息数>32 + token>阈值）"改为**单 token 条件**
- 摘要持久化已修（Layer A #1）：摘要作为 `V3SandboxMessage(role="user")` 追加到 `session.messages`

**待定**：
- 32 条消息窗口是否保持固定？用户说"我没选A（固定 32 条窗口），现在先待定"
- 递归摘要的具体实现方式：
  - 方案1：每次触发时，把 `older_messages` 中所有非 summary 的原始消息 + 旧 summary 一起重新摘要
  - 方案2：分层递归（Letta 风格），已有 summary 不重新送入 LLM，只摘要新超出的消息

---

## B.5 Heartbeat（#8）

**分析结论**：
- **只有 Letta 有显式 heartbeat**（`request_heartbeat` 参数）
- **主流框架均无 heartbeat**：
  - Codex / OpenAI Assistants：runtime 完全控制循环
  - Claude Code：runtime 完全控制，模型不声明循环意图
  - Hermes：无 loop 内控制，由 gateway/session 管理
  - LangGraph（V3 当前）：conditional edges 被动检测
- Letta 的 heartbeat 让模型显式声明"还要再来一步"，V3 当前靠 `send_message` 出现 + `max_steps` hard cap

**推荐**：不补 heartbeat。增加 heartbeat 会提高 prompt 复杂度和模型理解成本，而主流框架已证明 runtime 被动检测 + hard cap 足够工作。

用户态度：**未明确确认**，但 grill-me 中无反对意见。

---

## B.6 Block Schema 扩字段（#4，Layer B 先决项）

**当前 `CoreMemoryBlock` 字段**：`label/value/limit/read_only/metadata/tags/updated_at`

**Letta `BaseBlock` 缺失字段**：`description`（进 prompt 影响模型理解）、`hidden`、`template_*`

**讨论结论**：
- `description` 对 prompt 质量影响显著（Letta 用它来告诉模型"这个 block 是干什么的"）
- 用户尚未决定是否本轮补
- 如果补，是 schema 变更（`CoreMemoryBlock` 加字段），成本低但需同步测试

---

## B.7 Tokenizer 策略（#6，已确认）

**Q1 结论**（已确认）：
- 用 tiktoken (`cl100k_base`) 做**统一近似计数**
- 每个 block 的 token limit 留 **20% buffer**（实际 limit 设为预算的 80%），抵消不同模型 tokenizer 的 ±30% 偏差

**Q3 结论**（已确认）：
- **不改 schema**（保留 `limit` 为 chars）
- 只改**运行时预算监控**：`_build_tool_loop_messages` 中实时计算 system prompt token 数
- 超预算时加 warning prompt，让 agent 自行压缩

---

## B.8 待决策清单（供下一个 session）

1. **预算分配数字**：core memory 预留多少？对话上下文预留多少？是否采用弹性软预算（方案 C）？
2. **absolute_cap 值**：动态阈值中的 `min(absolute_cap, ...)`，cap 设多少？200k？
3. **是否弃用 deepseek-v3.2**：从 allowlist 中移除或标记为不支持？
4. **递归摘要实现方式**：方案1（全部重摘要）还是方案2（分层增量）？
5. **32 条消息窗口**：固定保留还是改为纯 token 驱动？
6. **Block schema 扩字段**：本轮是否补 `description`？
7. **Heartbeat**：明确确认"不补"还是保留开放？

---

# 附录 C：Layer C 决策记录与代码修正（2026-05-02）

> 本附录是对 B.8 待决策清单的逐项答复，并记录在本次 session 中发现的、需要立即修正的实现 bug。
> 修正属于"对齐原 spec / 修正实现漂移"，在原 task 授权范围内。

## C.1 设计前提（重新梳理）

V3 当前模型 allowlist 的实测 context window：

| 模型 | window | 备注 |
|---|---|---|
| minimax-m2.5 | 200k | |
| minimax-m2.7 | 200k | |
| deepseek-v4-flash | 1 000k | |
| deepseek-v3.1-terminus | 128k | 与 v3.2 同档 |
| deepseek-v3.2 | 128k | 用户倾向弃用 |
| kimi-k2.6 | 256k | |
| glm-5.1 | 200k | |

5 个 default block 的 chars limit 总和 = **42 000 chars**（persona 2k / human 5k / product 10k / sales_strategy 5k / customer_intelligence 20k），全写满中文 ≈ 50k tokens worst case，在 200k 窗口下占 25%。

**结论**：除 deepseek-v3.2 外，**没有任何模型逼近"必须按 100k 总预算切片"的场景**。Plan A/B 均属过度设计。

## C.2 B.8 决策

| # | 问题 | 决策 | 理由 |
|---|---|---|---|
| 1 | 预算分配 | **采纳改进版 Plan C（Letta 对齐的两层阈值 + per-block 限制）** | 不引入 core memory 总预算抽象。`SUMMARIZE_TRIGGER = 0.75`、`DESIRED_AFTER = 0.30`、`WARN_TO_AGENT = 0.60`（warn 层另开 task） |
| 2 | absolute_cap | **不设** | 比例缩放天然适配 1M 模型；cap 截断会浪费 1M 模型的优势 |
| 3 | deepseek-v3.2 | **本 task 不动 allowlist**；建议另开 task 移除 | 移除是 API/前端层改动，不属于 graph 层 bug-fix |
| 4 | 递归摘要实现 | **POC 阶段：迭代式全量重摘要（既非 B.4 方案 1 也非方案 2）** | B.4 方案 1 / 2 都假设 summary 持久化；C.3.3 决定不持久化后两者均失效。实际行为：每个超阈值 turn 把 older_messages 全量原文送一次 LLM，summary 临时使用、不进 session。优点：不会逐次劣化（始终从原文算）；缺点：单次输入随 turn 数线性增长，长会话会撞 LLM 单次输入上限。何时需要切换到真正递归（含旧 summary 入下一轮压缩），见 §C.6 退出条件。|
| 5 | 32 条消息窗口 | **保留固定 32**，语义改为 "minimum messages to keep verbatim"（安全垫） | 防止刚发生的纠正信号被卷入摘要 |
| 6 | block 加 `description` | **已经做了**（`schemas.py:24` + `default_core_memory_blocks` 都有 description） | 待决策项划除 |
| 7 | Heartbeat | **明确不补** | 主流框架（Codex / Claude Code / Hermes / LangGraph）都没有，V3 的 `send_message` 终止 + `max_steps` hard cap 已够用 |

## C.3 需立即修复的实现 bug（在原 task spec 内）

| # | 位置 | 现象 | 与 spec/Letta 的差距 | 修法 |
|---|---|---|---|---|
| **C.3.1** | `graph.py:34-40` `_MODEL_CONTEXT_WINDOWS` | 所有模型都标 128k，未列 `deepseek-v4-flash`、`glm-5.1` | 与 B.1 实测表完全不一致；minimax-m2.7 在 200k 实际窗口下被当作 128k → 阈值偏低近一倍 | 按 C.1 表更新映射 |
| **C.3.2** | `graph.py:41` `_CONTEXT_COMPRESSION_THRESHOLD_RATIO = 0.50` | 触发阈值 50% | task spec §3.3 / 决策表 Q5 写的是 "75%"；0.50 是 Hermes 长 code agent 设定，对销售对话过激 | 改为 `0.75` |
| **C.3.3** | `graph.py:413-421` 摘要写入 `session.messages` | 摘要被持久化为 `role="user"` 消息追加进 session | task spec §3.3 / 决策表 Q10 / handoff §1.3 都明确"不持久化"。会引发：(a) 下轮被当成普通历史拉进 recent_history；(b) 下下轮被卷入 older_messages 二次摘要导致信息劣化 | 删除 append 块；摘要仅在本次 messages 返回值中存在 |
| **C.3.4** | `graph.py:470-471` token 计数仅统计 messages | `all_text = "\n".join(... for m in session.messages[:-1])` 漏掉了 system prompt（写满时 ~44k） | 真触发阈值实际偏高近一倍 | 把 `_build_tool_loop_messages` 已构造的 system prompt 也算入 token 总数 |

## C.4 Out-of-scope（本 task 不动，需另开 task）

- 60% warn 层（在 system prompt 注入 "memory_pressure: high" 提示，让 agent 主动调用 `memory_rethink`）—— 新功能。
- 从 allowlist 移除 deepseek-v3.2 —— 涉及 API + 前端 + 文档，单独 task。
- partial-evict 模式（Letta 风格的增量驱逐）—— POC 阶段不需要。
- 真正的递归摘要（旧 summary + 新原文 → 新 summary）—— 需要先决定 summary 持久化层（参考 Letta 的 in-context vs full-message 分层），属架构变更。

## C.6 当前迭代式重摘要的退出条件

下列任一信号出现就应该重新评估 §C.4 的递归摘要 / partial-evict 选项：

1. 单 session 经常超过 100 turn 且持续在阈值之上
2. 单次 summarize 的输入逼近 LLM 单次输入上限（约 60% 模型窗口）
3. token 预算成本明显（每个超阈值 turn 多付一次大输入摘要）
4. 触发 ADR-010 §6 #5 跨 session agent 一等实体（届时 in-context vs full-message 自然分层，可顺带做持久化 summary）

## C.5 验证

C.3.1–C.3.4 修复后，重跑：

```bash
backend/.venv/bin/python -m pytest backend/tests/test_v3_sandbox_runtime.py -x -q
```

`test_context_compression_triggers_on_token_threshold` 在阈值升到 0.75 后可能需要把测试输入加大或调整断言（避免依赖原本 0.50 的低阈值）。
