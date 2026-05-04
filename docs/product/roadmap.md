# Product Roadmap

更新时间：2026-04-30

## 当前阶段

当前路线已切换为：

> **V3 Agent Sandbox-first Memory-native Sales Agent direction accepted；backend sandbox runtime POC completed**

V1 是 frozen demo baseline。V2 是 historical validated prototype asset。V3 是当前产品方向。

---

## V3 方向

V3 的目标是验证：

- Product Sales Agent 是否能长期维护和自编辑认知记忆。
- 推断、假设、策略和纠错能否进入 memory，并在后续对话中发挥作用。
- Agent 能否自主维护 sandbox workspace working state 和 customer intelligence working state。
- 未来 agent 自动建档、候选客户排序和打分是否值得扩展。
- Backend 能否先承担 runtime host、storage、trace 和 API 基础设施角色，而不是业务建档者。
- LangGraph / LangChain 是否适合作为自研 runtime 起点。
- Web 双入口是否能同时支持内部测试和真实销售用户体验验证。

---

## 近期推荐顺序

1. 完成 V3 docs rebaseline。
2. 单独讨论并精简 `AGENTS.md`。
3. 已完成 backend-only V3 sandbox runtime POC。
4. 开放 V3 Web `/lab` scaffold task，观察 memory、working state、customer intelligence draft 和 trace。
5. 讨论 V3 sandbox memory persistence design 是否进入正式 schema。
6. 再讨论 `/workspace` 用户雏形、Android UI 和 V2.2 search/contact 是否进入实现。

---

## 当前不排入路线

- MVP / production SaaS。
- production Web SaaS / auth / tenant / formal deployment。
- 完整 CRM。
- 自动触达。
- 真实 CRM 生产写入。
- 不可逆导出。
- 批量联系人抓取或导出。
- backend formal governance / Sales Workspace Kernel 作为 V3 默认实现路径。
- 正式 search / ContactPoint implementation。
- 未定义 V3 用户体验前的大规模 Android UI 改造。
- 未完成 V3 memory persistence design 前的完整 DB schema。
