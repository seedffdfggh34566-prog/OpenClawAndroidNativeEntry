# Handoff: V1 Demo Runbook And Evidence Pack

日期：2026-04-25

## 1. 完成内容

- 新增 V1 demo runbook：`docs/how-to/debug/v1-demo-runbook.md`
- 新增本次真机证据包：`docs/product/research/v1_demo_evidence_pack_2026_04_25.md`
- 使用真实 backend、真实 TokenHub、真机 Android 跑通中文 demo：
  - ProductProfile create / ProductLearning
  - ProductProfile confirm
  - LeadAnalysis LLM
  - ReportGeneration
  - 首页最终状态与报告页确认
- 复用 `8013` inspector backend，trace dir 为 `/tmp/openclaw_llm_traces_demo_evidence_pack`。
- demo 后恢复原输入法 `com.baidu.input_oppo/.ImeService`。

## 2. 关键证据

- ProductProfile：`pp_b8b393e5`
- ProductLearning run：`run_20c92ad5`，`succeeded`，`total_tokens=1074`
- LeadAnalysis run：`run_5f07b0f9`，`succeeded`，`total_tokens=1806`
- ReportGeneration run：`run_34e62bea`，`succeeded`
- LeadAnalysisResult：`lar_7f82b3f8`
- AnalysisReport：`rep_bd382d9f`
- LLM inspector trace：ProductLearning / LeadAnalysis 两条 trace 均 `parse_status=succeeded`
- UIAutomator 确认首页最终文案：`销售分析报告已生成。`
- UIAutomator 确认报告页文案：`执行摘要`、`重点建议`、`状态：可复看`
- logcat crash scan：无 `FATAL EXCEPTION` / `AndroidRuntime: FATAL`

## 3. 验证

- `./gradlew :app:assembleDebug`：通过
- `curl -sS http://127.0.0.1:8013/health`：通过
- `adb devices`：检测到 `f3b59f04`
- `adb reverse tcp:8013 tcp:8013`：通过
- `adb install -r app/build/outputs/apk/debug/app-debug.apk`：通过
- `adb logcat -d -t 300 | rg -i "FATAL EXCEPTION|AndroidRuntime: FATAL|Process: com.openclaw.android.nativeentry"`：无匹配
- `git diff --check`：通过

## 4. 已知限制

- 本次 demo 依赖真实 TokenHub；网络波动仍可能影响 ProductLearning / LeadAnalysis 等待时间。
- LeadAnalysis LLM 本次耗时约 22.6 秒，demo 时应预留等待窗口。
- ReportGeneration 仍为 heuristic，不代表最终 LLM 报告能力。
- Inspector trace 仅为本地开发工具，不应在生产默认开启。

## 5. 推荐下一步

当前正式 task 队列已收口为空。下一步应回到规划层决定是否进入：

- V1 demo 对外演示准备；
- latency / fallback 的正式实现；
- report_generation LLM phase1；
- 或继续扩大真实业务样例库。
