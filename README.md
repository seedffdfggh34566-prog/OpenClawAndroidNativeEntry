# OpenClawAndroidNativeEntry

> 仓库名保留历史来源；当前正式主线已切换为 **AI Sales Assistant V2 workspace-native planning baseline**。

当前建议先阅读：

1. [AGENTS.md](AGENTS.md)
2. [docs/README.md](docs/README.md)
3. [docs/delivery/tasks/_active.md](docs/delivery/tasks/_active.md)

---

## 当前定位

这个仓库现在应理解为：

- **AI 销售助手 App 的产品级 mono-repo**
- **V1 demo-ready baseline 的留存仓库**
- **V2 workspace-native Sales Agent / Sales Workspace Kernel 的当前规划与实现入口**
- **Android、backend、runtime、docs 共用的单一源工作区**

当前正式主线为：

> **Sales Workspace Kernel backend-only v0：用结构化 workspace、WorkspacePatch、候选排序、Markdown projection 和 ContextPack Compiler 验证 V2 backend 核心闭环。**

V1 已作为 demo-ready release candidate / learning milestone 收口，不再是默认开发方向。

---

## 当前执行入口

当前 active task：

- [docs/delivery/tasks/task_v2_sales_workspace_kernel_backend_only_v0.md](docs/delivery/tasks/task_v2_sales_workspace_kernel_backend_only_v0.md)

当前只允许实现：

- Pydantic schema
- in-memory / JSON fixture store
- WorkspacePatch apply
- deterministic candidate ranking
- Markdown projection
- ContextPack compiler
- pytest

当前不应自动实现：

- FastAPI endpoint
- SQLAlchemy ORM / Alembic migration / SQLite schema change
- Android UI
- LangGraph graph
- 真实 LLM / search provider
- CRM pipeline / ContactPoint / 自动触达

---

## 当前系统形态

- `backend/`
  - 当前正式业务后端与 V2 kernel prototype 位置
  - V2 backend-only v0 新增代码应进入 `backend/sales_workspace/`
- `app/`
  - Android 控制入口；当前不是 V2 kernel v0 的实现范围
- `docs/`
  - 产品方向、架构、任务、handoff 与 runbook 的正式入口
- `backend/runtime/`
  - Runtime / LangGraph Runtime 的未来执行层边界；当前 task 不接入

Sales Workspace Kernel 是正式对象写回裁决层，不是 Runtime graph，也不是 Dev Agent。

---

## 当前推荐阅读顺序

无论是人工开发者还是 Dev Agent，进入仓库后建议按以下顺序阅读：

1. [AGENTS.md](AGENTS.md)
2. [docs/README.md](docs/README.md)
3. [docs/product/overview.md](docs/product/overview.md)
4. [docs/product/prd/ai_sales_assistant_v2_prd.md](docs/product/prd/ai_sales_assistant_v2_prd.md)
5. [docs/adr/ADR-006-v2-conversational-sales-agent-baseline.md](docs/adr/ADR-006-v2-conversational-sales-agent-baseline.md)
6. [docs/architecture/workspace/workspace-object-model.md](docs/architecture/workspace/workspace-object-model.md)
7. [docs/architecture/workspace/sales-workspace-kernel.md](docs/architecture/workspace/sales-workspace-kernel.md)
8. [docs/architecture/workspace/workspace-kernel-v0-scope.md](docs/architecture/workspace/workspace-kernel-v0-scope.md)
9. [docs/delivery/tasks/_active.md](docs/delivery/tasks/_active.md)
10. 当前 task 引用的 handoff

开发协作中的 agent 术语边界参考：

- [docs/how-to/operate/dev-agent-vs-sales-agent-runbook.md](docs/how-to/operate/dev-agent-vs-sales-agent-runbook.md)

---

## 当前仓库结构

```text
OpenClawAndroidNativeEntry/
├─ app/          # Android 控制入口
├─ backend/      # 后端与 Sales Workspace Kernel v0 prototype
├─ docs/         # 正式文档、任务与 handoff
└─ ...
```

正式 docs 结构：

```text
docs/
├─ README.md
├─ product/
├─ architecture/
│  └─ workspace/
├─ reference/
├─ how-to/
├─ adr/
├─ delivery/
└─ archive/
```

---

## 常用验证命令

当前 backend 测试：

```bash
backend/.venv/bin/python -m pytest backend/tests -q
```

当前 Android 轻量入口检查：

```bash
./gradlew :app:tasks --offline
```

V2 Sales Workspace Kernel v0 实现后应额外固定运行：

```bash
backend/.venv/bin/python -m pytest backend/tests/sales_workspace -q
```

---

## 历史背景

这个仓库起源于早期 OpenClaw Android Native Entry / HarmonyOS 宿主入口实验，因此仓库名和部分历史资料保留旧痕迹。

这些内容现在只作为背景参考，统一放在：

- [docs/archive/openclaw/README.md](docs/archive/openclaw/README.md)

历史资料不再主导当前 V2 workspace-native Sales Agent 的方向、任务入口或日常工作流。
