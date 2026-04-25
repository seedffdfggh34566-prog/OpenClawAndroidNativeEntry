# V1 LLM Provider / Model Selection

更新时间：2026-04-25

## 1. 文档定位

本文记录 V1 product learning LLM Phase 1 的供应商、模型、计费形态与 API Key 获取决策。

它服务于：

- `task_v1_product_learning_llm_phase1.md` 的实现前置对齐
- 后续 heuristic vs LLM 样例对比
- 避免在代码实现时临时决定 provider、model、key 形态

本文不是：

- 长期多模型路由方案
- 成本核算系统设计
- 企业采购最终合同评审
- 通用大模型排行榜

---

## 2. 当前决策

当前 V1 product learning LLM Phase 1 采用：

- 供应商：腾讯云大模型服务平台 TokenHub
- 计费形态：普通 TokenHub 按量计费 API
- API Key 形态：TokenHub 控制台创建的普通 API Key
- OpenAI-compatible Base URL：`https://tokenhub.tencentmaas.com/v1`
- Chat Completions URL：`https://tokenhub.tencentmaas.com/v1/chat/completions`
- 第一轮默认模型：`minimax-m2.5`
- Prompt version：`product_learning_llm_v1`

推荐默认环境变量：

```bash
OPENCLAW_BACKEND_LLM_PROVIDER=tencent_tokenhub
OPENCLAW_BACKEND_LLM_BASE_URL=https://tokenhub.tencentmaas.com/v1
OPENCLAW_BACKEND_LLM_MODEL=minimax-m2.5
OPENCLAW_BACKEND_LLM_API_KEY=<provided-by-human>
OPENCLAW_BACKEND_LLM_PROMPT_VERSION=product_learning_llm_v1
```

API Key 必须只存在于服务端运行环境，不进入 Android 客户端，不提交到 Git。

Token Plan 企业版当前不作为本阶段默认方案。它只作为后续真实用量稳定后，用于降低单位成本和做企业团队配额管理的候选方案。

---

## 3. 为什么先用 `minimax-m2.5`

当前 product learning 的任务重点是中文产品信息抽取、字段补全和稳定结构化 draft 输出。

本轮优先级排序：

1. 低成本验证真实 LLM 是否能替代 heuristic
2. 输出能被 typed schema / Pydantic 校验
3. 质量能被 3 个固定样例集人工对比
4. 供应商和模型选择可复现

当前先用普通 TokenHub 按量 API，是为了避免在模型质量未验证前购买月度套餐。`minimax-m2.5` 继续作为第一轮 baseline，因为它能覆盖本轮文本生成 / 结构化补全需求，且可在同一 TokenHub API 下与 `kimi-k2.5`、`glm-5` 做同 prompt 对照。

| 模型 | 本轮定位 | 是否作为默认 |
|---|---|---|
| `minimax-m2.5` | 低成本 product learning baseline | yes |
| `kimi-k2.5` | 长上下文 / 更强能力对照模型 | no, second-pass comparison |
| `glm-5` | 结构化稳定性兜底对照 | no, fallback |
| `auto` | 临时办公或工具体验 | no, not reproducible baseline |

不先用 `kimi-k2.5` 作为默认的原因：

- Kimi-K2.5 的优势更偏长上下文、多模态、agent / coding 与复杂工具调用。
- 当前样例输入较短，产品学习重点是结构化抽取和补全，先用低成本模型更适合验证商业可行性。
- `kimi-k2.5` 应保留为对照模型：如果 `minimax-m2.5` 在字段质量、幻觉控制或 JSON 稳定性上不达标，再切换对比。

---

## 4. Human API Key 获取方案

由 human 在腾讯云控制台完成以下动作：

1. 开通或确认 TokenHub 普通 API 服务。
   - 控制台入口：`https://console.cloud.tencent.com/tokenhub/`
   - 模型广场入口：`https://console.cloud.tencent.com/tokenhub/models`
   - 当前阶段不要进入 Token Plan 企业版购买页。

