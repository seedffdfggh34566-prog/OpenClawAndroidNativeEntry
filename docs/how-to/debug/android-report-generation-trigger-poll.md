# Android report_generation 触发与轮询联调

更新时间：2026-04-23

## 1. 用途

本文档用于联调 Android 控制壳层在已有 LeadAnalysisResult 后触发 `report_generation` 并打开真实 AnalysisReport。

当前覆盖：

- `POST /analysis-runs`，`run_type = report_generation`
- `GET /analysis-runs/{id}`
- 成功后读取 `result_summary.report_id`
- 成功后读取 `GET /reports/{id}`
- 成功后刷新 `/history`
- 成功后打开 AnalysisReport 页

不覆盖：

- `GET /lead-analysis-results/{id}`
- 报告导出
- 真实 OpenClaw runtime 接入
- 鉴权、账号、多环境切换

---

## 2. 后端启动与设备转发

```bash
backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013
adb devices
adb reverse tcp:8013 tcp:8013
```

可先检查：

```bash
curl http://127.0.0.1:8013/health
curl http://127.0.0.1:8013/history
```

---

## 3. Android 操作

```bash
./gradlew :app:assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.openclaw.android.nativeentry/.MainActivity
```

操作步骤：

1. 确认 `/history.latest_product_profile` 和 `/history.latest_analysis_result` 都存在
2. 打开 AnalysisResult 页
3. 点击“生成分析报告”
4. 等待轮询结束
5. 确认自动跳转 AnalysisReport 页
6. 确认 AnalysisReport 页显示新生成报告
7. 再次检查 `/history.latest_report` 是否更新

---

## 4. curl smoke

```bash
curl -X POST http://127.0.0.1:8013/analysis-runs \
  -H 'Content-Type: application/json' \
  -d '{
    "run_type": "report_generation",
    "product_profile_id": "<product_profile_id>",
    "lead_analysis_result_id": "<lead_analysis_result_id>",
    "trigger_source": "curl_report_generation_smoke"
  }'

curl http://127.0.0.1:8013/analysis-runs/<run_id>
curl http://127.0.0.1:8013/history
```

预期：

- run 最终进入 `succeeded`
- `result_summary.report_id` 存在
- `/history.latest_report.id` 更新为新报告

---

## 5. 当前限制

- 轮询上限为 10 次，每次间隔 1 秒
- AnalysisResult 页仍不读取详情接口
- 当前后端仍使用 stub runtime
- Android base URL 固定为 `http://127.0.0.1:8013`
