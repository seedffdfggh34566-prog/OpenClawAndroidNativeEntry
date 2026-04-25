# Task：V1 Demo Device Smoke After LLM Lead Analysis

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V1 Demo Device Smoke After LLM Lead Analysis
- 建议路径：`docs/delivery/tasks/task_v1_demo_device_smoke_after_llm_lead_analysis.md`
- 当前状态：`done`
- 优先级：P0

本任务用于在 `lead_analysis` 切到真实 LLM、`report_generation` 完成交付物表达 polish 后，用真实 backend、真实 TokenHub 和真机 Android 验证一次 V1 demo 路径。

验证链路：

```text
创建 ProductProfile -> product_learning succeeded -> 确认 ProductProfile -> lead_analysis LLM succeeded -> polished report_generation succeeded -> 首页 / 结果页 / 报告页状态正确
```

---

## 2. 任务目标

本任务目标不是新增功能，而是确认当前 V1 已具备可演示的端到端体验。

必须验证：

1. Android 真机能连接本地 backend。
2. 产品学习使用真实中文样例创建 ProductProfile。
3. `product_learning` run 成功，并能进入可确认状态。
4. Android 能确认 ProductProfile。
5. `lead_analysis` 使用 TokenHub `minimax-m2.5` 成功生成 LeadAnalysisResult。
6. `report_generation` 成功生成 polished report。
7. 首页、结果页、报告页能展示 demo 所需关键状态。
8. 若出现 TokenHub timeout 阻断 demo，记录证据并触发 latency / fallback follow-up。

---

## 3. 范围

本任务 In Scope：

- 使用独立 smoke DB 启动真实 backend。
- 使用真实 TokenHub LLM 配置；API key 只从 `backend/.env` 或环境变量读取。
- 使用真机 Android + `adb reverse` 跑 demo 路径。
- 使用已准备的 `ADBKeyBoard` + `ADB_INPUT_B64` 输入中文。
- 后端 API 交叉检查 run 和最终对象状态。
- UIAutomator / logcat 证据收集。
- 只有发现明确 bug 时，做最小修复并重新验证。

本任务 Out of Scope：

- 修改 backend API。
- 修改 persisted schema。
- 修改 Android DTO / parser。
- 新增 Android 页面、导航、CRM、导出、分享能力。
- Prompt tuning。
- 模型切换、多模型路由或境外 endpoint。
- 主动实现 latency / fallback；只有 timeout 明确阻断 demo 时才进入后续任务。

---

## 4. 固定验证环境

- backend：`127.0.0.1:8013`
- Android base URL：`http://127.0.0.1:8013`
- 设备转发：`adb reverse tcp:8013 tcp:8013`
- smoke database：`OPENCLAW_BACKEND_DATABASE_PATH=/tmp/openclaw_v1_demo_device_smoke_after_llm_lead_analysis_2026_04_25.db`
- LLM 配置：继续从 `backend/.env` 或环境变量读取，不打印 API key
- 默认 provider：Tencent TokenHub
- 默认模型：`minimax-m2.5`

---

## 5. 固定 demo 样例

- 产品名：`工厂设备巡检助手`
- 一句话说明：`面向制造业设备主管的移动巡检和故障记录工具`
- 初始材料：`支持离线巡检、设备台账、异常拍照、维修派单；目标客户是中小制造工厂、设备主管和维修班组。`
- 补充材料：`补充：重点服务离散制造、机械加工和设备密集型工厂；核心痛点是纸质巡检漏项、故障记录分散、维修响应慢；优势是低成本部署、移动端离线可用、现场照片和维修闭环。`

---

## 6. 验收标准

满足以下条件可认为完成：

1. `backend/.env` 存在，且执行过程不读取或打印 secret 内容。
2. backend 使用 smoke DB 启动，`/health` 成功。
3. `./gradlew :app:assembleDebug` 成功。
4. `adb devices` 检测到真机。
5. `adb reverse tcp:8013 tcp:8013` 成功。
6. APK 安装并启动成功。
7. Android 使用中文样例完成 ProductProfile create。
8. ProductProfile 达到可确认状态并被确认到 `confirmed`。
9. `lead_analysis` run `succeeded`，且 runtime metadata 可见 LLM provider/model/usage。
10. `report_generation` run `succeeded`，AnalysisReport `published`。
11. UIAutomator 能定位首页、结果页、报告页关键文案。
12. `adb logcat -d -t 300` 未发现 `FATAL EXCEPTION` / `AndroidRuntime: FATAL`。
13. 若 demo 未被 timeout 阻断，latency / fallback follow-up 保持未触发。

---

## 7. 风险与注意事项

- 若设备未安装 `com.android.adbkeyboard`，先按 `docs/how-to/debug/android-chinese-input-smoke.md` 完成设备准备；不要自动破解厂商安全验证。
- 若 8013 端口被非目标进程占用且无法确认是当前 backend，本任务标记 blocked。
- 若 TokenHub timeout 或网络失败，先重试一次；重复失败记录为 latency / supplier connectivity evidence。
- 不把 API key 写入 Git、文档、日志或最终汇报。

---

## 8. 实际产出

- 已用真实 backend、真实 TokenHub `minimax-m2.5`、真机 Android 完成一次 V1 demo 路径：
  - 创建 ProductProfile
  - product_learning LLM succeeded
  - 确认 ProductProfile
  - lead_analysis LLM succeeded
  - polished report_generation succeeded
  - 首页 / 结果页 / 报告页状态正确
