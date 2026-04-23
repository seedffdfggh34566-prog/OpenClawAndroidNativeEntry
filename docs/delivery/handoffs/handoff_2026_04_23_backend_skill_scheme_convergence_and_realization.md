# 阶段性交接：后端 Skill 收敛与真实 Skill 落地

更新时间：2026-04-23

## 1. 本次改了什么

- 新增 `backend-task-bootstrap`，把 backend task / validation / handoff 模板能力补齐
- 将 `backend_local_runbook` 并入 `backend-local-verify`
- 将 `api_contract_change` 并入 `backend-api-change-check`
- 将 `schema_and_migration` 并入 `backend-db-risk-check`
- 将轻量 `agent_run_lifecycle` 要求并入 `backend-runtime-boundary-guard`
- 在 `docs/how-to/operate/skills-src/` 下新增 6 个真实 backend skill 源码目录
- 新增 `scripts/sync_codex_skills.py`，用于同步安装到本机 Codex skills

---

## 2. 现在的正式 backend skill 集

当前正式 backend skills 固定为：

1. `backend-task-bootstrap`
2. `backend-local-verify`
3. `backend-api-change-check`
4. `backend-db-risk-check`
5. `backend-runtime-boundary-guard`
6. `backend-contract-sync`

未来候选仍保留在 follow-up 层，不在本次落地：

- `agent_trace_and_eval`
- `tool_registration_mcp`
- `human_review_gate`
- `agent_run_lifecycle`
- `structured_output_validation`

---

## 3. 本次验证了什么

1. 6 个真实 skill 目录都通过了基础 `quick_validate.py`
2. `scripts/sync_codex_skills.py` 已把 6 个 backend skills 同步到 `${CODEX_HOME:-$HOME/.codex}/skills/`
3. `backend-local-verify` 的 bundled script 已做真实 smoke
4. 文档层校验 `git diff --check` 已通过

---

## 4. 已知限制

- 当前这些 skills 主要还是 workflow guardrails，不是自动化平台
- `backend-local-verify` 之外，其余 5 个仍以文本型 skill 为主
- 还没有为 `Langfuse`、`MCP`、`LangGraph`、`Postgres cutover` 单独落 skill

---

## 5. 推荐下一步

1. 后续 backend threads 先实际使用这 6 个 skills，观察触发频率和边界是否稳定
2. 如 `backend-task-bootstrap` 高频使用，再考虑给它补 task/handoff 模板资源
3. 只有在 `Langfuse`、`MCP`、`HITL` 等能力真正进入正式 task 后，再新增对应 skill
