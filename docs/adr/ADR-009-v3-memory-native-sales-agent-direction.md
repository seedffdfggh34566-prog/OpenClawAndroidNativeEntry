# ADR-009：V3 Memory-native Sales Agent Direction

- 文档状态：Accepted direction / implementation not started / sandbox-first update
- 决策日期：2026-04-29
- 关联文档：
  - `docs/product/prd/ai_sales_assistant_v3_prd.md`
  - `docs/architecture/v3/memory-native-sales-agent.md`
  - `docs/adr/ADR-008-v2-langgraph-letta-style-memory-direction.md`

---

## 1. 决策

项目当前新方向正式命名为 **V3 Memory-native Sales Agent**。

V3 采用以下方向：

- LangGraph / LangChain 作为优先自研 runtime 路线。
- Letta-style memory blocks、archival memory、memory tools 和 compaction 作为记忆设计参考。
- Product Sales Agent 允许维护和自编辑长期认知记忆、workspace working state 和 customer intelligence working state。
- V3 初期采用 Agent Sandbox-first：backend 作为 runtime host、storage、trace 和 API 基础设施，不作为业务建档者或第一阶段裁决者。

---

## 2. 原因

继续把新方向塞进 V2 会造成文档和实现口径混淆。V2 文档大量围绕 Sales Workspace Kernel、Draft Review、PatchDraft 和保守 formal writeback 展开，这些仍有价值，但会限制 V3 对长期认知记忆、自我修正、开放推断和 agent 自动建档能力的探索。

将新方向命名为 V3，可以明确：

- V2 是已验证资产和历史基线。
- V3 是当前产品与 runtime 方向。
- 旧 V2 contract 不应反向限制 V3 memory runtime。

---

## 3. 边界

V3 runtime 可以维护开放认知 memory、workspace working state 和 customer intelligence working state。

一句话边界：

```text
V3 初期所有 agent 写入默认是 sandbox working state；backend 是基础设施，不是业务裁决层。
```

V3 第一阶段不冻结：

- formal object schema。
- `WorkspacePatchDraft` / Draft Review / Sales Workspace Kernel 默认路径。
- customer intelligence schema。
- 候选客户排序 / 打分字段。
- CRM 写入、外部触达、不可逆导出。

未来可以演进为 agent-maintained customer intelligence system，由 Product Sales Agent 自动维护客户档案、候选客户池、排序、打分和推荐理由。当前只保留方向，不实现、不冻结 schema。

---

## 4. 非目标

本 ADR 不冻结：

- memory table schema。
- LangGraph graph 节点。
- LangChain provider 代码。
- API request / response。
- Android UI contract。
- search / ContactPoint implementation。
- backend formal governance / Sales Workspace Kernel 作为 V3 默认实现前提。

---

## 5. 文档影响

V3 当前真相入口为：

- `docs/product/prd/ai_sales_assistant_v3_prd.md`
- `docs/architecture/v3/memory-native-sales-agent.md`
- `docs/product/project_status.md`
- `docs/delivery/tasks/_active.md`

V2 文档保留为 historical validated prototype / reference only。
