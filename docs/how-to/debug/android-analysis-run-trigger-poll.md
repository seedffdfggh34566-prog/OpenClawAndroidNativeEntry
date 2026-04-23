# Android analysis-run 触发与轮询联调

更新时间：2026-04-23

## 1. 用途

本文档用于联调 Android 控制壳层触发 `lead_analysis` 并轮询 `AgentRun`。

当前只覆盖：

- `POST /analysis-runs`，`run_type = lead_analysis`
- `GET /analysis-runs/{id}`
- 成功后刷新 `/history`
- 成功后打开 AnalysisResult 摘要页

不覆盖：

- `report_generation`
- `GET /lead-analysis-results/{id}`
- 真实 OpenClaw runtime 接入

---

## 2. 后端启动与设备转发

```bash
backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013
adb devices
adb reverse tcp:8013 tcp:8013
```

---

## 3. Android 操作

```bash
./gradlew :app:assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.openclaw.android.nativeentry/.MainActivity
```

操作步骤：

1. 确认已有 ProductProfile，或先在 ProductLearning 页创建一个
2. 打开 ProductProfile 页
3. 点击“生成获客分析”
4. 等待轮询结束
5. 确认跳转 AnalysisResult 页，并显示最新 published 摘要

---

## 4. 验证点

- ProductProfile 页显示 analysis-run 状态
- 运行成功后进入 AnalysisResult 页
- `/history.latest_analysis_result` 更新为新结果
- 当前仍不展示 LeadAnalysisResult 详情字段

---

## 5. 当前限制

- 轮询上限为 10 次，每次间隔 1 秒
- 当前只支持 `lead_analysis`
- 当前后端仍使用 stub runtime
