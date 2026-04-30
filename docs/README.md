# 文档导航

更新时间：2026-04-30

## 1. 当前主线

当前项目主线正式切换为：

> **V3 Memory-native Sales Agent**

V3 的一句话方向：

> Product Sales Agent 拥有可自编辑认知记忆，基于 LangGraph / LangChain 自研 runtime 持续经营 Sales Workspace；backend 只在正式业务承诺处做治理。

当前 V3 是 accepted direction / implementation not started。本文档只提供当前入口，不代表 V3 implementation、MVP 或 production-ready 已完成。

---

## 2. 当前必读入口

进入仓库后优先阅读：

1. 根目录 `AGENTS.md`
2. `docs/product/project_status.md`
3. `docs/product/overview.md`
4. `docs/product/prd/ai_sales_assistant_v3_prd.md`
5. `docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`
6. `docs/architecture/v3/memory-native-sales-agent.md`
7. `docs/architecture/v3/web-dual-entry-prototype.md`
8. `docs/delivery/tasks/_active.md`
9. 当前 task / handoff

V2 历史资产可按需参考，但不再作为当前默认开发方向。

---

## 3. 当前真相层

当前真相集中在少数文件中：

- `docs/product/project_status.md`
- `docs/product/overview.md`
- `docs/product/prd/ai_sales_assistant_v3_prd.md`
- `docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`
- `docs/architecture/v3/memory-native-sales-agent.md`
- `docs/architecture/v3/web-dual-entry-prototype.md`
- `docs/delivery/tasks/_active.md`

这些文件优先级高于历史 task、handoff、V2 runtime contract 和旧 research evidence。

---

## 4. 历史资产

V1：

- demo-ready release candidate / learning milestone。
- 可作为 ProductProfile、LeadAnalysis、report、TokenHub 接入和 Android control entry 的参考。

V2：

- Sales Workspace / Kernel / Draft Review / Postgres persistence / chat-first prototype 的 validated prototype asset。
- 相关文档保留为 historical validated prototype / reference only。
- V2.1 / V2.2 不再是当前默认开发方向，除非后续 task 明确要求回到某个旧能力。

---

## 5. 文档目录

- `product/`：当前产品方向、PRD、状态和 roadmap。
- `adr/`：关键方向和架构决策。
- `architecture/`：V3 架构入口以及历史 workspace/runtime/data 参考。
- `reference/`：API contract、examples、schemas、evals。
- `delivery/`：当前 task 入口、历史 task、handoff 和 evidence。
- `how-to/`：运行、协作、调试和操作手册。
- `archive/`：历史 OpenClaw 资料。

---

## 6. 当前边界

- 不自动启动 V3 implementation。
- 不自动接入 LangGraph / LangChain 代码。
- 不自动新增 DB schema / migration。
- 不自动改 Android UI。
- 不自动 scaffold Web 工程或启动 production Web SaaS。
- 不自动进入 search / ContactPoint / CRM / outreach。
- V3 runtime memory 可以开放；formal business objects 仍由 backend governance 裁决。
