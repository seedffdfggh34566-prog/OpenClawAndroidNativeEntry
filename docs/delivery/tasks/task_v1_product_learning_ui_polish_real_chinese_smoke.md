# Task：V1 ProductLearning UI Polish + Real Chinese Device Smoke

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V1 ProductLearning UI Polish + Real Chinese Device Smoke
- 建议路径：`docs/delivery/tasks/task_v1_product_learning_ui_polish_real_chinese_smoke.md`
- 当前状态：`done`
- 优先级：P1

本任务用于把 Android 产品学习页从工程流程页收口成 V1 用户入口，并用真实中文输入跑通 create / enrich smoke。

---

## 1.1 队列衔接

- 当前 task 是否允许执行 agent 自主推进：`yes`
- 建议上游入口：`docs/delivery/tasks/_active.md`
- 建议下游任务：
  1. runtime usage metadata follow-up
  2. 扩大真实业务样例库
- 停止条件：
  - 需要修改 backend contract / schema。
  - 需要新增导航架构或产品功能模块。
  - 真实 LLM / TokenHub 网络连续失败，无法判断 Android UI 行为。
  - 当前设备未预装测试 IME，且安装触发 OnePlus / OPlus 未知来源安全验证。

---

## 2. 任务目标

在不改变 backend API、DTO、parser、navigation 和产品主流程的前提下：

1. 产品学习页去除面向用户的工程词。
2. 输入区、当前理解区、缺失字段区和补充区改成销售助手用户能理解的文案。
3. 使用测试 IME + `ADB_INPUT_B64` 验证真实中文输入和 create / enrich 流程。

---

## 3. 当前背景

当前 V1 主闭环已经在真机跑通，Product Learning LLM 也通过了 8 个真实样例评估。当前剩余风险主要是用户首次进入产品学习页时是否能看懂该填什么、下一步做什么，以及真实中文输入是否能稳定支持 smoke。

---

## 4. 范围

本任务 In Scope：

- 调整 `ProductLearningScreen` 的展示文案和本地展示 helper。
- 新增真实中文设备 smoke 记录。
- 更新 task、handoff 和 `_active.md`。

本任务 Out of Scope：

- 不改 backend contract / schema。
- 不改 Android DTO / JSON parser。
- 不改导航架构。
- 不调 LLM prompt、provider 或 model。
- 不扩展 lead_analysis / report_generation。

---

## 5. 涉及文件

高概率涉及：

