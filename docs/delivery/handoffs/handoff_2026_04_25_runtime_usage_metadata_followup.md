# 阶段性交接：Runtime Usage Metadata Follow-up

更新时间：2026-04-25

## 1. 本次完成了什么

- product learning LLM 成功路径会把 TokenHub `usage` 写入 `AgentRun.runtime_metadata.llm_usage`。
- `AgentRunPayload` 新增向后兼容字段 `runtime_metadata`，run detail 可直接看到 provider、model、prompt version、round index 和 token usage。
- usage 只记录非敏感 token 统计，不记录 prompt、用户输入全文、API key 或 secret。
- lead_analysis / report_generation 保持 heuristic metadata，不强制出现 `llm_usage`。

## 2. 涉及文件

- `backend/runtime/graphs/product_learning.py`
- `backend/runtime/types.py`
- `backend/runtime/adapter.py`
- `backend/api/services.py`
- `backend/api/schemas.py`
- `backend/api/serializers.py`
- `backend/tests/test_services.py`
- `backend/tests/test_api.py`
- `backend/tests/conftest.py`
- `docs/reference/api/backend-v1-minimum-contract.md`
- `docs/reference/runtime-v1-observability-eval-baseline.md`
- `docs/reference/schemas/v1-domain-model-baseline.md`
- `docs/product/research/product_learning_llm_eval_2026_04_25.md`
- `docs/delivery/tasks/task_v1_runtime_usage_metadata_followup.md`

## 3. 验证记录

- `backend/.venv/bin/python -m pytest backend/tests/test_services.py backend/tests/test_api.py backend/tests/test_tokenhub_client.py`：28 passed。
- `backend/.venv/bin/python -m pytest backend/tests`：35 passed。
- `git diff --check`：通过。
- `./gradlew :app:assembleDebug`：BUILD SUCCESSFUL。
- 真实 TokenHub create smoke：
  - ProductProfile：`pp_17b4d965`
  - run：`run_f0b319e5`
  - status：`succeeded`
  - `llm_model=minimax-m2.5`
  - `llm_usage.total_tokens=1013`
- 真实 TokenHub enrich smoke：
  - run：`run_58cbef58`
  - status：`succeeded`
  - `round_index=1`
  - `llm_model=minimax-m2.5`
  - `llm_usage.total_tokens=1317`
- 临时 backend 已停止，`127.0.0.1:8013` 已释放。

## 4. 已知限制

- 本次不做成本看板，不把 usage 展示到 Android UI。
- 历史 eval 文档中的 `token_usage=not_exposed` 保持为当时记录，不回填。
- 当前只对 product_learning LLM 成功路径记录 `llm_usage`；heuristic runtime 不生成该字段。

## 5. 推荐下一步

当前没有已排定的下一项 implementation task。建议下一步由规划层决定是否进入扩大真实业务样例库，并在新样例 eval 中记录 `llm_usage.total_tokens`。
