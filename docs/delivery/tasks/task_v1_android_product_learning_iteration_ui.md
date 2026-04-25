# Task：V1 Android Product Learning Iteration UI

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V1 Android Product Learning Iteration UI
- 建议路径：`docs/delivery/tasks/task_v1_android_product_learning_iteration_ui.md`
- 当前状态：`done`
- 优先级：P2

本任务用于在 backend 迭代 contract 与 LLM phase 1 明确后，把当前 Android 端的“提交一次 + 等待富化”学习页升级为可继续补充信息的轻量交互页。

---

## 1.1 队列衔接

- 当前 task 是否允许执行 agent 自主推进：`yes`
- 建议上游入口：`docs/delivery/tasks/task_v1_product_learning_llm_phase1.md`
- 建议下游任务：
  1. 视结果再拆 product learning polish / UX follow-up
- 停止条件：
  - backend iteration contract 尚未冻结
  - backend public API 尚未稳定
  - 需要把页面扩大成完整聊天客户端重写

---

## 2. 任务目标

在不把 Android 端扩大成完整 chat app 的前提下，实现：

1. 学习页可展示当前理解摘要
2. 学习页可展示缺失字段
3. 学习页可提交一轮补充信息
4. 学习页可展示当前 run 状态
5. `ready_for_confirmation` 后突出确认 CTA

---

## 3. 当前背景

当前 Android 已经具备：

- create response 的 `current_run` 轮询
- `learningStage` 展示
- confirm gating

但当前仍缺：

- 用户无法继续补充第二轮信息
- 学习页还是“单次提交”心智
- UI 还没形成真正的 product learning 体验

这个任务应在 backend contract 稳定后再做，否则 UI 会被后端反复拖着改。

---

## 4. 范围

本任务 In Scope：

- ProductLearningScreen 的最小迭代式 UI
- 新 contract 对应的 DTO / parser / state 接线
- 缺失字段 / 当前摘要 / run 状态展示
- confirm CTA 与学习阶段表达的交互收口

本任务 Out of Scope：

- 完整聊天消息系统
- streaming token UI
- 消息持久化时间线
- Android 大规模导航重构
- backend API 设计

---

## 5. 涉及文件

高概率涉及：

- `app/src/main/java/com/openclaw/android/nativeentry/data/backend/*`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/OpenClawApp.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/shell/V1ShellScreens.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/home/HomeScreen.kt`
- `app/AGENTS.md`

参考文件：

- `docs/architecture/clients/mobile-information-architecture.md`
- `docs/delivery/tasks/task_v1_product_learning_iteration_contract.md`

---

## 6. 产出要求

至少应产出：

1. Android 端 iteration contract 接线
2. ProductLearningScreen 的最小可用迭代交互
3. 相关状态说明和 host-side build 验证
4. handoff 与 task 更新

---

## 7. 验收标准

满足以下条件可认为完成：

1. 学习页能够提交至少一轮补充输入
2. 学习页能展示 backend 返回的阶段与缺失字段
3. 当前 run 状态在学习页可见
4. `ready_for_confirmation` 后确认入口清晰
5. `./gradlew :app:assembleDebug` 通过
6. 如设备可用，至少一次 install/run smoke 通过

---

## 8. 推荐执行顺序

建议执行顺序：

1. 先对准 iteration contract
2. 接 DTO / parser / app state
3. 改 ProductLearningScreen 最小交互
4. 做 build / install / smoke
5. 更新 docs 与 handoff

---

## 9. 风险与注意事项

- 不要顺手把学习页重写成完整聊天产品
- 不要让端侧重复推断 backend 已提供的规则
- 设计上应优先服务“补齐关键信息并进入确认”，而不是追求聊天感

---

## 10. 下一步衔接

本任务完成后，推荐继续：

1. 视产品验证结果再拆 polish / follow-up

---

## 11. 实际产出

- Android backend adapter 新增 `ProductProfileEnrichRequestDto` / `ProductProfileEnrichResponseDto`。
- `V1BackendClient.enrichProductProfile()` 接入 `POST /product-profiles/{id}/enrich`，请求体固定为 `supplemental_notes` + `trigger_source`。
- `OpenClawApp` 新增补充材料输入状态、enrich job、提交补充并轮询 `product_learning` AgentRun 的流程。
- ProductLearning 页面新增：
  - 当前理解摘要
  - 仍需补充字段
  - 继续补充信息输入框与提交按钮
  - product_learning run 状态展示
  - `ready_for_confirmation` 后更明确的“查看并确认产品画像”入口
- 创建 ProductProfile 后保留在产品学习页，避免用户被自动跳走后无法继续补充。

---

## 12. 本次定稿边界

- Android 仍只是控制入口，未新增 public backend API，未修改 persisted object schema。
- 未引入聊天列表、streaming token、消息持久化、ViewModel/Hilt/Retrofit/Room/WorkManager。
- `missingFields`、`learningStage`、ProductProfile 写回仍完全由 backend 决定；Android 只展示与触发下一轮 enrich。
- `trigger_source` 固定为 `android_product_learning_iteration`。

---

## 13. 已做验证

已完成：

1. `./gradlew :app:assembleDebug`
   - 结果：成功。
   - 备注：仍有既有 AGP / compileSdk warning 与 `LocalLifecycleOwner` deprecated warning，不属于本任务新增失败。
2. `adb devices`
   - 结果：检测到设备 `f3b59f04`。
3. `adb install -r app/build/outputs/apk/debug/app-debug.apk`
   - 结果：成功。
4. `adb shell am start -n com.openclaw.android.nativeentry/.MainActivity`
   - 结果：成功。
5. `adb shell pidof com.openclaw.android.nativeentry`
   - 结果：应用进程存在。
6. `adb shell dumpsys window`
   - 结果：当前焦点为 `com.openclaw.android.nativeentry/.MainActivity`。
7. `adb logcat -d -t 200`
   - 结果：未发现 `FATAL EXCEPTION` / `AndroidRuntime` 崩溃。
8. `uiautomator dump`
   - 结果：确认应用首页可见。
9. 设备上点击“开始分析”进入 ProductLearning 页面，并通过 `uiautomator dump` 检查页面文本
   - 结果：确认“产品学习”“创建产品画像草稿”“当前理解”“仍需补充”“继续补充信息”“提交补充并重新学习”可见。

未完成：

- 未在真机上完成一次完整“创建 ProductProfile -> 提交补充 -> enrich run succeeded -> ProductProfile 刷新”的手动链路；设备 smoke 时 backend / `adb reverse tcp:8013 tcp:8013` 未保持联通，页面显示后端不可达提示。

---

## 14. 实际结果说明

本任务已完成 Android 端最小迭代 UI 与 contract 接线。当前代码已经能按既有 backend contract 发起 enrich、轮询 returned AgentRun，并在成功后重新读取 ProductProfile 和 `/history`。

剩余风险主要在真实设备联调环境：需要 backend 在 `127.0.0.1:8013` 运行，并执行 `adb reverse tcp:8013 tcp:8013` 后，再做一次完整 enrich 人工 smoke。
