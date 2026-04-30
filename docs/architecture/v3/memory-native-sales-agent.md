# V3 Memory-native Sales Agent Architecture

更新时间：2026-04-30

## 1. 定位

本文档是 V3 的轻量架构入口。它合并说明 runtime、memory 和 backend governance 的关系，不冻结具体 schema、API 或 graph 实现。

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
      -> WorkspacePatchDraft when formal writeback is needed
    -> Backend governance / Sales Workspace Kernel
    -> Structured business objects and traces
```

---

## 3. Memory-native 原则

V3 Product Sales Agent 可以维护长期认知 memory：

- 用户偏好。
- 产品理解。
- 销售策略。
- 工作假设。
- 被用户纠正的信息。
- 已拒绝或被替代的信息。

Memory 可以保存推断和假设，但必须带状态或可解释上下文。推荐状态词为：

```text
observed / inferred / hypothesis / confirmed / rejected / superseded
```

这些状态用于治理，不用于提前禁止 agent 思考。

---

## 4. Runtime 原则

V3 runtime 优先采用 LangGraph / LangChain，但 LangGraph checkpoint 不是业务主存。

Runtime 可以：

- 读取和更新认知 memory。
- 调用模型与工具。
- 形成策略和下一步建议。
- 在需要正式写回时提出 `WorkspacePatchDraft`。

Runtime 不应：

- 直接写正式业务对象。
- 把 hypothesis 写成 confirmed formal object。
- 绕过 backend governance 执行联系方式、报告、导出或自动触达。

---

## 5. Backend Governance 原则

Backend / Sales Workspace Kernel 继续负责正式业务承诺：

- 正式产品理解。
- 正式获客方向。
- 候选客户和来源证据。
- 联系方式。
- 报告、导出和对外动作。

V3 的变化不是取消治理，而是把治理后移到正式承诺边界，而不是阻止 runtime memory 形成开放认知。

---

## 6. 多端入口原则

V3 可以引入 Web 双入口：

- `/lab`：内部开发者和产品测试入口，用于观察 memory、trace、tool calls 和 formal writeback decision。
- `/workspace`：真实销售用户 Web 雏形，用于验证工作流和信息架构。

Web 入口服务 V3 学习和验证，不改变 App-first 长期入口策略。详细边界见 `docs/architecture/v3/web-dual-entry-prototype.md`。

---

## 7. 后续 POC 建议

后续 implementation task 可优先验证：

- LangChain 调用腾讯云 API。
- Product Sales Agent 通过工具自编辑 memory。
- Memory 影响下一轮回答。
- 用户纠错能 supersede 旧记忆。
- Formal writeback 仍经过 backend gate。
- Web `/lab` 能支持人工和 Playwright 验证 memory / trace / draft review。
