# Task：V1 Product Learning Eval / Prompt Tuning Follow-up

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V1 Product Learning Eval / Prompt Tuning Follow-up
- 建议路径：`docs/delivery/tasks/task_v1_product_learning_eval_prompt_tuning_followup.md`
- 当前状态：`done`
- 优先级：P1

本任务用于在 V1 主闭环已经跑通后，验证 `minimax-m2.5 + product_learning_llm_v1` 在更多真实产品输入下的稳定性。

本任务默认只做真实样例评估与记录；只有命中明确质量阈值时，才做最小 prompt 调整。

---

## 2. 任务目标

验证 product learning LLM 当前版本是否能稳定完成：

1. 真实产品材料的结构化抽取
2. 关键字段补齐
3. `ready_for_confirmation` 阶段收敛
4. enrich 后字段补强且不引入明显幻觉

---

## 3. 范围

本任务 In Scope：

- 使用真实 TokenHub `minimax-m2.5`
- 固定 `product_learning_llm_v1`
- 跑 6 个 create 样例 + 2 个 enrich 样例
- 记录人工 eval 表格
- 若触发阈值，做最小 prompt v1.1 调整
- 更新 task、handoff、eval 文档和必要索引

本任务 Out of Scope：

- lead_analysis / report_generation prompt 调整
- 多模型自动路由
- backend API / schema 修改
- Android UI 修改
- Langfuse / OTEL / 自动评分器
- Token Plan 或成本系统

---

## 4. 固定样例

Create 样例：

- Sample A：企业服务 SaaS
- Sample B：制造业软件工具
- Sample C：零售运营工具
- Sample D：教育培训招生 / 课程顾问工具
- Sample E：本地服务门店会员 / 复购运营工具
- Sample F：B2B 工业备件 / 询价管理工具

Enrich 样例：

- Sample B enrich：制造业样例补充离线、维修闭环、照片证据和低成本部署
- Sample C enrich：零售样例补充会员分层、库存预警、复购活动和多门店管理

---

## 5. Prompt Tuning 触发规则

固定规则如下：

- 若 6 个 create 样例中 `AgentRun.failed >= 1`，先定位错误，不调 prompt。
- 若 `required_fields_filled < 4/4` 的样例数 >= 2，做 prompt v1.1。
- 若明显幻觉字段总数 >= 3，做 prompt v1.1。
- 若 Sample A 再次稳定偏向过窄或错误行业归类，做 prompt v1.1。
- 若未触发以上条件，本任务只更新 eval 文档，不改 runtime 代码。

若需要 prompt v1.1：

- 只调整 `backend/runtime/graphs/product_learning.py` prompt 文案。
- 将默认 prompt version 改为 `product_learning_llm_v1_1`。
- 更新相关 tests、reference、task、handoff。
- 不新增多模型路由，不改 API，不改 schema。

---

## 6. 验收标准

满足以下条件可认为完成：

1. `backend/.env` 存在，且执行过程不读取或打印 secret 内容
2. backend 使用独立 eval DB 启动，`/health` 成功
3. 6 个 create 样例均跑到 terminal
4. 2 个 enrich 样例均跑到 terminal
5. 记录每个样例的 run status、learning stage、字段补齐率、幻觉数、review note
6. 明确是否触发 prompt tuning
7. 若未改代码，`git diff --check` 通过即可
8. 若改 prompt / runtime 代码，必须运行 backend tests 并重新验证触发样例

---

## 7. 风险与注意事项

- 真实 API key 只从 `backend/.env` 读取，不写入文档。
- 本任务会产生真实 TokenHub 调用费用，应限制在固定样例规模内。
- 如果供应商 timeout 或网络错误，先重试一次；重复失败记录为环境 / 供应商问题。
- 不把一次性人工判断升级为长期自动评分器。

---

## 8. 实际产出

- 完成 6 个 create 样例与 2 个 enrich 样例真实 TokenHub eval。
- 新增 eval 记录：`docs/product/research/product_learning_llm_eval_2026_04_25.md`。
- 新增 handoff：`docs/delivery/handoffs/handoff_2026_04_25_product_learning_eval_prompt_tuning_followup.md`。
- 8/8 样例 `AgentRun.status=succeeded`。
- 8/8 样例 `learning_stage=ready_for_confirmation`。
- 8/8 样例 required fields filled 为 `4/4`。
- 人工判断明显幻觉字段总数为 0。
- 未触发 prompt tuning 阈值，因此未修改 runtime 代码、prompt version、API、schema 或 Android 代码。

---

## 9. 已做验证

已完成：

1. `backend/.env` 存在，未读取或打印 secret 内容。
2. 使用独立 eval DB 启动 backend：
   - `/tmp/openclaw_product_learning_eval_2026_04_25.db`
3. `curl -sS http://127.0.0.1:8013/health`
   - 结果：`{"status":"ok"}`
4. 6 个 create 样例均跑到 terminal：
   - `run_00bc5cb8` succeeded
   - `run_88b687fc` succeeded
   - `run_3fb6b500` succeeded
   - `run_098b11e2` succeeded
   - `run_ad8d026d` succeeded
   - `run_e255a17e` succeeded
5. 2 个 enrich 样例均跑到 terminal：
   - `run_b625a20e` succeeded
   - `run_01b41486` succeeded
6. DB metadata 抽查：
   - `prompt_version=product_learning_llm_v1`
   - `llm_model=minimax-m2.5`
   - create 样例 `round_index=0`
   - enrich 样例 `round_index=1`
7. `git diff --check`
   - 结果：通过。

---

## 10. 后续建议

建议下一步回到规划层，在以下方向中选择：

1. ProductLearning 页面表达 polish，降低工程词汇和输入误触风险。
2. 扩大真实业务样例库，继续积累 product learning 边界样例。
3. 若要做成本记录，拆 runtime usage metadata follow-up，把 TokenHub usage 写入 runtime metadata。
