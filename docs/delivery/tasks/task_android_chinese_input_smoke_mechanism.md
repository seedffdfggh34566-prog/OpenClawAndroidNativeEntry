# Task：Android Chinese Input Smoke Mechanism

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：Android Chinese Input Smoke Mechanism
- 建议路径：`docs/delivery/tasks/task_android_chinese_input_smoke_mechanism.md`
- 当前状态：`done`
- 优先级：P2

本任务用于收口真机 smoke 中 `adb shell input text` 中文输入不可靠的问题。

本任务不修改产品功能代码，只把当前设备事实、推荐解决方案和后续执行步骤沉淀为 runbook，避免后续 smoke 继续把中文输入问题误判为 Android 或 backend 业务 bug。

---

## 2. 背景

在完整 V1 真机 smoke 中，当前设备对 `adb shell input text` 的中文输入不稳定：

- 直接输入中文可能触发系统侧异常
- 空格或转义字符可能被错误处理
- 长文本字段可能落入错误输入框或追加到上一字段

这属于真机自动化输入通道问题，不是 V1 backend / Android 业务 contract 问题。

---

## 3. 任务目标

明确当前阶段的处理策略：

1. 短期 smoke 继续使用无空格 ASCII 等价样例
2. 正式中文自动化输入使用测试专用 IME
3. 记录默认输入法与恢复步骤
4. 不在产品代码中加入测试输入入口

---

## 4. 实际产出

- 新增 runbook：`docs/how-to/debug/android-chinese-input-smoke.md`
- 记录当前设备输入法事实：
  - 设备：`f3b59f04`
  - 默认输入法：`com.baidu.input_oppo/.ImeService`
  - 当前可列出的 IME：`com.baidu.input_oppo/.ImeService`
- 明确推荐路径：
  - 继续用 ASCII 做主链路 smoke
  - 需要中文输入覆盖时，安装并启用测试专用 IME
  - 测试结束后恢复原输入法
- 明确不做：
  - 不修改 Android 产品代码
  - 不新增 debug-only 输入入口
  - 不把第三方测试 APK 纳入仓库

---

## 5. 已做验证

已完成：

1. `adb devices`
   - 结果：检测到真机 `f3b59f04`。
2. `adb shell settings get secure default_input_method`
   - 结果：`com.baidu.input_oppo/.ImeService`。
3. `adb shell ime list -s`
   - 结果：仅列出 `com.baidu.input_oppo/.ImeService`。
4. `git diff --check`
   - 结果：通过。

---

## 6. 后续建议

如果后续需要自动化中文 smoke，应单独执行 runbook 中的“测试 IME 方案”：

1. 准备可信的测试输入法 APK
2. 在 smoke 开始前记录原默认输入法
3. 启用测试 IME 并通过 broadcast 输入中文
4. smoke 结束后恢复原默认输入法
5. 将中文输入证据写入对应 handoff
