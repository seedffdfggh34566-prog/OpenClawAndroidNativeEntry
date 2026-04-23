# 阶段性交接：Android 最小真实后端读路径

更新时间：2026-04-23

## 1. 本次改了什么

- 新增 Android 侧最小 V1 backend client，使用 `HttpURLConnection + org.json` 读取 `http://127.0.0.1:8013`
- 新增 `/history`、`ProductProfileDetail`、`AnalysisReport` DTO / parser 与 `V1BackendUiState`
- Home / History 改为优先显示真实 `/history`
- ProductProfile 页读取真实 `GET /product-profiles/{id}`
- AnalysisReport 页读取真实 `GET /reports/{id}`
- AnalysisResult 页仅展示 `/history.latest_analysis_result` 摘要，不新增详情接口
- 新增联调 runbook：`docs/how-to/debug/android-real-backend-read-path.md`

---

## 2. 为什么这么定

- 当前任务只要求最小真实读路径联调，不做写路径和运行触发
- 继续保持 Android 作为控制入口，不把客户端扩展成业务主真相层
- 不引入 Retrofit / Hilt / Room，避免把 P0 联调任务扩成 Android 架构重写
- 详情页读取 `/history` 中的 latest id，避免本轮扩大导航和路由设计

---

## 3. 本次验证了什么

1. `backend/.venv/bin/python -m pytest backend/tests`：15 passed
2. `./gradlew :app:assembleDebug`：通过
3. `curl http://127.0.0.1:8013/health`：返回 `{"status":"ok"}`
4. `curl http://127.0.0.1:8013/history`：返回已有 ProductProfile / AnalysisResult / Report
5. `adb devices`：检测到设备 `f3b59f04`
6. `adb reverse tcp:8013 tcp:8013`：成功
7. `adb install -r app/build/outputs/apk/debug/app-debug.apk`：成功
8. `adb shell am start -n com.openclaw.android.nativeentry/.MainActivity`：成功
9. 真机 UI smoke：
   - Home 显示真实 `/history` 摘要
   - ProductProfile 页显示真实 `GET /product-profiles/{id}` 内容
   - AnalysisReport 页显示真实 `GET /reports/{id}` 内容
   - AnalysisResult 页显示 `/history.latest_analysis_result` 摘要与接口边界说明
   - 后端不可达显示失败态与“查看占位调试数据”入口
   - 临时空库后端显示真实空态

---

## 4. 已知限制

- 当前 base URL 固定为 `http://127.0.0.1:8013`
- 依赖 `adb reverse tcp:8013 tcp:8013` 完成真机到开发机后端转发
- ProductProfile / Report 详情页只打开 `/history` 中的 latest 对象
- AnalysisResult 详情接口不在当前最小 contract 中，本轮未新增
- 尚未实现 `POST /product-profiles`、`POST /analysis-runs` 或轮询 `GET /analysis-runs/{id}`
- 当前仍使用 stub runtime，未接真实 OpenClaw runtime

---

## 5. 推荐下一步

1. 新建 Android 最小写路径 task，覆盖 `POST /product-profiles`
2. 新建 Android analysis-run 触发 / 轮询 task，覆盖 `POST /analysis-runs` 与 `GET /analysis-runs/{id}`
3. 在客户端读写联调稳定后，再拆真实 OpenClaw runtime 接入任务
