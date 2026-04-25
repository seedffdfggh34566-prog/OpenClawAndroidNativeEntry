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
- 设备型号：OnePlus PHK110
- Android：16 / API 36
- 默认输入法：`com.baidu.input_oppo/.ImeService`
- 当前可列出的 IME：`com.baidu.input_oppo/.ImeService`

检查命令：

```bash
adb devices
adb shell settings get secure default_input_method
adb shell ime list -s
```

---

## 2.1 当前已验证方案与现状

已在当前设备验证可用：

- 测试 IME：`senzhk/ADBKeyBoard`
- APK 版本：GitHub `v2.5-dev`
- APK URL：`https://github.com/senzhk/ADBKeyBoard/releases/download/v2.5-dev/keyboardservice-debug.apk`
- 本地临时路径：`/tmp/openclaw-adbkeyboard/keyboardservice-debug.apk`
- SHA-256：`41a8a0996d7397a2390d1ca16a75cb66c4a7bdaa89cf4e63600a4d3fb346fbbb`
- 测试 IME id：`com.android.adbkeyboard/.AdbIME`
- 已验证输入文本：`工厂设备巡检助手`
- 验证方式：`ADB_INPUT_B64` + UIAutomator dump

当前现状：

- 默认输入法已恢复为 `com.baidu.input_oppo/.ImeService`
- `com.android.adbkeyboard` 当前未安装
- 2026-04-25 后续 smoke 再次安装时触发 OnePlus / OPlus 未知来源安全页与拼图验证，无法稳定自动化通过

因此当前推荐策略已调整为：

> 将 `ADBKeyBoard` 作为 jianglab 当前测试设备的一次性预装测试工具。设备准备阶段可人工完成厂商安全验证；日常 smoke 只切换 IME，不再重复安装或卸载测试输入法。

---

## 3. 短期策略：继续使用 ASCII Smoke 输入

用于快速验证主链路时，可以继续使用无空格 ASCII 等价样例。

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

如果本次 smoke 目标包含“真实中文输入覆盖”，优先使用第 4 节的测试 IME 方案。

---

## 4. 推荐方案：测试专用 IME

需要覆盖中文输入时，使用测试专用输入法。

当前流程分为两类：

1. 设备准备阶段：只在设备未安装测试 IME 时执行，允许人工完成厂商安全验证。
2. 日常 smoke 阶段：不安装、不卸载 APK，只切换 IME 并输入中文。

### 4.1 设备准备阶段

当前设备若未安装 `com.android.adbkeyboard`，先执行一次设备准备：

```bash
# 1. 下载可信的测试输入法 APK 到 /tmp，不提交到 Git
mkdir -p /tmp/openclaw-adbkeyboard
curl -L --fail --show-error \
  -o /tmp/openclaw-adbkeyboard/keyboardservice-debug.apk \
  https://github.com/senzhk/ADBKeyBoard/releases/download/v2.5-dev/keyboardservice-debug.apk
sha256sum /tmp/openclaw-adbkeyboard/keyboardservice-debug.apk

# 2. 推送到设备
adb push /tmp/openclaw-adbkeyboard/keyboardservice-debug.apk /data/local/tmp/openclaw-adbkeyboard.apk

# 3. 安装测试输入法
# 当前 OnePlus Android 16 设备可能弹出 OPlus 未知来源安全页和拼图验证。
# 该验证不应自动破解；如出现，请在真机上人工确认一次。
adb shell pm install -r /data/local/tmp/openclaw-adbkeyboard.apk

# 4. 查看测试输入法 id
adb shell ime list -s
```

准备完成标准：

```bash
adb shell pm list packages com.android.adbkeyboard
adb shell ime list -s
```

输出应包含：

```text
package:com.android.adbkeyboard
com.android.adbkeyboard/.AdbIME
```

说明：

- 测试 IME APK 不提交到 Git。
- 允许 `com.android.adbkeyboard` 保留安装在 jianglab 当前测试设备上。
- 只有设备重置、APK 被卸载或测试 IME 损坏时，才重新执行设备准备阶段。
- 不要把 OPlus 拼图验证写成自动化步骤；它属于厂商安全校验。

### 4.2 日常 smoke 阶段

设备已经预装 `ADBKeyBoard` 后，日常 smoke 使用以下流程：

```bash
# 1. 记录原默认输入法
ORIGINAL_IME="$(adb shell settings get secure default_input_method | tr -d '\r')"
echo "$ORIGINAL_IME"

# 2. 切换到测试输入法
adb shell ime enable com.android.adbkeyboard/.AdbIME
adb shell ime set com.android.adbkeyboard/.AdbIME
adb shell settings get secure default_input_method

# 3. 向当前焦点输入框发送中文
MSG_B64="$(printf '%s' '工厂设备巡检助手' | base64 -w 0)"
adb shell am broadcast -a ADB_INPUT_B64 --es msg "$MSG_B64"

# 4. 用 UIAutomator dump 确认文本进入目标输入框
adb shell uiautomator dump /sdcard/window.xml >/dev/null
adb exec-out cat /sdcard/window.xml | rg "工厂设备巡检助手"

# 5. smoke 结束后恢复原输入法
adb shell ime set "$ORIGINAL_IME"
adb shell settings get secure default_input_method
```

说明：

- `<test_ime_id>` 必须以设备实际 `adb shell ime list -s` 输出为准。
- 当前设备优先使用 `ADB_INPUT_B64`，避免 UTF-8 参数在 `adb shell am broadcast` 中被系统或 shell 错误处理。
- 不要在日常 smoke 中卸载 `com.android.adbkeyboard`。
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
7. 若设备未安装测试 IME，是否被 OPlus 未知来源安全页或拼图验证阻塞

只要后端 API、AgentRun 和 UI 状态正常，不应把中文注入失败归因于业务链路失败。
