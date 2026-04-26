# Dev Agent 与 Product Sales Agent 术语边界 Runbook

更新时间：2026-04-26

## 1. 文档定位

本文档给人工开发者和后续开发协作线程使用。

它用于区分：

- Codex / Claude Code 这类开发协作工具
- 产品中的 AI 销售助手
- 后端 runtime / LangGraph 执行层

本文档不是产品 PRD，不定义 Sales Agent 的功能范围，也不替代 `AGENTS.md`、`docs/README.md`、ADR 或 task 文档。

---

## 2. 三类 agent 边界

### 2.0 Canonical Naming

后续新增或更新文档时，优先使用以下命名：

| 层级 | 推荐术语 | 含义 |
|---|---|---|
| 开发协作层 | `Dev Agent` / `Execution Agent` / `开发 agent` / `执行 agent` | Codex、Claude Code 等开发协作工具 |
| 产品能力层 | `Product Sales Agent` / `Sales Agent` / `产品 Sales Agent` | AI 销售助手产品中的用户可见销售助手 |
| 后端执行层 | `Runtime` / `LangGraph Runtime` / `Runtime graph` | 后端 LLM / tool 编排层 |
| 写回裁决层 | `Sales Workspace Kernel` | 结构化 workspace 状态机和正式写回裁决层 |

规则：

- 新文档默认不要裸写 `agent`。
- 如果写 `agent`，上下文必须已经明确是哪一层。
- 涉及 Codex / Claude Code 时，用 `Dev Agent` 或 `Execution Agent`。
- 涉及产品用户体验、记忆、候选研究或工作区状态时，用 `Product Sales Agent`。
- 涉及 LangGraph、LLM、tool 调用或 draft payload 时，用 `Runtime / LangGraph Runtime`。
- 涉及正式对象写回、校验、排名和 Markdown projection 时，用 `Sales Workspace Kernel`。

### 2.1 Dev Agent / Execution Agent

含义：

- Codex
- Claude Code
- 其他受人工指挥修改仓库的开发协作工具

职责：

- 阅读仓库文档
- 执行当前 task
- 修改代码或文档
- 运行验证
- 更新 handoff
- 汇报实际变更

不得：

- 把自己当成产品里的 Sales Agent
- 自行扩展产品方向
- 跳过 `_active.md` 去发明新实现任务
- 把命令输出里的 “agent” 理解成产品对象，除非上下文明确

推荐写法：

```text
开发 agent / Dev Agent / Execution Agent
```

---

### 2.2 Product Sales Agent

含义：

- AI 销售助手产品中的用户可见销售 agent
- V2 workspace-native sales agent
- 面向中小企业老板 / 销售负责人的产品能力

职责：

- 通过 chat-first 入口理解用户产品和获客方向
- 产出 `WorkspacePatchDraft`
- 支撑产品理解、客户挖掘、候选排序和反馈闭环

不得：

- 直接写正式后端对象
- 绕过 Sales Workspace Kernel
- 把 Markdown、prompt、LangGraph checkpoint 或 SDK session 当成业务主存

推荐写法：

```text
Product Sales Agent / Sales Agent / 产品 Sales Agent
```

---

### 2.3 Runtime / LangGraph

含义：

- 后端 LLM / tool 执行层
- LangGraph graph
- runtime adapter

职责：

- 接收 `ContextPack`
- 编排 LLM / tool 调用
- 返回 typed draft payload 或 `WorkspacePatchDraft`

不得：

- 直接写正式业务对象
- 直接修改 Markdown projection
- 直接生成正式 `CandidateRankingBoard`
- 把 checkpoint 当成业务记忆主存

推荐写法：

```text
Runtime / LangGraph Runtime / Runtime graph
```

---

## 3. 给 Codex / Claude Code 的提示模板

### 3.1 标准执行任务模板

