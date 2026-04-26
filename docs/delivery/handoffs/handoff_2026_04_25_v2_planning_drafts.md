# Handoff: V2 planning drafts

日期：2026-04-25

## Summary

根据用户指令新增 V2 规划草案文档，当前仅用于规划层讨论，不创建 V2 implementation task，不更新 `_active.md` 为可执行队列。

## Changed

- 新增 `docs/product/prd/ai_sales_assistant_v2_prd.md`
  - 定义 V2 暂定方向：面向中小企业老板 / 销售负责人的轻量线索研究。
  - 记录允许主动联网 / 中文搜索、允许具体公司名、联系方式受控展示、不做 Web 前端、AI 引导式产品学习等边界。
  - 明确成功标准仍是草案，V2 是否进入 MVP 尚未冻结。
- 新增 `docs/architecture/data/v2-lead-research-data-model.md`
  - 定义 V2 线索研究的数据对象草案。
  - 将对话、产品画像版本、搜索来源、候选公司、联系方式和行动建议拆成可追踪对象。
  - 明确来源证据和联系方式必须可溯源。
- 更新 `docs/product/README.md`
  - 增加 V2 PRD 草案入口。
- 更新 `docs/architecture/data/README.md`
  - 增加 V2 data model 草案入口。

## Validation

- 文档结构只读检查：已确认当前 `_active.md` 无 current task，V1 已冻结为 demo-ready release candidate / learning milestone。
- 本次为 docs-only 规划草案，未运行 backend / Android 测试。

## Known Limits

- V2 定义尚未完善，本文档没有冻结数据库 schema、API contract 或 task queue。
- 联系方式边界仍需后续明确，尤其是个人联系方式展示、保留、删除和合规提示。
- 搜索 provider、成本治理、账号隔离、正式部署形态仍未决。
- V2 是否作为 MVP 仍未决。

## Recommended Next Step

先用两份草案完成规划层审阅，重点冻结：

1. V2 是否以 MVP 为目标。
2. V2 首批数据对象集合。
3. 是否首批实现 ProductLearningSession / ConversationMessage。
4. 搜索 provider 和来源保留策略。
5. ContactPoint 的个人信息边界。

在这些问题明确前，不建议创建 V2 implementation task queue。
