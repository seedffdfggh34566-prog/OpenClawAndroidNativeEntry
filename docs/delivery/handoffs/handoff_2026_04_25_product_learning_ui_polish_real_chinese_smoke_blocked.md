# 阶段性交接：ProductLearning UI Polish + Real Chinese Smoke Blocked

更新时间：2026-04-25

## 1. 本次改了什么

- 收口 Android 产品学习页文案和展示 helper，让页面更接近 V1 用户入口。
- 新增任务文档：`docs/delivery/tasks/task_v1_product_learning_ui_polish_real_chinese_smoke.md`。
- 新增设备预检任务：`docs/delivery/tasks/task_android_chinese_input_device_preflight.md`。
- 更新中文输入 runbook：`docs/how-to/debug/android-chinese-input-smoke.md`。
- 更新 `_active.md`，将当前优先任务切到中文输入设备预检。

---

## 2. 为什么这么定

- ProductLearning UI polish 已完成 host build，可以独立保留。
- 真实中文 smoke 被 OnePlus / OPlus 未知来源输入法安装安全页和拼图验证阻塞。
- 该阻塞属于设备安全策略，不是 OpenClaw Android UI 或 backend 逻辑问题。
- 不应自动破解厂商拼图；正确做法是一次性设备预检安装并保留测试 IME，后续 smoke 只切换输入法。

---

## 3. 本次验证了什么

1. `git diff --check`
   - 结果：通过。
2. `./gradlew :app:assembleDebug`
   - 结果：成功。
3. `adb devices`
   - 检测到真机 `f3b59f04`。
4. backend smoke
   - `curl -sS http://127.0.0.1:8013/health` 返回 `{"status":"ok"}`。
5. Android install / launch
   - `adb install -r app/build/outputs/apk/debug/app-debug.apk` 返回 `Success`。
   - App 可打开产品学习页。
6. UI 文案
   - UIAutomator dump 可见 `先讲清楚你要卖什么`、`产品名称`、`一句话描述`、`客户、场景、痛点和优势`。
7. 中文输入工具状态
   - 当前默认输入法：`com.baidu.input_oppo/.ImeService`。
   - `com.android.adbkeyboard` 当前未安装。
   - 重新安装 `ADBKeyBoard` 触发 OPlus 安全验证和拼图，无法稳定自动化继续。

---

## 4. 已知限制

- 真实中文 create / enrich smoke 尚未完成。
- 当前设备需要先完成 `task_android_chinese_input_device_preflight.md`。
- 日常 smoke 不应再卸载测试 IME，否则会重新触发厂商未知来源安装验证。

---

## 5. 推荐下一步

1. 人工一次性完成当前设备上的 `ADBKeyBoard` 安装确认和拼图验证。
2. 执行 `task_android_chinese_input_device_preflight.md` 验证测试 IME 已安装、可切换、可通过 `ADB_INPUT_B64` 输入中文。
3. 恢复 `task_v1_product_learning_ui_polish_real_chinese_smoke.md` 的真实中文 create / enrich smoke。
