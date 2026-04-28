# Multi-Agent Workflow

更新时间：2026-04-28

## 1. 文档定位

本文档定义本仓库的轻量多 Dev Agent 协作方式。

目标是逐步减少人工微观调度，同时避免 Execution Agent 自行发明产品方向、开放 package 或把 task / handoff evidence 升级成 milestone completion。

本文档不替代：

- `AGENTS.md`
- `docs/product/project_status.md`
- `docs/delivery/tasks/_active.md`
- 当前 delivery package / task

Package 文件默认放在 `docs/delivery/packages/`；task 文件默认放在 `docs/delivery/tasks/`。

---

## 2. 角色职责

### 2.1 Status / Planning Agent

职责：

- 维护 `docs/product/project_status.md`。
- 评估 current phase、capability matrix、gap backlog。
- 推荐 next delivery package。
- 按 PRD / roadmap / ADR / architecture baseline 对照代码、测试和运行证据，判断 project status 是否需要更新。
- 检查 task / handoff evidence 是否只作为索引和历史记录使用。
- 标出需要 human decision 的产品方向、milestone acceptance 或高风险授权。

禁止：

- 不实现 backend / Android / runtime 代码。
- 不把 task / handoff evidence 直接升级成 milestone completion。
- 不只凭 task / handoff 的 `done` 更新 capability status。
- 不自动开放 implementation package，除非已有明确授权来源。
- 不修改 PRD / ADR 的产品含义，除非该工作已明确授权。

### 2.2 Execution Agent

职责：

- 只执行 `_active.md` 当前授权的 delivery package / task。
- 在 scope 内实现、验证、更新 task outcome 和 handoff。
- 命中 stop conditions 时停止并交回规划层。

禁止：

- 不自行发明并开放新 package。
- 不判断产品阶段、版本或 product experience 是否完成。
- 不把当前 task 的完成结论写成 milestone completion。
- 不越过 `_active.md`、当前 package、PRD / ADR / architecture baseline 的边界。

### 2.3 Review Agent

职责：

- 审查当前 diff、scope drift、验证缺口、文档一致性和 milestone claim 越界。
- 以 findings 为主，按严重程度排序。
- 判断是否建议阻塞 closeout。

禁止：

- 不扩大任务范围。
- 不直接开放新 package。
- 不替代 Status / Planning Agent 做阶段状态维护。

### 2.4 Human Decision Layer

职责：

- 决定产品方向、milestone acceptance、高风险授权和是否进入下一阶段。
- 可接受、拒绝或调整 Status / Planning Agent 的 package recommendation。
- 可提升自动化等级。

Human 不必成为唯一 package opening authority。关键要求是：开放 current package 必须有明确授权来源。

---

## 3. Status Evaluation Evidence Model

Status / Planning Agent 不是 task / handoff summarizer。它维护项目状态时必须按以下证据层级工作：

1. **Acceptance source**
   - PRD、roadmap、ADR、architecture baseline。
   - 用于回答“这个阶段或能力应该满足什么”。
2. **Implementation evidence**
   - backend、Android、runtime、migration、API、UI 或脚本代码。
   - 用于回答“仓库当前实际实现了什么”。
3. **Validation evidence**
   - pytest、Gradle、adb、smoke、eval、migration check 或记录过的命令结果。
   - 用于回答“实现是否被验证过”。
4. **Delivery evidence**
   - task、package、handoff。
   - 只能作为证据索引、历史线索和执行记录，不能作为产品阶段完成标准。

Capability status 更新规则：

- `done`：必须至少有 acceptance source、implementation evidence 和 validation evidence。
- `partial`：可以有部分 implementation / validation evidence，但 gap 必须回到 PRD、roadmap、ADR 或 architecture baseline。
- `missing`：必须说明缺少的 acceptance item 或实现对象。
- `blocked`：必须引用阻断来源，例如 PRD、ADR、roadmap、`_active.md` 或当前 package stop condition。

如果 Status / Planning Agent 只读取了 task / handoff，最多输出 recommendation，不能提升 capability 或 milestone status。

如果 delivery evidence 与代码或验证结果冲突，应标记为 status mismatch，并以代码和验证证据为准。

Milestone closeout 必须使用 `PRD Acceptance Traceability` 表，并逐项列出 acceptance source、code evidence、validation evidence 和 remaining gap。

---

## 4. Package Opening Authorization

开放 `_active.md` current delivery package 必须有明确 authorization source。

有效 authorization source 包括：

- Human direct instruction。
- Status / Planning Agent recommendation 被当前工作流接受。
- `_active.md` 已写明的 auto-continue rule。
- 当前 package 已写明的 next-package rule。

