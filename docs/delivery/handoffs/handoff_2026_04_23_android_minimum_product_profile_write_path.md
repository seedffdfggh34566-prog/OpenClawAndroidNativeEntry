# 阶段性交接：Android 最小 ProductProfile 写路径

更新时间：2026-04-23

## 1. 本次改了什么

- Android backend client 新增 `POST /product-profiles`
- 新增 ProductProfile 创建请求 / 响应 DTO 与 parser
- ProductLearning 页新增最小创建表单
- OpenClawApp 新增提交状态、提交动作、成功后刷新 `/history` 与详情跳转
- 创建成功后 ProductProfile 页显示新建 draft 对象

---

## 2. 为什么这么定

- 当前只补最小写路径，不扩展到完整产品学习聊天页
- 继续保持 Android 为控制入口，后端仍是正式对象权威真相
- 复用既有 `HttpURLConnection + org.json` 轻量实现，避免引入重型 Android 基础设施
- 创建结果仍是 `draft`，不把本任务扩展为确认或分析触发流程

---

## 3. 本次验证了什么

1. `backend/.venv/bin/python -m pytest backend/tests`：15 passed
2. `./gradlew :app:assembleDebug`：通过
3. `curl http://127.0.0.1:8013/health`：返回 `{"status":"ok"}`
4. `curl -X POST http://127.0.0.1:8013/product-profiles ...`：成功创建 `CurlSmokeProduct`
5. `adb devices`：检测到设备 `f3b59f04`
6. `adb reverse tcp:8013 tcp:8013`：成功
7. `adb install -r app/build/outputs/apk/debug/app-debug.apk`：成功
8. `adb shell am start -n com.openclaw.android.nativeentry/.MainActivity`：成功
9. 真机 UI smoke：
   - ProductLearning 页显示最小创建表单
   - 表单提交成功创建 ProductProfile
   - 创建成功后跳转 ProductProfile 页
   - ProductProfile 页显示新建 draft 对象详情
   - `/history` 显示新建 ProductProfile 为 latest
   - 后端停止后再次提交，ProductLearning 页显示失败态

---

## 4. 已知限制

- 当前 base URL 固定为 `http://127.0.0.1:8013`
- 依赖 `adb reverse tcp:8013 tcp:8013`
- 当前只创建 ProductProfile draft，不支持编辑、确认或版本替换
- 尚未实现 `POST /analysis-runs` 或 `GET /analysis-runs/{id}` 轮询
- 当前仍使用 stub runtime，未接真实 OpenClaw runtime
- 本轮未新增自动化 UI 测试，仅完成真机 smoke

---

## 5. 推荐下一步

1. 新建 Android analysis-run 触发 / 轮询 task，覆盖 `POST /analysis-runs` 与 `GET /analysis-runs/{id}`
2. 决定是否补 `GET /lead-analysis-results/{id}` contract
3. 在客户端触发与轮询稳定后，再拆真实 OpenClaw runtime 接入任务
