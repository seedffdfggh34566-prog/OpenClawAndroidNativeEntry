# Task: V2.1 Sales Workspace Answer Quality And Device Bugfix

更新时间：2026-04-29

## 1. 任务定位

- 任务名称：V2.1 Sales Workspace Answer Quality And Device Bugfix
- 当前状态：`done`
- 优先级：P0
- 任务类型：`bugfix`
- Authorization source：human instruction on 2026-04-29，继续执行深度真机测试后暴露的 Sales Agent 回答质量与 Android 体验 bugfix。
- 完成后是否允许自动进入下游任务：`no`

## 2. 目标

修复 V2.1 Sales Workspace 当前产品体验中的核心缺陷：

- 真实 LLM transient timeout 后不可恢复。
- assistant 回复泄露 `patch_operations`、`revision_id`、`workspace_goal` 等内部术语。
- 产品描述已足够形成最小 product profile 时仍只追问、不沉淀。
- Android 设置按钮展开后不够可见，真机测试无法切换到指定测试 workspace。
- Android LLM 失败后缺少基于同一用户消息的重试路径。

本任务不声明 V2.1 milestone 完成，只修当前 chat-first workspace 的已知 bug。

## 3. Scope

In scope：

- 后端 LLM runtime transient request retry。
- LLM 输出 normalization / user-visible sanitizer。
- product profile / lead direction 最小草稿 fallback。
- Android workspace 设置面板、开发测试 workspace selector。
- Android LLM failure retry，不重复创建用户消息。
- Targeted backend pytest、Android debug build、最小 device smoke。
- 更新本 task outcome 和 handoff。

Out of scope：

- 新增正式 backend API / schema / migration。
- V2.2 search / contact / CRM / 自动触达。
- formal LangGraph、streaming、abort / inject。
- 正式 multi-workspace 产品管理、auth、tenant。
- PRD / roadmap / project_status / milestone review 更新。
- 读取或输出 `backend/.env` secret。

## 4. Expected files

- `backend/runtime/sales_workspace_chat_turn_llm.py`
- `backend/api/sales_workspace.py`
- `backend/tests/test_sales_workspace_chat_first_llm_runtime.py`
- `app/src/main/java/com/openclaw/android/nativeentry/data/backend/SalesWorkspaceBackendClient.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/navigation/OpenClawNavHost.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/OpenClawApp.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/workspace/SalesWorkspaceScreen.kt`
- this task file
- `docs/delivery/handoffs/handoff_2026_04_29_v2_1_sales_workspace_answer_quality_and_device_bugfix.md`

## 5. Validation

Required：

- `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_llm_runtime.py -q`
- `./gradlew :app:assembleDebug`
- `git diff --check`

Device smoke if adb device is available：

- install debug APK
- launch `com.openclaw.android.nativeentry/.MainActivity`
- confirm Settings panel exposes reply modes and dev/test workspace selector
- confirm backend connection / real LLM status when environment permits

## 6. Stop conditions

Stop and return to planning / human decision if the implementation would require：

- DB schema or migration.
- New formal product endpoint.
- V2.2 search / evidence / contact implementation.
- Product scope or PRD meaning change.
- Auth / tenant / multi-workspace formal product management.
- Secret inspection or secret output.

## 7. Execution Outcome

状态：`done`。

完成内容：

- 后端 LLM request transient error 增加 1 次重试，并在 runtime metadata 记录 `llm_request_attempts`。
- 后端 formatter 对 LLM assistant content 做用户可见清洗，避免内部字段和 runtime 术语直接出现在聊天回复。
- 产品描述足够时，即使 LLM 返回 clarifying/no patch，后端也会生成最小 product profile draft review。
- 获客方向模式仍保持“先给找客户建议，再沉淀 draft”的 fallback。
- Android 发送失败后保留用户 bubble；LLM 不可用时展示轻量错误和“重试”按钮，重试复用同一个 message id。
- Android 设置面板上移，增加“开发测试工作区 ID”输入和“切换/创建”按钮，便于真机深测进入指定 workspace。

未改变：

- 未新增正式 backend API、schema、migration。
- 未改 PRD、roadmap、project_status、milestone review。
- 未把 draft 自动写入正式 workspace；写入仍需要用户点击“写入”。

## 8. Validation

- `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_llm_runtime.py -q` passed：`17 passed`。
- `./gradlew :app:assembleDebug` passed。
- `./gradlew :app:lintDebug` passed。
- `git diff --check` passed。
- Device smoke on `f3b59f04` passed：
  - `adb reverse tcp:8013 tcp:8013` succeeded。
  - Backend on `127.0.0.1:8013` returned `{"status":"ok"}` in LLM mode。
  - APK install and launch succeeded。
  - Home showed `开始销售工作区`。
  - Workspace showed `主对话`、`新对话`、`对 Sales Agent 说`。
  - Settings opened and showed `开发测试工作区 ID`、`切换/创建`、`回复模式`、`产品理解`、`找客户建议`。
  - ADBKeyboard Chinese input smoke succeeded；发送后 user bubble immediately appeared and `Sales Agent 正在思考...` was visible。
  - Real LLM turn returned `run_sales_turn_001 succeeded main real_llm_no_langgraph 1` and generated a previewed `可保存到工作区` draft review。

## 9. Known Limits

- Dev/test workspace selector 是当前测试入口，不是正式 workspace list / multi-project 产品体验。
- LLM 连续失败仍会返回 `llm_runtime_unavailable`，不会回退 deterministic runtime。
- Android 真机深度 LLM smoke 依赖 backend、`adb reverse`、真实 LLM key 和设备可用性；缺失时只能记录 blocked。

## 10. Handoff

Detailed handoff：`docs/delivery/handoffs/handoff_2026_04_29_v2_1_sales_workspace_answer_quality_and_device_bugfix.md`。
