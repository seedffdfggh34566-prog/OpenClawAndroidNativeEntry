# 文档导航

更新时间：2026-04-24

## 1. 文档定位

本文件是当前仓库文档系统的总入口。

它主要服务以下目标：

- 让开发者快速知道当前项目主线是什么
- 让 Codex / agent 快速知道应先读哪些文件
- 让新 docs 结构成为正式唯一入口
- 减少后续多端与后端推进时的文档歧义

---

## 2. 当前项目一句话说明

当前仓库已不再以早期 OpenClaw Android Native Entry 实验为主线。

当前正式主线为：

> **AI 销售助手 App V1：后端为正式主真相，多端入口作为控制层。**

---

## 3. 当前建议阅读顺序

无论是开发者还是 agent，进入仓库后建议按以下顺序阅读：

1. 根目录 `AGENTS.md`
2. `docs/product/overview.md`
3. `docs/product/prd/ai_sales_assistant_v1_prd.md`
4. `docs/adr/ADR-001-backend-deployment-baseline.md`
5. `docs/adr/ADR-002-v1-runtime-and-product-learning-baseline.md`
6. `docs/adr/ADR-003-v1-product-learning-runtime-boundary.md`
7. `docs/adr/ADR-004-v1-product-learning-iteration-contract.md`
8. `docs/delivery/tasks/_active.md`
9. 当前 task 引用的 spec / runbook / handoff

---

## 4. 当前文档结构如何使用

当前仓库正式采用以下文档结构：

- `product/`：产品方向、PRD、研究与路线图
- `architecture/`：系统分层、仓库结构与客户端 / runtime / data 方案
- `reference/`：API contract、领域模型与其他权威参考
- `how-to/`：运行、运维、协作和排障手册
- `adr/`：关键架构与部署决策
- `delivery/`：任务与交接文档
- `archive/`：历史资料归档

旧的编号目录已迁出，不再作为正式入口。

---

## 5. 当前最重要的入口文件

### 5.1 项目方向

- `docs/product/overview.md`
- `docs/product/prd/ai_sales_assistant_v1_prd.md`
- `docs/adr/ADR-001-backend-deployment-baseline.md`
- `docs/adr/ADR-002-v1-runtime-and-product-learning-baseline.md`
- `docs/adr/ADR-003-v1-product-learning-runtime-boundary.md`
- `docs/adr/ADR-004-v1-product-learning-iteration-contract.md`

### 5.2 当前架构与后端方向

- `docs/architecture/system-context.md`
- `docs/reference/api/backend-v1-minimum-contract.md`
- `docs/reference/runtime-v1-observability-eval-baseline.md`
- `docs/architecture/repository-layout.md`
- `docs/architecture/backend/backend-agent-stack-phased-adoption.md`
- `docs/architecture/runtime/langgraph-runtime-architecture.md`
- `docs/architecture/clients/android-client-implementation-constraints.md`

### 5.3 当前执行入口

- `docs/delivery/tasks/_active.md`
- `docs/delivery/README.md`
- `docs/delivery/tasks/task_v1_product_learning_runtime_decision_freeze.md`
- `docs/delivery/tasks/task_v1_product_learning_runtime_followup.md`
- `docs/delivery/handoffs/handoff_2026_04_24_product_learning_runtime_decision_freeze.md`

### 5.4 当前工作流

- `docs/how-to/operate/developer_workflow_playbook.md`
- `docs/how-to/operate/jianglab_codex_ops.md`
- `docs/how-to/operate/codex_backend_first_workflow.md`

### 5.5 目录级入口

- `docs/product/README.md`
- `docs/architecture/README.md`
- `docs/reference/README.md`
- `docs/how-to/README.md`
- `docs/adr/README.md`
- `docs/delivery/README.md`

---

## 6. 当前 agent 文档工作原则

当前推荐把文档分成三层理解：

1. **方向层**
   - `product/overview.md`
   - `product/prd/*`
   - `adr/*`
2. **方案层**
   - `architecture/*`
   - `reference/*`
   - `how-to/*`
3. **执行层**
   - `delivery/tasks/*`
   - `delivery/handoffs/*`

agent 的标准动作应为：

1. 先确认方向层没有变化
2. 再读取方案层确认边界
3. 最后在执行层领取和推进任务

---

## 7. 当前结构摘要

当前文档系统按以下结构运行：

```text
docs/
├─ README.md
├─ product/
├─ architecture/
├─ reference/
├─ how-to/
├─ adr/
├─ delivery/
└─ archive/
```

当前阶段最重要的是：

- 用新结构稳定承接后端与客户端后续任务
- 让 agent 工作流统一依赖 `docs/README.md` 与 `docs/delivery/tasks/_active.md`
- 避免再次回到旧编号目录

---

## 8. 当前最推荐的下一步

当前 product learning LLM、Android iteration UI、真机 enrich smoke、Android 销售闭环产品表达收口与完整 V1 真机端到端 smoke 已完成。

下一步需要规划层决定优先进入哪条路线：

1. 真实样例评估 / prompt tuning follow-up
2. ProductLearning UI polish
3. 真机 smoke 自动化输入机制改进

当前补充建议阅读：

- `docs/delivery/tasks/_active.md`
- `docs/delivery/README.md`
- `docs/delivery/handoffs/`
