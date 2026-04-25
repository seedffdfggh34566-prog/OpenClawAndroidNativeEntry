# 阶段性交接：Android Chinese Input Test IME Device Smoke

更新时间：2026-04-25

## 1. 本次改了什么

- 新增任务文档：`docs/delivery/tasks/task_android_chinese_input_test_ime_device_smoke.md`
- 更新中文输入 runbook：`docs/how-to/debug/android-chinese-input-smoke.md`
- 更新 `_active.md`，记录本任务已完成。
- 未修改 Android 产品代码，未修改 backend。

---

## 2. 为什么这么定

- 当前设备 OnePlus PHK110 / Android 16 不能依赖 `adb shell input text "中文"`。
- 测试 IME 是 smoke 工具，不应进入产品功能或产品依赖。
- GitHub `senzhk/ADBKeyBoard` v2.5-dev 标注包含 Android 16 修复，因此本次优先验证该版本。

---

## 3. 本次验证了什么

1. `adb devices`
   - 检测到真机 `f3b59f04`。
2. 当前系统事实
   - Android：16 / API 36。
   - 原默认输入法：`com.baidu.input_oppo/.ImeService`。
3. APK 来源与校验
   - URL：`https://github.com/senzhk/ADBKeyBoard/releases/download/v2.5-dev/keyboardservice-debug.apk`
   - SHA-256：`41a8a0996d7397a2390d1ca16a75cb66c4a7bdaa89cf4e63600a4d3fb346fbbb`
4. 测试 IME 安装与切换
   - `adb shell pm install -r /data/local/tmp/openclaw-adbkeyboard.apk` 返回 `Success`。
   - 默认输入法切换到 `com.android.adbkeyboard/.AdbIME`。
5. 中文输入
   - 对 OpenClaw Android 产品学习页产品名称输入框执行 `ADB_INPUT_B64`。
   - UIAutomator XML 中确认出现 `text="工厂设备巡检助手"`。
6. 恢复与清理
   - 默认输入法恢复为 `com.baidu.input_oppo/.ImeService`。
   - `adb uninstall com.android.adbkeyboard` 返回 `Success`。
   - `/data/local/tmp/openclaw-adbkeyboard.apk` 已删除。

---

## 4. 已知限制

- 本次只验证 smoke 输入通道，不代表用户日常输入法体验。
- 当前设备上 `adb install -r` 曾长时间无返回；已验证 `adb push` + `adb shell pm install -r` 可用。
- 测试 IME APK 不提交到仓库，后续执行需按 runbook 重新下载并校验。

---

## 5. 推荐下一步

1. 后续真机 smoke 如需要中文样例，按 `docs/how-to/debug/android-chinese-input-smoke.md` 使用 `ADB_INPUT_B64`。
2. 当前 V1 主链路已完成，下一步仍建议回到规划层选择 ProductLearning UI polish、扩大真实业务样例库或 runtime usage metadata follow-up。