- `app/src/main/java/com/openclaw/android/nativeentry/ui/shell/V1ShellScreens.kt`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/tasks/task_v1_product_learning_ui_polish_real_chinese_smoke.md`
- `docs/delivery/handoffs/handoff_2026_04_25_product_learning_ui_polish_real_chinese_smoke.md`

参考文件：

- `docs/how-to/debug/android-chinese-input-smoke.md`

---

## 6. 产出要求

至少应产出：

1. ProductLearning 页面用户化文案收口。
2. Host build 验证记录。
3. 真实中文 create / enrich 设备 smoke 记录。
4. 任务结果和 handoff。

---

## 7. 验收标准

满足以下条件可认为完成：

1. 页面不再面向用户显示 `ProductProfile`、`product_learning`、`ready_for_confirmation`。
2. 中文输入样例能进入产品名称、一句话说明、初始材料和补充材料字段。
3. create run 成功并刷新出当前理解。
4. enrich run 成功并刷新产品画像。
5. ready 后 CTA 指向“查看并确认产品画像”。
6. `./gradlew :app:assembleDebug` 通过。
7. 真机 logcat 无 app crash 信号。

---

## 8. 推荐执行顺序

建议执行顺序：

1. 更新 task active。
2. 修改 ProductLearning 页面文案和展示 helper。
3. 运行 `git diff --check` 与 `./gradlew :app:assembleDebug`。
4. 启动真实 backend smoke DB。
5. 安装 App、配置 `adb reverse`。
6. 使用测试 IME 输入固定中文样例。
7. 验证 create / enrich 和关键文案。
8. 恢复默认输入法，并保留测试 IME 供后续 smoke 复用。
9. 更新 task、handoff 并提交原子 commit。

---

## 9. 风险与注意事项

- API key 只从 `backend/.env` 读取，不打印、不写入文档。
- 测试 IME 只作为 smoke 工具，结束后必须恢复默认输入法；当前设备保留 `com.android.adbkeyboard` 以避免重复触发厂商安全验证。
- 如果 TokenHub 超时，先记录为环境问题；只有 Android UI 自身问题才进入本任务修复。

---

## 10. 下一步衔接

本任务完成后，推荐继续：

1. runtime usage metadata follow-up。
2. 扩大真实业务样例库。

---

## 11. 实际产出

- 已完成 ProductLearning 页面文案和展示 helper 的最小收口：
  - 首页说明改为用户语言。
  - 创建区改为“先讲清楚你要卖什么”。
  - 输入字段说明补充客户、场景、痛点和优势。
  - 当前理解区改为“我们目前理解的是”。
  - 缺失字段区改为“还差哪些关键信息”。
  - 补充区按钮改为“提交补充并刷新产品画像”。
- 未修改 backend contract、Android DTO / parser、navigation、LLM prompt 或 provider。
- 真实中文 smoke 曾被当前设备未预装 `ADBKeyBoard` 阻塞；现已通过 `task_android_chinese_input_device_preflight.md` 完成设备预检，可恢复执行。
- 已完成真实中文 ProductLearning create / enrich 真机 smoke：
  - smoke DB：`/tmp/openclaw_product_learning_ui_polish_chinese_smoke.db`。
  - ProductProfile：`pp_653eb379`。
  - create run：`run_4f9580bf`，`succeeded`，输出 ProductProfile v2。
  - enrich run：`run_1acd919c`，`succeeded`，输出 ProductProfile v3。
  - 最终 ProductProfile：`draft`、`ready_for_confirmation`、`missing_fields=[]`、version 3。
- 真机 UI 已确认中文输入进入产品名称、一句话说明、初始材料和补充材料字段。
- 真机 UI 已确认关键文案可见：
  - `我们目前理解的是`
  - `还差哪些关键信息`
  - `目前没有必须补充的信息`
  - `查看并确认产品画像`
- smoke 结束后已恢复默认输入法：`com.baidu.input_oppo/.ImeService`。
- `com.android.adbkeyboard` 继续保留安装，供后续中文 smoke 复用。

---

## 12. 本次定稿边界

- 本次 UI polish 可独立保留。
- 中文 smoke 不应通过自动破解厂商拼图继续推进。
- 当前设备已完成 `task_android_chinese_input_device_preflight.md`，后续日常 smoke 只切换测试 IME，不卸载。
- 本次任务不进入 lead_analysis / report_generation，不扩大真实业务样例库，不调整 runtime usage metadata。

---

## 13. 已做验证

已完成：

1. `git diff --check`
   - 结果：通过，无输出。
2. `./gradlew :app:assembleDebug`
   - 结果：成功。
3. `adb devices`
   - 结果：检测到真机 `f3b59f04`。
4. `curl -sS http://127.0.0.1:8013/health`
   - 结果：`{"status":"ok"}`。
5. `adb install -r app/build/outputs/apk/debug/app-debug.apk`
   - 结果：成功。
6. UIAutomator dump
   - 结果：产品学习页可见 `先讲清楚你要卖什么`、`产品名称`、`一句话描述`、`客户、场景、痛点和优势`。
7. 设备中文输入工具检查
   - 当前默认输入法：`com.baidu.input_oppo/.ImeService`。
   - 重新安装测试 IME 曾触发 OPlus 安全验证和拼图，无法稳定自动化通过。
8. `task_android_chinese_input_device_preflight.md`
   - 结果：完成，`com.android.adbkeyboard` 已保留安装，`ADB_INPUT_B64` 中文输入已验证。
9. 真实中文 create smoke
   - 输入：`工厂设备巡检助手`、`面向制造业设备主管的移动巡检和故障记录工具`、`支持离线巡检、设备台账、异常拍照、维修派单；目标客户是中小制造工厂、设备主管和维修班组。`
   - 结果：`run_4f9580bf` 为 `succeeded`，`pp_653eb379` 刷新到 v2 且进入 `ready_for_confirmation`。
10. 真实中文 enrich smoke
    - 输入：`补充：重点服务离散制造、机械加工和设备密集型工厂；核心痛点是纸质巡检漏项、故障记录分散、维修响应慢；优势是低成本部署、移动端离线可用、现场照片和维修闭环。`
    - 结果：`run_1acd919c` 为 `succeeded`，`pp_653eb379` 刷新到 v3，`missing_fields=[]`。
11. 后端交叉确认
    - `GET /history`：`current_run=null`，latest ProductProfile 为 `pp_653eb379` v3。
    - `GET /product-profiles/pp_653eb379`：`status=draft`、`learning_stage=ready_for_confirmation`。
12. 真机运行检查
    - `adb logcat -d -t 300 | rg -i "FATAL EXCEPTION|AndroidRuntime: FATAL|Process: com.openclaw.android.nativeentry"`：无匹配。
    - `adb shell settings get secure default_input_method`：`com.baidu.input_oppo/.ImeService`。
    - `adb shell pm list packages com.android.adbkeyboard`：测试 IME 仍安装。

---

## 14. 实际结果说明

当前任务已完成。ProductLearning UI polish 已保留，真实中文 create / enrich 真机 smoke 已跑通；中文输入工具采用“设备预装保留、日常只切换 IME”的策略。
