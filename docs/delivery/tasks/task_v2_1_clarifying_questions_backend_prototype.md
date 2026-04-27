# Task: V2.1 Clarifying Questions Backend Prototype

状态：done

更新时间：2026-04-27

## Objective

实现 backend-first deterministic clarifying questions prototype，使 Product Sales Agent 在用户输入不足时返回 3 到 5 个中文关键追问。

## Scope

- 扩展现有 chat-first backend prototype。
- 当 message type 或输入内容不足以生成可靠 `ProductProfileRevision` / `LeadDirectionVersion` 时，返回 assistant `ConversationMessage(message_type = clarifying_question)`。
- 不生成 `WorkspacePatchDraft`，不创建 Draft Review，不 mutate workspace。
- 追问应基于 V2.1 acceptance examples，至少覆盖产品、目标客户、痛点、区域 / 行业、不优先客户。
- 增加 backend tests。

## Out Of Scope

- 不接真实 LLM。
- 不接正式 LangGraph。
- 不接 V2.2 search / ContactPoint / CRM。
- 不改 Android 大导航。
- 不写 migration。

## Validation

```bash
PYTHONPATH=$PWD backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py -q
git diff --check
```

## Outcome

- Insufficient `product_profile_update` / `lead_direction_update` chat input now returns an assistant `ConversationMessage(message_type = "clarifying_question")`.
- The response keeps `patch_draft = null` and `draft_review = null`; workspace state is not mutated.
- The deterministic questions cover product/service, target customers, pain points, region/industry/scale, and excluded customers/industries.

## Validation Run

```bash
PYTHONPATH=$PWD backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py -q
git diff --check
```
