# 后端优先阶段的 Codex 工作流

更新时间：2026-04-23

## 1. 文档定位

本文档用于说明在“后端优先、多端入口”的新阶段，开发者与 Codex 应如何使用当前仓库和文档体系推进开发。

它重点回答：

- 进入仓库后先看哪些文件
- 什么时候改方向文档，什么时候改 task
- agent 做完任务后必须回写哪些文件
- 当前如何从人工调度走向后续自动化

---

## 2. 当前最小标准流程

一次正式开发任务，建议按以下顺序推进：

1. 读取 `AGENTS.md`
2. 读取 `docs/README.md`
3. 查看 `docs/delivery/tasks/_active.md`
4. 打开对应 task
5. 阅读 task 引用的 PRD / spec / decision
6. 实施最小可行改动
7. 做最轻量但有意义的验证
8. 更新 task 状态
9. 写 handoff

---

## 3. 你应该看什么

### 3.1 判断当前方向

先看：

- `docs/product/overview.md`
- `docs/product/prd/ai_sales_assistant_v1_prd.md`
- `docs/adr/ADR-001-backend-deployment-baseline.md`

### 3.2 判断当前任务

再看：

- `docs/delivery/tasks/_active.md`
- 当前 task 文件

### 3.3 判断当前实现边界

必要时再看：

- `docs/architecture/system-context.md`
- `docs/reference/api/backend-v1-minimum-contract.md`
- `docs/architecture/repository-layout.md`

---

## 4. 你应该改什么

### 4.1 当方向变化时

优先改：

- `docs/product/overview.md`
- `docs/product/*`
- 必要时 `docs/adr/*`

不要先改代码。

### 4.2 当要开始一个新任务时

优先改：

- `docs/delivery/tasks/_active.md`
- 新 task 文件

### 4.3 当执行方式或运行方式改变时

优先改：

- `docs/architecture/*`
- `docs/reference/*`
- `docs/how-to/*`

### 4.4 当任务完成时

必须改：

- 当前 task 文件
- 对应 handoff 文件

---

## 5. agent 应维护什么

当前默认由 agent 主动维护：

- `docs/architecture/*`
- `docs/reference/*`
- `docs/delivery/tasks/*`
- `docs/how-to/*`
- `docs/delivery/handoffs/*`

当前不应由 agent 静默改写：

- `docs/product/overview.md`
- `docs/product/*`
- `docs/adr/*`

如果需要调整这些文件，应在回复中明确说明这是方向或决策层变更。

---

## 6. 当前推荐的任务粒度

Codex 当前最适合的任务粒度应满足：

- 单任务目标清楚
- 文件范围相对集中
- 可在一次 thread 中收口
- 最好在一小时左右的人类工作量内可以描述清楚

当前不建议：

- 一次线程混入多个大目标
- 一边改方向一边写实现
- 让 agent 自己猜当前活跃任务

---

## 7. 从人工调度走向自动化的路径

## 7.1 当前阶段：人工调度

你负责：

- 确认方向
- 选择当前任务
- review 结果

Codex 负责：

- 读取文档
- 执行任务
- 回写 task 与 handoff

## 7.2 下一阶段：半自动执行

后续可以先把以下工作交给定时 automation：

- 检查 `docs/delivery/tasks/_active.md` 是否与任务状态一致
- 汇总构建失败与测试失败
- 扫描 stale handoff / stale task
- 对低风险文档漂移提出修复建议

## 7.3 再下一阶段：受控自治

后续允许 agent 定时执行：

- 小型文档修复
- 小型测试补全
- 低风险重构建议
- task 巡检与状态更新建议

但以下内容仍建议保留人工批准：

- 版本方向变化
- 关键架构变更
- 数据迁移
- 部署与密钥操作
- 自动 push / 自动 merge

---

## 8. 当前最推荐的下一步工作方式

当前最推荐的推进方式为：

1. 用 `docs/delivery/tasks/_active.md` 明确当前唯一活跃任务
2. 让 Codex 只围绕该任务推进
3. 任务结束后写 handoff
4. 再切下一个任务

这样做的目的是：

- 降低上下文漂移
- 降低超范围修改
- 为未来自动化留下稳定接口

---

## 9. 当前后端本地命令

当前最小后端已落地后，推荐使用以下命令：

### 9.1 初始化后端环境

```bash
python3 -m venv backend/.venv
backend/.venv/bin/pip install -e backend
```

### 9.2 启动后端

```bash
backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013
```

### 9.3 运行后端测试

```bash
backend/.venv/bin/python -m unittest backend.tests.test_api
```

### 9.4 最小手工验证

至少验证：

1. `GET /health`
2. `POST /product-profiles`
3. `POST /analysis-runs` with `lead_analysis`
4. `POST /analysis-runs` with `report_generation`
5. `GET /history`
