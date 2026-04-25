# Task：V1 Full Sales Flow Device Smoke

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V1 Full Sales Flow Device Smoke
- 建议路径：`docs/delivery/tasks/task_v1_full_sales_flow_device_smoke.md`
- 当前状态：`done`
- 优先级：P1

本任务用于在 Android 销售闭环表达收口后，从空库开始完整验证一次 V1 主闭环。

验证链路：

```text
创建产品画像 -> 补充信息 -> 确认产品画像 -> 生成获客分析 -> 生成分析报告 -> 首页 / 结果页 / 报告页状态正确
```

---

## 2. 任务目标

本任务目标不是新增功能，而是确认当前已完成的 backend、runtime、LLM、Android UI 和真机联通能力能组合成一条稳定的用户主流程。

必须验证：

1. 空库启动后 Android 可以创建产品画像
2. product learning create / enrich 至少一个链路能让 ProductProfile 达到可确认状态
3. Android 可以确认产品画像
4. Android 可以生成获客分析
5. Android 可以生成分析报告
6. 首页、结果页、报告页能展示最终状态

---

## 3. 范围

本任务 In Scope：

- 新建 smoke DB 并启动真实 backend
- 真机 Android + `adb reverse` 完整主链路验证
- TokenHub `minimax-m2.5` 真实调用验证
- 后端 API 交叉检查
- UIAutomator 文案证据
- 若发现明确 bug，只做最小修复并重新完整验证
- task、handoff、delivery 索引更新

本任务 Out of Scope：

- 修改 backend API
- 修改 persisted schema
- 修改 Android DTO / parser
- 新增页面、导航、聊天、CRM、导出能力
- ProductLearning UI polish
- prompt tuning
- 模型对比

---

## 4. 固定验证环境

- backend：`127.0.0.1:8013`
- Android base URL：`http://127.0.0.1:8013`
- 设备转发：`adb reverse tcp:8013 tcp:8013`
- smoke database：`OPENCLAW_BACKEND_DATABASE_PATH=/tmp/openclaw_v1_full_sales_flow_device_smoke.db`
- LLM 配置：继续从 `backend/.env` 读取，不打印 API key
- 默认模型：`minimax-m2.5`

---

## 5. 固定 smoke 输入

由于当前设备的 `adb shell input text` 中文输入不可靠，自动化输入使用无空格 ASCII 等价样例：

- 产品名：`FactoryInspectionAssistant`
- 一句话描述：`ManufacturingMobileInspectionToolForEquipmentManagers`
- 初始材料：`OfflineInspectionEquipmentLedgerPhotoRepairDispatchManufacturingEquipmentManagers`
- 补充材料：`DiscreteManufacturingPainPaperGapsSlowRepairLowCostOfflinePhotosRepairLoop`

---

## 6. 验收标准

满足以下条件可认为完成：

1. `backend/.env` 存在，且执行过程不读取或打印 secret 内容
2. backend 使用 smoke DB 启动，`/health` 成功
3. `./gradlew :app:assembleDebug` 成功
4. `adb devices` 检测到真机
5. `adb reverse tcp:8013 tcp:8013` 成功
6. APK 安装并启动成功
7. Android 从空库完成 ProductProfile create
8. ProductProfile 达到 `ready_for_confirmation` 或经 enrich 后达到可确认状态
9. ProductProfile 被确认到 `confirmed`
10. lead_analysis run `succeeded`，LeadAnalysisResult `published`
11. report_generation run `succeeded`，AnalysisReport `published`
12. UIAutomator 能定位首页、结果页、报告页关键文案
13. `adb logcat -d -t 300` 未发现 `FATAL EXCEPTION` / `AndroidRuntime`

---

## 7. 风险与注意事项

- 若 8013 端口被非目标进程占用且无法确认是当前 backend，本任务标记 blocked，不擅自杀进程。
- 若 TokenHub timeout 或网络失败，先重试一次；重复失败记录为环境 / 供应商联通问题。
- 若 product learning create / enrich 后仍未达到可确认状态，记录为 LLM 输出质量或样例输入问题，不在本任务内调 prompt。
- 不把 API key 写入 Git、文档、日志或最终汇报。

---

## 8. 实际产出

