# Task：V1 Android Product Learning Iteration UI

更新时间：2026-04-24

## 1. 任务定位

- 任务名称：V1 Android Product Learning Iteration UI
- 建议路径：`docs/delivery/tasks/task_v1_android_product_learning_iteration_ui.md`
- 当前状态：`planned`
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

任务执行完成后补充。

---

## 12. 本次定稿边界

任务执行完成后补充。

---

## 13. 已做验证

任务执行完成后补充。

---

## 14. 实际结果说明

任务执行完成后补充。
