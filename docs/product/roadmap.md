# Product Roadmap

更新时间：2026-04-30

## 当前阶段

当前路线已切换为：

> **V3 Agent Sandbox-first Memory-native Sales Agent direction accepted；implementation not started**

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
3. 开放 V3 runtime POC planning task。
4. 验证 LangChain / 腾讯云 API 调用路径。
5. 验证 Product Sales Agent memory tools、self-edit memory 和 sandbox working state。
6. 开放 V3 Web dual-entry scaffold task，建立 `/lab`、`/workspace` 和 Playwright 验证链路。
7. 再讨论 schema、migration、Android UI 和 V2.2 search/contact 是否进入实现。

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
- 未定义 POC 前的大规模 Android UI 改造。
- 未定义最小 memory POC 前的完整 DB schema。
