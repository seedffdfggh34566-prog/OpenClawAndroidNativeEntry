# Task：Tencent TokenHub Native FC Model Probe Evidence

更新时间：2026-04-30

## 1. 任务定位

- 任务名称：Tencent TokenHub Native FC Model Probe Evidence
- 当前状态：`done`
- 优先级：P1
- 任务类型：`research docs / provider evidence`
- 是否属于 delivery package：`no`
- 文档同步级别：`Level 1 research evidence / task / handoff`

## 2. 授权来源

用户在当前线程明确要求记录本次腾讯云模型测试与分析，并说明：

- 这是当前时间点结果。
- 腾讯云配置、政策、模型可用性和价格会变化。
- 后续可能出现更优秀、更具性价比的模型。
- 如可行，记录腾讯云各模型成本。

## 3. 任务目标

将本次 Tencent TokenHub native Function Calling live probe 和模型选择分析记录为可追溯 evidence。

## 4. 范围

In scope:

- 记录 live probe 的 endpoint、时间、模型、native FC 结果和参数约束。
- 记录 OpenClaw V3 memory tool loop 的当前模型推荐。
- 记录腾讯云公开在线推理价格快照。
- 明确说明结果具有时效性。
- 明确说明本次测试没有读取或打印 `backend/.env` 内容。

Out of scope:

- 修改 `TokenHubClient`。
- 修改 `/lab Settings` allowlist。
- 新增 native FC adapter。
- 跑 Token Plan `/plan/v3` endpoint。
- 决定企业采购或长期 provider 策略。
- 声明 V3 runtime、memory implementation、MVP 或 production readiness 完成。

## 5. 产出

- `docs/product/research/tencent_tokenhub_native_fc_model_probe_2026_04_30.md`
- `docs/delivery/handoffs/handoff_2026_04_30_tencent_tokenhub_native_fc_model_probe.md`

## 6. 验证

- `git diff --check`

## 7. 实际结果说明

已完成 research evidence 文档，结论是：

- 当前 key 不需要先调整即可在 `/v1` endpoint 访问多个新模型。
- `minimax-m2.7` 是当前最适合作为第一版 native FC memory-tool-loop 默认模型的候选。
- `kimi-k2.6` 适合作为高能力 agent evaluation lane，但需要 per-model policy。
- 成本表记录为 2026-04-30 查询到的腾讯云公开在线推理价格快照，不作为长期价格承诺。
