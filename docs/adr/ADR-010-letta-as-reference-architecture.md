# ADR-010：Letta as Reference Architecture for V3

- 文档状态：Accepted / reference study only / 不开放具体复刻 task
- 决策日期：2026-05-02
- 关联文档：
  - `docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`
  - `docs/adr/ADR-008-v2-langgraph-letta-style-memory-direction.md`
  - `docs/architecture/v3/memory-native-sales-agent.md`
  - `docs/architecture/v3/letta-comparison.md`
  - `docs/product/prd/ai_sales_assistant_v3_prd.md`

---

## 1. 决策

V3 项目阶段性方向定为 **"先以 Letta 为 reference architecture"**，并通过 grill-me 收敛到下面这条窄路径：

> **(D) 先做 reference study（不动代码）→ 窄路径走 (A) 按差距清单逐项补齐自研实现**

具体实现策略：

- 将 Letta 仓库的 `0.16.7`（commit `f33324768950e6752f80d6c725873cc92d22f8b2`）作为 reference architecture，本地阅读副本放在仓库外 sibling 目录 `~/projects/_references/letta/`，**不** vendor 进本仓库、**不**作为 git submodule。
- 不接 Letta server、不 fork Letta 代码、不引入 Letta SDK 作为运行时依赖。
- 本 ADR 只圈定差距优先级与"保留 / 替换 / 抛弃"决策，**不**承诺 (A) 阶段的 task 排程。每个 (A) task 仍需用户单独授权进入 `_active.md`。

---

## 2. 原因

ADR-009 已定 V3 主线为 **Agent Sandbox-first Memory-native Sales Agent**，并把 Letta-style memory blocks、archival memory、memory tools、compaction 列为参考。任务 `task_2026_04_30_v3_letta_inspired_core_memory_tool_loop_poc.md` 已交付 native function-calling memory tool loop POC（5 个 core memory block + 4 个 memory tool + LangGraph 5 节点图 + opt-in DB 持久化 + `/lab` 可视化）。

但 Letta-style 不是 Letta。深入读源码后发现 V3 与 Letta 的差距集中在三类：

1. **Letta 三层 memory（core / recall / archival）** —— V3 只有 core 层；recall（hybrid 检索对话历史）与 archival（pgvector 长期记忆）整层缺失。
2. **Agent 一等实体与跨 session 持久化** —— Letta agent 跨 session 持久、blocks 多对多绑定、`message_ids` 是 in-context 指针；V3 的最大持久化单元仍是 session。
3. **Context 压缩与 step 控制** —— Letta 用 `summarize_messages_inplace` + `request_heartbeat`；V3 用 `messages[-8:]` + `v3_tool_loop_exhausted` 硬上限。

不固化"以 Letta 为参考"的窄路径，会出现两种风险：

- 把 V3 推向 Letta server 接入或 fork（违反 `_active.md` §5 与 AGENTS.md §14 "小步可逆"）。
- 在没有源码证据的情况下凭印象设计 archival / cross-session schema（与 ADR-009 "不冻结 schema" 冲突）。

本 ADR 用一个轻量的"参考层选择"决策，把这两类风险都关掉。

---

## 3. Letta 三层 memory 如何映射到 V3

| 层 | Letta | V3 当前 | 映射判断 |
|---|---|---|---|
| **Core memory** | `Block` 实体 + `core_memory_append/replace`、`memory_insert/replace/rethink/finish_edits`，默认 limit 20k–100k | `CoreMemoryBlock` + `core_memory_append/memory_insert/memory_replace`，limit 默认 2k 上限 20k | **形状已对齐**；缺 `description / metadata` 字段、缺 `memory_rethink/finish_edits`、limit 数量级偏小 |
| **Recall memory** | 全量 message 在 `message` 表，`conversation_search` 工具按 hybrid（vector + FTS）检索 | session 内消息全部内嵌、不可检索、`messages[-8:]` 截断 | **缺整层**；与压缩耦合 |
| **Archival memory** | `passage_manager.insert_passage` 走 embedding，`ArchivalPassage` SQL + 可选 Turbopuffer 双写；`archival_memory_search` 语义检索 | 无 | **缺整层**；前置依赖 embedding provider 与 schema 决策 |

