# Handoff: V2.1 Android Chat Surface Productization Planning

更新时间：2026-04-28

## Summary

根据最新人工产品反馈，V2.1 Android 问题不再只是“入口是否存在”。入口和 Sales Workspace 页面已经能看到，但页面仍过于工程化，缺少接近真实产品的聊天界面。

本次规划层将当前开放 package / task 的推进目标从 `chat entry recovery` 收敛为 `chat surface productization`：

- 页面第一视觉应是聊天体验，不是 workspace/debug 对象面板。
- 用户应能看到当前 ConversationMessage 上下文。
- 聊天输入框应明显可见，并支持继续输入中文业务描述。
- assistant response / clarifying question / Draft Review 应以消息流或轻量结果卡片展示。
- workspace id、version、AgentRun id、DraftReview id 等工程信息应弱化、下移或折叠。

## Changed

- `docs/product/project_status.md`
  - 将 V2.1 状态口径从 `android_chat_entry_missing` 收敛为 `android_chat_surface_missing`。
  - 明确 Android workspace demo path 的当前 gap 是 chat surface productization。
- `docs/delivery/packages/package_v2_1_android_chat_entry_recovery.md`
  - 保留文件路径，更新 package 名称和目标为 `V2.1 Android Chat Surface Productization`。
  - 更新验收标准：conversation context、明显 composer、assistant / Draft Review result card、弱化工程信息。
- `docs/delivery/tasks/task_v2_1_android_chat_entry_recovery_and_demo_path.md`
  - 保留文件路径，更新任务名称和执行目标为 `V2.1 Android Chat Surface Productization And Demo Path`。
  - 增加可直接复制给 Execution Agent 的 prompt。
- `docs/delivery/tasks/_active.md`
  - 保留 current package / task，不新增队列。
  - 更新当前 auto-continue 范围为 Android chat surface productization。
- `docs/README.md`、`docs/delivery/README.md`
  - 同步当前主线描述和 delivery 任务总览。

## Validation

已验证：

- `rg -n "android_chat_surface_missing|Chat Surface Productization|chat surface|conversation context|Draft Review 结果|docs sync level and rationale" docs`
  - 结果：通过；project status、current package、current task、active queue 和 prompt 均可检索。
- `git diff --check`
  - 结果：通过。

## Known Limits

- 本次只做规划层落地，不改 Android / backend / runtime 代码。
- 当前任务文件路径仍保留 `chat_entry_recovery` 名称，避免再迁移文件；实际任务标题和目标已更新为 chat surface productization。
- 本次不声明 V2.1 milestone completed。
- V2.2 search / ContactPoint / CRM / formal LangGraph 仍 blocked。

## Next Step

Execution Agent 直接执行：

- `docs/delivery/tasks/task_v2_1_android_chat_entry_recovery_and_demo_path.md`

优先做 Android UI 产品化和真机可见证据，不继续扩展工作流文档。
