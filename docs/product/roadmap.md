# Product Roadmap

更新时间：2026-04-25

## 当前阶段

当前路线已从 V1 implementation 切换为：

> **V2 planning baseline**

V1 已冻结为 demo-ready release candidate / learning milestone，不继续追加 V1 功能，不包装为 MVP。

---

## V2 暂定方向

V2 暂定方向为：

> **对话式专属销售 agent prototype**

当前假设：

- 目标用户：中小企业老板 / 销售负责人。
- 前端方向：Android 控制入口，不做 Web 前端。
- V2.1：对话式产品理解、获客方向分析和用户实时调整方向。
- V2.2：确认方向后进入联网 / 中文公开网页搜索。
- 输出形态：会话消息、产品画像版本、获客方向版本、后续候选公司和来源证据。
- 联系方式：V2.2 才进入，受控展示、必须可溯源、默认人工验证、不自动触达。

---

## 近期推荐顺序

1. 冻结 V2.1 conversational sales agent backend contract 草案。
2. 冻结 `v2-sales-agent-data-model.md` 到 Draft v0.2。
3. 设计 `sales_agent_turn_graph` draft schema。
4. 创建 V2.1 backend-only prototype task。
5. 完成 V2.1 后，再恢复 V2.2 lead research provider、来源证据和联系方式实现讨论。
6. V2.2 用 5 到 10 个真实中文业务样例评估候选质量、来源质量、成本和耗时。

---

## 当前不排入路线

- Web 前端
- 完整 CRM
- 自动触达
- 批量联系人抓取
- 批量联系人导出
- 大规模爬虫系统
- 正式云端 SaaS 部署
- 多用户 / 租户 / 权限实现
- Android 大规模聊天 UI 改造

上述内容只有在 V2 PRD、ADR 和 task queue 明确后才能重新进入讨论。

---

## Phase Exit Criteria

V2 planning baseline 退出条件：

- V2 PRD v0.2 明确 V2.1 / V2.2 / V2.3 阶段。
- V2 sales agent data model v0.2 明确首批对象集合。
- ADR-006 已冻结 prototype、本地后端沉淀、继续 LangGraph、会话消息首批持久化和 lead research 后置。
- V2.1 backend contract 草案明确最小会话 API 和对象写回边界。
- `_active.md` 明确是否创建 V2 implementation queue。

在这些条件满足前，不应自动开始后端 schema / migration / API 实现。
