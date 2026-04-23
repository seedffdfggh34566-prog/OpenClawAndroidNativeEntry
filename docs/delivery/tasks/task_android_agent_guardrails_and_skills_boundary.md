# Task：第一阶段规则分层落地与 Android 约束下沉

更新时间：2026-04-23

## 1. 任务定位

- 任务名称：第一阶段规则分层落地与 Android 约束下沉
- 建议路径：`docs/delivery/tasks/task_android_agent_guardrails_and_skills_boundary.md`
- 当前状态：`done`
- 优先级：P1

---

## 2. 任务目标

在不进入具体产品功能开发的前提下，把第一阶段规则分层正式落地，重点达成以下结果：

- 根 `AGENTS.md` 收口回仓库级规则
- Android 详细约束下沉到 `app/AGENTS.md`
- Android 默认实现风格拥有一份方案层解释文档
- Skills 文档继续保留，但只承担边界与索引职责

---

## 3. 当前背景

当前仓库已经完成：

- workflow 标准入口
- docs 主结构迁移
- backend-first 对齐
- Android 控制壳层阶段性重构
- 最小后端实现

但当前仓库已经不是 Android 单端仓库，而是产品主仓库：

- `backend/` 承担正式后端
- `app/` 只是当前客户端入口之一
- 后续仍可能出现 iOS 等更多客户端

在这一背景下，如果继续把 Android 默认实现风格和详细验证规则长期放在根 `AGENTS.md`，会让根规则越来越偏向 Android 专仓规则，不利于后续多子系统协作。

因此第一阶段需要先完成规则分层，而不是继续在根规则里堆细节。

---

## 4. 范围

本任务 In Scope：

- 收口根 `AGENTS.md`
- 新建 `app/AGENTS.md`
- 新增 Android 实现约束解释文档
- 保留并收缩 Skills 边界文档
- 做最小导航更新
- 重写本 task 与 handoff 记录

本任务 Out of Scope：

- Android 产品功能开发
- backend API 扩展
- 新建真实 Skill 实现
- 调整 docs 主结构
- 重写现有架构文档体系

---

## 5. 涉及文件

高概率涉及：

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/README.md`
- `docs/architecture/README.md`
- `docs/architecture/clients/android-client-implementation-constraints.md`
- `docs/how-to/README.md`
- `docs/how-to/operate/agent_skills_boundary_and_index.md`
- `docs/delivery/tasks/task_android_agent_guardrails_and_skills_boundary.md`
- `docs/delivery/handoffs/handoff_2026_04_23_android_agent_guardrails_and_skills_boundary.md`

参考文件：

- `docs/how-to/operate/developer_workflow_playbook.md`
- `docs/architecture/repository-layout.md`
- `docs/product/overview.md`
- `app/build.gradle.kts`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/OpenClawApp.kt`

---

## 6. 产出要求

至少应产出：

1. 一版分层后的规则结构
2. 一份 `app/AGENTS.md`
3. 一份 Android 实现约束解释文档
4. 一份收缩后的 Skills 边界文档
5. 对本次第一阶段落地的 task 与 handoff 记录

---

## 7. 验收标准

满足以下条件可认为完成：

1. 根 `AGENTS.md` 已去 Android 细则化
2. Android 详细规则已下沉到 `app/`
3. Android 默认实现风格已进入 `docs/architecture/clients/`
4. Skills 文档仍在，但不再被当作主入口
5. 没有顺手扩成产品开发任务或 docs 主结构重构

---

## 8. 推荐执行顺序

建议执行顺序：

1. 回顾当前 Android 工程结构与已有 workflow 文档
2. 调研最新官方 Android 架构 / 测试 / 模块化建议
3. 调研最新 OpenAI / Codex 关于 `AGENTS.md` 与 Skills 的公开说明
4. 重写根 `AGENTS.md`
5. 新建 `app/AGENTS.md`
6. 新增 Android 解释型架构文档
7. 收缩 Skills 边界文档
8. 做最小导航同步
9. 写 handoff 并补验证记录

---

## 9. 风险与注意事项

- 不要把本任务扩展为 Android 架构重写
- 不要把 Skills 提升为新的仓库事实源
- 不要静默改变产品方向或当前活跃开发任务
- 不要为了“未来可能需要”预创建 `backend/AGENTS.md` 或 iOS 规则文件

---

## 10. 下一步衔接

本任务完成后，推荐继续：

1. 如有需要，再拆独立 follow-up task 沉淀具体 Android 验证 Skill
2. 后续若 `backend/` 或 iOS 目录开始形成稳定子系统，再按同一模式做局部规则分层

---

## 11. 实际产出

本次已完成以下产出：

1. 重写根 `AGENTS.md`，把 Android 细则移出根规则
2. 新建 `app/AGENTS.md`
3. 新增 `docs/architecture/clients/android-client-implementation-constraints.md`
4. 收缩 `docs/how-to/operate/agent_skills_boundary_and_index.md`
5. 同步更新 `docs/README.md`、`docs/architecture/README.md` 与 `docs/how-to/README.md`
6. 重写本 task 与对应 handoff

---

## 12. 本次定稿边界

本次明确采用以下边界：

- 只做第一阶段规则分层，不进入 Android 功能开发
- `backend/AGENTS.md` 与未来 iOS 规则文件本次不创建
- Skills 只保留最小索引与接口说明，不直接创建 Skill 实现
- 不修改方向层文档
- 不改变当前 docs 主结构

---

## 13. 已做验证

本次已完成以下验证：

1. 对照当前 Android 工程结构复核规则是否贴合现实
2. 对照官方 Android 架构 / 测试 / 模块化文档复核约束方向
3. 对照官方 OpenAI / Codex 资料复核 `AGENTS.md` 与 Skills 的职责划分
4. 运行文档层校验命令确认 patch 无格式错误

---

## 14. 实际结果说明

当前仓库的第一阶段规则分层已经正式落地：

1. 根规则重新回到仓库级职责
2. Android 详细规则已经进入 `app/`
3. Android 默认实现风格已进入方案层文档
4. Skills 继续是增强层，而不是新的主工作流
