# Task：V1 Real Business Sample Library Eval

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V1 Real Business Sample Library Eval
- 建议路径：`docs/delivery/tasks/task_v1_real_business_sample_library_eval.md`
- 当前状态：`done`
- 优先级：P1

本任务用于在 V1 主闭环、真实 LLM product learning、真实中文 smoke 和 runtime usage metadata 均完成后，用更多真实业务样例评估完整价值链路质量。

---

## 2. 任务目标

通过 backend API 跑 8 个真实中文业务样例，验证：

1. product learning 是否稳定生成可确认 ProductProfile。
2. lead_analysis 是否生成相关且可执行的获客分析。
3. report_generation 是否生成可读、可复看的报告。
4. product learning LLM token usage 是否可记录到 eval 表。

---

## 3. 范围

本任务 In Scope：

- 新增真实业务样例 eval 记录。
- 使用独立 DB 执行 backend API 全链路。
- 记录质量、成本、失败点和后续建议。
- 更新 task、handoff 和 docs 入口。

本任务 Out of Scope：

- 不改 prompt。
- 不改模型。
- 不把 lead_analysis / report_generation 切到 LLM。
- 不改 Android UI。
- 不新增 public API。
- 不引入自动评分平台。

---

## 4. 固定样例

1. 制造业设备巡检助手
2. 门店会员复购助手
3. 教培招生线索跟进助手
4. 工业备件询价管理工具
5. 口腔诊所预约与复诊运营工具
6. 装修 / 工程项目报价跟进助手
7. 外贸 B2B 询盘跟进助手
8. 本地生活门店排班与经营异常助手

---

## 5. 验收标准

满足以下条件可认为完成：

1. 8 个样例中 product_learning failed 数为 0。
2. 至少 6/8 样例达到 `ready_for_confirmation`。
3. 至少 6/8 样例的 lead_analysis relevance 标为 `pass`。
4. 至少 6/8 样例的 report readability 标为 `pass`。
5. 明显幻觉字段总数小于 4。
6. eval 文档记录 `llm_usage.total_tokens`。
7. `git diff --check` 通过。

---

## 6. 执行环境

- backend：`127.0.0.1:8013`
- database：`/tmp/openclaw_v1_real_business_sample_eval_2026_04_25.db`
- provider：腾讯云 TokenHub
- model：`minimax-m2.5`
- API key：只从 `backend/.env` 读取，不打印、不写入文档

---

## 7. 实际产出

- 新增真实业务样例 eval 记录：`docs/product/research/v1_real_business_sample_eval_2026_04_25.md`。
- 使用 8 个真实中文业务样例跑通 backend API 全链路：
  - ProductLearning
  - ProductProfile confirm
  - lead_analysis
  - report_generation
- 记录每个样例的 `llm_usage.total_tokens`。
- 发现并修复 lead/report 用户可见工程表述泄漏：
  - `Phase 1`
  - `LangGraph`
  - `v1_langgraph_phase1`
- 未改模型、未调 prompt、未新增 API、未改 Android UI。

---

## 8. 已做验证

已完成：

1. `git status --short`
   - 开始执行前工作区干净。
2. `backend/.env`
   - 文件存在，未读取或打印 secret 内容。
3. backend smoke
   - DB：`/tmp/openclaw_v1_real_business_sample_eval_2026_04_25.db`
   - `/health` 返回 `{"status":"ok"}`。
4. 初始 8 样例 eval
   - product_learning failed：0/8。
   - ready_for_confirmation：8/8。
   - lead_analysis relevance pass：8/8。
   - lead_analysis actionability pass：8/8。
   - report readability：0/8，原因是用户可见工程表述泄漏。
5. 最小代码修复后复跑 lead/report
   - report readability：8/8。
   - `analysis_scope` 均为 `基于已确认产品画像的获客方向分析`。
6. 最终验收汇总
   - product_learning failed：0/8。
   - ready_for_confirmation before confirm：8/8。
   - required_fields_filled：8/8 为 4/4。
   - lead_analysis relevance pass：8/8。
   - lead_analysis actionability pass：8/8。
   - report readability pass：8/8。
   - hallucination_count total：0。
   - product_learning LLM token total：9233。
7. `backend/.venv/bin/python -m pytest backend/tests`
   - 结果：35 passed。
8. `git diff --check`
   - 结果：通过，无输出。
9. 临时 backend
   - 已停止，`127.0.0.1:8013` 已释放。

---

## 9. 实际结果说明

当前任务已完成。V1 全链路在 8 个真实中文业务样例上稳定跑通；本轮暴露并修复了 lead/report 工程表述泄漏问题。后续若继续提升产品价值，建议优先拆 lead_analysis / report_generation 质量提升任务。
