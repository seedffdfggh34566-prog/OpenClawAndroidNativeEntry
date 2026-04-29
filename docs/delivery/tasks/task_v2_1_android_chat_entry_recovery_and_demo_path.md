# Task: V2.1 Android Chat Surface Productization And Demo Path

更新时间：2026-04-28

## 1. 任务定位

- 任务名称：V2.1 Android Chat Surface Productization And Demo Path
- 当前状态：`done`
- 优先级：P0
- 任务类型：`implementation / product surface`
- 所属 package：`V2.1 Android Chat Surface Productization`
- Authorization source：human product feedback on 2026-04-28: 入口和 workspace 已可见，但页面过于粗糙，需要接近 OpenClaw 前端的聊天上下文体验。
- Execution mode：`Product-first`
- 是否允许执行 agent 自主推进：`yes`
- 完成后是否允许自动进入下游任务：`no`
- 文档同步级别：`Level 1 task`

---

## 2. 任务目标

把 V2.1 Android product experience 从工程调试式 workspace 面板推进为可用的聊天产品界面：

> 用户可以像使用 OpenClaw 前端一样，在 Android 上看到当前聊天上下文、继续输入业务描述，并看到 assistant / Draft Review 结果。

当前任务不是继续证明 backend path 存在，而是把 Sales Workspace 页面做成一个可被人使用和验收的 chat-first surface。

---

## 3. 当前问题

历史 lightweight entry polish task 记录了代码和 build/install evidence，但没有完成 Workspace 页点击级 smoke。当前人工验收反馈说明：

- 后续真机观察确认销售工作区入口和 Sales Workspace 页面已经出现。
- 但页面仍过于工程化，用户看到的是 workspace / version / review 等对象面板，而不是清晰的聊天体验。
- 因此历史 `done` 只能保留为 delivery evidence，不能作为 V2.1 product experience completion 标准。
- V2.1 当前状态为 `partial / android_chat_surface_missing`。

---

## 4. Scope

In scope：

- 阅读并遵守 `app/AGENTS.md`。
- 复核 Android app 首屏、主导航、Workspace route 和 SalesWorkspaceScreen 信息架构。
- 保留用户能发现并点击“开始销售工作区”的入口。
- 点击后使用现有 `POST /sales-workspaces` 创建或进入默认 `ws_demo`。
- 将 Workspace 页面第一视觉改为聊天体验：
  - 当前 ConversationMessage 上下文以可读消息流展示。
  - user / assistant / clarifying question / explanation / draft summary 明确区分。
  - 输入框在用户容易发现的位置。
  - loading / error / assistant response / Draft Review 状态可见。
  - Draft Review 作为轻量结果卡片或紧邻消息流的结果区。
  - workspace id、version、AgentRun id、DraftReview id 等工程信息弱化、下移或折叠。
- 使用现有 backend path 完成或尽量完成一轮中文 chat-first smoke。
- 更新 task outcome 和一个简短 handoff。

Product-first execution rules：

- 本任务优先做 Android UI / state / navigation 和真机产品体验。
- 只更新本 task outcome 和一个短 handoff。
- 不更新 `docs/product/project_status.md`、milestone review、root / docs README、`_active.md` 或 package closeout。
- 如果执行中确实需要更新上述高层文档，先停止并请求人工决策。

Out of scope：

- 新 backend endpoint。
- 新 migration / schema baseline。
- 多 workspace selector 或 workspace lifecycle 产品化。
- auth / tenant / production SaaS。
- V2.2 search / ContactPoint / CRM。
- formal LangGraph。
- 自动触达。
- 完整设计系统、复杂动画、Web 前端或跨端重写。
- 大规模 Android 架构重写。

---

## 5. 高概率涉及文件

Android：

