# Task：ProductProfile 确认流程

更新时间：2026-04-24

## 1. 任务定位

- 任务名称：ProductProfile 确认流程
- 建议路径：`docs/delivery/tasks/task_v1_product_profile_confirmation_flow.md`
- 当前状态：`completed`
- 优先级：P0

本任务用于补齐 ProductProfile 从 `draft` 到 `confirmed` 的确认边界，消除 `runtime_allow_draft_profiles` 开发 hack，让 V1 产品学习 → 确认 → 分析闭环完整。

---

## 2. 任务目标

在保持 V1 小闭环的前提下，实现：

- 后端新增 `POST /product-profiles/{id}/confirm` 最小 contract
- 后端移除或隔离 `runtime_allow_draft_profiles` bypass
- Android ProductProfileScreen 新增"确认产品画像"按钮
- Android 仅在 ProductProfile 状态为 `confirmed` 时允许触发 `lead_analysis`
- 空态、失败态、加载态和确认成功态清晰可见

---

## 3. 范围

本任务 In Scope：

- 后端确认接口（只读状态变更，不做复杂编辑）
- 后端移除 draft bypass（生产路径拒绝 draft）
- 测试覆盖确认成功、重复确认、未找到对象、draft 被拒绝等路径
- Android 新增确认读取与触发
- ProductProfileScreen 展示状态并允许确认
- 补充 task、handoff 与最小验证

本任务 Out of Scope：

- 完整 ProductProfile 编辑（PATCH 所有字段）
- 重写 analysis-run 流程
- 真实 OpenClaw runtime 接入
- CRM、联系人抓取、自动外呼或自动触达
- 鉴权、账号、多环境切换
- Android 架构重写或新增重型框架

---

## 4. 验收标准

满足以下条件可认为完成：

1. 后端 `POST /product-profiles/{id}/confirm` 将 `draft` 升级为 `confirmed`
2. 后端重复确认返回幂等成功（已是 confirmed 再次确认不报错）
3. 后端 `lead_analysis` 在 `draft` 状态下返回 409（除非测试显式启用 bypass）
4. Android ProductProfileScreen 显示当前状态（draft / confirmed）
5. Android 在 `draft` 状态下显示"确认产品画像"按钮，在 `confirmed` 后禁用
6. Android 仅在 `confirmed` 时启用"生成获客分析"按钮
7. `./gradlew :app:assembleDebug` 通过
8. 后端测试通过
9. 完成一次本地后端 + Android 真机 smoke

---

## 5. 风险与注意事项

- 这是状态变化任务，应先更新 reference，再改实现
- 移除 bypass 会影响现有测试，需要更新测试显式确认 profile
- 不要把本任务扩大成完整 CRUD 编辑
- 如果确认字段与现有 domain model 冲突，应先回到 docs/reference 对齐
