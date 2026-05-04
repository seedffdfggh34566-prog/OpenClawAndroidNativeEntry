# Handoff: V3 文档清理、模型 allowlist 修正与开发环境合约

## 1. 变更内容

### 1.1 Dev Environment Contract

新增开发环境 canonical 入口与维护规则：

| 文件 | 说明 |
|---|---|
| `Makefile` | `dev`、`dev-smoke`、`test`、`backend-test`、`alembic`、`clean` |
| `scripts/start-dev.sh` | 一键启动 backend (`127.0.0.1:8013`) + web (`0.0.0.0:5173`)；带端口占用检测、Alembic migration、 readiness 等待、Level A smoke check |
| `scripts/dev-environment.md` | 服务清单、proxy 规则、health check、smoke test 分层（A/B/C）、维护规则 |
| `backend/AGENTS.md` | 新增 §4.4 "Dev Environment Contract"：规定 `make dev` 为 canonical 入口；改端口/proxy/Alembic/env/新服务时必须同步更新 `scripts/start-dev.sh` + `scripts/dev-environment.md`；变更后验证 30 秒内启动且 `/health` 返回 `{"status":"ok"}` |

### 1.2 根目录 README V2→V3 rebaseline

根目录 `README.md` 从 V2.1 定位重写为 V3 主线：

- 标题与定位改为 "V3 Agent Sandbox-first Memory-native Sales Agent"
- 必读入口指向 V3 文档（`docs/README.md`、`docs/product/project_status.md` 等）
- 当前系统形态描述改为 `backend/`（sandbox runtime）、`web/`（`/lab`）、`app/`（Android）
- 常用验证命令替换为 V3 命令（`make backend-test`、`make dev`、`make dev-smoke`）
- 删除 V2 Sales Workspace Kernel、Draft Review、Postgres persistence 等专属验证命令
- 保留历史背景与 archive 链接

### 1.3 Replay 不复用 summary 观察项闭环

`docs/delivery/handoffs/handoff_2026_05_03_v3_endpoint_a_lite_persistent_recursive_summary.md`：

- §4 "Replay 行为"更新为已验证状态，引用 `test_replay_does_not_reuse_persisted_summary` 与 `test_session_reset_clears_summary_fields`
- §5 候选列表第 5 项标记为 "已完成"

### 1.4 从 allowlist 移除 deepseek-v3.2

原因：128k 窗口对分层预算（0.75 阈值 + 32 条 recent 保留 + response headroom）偏紧；Layer C 修正已建议移除。

| 文件 | 改动 |
|---|---|
| `backend/api/v3_sandbox.py` | `AllowedV3SandboxModel` 移除 `"deepseek-v3.2"` |
| `backend/runtime/v3_sandbox/graph.py` | `_MODEL_CONTEXT_WINDOWS` 移除 `"deepseek-v3.2": 128_000` |
| `backend/runtime/tokenhub_native_fc.py` | `V3_TOKENHUB_NATIVE_FC_MODEL_ALLOWLIST` 与 `V3_TOKENHUB_NATIVE_FC_MODEL_POLICIES` 移除 deepseek-v3.2 条目 |

## 2. 验证结果

- `backend/.venv/bin/python -m pytest backend/tests -q`：**167 passed, 18 skipped**（0 regression）
- `make dev-smoke`：Level A 通过（backend health + `/lab` 可访问）
- 根目录 README 无代码影响，人工阅读确认结构与链接正确

## 3. 已知限制

- `scripts/start-dev.sh` 尚未覆盖 Level B/C smoke（仍靠 `make backend-test` / live LLM env）
- `start-dev.sh` 的 Web readiness 检查只验证 `GET /` 返回 HTML，不验证 `/lab` 路由内容
- deepseek-v3.2 的历史 research 文档（`docs/product/research/...`）未删除，仅作历史参考

## 4. 推荐下一步

无需立即跟进。当前三项收尾已完成，开发环境合约已生效。
