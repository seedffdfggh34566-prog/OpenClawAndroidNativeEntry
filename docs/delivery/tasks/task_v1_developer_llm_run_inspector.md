# Task：V1 Developer LLM Run Inspector

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V1 Developer LLM Run Inspector
- 建议路径：`docs/delivery/tasks/task_v1_developer_llm_run_inspector.md`
- 当前状态：`planned`
- 优先级：P0

本任务用于在 `task_v1_extended_business_eval_round2.md` 前补齐一个开发者用的最小 LLM 观察面板 / run inspector，让人类开发者能看清每个样例在 ProductLearning 和 LeadAnalysis 环节的 LLM 调用结果、解析状态、usage 和耗时。

当前问题：

- `/analysis-runs/{id}` 已能看到 `runtime_metadata.llm_usage`，但看不到 LLM 原始输出、解析后的 draft、解析失败原因和每个环节的耗时细节。
- round2 eval 将跑 16 个真实样例，如果没有 inspector，失败定位和质量评审会很低效。

---

## 2. 目标

实现一个最小、开发者本地使用的 inspector：

1. 能按 run id 查看 LLM 调用摘要。
2. 能看到 ProductLearning / LeadAnalysis 的 raw model content。
3. 能看到解析后的 draft JSON。
4. 能看到 usage、provider、model、prompt_version、duration、parse status。
5. 能把 round2 eval 中每个样例的 product_learning run 和 lead_analysis run 串起来查看。

---

## 3. 最小实现建议

建议采用 **dev-only trace artifact + backend local inspector endpoint**，避免污染正式业务对象和 public API contract：

- 新增 dev-only LLM trace 写入：
  - 仅当 `OPENCLAW_BACKEND_DEV_LLM_TRACE_ENABLED=true` 时启用。
  - 默认关闭。
  - 输出目录默认 `/tmp/openclaw_llm_traces`，可用 `OPENCLAW_BACKEND_DEV_LLM_TRACE_DIR` 覆盖。
  - 每次 LLM 调用写入一个 JSON 文件，文件名包含 `run_id` 和 `run_type`。
- trace 内容只用于开发者：
  - `run_id`
  - `run_type`
  - `provider`
  - `model`
  - `prompt_version`
  - `started_at`
  - `ended_at`
  - `duration_ms`
  - `raw_content`
  - `parsed_draft`
  - `usage`
  - `parse_status`
  - `error_type` / `error_message`，如有
- 新增 dev-only inspector endpoint：
  - `GET /dev/llm-runs`
  - `GET /dev/llm-runs/{run_id}`
  - 仅当 `OPENCLAW_BACKEND_DEV_LLM_TRACE_ENABLED=true` 时可用，否则返回 404。
- 可选最小 HTML 面板：
  - `GET /dev/llm-inspector`
  - 展示 run list 和单 run detail。
  - 不引入前端框架。

---

## 4. 边界

In Scope：

- ProductLearning LLM trace。
- LeadAnalysis LLM trace。
- 本地开发者只读 inspector。
- round2 eval 可引用 inspector 输出定位质量问题。

Out of Scope：

- 不改 Android。
- 不改 public V1 API contract。
- 不改 persisted schema。
- 不接 Langfuse / OTEL。
- 不做用户可见 UI。
- 不记录 API key 或 Authorization header。
- 不把 trace 文件提交到 Git。

---

## 5. 安全与合规默认

- 默认关闭，只有显式 env 打开。
- trace 可能包含用户输入和模型输出，因此只用于本地开发。
- task / handoff / eval 文档不得粘贴长 raw content；只记录摘要、run id 和问题类型。
- `.gitignore` 如有必要应覆盖本地 trace 目录或约定只写 `/tmp`。

---

## 6. 验收标准

1. 默认未开启 trace 时，现有测试与 API 行为不变。
2. 开启 trace 后，ProductLearning / LeadAnalysis 成功 run 会生成 trace。
3. 开启 trace 后，LLM 解析失败 run 也会生成包含 raw content 和 error 的 trace。
4. `/dev/llm-runs/{run_id}` 能返回对应 trace。
5. `/dev/llm-inspector` 能在浏览器中查看 run list 和 detail。
6. `backend/.venv/bin/python -m pytest backend/tests` 通过。
7. `git diff --check` 通过。

---

## 7. 后续关系

本任务完成后，再继续：

1. `task_v1_extended_business_eval_round2.md`
2. `task_v1_demo_runbook_and_evidence_pack.md`
