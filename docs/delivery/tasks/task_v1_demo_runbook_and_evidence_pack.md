# Task：V1 Demo Runbook And Evidence Pack

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V1 Demo Runbook And Evidence Pack
- 建议路径：`docs/delivery/tasks/task_v1_demo_runbook_and_evidence_pack.md`
- 当前状态：`planned`
- 优先级：P0

本任务用于在 V1 RC hardening、report polish、developer LLM inspector 和 16 样例 round2 eval 完成后，固化可重复 demo 流程，并收集一次真机中文 demo 证据包。

---

## 2. 范围

In Scope：

- 编写正式 demo runbook。
- 使用真实 backend、真实 TokenHub、真机 Android 跑一次中文 demo。
- 记录对象 ID、run ID、token usage、关键 UI 文案证据和 logcat 崩溃扫描结果。
- 默认复用人工正在查看的 `8013` inspector backend；不得静默切到其他端口。
- 如 demo 被 timeout 阻断，只记录证据并决定是否重新打开 latency / fallback follow-up。

Out of Scope：

- 不新增功能。
- 不改 public API / schema。
- 不改 Android 导航或 DTO。
- 不切模型 / provider。
- 不实现 fallback，除非后续任务明确触发。

---

## 3. 建议验证路径

```text
创建产品画像 -> 确认产品画像 -> LeadAnalysis LLM -> ReportGeneration -> 首页最终状态 -> 报告页
```

固定中文 demo 样例优先继续使用：

- 产品名：`工厂设备巡检助手`
- 一句话说明：`面向制造业设备主管的移动巡检和故障记录工具`
- 初始材料：`支持离线巡检、设备台账、异常拍照、维修派单；目标客户是中小制造工厂、设备主管和维修班组。`

---

## 4. 验收标准

- demo runbook 可被开发者按步骤复现。
- 真机 demo 至少跑通一次完整路径。
- Evidence pack 包含：
  - ProductProfile id
  - ProductLearning run id
  - LeadAnalysis run id
  - ReportGeneration run id
  - token usage
  - 关键 UIAutomator 文案
  - logcat 崩溃扫描结果
- 若未能跑通，必须明确记录 blocked 原因。
