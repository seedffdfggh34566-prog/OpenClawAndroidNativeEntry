# 阶段性交接：Product Learning LLM Provider Selection

更新时间：2026-04-25

## 1. 本次改了什么

- 新增 `docs/reference/runtime-v1-llm-provider-selection.md`，记录 V1 product learning LLM Phase 1 的 provider / model / API Key 决策。
- 更新 `docs/delivery/tasks/task_v1_product_learning_llm_phase1.md`，补充腾讯云 TokenHub 普通按量 API、`minimax-m2.5` 默认模型、human API Key 前置动作与模型对照策略。
- 更新 `docs/reference/README.md` 与 `docs/README.md`，把 LLM provider selection 文档加入推荐阅读入口。
- 更正早先把当前阶段写成 Token Plan 企业版的表述：当前阶段先使用普通 TokenHub 按量计费 API，Token Plan 只作为后续规模化成本优化选项。

---

## 2. 为什么这么定

- 当前 V1 product learning 的第一阶段重点是低成本验证真实 LLM 能否替代 heuristic，而不是追求最强长上下文或 agent 能力。
- 当前阶段尚未验证模型质量和真实调用量，不应先购买月度 Token Plan。
- 普通 TokenHub 按量 API 更适合 first-pass 技术试验，可先用小规模样例和免费额度 / 后付费用量确认质量。
- `kimi-k2.5` 保留为第二轮质量对照模型，适合在 `minimax-m2.5` 输出质量或稳定性不足时比较。
- `glm-5` 保留为结构化稳定性兜底对照模型。
- `auto` 不作为 baseline，因为自动路由不利于样例复现和质量归因。

---

## 3. 本次验证了什么

1. 查阅并引用腾讯云 TokenHub 快速入门、计费方式、API 使用说明和文本生成文档。
2. 确认普通 TokenHub OpenAI-compatible Base URL 为 `https://tokenhub.tencentmaas.com/v1`。
3. 确认可用模型 ID 包含 `kimi-k2.5`、`minimax-m2.5`、`glm-5` 等。
4. 本次为 docs-only 变更，后续仍需运行 `git diff --check`。

---

## 4. 已知限制

- 尚未接入真实 LLM，`task_v1_product_learning_llm_phase1.md` 状态仍为 `planned`。
- 尚未获得或验证腾讯云 API Key。
- 尚未完成 `minimax-m2.5`、`kimi-k2.5`、`glm-5` 的样例质量对比。
- 成本估算来自腾讯云公开文档，实际消耗仍应以后续 `usage` 和控制台账单为准。

---

## 5. 推荐下一步

1. Human 在腾讯云 TokenHub 创建普通按量 API dev key，并授权 `MiniMax-M2.5`，建议同时授权 `Kimi-K2.5` 与 `GLM-5`。
2. 将 API Key 注入 backend/server 环境变量，不写入 Git、文档或 Android 客户端。
3. 进入 `docs/delivery/tasks/task_v1_product_learning_llm_phase1.md`，实现 `minimax-m2.5` 的真实 LLM draft 生成。
4. 使用 `docs/reference/runtime-v1-observability-eval-baseline.md` 的 3 个样例记录 heuristic vs `minimax-m2.5` 对比。
