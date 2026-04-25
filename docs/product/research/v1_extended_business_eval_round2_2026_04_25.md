# V1 Extended Business Eval Round 2：2026-04-25

## 1. 评估目标

本轮评估用于验证 V1 RC 在更多真实业务输入下的完整链路质量：

```text
ProductLearning -> ProductProfile confirmation -> LeadAnalysis LLM -> ReportGeneration
```

本轮只评估质量、稳定性和成本，不新增功能。

---

## 2. 执行环境

- backend：`127.0.0.1:8013`
- database：`/tmp/openclaw_v1_extended_business_eval_round2_2026_04_25.db`
- provider：Tencent TokenHub
- model：`minimax-m2.5`
- prompt versions：`product_learning_llm_v1`、`lead_analysis_llm_v1`

---

## 3. 结果表

尚未执行。

2026-04-25 曾进入本任务准备阶段并启动独立 backend，但在正式跑 16 个样例前中断。当前决定先补 `task_v1_developer_llm_run_inspector.md`，以便 round2 eval 能查看每个样例 ProductLearning / LeadAnalysis 的 LLM raw output、parsed draft、usage、duration 和 parse status。

---

## 4. 总结

尚未执行。等待 developer LLM run inspector 完成后继续。
