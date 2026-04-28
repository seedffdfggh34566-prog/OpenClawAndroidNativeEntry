# Task: V2.1 Lightweight Workspace Start Entry Polish

更新时间：2026-04-28

## 1. 任务定位

- 任务名称：V2.1 Lightweight Workspace Start Entry Polish
- 建议路径：`docs/delivery/tasks/task_v2_1_chat_first_workspace_start_gap_closure.md`
- 当前状态：`planned`
- 优先级：P0
- 任务类型：`delivery / polish`
- 是否属于 delivery package：`yes`
- 所属 package：`V2.1 Milestone Acceptance And Gap Closure`

---

## 1.1 队列衔接

- 当前 task 是否允许执行 agent 自主推进：`yes`
- 当前 task 内部 steps 是否允许连续执行：`yes`
- 完成后是否允许自动进入下游任务：`no`
- 建议上游入口：`docs/delivery/tasks/_active.md`
- 建议下游任务：
  1. milestone review addendum / project status refresh
- 自动继续条件：
  - 只处理 V2.1 lightweight start button product entry polish。
  - 不新增 backend public API。
  - 不新增 migration。
- 停止条件：
  - 需要多 workspace 管理、账号、租户、权限或 production onboarding。
  - 需要新增 backend endpoint 或 schema。
  - 需要改变 V2.1 PRD / ADR 含义。

---

## 1.2 自动化契约

- 本任务允许编辑：
  - Android workspace screen / app state / backend client 的最小入口 polish。
  - V2.1 task、handoff、project status、milestone review addendum。
- 本任务禁止编辑：
  - backend public API surface。
  - Alembic migration / schema baseline。
  - V2.2 search / ContactPoint / CRM。
  - formal LangGraph。
  - auth / tenant / production SaaS。
- 可在任务内连续完成的 steps：
  1. 读取 `app/AGENTS.md`。
  2. 复核当前 Android Workspace onboarding flow。
  3. 将技术化入口文案产品化为“开始销售工作区”。
  4. 点击后使用现有 `POST /sales-workspaces` 创建或进入默认 workspace，并展示 chat-first 输入。
  5. 保持已存在 workspace 的 chat submit 行为不变。
  6. 更新 task / handoff / review addendum。
- 必须拆出独立 task 或停止确认的情况：
  - 需要新增 backend endpoint。
  - 需要 workspace selector、多 workspace lifecycle 或登录态。

---

## 2. 任务目标

让 Android 控制入口满足 V2.1 PRD 的修正后最小要求：

> 用户无需理解 workspace；首次使用时可点击轻量按钮“开始销售工作区”，进入聊天后再用自然语言表达业务。

具体行为：

- 如果 `ws_demo` 已加载，直接展示 chat-first 输入，chat submit 行为保持现状。
- 如果 `ws_demo` 不存在或尚未加载，用户点击“开始销售工作区”，Android 使用已有 `POST /sales-workspaces` 创建默认 `ws_demo`，随后刷新并展示 chat-first 输入。
- 不要求用户首句自然语言自动创建 workspace，也不要求同一点击同时触发 `ConversationMessage` / `AgentRun`。
- 创建 workspace 失败但 backend 表示 workspace 已存在时，应刷新并进入聊天，不要求新增后端语义。

---

## 3. 当前背景

Milestone acceptance review 初版将“一句话启动 SalesWorkspace”判为 V2.1 implementation gap。2026-04-28 产品讨论后，该要求弱化为轻量开始按钮：用户无需理解 workspace，但可以点击“开始销售工作区”进入聊天。因此本任务不再要求首句自然语言自动创建 workspace，只做产品入口 polish。

---

## 4. 范围

本任务 In Scope：

- Android Workspace 页面最小启动流。
- 使用现有 backend endpoint。
- 最小 Android build 验证。
- 更新 acceptance review addendum。

本任务 Out of Scope：

- 新 backend endpoint。
- 多 workspace selector。
- 登录、租户、权限。
- V2.2 search / ContactPoint。
- formal LangGraph。
- production onboarding。

---

## 5. 涉及文件

高概率涉及：

- `app/src/main/java/com/openclaw/android/nativeentry/ui/workspace/SalesWorkspaceScreen.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/OpenClawApp.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/data/backend/SalesWorkspaceBackendClient.kt`

参考文件：

- `docs/product/research/v2_1_milestone_acceptance_review_2026_04_28.md`
- `docs/product/prd/ai_sales_assistant_v2_prd.md`
- `docs/architecture/runtime/v2-1-chat-first-runtime-design.md`

---

## 6. 产出要求

至少应产出：

1. Android 最小 product entry polish。
2. task outcome。
3. handoff。
4. milestone review addendum 或 project status refresh。

---

## 7. 验收标准

满足以下条件可认为完成：

1. 用户在未加载 workspace 的情况下可点击“开始销售工作区”，Android 使用现有 endpoint 创建或进入默认 workspace。
2. 创建或进入默认 workspace 后展示 chat-first 输入。
3. 已加载 workspace 的 chat submit 不回退。
4. 不新增 backend API、migration 或 V2.2 能力。
5. `./gradlew :app:assembleDebug` 通过。
6. 如可用，补充最小 device smoke；不可用时明确记录未验证项。

---

## 8. 推荐执行顺序

建议执行顺序：

1. 读取 `app/AGENTS.md`。
2. 检查当前 `OpenClawApp` 与 `SalesWorkspaceScreen` submit flow。
3. 做最小 Android 入口文案 / 状态改动。
4. 运行 `./gradlew :app:assembleDebug`。
5. 更新 task、handoff 和 milestone review addendum。

---

## 9. 风险与注意事项

- 不要把本任务扩展成完整 onboarding 系统。
- 不要新增后端接口；复用已有 `POST /sales-workspaces`。
- 不要实现首句自然语言自动创建并提交 agent turn。
- 不要自动进入 V2.2。

---

## 10. 下一步衔接

本任务完成后，推荐：

1. 重新更新 V2.1 milestone acceptance review。
2. 由规划层判断 V2.1 product milestone 是否仍有 `partial / missing` implementation gap。

---

## 11. 实际产出

任务执行完成后补充。

---

## 12. 本次定稿边界

任务执行完成后补充。

---

## 13. 已做验证

任务执行完成后补充。

---

## 14. 实际结果说明

任务执行完成后补充。
