# Handoff: V3 memory_rethink + Step 上限提升 + Context 压缩/摘要

## 1. 变更内容

### 1.1 `memory_rethink` 工具

- 新增 `memory_rethink` 到 `CoreMemoryToolName` 字面量 (`backend/runtime/v3_sandbox/schemas.py`)。
- 在 `_core_memory_tools()` 中注册新工具，docstring 复刻 Letta 风格，明确说明用于大范围整理/压缩/重组，不用于小编辑。
- `_execute_core_memory_tool` 中新增 `memory_rethink` 分支，调用 `_tool_memory_rethink()`。
- `_tool_memory_rethink()` 实现完整替换逻辑：
  - 替换 `core_memory_blocks[label].value`。
  - 检查替换后长度是否超过 `block.limit`。
  - 防御 line-number prefix (`\nLine \d+: `) 和 `CORE_MEMORY_LINE_NUMBER_WARNING` 混入新内容。
- `backend/api/v3_sandbox.py` 的 `memory_runtime.tools` 同步更新。

### 1.2 Step 上限可配置

- `V3SandboxGraphState` 新增 `max_steps: int` 字段。
- `run_v3_sandbox_turn` 接受 `max_steps: int = 16`，运行时钳制到 `4–50`。
- `_continue_or_return` 从硬编码 `4` 改为读取 `state["max_steps"]`：
  - `tool_events` 硬上限改为 `max_steps * 4`。
  - `call_count >= max_steps` 时抛 `v3_tool_loop_exhausted`。
- API 层：
  - `V3SandboxRuntimeConfigPatch` 新增 `max_steps: int | None`（`ge=4, le=50`）。
  - `_RUNTIME_OVERRIDE_KEYS` 新增 `"max_steps"`。
  - `_runtime_config_response` 返回 `max_steps` 配置和 allowlist。
  - turn / replay 端点把 `max_steps` 传给 `run_v3_sandbox_turn`。
- Web 层：
  - `api.ts` 同步 `runtime_config` 和 `allowlists` 类型。
  - `App.tsx` Settings panel 增加 `max_steps` 数字输入框（带 min/max 校验）。

### 1.3 Context 压缩/摘要

- `_build_tool_loop_messages` 在构建消息列表时，若会话消息数超过 32 条，调用 `_maybe_summarize_older_messages`。
- `_maybe_summarize_older_messages`：
  - 使用 `tiktoken` (`cl100k_base`) 近似计数。
  - 阈值：8000 tokens。
  - 仅对超出最近 32 条窗口的旧消息生成摘要。
  - 调用 LLM 生成 1-2 句话摘要。
  - 将摘要打包为 `role="user"` 消息，插入 system prompt 之后、recent history 之前。
  - 摘要不持久化到 `session.messages`。

### 1.4 Schema 加固

- `V3SandboxModel` 基础 `model_config` 从 `extra="ignore"` 收紧为 `extra="forbid"`。
- `V3SandboxSession` 单独覆盖 `extra="ignore"` 以兼容持久化层可能存在的遗留字段。
- `CoreMemoryBlock._value_fits_limit` 从 `field_validator` 改为 `model_validator(mode="after")` 以支持跨字段校验。

## 2. 文件改动

| 文件 | 变更类型 |
|---|---|
| `backend/runtime/v3_sandbox/schemas.py` | 修改 |
| `backend/runtime/v3_sandbox/graph.py` | 修改 |
| `backend/api/v3_sandbox.py` | 修改 |
| `web/src/api.ts` | 修改 |
| `web/src/App.tsx` | 修改 |
| `backend/tests/test_v3_sandbox_runtime.py` | 修改 |

## 3. 验证结果

- `backend/tests/test_v3_sandbox_runtime.py`：29 项全部通过。
- 全量 backend tests：`161 passed, 18 skipped`（18 项为 Postgres/live LLM，需环境变量）。
- Web build：`npm run build` 通过，无 TypeScript 错误。
- Alembic：本 task 不改 DB schema，无需 migration。

## 4. 已知限制

- tiktoken 计数是近似值，与 Tencent 模型实际 tokenizer 可能有 ±20% 偏差，作为阈值判断足够。
- 摘要质量依赖 LLM，可能遗漏早期细节；缓解：保留最近 32 条消息不进入摘要。
- `memory_rethink` 仍有被模型误用于小编辑的风险，需通过 docstring 和运行时 trace 引导。

## 5. 推荐下一步

候选（需用户显式授权）：
1. ADR-010 §6 #4 archival memory 设计。
2. ADR-010 §6 #5 跨 session agent 一等实体。
3. Web e2e 回归测试。
4. 60% warn 层（在 system prompt 注入 "memory_pressure: high" 提示，让 agent 主动 `memory_rethink`）。
5. 从 allowlist 移除 deepseek-v3.2（涉及 API + 前端 + 文档）。

## 6. Layer C 修正（2026-05-02 追加）

> 见任务文档附录 C。原 task 完成后发现 4 处实现漂移，本次回到 spec：

| # | 文件 | 修正 |
|---|---|---|
| C.3.1 | `backend/runtime/v3_sandbox/graph.py:34-46` | `_MODEL_CONTEXT_WINDOWS` 按 B.1 实测表更新（minimax-m2.5/m2.7=200k、deepseek-v4-flash=1M、kimi-k2.6=256k、glm-5.1=200k、deepseek-v3.x=128k）；新增 `_DEFAULT_CONTEXT_WINDOW = 128_000` 常量供未知模型 fallback |
| C.3.2 | `backend/runtime/v3_sandbox/graph.py:46` | `_CONTEXT_COMPRESSION_THRESHOLD_RATIO`：`0.50` → `0.75`，对齐 task spec §3.3 / Q5（Hermes 0.50 偏激进，0.75 留 25% 余量给响应） |
| C.3.3 | `backend/runtime/v3_sandbox/graph.py:412-419` | 删除把 summary 作为 `V3SandboxMessage(role="user")` 追加到 `session.messages` 的代码。摘要仅在本次返回的 LLM messages 中存在，不进 session 持久层。对齐 spec Q10、消除"下一轮被当成普通历史 / 下下轮被卷入二次摘要"两个隐患 |
| C.3.4 | `backend/runtime/v3_sandbox/graph.py:451-485` | `_maybe_summarize_older_messages` 新增 `system_prompt`、`current_user_content` 关键字参数；token 计数现在包含 system prompt（含全部 core memory blocks，worst case ~44k）+ 完整 history + 当前用户 turn，反映模型真实可见量 |

### 测试调整

- `test_context_compression_triggers_on_token_threshold`：把每条消息的 long_text 从 `* 300` 提到 `* 2000`，确保跨过 200k 窗口下的 150k 阈值；新增 `assert len(session.messages) == messages_before` 验证摘要不持久化。

### 验证

- `backend/tests/test_v3_sandbox_runtime.py`：29 passed
- `backend/tests`（全量）：161 passed, 18 skipped（与修正前一致）

### Out-of-scope（需另开 task）

- 60% warn 层注入。
- partial-evict 模式（Letta 增量驱逐风格）。
- 移除 deepseek-v3.2。
