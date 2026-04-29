# Delivery Package: V2.1 Android Chat Surface Productization

更新时间：2026-04-28

## 1. Package 定位

- Package 名称：V2.1 Android Chat Surface Productization
- 当前状态：`in_progress`
- 优先级：P0
- Package 类型：`implementation / product surface / product acceptance`
- Authorization source：human feedback on 2026-04-28: Android 入口和 workspace 已可见，但页面仍过于工程化，缺少接近 OpenClaw 前端的聊天上下文体验。
- 是否允许 package 内部 tasks / steps 连续执行：`yes`
- 完成后是否允许自动进入下游 package：`no`

本 package 只处理 V2.1 Android product experience 的 chat-first surface 和代表性 demo path。它不开放 V2.2 search / ContactPoint / CRM / formal LangGraph，也不声明 V2.1 milestone completed。

---

## 2. 背景与问题

此前 lightweight entry polish task 记录了代码、build、install/start evidence，但设备 click-level Workspace smoke 未完成。2026-04-28 人工验收反馈指出：

> Android app 上没有看到聊天入口。

后续人工观察确认：销售工作区入口和 Sales Workspace 页面已经出现，但页面仍是工程对象面板，缺少真实聊天产品应有的上下文对话流、明显输入框和 assistant / Draft Review 结果呈现。

因此，本 package 从“入口恢复”收敛为“Android chat surface 产品化”。V2.1 product milestone 当前状态应为 `partial / android_chat_surface_missing`。

---

## 3. Package 目标

本 package 目标是把 V2.1 的 Android product path 从“工程调试面板”推进为“用户可见、可操作、可复现的 chat-first 产品界面”：

1. App 首屏或明确导航路径暴露轻量入口“开始销售工作区”。
2. 用户点击后进入 Sales Workspace chat-first 页面。
3. 页面第一视觉应是聊天体验，而不是 workspace id/version/raw object/debug 面板。
4. 页面必须显示当前 ConversationMessage 上下文，user / assistant 消息应以可读对话流展示。
5. 聊天输入框必须明显可见，并允许用户用自然语言继续表达业务。
6. 代表性 V2.1 demo path 应从 Android 控制入口走通：进入 workspace、提交一轮业务描述、看到 Product Sales Agent 追问、assistant response 或 Draft Review 结果。
7. Draft Review / assistant result 应以轻量结果卡片呈现；工程信息默认弱化、下移或折叠。

---

## 4. Package 内任务

当前开放任务：

1. `docs/delivery/tasks/task_v2_1_android_chat_entry_recovery_and_demo_path.md`（in_progress，当前实际目标为 Android chat surface productization）

Package 内可连续推进的内部 steps：

1. 复核 Android app 当前首屏、导航、Workspace route 和 SalesWorkspaceScreen 信息架构。
2. 保留“开始销售工作区”入口，但把后续页面重构为 chat-first surface。
3. 将 ConversationMessage history 以消息流 / 气泡 / 清晰上下文展示。
4. 将 composer 放在用户容易发现的位置，并提供 loading、error、assistant response 状态。
5. 将 Draft Review / assistant result 作为结果卡片呈现，而不是工程调试主界面。
6. 弱化 workspace id、version、AgentRun id、DraftReview id 等工程信息。
7. 使用现有 backend API 创建或进入默认 `ws_demo` 并提交代表性中文业务输入。
8. 更新 task outcome 和 handoff；除非实际改变 milestone status，不默认更新 project_status / README / milestone review。

---

## 5. 允许范围

允许：

- Android app entry / navigation / state restore 的最小修复。
- Android Workspace screen 的聊天界面产品化、空态、错误态、loading、消息流和结果卡片。
- 既有 backend API integration 的 Android 侧兼容修复。
- 代表性 V2.1 demo path 的真机 evidence 和简短 handoff。
- 必要时修复阻断 V2.1 Android chat-first path 的小型 backend bug，但不得改变 public API contract。

禁止：

- 新增 backend public API endpoint。
- 新增 Alembic migration 或 schema baseline 变更。
- 多 workspace 产品化、账号、租户、权限、production onboarding。
- V2.2 search / evidence / ContactPoint implementation。
- CRM、自动触达、批量联系人。
- formal LangGraph graph / checkpoint lifecycle。
- 将 task 或 handoff 的完成升级为 milestone completion。

---

## 6. Stop Conditions

命中以下任一情况必须停止并交回人工决策：

- 恢复聊天入口需要新增 backend public API、migration、auth、tenant 或多 workspace 生命周期。
- 需要改变 V2.1 PRD / ADR 的产品含义。
- 修复范围扩大到 V2.2 search / ContactPoint / CRM / formal LangGraph。
- Android app 的当前主导航结构与 V2.1 产品入口冲突，需要重新决策信息架构。
- 代表性 demo path 需要外部 provider、生产账号或 secrets 才能成立。
- 要求做完整设计系统、复杂动画、Web 前端或跨端前端重写。

---

## 7. 验收标准

Package 可关闭的最低标准：

1. Android app 上用户能看到“开始销售工作区”或等价明确入口。
2. 点击后能进入一个以聊天为主视觉的 Sales Workspace 页面。
3. 页面显示当前 conversation context，至少最近 user / assistant messages 可读。
4. 聊天输入框明显可见，用户不需要理解 `workspace` 技术概念也能继续输入。
5. 至少一条自然语言业务输入可以从 Android 发送到既有 backend path。
6. 若出现 Draft Review、追问或 assistant result，应能在 Android 上以结果卡片或消息流被用户看到。
7. 工程调试信息被弱化，不抢占主视觉。
8. 真机验证记录入口、对话上下文和输入框可见；尽量完成一轮中文输入 smoke。
9. 只更新 task outcome 和 handoff；除非状态真实变化，不默认更新 `project_status.md`、milestone review 或 README。
10. V2.2 implementation 仍 blocked。

验收完成后只能建议 Status / Planning flow 重新 review V2.1 milestone；不能由本 package 直接声明 V2.1 done。
