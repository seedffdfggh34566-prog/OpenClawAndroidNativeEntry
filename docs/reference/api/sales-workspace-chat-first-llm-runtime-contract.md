# Sales Workspace Chat-first LLM Runtime Contract

更新时间：2026-04-28

## 1. Purpose

本文档定义 V2.1 chat-first Product Sales Agent 使用 Tencent TokenHub LLM 时的 structured output contract。

LLM 不直接写 workspace。LLM 只返回结构化 runtime output；backend 负责校验、materialize `WorkspacePatchDraft`、创建 Draft Review，并由 Sales Workspace Kernel 负责正式写回。

## 2. Runtime Mode

LLM runtime 仅在显式配置下启用：

```text
OPENCLAW_BACKEND_SALES_AGENT_RUNTIME_MODE=llm
```

默认 `deterministic` runtime 行为保持不变。

## 3. `SalesAgentTurnLlmOutput`

LLM 必须只输出单个 JSON object。

```json
{
  "message_type": "draft_summary",
  "assistant_message": "我已整理出一版产品理解草稿，请审阅后应用。",
  "clarifying_questions": [],
  "patch_operations": [
    {
      "type": "upsert_product_profile_revision",
      "payload": {
        "product_name": "工业设备维保软件",
        "one_liner": "帮助工厂降低停机时间的设备维保软件。",
        "target_customers": ["制造业工厂设备部"],
        "target_industries": ["制造业"],
        "pain_points": ["停机损失"],
        "value_props": ["降低停机时间"],
        "constraints": ["需要确认设备类型和地区"]
      }
    }
  ],
  "confidence": 0.78,
  "missing_fields": [],
  "reasoning_summary": "用户提供了产品、目标客户和核心痛点，足以生成可审阅草稿。"
}
```

Allowed `message_type`:

- `clarifying_question`
- `workspace_question`
- `draft_summary`
- `out_of_scope_v2_2`

`reasoning_summary` 必须是面向用户和审计的短摘要，不记录 chain-of-thought。

## 4. Clarifying Questions

当输入不足时：

- `message_type = "clarifying_question"`。
- `clarifying_questions` 必须有 3 到 5 条中文问题。
- `patch_operations` 必须为空。
- backend 不创建 Draft Review。
- workspace 不得 mutate。

## 5. Workspace Explanation

当用户问当前 workspace 状态或推荐原因时：

- `message_type = "workspace_question"`。
- `assistant_message` 必须基于 ContextPack 中的 current product / direction / source versions。
- `patch_operations` 必须为空。
- backend 不创建 Draft Review。
- workspace 不得 mutate。

## 6. Draft Summary

当用户输入足以更新产品理解或获客方向时：

- `message_type = "draft_summary"`。
- `patch_operations` 可包含现有 Sales Workspace Kernel 支持的 operation。
- backend 为 operation 补齐 workspace-local IDs、workspace_id、version 和 trace refs。
- backend materialize 为 `WorkspacePatchDraft`。
- backend 创建 `WorkspacePatchDraftReview(status = previewed)`。
- apply 仍必须由 Draft Review endpoint 和 Sales Workspace Kernel 完成。

V2.1 LLM runtime 允许的 formal write operations：

- `upsert_product_profile_revision`
- `upsert_lead_direction_version`
- `set_active_lead_direction`

V2.1 LLM runtime 不允许生成：

- search result
- ContactPoint
- CRM object
- direct ranking board write
- Markdown projection write

## 7. Error Semantics

LLM runtime failure must not mutate workspace.

| Condition | API error code | AgentRun status |
| --- | --- | --- |
| API key missing | `llm_runtime_unavailable` | `failed` |
| TokenHub request failed / timeout | `llm_runtime_unavailable` | `failed` |
| output is not JSON object | `llm_structured_output_invalid` | `failed` |
| JSON fails schema validation | `llm_structured_output_invalid` | `failed` |
| operation unsupported by kernel | `unsupported_workspace_operation` | `failed` |
| base workspace version stale | `workspace_version_conflict` | `failed` |

## 8. Metadata

AgentRun and `WorkspacePatchDraft.runtime_metadata` should record:

- provider: `tencent_tokenhub`
- model
- prompt_version
- mode: `real_llm_no_langgraph`
- source message ids
- context pack id
- token usage if available

Metadata must not record API keys, Authorization headers, full prompt bodies, or provider console exports.
