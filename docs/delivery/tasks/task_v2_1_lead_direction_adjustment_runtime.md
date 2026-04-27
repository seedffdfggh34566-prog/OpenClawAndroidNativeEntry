# Task: V2.1 Lead Direction Adjustment Runtime

状态：planned / blocked

更新时间：2026-04-27

## Objective

扩展 deterministic chat-first runtime，使用户能通过自然语言调整获客方向，并沉淀为新的 `LeadDirectionVersion`。

## Scope

- 从用户消息中识别行业、地区、客户规模、优先约束、排除行业和排除客户类型。
- 将调整写入 `WorkspacePatchDraft`，经 Draft Review 后正式写回。
- 记录 source message refs 和 change reason。

## Out Of Scope

- 不接搜索。
- 不生成具体公司候选。
- 不生成 ContactPoint。
- 不跳过 backend kernel。
