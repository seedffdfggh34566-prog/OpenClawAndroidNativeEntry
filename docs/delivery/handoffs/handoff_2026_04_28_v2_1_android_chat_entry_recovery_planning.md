# Handoff: V2.1 Android Chat Entry Recovery Planning

更新时间：2026-04-28

## Summary

根据 2026-04-28 人工验收反馈，之前 lightweight entry polish 的 product-entry done 结论不成立：用户在 Android app 上没有看到聊天入口。

本次只做规划层纠偏，不改 Android/backend/runtime 代码，不运行测试。

## Changed

- 将 `docs/product/project_status.md` 中 V2.1 状态降级为 `partial / android_chat_entry_missing`。
- 将 milestone acceptance review 中 lightweight entry criterion 从 `done` 修正为 `missing`。
- 开放 V2.1-only recovery package：
  - `docs/delivery/packages/package_v2_1_android_chat_entry_recovery.md`
- 开放当前 implementation task：
  - `docs/delivery/tasks/task_v2_1_android_chat_entry_recovery_and_demo_path.md`
- 更新 `_active.md`，允许 Execution Agent 在该 package 内 auto-continue。

## Validation

- 未运行测试或 build。原因：用户本轮明确表示“不用测试了”。
- 本次证据来源是人工验收反馈，不是自动化验证。

## Known Limits

- 旧 handoff / task 中关于 lightweight entry polish 的代码和 build evidence 仍保留为历史 delivery evidence，但不能作为 product-entry done 标准。
- Execution Agent 仍需实际修复 Android app 入口并补充可见聊天入口 evidence。
- 本 handoff 不声明 V2.1 milestone completed。

## Next Step

Execution Agent 执行：

- `docs/delivery/tasks/task_v2_1_android_chat_entry_recovery_and_demo_path.md`

边界：

- 只恢复 V2.1 Android chat-first product entry 和代表性 demo path。
- 不开放 V2.2 search / ContactPoint / CRM / formal LangGraph。
- 若需要新 API、migration、auth、tenant、多 workspace 产品化或 PRD/ADR 改义，停止并交回人工决策。
