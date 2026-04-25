# Task：V1 Android Product Learning Enrich Device Smoke

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V1 Android Product Learning Enrich Device Smoke
- 建议路径：`docs/delivery/tasks/task_v1_android_product_learning_enrich_device_smoke.md`
- 当前状态：`done`
- 优先级：P1

本任务用于补齐 Android Product Learning Iteration UI 完成后尚未覆盖的真实设备完整联调验证。

---

## 2. 任务目标

在 `jianglab` 上启动真实 backend，通过 `adb reverse tcp:8013 tcp:8013` 让真机 Android 访问本地后端，完整验证：

1. Android 端创建 ProductProfile
2. ProductLearning 页面展示当前理解与缺失字段
3. Android 端提交一轮补充信息
4. backend 创建并处理 `product_learning` enrich AgentRun
5. Android 端轮询完成后刷新 ProductProfile
6. `ready_for_confirmation` / `missingFields` / CTA 状态可见

---

## 3. 范围

本任务 In Scope：

- 真实 backend + 真机 Android + `adb reverse` 联通验证
- TokenHub `minimax-m2.5` 真实 LLM 调用验证
- 必要时修复当前 enrich UI 或 client 接线中的明确 bug
- 更新 task、handoff、delivery 索引

本任务 Out of Scope：

- 新增 backend API
- 修改 backend contract / persisted schema
- 新增 Android 页面或导航目的地
- ProductLearning UI polish
- 首页、结果页、报告页最终产品表达收口

---

## 4. 固定验证环境

- backend：`127.0.0.1:8013`
- Android base URL：`http://127.0.0.1:8013`
- 设备转发：`adb reverse tcp:8013 tcp:8013`
- smoke database：`OPENCLAW_BACKEND_DATABASE_PATH=/tmp/openclaw_android_enrich_smoke.db`
- LLM 配置：继续从 `backend/.env` 读取，不打印 API key
- 默认模型：`minimax-m2.5`

---

## 5. 固定 smoke 样例

- 产品名：`工厂设备巡检助手`
- 一句话描述：`面向制造业设备主管的移动巡检和故障记录工具`
- 初始材料：`支持离线巡检、设备台账、异常拍照、维修派单；目标客户是中小制造工厂、设备主管和维修班组。`
- 补充材料：`补充：重点服务离散制造、机械加工和设备密集型工厂；核心痛点是纸质巡检漏项、故障记录分散、维修响应慢；优势是低成本部署、移动端离线可用、现场照片和维修闭环。`

---

## 6. 验收标准

满足以下条件可认为完成：

1. `backend/.env` 存在，且执行过程不读取或打印 secret 内容
2. backend 使用 smoke DB 启动，`/health` 成功
3. `./gradlew :app:assembleDebug` 成功
4. `adb devices` 检测到真机
5. `adb reverse tcp:8013 tcp:8013` 成功
6. APK 安装并启动成功
7. Android 端 ProductLearning 页面真实提交 create 与 enrich
8. 后端确认 create run 与 enrich run 均进入 `succeeded`
9. ProductProfile 刷新后字段可见，`missingFields` 与确认 CTA 状态可定位
10. `adb logcat -d -t 300` 未发现 `FATAL EXCEPTION` / `AndroidRuntime`

---

## 7. 风险与注意事项

- 若 8013 端口被非目标进程占用且无法确认是当前 backend，本任务标记 blocked，不擅自杀进程。
- 若 TokenHub 超时或网络路径失败，优先记录为环境 / 供应商联通问题。
- 若发现 Android 或 backend 自身 bug，只做当前 smoke 所需的最小修复。
- 不把 API key 写入 Git、文档、日志或最终汇报。

---

## 8. 实际产出

