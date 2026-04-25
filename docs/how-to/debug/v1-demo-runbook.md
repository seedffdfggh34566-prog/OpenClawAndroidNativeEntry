# V1 Demo Runbook

更新时间：2026-04-25

## 1. 目的

本 runbook 用于在 `jianglab` 上复现 OpenClaw AI 销售助手 V1 demo 路径：

```text
创建产品画像 -> 确认产品画像 -> 生成获客分析 -> 生成分析报告 -> 首页 / 报告页状态确认
```

本流程使用真实 backend、真实 Tencent TokenHub、真机 Android 和开发者 LLM Run Inspector。

## 2. 前提

- backend API key 已存在于 `backend/.env` 或环境变量中。
- 不打印、不复制、不提交 API key。
- 真机已通过 `adb devices` 可见。
- 真机已保留测试 IME：`com.android.adbkeyboard/.AdbIME`。
- Win10 如需查看 inspector，可先建立隧道：

```bash
ssh -N -L 8013:127.0.0.1:8013 yulin@jianglab
```

然后打开：

```text
http://127.0.0.1:8013/dev/llm-inspector
```

## 3. 固定 demo 输入

- 产品名：`工厂设备巡检助手`
- 一句话说明：`面向制造业设备主管的移动巡检和故障记录工具`
- 初始材料：`支持离线巡检、设备台账、异常拍照、维修派单；目标客户是中小制造工厂、设备主管和维修班组。`

## 4. 启动 backend

默认复用人正在查看的 `8013` inspector backend。不要静默切到 `8014` 或其他端口。

```bash
rm -f /tmp/openclaw_v1_demo_runbook_evidence_pack_2026_04_25.db
rm -rf /tmp/openclaw_llm_traces_demo_evidence_pack
mkdir -p /tmp/openclaw_llm_traces_demo_evidence_pack

set -a
. backend/.env
set +a

OPENCLAW_BACKEND_DATABASE_PATH=/tmp/openclaw_v1_demo_runbook_evidence_pack_2026_04_25.db \
OPENCLAW_BACKEND_DEV_LLM_TRACE_ENABLED=true \
OPENCLAW_BACKEND_DEV_LLM_TRACE_DIR=/tmp/openclaw_llm_traces_demo_evidence_pack \
backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013
```

验证：

```bash
curl -sS http://127.0.0.1:8013/health
curl -sS http://127.0.0.1:8013/dev/llm-runs
```

## 5. 启动 Android

```bash
./gradlew :app:assembleDebug
adb reverse tcp:8013 tcp:8013
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.openclaw.android.nativeentry/.MainActivity
```

## 6. 中文输入

保存原输入法：

```bash
adb shell settings get secure default_input_method
```

切换测试 IME：

```bash
adb shell ime set com.android.adbkeyboard/.AdbIME
```

输入中文示例：

```bash
MSG_B64="$(printf '%s' '工厂设备巡检助手' | base64 -w 0)"
adb shell am broadcast -a ADB_INPUT_B64 --es msg "$MSG_B64"
```

结束后恢复原输入法，例如：

```bash
adb shell ime set com.baidu.input_oppo/.ImeService
```

更完整的中文输入说明见 `docs/how-to/debug/android-chinese-input-smoke.md`。

## 7. Demo 操作路径

1. 首页点击“开始分析”。
2. 在产品学习页填写三个字段并点击“创建并学习产品”。
3. 等待 ProductLearning run succeeded。
4. 点击“查看并确认产品画像”。
5. 在产品画像页点击“确认产品画像”。
6. 点击“生成获客分析”。
7. 等待 LeadAnalysis run succeeded，并打开分析结果页。
8. 点击“生成可复看的分析报告”。
9. 打开报告页，确认“执行摘要”“重点建议”“状态：可复看”可见。
10. 回到首页，确认“销售分析报告已生成。”可见。

## 8. 证据收集

建议记录：

- `GET /history`
- ProductLearning run：`GET /analysis-runs/{run_id}`
- LeadAnalysis run：`GET /analysis-runs/{run_id}`
- ReportGeneration run：`GET /analysis-runs/{run_id}`
- LLM trace list：`GET /dev/llm-runs`
- LLM trace detail：`GET /dev/llm-runs/{run_id}`
- UI evidence：

```bash
adb shell uiautomator dump /sdcard/window.xml >/dev/null
adb exec-out cat /sdcard/window.xml
```

- crash scan：

```bash
adb logcat -d -t 300 | rg -i "FATAL EXCEPTION|AndroidRuntime: FATAL|Process: com.openclaw.android.nativeentry"
```

## 9. Timeout 处理

如果 ProductLearning 或 LeadAnalysis timeout 阻断 demo：

- 记录 run id、`error_type`、耗时和是否重试成功。
- 不在本 runbook 内切换供应商或实现 fallback。
- 重新打开 latency / fallback follow-up task，由后续任务处理。
