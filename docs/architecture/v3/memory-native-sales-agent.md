# V3 Sandbox-first Memory-native Sales Agent Architecture

更新时间：2026-04-30

## 1. 定位

本文档是 V3 的轻量架构入口。它合并说明 runtime、memory、working state 和 backend infrastructure 的关系，不冻结具体 schema、API 或 graph 实现。

---

## 2. 推荐分层

```text
Android control entry
Web /lab developer test surface
Web /workspace user prototype
  -> OpenClaw Backend API
    -> Product Sales Agent Runtime (LangGraph / LangChain)
      -> Tencent Cloud API or OpenClaw LLM Gateway
      -> Memory tools
      -> Sandbox workspace working state
      -> Customer intelligence working state
    -> Backend infrastructure: runtime host / storage / trace / API
```

---

## 3. Memory-native 原则

V3 Product Sales Agent 可以维护长期认知 memory：

- 用户偏好。
- 产品理解。
- 销售策略。
- 工作假设。
- workspace working state。
- customer intelligence working state。
- 被用户纠正的信息。
- 已拒绝或被替代的信息。

Memory 可以保存推断和假设，但必须带状态或可解释上下文。推荐状态词为：

```text
observed / inferred / hypothesis / confirmed / rejected / superseded
```

这些状态用于解释和修正，不用于提前禁止 agent 思考。

---

## 4. Runtime 原则

V3 runtime 优先采用 LangGraph / LangChain，但 LangGraph checkpoint 不是业务主存。

Runtime 可以：

- 读取和更新认知 memory。
- 维护 sandbox workspace working state。
- 维护早期 customer intelligence working state。
- 调用模型与工具。
- 形成策略和下一步建议。
- 记录 agent actions、trace 和可回放上下文。

Runtime 不应：

- 被降级为 `WorkspacePatchDraft` 生成器。
- 在第一阶段被迫先满足 formal object / Kernel / Draft Review 路径。
- 执行真实外部触达、CRM 生产写入或不可逆导出。

---

## 5. Backend Infrastructure 原则

V3 第一阶段不把 backend formal governance 作为默认实现前提。Backend 初期职责是基础设施：

- runtime host。
- memory / working state storage。
- trace / event log。
- API surface。
- local/dev diagnostics。

Backend 不应在 V3 初期承担业务建档者或第一阶段裁决者角色。V2 的 Sales Workspace Kernel、Draft Review、`WorkspacePatchDraft` 和 formal writeback 是 historical validated assets，可供未来参考，但不是 V3 sandbox-first 的默认路径。

当前仍禁止真实外部触达、CRM 生产写入、不可逆导出和 production SaaS/auth/tenant。后续如果这些能力进入实现，再单独设计安全边界。

---

## 6. 多端入口原则

V3 可以引入 Web 双入口：

- `/lab`：内部开发者和产品测试入口，用于观察 memory、working state、agent actions、trace 和 replay。
- `/workspace`：真实销售用户 Web 雏形，用于验证工作流和信息架构。

Web 入口服务 V3 学习和验证，不改变 App-first 长期入口策略。详细边界见 `docs/architecture/v3/web-dual-entry-prototype.md`。

---

## 7. 后续 POC 建议

后续 implementation task 可优先验证：

- LangChain 调用腾讯云 API。
- Product Sales Agent 通过工具自编辑 memory。
- Memory 影响下一轮回答。
- 用户纠错能 supersede 旧记忆。
- Agent 维护 customer intelligence working state、候选客户排序理由和打分草案。
- Web `/lab` 能支持人工和 Playwright 验证 memory / working state / trace / replay。
