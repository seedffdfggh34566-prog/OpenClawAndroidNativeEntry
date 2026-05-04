# AI 销售助手 V3 PRD

- 文档状态：Draft v0.1 / direction baseline
- 更新日期：2026-04-30
- 阶段定位：V3 Agent Sandbox-first / Memory-native Sales Agent 方向定义；backend sandbox runtime POC completed，正式产品实现未完成
- 关联文档：
  - `docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`
  - `docs/architecture/v3/memory-native-sales-agent.md`
  - `docs/architecture/v3/web-dual-entry-prototype.md`
  - `docs/product/project_status.md`

---

## 1. V3 北极星

V3 的产品北极星是：

> **Agent Sandbox-first Memory-native Sales Agent：Product Sales Agent 先在 sandbox working state 中自主维护 memory、workspace state 和 customer intelligence；backend 初期只作为 runtime host、storage、trace 和 API 基础设施。**

V3 不再把 Product Sales Agent 主要定义为 `WorkspacePatchDraft` 生成器，也不再把“只允许确认事实进入记忆”作为默认策略。V3 第一阶段不以 backend formal governance 作为实现前提，而是先验证 agent 是否能开放地形成、修正和使用长期认知状态。

---

## 2. 核心能力

V3 首批只定义方向能力，不冻结 schema 或 API：

- Product Sales Agent 可以自编辑长期认知记忆。
- 记忆可以包含用户原话、推断、假设、策略、纠错和已废弃信息。
- 记忆应能标记为 `observed`、`inferred`、`hypothesis`、`confirmed`、`rejected`、`superseded`。
- Product Sales Agent 可以维护 sandbox workspace working state 和 customer intelligence working state。
- 未来可演进为 agent-maintained customer intelligence system，包括自动建档、候选客户排序和打分。
- LangGraph / LangChain 是优先 runtime 路线。
- Letta-style memory blocks、archival memory、memory tools 和 compaction 是主要参考模式。
- Backend 初期定位为 runtime host、storage、trace 和 API surface，不作为业务建档者或第一阶段裁决者。
- Web 可以作为 V3 双入口产品雏形：`/lab` 面向内部开发和产品测试，`/workspace` 面向真实销售用户体验验证；App 仍是长期主要用户入口。

---

## 3. 非目标

V3 当前不代表：

- 已实现完整 LangGraph production runtime。
- 已接入 Letta server。
- 已冻结 memory database schema。
- 已冻结 customer intelligence schema、候选客户 scoring schema 或自动建档模型。
- 已冻结 API contract。
- 已启动 backend formal governance / Sales Workspace Kernel 作为 V3 默认路径。
- 已启动 Android 大改。
- 已启动正式 Web SaaS、登录、多租户或生产部署。
- 已进入 V2.2 search / ContactPoint implementation。
- 已成为 MVP 或 production-ready SaaS。

---

## 4. 成功标准草案

V3 direction POC 后续成功应至少证明：

- 多轮对话后，Product Sales Agent 能保留并使用长期 memory。
- Product Sales Agent 能通过工具更新、纠正、废弃自己的 memory。
- 推断和假设可以进入 sandbox working state，并能被用户纠正或废弃。
- 用户纠错会影响后续回答和策略。
- Agent 可以维护早期 customer intelligence working state，包括候选客户线索、排序理由和评分草案。
- 腾讯云模型 API 可通过 LangChain 或 OpenClaw LLM Gateway 稳定调用。
- Web `/lab` 能支持人工测试和 Dev Agent 自动化验证 memory、working state、agent actions、trace 和 replay。
- Web `/workspace` 能验证真实销售用户是否理解 agent 建议、memory 摘要和确认流程。

这些标准只是后续 POC 的方向，不代表当前实现已完成。

---

## 5. 与 V1 / V2 的关系

V1 是 demo-ready learning baseline。V2 是 Sales Workspace / Kernel / Draft Review / persistence 的 validated prototype asset。

V3 可以参考 V2 的 Sales Workspace 资产，但当前默认开发方向转为 sandbox-first memory-native Sales Agent。旧 V2 文档保留为 historical validated prototype / reference only；V2 Kernel、Draft Review、`WorkspacePatchDraft` 和 formal writeback 不再作为 V3 第一阶段默认实现路径。
