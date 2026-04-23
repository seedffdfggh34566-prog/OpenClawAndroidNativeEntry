# 阶段性交接：后端 Agent 技术栈规则与 Skill 规格补强

更新时间：2026-04-23

## 1. 本次改了什么

- 新增 `backend/AGENTS.md`，把 backend 作用域规则单独收口
- 新增 `docs/architecture/backend/backend-agent-stack-phased-adoption.md`
- 新增 5 份 backend skill specs 和 `backend-rollout-order.md`
- 更新 backend / architecture / skills 相关索引文档
- 新增本次 task 文档并收口为 `done`

---

## 2. 为什么这么定

- 当前 backend 仍处于最小正式实现阶段，先补 rules / skills / phased adoption 比直接平台化更稳
- `Pydantic`、`LangGraph`、`MCP`、`Langfuse`、`Postgres`、`pgvector`、`MCP Toolbox for Databases` 需要明确“该不该用”和“什么时候用”
- 当前仓库已经在 Android 侧完成局部规则与 skill specs，backend 侧补齐后，整体工作流会更对称

---

## 3. 本次验证了什么

1. 文档内容与当前 backend 现实保持一致：仍是 `FastAPI + Pydantic + SQLAlchemy + SQLite + stub runtime`
2. backend 局部规则、backend skill specs、backend adoption 文档之间的引用链已补齐
3. 文档层校验 `git diff --check` 已通过

---

## 4. 已知限制

- 本次没有引入任何新的 backend 功能实现
- 本次没有接入 `LangGraph`、`MCP`、`Langfuse`、`Postgres`、`pgvector`
- backend skill specs 目前仍是 repo 内规格层，不是真实安装的 Codex skills

---

## 5. 推荐下一步

1. 正式开发仍优先参考 `docs/delivery/tasks/_active.md` 中的当前推荐任务
2. 若后续要引入 `Postgres`、`LangGraph`、`MCP` 或 observability，再分别开 follow-up task
3. 若 backend 相关 thread 开始高频重复，可优先把 `backend-local-verify` 与 `backend-runtime-boundary-guard` 落成真实 skills
