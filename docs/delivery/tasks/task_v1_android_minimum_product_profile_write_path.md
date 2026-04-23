# Task：Android 最小 ProductProfile 写路径

更新时间：2026-04-23

## 1. 任务定位

- 任务名称：Android 最小 ProductProfile 写路径
- 建议路径：`docs/delivery/tasks/task_v1_android_minimum_product_profile_write_path.md`
- 当前状态：`done`
- 优先级：P0

本任务用于让 Android 控制壳层在已完成真实后端读路径后，具备创建第一版 `ProductProfile` 草稿的最小写入能力。

---

## 2. 任务目标

在不重写当前 Android 壳层架构的前提下，至少实现以下结果：

- ProductLearning 页提供最小输入表单
- Android 调用真实 `POST /product-profiles`
- 创建成功后刷新 `/history`
- 创建成功后跳转到 ProductProfile 详情页
- ProductProfile 详情页能读取新创建对象

---

## 3. 范围

本任务 In Scope：

- 新增 Android 侧 `POST /product-profiles` client 方法
- 新增请求 / 响应 DTO 与 JSON parser
- 在 ProductLearning 页接入最小表单字段：
  - `name`
  - `one_line_description`
  - `source_notes`
- 提供提交中的 loading、成功后跳转、失败提示
- 补充 task 与 handoff

本任务 Out of Scope：

- `PATCH /product-profiles/{id}`
- ProductProfile 确认接口
- `POST /analysis-runs`
- `GET /analysis-runs/{id}` 轮询
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
- `docs/delivery/tasks/task_v1_android_minimum_real_backend_integration.md`
- `docs/how-to/debug/android-real-backend-read-path.md`

---

## 5. 验收标准

满足以下条件可认为完成：

1. Android 真机可在 ProductLearning 页输入产品名称和一句话描述
2. 点击提交后成功调用 `POST /product-profiles`
3. 创建成功后刷新 `/history`
4. 创建成功后跳转到 ProductProfile 页，并显示新对象详情
5. 后端不可达或提交失败时有明确 UI 提示
6. 工程通过最小构建校验
7. 至少完成一次 `adb reverse + 后端本地启动 + Android 真机创建 ProductProfile` 的 smoke test

---

## 6. 推荐执行顺序

1. 确认 `POST /product-profiles` contract
2. 新增 Android request / response DTO 和 parser
3. 新增 client 写方法
4. 在 ProductLearning 页接入最小表单
5. 在 OpenClawApp 中持有提交状态并处理成功跳转
6. 运行后端测试、Android 构建与真机 smoke
7. 更新 task 状态与 handoff

---

## 7. 风险与注意事项

- 不要把本任务扩展成完整产品学习聊天页
- 不要在本任务里触发 analysis-run
- 不要新增未冻结的后端接口
- 不要把 Android 提交草稿升级成正式确认流程
- 当前 base URL 仍固定为 `http://127.0.0.1:8013`

---

## 8. 实际产出

本次已完成以下产出：

1. Android backend client 新增 `POST /product-profiles`
2. 新增 ProductProfile 创建请求 / 响应 DTO 与 JSON parser
3. ProductLearning 页新增最小创建表单：
   - 产品名称
   - 一句话描述
   - 补充材料（可选）
4. OpenClawApp 新增 ProductProfile 创建状态与提交流程
5. 创建成功后刷新 `/history`
6. 创建成功后读取新对象详情并跳转 ProductProfile 页
7. 创建失败时在 ProductLearning 页显示后端错误
8. 新增本任务 handoff

---

## 9. 本次定稿边界

本次明确采用以下边界：

- Android 继续采用 `HttpURLConnection + org.json + Dispatchers.IO`
- 不新增 Retrofit、Hilt、Room、WorkManager 或重型 MVI 框架
- 不修改后端 API contract
- 不新增 PATCH、确认接口或 analysis-run 触发
- 不接真实 OpenClaw runtime
- 不引入鉴权、多环境切换或配置页

---

## 10. 已做验证

本次已完成以下验证：

1. `backend/.venv/bin/python -m pytest backend/tests`
2. `./gradlew :app:assembleDebug`
3. `curl http://127.0.0.1:8013/health`
4. `curl -X POST http://127.0.0.1:8013/product-profiles ...`
5. `adb devices`
6. `adb reverse tcp:8013 tcp:8013`
7. `adb install -r app/build/outputs/apk/debug/app-debug.apk`
8. `adb shell am start -n com.openclaw.android.nativeentry/.MainActivity`
9. 真机 UI smoke：
   - ProductLearning 页显示最小创建表单
   - 表单提交成功
   - 创建成功后跳转 ProductProfile 页
   - ProductProfile 页显示新建 draft 对象详情
   - `/history` 显示新建 ProductProfile 为 latest
   - 后端停止后再次提交，ProductLearning 页显示失败态

---

## 11. 实际结果说明

当前该任务已满足原验收目标：

1. Android 已能创建第一版 ProductProfile 草稿
2. Android 已能在创建后刷新真实后端状态
3. Android 已能在创建后进入真实 ProductProfile 详情页
4. 后续可继续拆 Android analysis-run 触发 / 轮询任务
