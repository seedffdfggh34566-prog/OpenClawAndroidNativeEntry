# Task：V1 Demo Release Candidate Hardening

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V1 Demo Release Candidate Hardening
- 建议路径：`docs/delivery/tasks/task_v1_demo_release_candidate_hardening.md`
- 当前状态：`done`
- 优先级：P0

本任务用于在 V1 已完成真实 LLM 主闭环、真机中文 demo smoke 和 latency/fallback conditional closeout 后，把当前 demo-ready 状态冻结为 release candidate hardening 基线。

本任务不新增功能，只明确：

1. RC 当前能演示什么。
2. RC 不能承诺什么。
3. 固定 demo 路径、固定样例和验收标准。
4. 后续 3 个任务的执行顺序。

---

## 2. RC 当前状态

当前 V1 已具备 release candidate hardening 条件：

- ProductLearning：已接 Tencent TokenHub `minimax-m2.5`。
- LeadAnalysis：已接 Tencent TokenHub `minimax-m2.5`。
- ReportGeneration：仍为 heuristic，但已 polish 为可复看的交付物结构。
- Android：主闭环、中文输入、产品画像确认、结果页和报告页均已在真机跑通。
- Observability：ProductLearning / LeadAnalysis 的 `llm_usage` 已通过 run detail 可见。
- Latency / fallback：本轮 demo 未被 timeout 阻断，fallback 未触发实现。

当前不进入：

- CRM
- 联系人抓取
- 自动外呼
- 自动触达
- 导出 / 分享
- 多模型路由
- 云部署 / Postgres 迁移

---

## 3. RC Demo Acceptance

一次 RC demo 至少应满足：

1. 使用真实 backend 和独立 smoke DB。
2. 使用真实 TokenHub `minimax-m2.5`，key 只从 `backend/.env` 或环境变量读取。
3. Android 真机可通过 `adb reverse tcp:8013 tcp:8013` 访问 backend。
4. 使用真实中文样例创建 ProductProfile。
5. ProductLearning run `succeeded`。
6. ProductProfile 可确认并成功进入 `confirmed`。
7. LeadAnalysis LLM run `succeeded`，且 run detail 可见 `llm_usage.total_tokens`。
8. ReportGeneration run `succeeded`。
9. 首页显示最终报告已生成状态。
10. 结果页可见 `优先尝试方向`。
11. 报告页可见 `执行摘要`、`重点建议`、`状态：可复看`。
12. `adb logcat` 未发现 `FATAL EXCEPTION` / `AndroidRuntime: FATAL`。

不要求：

- 30 秒内一定完成。
- 网络延迟稳定低于某个阈值。
- 具备生产级 fallback。
- 报告达到最终商业交付质量。
- 支持多项目、团队协作或正式云端部署。

---

## 4. 固定 Demo 样例

优先使用：

- 产品名：`工厂设备巡检助手`
- 一句话说明：`面向制造业设备主管的移动巡检和故障记录工具`
- 初始材料：`支持离线巡检、设备台账、异常拍照、维修派单；目标客户是中小制造工厂、设备主管和维修班组。`
- 补充材料：`补充：重点服务离散制造、机械加工和设备密集型工厂；核心痛点是纸质巡检漏项、故障记录分散、维修响应慢；优势是低成本部署、移动端离线可用、现场照片和维修闭环。`

---

## 5. 已知限制

- TokenHub TTFT 存在明显延迟风险，中位数约 9.9s，最大约 35.9s。
- `lead_analysis` LLM 已设置最小 60s timeout，但没有自动 fallback。
- `report_generation` 仍是 heuristic。
- 当前 Android 中文 smoke 依赖测试设备预装 `com.android.adbkeyboard`。
- 当前持久化仍为 SQLite 开发基线。
- 当前不接外部搜索，行业判断来自用户输入、产品画像和模型归纳。

---

## 6. 后续执行顺序

本任务完成后，固定后续顺序：

1. `task_v1_report_readability_postprocess_followup.md`
   - 收口报告可读性，减少超长 bullet 和长 summary。
2. `task_v1_extended_business_eval_round2.md`
   - 扩展到 16 个真实中文业务样例，评估质量、稳定性和 token 成本。
3. `task_v1_demo_runbook_and_evidence_pack.md`
   - 固化 demo runbook，并跑一次最终真机中文 demo evidence pack。

---

## 7. 实际产出

- 新增 RC hardening task。
- 新增 RC readiness 文档。
- 更新 `_active.md` 和 delivery 索引，将 next task 指向 report readability follow-up。
- 未修改 runtime、backend API、schema、Android 或产品方向文档。

---

## 8. 验证

- `git diff --check`
  - 通过。

---

## 9. Handoff

见 `docs/delivery/handoffs/handoff_2026_04_25_v1_demo_release_candidate_hardening.md`。
