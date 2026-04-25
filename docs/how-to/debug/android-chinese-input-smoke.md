# Android 中文输入 Smoke Runbook

更新时间：2026-04-25

## 1. 适用场景

本文档用于处理真机 smoke 中需要向 Android 输入框注入中文文本的场景。

当前结论：

> 不要把 `adb shell input text "中文"` 作为可靠中文输入方案。

该命令对中文、空格、长文本和不同系统输入法的支持不稳定，容易把测试输入问题误判为 App 业务问题。

---

## 2. 当前设备事实

当前已检查设备：

- 设备 ID：`f3b59f04`
- 默认输入法：`com.baidu.input_oppo/.ImeService`
- 当前可列出的 IME：`com.baidu.input_oppo/.ImeService`

检查命令：

```bash
adb devices
adb shell settings get secure default_input_method
adb shell ime list -s
```

---

## 3. 短期策略：继续使用 ASCII Smoke 输入

用于验证主链路时，继续使用无空格 ASCII 等价样例。

适用任务：

- backend / Android 主流程 smoke
- create / enrich / confirm / analysis / report_generation 链路验证
- UI 文案与状态跳转验证

优点：

- 不改设备输入法
- 不依赖第三方 APK
- 对 `adb shell input text` 最稳定

限制：

- 不能验证真实中文输入体验
- 长文本仍可能因焦点问题落入错误输入框，执行时需用 UIAutomator dump 交叉确认

---

## 4. 推荐方案：测试专用 IME

需要覆盖中文输入时，使用测试专用输入法。

基本流程：

```bash
# 1. 记录原默认输入法
ORIGINAL_IME="$(adb shell settings get secure default_input_method | tr -d '\r')"
echo "$ORIGINAL_IME"

# 2. 安装可信的测试输入法 APK
adb install -r /path/to/test-ime.apk

# 3. 查看测试输入法 id
adb shell ime list -s

# 4. 启用并切换到测试输入法
adb shell ime enable <test_ime_id>
adb shell ime set <test_ime_id>

# 5. 向当前焦点输入框发送中文
adb shell am broadcast -a ADB_INPUT_TEXT --es msg "工厂设备巡检助手"

# 6. smoke 结束后恢复原输入法
adb shell ime set "$ORIGINAL_IME"
```

说明：

- `<test_ime_id>` 必须以设备实际 `adb shell ime list -s` 输出为准。
- `ADB_INPUT_TEXT` 是常见测试输入法使用的 broadcast action，具体 action 以所选测试 IME 文档为准。
- 不要把第三方测试 APK 提交到仓库。
- smoke handoff 必须记录测试 IME 名称、版本来源、切换前后默认输入法。

---

## 5. 不推荐方案

不要优先采用以下方案：

- 在产品代码中加入隐藏中文预填入口
- 在 debug build 中暴露业务测试 endpoint
- 依赖 `adb shell input text` 直接输入中文
- 在未记录恢复步骤的情况下切换系统默认输入法

这些方案要么污染产品行为，要么会让设备状态不可控。

---

## 6. 故障判断

如果中文输入失败，按以下顺序判断：

1. `adb devices` 是否仍检测到设备
2. 当前焦点是否在目标输入框
3. 当前默认输入法是否为测试 IME
4. broadcast action 是否与测试 IME 文档一致
5. UIAutomator dump 是否显示文本进入目标字段
6. 是否已恢复原默认输入法

只要后端 API、AgentRun 和 UI 状态正常，不应把中文注入失败归因于业务链路失败。
