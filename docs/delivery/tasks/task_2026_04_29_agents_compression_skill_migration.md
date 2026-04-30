# Task：AGENTS.md compression and minimal skill migration

更新时间：2026-04-29

## 1. 任务定位

- 任务名称：`AGENTS.md compression and minimal skill migration`
- 当前状态：`done`
- 优先级：P0
- 任务类型：`guardrail / workflow`
- 是否属于 delivery package：`no`
- 文档同步级别：`Level 1 task`

---

## 2. 任务目标

按用户明确授权，将根 `AGENTS.md` 从 V2 / 多 agent / 硬 milestone 口径压缩为 V3-first 的稳定仓库执行契约，并把可复用的 task/bootstrap 与 handoff closeout 流程迁入最小真实 skill。

---

## 3. 范围

In Scope：

- 压缩根 `AGENTS.md`。
- 删除当前默认多 agent 工作流口径。
- 移除硬性 milestone acceptance / PRD traceability 规则。
- 保留 task/handoff 不应随意声明版本、milestone 或产品阶段完成的轻量边界。
- 新增 `repo-task-bootstrap` skill source/spec。
- 更新 `task-handoff-sync` skill source/spec。
- 同步本机 Codex skills。

Out of Scope：

- 不修改 `app/AGENTS.md` 或 `backend/AGENTS.md` 的细节。
- 不启动 V3 runtime / memory / backend / Android 实现。
- 不创建 git worktree 或 milestone review skill。

---

## 4. 涉及文件

- `AGENTS.md`
- `scripts/sync_codex_skills.py`
- `docs/how-to/README.md`
- `docs/how-to/operate/developer_workflow_playbook.md`
- `docs/how-to/operate/multi_agent_workflow.md`
- `docs/how-to/operate/multi_agent_prompts.md`
- `docs/how-to/operate/skills/`
- `docs/how-to/operate/skills-src/`
- `docs/delivery/tasks/_active.md`

---

## 5. 验收标准

满足以下条件可认为完成：

1. `AGENTS.md` 当前方向为 V3，不再把 V2 作为当前默认方向。
2. 根规则不再包含默认多 agent 工作流。
3. 根规则不再包含硬性 milestone acceptance / PRD traceability 表格规则。
4. `repo-task-bootstrap` 作为真实 skill 可同步到本机 Codex skills。
5. `task-handoff-sync` 包含轻量 completion wording guard。
6. `git diff --check` 通过。

---

## 6. 实际产出

- 已压缩根 `AGENTS.md`。
- 已将多 agent how-to 文件降级为 historical reference only。
- 已新增 `repo-task-bootstrap` skill source/spec。
- 已更新 `task-handoff-sync` skill source/spec。
- 已更新 skill 同步脚本并同步本机 skills。

---

## 7. 已做验证

- `git diff --check`
- 关键旧口径 `rg` 检查
- V3 / task-handoff 关键词检查
- 本机 Codex skills 文件存在性检查

---

## 8. 实际结果说明

本任务仅完成仓库工作流与 skill 迁移，不代表 V3 implementation、runtime、memory schema、Android UI 或 backend 代码已启动。
