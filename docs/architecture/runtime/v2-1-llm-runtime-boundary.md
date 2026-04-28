# V2.1 LLM Runtime Boundary

更新时间：2026-04-28

## 1. Purpose

V2.1 允许真实 LLM 参与 chat-first Product Sales Agent turn。

本边界的核心原则是：

> LLM 是 Runtime execution layer，不是 formal workspace truth layer。

LLM 可以帮助理解用户输入、生成追问、解释当前 workspace，并提出 `WorkspacePatchDraft`。正式业务对象仍只能由 backend Draft Review 和 Sales Workspace Kernel 写入。

## 2. Runtime Responsibilities

Tencent TokenHub LLM runtime 可以产出：

- assistant `ConversationMessage` draft。
- 3 到 5 个中文 clarifying questions。
- workspace explanation。
- `WorkspacePatchDraft`，用于产品理解或获客方向更新。
- runtime metadata，例如 provider、model、prompt version、token usage 和 source refs。

Runtime 不可以：

- 直接修改 `SalesWorkspace`。
- 直接写 `ProductProfileRevision` 或 `LeadDirectionVersion`。
- 直接写 `RankingBoard`、Markdown projection 或 ContextPack。
- 跳过 Draft Review。
- 生成 V2.2 search / ContactPoint / CRM formal objects。

## 3. Writeback Boundary

LLM output 的正式写回路径必须保持：

```text
ConversationMessage
-> AgentRun
-> ContextPack
-> Tencent TokenHub LLM Runtime
-> WorkspacePatchDraft
-> WorkspacePatchDraftReview
-> human accept / apply
-> WorkspacePatch
-> Sales Workspace Kernel
-> ProductProfileRevision / LeadDirectionVersion
```

失败路径必须不 mutate workspace。

## 4. Runtime Mode

V2.1 保留 deterministic runtime 作为默认模式。真实 LLM 通过显式 dev flag 启用：

```text
OPENCLAW_BACKEND_SALES_AGENT_RUNTIME_MODE=llm
```

默认值保持 `deterministic`，避免本地 demo、现有 tests 和 Android prototype 被真实 LLM 可用性阻断。

## 5. Non-goals

本阶段不引入：

- formal LangGraph graph。
- durable checkpoint / resume lifecycle。
- V2.2 evidence / search / ContactPoint。
- CRM 或自动触达。
- Android 新 UI。
- DB schema migration。

如果后续要进入正式 LangGraph，应创建独立 task，并重新定义 runtime lifecycle、state checkpoint、retry、human interrupt 和 observability 边界。
