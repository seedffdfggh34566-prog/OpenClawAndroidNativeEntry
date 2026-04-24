# 阶段性交接：AnalysisResult 详情 contract 与页面读取

更新时间：2026-04-24

## 1. 本次改了什么

- 后端新增 `GET /lead-analysis-results/{id}` 最小 contract
- 后端新增 `LeadAnalysisResultDetail` schema、`lead_analysis_result_detail` serializer
- 后端新增测试覆盖 200 成功路径和 404 缺失路径
- Android 新增 `LeadAnalysisResultDetailDto`、`parseLeadAnalysisResultDetail()`、`getLeadAnalysisResult()`
- Android `V1BackendUiState` 新增 `analysisResult` 字段
- Android `OpenClawApp` 新增 `loadLatestAnalysisResult()` 与 `LaunchedEffect` 自动触发
- Android `OpenClawNavHost` 新增 `onLoadLatestAnalysisResult` 参数传递
- Android `AnalysisResultScreen` 从仅展示 `/history` 摘要重写为展示完整详情
- 更新 API reference 文档，将最小接口从 6 个扩展为 7 个

## 2. 为什么这么定

- 补齐 V1 客户端对象读链路的最后一块拼图
- 保持后端与 Android 的轻量风格，不重写架构
- 复用现有 `GET /product-profiles/{id}` 和 `GET /reports/{id}` 的模式

## 3. 本次验证了什么

1. `backend/.venv/bin/python -m pytest tests/`：16 passed
2. `./gradlew :app:assembleDebug`：BUILD SUCCESSFUL
3. `curl http://127.0.0.1:8013/lead-analysis-results/{id}`：返回完整 detail 结构
4. `curl http://127.0.0.1:8013/lead-analysis-results/lar_missing`：返回 404

## 4. 已知限制

- 后端 runtime 仍为 stub，详情字段由 `StubRuntimeAdapter` 硬编码填充
- AnalysisResultScreen 未实现下拉刷新
- 当前轮询上限仍为 10 次、每次 1 秒

## 5. 推荐下一步

1. 真实 OpenClaw runtime 接入（替换 `StubRuntimeAdapter`）
2. 或：Android 设置页增加后端 base URL 配置
3. 或：补齐 `PUT /product-profiles/{id}` 确认接口
