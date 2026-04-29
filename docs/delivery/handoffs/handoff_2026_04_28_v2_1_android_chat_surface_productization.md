# Handoff: V2.1 Android Chat Surface Productization

日期：2026-04-28

## Scope

当前 task：`docs/delivery/tasks/task_v2_1_android_chat_entry_recovery_and_demo_path.md`

本次只推进 Android V2.1 Sales Workspace chat surface 和代表性中文 smoke。不新增 backend API、migration、schema、V2.2 search/contact、CRM、formal LangGraph、auth、tenant 或 multi-workspace scope。

## Changed Files

- `app/src/main/java/com/openclaw/android/nativeentry/ui/home/HomeScreen.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/navigation/OpenClawDestination.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/navigation/OpenClawNavHost.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/OpenClawApp.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/data/backend/SalesWorkspaceBackendClient.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/workspace/SalesWorkspaceScreen.kt`
- `docs/delivery/tasks/task_v2_1_android_chat_entry_recovery_and_demo_path.md`
- `docs/delivery/handoffs/handoff_2026_04_28_v2_1_android_chat_surface_productization.md`

## What Changed

- Home 首屏提供“开始销售工作区”主入口，点击进入 `Workspace` route。
- 底部导航 `Workspace` 文案调整为“销售工作区”。
- 默认 `ws_demo` 已存在时，Android 创建入口会加载现有 workspace 和消息历史，而不是停在 HTTP 409。
- Sales Workspace loaded 后第一视觉改为 transcript-first 聊天界面：
  - 空历史显示 Sales Agent 欢迎消息。
  - 最近 user / assistant 消息以“你 / Sales Agent”气泡展示。
  - 输入框 label 为“对 Sales Agent 说”，placeholder 使用中文业务示例。
  - 发送中显示“Sales Agent 正在思考”。
  - backend 返回的 assistant result 进入 transcript，不再把 raw `Message` / `AgentRun` / id 放在主视觉。
- Draft Review 操作保留为结果动作区；工作区详情、候选排序、ContextPack、projection 默认折叠到“工作区详情”次级入口。
- Android chat-first turn read timeout 调整为 120s，避免真实 LLM 调用被旧的 5s read timeout 截断；其他 backend API path 不变。

## Validation

- `./gradlew :app:assembleDebug` passed。
- `adb devices` detected `f3b59f04 device`。
- `adb install -r app/build/outputs/apk/debug/app-debug.apk` passed。
- `adb shell am start -n com.openclaw.android.nativeentry/.MainActivity` launched app。
- UIAutomator evidence confirmed Home shows “开始销售工作区” and bottom nav “销售工作区”。
- `backend/.env` was checked for presence / git-ignore status only; contents were not read or printed.
- Temporary backend started with SQLite + JSON store + `OPENCLAW_BACKEND_SALES_AGENT_RUNTIME_MODE=llm` and `OPENCLAW_BACKEND_SALES_AGENT_LLM_PROMPT_VERSION=sales_agent_turn_llm_v1` on `127.0.0.1:8013`; `adb reverse tcp:8013 tcp:8013` configured; `/health` returned `{"status":"ok"}`。
- UIAutomator evidence confirmed Workspace page shows transcript-first Sales Agent messages, `EditText` label “对 Sales Agent 说”, fixed composer, and collapsed “工作区详情” entry; ContextPack / Projection details do not appear as the main chat viewport by default.
- Chinese smoke completed through ADBKeyboard against real LLM runtime:
  - Input: “我们做工业设备维保软件”。
  - Android displayed “你 · 产品理解”。
  - Android displayed a Sales Agent Chinese assistant response.
  - Second input: “我们做面向连锁餐饮的排班和库存SaaS”。
  - Android displayed “你 · 产品+方向” and a different Sales Agent Chinese assistant response about连锁餐饮排班和库存 SaaS.
- Backend run metadata confirmed `run_sales_turn_001`, `run_sales_turn_003`, and `run_sales_turn_005` all `succeeded` with `mode=real_llm_no_langgraph`, provider `tencent_tokenhub`, model `minimax-m2.5`, prompt version `sales_agent_turn_llm_v1`.
- One duplicate second-message submission occurred during ADB input retry; the latest visible assistant response correctly acknowledged the duplicate message. This does not affect the real LLM smoke evidence.
- Original IME restored to `com.baidu.input_oppo/.ImeService` after smoke.
- `git diff --check` passed.

## Known Limits

- Device smoke used a temporary local backend with SQLite and JSON store for demo continuity.
- The smoke used the existing real LLM runtime path, not deterministic runtime, but it did not use production backend, V2.2 search/contact, CRM, or formal LangGraph.
- Real LLM output quality is provider / prompt dependent; this task only fixed the Android chat surface and verified the runtime mode was no longer deterministic.
- This handoff is task evidence only; it does not declare V2.1 milestone or product experience complete.

## Next Step

Stop here and hand back to Status / Planning flow for any V2.1 milestone acceptance review or downstream package decision.
