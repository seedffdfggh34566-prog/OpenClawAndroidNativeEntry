# Handoff：Tencent TokenHub Native FC Model Probe Evidence

日期：2026-04-30

## 1. 变更摘要

记录本次 Tencent TokenHub native Function Calling 模型测试与模型选择分析。

重点记录：

- `/v1` endpoint 下各模型 live probe 结果。
- Kimi K2.6 / K2.5、MiniMax M2.7、DeepSeek V4 Flash、DeepSeek V3.2、GLM-5.1、Hy3 preview 等模型的 FC 行为差异。
- Kimi K2.6 和 DeepSeek V4 Flash 的 per-model 参数约束。
- 2026-04-30 查询到的腾讯云公开在线推理价格快照。
- 本结论只代表当前时间点，不代表腾讯云后续模型、政策、价格或 Token Plan 覆盖范围。

## 2. 文件或区域

- `docs/product/research/tencent_tokenhub_native_fc_model_probe_2026_04_30.md`
- `docs/delivery/tasks/task_2026_04_30_tencent_tokenhub_native_fc_model_probe.md`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/README.md`

## 3. 验证

- `git diff --check`

## 4. 已知边界

- 本次没有修改 backend runtime、`TokenHubClient`、`/lab Settings` 或 model allowlist。
- 本次没有测试 Token Plan `/plan/v3` endpoint。
- 本次没有读取或打印 `backend/.env` 内容，也没有记录任何 API key。
- 成本记录来自腾讯云公开在线推理价格页，不等同于企业 Token Plan 的实际可用模型或抵扣规则。
- 结论不声明 V3 native FC adapter、memory tool loop、MVP 或 production-ready 完成。

## 5. 推荐下一步

建议单独开放小任务：

- `V3 TokenHub Native Tool Calling Adapter POC`

建议范围：

- `TokenHubClient.complete_with_tools(...)`
- 解析 `message.tool_calls`
- 支持 model policy：`temperature`、`thinking`、`reasoning_effort`、forced/named tool-choice fallback
- 更新 `/lab Settings` allowlist：
  - `minimax-m2.7`
  - `deepseek-v4-flash`
  - `deepseek-v3.2`
  - `kimi-k2.6`
  - `glm-5.1`
- 保留 JSON-simulated tool calls 作为 fallback。
