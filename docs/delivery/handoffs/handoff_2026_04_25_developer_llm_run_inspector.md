# Handoff：V1 Developer LLM Run Inspector

日期：2026-04-25

## 变更内容

- 新增默认关闭的开发者 LLM trace 能力。
- ProductLearning / LeadAnalysis LLM 调用现在可在本地记录 raw content、parsed draft、usage、耗时和失败原因。
- 新增 dev-only `/dev/llm-runs`、`/dev/llm-runs/{run_id}` 和 `/dev/llm-inspector`。
- 新增 runbook：`docs/how-to/debug/developer-llm-run-inspector.md`。

## 触达文件

- `backend/api/config.py`
- `backend/api/main.py`
- `backend/runtime/llm_trace.py`
- `backend/runtime/graphs/product_learning.py`
- `backend/runtime/graphs/lead_analysis.py`
- `backend/tests/test_dev_llm_inspector.py`
- `backend/tests/conftest.py`
- `docs/delivery/tasks/task_v1_developer_llm_run_inspector.md`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/README.md`
- `docs/how-to/README.md`
- `docs/how-to/debug/developer-llm-run-inspector.md`

## 验证

- `backend/.venv/bin/python -m pytest backend/tests/test_dev_llm_inspector.py`
  - 通过，5 passed。
- `backend/.venv/bin/python -m pytest backend/tests`
  - 通过，45 passed。
- backend startup smoke with dev trace enabled
  - `/health` 返回 `{"status":"ok"}`。
  - `/dev/llm-runs` 返回空列表。
  - `/dev/llm-inspector` 返回 HTTP 200。
- `git diff --check`
  - 通过。

## 边界结论

- 未改 Android。
- 未改数据库 schema。
- 未改正式 V1 public API contract。
- 未新增 AgentRun 状态。
- raw LLM content 不写入 `AgentRun.runtime_metadata`，只在显式开启 trace 时写入本地 JSON 文件。
- trace 不记录 API key、Authorization header、完整 prompt messages 或完整 request body。

## 已知限制

- inspector 是本地开发工具，没有鉴权、多用户隔离或长期存储设计。
- trace 文件可能包含用户输入复述和模型输出，不能提交到 Git。
- 当前不记录完整 prompt；若后续 prompt tuning 需要，应另加显式开关。

## 建议下一步

继续执行 `task_v1_extended_business_eval_round2.md`，开启 inspector 跑 16 个真实中文业务样例，使用 run id 和 trace 详情辅助评估 LLM 输出质量。
