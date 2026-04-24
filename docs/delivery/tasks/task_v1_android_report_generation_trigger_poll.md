# Task：Android report_generation 触发与轮询

更新时间：2026-04-23

## 1. 任务定位

- 任务名称：Android report_generation 触发与轮询
- 建议路径：`docs/delivery/tasks/task_v1_android_report_generation_trigger_poll.md`
- 当前状态：`done`
- 优先级：P0

本任务用于让 Android 在已有 `LeadAnalysisResult` 摘要后，具备触发报告生成 run、轮询状态并打开真实 `AnalysisReport` 的最小能力。

---

## 2. 任务目标

在不重写当前 Android 壳层架构的前提下，实现：

- AnalysisResult 页可触发 `POST /analysis-runs`，`run_type = report_generation`
- Android 轮询 `GET /analysis-runs/{id}`
- 运行成功后刷新 `/history`
- 运行成功后读取并打开 `GET /reports/{id}`

---

## 3. 范围

本任务 In Scope：

- 复用现有 Android analysis-run client / DTO / parser
- 在 AnalysisResult 页接入“生成分析报告”按钮
- 在 AnalysisResult 页展示 report_generation 运行状态
- 成功后读取新生成报告详情并跳转 AnalysisReport 页
- 补充 task、runbook 与 handoff

本任务 Out of Scope：

- `GET /lead-analysis-results/{id}`
- LeadAnalysisResult 详情页增强
- 报告导出
- 真实 OpenClaw runtime 接入
- 鉴权、账号、多环境切换
- 引入 Hilt、Retrofit、Room、WorkManager 或重型 MVI 框架

---

## 4. 验收标准

满足以下条件可认为完成：

1. Android 真机可从 AnalysisResult 页触发 `report_generation`
2. Android 能轮询 `GET /analysis-runs/{id}` 到 terminal 状态
3. 成功后 `/history.latest_report` 更新
4. 成功后跳转 AnalysisReport 页
5. AnalysisReport 页显示新生成报告详情
6. 工程通过最小构建校验
7. 至少完成一次 `adb reverse + 后端本地启动 + Android 真机触发 report_generation` 的 smoke test

---

## 5. 本次结果

已完成：

- AnalysisResult 页新增“生成分析报告”入口
- Android 通过 `POST /analysis-runs` 创建 `report_generation` run
- Android 轮询 `GET /analysis-runs/{id}`
- run succeeded 后读取 `result_summary.report_id`
- Android 拉取 `GET /reports/{id}` 并跳转 AnalysisReport 页
- 成功后刷新 `/history`，`latest_report` 指向新生成报告
- 轮询失败、运行失败、缺少 `report_id` 时显示明确失败态

本任务未扩大到：

- `GET /lead-analysis-results/{id}`
- 报告导出
- 真实 OpenClaw runtime
- 鉴权、账号、多环境切换

---

## 6. 验证记录

已完成验证：

1. `backend/.venv/bin/python -m pytest backend/tests`：15 passed
2. `./gradlew :app:assembleDebug`：通过
3. `curl http://127.0.0.1:8013/health`：返回 `{"status":"ok"}`
4. `curl http://127.0.0.1:8013/history`：返回现有 ProductProfile / LeadAnalysisResult / Report
5. `curl -X POST http://127.0.0.1:8013/analysis-runs ... run_type=report_generation`：创建 `run_dccc85be`
6. `curl http://127.0.0.1:8013/analysis-runs/run_dccc85be`：返回 `succeeded` 与 `result_summary.report_id=rep_f6852601`
7. `adb devices`：检测到设备 `f3b59f04`
8. `adb reverse tcp:8013 tcp:8013`：成功
9. `adb install -r app/build/outputs/apk/debug/app-debug.apk`：成功
10. `adb shell am start -n com.openclaw.android.nativeentry/.MainActivity`：成功
11. 真机 UI smoke：
    - AnalysisResult 页显示“生成分析报告”
    - 点击后触发 `report_generation`
    - 成功后跳转 AnalysisReport 页
    - AnalysisReport 页显示新报告 `AndroidSmokeProductCreatedByAndroidSmokeDeviceSmoke 获客分析报告`
    - `/history.latest_report` 更新为 Android 触发生成的 `rep_8e087d95`

---

## 7. 风险与注意事项

- 不要在本任务中新增 LeadAnalysisResult 详情接口
- 不要在本任务中接真实 OpenClaw runtime
- 不要扩展报告导出或编辑能力
- 当前 base URL 仍固定为 `http://127.0.0.1:8013`

---

## 8. 后续建议

下一步建议新建并执行 AnalysisResult 详情 contract / 页面 follow-up，让获客分析结果从 `/history.latest_analysis_result` 摘要升级为正式详情读取。
