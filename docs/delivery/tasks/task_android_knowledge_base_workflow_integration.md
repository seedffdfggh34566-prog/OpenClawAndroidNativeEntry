# Task：Android Knowledge Base 工作流接入

更新时间：2026-04-23

## 1. 任务定位

- 任务名称：Android Knowledge Base 工作流接入
- 建议路径：`docs/delivery/tasks/task_android_knowledge_base_workflow_integration.md`
- 当前状态：`done`
- 优先级：P1

---

## 2. 任务目标

在不安装 Android CLI、也不修改 Android 源码的前提下，把 Android Knowledge Base
接入当前仓库的 Android 工作流、规则层与相关 Skill 规格层。

---

## 3. 当前背景

当前仓库已经完成：

- 根 `AGENTS.md` 与 `app/AGENTS.md` 分层
- Android 默认实现风格解释文档
- Android / workflow Skills 规格层

当前仍未完成：

- Android 官方最新文档 grounding 在仓库工作流中的明确落点
- Android Knowledge Base 与仓库事实源边界的明确说明
- Android CLI 在当前仓库中的定位说明

---

## 4. 范围

本任务 In Scope：

- 在 Android 作用域规则中加入 Android Knowledge Base 的定位
- 在 Android 相关 workflow 文档中补充标准使用方式
- 对相关 Android Skill specs 做最小补充
- 明确 Android CLI 只是可选增强工具
- 新增本 task 与对应 handoff

本任务 Out of Scope：

- 安装 Android CLI
- 创建真实 Skills
- 修改 Android 产品代码
- 改动测试基建
- 把 Android Knowledge Base 升格为项目事实源

---

## 5. 涉及文件

高概率涉及：

- `app/AGENTS.md`
- `docs/architecture/clients/android-client-implementation-constraints.md`
- `docs/how-to/operate/developer_workflow_playbook.md`
- `docs/how-to/operate/jianglab_codex_ops.md`
- `docs/how-to/operate/skills/android-build-verify.md`
- `docs/how-to/operate/skills/android-logcat-triage.md`
- `docs/how-to/operate/skills/android-ui-change-check.md`
- `docs/how-to/operate/skills/android-runtime-integration-guard.md`
- `docs/delivery/tasks/task_android_knowledge_base_workflow_integration.md`
- `docs/delivery/handoffs/handoff_2026_04_23_android_knowledge_base_workflow_integration.md`

参考文件：

- 根 `AGENTS.md`
- `docs/README.md`
- `docs/delivery/tasks/_active.md`

---

## 6. 产出要求

至少应产出：

1. Android Knowledge Base 在仓库中的明确定位
2. Android 工作流中的标准使用边界
3. 对相关 Android Skill specs 的最小补充
4. Android CLI “可选增强、非前置依赖”的明确说明

---

## 7. 验收标准

满足以下条件可认为完成：

1. Android 相关规则明确“优先查官方 Android 文档 / Android Knowledge Base”
2. 仓库文档仍明确 `docs/`、task、handoff 是项目事实源
3. 只有需要最新官方 guidance 的 Android Skills 才补充 Android Knowledge Base 说明
4. Android CLI 没有被写成仓库必装工具或前置依赖
5. 本次变更不依赖 Android CLI 安装或真实 `android docs` 执行

---

## 8. 风险与注意事项

- 不要把 Android Knowledge Base 写成产品方向来源
- 不要让外部官方资料直接覆盖 task / docs / handoff 的边界
- 不要把 Android CLI 提前写进必备工具链
- 不要把本任务扩展成 Android CLI 试点实施任务

---

## 9. 已做验证

本次已完成以下验证：

1. 运行文档层校验命令确认 patch 无格式错误
2. 搜索确认 Android Knowledge Base 约定只落在 Android 作用域规则、Android 相关 workflow 文档与 Android 相关 Skill specs
3. 搜索确认 Android CLI 仅被写成可选增强工具

---

## 10. 实际结果说明

当前仓库已经形成如下接入方式：

1. Android 问题默认优先查官方 Android 文档 / Android Knowledge Base
2. 仓库事实仍以 `AGENTS.md`、`app/AGENTS.md`、`docs/`、task、handoff 为准
3. Android CLI 当前仅保留为后续试点增强项
