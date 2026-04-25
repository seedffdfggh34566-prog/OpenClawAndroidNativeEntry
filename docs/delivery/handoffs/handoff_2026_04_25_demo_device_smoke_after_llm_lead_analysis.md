# Handoff：V1 Demo Device Smoke After LLM Lead Analysis

日期：2026-04-25

## 变更内容

- 新增并完成 `task_v1_demo_device_smoke_after_llm_lead_analysis.md`。
- 用真实 backend、真实 TokenHub、真机 Android 和真实中文输入跑通 V1 demo 路径。
- 修复 lead_analysis LLM 输出解析的稳定性问题：解析器现在扫描并解析第一个合法 JSON object，避免模型前缀 / 非 JSON 花括号导致 run 失败。

## 触达文件

- `backend/runtime/graphs/lead_analysis.py`
- `backend/tests/test_tokenhub_client.py`
- `docs/delivery/tasks/task_v1_demo_device_smoke_after_llm_lead_analysis.md`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/README.md`

## 验证

- `backend/.venv/bin/python -m pytest backend/tests`
  - 40 passed。
- `git diff --check`
  - 通过。
- `./gradlew :app:assembleDebug`
  - 成功；仍有既有 AGP / compileSdk warning。
- 真机 `f3b59f04`：
  - `adb reverse tcp:8013 tcp:8013` 成功。
  - APK install / launch 成功。
  - 中文输入通过 `ADB_INPUT_B64` 完成。
  - ProductLearning / ProductProfile confirm / LeadAnalysis LLM / ReportGeneration 完整跑通。
- `adb logcat -d -t 300 | rg -i "FATAL EXCEPTION|AndroidRuntime: FATAL|Process: com.openclaw.android.nativeentry"`
  - 无匹配。

## 结果对象

- ProductProfile：`pp_7f04d2f7`，`confirmed`，v3。
- LeadAnalysisResult：`lar_9a81c480`，`published`。
- AnalysisReport：`rep_7ef24e42`，`published`。
- 成功 AgentRun：
  - `run_c2759b51`：product_learning，succeeded。
  - `run_cb68783e`：lead_analysis，succeeded，`llm_usage.total_tokens=1864`。
  - `run_55159132`：report_generation，succeeded。
- 保留失败证据：
  - `run_cddc84b5`：lead_analysis，failed，`lead_analysis_llm_json_decode_failed`。

## 已知限制

- 本次 smoke 中曾出现一次 lead_analysis JSON decode 失败；已做最小解析修复并通过同一路径复验。
- 本次没有触发 timeout，因此没有实现 latency / fallback。
- `report_generation` 仍是 heuristic，不是 LLM。
- 设备仍依赖已预装 `com.android.adbkeyboard` 才能稳定执行中文 smoke。

## 建议下一步

创建 / 收口 `task_v1_llm_latency_and_fallback_followup.md` 为 conditional not triggered：本次 demo 没有 timeout 阻断，不应提前实现 fallback。
