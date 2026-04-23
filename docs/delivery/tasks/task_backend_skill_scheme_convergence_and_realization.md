# Task：后端 Skill 收敛与真实 Skill 落地

更新时间：2026-04-23

## 1. 任务定位

- 任务名称：后端 Skill 收敛与真实 Skill 落地
- 建议路径：`docs/delivery/tasks/task_backend_skill_scheme_convergence_and_realization.md`
- 当前状态：`done`
- 优先级：P1

本任务用于把 backend skill 体系从“5 份 repo 内 specs”收敛为“6 个正式 backend workflow skills”，并将其落到 repo 内真实 skill 源码与本机可安装 skills。

---

## 2. 任务目标

至少完成以下结果：

- 当前 backend skill 集固定为 6 个
- 新增 `backend-task-bootstrap`
- 原有 5 个 specs 吸收重叠候选方案
- repo 内存在真实 skill 源码目录
- 本机 Codex skills 目录可安装并发现这 6 个 backend skills

---

## 3. 当前背景

当前仓库此前已具备：

- backend 局部规则 `backend/AGENTS.md`
- 5 份 backend skill specs
- backend rollout order

但此前仍缺：

- task/bootstrap 类型 skill
- 收敛后的正式 backend skill 集合
- repo 内真实 skill 源码
- skills 同步安装入口

---

## 4. 范围

本任务 In Scope：

- 新增 `backend-task-bootstrap` spec
- 更新现有 backend skill specs 的职责边界
- 更新 backend skill 索引与 rollout 文档
- 新增 repo 内真实 skill 源码
- 新增本机技能同步脚本
- 同步安装 6 个 backend skills
- 新增对应 handoff

本任务 Out of Scope：

- 修改 backend 产品功能
- 新增 `agent_trace_and_eval`
- 新增 `tool_registration_mcp`
- 新增 `human_review_gate`
- 新增 `agent_run_lifecycle`
- 新增 `structured_output_validation`
- 新增 `backend-postgres-cutover-guard`

---

## 5. 涉及文件

高概率涉及：

- `docs/how-to/operate/skills/*`
- `docs/how-to/operate/agent_skills_boundary_and_index.md`
- `docs/how-to/operate/skills-src/*`
- `scripts/sync_codex_skills.py`
- `docs/delivery/tasks/task_backend_skill_scheme_convergence_and_realization.md`
- `docs/delivery/handoffs/` 下对应 handoff

---

## 6. 验收标准

满足以下条件可认为完成：

1. 当前 backend 正式 skill 集合固定为 6 个
2. `backend-task-bootstrap` 已加入 spec 与真实 skill 源码
3. `backend_local_runbook`、`api_contract_change`、`schema_and_migration` 已并入现有 skill，而不是单独新增
4. 未来技能候选只保留为 follow-up，不假装成当前已落地
5. 真实 skill 源码可同步安装到本机 Codex skills 目录

---

## 7. 实际产出

本次已完成以下产出：

1. 新增 `backend-task-bootstrap` spec
2. 更新 5 份 backend skill specs 的收敛边界
3. 更新 `backend-rollout-order.md` 与 skill 索引说明
4. 新增 6 个 repo 内真实 backend skill 源码目录
5. 新增 `scripts/sync_codex_skills.py`
6. 将 6 个 backend skills 同步安装到本机 Codex skills 目录
7. 新增对应 handoff

---

## 8. 已做验证

本次已完成以下验证：

1. 运行 6 个 skill 目录的 `quick_validate.py`
2. 运行 `scripts/sync_codex_skills.py`
3. 确认 `${CODEX_HOME:-$HOME/.codex}/skills/` 下已存在 6 个 backend skills
4. 运行 `backend-local-verify` bundled script 的真实 smoke
5. 运行 `git diff --check`

---

## 9. 下一步衔接

本任务完成后，backend skills 的下一步建议为：

1. 先在真实 backend threads 中高频使用这 6 个 skills
2. 等 `Langfuse` 真接入后，再考虑 `agent_trace_and_eval`
3. 等 `MCP` 真进入后端工具边界后，再考虑 `tool_registration_mcp`
4. 等 `waiting_for_user` / interrupt / resume 进入实现后，再考虑 `agent_run_lifecycle` 与 `human_review_gate`
