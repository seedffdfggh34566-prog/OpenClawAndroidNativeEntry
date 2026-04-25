# Developer LLM Run Inspector

更新时间：2026-04-25

## 1. 用途

本 runbook 用于在本地开发时查看 ProductLearning / LeadAnalysis 的 LLM 调用 trace。

它是开发者工具，不是 V1 用户功能。默认关闭，不影响正式 API 行为。

## 2. 启动方式

使用独立 DB 和独立 trace 目录启动 backend：

```bash
OPENCLAW_BACKEND_DATABASE_PATH=/tmp/openclaw_llm_inspector.db \
OPENCLAW_BACKEND_DEV_LLM_TRACE_ENABLED=true \
OPENCLAW_BACKEND_DEV_LLM_TRACE_DIR=/tmp/openclaw_llm_traces \
backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013
```

真实 TokenHub 配置继续从 `backend/.env` 或环境变量读取。不要在命令、日志或文档中打印 API key。

## 3. 查看入口

- HTML 面板：`http://127.0.0.1:8013/dev/llm-inspector`
- run 列表：`http://127.0.0.1:8013/dev/llm-runs`
- 单 run trace：`http://127.0.0.1:8013/dev/llm-runs/{run_id}`

未设置 `OPENCLAW_BACKEND_DEV_LLM_TRACE_ENABLED=true` 时，这些入口返回 404。

## 4. Trace 内容

每次 ProductLearning / LeadAnalysis LLM 调用会写入一个本地 JSON 文件，字段包括：

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
- `error_type`
- `error_message`

trace 不记录 API key、Authorization header、完整 prompt messages 或完整 request body。

## 5. 清理

trace 默认写入 `/tmp/openclaw_llm_traces`，可直接清理：

```bash
rm -rf /tmp/openclaw_llm_traces
```

如果把 `OPENCLAW_BACKEND_DEV_LLM_TRACE_DIR` 指到仓库内，提交前必须确认 trace JSON 不进入 Git。

## 6. Round 2 Eval 建议

执行 `task_v1_extended_business_eval_round2.md` 时建议开启 inspector，并在 eval 记录中只引用 run id、usage 和问题摘要，不粘贴长 raw content。