- `app/AGENTS.md`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/OpenClawApp.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/workspace/SalesWorkspaceScreen.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/data/backend/SalesWorkspaceBackendClient.kt`
- 相关 navigation / state / model / parser 文件

Docs：

- `docs/delivery/tasks/task_v2_1_android_chat_entry_recovery_and_demo_path.md`
- `docs/delivery/handoffs/`

默认不更新：

- `docs/product/project_status.md`
- milestone review
- root / docs README
- `_active.md`

除非执行结果真实改变 current package / task、队列、capability status 或 milestone evidence。

---

## 6. Acceptance Criteria

满足以下条件可关闭任务：

1. Android app 启动后，用户能在首屏或明确导航路径看到 Sales Workspace / “开始销售工作区”入口。
2. 用户点击入口后进入一个以聊天为主视觉的页面。
3. 页面展示当前 conversation context，至少最近消息上下文可读。
4. 聊天输入框明显可见，且文案不要求用户理解 `workspace` 技术概念。
5. 提交一条自然语言业务描述后，Android 能显示 backend 返回的追问、assistant response 或 Draft Review 结果。
6. Draft Review / assistant result 不再作为工程调试主面板，而是作为消息流结果或轻量结果卡片。
7. workspace id、version、AgentRun id、DraftReview id 等工程信息不抢占主视觉。
8. 历史详情页恢复态不会阻断用户回到聊天入口。
9. 未新增 backend API、migration、schema、V2.2、CRM、formal LangGraph、auth、tenant 或 multi-workspace scope。
10. 真机验证记录入口、聊天上下文和输入框可见；尽量记录一轮中文输入 smoke。
11. task outcome 和 handoff 已同步；不默认更新高层状态文档。

---

## 7. Validation Guidance

用户本轮明确表示“不用测试了”。因此当前规划层不运行测试。

Execution Agent 接手实现时，应按 `app/AGENTS.md` 和 Android validation ladder 执行最轻必要验证。推荐但不由规划层代跑：

- `./gradlew :app:assembleDebug`
- 如设备可用，安装/启动并人工或 UIAutomator / screenshot 记录：
  - “开始销售工作区”入口可见。
  - conversation context 可见。
  - 聊天输入框可见。
  - 发送一轮中文输入后的 response / loading / error 可见。
- 如 backend 相关，运行最小 targeted backend check；不得读取或暴露 secrets。

如果设备验证不可用，必须在 handoff 中明确写出未验证项，不能把任务关闭为 product accepted。

---

## 8. Stop Conditions

执行中遇到以下情况必须停止：

- 需要新增 backend API / migration。
- 需要改变 V2.1 PRD / ADR 含义。
- 需要引入 V2.2 search/contact、formal LangGraph、CRM、auth、tenant。
- Android 当前信息架构无法承载“开始销售工作区”入口，需要产品决策。
- 无法证明用户能从 app 进入可用聊天界面。
- 需要把工程对象面板整体替换为复杂新设计系统。

---

## 9. Expected Outcome

本任务完成后，V2.1 仍不自动 declared done。它只提供 Android chat surface product evidence，供 Status / Planning Agent 在人工验收通过后再判断 milestone status。

## 10. Execution Outcome

状态：`done`。

本次执行完成了 Android chat surface productization 的最小闭环：

- Android Home 首屏保留“开始销售工作区”主入口，底部导航显示“销售工作区”。
- Workspace loaded 后第一视觉改为 transcript-first 聊天界面，显示可读 conversation context；空历史时显示 Sales Agent 欢迎消息。
- 最近 user / assistant `ConversationMessage` 以“你 / Sales Agent”消息气泡展示，不再把 `Message` / `AgentRun` / raw id 放在主视觉。
- 聊天输入框 `对 Sales Agent 说` 在 Sales Workspace 页首屏可见；中文 placeholder 使用业务描述示例。
- 发送中显示“Sales Agent 正在思考”；`chatFirstTurnState.Loaded` 进入 transcript 展示追问 / 解释 / Draft Review 摘要。
- Draft Review 操作保留在结果动作区；workspace / version / ContextPack / projection 等工程详情默认折叠到“工作区详情”次级入口。
- Android chat-first turn read timeout 调整为 120s，支持真实 LLM smoke；backend API path 未变化。
- 没有新增 backend API、migration、schema、V2.2 search/contact、CRM、formal LangGraph、auth、tenant 或 multi-workspace scope。

Validation：

- `./gradlew :app:assembleDebug` passed。
- `adb devices` detected `f3b59f04 device`。
- `adb install -r app/build/outputs/apk/debug/app-debug.apk` passed。
- `adb shell am start -n com.openclaw.android.nativeentry/.MainActivity` launched app。
- UIAutomator evidence confirmed Home shows “开始销售工作区” and bottom nav “销售工作区”。
- `backend/.env` was checked for presence / git-ignore status only; contents were not read or printed.
- Temporary backend started with SQLite + JSON store + `OPENCLAW_BACKEND_SALES_AGENT_RUNTIME_MODE=llm` and `OPENCLAW_BACKEND_SALES_AGENT_LLM_PROMPT_VERSION=sales_agent_turn_llm_v1` on `127.0.0.1:8013`; `adb reverse tcp:8013 tcp:8013` configured; `/health` returned `{"status":"ok"}`。
- UIAutomator evidence confirmed Workspace page shows transcript-first Sales Agent messages, fixed composer, `EditText` label “对 Sales Agent 说”, and collapsed “工作区详情” entry.
- Chinese smoke completed through ADBKeyboard:
  - Input 1: “我们做工业设备维保软件”; Android displayed “你 · 产品理解” and a Chinese Sales Agent response.
  - Input 2: “我们做面向连锁餐饮的排班和库存SaaS”; Android displayed “你 · 产品+方向” and a different Chinese Sales Agent response about连锁餐饮排班和库存 SaaS.
- Backend run metadata confirmed `run_sales_turn_001`, `run_sales_turn_003`, and `run_sales_turn_005` all `succeeded` with `mode=real_llm_no_langgraph`, provider `tencent_tokenhub`, model `minimax-m2.5`, prompt version `sales_agent_turn_llm_v1`.
- One duplicate second-message submission occurred during ADB input retry; the latest visible assistant response acknowledged the duplicate message. The run metadata still proves real LLM runtime rather than deterministic runtime.
- Original IME restored to `com.baidu.input_oppo/.ImeService` after smoke.
- `git diff --check` passed.

Known limits：

- Validation used a temporary local backend with SQLite and JSON store for device smoke.
- The smoke used the existing real LLM runtime path, not deterministic runtime; no production backend, V2.2 search/contact, CRM, formal LangGraph, new backend API, migration, or schema change was involved.
- The task provides Android product-surface evidence only. It does not declare V2.1 milestone or product experience complete.

## 11. Execution Agent Prompt

建议直接复制给 Execution Agent：

```text
你是一个 Dev Agent。本线程只做 Android V2.1 chat surface 产品化，不做文档治理。

