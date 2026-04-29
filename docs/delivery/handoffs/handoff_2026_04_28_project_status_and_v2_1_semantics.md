# 阶段性交接：Project Status And V2.1 Completion Semantics

更新时间：2026-04-28

## 1. 本次改了什么

- 新增 `docs/product/project_status.md`，作为当前项目阶段状态的权威入口。
- 新增 `docs/product/research/v2_1_completion_semantics_correction_2026_04_28.md`，修正 V2.1 completed / closeout 的解释边界。
- 更新 `AGENTS.md` 和 developer workflow playbook，禁止普通 task / handoff 自行声明产品阶段完成。
- 更新 README、docs README、product overview、roadmap、delivery README 和 `_active.md`，将 V2.1 口径调整为：
  - `V2.1 validated prototype path completed`
  - `V2.1 product milestone remains open under planning control`
- 为关键历史 review / package / handoff 增加 interpretation note，保留 evidence 但不再作为完整 V2.1 milestone closeout 依据。

---

## 2. 为什么这么定

- `_active.md` 应只作为执行授权入口，不承担项目阶段判断。
- task / handoff 是执行证据，不是产品阶段完成标准。
- 既有 V2.1 evidence 能证明 prototype path，但不能自动升级为完整 V2.1 product milestone completed。

---

## 3. 本次验证了什么

已完成验证：

1. `git diff --check`
   - 结果：通过。
2. `rg -n "V2\\.1.*completed|V2\\.1.*完成|product experience prototype completed|final closeout|下一步只允许" README.md docs`
   - 结果：入口文档已改为 `validated prototype path` / `product milestone remains open` 口径；剩余命中为历史 evidence、任务名、验证命令或带有 correction / interpretation note 的历史文件。
3. `rg -n "project_status|validated prototype path|product milestone remains open|Milestone Completion Claims|阶段完成判断规则" README.md docs AGENTS.md`
   - 结果：新状态入口、规则层约束和入口文档引用均可检索。

---

## 4. 已知限制

- 本次没有修改 backend / Android 代码。
- 本次没有开放新的 current delivery package 或 task。
- 本次没有重写所有历史 task / handoff，只对关键历史结论增加 supersession / interpretation note。
- V2.2 evidence / search / ContactPoint implementation、formal LangGraph、CRM、自动触达和 production SaaS 仍 blocked。

---

## 5. 推荐下一步

1. 若继续 V2.1，应由规划层开放一个 V2.1 continuation delivery package。
2. 优先候选包括 demo reproducibility、Android onboarding / workspace creation、LLM prompt quality、trace / history visibility、Postgres verification。
3. 后续 Dev Agent 做项目进度评估时，应先读 `docs/product/project_status.md`，再读 `_active.md` 和 task / handoff evidence。
