# Task：V3 Letta Reference Study (Phase D2)

更新时间：2026-05-02

## 1. 任务定位

- 任务名称：V3 Letta Reference Study (Phase D2)
- 当前状态：`done`
- 优先级：P2
- 任务类型：`docs / reference architecture`
- 是否属于 delivery package：`no`

## 2. 授权来源

用户在当前线程明确指示项目阶段性方向为"先复刻 Letta"，并通过 grill-me 收敛到：

> (D) 先做 reference study（不动代码）→ 窄路径走 (A) 按差距清单逐项补齐自研实现

本任务对应 (D2)：产出 ADR + 子系统对照表 + 任务 / handoff 记录，作为后续 (A) 阶段开 task 的证据基础。

## 3. 范围

In scope:

- Clone Letta 仓库到仓库外 sibling 目录 `~/projects/_references/letta/` 并 pin release tag。
- 阅读 Letta 优先子系统：agent loop、block schema/ORM、memory 工具集、archival memory、context 压缩、Pydantic schemas。
- 产出 `docs/adr/ADR-010-letta-as-reference-architecture.md`。
- 产出 `docs/architecture/v3/letta-comparison.md`。
- 写本任务与 handoff。
- 更新 `docs/delivery/tasks/_active.md` Recently completed 列表。

Out of scope（**不做**）：

- 修改 `backend/`、`app/`、`web/` 下的任何代码、schema、prompt、迁移。
- 把 Letta 源码 vendor 进本仓库或作为 git submodule。
- 接 Letta server / Letta SDK 作为运行时依赖。
- 在 ADR / 对照表中复制 Letta 源码片段（仅引用路径 + 行号 + commit SHA）。
- 自动开放 (A) 阶段下游 task。
- 触碰被 `_active.md` §5 禁止的方向（archival schema、Android 重写、CRM/outreach 等）。

## 4. 实际结果

- Letta `0.16.7`（commit `f33324768950e6752f80d6c725873cc92d22f8b2`）clone 至 `~/projects/_references/letta/`。
- 阅读了以下优先位置（在 ADR-010 与对照表中均带行号引用）：
  - `letta/agent.py:1107` `summarize_messages_inplace`、`:563` `request_heartbeat`、`:336` heartbeat 强制路径。
  - `letta/agents/letta_agent_v3.py:222` `step(max_steps=DEFAULT_MAX_STEPS)`；`letta/constants.py:75` `DEFAULT_MAX_STEPS=50`。
  - `letta/functions/function_sets/base.py`：`send_message`、`conversation_search`（hybrid）、`archival_memory_insert/search`、`core_memory_append/replace`、`memory_replace/insert/rethink/finish_edits`。
  - `letta/schemas/block.py:13` `BaseBlock`、`letta/orm/block.py:20` ORM `Block` 与 `blocks_agents` 多对多关系、`block_history` 与 `version` 乐观锁。
  - `letta/services/passage_manager.py:543` `insert_passage`（embedding + 可选 Turbopuffer 双写）。
  - `letta/services/message_manager.py:1147` hybrid 检索 (`vector/fts/hybrid/timestamp`)。
  - `letta/schemas/agent.py:67` `AgentState`：`message_ids` 指针 / `blocks` / `tools` / `enable_sleeptime` / `compaction_settings`。
  - `letta/constants.py:433-435` block 默认 limit (persona/human=20000，其他=100000)。
- 产出文档：
  - `docs/adr/ADR-010-letta-as-reference-architecture.md`
  - `docs/architecture/v3/letta-comparison.md`
- 关键决策（详见 ADR-010 §5）：保留 LangGraph + Pydantic + Alembic + TokenHub + `/lab`；替换 `messages[-8:]` 截断与 4 步上限；抛弃 `MemoryItem` / `WorkingState` / `CustomerIntelligenceDraft` 与 `_apply_action`（与 core memory blocks 职责重叠且当前在 native tool loop 中是死代码）。
- 缺口优先级（详见 ADR-010 §6）：① block schema 扩字段 + memory tool 描述对齐 → ② 死代码清理 → ③ context 压缩 / step 上限 → ④ archival memory（需 §5 松绑）→ ⑤ 跨 session agent 一等实体（需 §5 松绑）→ ⑥ recall memory。

## 5. 验证

本任务无代码改动，验证以文档自洽与边界为主：

- `git status --short` 仅新增 4 文档 + 修改 `_active.md`。
- `git diff --check` 无空白错误。
- ADR-010 §3-§6 的差距条目可在 `letta-comparison.md` §3 找到对应行。
- ADR-010 §5 的"保留 / 替换 / 抛弃"决策每行可在当前 V3 代码（`backend/runtime/v3_sandbox/graph.py`、`schemas.py`）里指认到具体文件 / 函数。
- Letta pin：`cd ~/projects/_references/letta && git rev-parse HEAD` → `f33324768950e6752f80d6c725873cc92d22f8b2`。
- `_active.md` `Auto-continue: no`，未自动开放 (A) task。

不触发：

- pytest（无 Python 改动）
- `npm run build` / `test:e2e`（无前端改动）
- alembic upgrade（无 schema 改动）

## 6. 已知限制

- ADR-010 §6 的优先级是基于源码差距和销售场景判断的推荐，不基于真实用户测试结果。具体顺序可能在 (A) 阶段被用户调整。
- Letta `0.16.7` 是 D2 阶段截止时 `git tag --sort=-creatordate` 列出的最新 release tag；后续若升级 pin 版本，需同步更新 `letta-comparison.md` §2 与 ADR-010 §1，并 spot-check 行号引用。
- 本任务**不**测试 Letta 工具描述在 TokenHub / Tencent 模型上的实际效果；该实证留给后续 (A) task。

## 7. 后续建议

下一步建议单独开放（**不**自动开工）：

- 任一 ADR-010 §6 列出的 (A) 缺口；推荐从 #1（block schema 扩字段 + memory tool 描述对齐）或 #2（死代码清理）起步，因为风险最低、可逆、不触 §5 红线。
- 若用户希望先打 archival 这一刀，需先在 `_active.md` §5 显式松绑"超出 sandbox POC 的 memory DB schema"，并起 ADR-011 圈定 archival schema / embedding provider。
