# LangGraph + Letta-style Sales Agent Memory Direction

更新时间：2026-04-29

## 1. 文档定位

本文档记录一次轻量方向调整：

> **先用 LangGraph / LangChain 建设自研 Product Sales Agent runtime，并借鉴 Letta 的可自编辑记忆模式。**

本文档不是 implementation spec，不冻结数据库 schema、API shape、graph 节点、工具参数或迁移计划。

2026-04-29 更新：当前新方向已正式命名为 V3 Memory-native Sales Agent。本文档作为过渡参考保留，当前 V3 入口以 `docs/architecture/v3/memory-native-sales-agent.md` 和 `docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md` 为准。

---

## 2. 为什么调整

最近的多轮对话和测试暴露出一个问题：如果系统一开始只允许“已确认事实”进入记忆，Product Sales Agent 会过早失去判断、联想、假设、策略沉淀和自我修正能力。

新的方向是：

- 先允许 Product Sales Agent 形成更开放的 runtime memory。
- 允许 memory 中存在推断、假设、策略、纠错和被废弃的信息。
- 通过标记和后续治理处理幻觉，而不是一开始就禁止模型形成认知。
- 只在正式业务对象写回、对外承诺、联系方式、报告和自动动作处保持严格 gate。

也就是说：

```text
Runtime memory 可以开放。
Formal business objects 才需要严格裁决。
```

---

## 3. 推荐方向

当前推荐：

```text
Android
  -> OpenClaw Backend
    -> LangGraph / LangChain Sales Agent Runtime
      -> Tencent Cloud API 或 OpenClaw LLM Gateway
      -> Memory tools
      -> WorkspacePatchDraft
    -> Backend services / Sales Workspace Kernel
```

核心取舍：

- **LangGraph / LangChain**：作为第一实施路径，承担 runtime orchestration、model/tool calling 和后续可扩展执行图。
- **Letta**：暂不优先作为 server runtime 接入；优先借鉴它的 memory blocks、archival memory、tool-based self-edit memory 和 compaction 思路。
- **OpenClaw Backend**：继续负责正式业务对象、审阅、写回和可追溯记录。

---

## 4. Memory 核心思路

Product Sales Agent memory 不应只保存确认事实。第一阶段只需要记住这些核心概念：

- **Memory blocks**：长期注入上下文的核心记忆，例如用户偏好、当前产品理解、销售策略、待纠错信息。
- **Archival memory**：不必每轮都注入，但可被搜索召回的长期材料。
- **Agent self-edit memory**：Product Sales Agent 可以通过受控工具更新自己的 runtime memory。
- **Status labels**：记忆可以标记为 `observed`、`inferred`、`hypothesis`、`confirmed`、`rejected`、`superseded`。

这些标签用于治理和解释，不用于禁止 agent 形成认知。

---

## 5. 边界

Product Sales Agent runtime 可以：

- 维护自编辑 runtime memory。
- 记录推断、假设、策略和未确认判断。
- 基于记忆生成 assistant response。
- 提出 `WorkspacePatchDraft`。

Product Sales Agent runtime 不应直接：

- 修改正式 `SalesWorkspace` 对象。
- 将 hypothesis 当成 confirmed fact 写入正式对象。
- 写入联系方式、候选客户、正式报告或对外动作。
- 把 LangGraph checkpoint、SDK session 或聊天历史当成唯一业务主存。

正式写回仍由 backend services / Sales Workspace Kernel 裁决。

---

## 6. 后续实施提醒

后续如果进入实现，应另开 task，并最小化验证：

- LangChain / Tencent Cloud API 接入方式。
- memory block 的最小存储方式。
- Product Sales Agent memory tools。
- `WorkspacePatchDraft` 与 cognitive memory update 的关系。
- 多轮对话中 memory 是否真实影响下一轮输出。

本方向文档只记录“往哪里走”，不提前冻结“具体怎么做”。
