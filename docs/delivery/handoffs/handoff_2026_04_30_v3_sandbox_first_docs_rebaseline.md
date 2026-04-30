# Handoff：V3 Sandbox-first 文档重基线

日期：2026-04-30

## 1. 变更摘要

本次只做文档重基线，不改代码、不新增依赖、不跑 migration。

核心结果：

- V3 当前口径从 “memory-native + backend governance/formal writeback” 调整为 **Agent Sandbox-first Memory-native Sales Agent**。
- V3 初期所有 agent 写入默认是 sandbox / working state，不区分正式业务对象。
- Backend 初期定位为 runtime host、storage、trace、API surface，不是业务建档者或第一阶段裁决者。
- 未来保留 agent-maintained customer intelligence、自动建档、候选客户排序和打分方向，但当前不实现、不冻结 schema。
- V2 Kernel、Draft Review、`WorkspacePatchDraft` 和 formal writeback 降级为 historical validated assets，不是 V3 初期默认路径。
- 相关 repo-managed backend skills 已同步到本机 Codex skills 目录。

## 2. 文件或区域

- `docs/product/prd/ai_sales_assistant_v3_prd.md`
- `docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`
- `docs/architecture/v3/memory-native-sales-agent.md`
- `docs/architecture/v3/web-dual-entry-prototype.md`
- `docs/README.md`
- `docs/product/overview.md`
- `docs/product/project_status.md`
- `docs/product/README.md`
- `docs/product/roadmap.md`
- `docs/architecture/README.md`
- `docs/how-to/operate/skills-src/backend-*/SKILL.md`
- `docs/how-to/operate/skills/backend-*.md`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/README.md`
- `docs/delivery/tasks/task_2026_04_30_v3_sandbox_first_docs_rebaseline.md`

## 3. 验证

- `git diff --check`
- `rg "backend governance|formal writeback|WorkspacePatchDraft|Sales Workspace Kernel|backend gate" docs/README.md docs/product docs/architecture/v3 docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`
- `rg "sandbox-first|working state|customer intelligence|自动建档|排序|打分|runtime host|storage|trace|API" docs/README.md docs/product docs/architecture/v3 docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`
- 人工检查 task / handoff 未出现 V3 implementation、Web implementation、MVP 或 production readiness 完成性误声明。
- `python3 scripts/sync_codex_skills.py backend-runtime-boundary-guard backend-api-change-check backend-db-risk-check backend-contract-sync backend-task-bootstrap`

## 4. 已知边界

- 未改历史 V1/V2 task、handoff、research 正文。
- 未新增 schema、API、DB migration。
- 未实现 runtime、memory tools、customer intelligence、Web、Android 或 backend 代码。
- 未同步外部 CRM、真实外部触达、不可逆导出或 production SaaS/auth/tenant。

## 5. 推荐下一步

正式 implementation 前，建议新开 `V3 sandbox runtime POC` task：

- 验证 LangChain / 腾讯云 API 调用。
- 验证 agent 自编辑 memory。
- 验证 sandbox workspace working state。
- 验证 customer intelligence working state、候选客户排序理由和打分草案。
- 用 Web `/lab` 做人工与 Playwright smoke。
