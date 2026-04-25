# V1 Demo Release Candidate Hardening：2026-04-25

## 1. 结论

V1 当前状态：**已具备稳定 demo 的 release candidate hardening 条件，但尚不是生产可用版本。**

当前主闭环已经通过真实中文真机 demo：

```text
产品学习 -> 产品画像确认 -> LeadAnalysis LLM -> 分析报告 -> 首页最终状态
```

下一阶段目标不是扩功能，而是把现有闭环收口为可重复演示、可记录证据、可继续评估质量的 RC 版本。

---

## 2. 当前 RC 能演示什么

- 用中文描述一个产品。
- 后端调用 ProductLearning LLM 生成产品画像草稿。
- 用户在 Android 上确认产品画像。
- 后端调用 LeadAnalysis LLM 生成获客方向。
- 后端生成结构化分析报告。
- Android 首页、结果页和报告页显示完整状态。
- run detail 可查看 ProductLearning / LeadAnalysis 的 token usage。

---

## 3. 当前 RC 不能承诺什么

- 不承诺生产级可用性。
- 不承诺低延迟或 30 秒内完成。
- 不提供 CRM、联系人抓取、自动触达、外呼或导出。
- 不提供多用户、团队权限、正式云部署或正式数据隔离。
- 不提供 LLM timeout fallback，除非后续 demo 再次被 timeout 阻断。
- 不接外部搜索或实时行业数据。

---

## 4. RC 验收标准

一次 RC demo 通过，至少应满足：

| 项目 | 标准 |
|---|---|
| backend | 独立 smoke DB 启动，`/health` 正常 |
| Android | 真机 install / launch 成功 |
| 中文输入 | `ADB_INPUT_B64` 可输入固定中文样例 |
| ProductLearning | run `succeeded` |
| ProductProfile | 达到可确认状态并确认到 `confirmed` |
| LeadAnalysis | LLM run `succeeded`，usage 可见 |
| ReportGeneration | run `succeeded` |
| 首页 | 显示报告已生成 |
| 结果页 | 显示优先尝试方向 |
| 报告页 | 显示执行摘要、重点建议、状态可复看 |
| logcat | 无 app crash 信号 |

---

## 5. 固定 Demo 输入

- 产品名：`工厂设备巡检助手`
- 一句话说明：`面向制造业设备主管的移动巡检和故障记录工具`
- 初始材料：`支持离线巡检、设备台账、异常拍照、维修派单；目标客户是中小制造工厂、设备主管和维修班组。`
- 补充材料：`补充：重点服务离散制造、机械加工和设备密集型工厂；核心痛点是纸质巡检漏项、故障记录分散、维修响应慢；优势是低成本部署、移动端离线可用、现场照片和维修闭环。`

---

## 6. 当前风险

1. **延迟风险**
   - 控制台 TTFT 中位数约 9.9s，最大约 35.9s。
   - demo / smoke 必须把 LLM run 视为异步任务。

2. **LLM 输出格式风险**
   - 最近真机 demo 曾触发一次 LeadAnalysis JSON decode failure。
   - 已修复为扫描第一个合法 JSON object，但仍需在样例扩展中继续观察。

3. **报告可读性风险**
   - 报告结构已像交付物，但 LLM 生成的长建议可能在 report 中形成过长 bullet。
   - 下一步应做 report readability postprocess。

4. **fallback 风险**
   - 本轮 demo 没有 timeout 阻断，因此没有实现 fallback。
   - 只有 timeout 再次阻断 demo 时才重新打开 latency / fallback task。

---

## 7. 推荐后续顺序

1. Report readability postprocess。
2. Extended business eval round 2。
3. Demo runbook and evidence pack。

当前不建议新增 V1 外能力。
