# Delivery Package: V2.1 Milestone Acceptance And Gap Closure

更新时间：2026-04-28

## 1. Package 定位

- Package 名称：V2.1 Milestone Acceptance And Gap Closure
- 建议路径：`docs/delivery/packages/package_v2_1_milestone_acceptance_and_gap_closure.md`
- 当前状态：`done`
- 优先级：P0
- Package 类型：`closeout / delivery`
- Authorization source：human instruction on 2026-04-28: "PLEASE IMPLEMENT THIS PLAN"
- 是否允许 package 内部 tasks / steps 连续执行：`yes`
- 完成后是否允许自动进入下游 package：`no`

---

## 2. 目标

本 package 用于回答一个明确问题：

> V2.1 是否真的已经实现？

判断标准不是 task / handoff 的 `done`，而是 V2 PRD、roadmap、ADR 和 architecture baseline 对 V2.1 的成功标准。只有当每项 V2.1 PRD criterion 都具备 acceptance source、code evidence 和 validation evidence，或被明确判为 out of scope，才能建议将 V2.1 product milestone 升级为 implemented / done。

2026-04-28 产品决策更新：

- 不再要求用户首句自然语言自动创建 `SalesWorkspace` 并触发同一轮 agent turn。
- V2.1 首次入口弱化为轻量按钮“开始销售工作区”。
- 用户无需理解 workspace；点击按钮后系统创建或进入默认 workspace，并展示聊天入口。
- 当前 package 的剩余任务从 implementation gap closure 降级为 product entry polish。

---

## 3. Package 内任务 / Steps

固定顺序：

1. `docs/delivery/tasks/task_v2_1_milestone_acceptance_review.md`（done）
2. `docs/delivery/tasks/task_v2_1_chat_first_workspace_start_gap_closure.md`（done，re-scoped to lightweight start button entry polish）

如果 product entry polish 后仍发现新的 V2.1 PRD implementation gap，应在本 package 内新增具体 V2.1 task；如果 gap 需要新 API、migration、外部 provider 或产品方向变更，应停止并交回人工决策。

---

## 4. 允许范围

允许编辑：

- V2.1 milestone review、task、handoff 和 project status 文档。
- V2.1 Android workspace entry 的轻量产品入口 polish。
- 仅为验证 V2.1 product entry polish 所需的 Android build。

禁止编辑：

- V2.2 search / evidence / ContactPoint implementation。
- formal LangGraph graph。
- CRM、自动触达、批量联系人。
- production SaaS、多用户、租户、权限。
- 新增 backend public API endpoint。
- 新增 Alembic migration 或 schema baseline 变更。
- PRD / ADR 产品含义变更。

---

## 5. Auto-continue 条件

本 package 当前已完成；以下为执行期间适用的历史条件。

- 当前 task 明确列在本 package 内。
- 变更只服务 V2.1 lightweight start button product entry polish。
- 不触发本 package stop conditions。
- 每个 task 必须单独记录 validation 和 handoff。

---

## 6. Stop Conditions

命中以下情况时停止并交回规划层：

- 需要新增 V2.2 search / ContactPoint / CRM 能力。
- 需要新增 backend public API endpoint、migration 或外部 provider。
- 需要把 Tencent TokenHub runtime 升级为 production-ready Product Sales Agent。
- 需要正式 LangGraph checkpoint / resume lifecycle。
- 需要改变 V2.1 PRD success criteria 或 ADR 边界。
- Android product entry polish 扩展成多 workspace、账号、租户或权限系统。

---

## 7. Package 验收标准

满足以下条件可关闭 package：

1. Milestone acceptance review 已完成，并逐项使用 `done / partial / missing / out of scope`。
2. 所有 `partial / missing` 且属于 V2.1 implementation gap 的条目已有对应 task。
3. 当前 product entry polish task 完成后，重新更新 milestone review 或补充 review addendum。
4. `docs/product/project_status.md` 与 `_active.md` 对当前阶段和授权状态一致。
5. V2.2 implementation 仍 blocked。

---

## 8. Package Closeout

当前 package 已完成当前执行范围；不声明 V2.1 product milestone 完成。

Correction on 2026-04-28：

- 2026-04-28 人工验收反馈指出 Android app 上没有看到聊天入口。
- 因此本 package closeout 中关于 lightweight entry polish 已满足 product entry 的表述，只能保留为历史 delivery evidence，不能作为 V2.1 product-entry done 或 milestone completion 标准。
- 当前 V2.1 状态以 `docs/product/project_status.md` 和 `docs/delivery/packages/package_v2_1_android_chat_entry_recovery.md` 为准。

已完成：

- Evidence-based V2.1 milestone acceptance review。
- 产品决策已将 chat-first one-sentence workspace start 弱化为轻量按钮“开始销售工作区”入口 polish。
- Android lightweight entry polish：历史代码和 build/install evidence 曾记录入口按钮文案产品化为“开始销售工作区”，点击后通过既有 `POST /sales-workspaces` 创建或进入默认 `ws_demo`；但当前人工验收未看到聊天入口，因此该项不能作为 product-entry done。
- `workspace_already_exists` 既有 409 backend 语义已在 Android 侧作为“进入现有 workspace”处理。
- 已补充 task outcome、handoff、milestone review addendum 和 project status refresh。

验证：

- `./gradlew :app:assembleDebug` 通过。
- `adb devices` 检测到设备 `f3b59f04	device`。
- `adb install -r app/build/outputs/apk/debug/app-debug.apk` 通过。
- `adb shell am start -n com.openclaw.android.nativeentry/.MainActivity` 可启动应用。
- `adb shell uiautomator dump` 可读取 app UI tree；设备恢复在历史 `分析报告` 内页，未自动完成 Workspace 页点击级 smoke。

后续：

- 已开放 `docs/delivery/packages/package_v2_1_android_chat_entry_recovery.md`。
- V2.1 product milestone 当前为 `partial / android_chat_entry_missing`。
