# Handoff: V3 上下文阈值提升、Pressure Warning、Tool Loop Guard 与前端暴露

## 1. 变更内容

### 1.1 移除 deepseek-v3.1-terminus

原因：128k 窗口对分层预算（0.90 阈值 + 32 条 recent 保留 + response headroom）偏紧；Layer C 修正已建议移除。

| 文件 | 改动 |
|---|---|
| `backend/api/v3_sandbox.py` | `AllowedV3SandboxModel` 移除 `"deepseek-v3.1-terminus"` |
| `backend/runtime/v3_sandbox/graph.py` | `_MODEL_CONTEXT_WINDOWS` 移除 `"deepseek-v3.1-terminus": 128_000` |
| `backend/runtime/tokenhub_native_fc.py` | `V3_TOKENHUB_NATIVE_FC_MODEL_ALLOWLIST` 与 `V3_TOKENHUB_NATIVE_FC_MODEL_POLICIES` 移除 deepseek-v3.1-terminus 条目 |

### 1.2 统一强制压缩阈值 90%

**文件：** `backend/runtime/v3_sandbox/graph.py`

- `_CONTEXT_COMPRESSION_THRESHOLD_RATIO = 0.75` → `0.90`
- 注释更新：对齐 Letta ~0.9 实践，当前 allowlist 最低窗口为 200k，90% 仍留有 response headroom

### 1.3 Pressure Warning（75%）

**文件：** `backend/runtime/v3_sandbox/graph.py`

- 在 `_build_tool_loop_messages` 中，构建完 `system_prompt` 后计算当前 token 数
- 若 `token_count > context_window * 0.75`：在 `system_lines` 末尾追加 pressure warning
- Warning 内容：推荐 `memory_insert` / `memory_replace` / `core_memory_append`，明确不推荐 `memory_rethink`

### 1.4 Tool Loop Guard（95%）

**文件：** `backend/runtime/v3_sandbox/graph.py`

- 在 `_continue_or_return` 中增加 tiktoken 精确检查
- 若 `token_count > context_window * 0.95`：返回 `"return"`，优雅结束 tool loop
- 在 `runtime_metadata` 中记录 `"early_return_reason": "context_budget_exhausted"`
- `try/except` 保护 tiktoken 不可用的情况

### 1.5 空 final_message 兜底

**文件：** `backend/runtime/v3_sandbox/graph.py`

- 在 `_return_turn` 中，若 `final_message` 为空：
  - 设为 `"（Agent 在本轮执行了多个内部操作，但因上下文预算耗尽未发送最终回复。）"`

### 1.6 memory_rethink 引导

**文件：** `backend/runtime/v3_sandbox/graph.py`

- 在 `user_lines` 末尾补充：
  - "Use memory_rethink only for large sweeping reorganizations of a memory block; for small precise edits, prefer memory_insert or memory_replace."

### 1.7 前端暴露 early_return_reason

| 文件 | 改动 |
|---|---|
| `web/src/App.tsx` | `TraceList` 和 `TraceInspector` sidebar 中显示 `Context budget exhausted` 警告 |
| `web/src/styles.css` | 新增 `.trace-warning`（文字）和 `.trace-warning-badge`（标签）样式 |

### 1.8 单元测试

**文件：** `backend/tests/test_v3_sandbox_runtime.py`

新增 4 个测试：

| 测试 | 验证点 |
|---|---|
| `test_threshold_changed_to_ninety` | 阈值常量 == 0.90 |
| `test_ninety_five_percent_guard_returns_early` | mock tiktoken 超 95%，验证返回 `"return"` 且记录 `early_return_reason` |
| `test_pressure_warning_injected_above_threshold` | mock tiktoken 超 75%，验证 system prompt 包含 warning |
| `test_empty_final_message_fallback` | 验证空 `final_message` 被填充为中文兜底消息 |

## 2. 文件改动汇总

| 文件 | 变更 |
|---|---|
| `backend/api/v3_sandbox.py` | 移除 deepseek-v3.1-terminus |
| `backend/runtime/v3_sandbox/graph.py` | 阈值提升、pressure warning、loop guard、空 message 兜底、memory_rethink 引导 |
| `backend/runtime/tokenhub_native_fc.py` | 移除 deepseek-v3.1-terminus |
| `backend/tests/test_v3_sandbox_runtime.py` | 新增 4 个单元测试 |
| `web/src/App.tsx` | 暴露 early_return_reason 到 trace UI |
| `web/src/styles.css` | 新增 warning 样式 |
| `docs/delivery/handoffs/handoff_2026_05_03_v3_endpoint_a_lite_persistent_recursive_summary.md` | 更新 §4/§5 反映新阈值和已完成事项 |

## 3. 验证结果

- `backend/tests/test_v3_sandbox_runtime.py`：**42 passed**
- `backend/tests` 全量：**174 passed, 18 skipped**（0 regression）
- `web build`：通过
- `alembic upgrade head`：通过（无 schema 变更）

未跑：Postgres alembic（无 docker daemon）、real LLM smoke（需 `OPENCLAW_BACKEND_RUN_LIVE_LLM_SMOKE=1`）。

## 4. 已知限制

- pressure warning 和 loop guard 均依赖 tiktoken；tiktoken 不可用时静默跳过
- 前端未写自动化测试（web 目录无测试套件）
- 未验证 pressure warning 在真实 LLM 下的行为效果（需 live LLM smoke）

## 5. 推荐下一步

无需立即跟进。当前上下文管理分层（90% 压缩 + 75% warn + 95% guard + 空消息兜底）已完整。
