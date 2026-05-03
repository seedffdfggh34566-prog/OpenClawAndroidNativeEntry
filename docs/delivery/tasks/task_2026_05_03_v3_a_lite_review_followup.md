# Task：V3 A-lite 摘要 Code Review 修复

更新时间：2026-05-03

## 1. 任务定位

- 任务名称：V3 A-lite 摘要 Code Review 修复
- 当前状态：`completed`
- 优先级：P2
- 任务类型：`backend runtime / observability / testing / config`
- 是否属于 delivery package：`no`
- 上游：`docs/delivery/tasks/task_2026_05_03_v3_endpoint_a_lite_persistent_recursive_summary.md`（已 completed）

## 2. 授权来源

用户在当前线程（2026-05-03）对 A-lite 实现进行 code review，并明确要求按照 review 发现进行修复。

## 3. 范围

### 修复项一览

| 优先级 | 问题 | 修法 |
|---|---|---|
| P2 | `_compose_context` 不返回 `session`，依赖 Python 引用语义传递 mutation | `_compose_context` return dict 加 `"session": state["session"]` |
| P2 | `_maybe_run_summarization` timeout 硬编码 `max(..., 90.0)`，用户无法覆盖 | `Settings` 加 `llm_summary_timeout_seconds: float = 90.0`；函数改用该字段 |
| P2↑ | `summary_action="noop"` 同时代表"未触发"和"LLM 失败"，trace 无法区分 | 所有 return 路径改为具体 action 字符串，失败路径单独命名 |
| P2 | LLM 失败、空响应、tiktoken 失败三条路径无测试覆盖 | 新增 3 个失败路径测试 |
| P3 | return dict 含死字段 `new_cursor_id`（无任何消费方） | 删除 |
| P3 | `return` / `return None` 混用 | 全部路径改为返回具体 dict，消除混用 |

不在本 task 范围：
- `_maybe_run_summarization` 复用调用方 `TokenHubClient`（需改图结构，留候选）
- P2 #4 测试 cursor 偏移已有文档记录，无需改动

## 4. 验证

- `pytest backend/tests/test_v3_sandbox_runtime.py`：**38 passed**（+3 新测试）
- `pytest backend/tests/`：**170 passed, 18 skipped**，零 regression
