# Project Status

更新时间：2026-04-30

## 1. 文档定位

本文档是当前项目阶段状态的权威入口。它维护当前事实状态，不替代 PRD、ADR、roadmap 或 `_active.md`。

---

## 2. 当前阶段摘要

| Area | Status | Notes |
|---|---|---|
| V3 direction | `accepted / backend sandbox POC completed` | 当前主线已定为 Agent Sandbox-first Memory-native Sales Agent。 |
| V3 runtime / memory implementation | `poc_with_opt_in_persistence` | 已有 backend-only `/v3/sandbox` LangGraph + memory/action POC，并支持 opt-in DB persistence；正式跨 session memory / CRM schema 仍未冻结。 |
| V3 sandbox / working state | `poc_with_opt_in_persistence` | POC 中所有 agent 写入仍是 sandbox working state；DB store 保存 session-scoped snapshot/events，不冻结正式对象。 |
| Agent-maintained customer intelligence | `poc_draft_only / future direction` | POC 只维护 customer intelligence draft；自动建档、正式排序和打分仍未实现、不冻结 schema。 |
| V3 Web dual-entry direction | `lab_settings_trace_inspector_completed / workspace_not_started` | `/lab` 已有内部测试入口，支持 seed/reset/replay、Settings runtime config、fullscreen Trace Inspector，可观察 DB store、memory transitions 和完整 LangGraph debug trace；`/workspace` 用户雏形未实现，App 仍是长期主要入口。 |
| V2 workspace/kernel assets | `historical validated prototype` | Sales Workspace Kernel、Draft Review、Postgres persistence、chat-first prototype 可复用。 |
| V2.1 / V2.2 product direction | `superseded by V3 direction` | V2 文档保留为 historical / reference only。 |
| V1 demo baseline | `frozen` | V1 已冻结为 demo-ready release candidate / learning milestone。 |
| MVP / production SaaS | `not_started` | 不在当前默认实现范围。 |

当前解释：

> **V3 is the current product direction. A backend-only sandbox runtime POC now exists; broader V3 product implementation is not open.**

---

## 3. Current Capability Matrix

| Capability | Status | Evidence | Next Need |
|---|---|---|---|
| V3 Sandbox-first Memory-native Sales Agent direction | `accepted` | ADR-009、V3 PRD、V3 architecture entry。 | 单独开放后续 Web / persistence / product tasks。 |
| Self-editable cognitive memory | `poc_with_opt_in_persistence` | `task_2026_04_30_v3_sandbox_memory_persistence.md`。 | 继续观察 transition events，再决定 archival/cross-session memory。 |
| Sandbox workspace working state | `poc_with_opt_in_persistence` | `/v3/sandbox` POC + opt-in DB store。 | 不冻结 formal schema。 |
| Customer intelligence working state | `draft_poc_completed` | `/v3/sandbox` POC。 | 后续如需正式建档/排序/打分，另开 task。 |
| LangGraph / LangChain runtime | `poc_completed` | `/v3/sandbox` LangGraph loop + TokenHub smoke。 | 后续决定是否扩展 graph lifecycle。 |
| V3 Web Lab / Workspace prototype | `lab_settings_trace_inspector_completed` | `task_2026_04_30_v3_lab_settings_trace_inspector.md`。 | 后续可开放 `/workspace` task、trace playback 或 LangGraph Studio adapter spike。 |
| Backend infrastructure | `partial_poc_completed` | `/v3/sandbox` opt-in DB store 保存 session snapshot、trace/action events 和 memory transition events。 | 后续如需 production persistence / tenant / auth，另开 task。 |
| V2 Sales Workspace Kernel | `historical validated prototype` | Kernel docs、tests、API contract、Postgres chain。 | 仅作为历史资产，不是 V3 初期默认路径。 |
| V2 LLM runtime prototype | `historical reference` | explicit dev flag、fake-client tests、live eval。 | 不作为 V3 runtime contract。 |

---

## 4. 当前执行授权

当前执行状态以 `docs/delivery/tasks/_active.md` 为准。

当前口径：

- Current delivery package：暂无。
- Current task：`docs/delivery/tasks/task_2026_04_30_v3_lab_settings_trace_inspector.md`。
- Auto-continue：`no`。
- Next queued task：暂无 implementation task 自动开放。

---

## 5. 下一步候选

以下只是候选，不代表已开放执行：

1. **V3 workspace user prototype planning**
   - 将已验证的 memory / working state 信息架构转为用户可理解体验。
2. **V3 archival memory design**
   - 在 session-scoped persistence 基础上设计跨 session / retrieval 边界。
3. **V3 /lab trace playback**
   - 如需要更细粒度调试，再补 action/transition 时间线播放。
4. **V3 LangGraph Studio adapter spike**
   - 如需要官方 Studio 观察，再将 V3 sandbox graph 适配为 LangGraph Agent Server app。

---

## 6. 状态判断规则

普通 task / handoff 只能作为 evidence，不能自行声明产品阶段完成。

如果历史 V2 文档与 V3 PRD / ADR-009 / V3 architecture entry 冲突，以 V3 当前真相层为准。
