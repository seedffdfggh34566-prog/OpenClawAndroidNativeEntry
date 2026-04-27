# Task: V2.1 Product Profile Extraction Runtime

状态：planned / blocked

更新时间：2026-04-27

## Objective

扩展 deterministic chat-first runtime，使其能从 5 个中文验收样例中生成更真实的 `ProductProfileRevision` draft，而不是固定 FactoryOps AI 路径。

## Scope

- 等 clarifying questions 和 explanation prototype 完成后再开放。
- 从用户输入抽取产品类别、目标客户、行业、痛点、价值主张和不确定项。
- 输出仍通过 `WorkspacePatchDraft` -> Draft Review -> WorkspacePatch 写回。

## Out Of Scope

- 不接真实 LLM。
- 不接 V2.2 search / ContactPoint / CRM。
- 不跳过 Draft Review。
