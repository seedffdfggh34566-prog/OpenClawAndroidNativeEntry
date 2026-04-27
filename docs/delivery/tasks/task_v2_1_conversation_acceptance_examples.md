# Task: V2.1 Conversation Acceptance Examples

状态：done

更新时间：2026-04-27

## Objective

定义 5 个中文业务样例，作为 V2.1 conversational product experience completion 的验收输入。

## Scope

- 覆盖不同业务类型：工业设备维保软件、本地企业培训服务、中小企业财税 SaaS、园区招商服务、制造业外包服务。
- 每个样例定义初始输入、期望追问、期望产品画像、期望获客方向、期望解释型回答和 trace refs。
- 明确样例不要求 V2.2 search / ContactPoint / CRM。

## Outcome

- 新增 `docs/reference/evals/v2_1_conversation_acceptance_examples.md`。
- 后续实现必须以这些样例作为 deterministic acceptance baseline。

## Validation

```bash
rg "工业设备维保软件|本地企业培训服务|中小企业财税 SaaS|园区招商服务|制造业外包服务" docs/reference/evals/v2_1_conversation_acceptance_examples.md
rg "3 to 5 useful Chinese clarifying questions|ProductProfileRevision|LeadDirectionVersion|ContactPoint" docs/reference/evals/v2_1_conversation_acceptance_examples.md
git diff --check
```
