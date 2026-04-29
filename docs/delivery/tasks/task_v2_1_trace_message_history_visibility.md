# Task: V2.1 Trace Message History Visibility

更新时间：2026-04-28

## 1. 任务定位

- 任务名称：V2.1 Trace Message History Visibility
- 建议路径：`docs/delivery/tasks/task_v2_1_trace_message_history_visibility.md`
- 当前状态：`done`
- 优先级：P1
- 任务类型：`delivery`
- 是否属于 delivery package：`yes`
- 所属 package：`V2.1 Implementation Continuation`

---

## 2. 任务目标

在 Android Workspace 页面展示最小 ConversationMessage history，让 V2.1 chat-first trace 可复看。

---

## 3. 范围

In Scope：

- Android client 复用 `GET /sales-workspaces/{workspace_id}/messages`。
- Workspace 页面展示最近 8 条 conversation messages。

Out of Scope：

- 新增 AgentRun list API。
- DraftReview history browser。
- WorkspaceCommit diff viewer。
- V2.2 search / ContactPoint。

---

## 4. 实际产出

- 新增 `listConversationMessages` Android client 方法。
- 新增 conversation messages response DTO / parser。
- `OpenClawApp` 在刷新 workspace、创建 workspace、提交 chat turn、apply draft 后同步更新 message history。
- `SalesWorkspaceScreen` 展示最近 8 条消息的 role、message_type、id 和 content。

---

## 5. 已做验证

- `./gradlew :app:assembleDebug`

---

## 6. 实际结果说明

本任务未新增 backend endpoint；只消费已有 messages endpoint。AgentRun 列表和 DraftReview history 留给后续独立任务。

