# Product Roadmap

更新时间：2026-04-25

## 当前阶段

当前路线已从 V1 implementation 切换为：

> **V2 planning baseline**

V1 已冻结为 demo-ready release candidate / learning milestone，不继续追加 V1 功能，不包装为 MVP。

---

## V2 暂定方向

V2 暂定方向为：

> **带来源证据的轻量线索研究**

当前假设：

- 目标用户：中小企业老板 / 销售负责人。
- 前端方向：Android 控制入口，不做 Web 前端。
- 产品学习：从表单式录入逐步升级为 AI 引导式对话。
- 线索研究：允许主动联网 / 中文公开网页搜索。
- 输出形态：具体公司候选、来源证据、匹配理由、不确定性、下一步人工验证动作。
- 联系方式：受控展示、必须可溯源、默认人工验证、不自动触达。

---

## 近期推荐顺序

1. 冻结 `ai_sales_assistant_v2_prd.md` 到 Draft v0.2。
2. 冻结 `v2-lead-research-data-model.md` 到 Draft v0.2。
3. 基于 ADR-005 补 V2 backend contract 草案。
4. 明确搜索 provider、数据保留和联系方式边界。
5. 创建后端-only lead research spike task。
6. 用 5 到 10 个真实中文业务样例评估候选质量、来源质量、成本和耗时。

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

- V2 PRD v0.2 明确是否以 MVP 为目标。
- V2 data model v0.2 明确首批对象集合。
- ADR-005 已冻结搜索、来源证据、联系方式和非目标边界。
- V2 backend contract 草案明确最小 API 和对象写回边界。
- `_active.md` 明确是否创建 V2 implementation queue。

在这些条件满足前，不应自动开始后端 schema / migration / API 实现。
