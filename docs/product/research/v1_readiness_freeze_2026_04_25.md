# V1 Readiness Freeze：2026-04-25

## 1. 结论

V1 当前状态：**具备 demo 条件，接近内测可用，但仍应明确标记延迟、报告深度和供应商稳定性风险。**

当前可 demo 的主闭环：

`产品学习 -> 产品画像确认 -> 获客分析 -> 分析报告 -> 首页状态回流`

当前不应扩展到 CRM、联系人抓取、自动外呼、自动触达、企业工作流、导出分享或部署迁移。

---

## 2. 当前能力状态

| 模块 | 当前状态 | 证据 |
|---|---|---|
| ProductLearning | 已接入 Tencent TokenHub `minimax-m2.5` | 8 个真实样例稳定，未触发 prompt tuning |
| ProductLearning iteration | Android 可继续补充一轮信息 | 真机 create / enrich 中文 smoke 已通过 |
| ProductProfile confirmation | 已有确认门控 | 只有 ready draft 可确认 |
| LeadAnalysis | 已接入 Tencent TokenHub `minimax-m2.5` | 8 个真实样例 LLM eval 通过 |
| ReportGeneration | 仍为 heuristic | 可承接 LeadAnalysisResult，但交付感仍需 polish |
| Android 主闭环 | 已跑通 | 真机 full sales flow smoke 已完成 |
| 中文输入 smoke | 已有测试 IME 方案 | `ADB_INPUT_B64` 可用于固定中文样例 |
| Usage metadata | 已可见 | ProductLearning 与 LeadAnalysis 都记录 `llm_usage` |
| TTFT / latency | 存在明显风险 | 控制台 TTFT 中位数约 9.9s，最大约 35.9s |

---

## 3. Demo Acceptance

一次 V1 demo 至少应满足：

1. 从空库创建中文 ProductProfile。
2. ProductLearning run `succeeded`，ProductProfile 达到 `ready_for_confirmation`。
3. 用户确认 ProductProfile。
4. LeadAnalysis LLM run `succeeded`。
5. ReportGeneration run `succeeded`。
6. 首页显示最终报告已生成状态。
7. 结果页可看到获客分析方向。
8. 报告页可看到可复看的分析报告。
9. run detail 中 ProductLearning / LeadAnalysis 的 `llm_usage.total_tokens` 可定位。
10. Android 不出现 `FATAL EXCEPTION` / `AndroidRuntime` 崩溃。

不要求：

- 30 秒内一定完成。
- 每次都具备稳定低延迟。
- 报告达到最终商业交付质量。
- 支持导出、分享、CRM、触达或多项目管理。

---

## 4. 固定 Demo 样例

优先使用：

- 产品名：`工厂设备巡检助手`
- 一句话说明：`面向制造业设备主管的移动巡检和故障记录工具`
- 初始材料：`支持离线巡检、设备台账、异常拍照、维修派单；目标客户是中小制造工厂、设备主管和维修班组。`
- 补充材料：`补充：重点服务离散制造、机械加工和设备密集型工厂；核心痛点是纸质巡检漏项、故障记录分散、维修响应慢；优势是低成本部署、移动端离线可用、现场照片和维修闭环。`

备用 backend eval 样例：

- 门店会员复购助手
- 教培招生线索跟进助手
- 工业备件询价管理工具
- 口腔诊所预约与复诊运营工具
- 装修 / 工程项目报价跟进助手
- 外贸 B2B 询盘跟进助手
- 本地生活门店排班与经营异常助手

---

## 5. 成本与延迟

最近 8 样例 LeadAnalysis LLM eval：

- ProductLearning token total：9222
- LeadAnalysis token total：15286
- Combined token total：24508
- Average combined token：约 3064 / 样例

腾讯云控制台 TTFT 数据：

- 非空分钟点：27
- 中位数：约 9896 ms
- P95：约 15868 ms
- 最大值：约 35936 ms

判断：

- 延迟风险真实存在，但暂不阻塞 V1 继续开发。
- `lead_analysis` 已设置最小 60s timeout。
- Demo / smoke 必须把 run 当作异步任务，不应假设同步低延迟。

---

## 6. Known Limitations

- `report_generation` 仍是 heuristic，当前报告仍需要表达 polish。
- `lead_analysis` LLM 失败时目前不自动 fallback 到 heuristic。
- 不接外部搜索，行业证据来自用户输入、产品画像和模型归纳。
- 当前 key 访问 `tokenhub-intl.tencentmaas.com` 返回 401，境外 endpoint 暂不可用。
- jianglab 仍可能经 Tailscale / 新加坡出口访问公网；本轮暂不处理网络路由。
- SQLite 仍是当前开发持久化基线，未进入 Postgres。
- 没有 Langfuse / OTEL / 自动 eval 平台。

---

## 7. 推荐后续顺序

1. `task_v1_report_generation_polish.md`
   - 让最终报告更像用户可复看的交付物。
2. `task_v1_demo_device_smoke_after_llm_lead_analysis.md`
   - 在真机验证 LeadAnalysis LLM 后的完整 demo 路径。
3. `task_v1_llm_latency_and_fallback_followup.md`
   - 只在 demo smoke 被 timeout 明显阻断时执行。

当前不建议继续新增大能力。