映射结论：**core 层基本对齐、recall/archival 整层缺失**。这是 V3 距离 Letta-style 最大的技术债，但不必须一次补齐 —— archival 的"用户价值"（销售场景里跨会话记客户信息）大于 recall（同一会话内查历史）。

---

## 4. 哪些 Letta 机制是必要的，哪些是 over-engineering

针对销售场景 + V3 sandbox POC 边界判断：

### 4.1 必要（应在 (A) 阶段逐项授权补齐）

- **Archival memory + embedding + 语义检索**：销售场景的核心价值之一是"agent 跨会话记得客户"，这是 ADR-009 §3 已经允许的方向。
- **Context 压缩 / 摘要**：当前 `messages[-8:]` 截断在长会话下会丢客户上下文，是用户体验阻断点。
- **Agent 一等实体 + 跨 session 持久化身份**：销售助手不能"换个 session 就失忆"；blocks 必须挂在 agent 上而不是 session 上。
- **Block `description` 字段**：让模型理解每个 block 的职责，对 prompt 质量提升明显，改造代价小。
- **Memory tool 描述对齐**：参考 Letta `core_memory_replace` / `memory_insert` 的措辞和 line-number 防御机制。
- **死代码清理**：当前 `MemoryItem / WorkingState / CustomerIntelligenceDraft / _apply_action` 与 core memory blocks 职责重叠且在 native tool loop 中已不被调用。

### 4.2 可选（视用户反馈再开）

- **Recall memory（`conversation_search`）**：在 archival 落地后再评估；销售场景里大部分"该记的"应该已经被 agent 提取到 archival。
- **`request_heartbeat` 机制**：Letta 的 step 上限是 50 步配 heartbeat；V3 当前 4 步硬上限 + send_message 终止已能满足销售对话场景。先调 step 上限，必要时再引 heartbeat。
- **`memory_rethink` / `memory_finish_edits`**：解决 block 内容碎片化问题，但销售场景下 block 增长速率不一定触发。
- **Block multi-agent 共享 / `block_history` 版本**：跨 agent 共享 block 是企业场景需求；版本历史是高级能力，POC 阶段不必。

### 4.3 over-engineering（明确不复刻）

- **Letta server 整体接入 / Letta SDK 作为运行时依赖**：被 `_active.md` §5 禁止。
- **多 agent / agent-to-agent / Group / Identity 体系**：被 §5 禁止；销售单 agent 场景不需要。
- **Sleeptime agent / background worker**：被 §5 禁止。
- **Tool sandbox executor（E2B / 本地 subprocess）**：销售场景工具是 deterministic memory + send_message，不需要外部执行。
- **ADE 前端**：V3 `/lab` 已能覆盖单 agent 调试需求。
- **Composio / MCP 集成、Cloud / org / billing / auth、Identity / 模板化 deployment**：与 V3 sandbox POC 边界无关。
- **Provider 抽象层**：V3 已对齐 Tencent TokenHub native FC，强行多 provider 抽象会引入未验证依赖。

---

## 5. 当前 V3 资产：保留 / 替换 / 抛弃

| 资产 | 决策 | 理由 |
|---|---|---|
| **LangGraph 5 节点图** (`backend/runtime/v3_sandbox/graph.py`) | **保留** | 已被 native FC tool loop POC 验证；与 Letta `letta_agent_v3.step()` 概念上等价 |
| **LangGraph + LangChain 自研路线** | **保留** | ADR-009 §1 已定；Letta 自身在向多 agent class 演进，但我们没必要为追随它换 runtime |
| **Pydantic schema + Alembic migration** | **保留** | 与 Letta 同栈；后续扩 archival / agent 一等实体走 Alembic 增量 migration |
| **Tencent TokenHub native FC client** | **保留** | 已 smoke 通过；不引入多 provider 抽象 |
| **`/lab` 调试视图** | **保留** | 已超过 ADE 子集（trace/transition/memory blocks 都有），是 V3 独有资产 |
| **`messages[-8:]` 硬截断** (`graph.py:386`) | **替换** | 长会话场景会丢客户信息；需引入摘要或扩大 in-context window |
| **`v3_tool_loop_exhausted` 4 步上限** (`graph.py:374`) | **替换** | Letta 默认 50 步；销售场景里 agent 可能需要先 append、再 replace、再 send_message，4 步偏紧 |
| **Memory tool 描述与 prompt 组装** (`graph.py:401-422`、`:425`) | **替换** | 参考 Letta 工具 docstring 与 line-number 防御重写；保留 V3 的 substring `memory_insert` 还是切到 line-based 在 (A) task 中决定 |
| **`MemoryItem` + status 状态机** (`schemas.py`、`graph.py:887` `_apply_action`) | **抛弃** | 与 core memory blocks 职责重叠；native tool loop 不再调用 `_apply_action`；当前是死代码 |
| **`WorkingState` / `CustomerIntelligenceDraft`** (`schemas.py`) | **抛弃** | 同上；销售特定字段后续应迁到 `customer_intelligence` core memory block 的 value 与可选的 `metadata` 中，由 agent 自己维护 |
| **`update_working_state` / `update_customer_intelligence` action 分支** | **抛弃** | `_apply_action` 路径整体下线后自然消失 |
| **`CoreMemoryBlock` 当前字段** | **扩字段** | 增 `description / metadata`；考虑 `tags`；提升默认 `limit` |

