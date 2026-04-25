# 后端优先阶段的 agent 工作流

更新时间：2026-04-24

## 1. 文档定位

本文档用于说明在“后端优先、多端入口”的新阶段，开发者与 agent 应如何使用当前仓库和文档体系推进开发。

它重点回答：

- 进入仓库后先看哪些文件
- 什么时候改方向文档，什么时候改 task
- agent 做完任务后必须回写哪些文件
- 当前如何从人工调度走向受控自治

---

## 2. 当前最小标准流程

一次正式开发任务，建议按以下顺序推进：

1. 读取 `AGENTS.md`
2. 读取 `docs/README.md`
3. 查看 `docs/delivery/tasks/_active.md`
4. 打开当前 task
5. 阅读 task 引用的 PRD / spec / decision
6. 实施最小可行改动
7. 做最轻量但有意义的验证
8. 更新 task 状态
9. 写 handoff
10. 创建一个原子 commit
11. 若 next queued task 已写明且未命中 stop conditions，则继续

---

## 3. 你应该看什么

### 3.1 判断当前方向

先看：

- `docs/product/overview.md`
- `docs/product/prd/ai_sales_assistant_v1_prd.md`
- `docs/adr/ADR-001-backend-deployment-baseline.md`

### 3.2 判断当前任务队列

再看：

- `docs/delivery/tasks/_active.md`
- 当前 task 文件
- next queued tasks

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

## 5. 当前 agent 职责模型

当前默认采用 3 层职责：

- **执行 agent**：执行当前 task，验证，更新 task，写 handoff，提交 commit
- **规划层**：维护方向、优先级、task 队列、stop conditions
- **人工层**：方向变化、关键架构、部署、发布与高风险最终决策

这里的规则按职责写，不绑定具体工具身份。

---

## 6. 当前推荐的任务粒度

当前最适合的任务粒度应满足：

- 单任务目标清楚
- 文件范围相对集中
- 可在一次连续执行中收口
- 完成后能形成一个独立 commit

当前不建议：

- 一次连续运行混入多个未排定大目标
- 一边改方向一边写实现
- 让执行 agent 自己猜当前活跃任务

---

## 7. 从人工调度走向自动化的路径

## 7.1 当前阶段：轻约束自治

人工层负责：

- 确认方向
- 决定队列的起点和边界
- review 阶段性结果

规划层负责：

- 写清当前 task
- 写清 next queued tasks
- 写清 auto-continue allowed when
- 写清 stop conditions

执行 agent 负责：

- 读取文档
- 执行 task
- 回写 task 与 handoff
- 创建原子 commit
- 在边界内继续下一个已排定 task

## 7.2 下一阶段：受控自治

后续可以把以下工作进一步交给自动化：

- 检查 `docs/delivery/tasks/_active.md` 是否与任务状态一致
- 汇总构建失败与测试失败
- 扫描 stale handoff / stale task
- 对低风险文档漂移提出修复建议

## 7.3 保留人工批准的事项

以下内容仍建议保留人工批准：

- 版本方向变化
- 关键架构变更
- 数据迁移
- 部署与密钥操作
- 自动 push / 自动 merge

---

## 8. 当前最推荐的推进方式

当前最推荐的推进方式为：

1. 用 `docs/delivery/tasks/_active.md` 明确当前 task 与 next queued tasks
2. 让执行 agent 围绕该队列推进
3. 每个 task 结束后写 handoff
4. 每个 task 独立提交
5. 命中 stop conditions 时再回到规划层

这样做的目的是：

- 降低上下文漂移
- 降低超范围修改
- 保持连续开发能力
- 为未来自动化留下稳定接口

---

## 9. Stop Conditions

执行 agent 应停止并把控制权交回规划层，当出现以下情况时：

- 方向变化
- task 队列耗尽或不明确
- docs / contract / code 冲突
- 需要新基础设施、迁移或部署变化
- 连续验证失败说明任务边界可能错误
- 需要 push、merge 或其他高风险不可逆动作

只要未命中 stop conditions，执行 agent 就可以继续已排定 task 队列。

---

## 10. 当前后端本地命令

当前最小后端已落地后，推荐使用以下命令：

### 10.1 初始化后端环境

```bash
python3 -m venv backend/.venv
backend/.venv/bin/pip install -e backend
```

### 10.2 启动后端

```bash
backend/.venv/bin/alembic upgrade head
backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013
```

### 10.3 运行后端测试

```bash
backend/.venv/bin/python -m pytest backend/tests
```

### 10.4 最小手工验证

至少验证：

1. `GET /health`
2. `POST /product-profiles`
3. `POST /analysis-runs` with `lead_analysis`
4. `POST /analysis-runs` with `report_generation`
5. `GET /history`

### 10.5 数据库迁移检查

```bash
backend/.venv/bin/alembic check
```
