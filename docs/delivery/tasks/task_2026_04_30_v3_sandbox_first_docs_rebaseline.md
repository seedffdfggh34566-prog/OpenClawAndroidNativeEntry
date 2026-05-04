# Task：V3 Sandbox-first 文档重基线

更新时间：2026-04-30

## 1. 任务定位

- 任务名称：V3 Sandbox-first 文档重基线
- 当前状态：`done`
- 优先级：P0
- 任务类型：`planning`
- 是否属于 delivery package：`no`
- 文档同步级别：`Level 3 product / architecture / guardrail`

---

## 2. 授权来源

用户明确确认：

- V3 初期接受将所有 agent 写入视为 sandbox working state，而不是 formal business object。
- 希望第一阶段不要以 backend formal governance 作为默认实现前提。
- 未来保留 agent 自动维护客户情报、自动建档、候选客户排序和打分的扩展空间。

---

## 3. 任务目标

将当前 V3 口径从 “memory-native + backend governance/formal writeback” 调整为：

> **Agent Sandbox-first Memory-native Sales Agent**

核心含义：

- Product Sales Agent 先自主维护 memory、workspace working state 和 customer intelligence working state。
- Backend 初期只作为 runtime host、storage、trace 和 API 基础设施。
- 不把 backend 写成业务建档者或第一阶段裁决者。
- V2 Kernel、Draft Review、`WorkspacePatchDraft` 和 formal writeback 仅作为 historical validated assets。

---

## 4. 范围

In Scope：

- 更新当前 V3 PRD、ADR、architecture、README、overview、project status、roadmap。
- 更新 V3 Web dual-entry 文档中的 `/lab` 观察对象。
- 更新 backend guardrail skill source/spec 文档，避免 Dev Agent 回到 V2 formal object / PatchDraft / Kernel 默认路径。
- 同步更新后的 backend skills 到本机 Codex skills 目录。
- 更新 `_active.md` 和 delivery README。
- 新增 handoff。

Out of Scope：

- 修改历史 V1/V2 task、handoff、research 正文。
- 新增 schema、API、migration。
- 新增 Web 工程或 npm 依赖。
- 实现 runtime、memory tools、customer intelligence、Android/backend 代码。
- 启动真实外部触达、CRM 生产写入、不可逆导出、production SaaS/auth/tenant。

---

## 5. 实际结果说明

已完成 V3 sandbox-first docs rebaseline。当前 V3 仍是 direction accepted / implementation not started。

后续 implementation 需单独开放 task，并应从 sandbox working state、memory tools、customer intelligence working state 和 backend infrastructure 的最小验证开始。

---

## 6. 已做验证

- `git diff --check`
- `rg "backend governance|formal writeback|WorkspacePatchDraft|Sales Workspace Kernel|backend gate" docs/README.md docs/product docs/architecture/v3 docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`
- `rg "sandbox-first|working state|customer intelligence|自动建档|排序|打分|runtime host|storage|trace|API" docs/README.md docs/product docs/architecture/v3 docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`
- 人工检查 task / handoff 未出现 V3 implementation、Web implementation、MVP 或 production readiness 完成性误声明。
- `python3 scripts/sync_codex_skills.py backend-runtime-boundary-guard backend-api-change-check backend-db-risk-check backend-contract-sync backend-task-bootstrap`
- 人工检查未新增 schema/API/migration，未启动实现。
