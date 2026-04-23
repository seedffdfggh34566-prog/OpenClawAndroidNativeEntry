# 阶段性交接：开发者工作流手册升级

更新时间：2026-04-23

## 1. 本次改了什么

- 重写了 `docs/how-to/operate/developer_workflow_playbook.md`
- 将手册内容切换到当前新 docs 结构与真实执行入口
- 明确了 `AGENTS.md -> docs/README.md -> docs/delivery/tasks/_active.md -> 当前 task` 的标准入口链
- 补齐了方向变化、新任务、细节修订三类变化在新结构下的处理方式

---

## 2. 为什么这么定

旧版手册虽然原则还对，但还停留在更早阶段，没有完整反映当前 docs 控制平面、`_active.md` 驱动方式和新 docs 目录结构。

这次升级的目标是让开发者手册与当前真实工作流保持一致，避免开发者和 agent 对“先看哪份、先改哪份、什么时候开线程、什么时候收口”理解不一致。

---

## 3. 本次验证了什么

1. 检查手册中已不再出现旧编号目录与 `archive_openclaw`
2. 复核手册中的入口顺序与 `AGENTS.md`、`docs/README.md`、`docs/delivery/tasks/_active.md` 一致
3. 复核文档分层与当前 `product / architecture / reference / how-to / adr / delivery / archive` 结构一致

---

## 4. 已知限制

- 本次只升级了开发者手册，没有新增自动化 runbook
- 当前手册仍以人工调度 + 单 task 推进为主，没有展开 24 小时自动化执行细节

---

## 5. 推荐下一步

1. 继续按 `_active.md` 推进当前唯一正式任务
2. 后续如果开始 automation，再补一份专门的自动化工作流手册