- 已从空库完成真机 Android + 真实 backend + TokenHub LLM 的 V1 主闭环 smoke。
- 使用 Android UI 完成：
  - 创建 ProductProfile
  - 提交一轮 supplemental enrich
  - 确认 ProductProfile
  - 生成获客分析
  - 生成分析报告
  - 回首页确认最终状态
- 后端最终对象：
  - ProductProfile：`pp_2966a345`，`confirmed`，v4
  - LeadAnalysisResult：`lar_5d4304b4`，`published`
  - AnalysisReport：`rep_b7d058e1`，`published`
- 后端最终 AgentRun：
  - create product_learning：`run_4d517bc6`，`succeeded`
  - enrich product_learning：`run_5857cb62`，`succeeded`
  - lead_analysis：`run_f47cf4be`，`succeeded`
  - report_generation：`run_f97620f3`，`succeeded`
- 本任务未修改 backend API、schema、Android DTO / parser、页面导航或产品功能代码。

---

## 9. 已做验证

已完成：

1. `git status --short`
   - 结果：开始执行前工作区干净。
2. 确认 `backend/.env` 存在
   - 结果：存在；未读取或打印 secret 内容。
3. 8013 端口检查
   - 结果：启动前端口空闲。
4. 启动 backend
   - 命令：`OPENCLAW_BACKEND_DATABASE_PATH=/tmp/openclaw_v1_full_sales_flow_device_smoke.db backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013`
   - 结果：Alembic 初始化 smoke DB 成功，backend 正常启动。
5. `curl -sS http://127.0.0.1:8013/health`
   - 结果：`{"status":"ok"}`
6. 初始 `GET /history`
   - 结果：空库，`latest_product_profile=null`、`latest_analysis_result=null`、`latest_report=null`。
7. `./gradlew :app:assembleDebug`
   - 结果：成功。
   - 备注：仍有既有 AGP / compileSdk warning。
8. `adb devices`
   - 结果：检测到真机 `f3b59f04`。
9. `adb reverse tcp:8013 tcp:8013`
   - 结果：成功。
10. `adb install -r app/build/outputs/apk/debug/app-debug.apk`
    - 结果：成功。
11. Android UI create
    - 结果：`run_4d517bc6` succeeded，ProductProfile 输出 v2，并达到 `ready_for_confirmation`。
12. Android UI enrich
    - 结果：`run_5857cb62` succeeded，ProductProfile 输出 v3，仍可确认。
13. Android UI confirm
    - 结果：ProductProfile `pp_2966a345` 确认到 `confirmed` / v4。
14. Android UI lead_analysis
    - 结果：`run_f47cf4be` succeeded，LeadAnalysisResult `lar_5d4304b4` published。
15. Android UI report_generation
    - 结果：`run_f97620f3` succeeded，AnalysisReport `rep_b7d058e1` published。
16. 后端交叉验证
    - `GET /history`：最终存在 latest product profile、lead analysis result、report。
    - `GET /product-profiles/pp_2966a345`：`status=confirmed`，`learning_stage=confirmed`，`missing_fields=[]`。
    - `GET /lead-analysis-results/lar_5d4304b4`：`status=published`。
    - `GET /reports/rep_b7d058e1`：`status=published`。
    - `GET /analysis-runs/{id}`：四个 run 均为 `succeeded`。
17. UIAutomator 文案证据
    - 产品画像页可见 `我们理解你的产品`、`适合卖给谁`。
    - 结果页可见 `优先尝试方向`。
    - 报告页可见 `执行摘要`、`重点建议`、`状态：可复看`。
    - 首页可见 `销售分析报告已生成。`、`当前产品：FactoryInspectionAssistant`。
18. `adb logcat -d -t 300 | rg -i "FATAL EXCEPTION|AndroidRuntime: FATAL|Process: com.openclaw.android.nativeentry"`
    - 结果：无匹配，未发现崩溃信号。
19. `git diff --check`
    - 结果：通过。

---

## 10. 后续建议

建议下一步回到规划层，在以下方向中选择：

1. 真实样例评估 / prompt tuning follow-up：当前完整链路已跑通，下一项高价值风险是 LLM 输出质量和稳定性。
2. ProductLearning UI polish：降低产品学习页剩余工程词汇和输入误触风险。
3. Android 输入自动化改进：若后续需要更稳定的真机自动 smoke，可单独研究测试输入机制，不建议在产品代码里加入临时入口。
