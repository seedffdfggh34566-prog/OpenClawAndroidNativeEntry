# Task：AnalysisResult 详情 contract 与页面读取

更新时间：2026-04-23

## 1. 任务定位

- 任务名称：AnalysisResult 详情 contract 与页面读取
- 建议路径：`docs/delivery/tasks/task_v1_analysis_result_detail_contract.md`
- 当前状态：`planned`
- 优先级：P0

本任务用于补齐 `LeadAnalysisResult` 的正式详情读取边界，让 Android AnalysisResult 页不再只展示 `/history.latest_analysis_result` 摘要。

---

## 2. 任务目标

在保持 V1 小闭环的前提下，实现：

- 后端明确并实现 `GET /lead-analysis-results/{id}` 最小 contract
- Android backend client 新增对应 DTO / parser / mapper
- AnalysisResult 页进入时读取 latest analysis result 详情
- 空态、失败态、加载态和真实详情态清晰可见

---

## 3. 范围

本任务 In Scope：

- 补充 backend API reference
- 后端新增只读详情接口
- Android 新增只读详情读取
- AnalysisResult 页展示结构化获客分析结果
- 补充 task、runbook、handoff 与最小验证

本任务 Out of Scope：

- 重写 analysis-run 流程
- 报告导出
- 真实 OpenClaw runtime 接入
- CRM、联系人抓取、自动外呼或自动触达
- 鉴权、账号、多环境切换
- Android 架构重写或新增重型框架

---

## 4. 验收标准

满足以下条件可认为完成：

1. 后端 `GET /lead-analysis-results/{id}` 返回已冻结的最小详情结构
2. 后端测试覆盖成功、不存在对象、schema 解析等关键路径
3. Android AnalysisResult 页可读取 latest id 对应详情
4. Android 能显示加载、空、失败和真实详情态
5. `./gradlew :app:assembleDebug` 通过
6. 后端测试通过
7. 完成一次本地后端 + Android 真机 smoke

---

## 5. 风险与注意事项

- 这是 contract 变化任务，应先更新 reference，再改实现
- 不要把本任务扩大成真实 runtime 接入
- 不要在 Android 侧制造业务主真相
- 如果详情字段与现有 domain model 冲突，应先回到 docs/reference 对齐