"抛弃" 的实际删除动作仍需单独 (A) task 授权 —— 本 ADR 只锁决策。

---

## 6. (A) 阶段缺口优先级（仅候选，不开放）

下列顺序是本 ADR 的推荐，**不**等于自动开放任务。每项都需用户在 `_active.md` 显式开 task。

1. **Block schema 扩字段 + memory tool 描述对齐**（小、低风险、不改 schema 数据库表）
2. **死代码清理：`MemoryItem` / `WorkingState` / `CustomerIntelligenceDraft` / `_apply_action`** （机械重构、可逆）
3. **Context 压缩 / step 上限调整**（中、不引入新表）
4. **Archival memory 三层模型补齐**（大、需 §5 显式开放、需新表 + embedding provider 决策）
5. **跨 session agent 一等实体持久化**（大、需 §5 显式开放、与 #4 schema 设计耦合）
6. **Recall memory（`conversation_search`）**（在 #4 落地后再评估）

理由：1–3 都在当前 sandbox POC 边界内可做；4–5 需要 ADR-009 §3 与 `_active.md` §5 显式松绑。把小、低风险的优先做，能在不触碰 §5 红线的前提下让 V3 更接近 Letta 的"形状"。

---

## 7. 不目标 / 边界

- **不**设定时间线或 milestone。
- **不**预先承诺 (A) 阶段会全部完成。
- **不**为 (A) 阶段批量开 task；每项需要用户在当前会话或 `_active.md` 显式授权。
- **不**修改本 ADR 与对照表外的代码、schema 或测试 —— 即使阅读源码过程中发现可优化点，也走单独 task。
- **不**把 Letta 源码片段复制进本仓库；引用一律 `letta/...:行号` + commit SHA。
- **不**把 Letta 当 product source of truth；销售领域决策仍以 V3 PRD / ADR-009 / `docs/architecture/v3/memory-native-sales-agent.md` 为准。
- 升级 Letta pin 版本时，更新 `letta-comparison.md` §2 的 release tag / commit SHA，并 spot-check 行号引用。

---

## 8. 验证

本 ADR 与对照表是 D2 阶段产物，无代码改动。验证以文档自洽为主：

- ADR §3-§6 的差距条目能在 `letta-comparison.md` 第 3 节里找到对应行。
- ADR §5 的"保留 / 替换 / 抛弃"决策每行能在当前 V3 代码里指认到具体文件 / 函数。
- `_active.md` 在本任务完成后 `Auto-continue` 仍为 `no`，未自动开放 (A) task。
- Letta pin 版本（0.16.7 / `f3332476...`）可在 `~/projects/_references/letta/` `git rev-parse HEAD` 验证。

---

## 9. 后续

- 本 ADR 完成后，V3 项目阶段状态在 `docs/product/project_status.md` 中保持原状（POC 边界未变），不需要更新。
- 用户决定开 (A) 第一刀时，建议从 §6 表里取一项，按 `repo-task-bootstrap` 或 `backend-task-bootstrap` 起 task；该 task 应在自身 §1 引用本 ADR 与对照表对应行。
- 本 ADR 的修订（包括 Letta pin 升级）走"修改 ADR + 同步对照表" 一同提交，避免漂移。