```text
你现在是 Dev Agent / Execution Agent，不是产品中的 Sales Agent。

请先读取：
1. AGENTS.md
2. docs/README.md
3. docs/delivery/tasks/_active.md
4. 当前 task 文档

本任务中的 Product Sales Agent / Sales Agent 是产品概念；
Runtime / LangGraph 是后端执行层概念；
你只负责按当前 task 修改仓库，不要自行扩展产品方向。

完成后请运行最轻量有意义的验证，并更新 handoff。
```

### 3.2 文档同步任务模板

```text
你现在是 Dev Agent，任务是同步仓库文档。

请不要把文档中的 Sales Agent 理解为你自己。
Sales Agent 指产品中的 AI 销售助手。
Runtime / LangGraph 指后端 LLM/tool 执行层。

只修改 task 指定的文档范围。
不要改代码，不要重定义产品方向。
```

### 3.3 后端实现任务模板

```text
你现在是 Dev Agent，负责实现当前 backend task。

Product Sales Agent 是产品概念；
Runtime / LangGraph 是未来执行层；
Sales Workspace Kernel 是正式写回裁决层。

如果实现需要改变 Product Sales Agent 行为、Runtime 写回边界、API contract 或 DB schema，
请停止并回到 task / ADR / PRD，不要自行扩大范围。
```

---

## 4. 文档写作规则

### 4.1 写开发协作工具时

使用：

```text
Dev Agent
Execution Agent
开发 agent
执行 agent
Codex / Claude Code
```

不要只写：

```text
agent
```

除非上下文已经明确是在说开发协作层。

### 4.2 写产品能力时

使用：

```text
Product Sales Agent
Sales Agent
产品 Sales Agent
workspace-native sales agent
```

不要写成：

```text
Codex agent
开发 agent
执行 agent
```

### 4.3 写后端执行层时

使用：

```text
Runtime
LangGraph Runtime
Runtime graph
backend/runtime
```

不要把 runtime 直接称为产品主架构。当前 V2 主架构是：

```text
Sales Workspace Kernel
```

---

## 5. 常见误写与推荐改写

| 容易混淆的写法 | 推荐改写 |
|---|---|
| agent 读取 docs 后开始开发 | Dev Agent 读取 docs 后开始开发 |
| agent 负责理解产品并生成候选客户 | Product Sales Agent 负责理解产品并生成候选客户 draft |
| agent 写入 workspace 对象 | Runtime 产出 WorkspacePatchDraft，Sales Workspace Kernel 裁决写回 |
| LangGraph 是 V2 主架构 | LangGraph 是 runtime execution layer，Sales Workspace Kernel 是 V2 主架构 |
| 让 agent 直接更新 Markdown workspace | Markdown 是 projection；Dev Agent 可改文档，Product Sales Agent / Runtime 不直接改 generated Markdown |
| agent memory 存在 checkpoint 里 | Product Sales Agent memory 必须沉淀为结构化后端对象 |

---

## 6. 执行前检查清单

开 Codex / Claude Code 线程前，人工开发者应检查：

1. 当前线程里的 “agent” 是否指 Dev Agent。
2. 产品文档里的 “Sales Agent” 是否明确是产品对象。
3. Runtime / LangGraph 是否被描述为执行层，而不是业务主存。
4. 当前任务是否已经写入 `docs/delivery/tasks/_active.md`。
5. 当前任务是否明确 out of scope。
6. 提示词是否说明“你是 Dev Agent，不是 Product Sales Agent”。

---

## 7. 停止条件

Dev Agent 遇到以下情况时应停止，并回到 task / ADR / PRD：

- 需要改变 V2 产品方向。
- 需要改变 Product Sales Agent 的用户可见行为。
- 需要改变 Runtime / LangGraph 的正式写回边界。
- 需要让 Runtime 直接写正式业务对象。
- 需要改变 Sales Workspace Kernel 的主真相规则。
- 需要新增 API contract。
- 需要新增 DB schema / migration。
- 需要接入 Android UI。
- 需要接入真实 LLM、搜索 provider 或联系方式处理。

---

## 8. 一句话原则

> Codex / Claude Code 是 Dev Agent；产品里的销售助手是 Product Sales Agent；LangGraph 是 Runtime。三者不能混用。
