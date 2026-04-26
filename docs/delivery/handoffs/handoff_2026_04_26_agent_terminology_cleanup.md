# 阶段性交接：Agent terminology cleanup

更新时间：2026-04-26

## 1. 本次改了什么

- 在 `AGENTS.md` 中同步 V2 workspace-native / Sales Workspace Kernel 当前基线。
- 在 `AGENTS.md` 中补强术语边界：未限定的 `agent` 在该文件中默认指 Dev Agent / Execution Agent；产品行为、runtime draft、memory 和 writeback 必须写具体术语。
- 在 `backend/AGENTS.md` 与 `app/AGENTS.md` 中明确规则面向 Dev Agent / Execution Agent。
- 在 `docs/README.md`、`docs/delivery/README.md`、`docs/product/overview.md`、V2 PRD 和 workspace v0 文档中清理高风险 `agent` 混用。
- 在 `docs/how-to/operate/dev-agent-vs-sales-agent-runbook.md` 中新增 canonical naming 规则。

## 2. 本次未改什么

- 未批量改历史 handoff。
- 未批量改 V1 research / archive。
- 未重写 2026-04-25 的 data/runtime 正文。
- 未修改代码、API、DB、Android 或 runtime 实现。

## 3. 验证

- 已检查当前入口 / 基线文件中不再匹配本次定义的高风险旧写法。
- 已检查当前入口 / 基线文件包含：
  - `Dev Agent`
  - `Product Sales Agent`
  - `Runtime / LangGraph Runtime`
  - `Sales Workspace Kernel`
- 已运行 `git diff --check`。

## 4. 已知限制

- 历史 handoff 和 V1 research 中仍可能出现旧 `agent` 表述，但保留为历史语境。
- `docs/architecture/data/*` 与 `docs/architecture/runtime/langgraph-runtime-architecture.md` 正文仍需要后续单独做 data/runtime 文档同步。

## 5. 推荐下一步

继续按 `docs/delivery/tasks/_active.md` 执行当前 Sales Workspace Kernel backend-only v0 task。若后续要清理 data/runtime 正文术语，应单独创建文档同步任务。
