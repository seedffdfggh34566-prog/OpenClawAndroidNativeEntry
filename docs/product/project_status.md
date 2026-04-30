# Project Status

更新时间：2026-04-30

## 1. 文档定位

本文档是当前项目阶段状态的权威入口。它维护当前事实状态，不替代 PRD、ADR、roadmap 或 `_active.md`。

---

## 2. 当前阶段摘要

| Area | Status | Notes |
|---|---|---|
| V3 direction | `accepted / implementation not started` | 当前主线已定为 Agent Sandbox-first Memory-native Sales Agent。 |
| V3 runtime / memory implementation | `not_started` | LangGraph / LangChain、memory tools、schema、API 均未实现。 |
| V3 sandbox / working state | `planned` | 第一阶段所有 agent 写入默认是 sandbox working state，不冻结正式对象。 |
| Agent-maintained customer intelligence | `planned / future direction` | 未来允许 agent 自动建档、候选客户排序和打分；当前不实现、不冻结 schema。 |
| V3 Web dual-entry direction | `accepted / implementation not started` | Web 可作为 `/lab` 内部测试入口和 `/workspace` 用户雏形；App 仍是长期主要入口。 |
| V2 workspace/kernel assets | `historical validated prototype` | Sales Workspace Kernel、Draft Review、Postgres persistence、chat-first prototype 可复用。 |
| V2.1 / V2.2 product direction | `superseded by V3 direction` | V2 文档保留为 historical / reference only。 |
| V1 demo baseline | `frozen` | V1 已冻结为 demo-ready release candidate / learning milestone。 |
| MVP / production SaaS | `not_started` | 不在当前默认实现范围。 |

当前解释：

> **V3 is the current product direction. It is accepted as direction only; implementation is not open.**

---

## 3. Current Capability Matrix

| Capability | Status | Evidence | Next Need |
|---|---|---|---|
| V3 Sandbox-first Memory-native Sales Agent direction | `accepted` | ADR-009、V3 PRD、V3 architecture entry。 | 单独开放 runtime POC task。 |
| Self-editable cognitive memory | `planned` | V3 docs define direction only。 | 设计最小 memory tools / storage。 |
| Sandbox workspace working state | `planned` | V3 docs define direction only。 | POC 时定义最小 working state，不冻结 formal schema。 |
| Customer intelligence working state | `planned` | V3 docs define future direction。 | POC 时验证 agent 自动维护候选客户理由和评分草案。 |
| LangGraph / LangChain runtime | `planned` | ADR-009 direction。 | 验证腾讯云 API 调用和 tool loop。 |
| V3 Web Lab / Workspace prototype | `planned` | `docs/architecture/v3/web-dual-entry-prototype.md`。 | 单独开放 Web scaffold / Playwright task。 |
| Backend infrastructure | `planned` | V3 docs define backend as runtime host / storage / trace / API。 | 单独开放 backend infrastructure task。 |
| V2 Sales Workspace Kernel | `historical validated prototype` | Kernel docs、tests、API contract、Postgres chain。 | 仅作为历史资产，不是 V3 初期默认路径。 |
| V2 LLM runtime prototype | `historical reference` | explicit dev flag、fake-client tests、live eval。 | 不作为 V3 runtime contract。 |

---

## 4. 当前执行授权

当前执行状态以 `docs/delivery/tasks/_active.md` 为准。

当前口径：

- Current delivery package：暂无。
- Current task：`docs/delivery/tasks/task_2026_04_30_v3_sandbox_first_docs_rebaseline.md`。
- Auto-continue：`no`。
- Next queued task：暂无 implementation task 自动开放。

---

## 5. 下一步候选

以下只是候选，不代表已开放执行：

1. **V3 runtime POC planning**
   - LangChain / Tencent API 或 OpenClaw LLM Gateway。
   - Product Sales Agent memory tools。
   - Sandbox working state。
   - Customer intelligence working state。
2. **V3 Web dual-entry scaffold planning**
   - 单个 `web/` 工程。
   - `/lab` 内部测试入口。
   - `/workspace` 销售用户体验雏形。
   - Playwright 验证链路。
3. **V3 memory model design**
   - 只在 POC 前定义最小 memory / working state，不提前冻结完整 schema。

---

## 6. 状态判断规则

普通 task / handoff 只能作为 evidence，不能自行声明产品阶段完成。

如果历史 V2 文档与 V3 PRD / ADR-009 / V3 architecture entry 冲突，以 V3 当前真相层为准。
