# Task: V2.1 Android OpenClaw-Style Multi-Thread Chat

更新时间：2026-04-28

## 1. 任务定位

- 任务名称：V2.1 Android OpenClaw-Style Multi-Thread Chat
- 当前状态：`done`
- 优先级：P0
- 所属 package：`V2.1 Android OpenClaw-Style Multi-Thread Chat`
- Authorization source：human instruction on 2026-04-28: 当前 Android 对话框太小、不够像 OpenClaw，并需要同一个项目下多个对话。
- 完成后是否允许自动进入下游任务：`no`

## 2. 目标

在同一个 Sales Workspace 项目下支持多个 conversation thread，并将 Android Workspace 页面调整为 OpenClaw Control UI 风格的信息架构：线程切换、大 transcript、固定 composer、运行状态和次级工作区详情。

## 3. Scope

In scope：

- 新增 `SalesWorkspaceConversationThread` backend model / persistence / migration。
- 给 `ConversationMessage`、`SalesAgentTurnRun`、`SalesAgentTurnContextPack` 增加 `thread_id`。
- 新增 thread list/create/messages/agent-turn routes。
- 保持旧 messages / agent-turn endpoints 映射到 default thread `main`。
- Android client/model/parser/state 支持 thread list、thread selection、new thread 和 thread-scoped messages。
- Android Workspace 页面显示 thread switcher、“新对话”、large transcript、fixed composer。
- 验证 thread history 不串线，且 real LLM smoke 走 `real_llm_no_langgraph`。

Out of scope：

- auth / tenant / CRM / V2.2 search/contact。
- formal LangGraph、WebSocket streaming、完整 abort / inject。
- 产品 milestone completion claim。

## 4. Execution Outcome

状态：`done`。

完成内容：

- Backend 新增 conversation thread 维度，默认线程为 `main`。
- 新 endpoint 已增加：thread list/create、thread messages、thread-scoped sales-agent turns。
- 旧 endpoint 仍兼容 `main` thread。
- Agent turn context 只读取当前 thread 的 recent messages，同时继续读取同一 workspace 的正式对象。
- Android Workspace 改为 thread switcher + transcript-first chat surface；composer 固定在底部，“新对话”可见。
- Composer 从全宽大卡片收敛为更紧凑输入区，移动端 transcript 空间明显增大。
- 工作区详情仍保留，但作为次级入口，不抢主视口。

## 5. Validation

- `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_persistence_schema.py backend/tests/test_sales_workspace_chat_first_api.py -q` passed：`21 passed, 1 skipped`。
- `backend/.venv/bin/alembic upgrade head` passed。
- `./gradlew :app:assembleDebug` passed。
- `adb install -r app/build/outputs/apk/debug/app-debug.apk` passed。
- `adb shell am start -n com.openclaw.android.nativeentry/.MainActivity` launched app。
- UIAutomator confirmed Home shows “开始销售工作区”。
- UIAutomator confirmed Workspace shows thread switcher (“连锁餐饮”, “工厂维保”, “新对话”), large transcript, composer label “对 Sales Agent 说”, and send button。
- Backend smoke created two threads under `ws_demo` and confirmed histories remain separate。
- Real LLM smoke succeeded for both threads with runtime metadata `real_llm_no_langgraph`, provider `tencent_tokenhub`, model `minimax-m2.5`。
- `backend/.env` was only checked for presence / git-ignore status; contents were not read or printed。

## 6. Known Limits

- Device validation used a temporary local backend at `127.0.0.1:8013` with SQLite + JSON store for manual testing continuity。
- In JSON-store mode, chat trace state is process-local; restarting the temporary backend loses seeded thread messages unless Postgres store is used。
- Android currently implements thread switching and thread-scoped turn submission, not streaming, abort, inject, auth, tenant, CRM, V2.2 search/contact, or formal LangGraph。
- This task is delivery evidence only and does not declare V2.1 milestone complete。

## 7. Handoff

Detailed handoff：`docs/delivery/handoffs/handoff_2026_04_28_v2_1_android_openclaw_multithread_chat.md`。

## 8. UI Bugfix Follow-up: Compact Chat Surface

状态：`done`。

2026-04-28 追加验收反馈修复：

- Workspace route 隐藏全局 TopAppBar / bottom NavigationBar，避免双标题和底栏压缩聊天区；Home / History / Ops / Settings 保持原 chrome。
- Loaded Workspace 调整为 `CompactWorkspaceHeader` + `ThreadSwitcher` + large transcript + folded settings + compact composer。
- Composer 固定底部并收敛为 1-3 行输入条；模式选择和工作区详情默认折叠到“设置”。
- Transcript 保留 thread-scoped history，降低 message metadata 权重，并新增 Compose Preview mock cases。

追加验证：

- `./gradlew :app:assembleDebug` passed。
- `./gradlew :app:lintDebug` passed。
- `adb install -r app/build/outputs/apk/debug/app-debug.apk` passed。
- UIAutomator confirmed Home “开始销售工作区” remains visible。
- UIAutomator confirmed Workspace shows no global app chrome, visible thread switcher / “新对话”, large transcript, fixed composer “对 Sales Agent 说”, and folded settings “回复模式” / “工作区详情” after tapping “设置”。
- Device smoke with ADBKeyboard submitted Chinese input “我们做工业设备维保软件”; Android displayed the user message and assistant follow-up in the transcript。
- Thread switch smoke confirmed “工厂维保” and “连锁餐饮” histories do not visually cross over; “新对话” creates and selects a blank welcome thread。

Known limit：

- The Chinese smoke response still appeared as the existing five-question follow-up. This UI bugfix did not change backend runtime mode or LLM behavior。

## 9. UI Bugfix Follow-up: Chat Interaction State

状态：`done`。

2026-04-28 追加验收反馈修复：

- 发送 chat-first 输入后，Android 立即把 user message 作为本地 pending bubble 放入 transcript，并立即清空 composer；后端返回并刷新 history 后去重。
- `+ 新对话` 改为先弹出“命名新对话”对话框，再用输入 title 创建 thread；空 title fallback 为“新对话”。
- “可审阅更新”作为当前 assistant 回复的 Draft Review 附件，不再在主聊天卡片中暴露无上下文“生成可审阅更新”按钮。
- Draft Review 写入成功后保留 `applied` 终态，显示已写入版本，不再回到可重新生成状态。

追加验证：

- `./gradlew :app:assembleDebug` passed。
- `./gradlew :app:lintDebug` passed。
- `adb install -r app/build/outputs/apk/debug/app-debug.apk` passed。
- UIAutomator confirmed “命名新对话” dialog；输入 `OPC 客户验证` 后创建成功，header/thread tab 显示该名称。
- ADBKeyboard Chinese smoke submitted `我们是面向OPC的一人公司销售助手`；发送 1 秒内 composer 清空、user bubble 进入 transcript，并显示 `Sales Agent 正在思考...`。
- 后端返回后 user message 未重复，Draft Review 附件出现且没有“生成可审阅更新”按钮。
- Draft Review smoke confirmed `采纳` 后 workspace 仍为 v5；`写入` 后 workspace 为 v6，并显示 `更新建议状态：已写入` / `工作区已更新到版本 6。`

Known limit：

- “工作区信息沉淀的后端开发者可视化页面”未在本 task 实现；应另开 dev-only read-only diagnostics task。

## 10. Stop Condition

未触发 stop condition。新增 backend API / migration 是本次人工开放 package 的显式范围；未越过 V2.2 search/contact、CRM、auth、tenant、formal LangGraph 或 milestone completion 边界。
