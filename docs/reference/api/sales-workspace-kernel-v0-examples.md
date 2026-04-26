# Sales Workspace Kernel API Contract Examples v0

更新时间：2026-04-27

## 1. 文档定位

本文档提供 Sales Workspace Kernel API contract v0 的 fixture examples / state transition examples。

这些 examples 用于：

- 验证 API contract shape。
- 说明 workspace state transition。
- 支撑后续是否开放 backend API implementation 的判断。

这些 examples 不是：

- runtime fixtures。
- DB fixtures。
- FastAPI implementation。
- persistence baseline。

关联文档：

- `docs/reference/api/sales-workspace-kernel-v0-contract.md`
- `docs/adr/ADR-007-v2-sales-workspace-persistence-decision.md`
- `docs/delivery/tasks/task_v2_sales_workspace_contract_fixture_examples.md`

---

## 2. 示例目录

JSON examples 位于：

```text
docs/reference/api/examples/sales_workspace_kernel_v0/
```

文件：

- `01_create_workspace_request.json`
- `02_create_workspace_response.json`
- `03_patch_product_direction_request.json`
- `04_patch_round_1_request.json`
- `05_patch_round_2_request.json`
- `06_ranking_board_response.json`
- `07_projection_response.json`
- `08_context_pack_response.json`
- `09_error_workspace_version_conflict.json`
- `10_error_validation_error.json`

---

## 3. State Transition

示例使用现有 backend-only v0 e2e 场景中的稳定对象：

- workspace：`ws_demo`
- product：`FactoryOps AI`
- lead direction：`dir_v1`
- research rounds：`rr_001`, `rr_002`
- candidates：`cand_a`, `cand_b`, `cand_d`

状态流：

```text
create workspace
-> patch product + lead direction
-> patch round 1 candidate / observation
-> patch round 2 stronger candidate
-> derived ranking board shows cand_d at #1
-> derived Markdown projection contains rankings/current.md
-> derived ContextPack contains cand_d as top candidate
```

---

## 4. Contract Notes

- `WorkspacePatch` 是唯一写入口。
- `CandidateRankingBoard` 是 derived output。
- Markdown projection 是 derived output，不支持 parse-back。
- `ContextPack` 是 derived output，从 structured state 编译。
- `in-memory / JSON fixture` 仅作为 prototype / contract validation 支撑，不是正式 persistence baseline。
- backend API implementation 继续 blocked。
- FastAPI endpoint、Alembic migration、SQLite schema change、Android UI、Runtime / LangGraph integration 都不在本 examples task 范围。

---

## 5. Validation

验证命令：

```bash
find docs/reference/api/examples/sales_workspace_kernel_v0 -name "*.json" -print0 | xargs -0 -n1 python3 -m json.tool >/dev/null
rg "sales-workspace-kernel-v0-examples.md|sales_workspace_kernel_v0" docs/reference docs/delivery docs/README.md
rg "workspace_version_conflict|validation_error|cand_d|ContextPack|Markdown projection" docs/reference/api/sales-workspace-kernel-v0-examples.md docs/reference/api/examples/sales_workspace_kernel_v0
```

当前 `jianglab` 环境没有 `python` 别名，实际验证使用 `python3 -m json.tool`。
