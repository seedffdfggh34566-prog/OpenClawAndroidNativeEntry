# 项目总览

更新时间：2026-04-30

## 1. 当前项目是什么

当前仓库主线为：

> **AI 销售助手 App：V3 Memory-native Sales Agent**

V3 不是 V2.1 的小修补。它将产品方向从 “Sales Workspace + PatchDraft-driven runtime” 重基线为：

> **Product Sales Agent 拥有可自编辑认知记忆，基于 LangGraph / LangChain 自研 runtime 持续经营 Sales Workspace；backend 只在正式业务承诺处做治理。**

当前 V3 处于 accepted direction / implementation not started。

---

## 2. V1 / V2 定位

V1 已冻结为 demo-ready release candidate / learning milestone。

V2 已形成重要历史资产：

- Sales Workspace Kernel。
- WorkspacePatch / Draft Review。
- Postgres / Alembic persistence chain。
- chat-first backend prototype。
- Tencent TokenHub explicit-flag LLM runtime prototype。
- Android control entry 与 device validation evidence。

这些资产可被 V3 复用，但 V2 文档不再作为当前默认开发方向。

---

## 3. V3 北极星

V3 的核心不是一次性报告，也不是只生成 `WorkspacePatchDraft`。

V3 的核心是：

- Product Sales Agent 长期理解用户、产品、市场假设和销售策略。
- Memory 可以包含 observed / inferred / hypothesis / confirmed / rejected / superseded。
- Agent 可以自编辑 memory，并在用户纠错后修正或废弃旧记忆。
- LangGraph / LangChain 是优先 runtime 路线。
- Letta-style memory blocks、archival memory、memory tools 和 compaction 是主要参考。
- Backend / Sales Workspace Kernel 在正式对象、报告、联系方式、导出和对外动作处做治理。
- Web 可以作为 V3 双入口原型：内部 `/lab` 用于测试 runtime / memory，用户 `/workspace` 用于验证真实销售工作流；App 仍是长期主要入口。

---

## 4. 当前不做

当前不做：

- V3 implementation。
- MVP / production SaaS。
- production Web SaaS / 登录 / 多租户 / 正式部署。
- 完整 CRM。
- 自动邮件 / 短信 / 企微 / 电话触达。
- 批量联系人抓取或导出。
- 大规模爬虫系统。
- 未经 task 开放的 DB schema / migration。
- 未经 task 开放的 Android 大改。

---

## 5. 当前入口

当前方向入口：

- `docs/product/prd/ai_sales_assistant_v3_prd.md`
- `docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`
- `docs/architecture/v3/memory-native-sales-agent.md`
- `docs/architecture/v3/web-dual-entry-prototype.md`
- `docs/product/project_status.md`
- `docs/delivery/tasks/_active.md`

历史 V2 入口仍可用于查证：

- `docs/product/prd/ai_sales_assistant_v2_prd.md`
- `docs/adr/ADR-006-v2-conversational-sales-agent-baseline.md`
- `docs/architecture/workspace/`
- `docs/architecture/runtime/`

历史 V2 文档是 reference only，不应覆盖 V3 当前方向。
