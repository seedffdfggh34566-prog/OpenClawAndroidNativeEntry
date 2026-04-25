# 阶段性交接：Product Learning Eval / Prompt Tuning Follow-up

更新时间：2026-04-25

## 1. 本次做了什么

- 新增并完成 `task_v1_product_learning_eval_prompt_tuning_followup.md`。
- 新增真实样例 eval 记录：`docs/product/research/product_learning_llm_eval_2026_04_25.md`。
- 使用真实 TokenHub `minimax-m2.5` 跑 6 个 create 样例和 2 个 enrich 样例。
- 根据固定阈值判断是否需要 prompt tuning。
- 本次未修改 backend runtime、API、schema、Android 代码或 prompt。

---

## 2. 本次验证了什么

1. `backend/.env` 存在，未读取或打印 secret 内容。
2. backend 使用 `/tmp/openclaw_product_learning_eval_2026_04_25.db` 启动，`/health` 返回 `{"status":"ok"}`。
3. 6 个 create 样例全部成功：
   - `run_00bc5cb8`
   - `run_88b687fc`
   - `run_3fb6b500`
   - `run_098b11e2`
   - `run_ad8d026d`
   - `run_e255a17e`
4. 2 个 enrich 样例全部成功：
   - `run_b625a20e`
   - `run_01b41486`
5. 8/8 样例 `AgentRun.status=succeeded`。
6. 8/8 样例 `learning_stage=ready_for_confirmation`。
7. 8/8 样例 required fields filled 为 `4/4`。
8. 人工判断明显幻觉字段总数为 0。
9. DB metadata 确认：
   - `prompt_version=product_learning_llm_v1`
   - `llm_model=minimax-m2.5`
   - create 样例 `round_index=0`
   - enrich 样例 `round_index=1`
10. `git diff --check`
    - 结果：通过。

---

## 3. 结论

本次未触发 prompt tuning 条件：

- create 样例失败数为 0
- 字段补齐不足样例数为 0
- 明显幻觉字段总数为 0
- Sample A 未再次出现稳定偏窄或错误行业归类

因此保留当前默认：

- provider：Tencent TokenHub
- model：`minimax-m2.5`
- prompt_version：`product_learning_llm_v1`

---

## 4. 已知限制

- 当前 public API 和 AgentRun detail 未暴露 token usage，本次 `token_usage` 记录为 `not_exposed`。
- 本次只评估 product learning，不覆盖 lead_analysis / report_generation。
- 本次没有跑 `kimi-k2.5` / `glm-5` 对照，因为未触发对照条件。
- 本次人工 eval 仍是轻量人工判断，不是自动评分平台。

---

## 5. 推荐下一步

1. 若继续推进质量侧，扩大真实业务样例库，并记录更多失败 / 边界样例。
2. 若回到产品体验侧，执行 ProductLearning 页面表达 polish，降低工程词汇和输入误触风险。
3. 若未来需要记录 token 成本，可单独拆 runtime usage metadata follow-up，把 TokenHub usage 写入 runtime metadata。
