# V3 Web Dual-entry Prototype

更新时间：2026-04-30

## 1. 定位

本文档记录 V3 Web 入口方向：Web 可以同时承担内部开发测试台和真实销售用户产品雏形，但它们应是同一个 Web 工程里的两个入口，而不是两个独立产品。

当前状态：direction accepted / implementation not started。

---

## 2. 核心结论

推荐形态：

```text
web/
  /lab         V3 Sales Agent Lab
  /workspace   Sales user workspace prototype
```

原则：

- 一个 Web 工程，两个 route / app shell。
- 共享 API client、domain types、memory rendering 和 conversation state。
- `/lab` 面向开发者和产品调试，强调可观察、可回放、可验证。
- `/workspace` 面向真实销售用户体验雏形，强调任务、对话、确认和行动建议。
- Android / App 仍是长期主要用户入口。
- Web 不代表 production SaaS、正式多租户、正式登录权限或正式部署已启动。

---

## 3. 分层关系

```text
Android App primary entry
Web /workspace user prototype
Web /lab developer and product test surface
  -> OpenClaw Backend API
    -> Product Sales Agent Runtime
      -> LangGraph / LangChain
      -> Tencent Cloud API or OpenClaw LLM Gateway
      -> Memory tools
    -> Backend governance / Sales Workspace Kernel
    -> Formal business objects and traces
```

Web 的职责是更快验证 V3 runtime、memory 和 user workflow，不改变 backend / runtime / memory 的产品核心位置。

---

## 4. `/lab` 入口

`/lab` 是内部开发者友好型入口。它可以暴露真实用户不应看到的细节：

- agent trace。
- memory blocks。
- memory status：`observed / inferred / hypothesis / confirmed / rejected / superseded`。
- tool calls。
- prompt / response summary。
- latency、error、request id。
- draft review payload。
- formal writeback decision。
- demo seed、reset、replay。

`/lab` 的主要验收不是漂亮，而是能让人工和 Dev Agent 快速判断 agent 是否真的记住、修正和使用 memory。

---

## 5. `/workspace` 入口

`/workspace` 是真实销售用户 Web 雏形。它应隐藏 runtime 内部细节，只表达用户工作流：

- 今天该做什么。
- 当前产品理解。
- 客户 / 线索状态。
- Product Sales Agent 的建议。
- 多轮对话。
- 需要用户确认、拒绝或修改的信息。
- 用户可理解的 memory 摘要。

`/workspace` 用来验证销售用户体验和信息架构。被验证有效的交互，可以后续迁移或复用到 Android App。

---

## 6. App-first 边界

长期产品入口仍以 App 为主。Web 的当前价值是：

- 缩短 V3 runtime / memory 人工测试反馈链路。
- 给 Dev Agent 提供 Playwright 友好的自动化测试表面。
- 在桌面场景验证复杂 workspace 和 review 流程。
- 为 Android 主体验提供信息架构参考。

Web 不应在当前阶段抢先定义：

- 正式 SaaS packaging。
- 多租户权限体系。
- 正式部署方案。
- 最终设计系统。
- Android 主体验替代方案。

---

## 7. 推荐实施顺序

后续若开放 implementation task，建议顺序为：

1. 建立最小 `web/` 工程和 Playwright 验证链路。
2. 先实现 `/lab`，接入已有 Sales Workspace API 和 trace / diagnostics 能力。
3. 在 V3 runtime POC 出现后，把 memory blocks、tool calls、agent trace 接入 `/lab`。
4. 再实现 `/workspace` 的真实销售用户雏形。
5. 将 `/workspace` 中验证有效的流程同步到 Android App 设计。

---

## 8. 不冻结内容

本文档不冻结：

- Web framework。
- route 细节。
- component library。
- API request / response contract。
- memory schema。
- auth / tenant / deployment。
- Android UI contract。

下一步如果要实现 Web，应另开 task 明确 framework、目录、验证命令和最小首屏范围。
