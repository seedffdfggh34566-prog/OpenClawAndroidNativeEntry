# 阶段性交接：Android analysis-run 触发与轮询

更新时间：2026-04-23

## 1. 本次改了什么

- Android backend client 新增 `POST /analysis-runs`
- Android backend client 新增 `GET /analysis-runs/{id}`
- 新增 AgentRun / AnalysisRun request-response DTO 与 parser
- ProductProfile 页新增“生成获客分析”按钮
- ProductProfile 页新增 analysis-run 状态展示
- OpenClawApp 新增 `lead_analysis` 创建与轮询流程
- 运行成功后刷新 `/history` 并跳转 AnalysisResult 摘要页

---

## 2. 为什么这么定

- 当前只补客户端触发与轮询，不扩展到报告生成
- 继续保持后端为正式对象权威真相
- 不新增未冻结的 `GET /lead-analysis-results/{id}`
- 继续复用轻量 `HttpURLConnection + org.json` 实现，避免架构扩张

---

## 3. 本次验证了什么

1. `backend/.venv/bin/python -m pytest backend/tests`：15 passed
2. `./gradlew :app:assembleDebug`：通过
3. `curl -X POST http://127.0.0.1:8013/analysis-runs ...`：成功创建 run
4. `curl http://127.0.0.1:8013/analysis-runs/{id}`：返回 succeeded 与 `result_summary`
5. `adb devices`：检测到设备 `f3b59f04`
6. `adb reverse tcp:8013 tcp:8013`：成功
7. `adb install -r app/build/outputs/apk/debug/app-debug.apk`：成功
8. `adb shell am start -n com.openclaw.android.nativeentry/.MainActivity`：成功
9. 真机 UI smoke：
   - ProductProfile 页显示“生成获客分析”
   - 点击后成功触发 `lead_analysis`
   - Android 轮询到 succeeded
   - 成功后跳转 AnalysisResult 页
   - AnalysisResult 页显示新生成的 published 摘要
   - `/history.latest_analysis_result` 更新为新生成结果

---

## 4. 已知限制

- 当前只支持 `lead_analysis`
- 当前不支持 `report_generation`
- 当前不读取 LeadAnalysisResult 详情，只展示 `/history.latest_analysis_result` 摘要
- 当前轮询上限为 10 次，每次 1 秒
- 当前仍使用 stub runtime，未接真实 OpenClaw runtime
- 当前 base URL 固定为 `http://127.0.0.1:8013`

---

## 5. 推荐下一步

1. 新建 report_generation 触发 / 轮询 task，覆盖 `run_type = report_generation`
2. 或先补 `GET /lead-analysis-results/{id}` contract，再增强 AnalysisResult 详情页
3. 在客户端运行链路稳定后，再拆真实 OpenClaw runtime 接入任务
