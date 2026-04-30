# ADR-008：V2 LangGraph + Letta-style Memory Direction

- 文档状态：Transition record / superseded by ADR-009
- 决策日期：2026-04-29
- 关联文档：
  - `docs/product/prd/ai_sales_assistant_v2_prd.md`
  - `docs/architecture/runtime/langgraph-letta-style-sales-agent-memory.md`
  - `docs/architecture/runtime/langgraph-runtime-architecture.md`
  - `docs/architecture/runtime/v2-1-llm-runtime-boundary.md`

---

## 1. 决策

2026-04-29 更新：本文档保留为从 V2 过渡到 V3 的方向记录。当前正式方向以 `docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md` 为准。

V2 Product Sales Agent runtime 的下一阶段方向调整为：

> **优先用 LangGraph / LangChain 建设自研 runtime，同时借鉴 Letta 的可自编辑记忆模式。**

本 ADR 只固定方向，不冻结字段、表结构、API、graph 节点或具体依赖版本。

---

## 2. 核心原则

1. Product Sales Agent 应允许自编辑长期 runtime memory。
2. Memory 可以包含事实、推断、假设、策略、纠错和已废弃信息。
3. 对未确认内容的治理方式应优先是标记、解释、审阅和降级，而不是提前禁止进入记忆。
4. 正式业务对象仍由 backend services / Sales Workspace Kernel 写回和裁决。

一句话边界：

```text
Runtime memory 是开放认知层；formal business objects 才是正式业务承诺层。
```

---

## 3. 技术取舍

当前不优先直接接入 Letta server 作为产品 runtime。原因是本项目仍需要保留后续自研 kernel、backend object governance 和 Android-first 控制入口。

当前优先：

- 使用 LangGraph / LangChain 获得更高 runtime 自由度。
- 借鉴 Letta 的 memory blocks、archival memory、memory tools 和 compaction 思路。
- 让 OpenClaw backend 继续持有正式业务对象和写回边界。

---

## 4. 非目标

本决策不代表：

- 已经实现 LangGraph runtime。
- 已经接入 Letta。
- 已经冻结 memory schema。
- 已经引入新的数据库迁移。
- 已经改变 V2.2 search / ContactPoint 边界。
- 已经允许 runtime 绕过 Draft Review 或 Sales Workspace Kernel。

---

## 5. 后续

后续实现必须另开 delivery task。优先验证：

- LangChain 调用腾讯云 API 的最小路径。
- Product Sales Agent 是否能通过工具自编辑 memory。
- 自编辑 memory 是否能影响后续多轮回答。
- 正式对象写回是否仍经过 backend gate。
