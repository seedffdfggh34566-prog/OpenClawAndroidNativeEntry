# Task：V1 Extended Business Eval Round 2

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V1 Extended Business Eval Round 2
- 建议路径：`docs/delivery/tasks/task_v1_extended_business_eval_round2.md`
- 当前状态：`planned`
- 优先级：P0

本任务用于在 V1 RC hardening、report readability postprocess 和 developer LLM run inspector 后，用 16 个真实中文业务样例验证完整 backend API 链路质量、稳定性和 token 成本。

验证链路：

```text
product_learning -> confirm -> lead_analysis -> report_generation
```

---

## 2. 范围

In Scope：

- 使用独立 DB 和真实 TokenHub。
- 使用 backend API 执行，不走 Android。
- 记录 ProductLearning / LeadAnalysis token usage。
- 记录 run status、report readability、actionability、hallucination_count 和 review_note。
- 若暴露明确稳定性 bug，只做最小修复并重跑受影响样例。

Out of Scope：

- 不改 Android。
- 不改 public API / schema。
- 不做 prompt tuning 大改。
- 不切模型 / provider。
- 不实现 fallback。

---

## 3. 固定环境

- backend：`127.0.0.1:8013`
- database：`/tmp/openclaw_v1_extended_business_eval_round2_2026_04_25.db`
- provider：Tencent TokenHub
- model：`minimax-m2.5`
- API key：只从 `backend/.env` 或环境变量读取，不打印、不写入文档。

---

## 4. 验收标准

- ProductLearning succeeded >= 15/16。
- LeadAnalysis succeeded >= 15/16。
- ReportGeneration succeeded >= 16/16。
- report_readability pass >= 14/16。
- 明显幻觉总数 < 6。
- token usage 记录完整。

---

## 5. 实际产出

- 尚未执行。
- 2026-04-25 曾创建本任务并启动临时 backend，但用户中断后决定先补 developer LLM run inspector。
- 未跑 16 个样例，未产生 eval 结果。

---

## 6. 验证

- 尚未执行。

---

## 7. Handoff

- 尚未执行；等待 `task_v1_developer_llm_run_inspector.md` 完成后继续。