- 使用真实中文样例 `工厂设备巡检助手`，中文输入通过已预装 `com.android.adbkeyboard` + `ADB_INPUT_B64` 完成。
- 发现并修复一个非 timeout 问题：
  - 首次 lead_analysis run `run_cddc84b5` 失败，错误为 `lead_analysis_llm_json_decode_failed`。
  - 原因：lead_analysis JSON 解析逻辑使用“第一个 `{` 到最后一个 `}`”的粗粒度提取，遇到模型输出中 JSON 外前缀 / 花括号时不够稳。
  - 修复：`lead_analysis` 解析器改为扫描并解析第一个合法 JSON object。
  - 该修复不改变 public API、schema、Android DTO、AgentRun 生命周期或正式对象写回边界。
- 修复后重新触发 lead_analysis，demo 路径成功完成。
- 后端最终对象：
  - ProductProfile：`pp_7f04d2f7`，`confirmed`，v3
  - LeadAnalysisResult：`lar_9a81c480`，`published`
  - AnalysisReport：`rep_7ef24e42`，`published`
- 后端最终成功 AgentRun：
  - product_learning：`run_c2759b51`，`succeeded`
  - lead_analysis：`run_cb68783e`，`succeeded`
  - report_generation：`run_55159132`，`succeeded`
- 失败证据保留：
  - lead_analysis：`run_cddc84b5`，`failed`，`lead_analysis_llm_json_decode_failed`
- 未触发 latency / fallback follow-up：
  - 本次阻塞不是 timeout。
  - 修复后 LeadAnalysis LLM 成功耗时约 8.6 秒。
  - `runtime_metadata.llm_usage.total_tokens=1864`。

---

## 9. 已做验证

已完成：

1. `git status --short`
   - 结果：开始执行 Task3 时仅有本任务 docs 变更。
2. 确认 `backend/.env` 存在
   - 结果：存在；未读取或打印 secret 内容。
3. 8013 端口检查
   - 结果：启动前端口空闲。
4. 启动 backend
   - 命令：`OPENCLAW_BACKEND_DATABASE_PATH=/tmp/openclaw_v1_demo_device_smoke_after_llm_lead_analysis_2026_04_25.db backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013`
   - 结果：backend 正常启动。
5. `curl -sS http://127.0.0.1:8013/health`
   - 结果：`{"status":"ok"}`
6. `./gradlew :app:assembleDebug`
   - 结果：成功。
   - 备注：仍有既有 AGP / compileSdk warning。
7. `adb devices`
   - 结果：检测到真机 `f3b59f04`。
8. 测试 IME 检查
   - 结果：设备已安装 `com.android.adbkeyboard`，并列出 `com.android.adbkeyboard/.AdbIME`。
9. `adb reverse tcp:8013 tcp:8013`
   - 结果：成功。
10. `adb install -r app/build/outputs/apk/debug/app-debug.apk`
    - 结果：成功。
11. Android 中文输入
    - 结果：产品名称、一句话说明、初始材料均通过 `ADB_INPUT_B64` 输入，并在 UIAutomator XML 中可见。
12. Android UI product learning create
    - 结果：`run_c2759b51` succeeded，ProductProfile `pp_7f04d2f7` 达到 `ready_for_confirmation`。
13. Android UI ProductProfile confirm
    - 结果：`pp_7f04d2f7` 确认到 `confirmed` / v3。
14. Android UI lead_analysis 首次触发
    - 结果：`run_cddc84b5` failed，错误 `lead_analysis_llm_json_decode_failed`。
15. 修复后验证
    - `backend/.venv/bin/python -m pytest backend/tests`
    - 结果：40 passed。
    - `git diff --check`
    - 结果：通过。
16. Android UI lead_analysis 重新触发
    - 结果：`run_cb68783e` succeeded，LeadAnalysisResult `lar_9a81c480` published。
    - run detail 可见 `llm_provider=tencent_tokenhub`、`llm_model=minimax-m2.5`、`llm_usage.total_tokens=1864`。
17. Android UI report_generation
    - 结果：`run_55159132` succeeded，AnalysisReport `rep_7ef24e42` published。
18. UIAutomator 文案证据
    - 产品画像页可见 `我们理解你的产品`、`适合卖给谁`。
    - 结果页可见 `优先尝试方向`、`场景机会`、`上下游机会`。
    - 报告页可见 `执行摘要`、`重点建议`、`状态：可复看`。
    - 首页可见 `销售分析报告已生成。`、`当前产品：工厂设备巡检助手`。
19. 后端交叉验证
    - `GET /history`：最终存在 latest product profile、lead analysis result、report。
    - `GET /product-profiles/pp_7f04d2f7`：`status=confirmed`，`learning_stage=confirmed`。
    - `GET /lead-analysis-results/lar_9a81c480`：`status=published`。
    - `GET /reports/rep_7ef24e42`：`status=published`，sections 包含 polished report 结构。
    - `GET /analysis-runs/run_cb68783e`：`status=succeeded`，LLM metadata / usage 可见。
    - `GET /analysis-runs/run_55159132`：`status=succeeded`。
20. `adb logcat -d -t 300 | rg -i "FATAL EXCEPTION|AndroidRuntime: FATAL|Process: com.openclaw.android.nativeentry"`
    - 结果：无匹配，未发现崩溃信号。
21. 输入法恢复
    - 结果：默认输入法已恢复为 `com.baidu.input_oppo/.ImeService`。

---

## 10. 后续建议

建议下一步执行 `task_v1_llm_latency_and_fallback_followup.md` 的条件判断收口：

- 本次 demo 未被 timeout 阻断，因此不建议实现 fallback。
- 应只创建 / 更新 conditional task，记录未触发原因。
- 如果后续 demo 再次出现 ProductLearning 或 LeadAnalysis timeout，才进入 latency / fallback 的最小实现。
