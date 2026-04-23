# Task：Android analysis-run 触发与轮询

更新时间：2026-04-23

## 1. 任务定位

- 任务名称：Android analysis-run 触发与轮询
- 建议路径：`docs/delivery/tasks/task_v1_android_analysis_run_trigger_poll.md`
- 当前状态：`done`
- 优先级：P0

本任务用于让 Android 在已能创建和读取 `ProductProfile` 后，具备触发最小 `lead_analysis` run 并轮询状态的能力。

---

## 2. 任务目标

在不重写当前 Android 壳层架构的前提下，实现：

- ProductProfile 页可触发 `POST /analysis-runs`
- Android 轮询 `GET /analysis-runs/{id}`
- 运行成功后刷新 `/history`
- 运行成功后跳转 AnalysisResult 摘要页

---

## 3. 范围

本任务 In Scope：

- 新增 Android 侧 analysis-run request / response DTO
- 新增 `POST /analysis-runs` client 方法
- 新增 `GET /analysis-runs/{id}` client 方法
- 在 ProductProfile 页接入“生成获客分析”按钮
- 在 ProductProfile 页展示 queued / running / succeeded / failed 状态
- 成功后刷新 `/history` 并进入 AnalysisResult 摘要页
- 补充 task 与 handoff

本任务 Out of Scope：

- `report_generation`
- `GET /lead-analysis-results/{id}`
- 报告生成或报告轮询
- ProductProfile 确认接口
- 真实 OpenClaw runtime 接入
- 鉴权、账号、多环境切换
- 引入 Hilt、Retrofit、Room、WorkManager 或重型 MVI 框架

---

## 4. 涉及文件

高概率涉及：

- `app/src/main/java/com/openclaw/android/nativeentry/data/backend/*`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/OpenClawApp.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/navigation/OpenClawNavHost.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/shell/V1ShellScreens.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/shell/V1BackendUiState.kt`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/handoffs/*`

参考文件：

- `docs/reference/api/backend-v1-minimum-contract.md`
- `docs/delivery/tasks/task_v1_android_minimum_product_profile_write_path.md`

---

## 5. 验收标准

满足以下条件可认为完成：

1. Android 真机可从 ProductProfile 页触发 `lead_analysis`
2. Android 能轮询 `GET /analysis-runs/{id}` 到 terminal 状态
3. 成功后 `/history.latest_analysis_result` 更新
4. 成功后跳转 AnalysisResult 摘要页
5. 后端不可达或 run 失败时有明确 UI 提示
6. 工程通过最小构建校验
7. 至少完成一次 `adb reverse + 后端本地启动 + Android 真机触发 lead_analysis` 的 smoke test

---

## 6. 风险与注意事项

- 当前后端开发模式允许 draft ProductProfile 触发 stub `lead_analysis`
- 不要在本任务中接 `report_generation`
- 不要新增未冻结的 `LeadAnalysisResult` 详情接口
- 不要把 stub runtime 替换成真实 OpenClaw runtime

---

## 7. 实际产出

本次已完成以下产出：

1. Android backend client 新增 `POST /analysis-runs`
2. Android backend client 新增 `GET /analysis-runs/{id}`
3. 新增 AgentRun / AnalysisRun request-response DTO 与 parser
4. ProductProfile 页新增“生成获客分析”按钮
5. ProductProfile 页新增 analysis-run 状态展示
6. OpenClawApp 新增 `lead_analysis` 创建与轮询流程
7. 运行成功后刷新 `/history`
8. 运行成功后跳转 AnalysisResult 摘要页
9. 新增本任务 handoff

---

## 8. 本次定稿边界

本次明确采用以下边界：

- 只触发 `lead_analysis`
- 不触发 `report_generation`
- 不新增 `GET /lead-analysis-results/{id}`
- 不修改后端 API contract
- 不接真实 OpenClaw runtime
- 轮询上限为 10 次，每次间隔 1 秒
- Android 继续采用 `HttpURLConnection + org.json + Dispatchers.IO`

---

## 9. 已做验证

本次已完成以下验证：

1. `backend/.venv/bin/python -m pytest backend/tests`
2. `./gradlew :app:assembleDebug`
3. `curl -X POST http://127.0.0.1:8013/analysis-runs ...`
4. `curl http://127.0.0.1:8013/analysis-runs/{id}`
5. `adb devices`
6. `adb reverse tcp:8013 tcp:8013`
7. `adb install -r app/build/outputs/apk/debug/app-debug.apk`
8. `adb shell am start -n com.openclaw.android.nativeentry/.MainActivity`
9. 真机 UI smoke：
   - ProductProfile 页显示“生成获客分析”
   - 点击后成功触发 `lead_analysis`
   - Android 轮询到 succeeded
   - 成功后跳转 AnalysisResult 页
   - AnalysisResult 页显示新生成的 published 摘要
   - `/history.latest_analysis_result` 更新为新生成结果

---

## 10. 实际结果说明

当前该任务已满足原验收目标：

1. Android 已能从 ProductProfile 触发获客分析 run
2. Android 已能轮询 AgentRun 到完成
3. Android 已能在成功后展示最新 AnalysisResult 摘要
4. 后续可继续拆 report_generation 触发 / 轮询，或先补 AnalysisResult 详情 contract
