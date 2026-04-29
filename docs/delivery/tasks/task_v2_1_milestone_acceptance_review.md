# Task: V2.1 Milestone Acceptance Review

更新时间：2026-04-28

## 1. 任务定位

- 任务名称：V2.1 Milestone Acceptance Review
- 建议路径：`docs/delivery/tasks/task_v2_1_milestone_acceptance_review.md`
- 当前状态：`done`
- 优先级：P0
- 任务类型：`closeout`
- 是否属于 delivery package：`yes`
- 所属 package：`V2.1 Milestone Acceptance And Gap Closure`

---

## 1.1 队列衔接

- 当前 task 是否允许执行 agent 自主推进：`yes`
- 当前 task 内部 steps 是否允许连续执行：`yes`
- 完成后是否允许自动进入下游任务：`yes`
- 建议上游入口：`docs/delivery/tasks/_active.md`
- 建议下游任务：
  1. `docs/delivery/tasks/task_v2_1_chat_first_workspace_start_gap_closure.md`
- 自动继续条件：
  - 仅开放 V2.1 product entry polish。
  - 不开放 V2.2 implementation。
- 停止条件：
  - review 发现 gap 需要新 API、migration、外部 provider 或产品方向变更。

---

## 1.2 自动化契约

- 本任务允许编辑：
  - `docs/product/research/v2_1_milestone_acceptance_review_2026_04_28.md`
  - `docs/product/project_status.md`
  - `docs/delivery/tasks/_active.md`
  - package / task / handoff 文档
- 本任务禁止编辑：
  - backend / Android / runtime code
  - PRD / ADR 产品含义
  - V2.2 search / ContactPoint / CRM implementation
- 可在任务内连续完成的 steps：
  1. 读取 PRD / roadmap / ADR / architecture baseline。
  2. 检查 implementation evidence 与 validation evidence。
  3. 生成 PRD Acceptance Traceability。
  4. 根据 review 结果更新 project status 与 next task。
- 必须拆出独立 task 或停止确认的情况：
  - 需要代码实现。
  - 需要新增 API / migration / provider。

---

## 2. 任务目标

用四层证据模型判断 V2.1 是否已实现：

- acceptance source
- implementation / code evidence
- validation evidence
- delivery evidence

task / handoff 只能作为 delivery evidence，不能单独证明 V2.1 implemented。

---

## 3. 当前背景

用户明确认为 V2.1 可能还未实现，并授权开放 V2.1 milestone acceptance and gap closure package。本任务先做 docs-only evidence review，再决定是否需要排入 V2.1 follow-up task。

2026-04-28 后续产品决策：首次入口不再要求用户首句自然语言自动创建 workspace，而是允许通过轻量按钮“开始销售工作区”进入聊天。

---

## 4. 范围

本任务 In Scope：

- V2.1 PRD criteria evidence review。
- capability matrix 更新建议。
- V2.1 product milestone 状态建议。
- 必要的 V2.1 gap-closure task 创建。

本任务 Out of Scope：

- backend / Android / runtime code changes。
- V2.2 evidence / search / ContactPoint。
- formal LangGraph。
- production SaaS、auth、tenant、CRM、自动触达。

---

## 5. 涉及文件

高概率涉及：

- `docs/product/research/v2_1_milestone_acceptance_review_2026_04_28.md`
- `docs/product/project_status.md`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/packages/package_v2_1_milestone_acceptance_and_gap_closure.md`

参考文件：

- `docs/product/prd/ai_sales_assistant_v2_prd.md`
- `docs/product/roadmap.md`
- `docs/adr/ADR-006-v2-conversational-sales-agent-baseline.md`
- `docs/architecture/runtime/v2-1-chat-first-runtime-design.md`
- `docs/architecture/runtime/v2-1-llm-runtime-boundary.md`

---

## 6. 产出要求

至少应产出：

1. V2.1 milestone acceptance review。
2. project status 更新。
3. 如存在 implementation gap，创建具体 gap-closure task。
4. handoff。

---

## 7. 验收标准

满足以下条件可认为完成：

1. Review 使用 `done / partial / missing / out of scope`。
2. 每个 `done` 都有 acceptance source、code evidence、validation evidence。
3. `partial / missing` gap 回到 PRD / roadmap / ADR / architecture baseline。
4. V2.2 implementation 仍 blocked。

---

## 8. 推荐执行顺序

建议执行顺序：

1. 读取 source-of-truth docs。
2. 复核 code evidence 和 validation evidence。
3. 生成 milestone review。
4. 更新 project status 和 `_active.md`。
5. 创建 handoff。

---

## 9. 风险与注意事项

- 不得把 prototype path evidence 直接升级为 product milestone completion。
- 不得把 V2.2 search/contact 缺失算作 V2.1 blocker。
- 不得忽略 PRD 中首次进入销售工作区的 chat-first 入口要求；当前产品口径为轻量按钮“开始销售工作区”。

---

## 10. 下一步衔接

本任务完成后，继续：

1. `docs/delivery/tasks/task_v2_1_chat_first_workspace_start_gap_closure.md`

---

## 11. 实际产出

- 新增 `docs/product/research/v2_1_milestone_acceptance_review_2026_04_28.md`。
- 更新 `docs/product/project_status.md`。
- 更新 `docs/delivery/tasks/_active.md`。
- 新增 `docs/delivery/tasks/task_v2_1_chat_first_workspace_start_gap_closure.md`。
- 新增 handoff。

---

## 12. 本次定稿边界

本次 review 初版曾判定：V2.1 大部分能力已有实现和验证，但 PRD 的“一句话启动 SalesWorkspace”仍是 V2.1 implementation gap。后续产品决策已将该项弱化为轻量按钮入口 polish。

---

## 13. 已做验证

- `backend/.venv/bin/python -m pytest backend/tests/test_sales_workspace_chat_first_api.py backend/tests/test_sales_workspace_chat_first_llm_runtime.py backend/tests/test_sales_workspace_draft_reviews_api.py -q`
  - `35 passed, 1 skipped in 20.28s`
- `git diff --check`
  - passed

---

## 14. 实际结果说明

任务完成。后续产品决策后，V2.1 milestone remains `partial / product_entry_polish_open`，并已开放一个最小 V2.1 product entry polish task。
