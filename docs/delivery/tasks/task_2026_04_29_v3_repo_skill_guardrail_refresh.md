# Task：V3 repo-managed skill guardrail refresh

更新时间：2026-04-29

## 1. 任务定位

- 任务名称：`V3 repo-managed skill guardrail refresh`
- 当前状态：`done`
- 优先级：P0
- 任务类型：`guardrail / workflow`
- 是否属于 delivery package：`no`
- 文档同步级别：`Level 1 task`

---

## 2. 任务目标

按用户明确授权，将 repo-managed skills 从 V1/V2 guardrail 口径迁到 V3 Memory-native Sales Agent 口径，重点避免 backend/runtime/memory 相关 skill 继续误导后续实现。

---

## 3. 范围

In Scope：

- V3 化 backend runtime/API/task/DB/contract sync skills。
- 为 Android skills 补充 V3 scope note，明确 V3 不自动开放 Android implementation。
- 增强 `repo-task-bootstrap` 和 `task-handoff-sync` 的当前用户授权、V3 implementation wording、历史 V1/V2 文档边界检查。
- 同步 repo-managed skills 到本机 Codex skills。

Out of Scope：

- 不修改 backend / Android 代码。
- 不启动 V3 runtime、memory schema、migration、Android UI 或 backend implementation。
- 不删除现有 skills。
- 不安装第三方新 skill。

---

## 4. 涉及文件

- `docs/how-to/operate/skills-src/*/SKILL.md`
- `docs/how-to/operate/skills/*.md`
- `docs/delivery/tasks/_active.md`

---

## 5. 验收标准

满足以下条件可认为完成：

1. backend runtime/API/DB skills 以 ADR-009 和 V3 architecture 为当前入口。
2. V1/V2 docs 在相关 skills 中只作为 historical / compatibility reference。
3. Android skills 明确 V3 不自动开放 Android implementation。
4. `repo-task-bootstrap` 能识别当前用户消息作为授权来源。
5. `task-handoff-sync` 检查 V3 implementation / production-ready 过度声明。
6. `git diff --check` 通过。

---

## 6. 实际产出

- 已刷新 backend runtime/API/task/DB/contract sync skills。
- 已为 Android build/runtime/logcat skills 补 V3 scope note。
- 已增强 repo/task handoff workflow skills。
- 已同步本机 Codex skills。

---

## 7. 已做验证

- `git diff --check`
- 关键旧口径残留搜索
- V3 skill guardrail 关键词搜索
- 本机 Codex skills 同步确认

---

## 8. 实际结果说明

本任务仅更新 skill guardrail 与文档规格，不代表 V3 implementation、runtime、memory schema、Android UI 或 backend code 已启动。
