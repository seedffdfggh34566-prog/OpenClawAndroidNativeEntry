# Task：V1 Extended Business Eval Round 2

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V1 Extended Business Eval Round 2
- 建议路径：`docs/delivery/tasks/task_v1_extended_business_eval_round2.md`
- 当前状态：`done`
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

- 已使用真实 TokenHub `minimax-m2.5` 跑完 16 个中文业务样例。
- 已开启 developer LLM inspector，trace dir 为 `/tmp/openclaw_llm_traces_round2`。
- 端口实际使用 `127.0.0.1:8014`：
  - 原因是 `8013` 已有人工 inspector backend 占用。
  - 为避免停止人工查看进程，本轮 eval 临时使用 `8014`。
- Eval 记录已更新：`docs/product/research/v1_extended_business_eval_round2_2026_04_25.md`。
- 初始 eval 中 3 个 LeadAnalysis run 因模型输出 malformed JSON 失败。
- 本任务内做了最小 parser 修复：
  - 仅兼容 LeadAnalysis JSON 尾部多一个 `}` 或缺少数组 `]` 的已观测问题。
  - 不改 prompt、模型、provider、public API、schema 或 Android。
- 修复后只重跑受影响样例，最终达到验收线：
  - ProductLearning succeeded：16/16
  - LeadAnalysis succeeded：16/16
  - ReportGeneration succeeded：16/16
  - report_readability pass：16/16
  - hallucination_count total：0
  - product_learning token total：18785
  - lead_analysis token total：28451

---

## 6. 验证

- `backend/.venv/bin/python -m pytest backend/tests/test_tokenhub_client.py backend/tests/test_dev_llm_inspector.py`
  - 通过，16 passed。
- `backend/.venv/bin/python -m pytest backend/tests`
  - 通过，47 passed。
- backend smoke：
  - `/health` 返回 `{"status":"ok"}`。
  - `/dev/llm-runs` 可读取 round2 trace。
- `git diff --check`
  - 通过。

---

## 7. Handoff

- 见 `docs/delivery/handoffs/handoff_2026_04_25_extended_business_eval_round2.md`。
