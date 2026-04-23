# Task：后端 Agent 技术栈规则与 Skill 规格补强

更新时间：2026-04-23

## 1. 任务定位

- 任务名称：后端 Agent 技术栈规则与 Skill 规格补强
- 建议路径：`docs/delivery/tasks/task_backend_agent_stack_guardrails_and_skills.md`
- 当前状态：`done`
- 优先级：P1

本任务用于在不进入后端功能扩展的前提下，为当前仓库补齐后端作用域规则、后端 agent 技术栈方案层说明，以及 repo 内 backend skill specs。

---

## 2. 任务目标

完成一组后端仓库级补强产物，至少满足：

- `backend/` 有独立局部规则入口
- 仓库内存在对 `LangGraph / MCP / Pydantic / Langfuse / Postgres / pgvector / MCP Toolbox for Databases` 的清晰分阶段结论
- backend skill specs 与当前仓库现实一致
- 不把这些结论误写成“现在已经全部实现”

---

## 3. 当前背景

当前仓库已经完成：

- 最小正式 backend 落地
- Android 侧局部规则与 skill specs
- Android Knowledge Base / Android CLI 边界澄清

当前尚未完成：

- backend 作用域局部规则
- backend-specific skill specs
- 后端 agent 技术栈的分阶段 adoption 方案

因此，当前更合理的 follow-up 不是直接平台化实现，而是先把后端 guardrails 与 adoption 路线固定下来。

---

## 4. 范围

本任务 In Scope：

- 新增 `backend/AGENTS.md`
- 新增后端 agent 技术栈方案层文档
- 新增 backend skill specs 与 rollout order
- 同步最小 docs 导航与索引
- 新增本任务对应 handoff

本任务 Out of Scope：

- 修改 backend 产品代码
- 引入 `LangGraph`
- 引入 `MCP`
- 接入 `Langfuse`
- 执行 `SQLite -> Postgres` 迁移
- 引入 `pgvector`
- 接入 `MCP Toolbox for Databases`

---

## 5. 涉及文件

高概率涉及：

- `backend/AGENTS.md`
- `docs/architecture/backend/*`
- `docs/how-to/operate/skills/*`
- `docs/how-to/operate/agent_skills_boundary_and_index.md`
- `docs/delivery/tasks/task_backend_agent_stack_guardrails_and_skills.md`
- `docs/delivery/handoffs/` 下对应 handoff

参考文件：

- `backend/README.md`
- `docs/architecture/system-context.md`
- `docs/how-to/operate/codex_backend_first_workflow.md`
- `docs/delivery/tasks/task_v1_backend_minimum_implementation.md`

---

## 6. 产出要求

至少应产出：

1. `backend/AGENTS.md`
2. 一份后端 agent 技术栈分阶段方案文档
3. 一组 backend skill specs
4. 一份 backend skill rollout order
5. 对应 task 与 handoff 收口

---

## 7. 验收标准

满足以下条件可认为完成：

1. `backend/` 已有独立规则入口
2. 后端 stack 结论已明确“哪些该用、哪些暂不立刻上”
3. backend skill specs 与当前仓库现实一致
4. 本次没有把 follow-up 技术决策冒充成已实现能力

---

## 8. 推荐执行顺序

建议执行顺序：

1. 复核当前 backend 现实
2. 编写 `backend/AGENTS.md`
3. 编写后端 stack 分阶段 adoption 文档
4. 编写 backend skill specs 与 rollout order
5. 同步索引与最小导航
6. 补 handoff 与文档层验证

---

## 9. 风险与注意事项

- 不要把后端最小实现 task 继续扩写成平台化 task
- 不要把 `LangGraph / MCP / Postgres / Langfuse` 直接写成当前已启用
- 不要因为需要 future direction，就修改 backend 产品代码

---

## 10. 下一步衔接

本任务完成后，推荐继续：

1. 视正式优先级推进 `task_v1_android_minimum_real_backend_integration.md`
2. 后续若要引入 `Postgres`、`LangGraph`、`MCP` 或 `Langfuse`，分别新建 follow-up task

---

## 11. 实际产出

本次已完成以下产出：

1. 新增 `backend/AGENTS.md`
2. 新增后端 agent 技术栈与分阶段落地方案文档
3. 新增 5 份 backend skill specs
4. 新增 backend skill rollout order
5. 同步 skill 索引与最小文档导航
6. 新增对应 handoff

---

## 12. 本次定稿边界

本次明确采用以下边界：

- 规则层与方案层补强优先
- 不引入新的后端功能实现
- `Pydantic` 继续作为当前 schema 核心
- `LangGraph` 仅被定位为未来 runtime/orchestration 层候选
- `MCP` 仅被定位为未来工具协议边界
- `Langfuse` 被记录为当前更合适的 observability 候选
- `Postgres` 是下一阶段推荐基线，`pgvector` 为按需能力
- `MCP Toolbox for Databases` 只被定位为开发/运维增强或最小权限 custom tools 候选

---

## 13. 已做验证

本次已完成以下验证：

1. 运行文档与现状对齐检查
2. 运行 `git diff --check`
3. 运行 `find backend -name AGENTS.md -print`
4. 运行 `rg` 检查 backend skill 索引与后端 stack 方案文档已接入

---

## 14. 实际结果说明

当前本任务已满足原验收目标：

1. 后端已有独立 agent 规则入口
2. 后端 agent 技术栈结论已收口为 repo 内方案层文档
3. backend skill specs 已形成可继续实现的规格层
4. 当前仓库仍保持“先规则与边界，后分步落地”的节奏