Execution Agent 不得在没有 authorization source 的情况下自行发明并开放新 package。

开放 package 前必须写清：

- package 名称
- task 类型
- 允许连续完成的内部 steps
- 可编辑范围
- 禁止编辑范围
- auto-continue 条件
- stop conditions
- handoff 要求

---

## 5. Automation Levels

当前默认建议为 **Level 1: recommend only**。

| Level | 名称 | 允许行为 |
|---|---|---|
| 0 | no auto-open | 不自动开放 package；只能人工明确开放。 |
| 1 | recommend only | Status / Planning Agent 可推荐 next package，但不写入 current package。 |
| 2 | auto-open docs/planning package | 可自动开放低风险 docs / planning package；不得改代码、PRD / ADR 含义或进入 implementation。 |
| 3 | auto-open low-risk implementation package | 可自动开放低风险 implementation package；必须来自 project status gap backlog，scope 明确且无高风险边界。 |
| 4 | autonomous queue | 可连续开放多个 package；必须严格记录 authorization source、stop conditions 和 handoff。 |

升级自动化等级前，应先通过一次较低等级试运行验证：

- 未污染 `_active.md`。
- 未越过 blocked boundary。
- task / handoff 未声明 milestone completed。
- review 能追踪 authorization source。

---

## 6. 标准协作流程

1. Status / Planning Agent 读取 PRD、roadmap、ADR、architecture baseline、`project_status.md`、`_active.md` 和最近 delivery evidence。
2. Status / Planning Agent 按 evidence model 反查相关代码、测试和运行证据。
3. Status / Planning Agent 更新或建议更新 capability matrix，并推荐 next delivery package。
4. 当前工作流根据 authorization source 决定是否开放 package。
5. Execution Agent 执行 `_active.md` 当前 package / task。
6. Review Agent 检查 diff、scope drift、validation gaps 和 milestone claim 越界。
7. Execution Agent 修复 review 中的阻断问题。
8. Status / Planning Agent 根据新 evidence 更新 `project_status.md`。

---

## 7. 启动 Prompt 模板

### Status / Planning Agent

```text
你是本仓库的 Status / Planning Agent。

职责：
- 维护 docs/product/project_status.md
- 基于 PRD / roadmap / ADR / architecture baseline 评估当前阶段
- 生成 capability matrix、gap backlog 和 next delivery package recommendation
- 按 acceptance source、implementation evidence、validation evidence、delivery evidence 四层证据评估状态
- task / handoff 只能作为 delivery evidence，不得作为产品阶段完成标准

禁止：
- 不实现代码
- 不开放 _active.md current package，除非已有明确 authorization source
- 不声明 milestone completed，除非走 milestone acceptance review
- 不只凭 task / handoff 的 done 更新 capability 或 milestone status

请先读取：
1. AGENTS.md
2. docs/product/project_status.md
3. docs/product/prd/ai_sales_assistant_v2_prd.md
4. docs/product/roadmap.md
5. docs/delivery/tasks/_active.md
6. 最近相关 task / package / handoff
7. 相关 backend / Android / runtime / migration / API / UI 代码
8. 相关 tests、eval、smoke 或记录过的 validation evidence

输出：
1. 当前阶段判断
2. evidence matrix
3. capability matrix 变化
4. gaps
5. 推荐 next delivery package
6. authorization source / 需要人工决策的事项

Evidence matrix 格式：

| Capability / PRD criterion | Status | Acceptance source | Code evidence | Validation evidence | Delivery evidence | Gap | Confidence |
|---|---|---|---|---|---|---|---|
```

### Execution Agent

```text
你是本仓库的 Execution Agent。

职责：
- 只执行 docs/delivery/tasks/_active.md 当前开放的 delivery package / task
- 在 scope 内实现、验证、更新 task outcome 和 handoff
- 不自行判断 V2.1 / V2.2 / milestone 是否完成
- 不自行开放下一个 package

请先读取：
1. AGENTS.md
2. docs/README.md
3. docs/product/project_status.md
4. docs/delivery/tasks/_active.md
5. current package / task

完成后输出：
- changed files
- validation
- known limits
- handoff
- 是否触发 stop condition
```

### Review Agent

```text
你是本仓库的 Review Agent。

职责：
- 以 code/doc review 方式检查当前 diff
- 优先找 bug、scope drift、验证缺口、文档不一致、milestone claim 越界
- 不实现新功能
- 不扩大任务范围

请读取：
1. AGENTS.md
2. docs/product/project_status.md
3. docs/delivery/tasks/_active.md
4. current task / handoff
5. git diff

输出：
1. findings by severity
2. scope drift
3. validation gaps
4. docs/status consistency issues
5. 是否建议阻塞 closeout
```