- 完成真实 backend + 真机 Android + `adb reverse` product learning create / enrich 联调。
- 发现并修复 Android enrich 轮询接线问题：
  - 将 AgentRun 轮询窗口从约 10 秒延长到约 30 秒，匹配真实 LLM 调用耗时。
  - enrich 轮询每次拿到最新 run detail 时，同步更新“继续补充信息”区显示的 AgentRun 状态。
- 验证 ProductProfile 从 v1 创建到 v2 初次学习，再到 v3 enrich 写回。
- 确认 ProductLearning 页面显示：
  - 当前理解字段
  - `missingFields = []`
  - `ready_for_confirmation`
  - “查看并确认产品画像” CTA
  - enrich run `succeeded`

---

## 9. 已做验证

已完成：

1. `git status --short`
   - 结果：仅有本任务文档与当前 smoke 修复相关改动。
2. 确认 `backend/.env` 存在
   - 结果：存在；未读取或打印 secret 内容。
3. 确认 8013 端口空闲
   - 结果：启动前无监听进程。
4. 启动 backend
   - 命令：`OPENCLAW_BACKEND_DATABASE_PATH=/tmp/openclaw_android_enrich_smoke.db backend/.venv/bin/python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8013`
   - 结果：Alembic 初始化 smoke DB 成功，backend 正常启动。
5. `curl -sS http://127.0.0.1:8013/health`
   - 结果：`{"status":"ok"}`
6. `./gradlew :app:assembleDebug`
   - 结果：成功。
   - 备注：仍有既有 AGP / compileSdk warning 与 `LocalLifecycleOwner` deprecated warning。
7. `adb devices`
   - 结果：检测到真机 `f3b59f04`。
8. `adb reverse tcp:8013 tcp:8013`
   - 结果：成功。
9. `adb install -r app/build/outputs/apk/debug/app-debug.apk`
   - 结果：成功。
10. `adb shell am start -n com.openclaw.android.nativeentry/.MainActivity`
    - 结果：应用启动成功。
11. Android 端 ProductLearning create smoke
    - 结果：`run_52d5dbb7` succeeded，`ProductProfile pp_868d490b` 输出 v2。
12. Android 端 ProductLearning enrich smoke
    - 结果：`run_dc28b5a1` succeeded，`ProductProfile pp_868d490b` 输出 v3。
13. 后端交叉验证
    - `GET /analysis-runs/run_52d5dbb7`：`status=succeeded`，output `version=2`。
    - `GET /analysis-runs/run_dc28b5a1`：`status=succeeded`，`trigger_source=android_product_learning_iteration`，output `version=3`。
    - `GET /product-profiles/pp_868d490b`：`learning_stage=ready_for_confirmation`，`version=3`，`missing_fields=[]`。
14. UIAutomator dump
    - 结果：页面可见 `状态：draft · ready_for_confirmation · v3`、`• 暂无`、`当前画像已达到 ready_for_confirmation`、`状态：succeeded`、`查看并确认产品画像`。
15. `adb logcat -d -t 300 | rg -i "FATAL EXCEPTION|AndroidRuntime: FATAL|Process: com.openclaw.android.nativeentry"`
    - 结果：无匹配，未发现崩溃信号。

---

## 10. 实际结果说明

本任务已完成真实设备完整 enrich smoke，并在过程中修复了一个真实 Android 状态接线问题。

设备侧 adb 输入限制：

- `adb shell input text` 在当前设备上直接输入中文会触发系统侧 NPE。
- `%20` 不会被转换为空格，会作为字面文本输入。
- 因此 Android 端实际 smoke 使用无空格 ASCII 等价样例：
  - 产品名：`FactoryInspectionAssistant`
  - 一句话描述：`ManufacturingMobileInspectionToolForEquipmentManagers`
  - 补充材料：`DiscreteManufacturingPainPaperGapsSlowRepairLowCostOfflinePhotos`

该限制只影响 adb 自动输入，不影响 App 对真实后端、TokenHub LLM 或 ProductProfile 中文字段的展示；LLM 输出字段在 UI 和 backend detail 中均为中文。