2. 可先领取新用户免费体验额度。
   - 腾讯云 TokenHub 文档说明新用户可在模型广场领取免费体验额度，具体额度和有效期以控制台显示为准。
   - 免费额度不足或过期后，普通语言模型按后付费 tokens 计量。

3. 创建普通 TokenHub API Key。
   - API Key 管理入口：`https://console.cloud.tencent.com/tokenhub/apikey`
   - Key 名称建议：`openclaw-v1-product-learning-dev`
   - 可访问范围建议先限定到本轮需要的模型，至少包含 `MiniMax-M2.5`。
   - 建议同时允许 `Kimi-K2.5`、`GLM-5`，便于后续同 prompt 对照。

4. 成本控制。
   - 当前不是预付费 Token Plan，因此主要通过腾讯云账户预算、告警、用量查询和 dev key 访问范围控制成本。
   - 实现侧应限制样例运行规模，记录 `usage`，不要在未确认前做批量调用。

5. 交付 API Key。
   - 不要把 API Key 发送到 Git、文档、聊天记录或 Android 端代码。
   - 推荐通过服务器环境变量、部署平台 secret、或仅 human 可控的本地 `.env` 注入。
   - 交付给执行 agent 时，只说明 key 已放入哪台服务器的哪个运行环境，不需要把明文 key 写进仓库。

6. 最小连通性验证。
   - 使用 `model=minimax-m2.5`
   - 使用非流式 `chat/completions`
   - 验证返回中包含 `choices` 与 `usage`
   - 记录实际模型、输入 token、输出 token、错误码或限流情况

---

## 5. 实现约束

LLM Phase 1 实现时必须保持：

- Android / Web client 只调用本项目 backend，不直接持有腾讯云 API Key。
- Backend 调用 TokenHub，并把 provider/model/prompt_version 记录到 runtime metadata。
- Runtime 只返回 typed draft，正式对象写回仍由 `backend/api/services.py` 负责。
- Backend 继续拥有 canonical `missing_fields` 和 `learning_stage` 判定权。
- 若 LLM 返回非 JSON 或 schema 校验失败，应失败可定位，不能静默写入坏数据。

推荐 metadata 增补字段：

- `llm_provider`: `tencent_tokenhub`
- `llm_model`: `minimax-m2.5`
- `llm_base_url`: 不记录完整 secret，只记录 provider URL 或 provider name
- `prompt_version`: `product_learning_llm_v1`

---

## 6. 最小评估路径

第一轮实现后至少运行：

1. `runtime-v1-observability-eval-baseline.md` 中的 3 个 product learning 样例。
2. 记录 heuristic vs `minimax-m2.5` 的表格对比。
3. 如果 `minimax-m2.5` 明显不达标，再用同一 prompt 跑 `kimi-k2.5`。
4. 如果 JSON / schema 稳定性仍不达标，再用同一 prompt 跑 `glm-5`。

切换默认模型的触发条件：

- `minimax-m2.5` 的 hallucination count 明显高于 heuristic 或人工不可接受。
- `minimax-m2.5` 不能稳定输出可解析 JSON。
- `kimi-k2.5` 或 `glm-5` 在同样样例中显著提升字段质量，且成本可接受。

---

## 7. 参考来源

- 腾讯云 TokenHub 产品页：`https://cloud.tencent.com/product/tokenhub`
- 腾讯云 TokenHub 快速入门：`https://cloud.tencent.com/document/product/1823/130058`
- 腾讯云 TokenHub 计费方式：`https://cloud.tencent.com/document/product/1823/130054`
- 腾讯云 TokenHub API 使用说明：`https://cloud.tencent.com/document/product/1823/130078`
- 腾讯云 TokenHub 文本生成 / OpenAI-compatible Chat Completions：`https://cloud.tencent.com/document/product/1823/130079`
- Kimi-K2.5 官方模型说明：`https://www.kimi.com/ai-models/kimi-k2-5`
