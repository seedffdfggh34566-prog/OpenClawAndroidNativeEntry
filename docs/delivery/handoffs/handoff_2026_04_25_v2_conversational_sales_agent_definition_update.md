# 阶段性交接：V2 conversational sales agent definition update

更新时间：2026-04-25

## 1. 本次改了什么

- 将 V2 PRD 从“轻量线索研究工具”调整为“对话式专属销售 agent prototype”。
- 新增 V2.1 / V2.2 / V2.3 阶段划分。
- 新增 `v2-sales-agent-data-model.md`，定义 `SalesAgentSession`、`ConversationMessage`、`ProductProfileRevision`、`LeadDirectionVersion`、`AgentContextPack` 和 `sales_agent_turn`。
- 新增 ADR-006，冻结 prototype、本地后端沉淀、继续 LangGraph、会话消息首批持久化和 lead research 后置。
- 将 `v2-lead-research-data-model.md` 调整为 V2.2 lead research 子模型。
- 更新 overview、roadmap、README、runtime spec、delivery README 和 `_active.md`。

---

## 2. 为什么这么定

- 用户明确 V2 先做 prototype，而不是 MVP。
- 用户希望核心交互是对话框式获客分析，agent 能主动询问、回答并根据用户反馈实时调整获客方向。
- 如果直接先做 lead research，会过早进入搜索 provider、联系方式和来源质量风险，而没有先验证“专属销售 agent”的核心体验。

---

## 3. 本次验证了什么

1. `git diff --check`

本次为 docs-only 变更，未运行 backend / Android 测试。

---

## 4. 已知限制

- 未冻结 V2.1 API contract。
- 未冻结 `LeadDirectionVersion` 是否独立建表。
- 未实现 `sales_agent_turn_graph`。
- 未实现后端 schema / migration。
- 未实现 Android 对话 UI。
- 未进入 V2.2 搜索 provider 和联系方式实现。

---

## 5. 推荐下一步

1. 冻结 V2.1 conversational sales agent backend contract。
2. 冻结 `sales_agent_turn_graph` draft schema。
3. 创建 V2.1 backend-only prototype task。
