# V1 LLM Provider / Model Selection

更新时间：2026-04-25

## 1. 文档定位

本文记录 V1 product learning LLM Phase 1 的供应商、模型与 API Key 获取决策。

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
- 计费形态：Token Plan 企业版 API Key
- OpenAI-compatible Base URL：`https://tokenhub.tencentmaas.com/plan/v3`
- Chat Completions URL：`https://tokenhub.tencentmaas.com/plan/v3/chat/completions`
- 第一轮默认模型：`minimax-m2.5`
- Prompt version：`product_learning_llm_v1`

推荐默认环境变量：

```bash
OPENCLAW_BACKEND_LLM_PROVIDER=tencent_tokenhub_plan
OPENCLAW_BACKEND_LLM_BASE_URL=https://tokenhub.tencentmaas.com/plan/v3
OPENCLAW_BACKEND_LLM_MODEL=minimax-m2.5
OPENCLAW_BACKEND_LLM_API_KEY=<provided-by-human>
OPENCLAW_BACKEND_LLM_PROMPT_VERSION=product_learning_llm_v1
```

API Key 必须只存在于服务端运行环境，不进入 Android 客户端，不提交到 Git。

---

## 3. 为什么先用 `minimax-m2.5`

当前 product learning 的任务重点是中文产品信息抽取、字段补全和稳定结构化 draft 输出。

本轮优先级排序：

1. 低成本验证真实 LLM 是否能替代 heuristic
2. 输出能被 typed schema / Pydantic 校验
3. 质量能被 3 个固定样例集人工对比
4. 供应商和模型选择可复现

在腾讯云 Token Plan 企业版当前模型中，`minimax-m2.5` 的综合单价预估最低，适合做第一轮 baseline。

| 模型 | 本轮定位 | 是否作为默认 |
|---|---|---|
| `minimax-m2.5` | 低成本 product learning baseline | yes |
| `kimi-k2.5` | 长上下文 / 更强能力对照模型 | no, second-pass comparison |
| `glm-5` | 结构化稳定性兜底对照 | no, fallback |
| `auto` | 临时办公或工具体验 | no, not reproducible baseline |

不先用 `kimi-k2.5` 的原因：

- Kimi-K2.5 的优势更偏长上下文、多模态、agent / coding 与复杂工具调用。
- 腾讯云企业版 Token Plan 当前说明该套餐模型暂不支持图片、视频等多模态能力，本项目本轮也不需要视觉输入。
- 当前样例输入较短，产品学习重点是结构化抽取和补全，先用低成本模型更适合验证商业可行性。
- `kimi-k2.5` 应保留为对照模型：如果 `minimax-m2.5` 在字段质量、幻觉控制或 JSON 稳定性上不达标，再切换对比。

---

## 4. Human API Key 获取方案

由 human 在腾讯云控制台完成以下动作：

1. 购买或确认 Token Plan 企业版套餐。
   - 当前公开文档显示月预算范围为 5,000 元/月到 20,000 元/月，步长 5,000 元。
   - 如果只是技术试验，应优先只买最小可用周期和最小预算，避免在模型质量未验证前锁定更大成本。

2. 创建 API Key。
   - Key 名称建议：`openclaw-v1-product-learning-dev`
   - 模型选择至少勾选：`MiniMax-M2.5`
   - 建议同时勾选：`Kimi-K2.5`、`GLM-5`
   - 不建议依赖：`Auto`，除非只是人工临时测试。

3. 设置 Key 配额。
   - 独占积分：可先设为 `0`，使用共享池。
   - 总积分上限：为 dev key 设置较小上限，建议先用控制台允许的较小值，例如 `10000` 到 `50000` 积分；若控制台有更小最小值，以控制台为准。
   - TPM 限制：为 dev key 设置自定义较低值即可，满足单人开发和样例验证，不需要一开始放开套餐上限。

4. 交付 API Key。
   - 不要把 API Key 发送到 Git、文档、聊天记录或 Android 端代码。
   - 推荐通过服务器环境变量、部署平台 secret、或仅 human 可控的本地 `.env` 注入。
   - 交付给执行 agent 时，只说明 key 已放入哪台服务器的哪个运行环境，不需要把明文 key 写进仓库。

5. 最小连通性验证。
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

- `llm_provider`: `tencent_tokenhub_plan`
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

- 腾讯云 Token Plan 企业版套餐概览：`https://cloud.tencent.com/document/product/1823/130659`
- 腾讯云 Token Plan 企业版快速入门：`https://cloud.tencent.com/document/product/1823/130660`
- 腾讯云 TokenHub 文本生成 / OpenAI-compatible Chat Completions：`https://cloud.tencent.com/document/product/1823/130079`
- Kimi-K2.5 官方模型说明：`https://www.kimi.com/ai-models/kimi-k2-5`
