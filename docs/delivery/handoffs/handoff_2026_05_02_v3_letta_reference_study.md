# Handoff：V3 Letta Reference Study (Phase D2)

更新时间：2026-05-02

## 1. 任务

`docs/delivery/tasks/task_2026_05_02_v3_letta_reference_study.md`（status: `done`）

## 2. 实际产出

- `docs/adr/ADR-010-letta-as-reference-architecture.md` —— 决策：以 Letta 为 reference architecture，窄路径走 (A)；列出"保留 / 替换 / 抛弃"决策与缺口优先级。
- `docs/architecture/v3/letta-comparison.md` —— 21 行子系统对照表，覆盖 agent loop、heartbeat、memory 工具集、block schema、limit、共享、agent 一等实体、in-context 与历史消息、压缩、recall、archival、tool registry、prompt 组装、schema 边界、persistence、provider、embedding、Web 调试入口、sleeptime、多 agent、tool sandbox。
- `docs/delivery/tasks/task_2026_05_02_v3_letta_reference_study.md`
- `docs/delivery/tasks/_active.md` —— Recently completed 列表追加，`Auto-continue` 维持 `no`。

## 3. 涉及文件

新增：

- `docs/adr/ADR-010-letta-as-reference-architecture.md`
- `docs/architecture/v3/letta-comparison.md`
- `docs/delivery/tasks/task_2026_05_02_v3_letta_reference_study.md`
- `docs/delivery/handoffs/handoff_2026_05_02_v3_letta_reference_study.md`

修改：

- `docs/delivery/tasks/_active.md`

引用但未修改：

- `backend/runtime/v3_sandbox/graph.py`、`backend/runtime/v3_sandbox/schemas.py`、`backend/runtime/v3_sandbox/store.py`
- `backend/api/v3_sandbox.py`
- `backend/alembic/versions/20260430_0006_*.py`
- `web/src/App.tsx`、`web/src/api.ts`
- `docs/architecture/v3/memory-native-sales-agent.md`、`docs/architecture/v3/sandbox-memory-persistence.md`、`docs/architecture/v3/web-dual-entry-prototype.md`
- `docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`、`docs/adr/ADR-008-v2-langgraph-letta-style-memory-direction.md`

仓库外：

- `~/projects/_references/letta/`（Letta `0.16.7`，commit `f33324768950e6752f80d6c725873cc92d22f8b2`，Apache-2.0；阅读副本，未 vendor、未 submodule、未进 git）

## 4. 验证

- `git status --short` 应仅显示 4 个新增文档 + `_active.md` 修改。
- `git diff --check` 通过。
- ADR-010 §3-§6 的差距条目逐项在对照表 §3 中能定位到对应行。
- ADR-010 §5"保留 / 替换 / 抛弃"决策每行能在 V3 代码中指认到具体函数（参见对照表 #14）。
- Letta pin 验证：`cd ~/projects/_references/letta && git rev-parse HEAD` → `f33324768950e6752f80d6c725873cc92d22f8b2`。
- `_active.md` `Auto-continue: no`，未自动开放 (A) task。

不触发：pytest / `npm run build` / `npm run test:e2e` / alembic upgrade（皆无对应改动）。

## 5. 关键发现

- **Letta 三层 memory 中，V3 只对齐了 core 层；recall 与 archival 整层缺失**（对照表 #3 / #10 / #11）。
- **V3 当前的 `MemoryItem / WorkingState / CustomerIntelligenceDraft / _apply_action` 是死代码**：native FC tool loop 不再调用 `_apply_action`，但 `schemas.py` 与 `_build_messages` 仍保留 V2 期遗留路径。建议在最早的 (A) task 中清理（对照表 #14、ADR-010 §5）。
- **Block 默认 limit 数量级偏小**：V3 `default=2000, max=20000` vs Letta `persona/human=20000, others=100000`；销售场景下 `customer_intelligence` 容易先触顶（对照表 #5）。
- **Letta `memory_insert` 是 line-number 语义并带防御**（防 `\nLine N:` 前缀 / 防 `CORE_MEMORY_LINE_NUMBER_WARNING`），V3 是 substring `insert_after`。两种语义各有优劣，但 Letta 的防御机制对 prompt 鲁棒性影响显著（对照表 #3）。
- **Letta agent 是一等持久实体，blocks 通过 `blocks_agents` junction 表多对多绑定，且有 `block_history` + `version` 乐观锁**；V3 仍是 session 内嵌（对照表 #6 / #7）。
- **Letta 的 step 上限是 50 + heartbeat**，V3 是 4 + send_message 终止；销售场景里 4 步可能偏紧（对照表 #1 / #2）。
- **Letta `passage_manager.insert_passage`** 通过 `LLMClient.create(provider_type=embedding_endpoint_type)` 取 embedding，再 SQL + 可选 Turbopuffer 双写。V3 接 archival 时需先验证 TokenHub 是否提供 embedding endpoint（对照表 #11 / #17）。

## 6. 已知限制

- ADR-010 §6 的优先级是基于源码差距和销售场景判断的推荐，**不**基于实测；具体顺序可在 (A) 阶段被用户调整。
- 本任务**未**实测 Letta 工具描述在 TokenHub native FC 上的效果。
- Letta `0.16.7` 是 D2 阶段截止时的最新 release tag；版本升级时需同步对照表 §2 与 ADR-010 §1，并 spot-check 行号。

## 7. 推荐下一步

仅候选，**不**自动开工：

1. **(A) #1 — Block schema 扩字段 + memory tool 描述对齐**（小、低风险、不动 schema 表，仅 Pydantic 字段 + prompt）。
2. **(A) #2 — 死代码清理 (`MemoryItem` / `WorkingState` / `CustomerIntelligenceDraft` / `_apply_action`)**（机械重构、可逆）。
3. **(A) #3 — Context 压缩 / step 上限调整**（中、不引入新表）。
4. 若直接打 archival（(A) #4），需先在 `_active.md` §5 显式松绑"超出 sandbox POC 的 memory DB schema"，并新开 ADR-011 圈定 archival schema 与 embedding provider 选型。

执行 agent **不得**自行从上述候选中开工 —— 须由用户在 `_active.md` 显式开放对应 task。