目标：
把当前 Sales Workspace 页面从工程调试面板，改成接近 OpenClaw 前端体验的聊天界面：
1. 用户能看到当前 ConversationMessage 上下文。
2. user / assistant 消息以清晰对话流展示。
3. 聊天输入框明显可见，并能继续提交中文输入。
4. Draft Review / assistant result 以轻量结果卡片展示，不让 workspace id / version / raw AgentRun 抢主视觉。

严格限制：
- 优先只改 Android UI，主要是 SalesWorkspaceScreen.kt。
- 如确有必要，可改 OpenClawApp.kt 的状态传递。
- 不新增 backend API。
- 不改 PRD / project_status / README / milestone review。
- 不创建新 package。
- 文档最多写一个简短 handoff，说明 UI 改动和真机结果。

设计要求：
- 页面第一视觉应是聊天体验，不是 Workspace 对象详情。
- Conversation history 要可读，至少显示最近消息上下文。
- 输入框要在用户容易发现的位置。
- 工程调试信息可以折叠、下移或弱化。
- 保留 Draft Review apply 能力，但作为结果动作而不是主界面中心。

验证：
1. ./gradlew :app:assembleDebug
2. adb install -r app/build/outputs/apk/debug/app-debug.apk
3. adb shell am start -n com.openclaw.android.nativeentry/.MainActivity
4. 真机确认能看到聊天上下文和输入框
5. 尽量完成一次中文输入 smoke
6. 用截图或 uiautomator dump 记录结果

完成后只报告：
- 改了哪些 Android 文件
- docs sync level and rationale
- 真机上是否看到聊天上下文
- 真机上是否看到输入框
- 是否完成一轮中文输入
- 未完成的限制
```
