# 阶段性交接：Android Knowledge Base 工作流接入

更新时间：2026-04-23

## 1. 本次改了什么

- 更新 `app/AGENTS.md`
- 更新 `docs/architecture/clients/android-client-implementation-constraints.md`
- 更新 `docs/how-to/operate/developer_workflow_playbook.md`
- 更新 `docs/how-to/operate/jianglab_codex_ops.md`
- 更新 4 份 Android 相关 Skill specs
- 新增本 task 记录

---

## 2. 为什么这么定

- 当前仓库已经进入 Android agent 工作流与 Skill 规格层完善阶段，适合引入官方 Android 最新文档 grounding
- Android Knowledge Base 更适合作为 Android 问题的优先外部参考层，而不是项目事实源
- 当前 `adb + gradle + docs / task / handoff` 基本链路已可工作，不需要为了接入官方文档能力立刻引入 Android CLI
- Android CLI 目前更适合保留为后续单独试点的可选增强项

---

## 3. 本次验证了什么

1. 运行 `git diff --check`
2. 搜索确认 Android Knowledge Base 相关新增约定只出现在 Android 作用域规则、Android 相关 workflow 文档与 Android 相关 Skill specs 中
3. 搜索确认 Android CLI 只被写成可选增强，没有变成仓库前置依赖

---

## 4. 已知限制

- 本次没有安装 Android CLI
- 本次没有真实执行 `android docs`
- 本次没有修改 Android 源码或测试基建
- 后续若要正式试点 Android CLI，仍需单独开 follow-up task

---

## 5. 推荐下一步

1. 继续在 Android 相关研究与架构判断中优先使用官方 Android 文档 / Android Knowledge Base
2. 等出现明确收益后，再单独开 task 评估 Android CLI 试点
