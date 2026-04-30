# ADR-009：V3 Memory-native Sales Agent Direction

- 文档状态：Accepted direction / implementation not started
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
- Product Sales Agent 允许维护和自编辑长期认知记忆。
- Backend / Sales Workspace Kernel 仍治理正式业务对象和正式业务承诺。

---

## 2. 原因

继续把新方向塞进 V2 会造成文档和实现口径混淆。V2 文档大量围绕 Sales Workspace Kernel、Draft Review、PatchDraft 和保守 formal writeback 展开，这些仍有价值，但会限制 V3 对长期认知记忆、自我修正和开放推断能力的探索。

将新方向命名为 V3，可以明确：

- V2 是已验证资产和历史基线。
- V3 是当前产品与 runtime 方向。
- 旧 V2 contract 不应反向限制 V3 memory runtime。

---

## 3. 边界

V3 runtime 可以维护开放认知 memory，但不能直接写正式业务对象。

一句话边界：

```text
V3 runtime memory 是开放认知层；backend formal objects 是正式业务承诺层。
```

正式写回仍包括：

- Product / lead direction formal revision。
- Candidate / contact / report 等正式对象。
- 对外承诺、导出、触达或自动动作。

这些必须经过 backend services / Sales Workspace Kernel 或后续明确的治理层。

---

## 4. 非目标

本 ADR 不冻结：

- memory table schema。
- LangGraph graph 节点。
- LangChain provider 代码。
- API request / response。
- Android UI contract。
- search / ContactPoint implementation。

---

## 5. 文档影响

V3 当前真相入口为：

- `docs/product/prd/ai_sales_assistant_v3_prd.md`
- `docs/architecture/v3/memory-native-sales-agent.md`
- `docs/product/project_status.md`
- `docs/delivery/tasks/_active.md`

V2 文档保留为 historical validated prototype / reference only。
