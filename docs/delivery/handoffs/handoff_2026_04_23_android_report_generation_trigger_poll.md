# 阶段性交接：Android report_generation 触发与轮询

更新时间：2026-04-23

## 1. 本次改了什么

- AnalysisResult 页新增“生成分析报告”按钮
- V1 backend UI state 新增 `reportRun`
- OpenClawApp 新增 `report_generation` 创建与轮询流程
- 复用现有 `POST /analysis-runs` 与 `GET /analysis-runs/{id}` client / DTO / parser
- run succeeded 后读取 `result_summary.report_id`
- 成功后读取 `GET /reports/{id}` 并跳转 AnalysisReport 页
- 成功后刷新 `/history`
- 补充轮询失败、run failed/cancelled、缺少 `report_id` 的失败态

---

## 2. 为什么这么定

- 当前目标是补齐 V1 客户端对象链路，不扩大后端 contract
- `LeadAnalysisResult` 详情接口仍不在本任务范围内
- Android 继续作为控制入口，不成为业务主真相
- 继续沿用轻量 `HttpURLConnection + org.json + coroutine` 风格

---

## 3. 本次验证了什么

1. `backend/.venv/bin/python -m pytest backend/tests`：15 passed
2. `./gradlew :app:assembleDebug`：通过
3. `curl http://127.0.0.1:8013/health`：返回 `{"status":"ok"}`
4. `curl http://127.0.0.1:8013/history`：返回现有 V1 对象摘要
5. `curl -X POST http://127.0.0.1:8013/analysis-runs ... run_type=report_generation`：成功创建 run
6. `curl http://127.0.0.1:8013/analysis-runs/run_dccc85be`：返回 `succeeded` 与 `result_summary.report_id=rep_f6852601`
7. `adb devices`：检测到设备 `f3b59f04`
8. `adb reverse tcp:8013 tcp:8013`：成功
9. `adb install -r app/build/outputs/apk/debug/app-debug.apk`：成功
10. `adb shell am start -n com.openclaw.android.nativeentry/.MainActivity`：成功
11. 真机 UI smoke：
    - AnalysisResult 页显示“生成分析报告”
    - 点击后成功触发 `report_generation`
    - 成功后跳转 AnalysisReport 页
    - AnalysisReport 页显示新报告 `AndroidSmokeProductCreatedByAndroidSmokeDeviceSmoke 获客分析报告`
    - `/history.latest_report` 更新为 Android 触发生成的 `rep_8e087d95`

---

## 4. 已知限制

- AnalysisResult 页仍只展示 `/history.latest_analysis_result` 摘要
- 当前未新增 `GET /lead-analysis-results/{id}`
- 当前轮询上限为 10 次，每次 1 秒
- 当前后端仍使用 stub runtime
- 当前 base URL 固定为 `http://127.0.0.1:8013`
- 当前未接入鉴权、账号、多环境切换或报告导出

---

## 5. 推荐下一步

1. 执行 `task_v1_analysis_result_detail_contract.md`
2. 先冻结并实现 `GET /lead-analysis-results/{id}`
3. 再让 Android AnalysisResult 页读取并展示真实详情
4. 详情 contract 稳定后，再拆真实 OpenClaw runtime 接入任务
