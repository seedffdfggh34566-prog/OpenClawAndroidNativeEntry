# Handoff: V2.1 Trace Message History Visibility

更新时间：2026-04-28

## 1. 本次改了什么

- Android backend client 新增 `listConversationMessages`。
- Android parser/model 增加 conversation messages response。
- Workspace 页面展示最近 8 条 `ConversationMessage`。
- `_active.md` 衔接到 P4 LLM prompt quality follow-up。

---

## 2. 为什么这么定

- 后端已有 messages endpoint，第一阶段 trace visibility 不需要新增 backend API。
- 只展示 messages，避免把 P3 扩展成 AgentRun / DraftReview history browser。

---

## 3. 本次验证了什么

1. `./gradlew :app:assembleDebug`

---

## 4. 已知限制

- 只展示最近 8 条消息。
- 不展示 AgentRun 列表、ContextPack detail 或 WorkspaceCommit diff。
- 未做真机手动 smoke；最终 package closeout 应补充设备情况。

---

## 5. 推荐下一步

继续 P4：扩充 V2.1 LLM runtime fake-client quality tests 和 eval 记录。

