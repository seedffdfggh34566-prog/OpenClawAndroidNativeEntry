# Handoff: V2.1 LLM Runtime Boundary Design

日期：2026-04-28

## Changed

- 新增 `task_v2_1_llm_runtime_boundary_design.md`。
- 新增 `docs/architecture/runtime/v2-1-llm-runtime-boundary.md`。

## Result

V2.1 允许 Tencent TokenHub LLM 参与 chat-first Product Sales Agent turn，但 LLM 只属于 Runtime execution layer。

正式写回仍必须经过：

```text
WorkspacePatchDraft -> Draft Review -> WorkspacePatch -> Sales Workspace Kernel
```

## Validation

- 文档边界检查。
- `git diff --check`。

## Limitations

- 尚未实现 backend LLM runtime。
- 尚未定义 LLM structured output contract。
- 尚未运行真实 TokenHub smoke。

## Next Step

执行 `task_v2_1_llm_provider_dev_baseline.md`，复用现有 Tencent TokenHub client，并新增 V2.1 sales-agent runtime mode 配置。
