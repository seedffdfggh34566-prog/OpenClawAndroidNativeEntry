# Task: V2.1 LLM Runtime Boundary Design

状态：done

更新时间：2026-04-28

## Objective

定义 V2.1 chat-first Product Sales Agent 接入真实 LLM 时的边界：LLM 可以参与用户消息理解、追问、解释和 draft 生成，但不能成为 formal workspace truth layer。

## Scope

- 明确 Tencent TokenHub LLM runtime 属于 Runtime execution layer。
- 明确 Runtime 只产出 assistant message、clarifying questions 和 `WorkspacePatchDraft`。
- 明确正式写回仍必须经过 Draft Review 和 Sales Workspace Kernel。
- 明确本阶段不接正式 LangGraph、search、ContactPoint、CRM 或 Android 新 UI。

## Out Of Scope

- 不实现 backend code。
- 不改 API route。
- 不读取或记录 LLM API key。
- 不改变 Draft Review / WorkspacePatch formal writeback contract。

## Outcome

新增 `docs/architecture/runtime/v2-1-llm-runtime-boundary.md`，将 LLM 接入定位为 V2.1 runtime prototype boundary。

## Validation

```bash
rg "Tencent TokenHub|WorkspacePatchDraft|Draft Review|Sales Workspace Kernel" docs/architecture/runtime docs/delivery/tasks/task_v2_1_llm_runtime_boundary_design.md
git diff --check
```
