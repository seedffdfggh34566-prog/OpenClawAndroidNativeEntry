# Handoff：LangGraph + Letta-style Memory 方向轻量文档沉淀

日期：2026-04-29

## 1. 变更摘要

本次只做文档方向沉淀，不改代码。

核心结论：

- Product Sales Agent runtime 后续优先走 LangGraph / LangChain 自研路线。
- Letta server 暂不作为第一接入 runtime；Letta 的 memory blocks、archival memory 和自编辑工具模式作为设计参考。
- Runtime memory 可以保存推断、假设、策略、纠错和被废弃信息。
- 正式业务对象写回仍由 backend services / Sales Workspace Kernel 裁决。

## 2. 触及文件

- `docs/architecture/runtime/langgraph-letta-style-sales-agent-memory.md`
- `docs/adr/ADR-008-v2-langgraph-letta-style-memory-direction.md`
- `docs/product/prd/ai_sales_assistant_v2_prd.md`
- `docs/architecture/runtime/README.md`
- `docs/adr/README.md`
- `docs/README.md`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/tasks/task_2026_04_29_langgraph_letta_memory_direction_docs.md`

## 3. 验证

- `git diff --check`
- `rg "LangGraph \\+ Letta-style|Letta-style|ADR-008|self-edit memory|自编辑" docs`

## 4. 已知边界

- 未实现 LangGraph runtime。
- 未接入 LangChain 或 Letta。
- 未新增 DB schema、migration 或 API contract。
- 未开放 V2.2 search / ContactPoint 实现。
- 后续 implementation 需要单独 task。

## 5. 推荐下一步

如果继续推进实现，建议单独创建 `LangGraph / LangChain Sales Agent runtime POC` task，先验证：

- 腾讯云 API 通过 LangChain 或 OpenClaw LLM Gateway 调用。
- Product Sales Agent 可通过工具自编辑 memory。
- 自编辑 memory 能影响后续多轮回答。
- 正式对象写回仍经过 backend gate。
