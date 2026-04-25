# Task：V1 Runtime Usage Metadata Follow-up

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V1 Runtime Usage Metadata Follow-up
- 建议路径：`docs/delivery/tasks/task_v1_runtime_usage_metadata_followup.md`
- 当前状态：`done`
- 优先级：P1

本任务用于补齐 product learning 真实 LLM 调用的 token usage 可观测性，让后续 eval 和商业成本判断不再只能记录 `not_exposed`。

---

## 2. 任务目标

在不改变 backend 对象生命周期、不引入外部 observability 平台、不改 Android UI 的前提下：

1. 将 TokenHub response 中的非敏感 `usage` 记录到 `AgentRun.runtime_metadata.llm_usage`。
2. 在 `AgentRunPayload` 中向后兼容暴露 `runtime_metadata`。
3. 更新 API contract、runtime observability baseline、eval 记录和 handoff。

---

## 3. 范围

本任务 In Scope：

- product_learning 成功路径的 LLM token usage 记录。
- `AgentRunPayload.runtime_metadata` 响应字段增补。
- backend tests 和最小真实 API smoke。
- task、reference、research、handoff 同步。

本任务 Out of Scope：

- 不接 Langfuse / OpenTelemetry。
- 不做成本看板。
- 不改 LLM provider / model / prompt。
- 不扩大真实业务样例库。
- 不把 usage 展示到 Android UI。

---

## 4. 验收标准

满足以下条件可认为完成：

1. product_learning run 成功后，`runtime_metadata.llm_usage.total_tokens` 可定位。
2. `/analysis-runs/{id}` 的 `agent_run.runtime_metadata` 可见。
3. lead_analysis / report_generation 不强制出现 `llm_usage`。
4. LLM 失败路径仍记录 `error_type`。
5. `backend/.venv/bin/python -m pytest backend/tests` 通过。
6. `./gradlew :app:assembleDebug` 通过。
7. 至少一次真实 TokenHub create / enrich smoke 可通过 run detail 看到 usage。

---

## 5. 实施边界

- `runtime_metadata` 是已有 JSON 字段，不需要数据库迁移。
- usage 只记录 token 统计，不记录 prompt、用户输入全文、API key 或 secret。
- API 响应增字段属于向后兼容扩展；当前 Android 手写 JSON parser 会忽略未知字段。

---

## 6. 实际产出

- 后端 product learning runtime 现在会把 TokenHub `usage` 规范化为 `AgentRun.runtime_metadata.llm_usage`。
- `llm_usage` 仅记录非敏感 token 统计：
  - `prompt_tokens`
  - `completion_tokens`
  - `total_tokens`
  - `cached_tokens`，如供应商返回
  - `reasoning_tokens`，如供应商返回
- `AgentRunPayload` 新增 `runtime_metadata` 响应字段，`GET /analysis-runs/{id}` 可直接查看 provider/model/prompt/round/usage。
- lead_analysis / report_generation 保持 heuristic metadata，不强制出现 `llm_usage`。
- 更新 API contract、runtime observability baseline、domain model baseline 和历史 eval 说明。

---

## 7. 已做验证

已完成：

1. `backend/.venv/bin/python -m pytest backend/tests/test_services.py backend/tests/test_api.py backend/tests/test_tokenhub_client.py`
   - 结果：28 passed。
2. `backend/.venv/bin/python -m pytest backend/tests`
   - 结果：35 passed。
3. `git diff --check`
   - 结果：通过，无输出。
4. `./gradlew :app:assembleDebug`
   - 结果：BUILD SUCCESSFUL。
5. 真实 TokenHub create smoke
   - DB：`/tmp/openclaw_runtime_usage_metadata_smoke.db`。
   - ProductProfile：`pp_17b4d965`。
   - create run：`run_f0b319e5`，`succeeded`。
   - `llm_model=minimax-m2.5`。
   - `llm_usage.total_tokens=1013`。
6. 真实 TokenHub enrich smoke
   - enrich run：`run_58cbef58`，`succeeded`。
   - `round_index=1`。
   - `llm_model=minimax-m2.5`。
   - `llm_usage.total_tokens=1317`。
7. 临时 backend 已停止，`127.0.0.1:8013` 已释放。

---

## 8. 实际结果说明

当前任务已完成。后续扩大真实业务样例库时，可以直接从 `/analysis-runs/{id}` 的 `agent_run.runtime_metadata.llm_usage` 记录 token 成本。
