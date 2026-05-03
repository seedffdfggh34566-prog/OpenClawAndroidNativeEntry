# Handoff：V3 A-lite 摘要 Code Review 修复

更新时间：2026-05-03

## 1. 本次改了什么

### 1.1 `backend/api/config.py`

新增字段：

```python
llm_summary_timeout_seconds: float = 90.0
```

可通过环境变量 `OPENCLAW_BACKEND_LLM_SUMMARY_TIMEOUT_SECONDS` 覆盖。默认值 90.0 保持原行为不变，但现在用户可在 `/lab` 低 timeout 测试模式下独立配置。

### 1.2 `backend/runtime/v3_sandbox/graph.py`

**`_compose_context`**

return dict 加入 `"session": state["session"]`。原实现依赖 Python 引用语义——`_maybe_run_summarization` mutate session 后，LangGraph state 中的 session 指针仍指向同一对象，所以能生效；但一旦引入 checkpointing 或 reducer，mutation 会静默丢失。显式返回消除该脆弱性。

**`_maybe_run_summarization`**

- 返回类型从 `dict[str, Any] | None` 改为 `dict[str, Any]`，所有路径均返回含 `"action"` 键的 dict：

  | action | 含义 |
  |---|---|
  | `"created"` | 首次摘要，写入 session |
  | `"refreshed"` | 递归摘要，写入 session |
  | `"noop_insufficient_messages"` | after_cursor 消息数不足 |
  | `"noop_below_threshold"` | token 未达压缩阈值 |
  | `"noop_cursor_at_boundary"` | cursor 已在窗口边界 |
  | `"failed_tiktoken"` | tiktoken import/encoding 失败 |
  | `"failed_llm_empty_response"` | LLM 返回空内容 |
  | `"failed_llm_exception"` | LLM call raise Exception |

- `timeout_seconds` 由 `max(settings.llm_timeout_seconds, 90.0)` 改为 `settings.llm_summary_timeout_seconds`。
- 删除 return dict 中的死字段 `new_cursor_id`（无任何消费方）。
- 6 处 `return` / `return None` 全部改为返回具体 dict，消除风格混用。

**`_return_turn`**

fallback `summary_action` 由 `"noop"` 改为 `"noop_no_settings"`，区分"settings 未传入"与其他 noop 路径。

### 1.3 `backend/tests/test_v3_sandbox_runtime.py`

新增 3 个失败路径测试：

| 测试 | 验证点 |
|---|---|
| `test_summarization_llm_exception_does_not_mutate_session` | LLM raise → session 字段未被污染，action=`failed_llm_exception` |
| `test_summarization_llm_empty_response_does_not_mutate_session` | LLM 返回空串 → session 字段未被污染，action=`failed_llm_empty_response` |
| `test_summarization_tiktoken_failure_does_not_mutate_session` | tiktoken import 失败 → session 字段未被污染，action=`failed_tiktoken` |

---

## 2. 为什么这么定

**session 显式返回**：原设计靠 Python 对象引用正确工作，但这是隐性契约。`_load_state` 已经显式返回 `session`；`_compose_context` 不返回是遗漏，代价接近零的修复彻底消除风险。

**action enum 拆分**：`"noop"` 同时掩盖了"未触发"和"LLM 失败"两种完全不同的情形，在 /lab trace inspector 调试时无法区分。失败路径静默不报是可观测性缺陷，比优先级描述更接近 P1。全部路径返回 dict 也顺带消除了 return/None 混用。

**timeout 配置化**：硬编码的 `max(..., 90.0)` 强制覆盖用户设置，破坏了"配置说什么就是什么"的约定。加独立字段而非删除下限，是因为摘要 prompt 确实比普通 turn 长，90s 默认值有合理依据，但应允许覆盖。

**失败路径测试**：原测试全覆盖成功路径，失败路径没有任何保护。虽然 review 分析确认失败路径下 mutation 不会发生（try/except 在 mutation 前 return），但没有测试就没有回归保护。

**跳过的项目**：
- `TokenHubClient` 复用：需要把 `client` 加入 graph state 或改 `_build_graph` 闭包结构，改动面比当前所有修复加起来还大，留候选。
- 测试 cursor 偏移（P2 #4）：原测试注释已明确记录该偏移是已知 trade-off，不是潜伏 bug；端到端测试更有价值但不在本次范围。

---

## 3. 本次验证了什么

1. `pytest backend/tests/test_v3_sandbox_runtime.py -x -q`：**38 passed**（原 35 + 新 3）
2. `pytest backend/tests/ -q`：**170 passed, 18 skipped**，零 regression

---

## 4. 已知限制

- `_maybe_run_summarization` 每次触发仍新建 `TokenHubClient` 实例，未复用调用方的 `client`。在同一 turn 内会有两个 client 对象并存（摘要用一个，主 turn 用另一个）。功能无影响，性能影响可忽略（POC 阶段）。
- `noop_no_settings`（settings 未传入时的 fallback）仅出现在直接调用 `_build_tool_loop_messages` 且不传 settings 的测试路径，生产流程不会走到这条路。

---

## 5. 推荐下一步

候选（需用户显式授权）：

1. 补充端到端 cursor 落点测试（通过 `run_v3_sandbox_turn` 验证生产路径 cursor = `msg_7`）
2. `TokenHubClient` 复用（把 `client` 透传到 `_maybe_run_summarization`，需改图结构）
3. γ 周期性硬刷新（每 K 次递归全量重摘要）
