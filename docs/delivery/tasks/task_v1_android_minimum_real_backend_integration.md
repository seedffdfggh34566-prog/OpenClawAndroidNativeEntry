# Task：Android 壳层最小真实后端对接

更新时间：2026-04-23

## 1. 任务定位

- 任务名称：Android 壳层最小真实后端对接
- 建议路径：`docs/delivery/tasks/task_v1_android_minimum_real_backend_integration.md`
- 当前状态：`planned`
- 优先级：P0

本任务用于让当前 Android 控制壳层从占位数据切到真实后端读取，但只做最小读路径联调，不扩展到完整分析流程执行。

---

## 2. 任务目标

在不重写当前 Android 壳层架构的前提下，至少实现以下结果：

- 首页与 History 页改为读取真实 `/history`
- ProductProfile 详情页改为读取真实 `GET /product-profiles/{id}`
- AnalysisReport 页改为读取真实 `GET /reports/{id}`
- 现有占位壳层只保留为无数据或失败时的降级显示，不再作为默认主数据源

---

## 3. 当前背景

当前项目已经完成：

- Android 控制壳层重构
- V1 最小后端 API contract 冻结
- V1 最小正式后端实现落地

当前 Android 页面结构已经符合 V1 信息架构，但主要内容仍来自 `V1ShellPlaceholderState`。如果继续在占位数据上推进，会导致：

- Android 壳层无法验证真实后端对象结构是否可用
- 首页与 History 页的真实聚合 contract 无法尽早暴露问题
- 后续 runtime 接入会缺少客户端读取基线

因此，当前最合理的下一步是先把 Android 切到真实读路径。

---

## 4. 范围

本任务 In Scope：

- 新增最小 Android 数据接入层
- 读取并映射 `/history`
- 按 `/history` 返回的对象引用读取 `ProductProfile` 与 `AnalysisReport` 详情
- 将 Home / History / ProductProfile / AnalysisReport 页面接到真实数据
- 提供最小失败态、空态与加载态
- 补充本地联调所需 runbook

本任务 Out of Scope：

- `POST /product-profiles`
- `POST /analysis-runs`
- `GET /analysis-runs/{id}` 的真实轮询流程
- 完整编辑能力
- 鉴权、账号、多环境切换
- 引入 Hilt、Retrofit、Room、MVI 等大改动

---

## 5. 涉及文件

高概率涉及：

- `app/src/main/java/com/openclaw/android/nativeentry/ui/OpenClawApp.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/navigation/OpenClawNavHost.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/home/HomeScreen.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/shell/V1ShellPlaceholderState.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/shell/V1ShellScreens.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/settings/SettingsScreen.kt`
- `app/build.gradle.kts`

建议新增：

- `app/src/main/java/com/openclaw/android/nativeentry/data/backend/`

参考文件：

- `docs/reference/api/backend-v1-minimum-contract.md`
- `docs/architecture/clients/mobile-information-architecture.md`
- `docs/delivery/tasks/task_v1_android_control_shell_refactor.md`
- `docs/delivery/tasks/task_v1_backend_minimum_implementation.md`

---

## 6. 产出要求

至少应产出：

1. 一个最小 Android backend client
2. 一组与 `/history`、`ProductProfileDetail`、`AnalysisReportDetail` 对应的 Android 侧 DTO / mapper
3. 一套从真实后端状态映射到当前壳层页面的数据模型
4. 一份本地联调说明
5. 对应 handoff

---

## 7. 推荐实现边界

本任务默认采用以下实现边界：

1. 不重写当前页面结构
   - 继续保留 `Home / History / Ops / Settings` 顶层结构
   - 优先替换数据源，而不是重做 UI

2. 不引入大规模 Android 架构升级
   - 当前工程没有现成网络栈
   - 为控制 blast radius，本任务应新增最小 HTTP 访问能力和手写映射
   - 不把该任务扩展成完整 repository / DI 重构

3. 开发期联调默认走 `adb reverse`
   - 后端当前本地启动端口是 `8013`
   - Android 端本轮默认读取 `http://127.0.0.1:8013`
   - 本地联调前通过 `adb reverse tcp:8013 tcp:8013` 建立设备到开发主机的转发

4. 当前读取策略以 `/history` 为主入口
   - 首页与 History 先读 `/history`
   - 当 `/history.latest_product_profile` 存在时，再读取详情页所需 `GET /product-profiles/{id}`
   - 当 `/history.latest_report` 存在时，再读取 `GET /reports/{id}`
   - 当前不要求 Android 主动发起新的分析 run

5. 占位数据仅作为降级方案
   - 后端空库时，页面应展示空态文案，而不是伪装成真实已有结果
   - 请求失败时允许显示“当前使用占位壳层/调试态”提示，但不能默认继续展示样例数据冒充真实结果

---

## 8. 验收标准

满足以下条件可认为完成：

1. Android 首页能基于真实 `/history` 显示：
   - `current_run`
   - 最近对象摘要
   - 是否存在继续流程入口
2. History 页能基于真实 `/history.recent_items` 展示列表
3. ProductProfile 页能读取真实 `GET /product-profiles/{id}`
4. AnalysisReport 页能读取真实 `GET /reports/{id}`
5. backend 空库、请求失败、后端不可达三种情况都有明确 UI
6. 工程通过最小构建校验
7. 至少完成一次 `adb reverse + 后端本地启动 + Android 真机/模拟器读取` 的 smoke test

---

## 9. 推荐执行顺序

建议执行顺序：

1. 先确认后端本地启动命令与 `adb reverse` 联调命令
2. 在 Android 侧新增最小 backend client 和 DTO / mapper
3. 用 `/history` 替换 `V1ShellPlaceholderState` 的默认数据来源
4. 补 ProductProfile 与 AnalysisReport 的详情读取
5. 为空态、失败态和加载态补最小 UI
6. 运行 `assembleDebug` 与真机/模拟器 smoke test
7. 更新 task 状态、runbook 与 handoff

---

## 10. 风险与注意事项

- 不要把本任务扩展成完整“产品学习聊天页接后端”
- 不要在本任务里一并实现写路径和分析触发
- 不要因为接真实数据就推翻现有壳层导航
- `127.0.0.1:8013` 只在 `adb reverse` 已建立时成立，联调说明必须写清
- 当前后端无鉴权，Android 端不要提前设计复杂 token 体系

---

## 11. 下一步衔接

本任务完成后，推荐继续：

1. Android 发起 `POST /product-profiles` 与最小写路径 task
2. Android 触发 `POST /analysis-runs` / 轮询 `GET /analysis-runs/{id}` task
3. 真实 OpenClaw runtime 与 backend 接入 task
