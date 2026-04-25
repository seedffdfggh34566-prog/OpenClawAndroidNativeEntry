# Task：V1 LLM Latency And Fallback Follow-up

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V1 LLM Latency And Fallback Follow-up
- 建议路径：`docs/delivery/tasks/task_v1_llm_latency_and_fallback_followup.md`
- 当前状态：`conditional_not_triggered`
- 优先级：P1（conditional）

本任务用于在真实 demo smoke 中出现 LLM timeout 明确阻断时，才进入延迟证据记录、prompt / timeout 最小调整或 fallback 设计。

本次 `task_v1_demo_device_smoke_after_llm_lead_analysis.md` 没有出现 timeout 阻断，因此本任务只记录触发条件与未触发结论，不做实现。

---

## 2. 触发条件

只有出现以下任一情况，才执行实现：

1. ProductLearning timeout 阻断 demo。
2. LeadAnalysis timeout 阻断 demo。
3. 同一路径重试 2 次仍因 timeout 失败。
4. Android 用户体验表现为长时间无反馈或误导，且后端 run 证据指向 LLM timeout。

---

## 3. 本次判断结果

本次 demo smoke 结果：

- ProductLearning LLM succeeded。
- LeadAnalysis LLM 首次失败原因是 `lead_analysis_llm_json_decode_failed`，不是 timeout。
- 已在 `task_v1_demo_device_smoke_after_llm_lead_analysis.md` 内做最小 JSON 解析修复。
- 修复后 LeadAnalysis LLM run `run_cb68783e` succeeded。
- LeadAnalysis LLM run 耗时约 8.6 秒，`llm_usage.total_tokens=1864`。
- ReportGeneration succeeded。
- Android 首页 / 结果页 / 报告页状态正确。

结论：

> 本次未触发 latency / fallback 实现条件。

---

## 4. 若未来触发时的最小方案

若后续 demo 确认被 timeout 阻断，执行顺序固定为：

1. 记录失败 run id、`error_type`、开始 / 结束时间、是否重试成功。
2. 对比 ProductLearning 与 LeadAnalysis 的 token usage、耗时和输入规模。
3. 优先压缩 prompt 或调高单次 timeout 配置。
4. 只有 lead_analysis timeout 反复阻断 demo 时，才考虑 heuristic fallback。

仍不做：

- 供应商切换。
- 境外 endpoint。
- split route。
- Token Plan。
- 多模型自动路由。

---

## 5. 实际产出

- 创建 conditional task 文档。
- 未修改 runtime、API、schema、Android 或配置。
- 未实现 fallback。
- `_active.md` 更新为当前无排定 implementation task。

---

## 6. 验证

- 参考 `task_v1_demo_device_smoke_after_llm_lead_analysis.md`：
  - 真机 demo 已跑通。
  - 未出现 timeout 阻断。
  - `adb logcat` 未发现 Android 崩溃信号。
- 本任务为 docs-only conditional closeout：
  - `git diff --check` 通过。

---

## 7. 后续建议

当前 4 个连续实施任务已完成：

1. V1 readiness freeze。
2. Report generation polish。
3. Demo device smoke after LLM lead analysis。
4. Latency / fallback conditional follow-up 未触发。

下一步应回到规划层，在“继续质量评估 / 更大样例库 / 报告可读性细节 / 正式发布准备”中选择新的已文档化任务。
