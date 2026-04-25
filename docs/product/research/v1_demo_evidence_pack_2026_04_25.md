# V1 Demo Evidence Pack

更新时间：2026-04-25

## 1. 环境

- backend：`127.0.0.1:8013`
- database：`/tmp/openclaw_v1_demo_runbook_evidence_pack_2026_04_25.db`
- trace dir：`/tmp/openclaw_llm_traces_demo_evidence_pack`
- inspector：`http://127.0.0.1:8013/dev/llm-inspector`
- Android package：`com.openclaw.android.nativeentry`
- device：`adb devices` 检测到 `f3b59f04`
- model：Tencent TokenHub `minimax-m2.5`

API key 只从 `backend/.env` 读取，未写入本记录。

## 2. Demo 输入

- 产品名：`工厂设备巡检助手`
- 一句话说明：`面向制造业设备主管的移动巡检和故障记录工具`
- 初始材料：`支持离线巡检、设备台账、异常拍照、维修派单；目标客户是中小制造工厂、设备主管和维修班组。`

## 3. 后端对象

| 对象 | ID | 状态 |
|---|---|---|
| ProductProfile | `pp_b8b393e5` | `confirmed` |
| LeadAnalysisResult | `lar_7f82b3f8` | `published` |
| AnalysisReport | `rep_bd382d9f` | `published` |

`GET /history` 最终返回：

- latest product profile：`pp_b8b393e5`
- latest analysis result：`lar_7f82b3f8`
- latest report：`rep_bd382d9f`
- current run：`null`

## 4. Run 证据

| 阶段 | run id | 状态 | 触发来源 | 输出对象 | token usage |
|---|---|---|---|---|---|
| ProductLearning | `run_20c92ad5` | `succeeded` | `android_product_learning` | `pp_b8b393e5` v2 | `1074` |
| LeadAnalysis | `run_5f07b0f9` | `succeeded` | `android_product_profile` | `lar_7f82b3f8` v1 | `1806` |
| ReportGeneration | `run_34e62bea` | `succeeded` | `android_analysis_result` | `rep_bd382d9f` v1 | N/A, heuristic |

LLM trace summary：

| run id | run type | prompt version | duration | parse status | total tokens |
|---|---|---|---:|---|---:|
| `run_20c92ad5` | `product_learning` | `product_learning_llm_v1` | 5899 ms | `succeeded` | 1074 |
| `run_5f07b0f9` | `lead_analysis` | `lead_analysis_llm_v1` | 22555 ms | `succeeded` | 1806 |

## 5. UI 证据

中文输入验证：

- `工厂设备巡检助手`
- `面向制造业设备主管的移动巡检和故障记录工具`
- `支持离线巡检、设备台账、异常拍照、维修派单；目标客户是中小制造工厂、设备主管和维修班组。`

产品学习 / 画像确认页可见：

- `我们目前理解的是`
- `适合卖给谁`
- `当前画像已达到可确认状态。确认后即可生成获客分析。`
- `确认产品画像`

分析结果页可见：

- `优先尝试方向`
- `优先行业`
- `场景机会`
- `生成可复看的分析报告`

报告页可见：

- `工厂设备巡检助手 获客分析报告`
- `执行摘要`
- `重点建议`
- `状态：可复看 · v1 · 2026-04-25T12:26:36.015505`

首页最终状态可见：

- `销售分析报告已生成。`
- `当前产品：工厂设备巡检助手`
- `产品理解：工厂设备巡检助手（已确认）`

## 6. 验证命令

- `./gradlew :app:assembleDebug`：通过
- `curl -sS http://127.0.0.1:8013/health`：返回 `{"status":"ok"}`
- `curl -sS http://127.0.0.1:8013/dev/llm-runs`：返回 ProductLearning / LeadAnalysis 两条 trace
- `adb reverse tcp:8013 tcp:8013`：通过
- `adb install -r app/build/outputs/apk/debug/app-debug.apk`：通过
- `adb logcat -d -t 300 | rg -i "FATAL EXCEPTION|AndroidRuntime: FATAL|Process: com.openclaw.android.nativeentry"`：无匹配

## 7. 结论

本次真机中文 demo 完整通过：

```text
创建产品画像 -> 确认产品画像 -> LeadAnalysis LLM -> ReportGeneration -> 首页最终状态 -> 报告页
```

未出现 TokenHub timeout 阻断。`task_v1_llm_latency_and_fallback_followup.md` 仍保持 conditional，不触发 fallback 实现。

## 8. 已知限制

- ProductLearning 和 LeadAnalysis 仍依赖外部 LLM，demo 网络质量会影响耗时。
- LeadAnalysis 本次耗时约 22.6 秒，仍需在正式 demo 时预留等待窗口。
- ReportGeneration 当前仍为 heuristic，不消耗 LLM token。
- Inspector trace 包含 raw model output，只应在本地开发显式开启 trace 时使用。
