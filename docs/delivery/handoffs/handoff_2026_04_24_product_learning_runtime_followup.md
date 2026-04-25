# Handoff：2026-04-24 Product Learning Runtime Follow-up

## 本次变更

- backend 实现 `product_learning` run type，继续复用 `AgentRun`
- `POST /product-profiles` 改为：
  - 创建 `ProductProfile draft`
  - 同时创建 `product_learning` `AgentRun`
  - 返回非空 `current_run`
- LangGraph 新增 `product_learning_graph`
- backend 写回同一个 `ProductProfile`，并派生 `learning_stage`
- `POST /product-profiles/{id}/confirm` 收紧为：
  - `ready_for_confirmation` 才允许确认
  - collecting draft 返回 `409`
- Android 最小接线已完成：
  - create response 读取 `current_run`
  - 轮询 `GET /analysis-runs/{id}`
  - 成功后刷新 `GET /product-profiles/{id}` 与 `/history`
  - `ProductProfile` 页面按 `learningStage` 禁用/放开确认按钮

## 主要文件

- backend
  - `backend/api/product_learning.py`
  - `backend/api/schemas.py`
  - `backend/api/serializers.py`
  - `backend/api/services.py`
  - `backend/api/main.py`
  - `backend/runtime/types.py`
  - `backend/runtime/adapter.py`
  - `backend/runtime/graphs/product_learning.py`
  - `backend/tests/test_api.py`
  - `backend/tests/test_services.py`
- Android
  - `app/src/main/java/com/openclaw/android/nativeentry/data/backend/V1BackendModels.kt`
  - `app/src/main/java/com/openclaw/android/nativeentry/data/backend/V1BackendJsonParser.kt`
  - `app/src/main/java/com/openclaw/android/nativeentry/ui/OpenClawApp.kt`
  - `app/src/main/java/com/openclaw/android/nativeentry/ui/shell/V1BackendUiState.kt`
  - `app/src/main/java/com/openclaw/android/nativeentry/ui/shell/V1ShellScreens.kt`
  - `app/src/main/java/com/openclaw/android/nativeentry/ui/home/HomeScreen.kt`
- docs
  - `docs/delivery/tasks/task_v1_product_learning_runtime_followup.md`
  - `docs/delivery/tasks/_active.md`
  - `docs/reference/api/backend-v1-minimum-contract.md`
  - `docs/architecture/runtime/langgraph-runtime-architecture.md`

## 验证

- `backend/.venv/bin/python -m pytest backend/tests` -> `23 passed`
- `OPENCLAW_BACKEND_DATABASE_PATH=/tmp/openclaw_manual_8013.db backend/.venv/bin/alembic upgrade head`
- backend startup + `GET /health` -> `{"status":"ok"}`
- 手工 API smoke：
  - `POST /product-profiles`
  - poll `GET /analysis-runs/{id}`
  - `GET /product-profiles/{id}`
  - `POST /product-profiles/{id}/confirm`
  - `POST /analysis-runs` (`lead_analysis`)
- `./gradlew :app:assembleDebug`
- `adb devices` -> one device online
- `adb install -r app/build/outputs/apk/debug/app-debug.apk`
- `adb shell monkey -p com.openclaw.android.nativeentry -c android.intent.category.LAUNCHER 1`

## 已知限制

- product learning 仍使用受控 Python heuristic，不接真实 LLM
- `learning_stage` 仍为 backend 派生字段，不持久化入库
- Android 已验证 build/install/launch，但未做完整人工界面点击 smoke

## 建议下一步

- 回到规划层，决定下一个正式任务：
  - 多轮 product learning chat / public endpoint
  - product learning observability
  - 产品结果页与报告页的表达迭代
