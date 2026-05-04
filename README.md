# OpenClaw

> 仓库名保留历史来源；当前主线已切换为 **V3 Agent Sandbox-first Memory-native Sales Agent**。
>
> V2.1 作为 historical validated prototype 保留，不再作为默认开发方向。

进入仓库后优先阅读：

1. [AGENTS.md](AGENTS.md)
2. [docs/README.md](docs/README.md)
3. [docs/product/project_status.md](docs/product/project_status.md)
4. [docs/delivery/tasks/_active.md](docs/delivery/tasks/_active.md)

---

## 当前定位

这个仓库现在应理解为：

- **AI 销售助手 App 的产品级 mono-repo**
- **V3 Agent Sandbox-first Memory-native Sales Agent 的 POC 与实现入口**
- **Android、backend、Web `/lab`、docs 共用的单一源工作区**

当前正式主线为：

> **V3 Agent Sandbox-first Memory-native Sales Agent。**

当前已验证方向：session-scoped core memory blocks + native memory tool loop、`/v3/sandbox` backend-only runtime POC、`/lab` 内部测试入口、seed/reset/replay 控制、opt-in sandbox DB persistence、Settings runtime config、fullscreen Trace Inspector、recursive context summary with message-id cursor、layered smoke tests（A/B/C）。

V2.1 Sales Workspace Kernel、Draft Review、Postgres persistence、chat-first prototype 作为 historical validated prototype 保留，不再是默认开发方向。

V1 已冻结为 demo-ready release candidate / learning milestone。

---

## 当前执行入口

当前 active task 以 [docs/delivery/tasks/_active.md](docs/delivery/tasks/_active.md) 为准。

当前默认不得自动实现：

- production hardening / 新增 API surface
- 未经 task 开放的真实 LLM 扩展 / search provider
- CRM pipeline / ContactPoint / 自动触达
- V2.2 evidence / search / ContactPoint
- production SaaS / auth / tenant

---

## 当前系统形态

- `backend/`
  - 当前 API edge 与 sandbox runtime host
  - `/v3/sandbox`：V3 sandbox runtime POC（LangGraph native tool loop + TokenHub LLM runtime + core memory blocks + recursive summary）
  - FastAPI + SQLite（当前默认 persistence baseline）
- `web/`
  - React + Vite 内部测试入口 `/lab`
  - Settings、Trace Inspector、seed/reset/replay 控制面
- `app/`
  - Android 控制入口；历史 V2 workspace read-only demo 保留
- `docs/`
  - 产品方向、架构、任务、handoff 与 runbook 的正式入口

---

## 常用验证命令

V3 sandbox runtime（Level B smoke）：

```bash
make backend-test
```

V3 sandbox runtime（全量）：

```bash
make test
```

启动本地开发环境：

```bash
make dev        # 启动 backend + web
make dev-smoke  # 启动并运行 Level A smoke check
```

Android 轻量入口检查：

```bash
./gradlew :app:tasks --offline
```

---

## 仓库结构

```text
OpenClawAndroidNativeEntry/
├─ app/          # Android 控制入口
├─ backend/      # 后端 API 与 V3 sandbox runtime
├─ web/          # React /lab 内部测试入口
├─ scripts/      # 开发环境启动脚本
├─ docs/         # 正式文档、任务与 handoff
└─ ...
```

正式 docs 结构：

```text
docs/
├─ README.md
├─ product/
├─ architecture/
│  └─ v3/
├─ reference/
├─ how-to/
├─ adr/
├─ delivery/
└─ archive/
```

---

## 历史背景

这个仓库起源于早期 OpenClaw Android Native Entry / HarmonyOS 宿主入口实验，因此仓库名和部分历史资料保留旧痕迹。

V2 历史资产可按需参考，但不再作为当前默认开发方向：

- [docs/archive/openclaw/README.md](docs/archive/openclaw/README.md)
- [docs/architecture/workspace/](docs/architecture/workspace/)

当前项目阶段状态以 [docs/product/project_status.md](docs/product/project_status.md) 为准；task / handoff 只作为证据，不自行定义产品阶段完成。
