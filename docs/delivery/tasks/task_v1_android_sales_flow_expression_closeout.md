# Task：V1 Android Sales Flow Expression Closeout

更新时间：2026-04-25

## 1. 任务定位

- 任务名称：V1 Android Sales Flow Expression Closeout
- 建议路径：`docs/delivery/tasks/task_v1_android_sales_flow_expression_closeout.md`
- 当前状态：`done`
- 优先级：P1

本任务用于在真实 product learning create / enrich 真机链路跑通后，收口 Android 端首页、产品画像确认页、获客分析结果页和分析报告页的产品表达。

目标不是新增功能，而是让用户能看懂：

1. 现在销售分析流程进展到哪一步
2. 下一步应该做什么
3. 当前结果对销售推进有什么价值

---

## 2. 任务目标

在不改 backend contract、不新增功能模块的前提下，把 Android 端从“工程对象展示”收口为“销售闭环体验”：

1. 首页展示当前进度和下一步行动
2. 产品画像确认页按用户理解组织信息
3. 获客分析结果页突出优先尝试方向与判断依据
4. 分析报告页呈现为最终可复看的交付物

---

## 3. 范围

本任务 In Scope：

- 首页表达收口
- ProductProfile 确认页轻度表达收口
- LeadAnalysisResult 结果页表达收口
- AnalysisReport 报告页表达收口
- 必要的本地纯展示 helper
- task、handoff、delivery 索引更新

本任务 Out of Scope：

- 修改 backend API
- 修改 persisted schema
- 新增 Android navigation destination
- 新增聊天系统、CRM、导出、分享或复制能力
- 引入 ViewModel / Hilt / Room / Retrofit / WorkManager
- 大规模导航或架构重构
- ProductLearning 深度 polish 或 prompt tuning

---

## 4. 实施原则

- Android 端仍是控制入口，不成为数据真相层。
- 页面继续消费现有 backend DTO 与现有状态，不新增后端字段。
- 主叙事尽量减少 `ProductProfile`、`AgentRun`、`LeadAnalysisResult`、`AnalysisReport` 等内部对象名。
- 调试 / 运维入口可以保留工程语义，但不作为主流程文案。
- 确认门控保持不变：只有 `draft + ready_for_confirmation` 才能确认。

---

## 5. 预计改动文件

- `app/src/main/java/com/openclaw/android/nativeentry/ui/home/HomeScreen.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/shell/V1ShellScreens.kt`
- `docs/delivery/tasks/_active.md`
- `docs/delivery/README.md`
- `docs/delivery/tasks/task_v1_android_sales_flow_expression_closeout.md`
- `docs/delivery/handoffs/handoff_2026_04_25_android_sales_flow_expression_closeout.md`

---

## 6. 验收标准

满足以下条件可认为完成：

1. 首页空库、有产品画像、有获客分析、有报告时文案能指向合理下一步
2. 产品画像确认页用“我们理解你的产品 / 适合卖给谁 / 优先场景 / 仍需确认”组织信息
3. 获客分析结果页首屏突出“优先尝试方向”和分析摘要
4. 报告页呈现为最终交付物，包含标题、执行摘要、重点建议、正文、更新时间和状态
5. 后端 API、DTO parser、persisted schema 无变化
6. `git diff --check` 通过
7. `./gradlew :app:assembleDebug` 通过
8. 如真机可用，安装启动后无 AndroidRuntime / FATAL EXCEPTION

---

## 7. 风险与注意事项

- 本任务只做表达收口，不把页面重写成新的交互系统。
- 如果发现现有状态不足以支撑某个表达，只允许新增本地展示 helper。
- 如果完整端到端流程还需要重新验证，应另拆 `task_v1_full_sales_flow_device_smoke.md`。

---

## 8. 实际产出

- 首页从对象清单改为“当前进度 + 建议下一步 + 最近交付物”表达：
  - 空库提示从产品学习开始
  - draft / ready / confirmed / analysis / report 状态均指向对应下一步
  - 最近结果入口改为产品理解、获客分析、分析报告
- 产品画像确认页改为用户可理解的分区：
  - “我们理解你的产品”
  - “适合卖给谁”
  - “优先场景”
  - “核心优势与限制”
  - “仍需补充”
- 获客分析结果页把“优先尝试方向”放到首屏，后续再展示分析范围、优先行业、客户类型、场景机会、判断依据、下一步建议、风险和限制。
- 分析报告页改为最终交付物表达：
  - “执行摘要”
  - “重点建议”
  - 分段正文
  - 状态、版本与更新时间
- 保持 backend API、persisted schema、Android DTO / parser、navigation destination 均无变化。

---

## 9. 已做验证

已完成：

1. `git diff --check`
   - 结果：通过。
2. `./gradlew :app:assembleDebug`
   - 结果：通过。
   - 备注：仍有既有 AGP / compileSdk warning。
3. `adb devices`
   - 结果：检测到真机 `f3b59f04`。
4. `adb install -r app/build/outputs/apk/debug/app-debug.apk`
   - 结果：成功。
5. 使用 `/tmp/openclaw_android_enrich_smoke.db` 启动 backend 并执行 `adb reverse tcp:8013 tcp:8013`
   - `/health` 返回 `{"status":"ok"}`。
6. 后端 smoke 数据补齐：
   - ProductProfile `pp_868d490b` 已确认到 `confirmed` / v4。
   - LeadAnalysisResult `lar_a406107e` 已生成。
   - AnalysisReport `rep_b5e14137` 已生成。
7. UIAutomator 首页文案抽查：
   - 可见 `销售分析报告已生成。`
   - 可见 `当前产品：FactoryInspectionAssistant`
   - 可见 `查看获客分析结果`
   - 可见 `查看分析报告`
8. UIAutomator 结果页文案抽查：
   - 可见 `优先尝试方向`
   - 可见 `分析范围`
   - 可见 `优先行业`
   - 可见 `生成可复看的分析报告`
9. UIAutomator 报告页文案抽查：
   - 可见 `这是一份可复看的销售分析交付物`
   - 可见 `执行摘要`
   - 可见 `重点建议`
   - 可见 `状态：可复看`
10. `adb logcat -d -t 300 | rg -i "FATAL EXCEPTION|AndroidRuntime: FATAL|Process: com.openclaw.android.nativeentry"`
    - 结果：无匹配，未发现崩溃信号。

---

## 10. 后续建议

建议下一步回到规划层，在以下方向中选择：

1. 拆 `task_v1_full_sales_flow_device_smoke.md`，跑完整“创建 -> enrich -> 确认 -> 分析 -> 报告”的端到端真机验证。
2. 拆真实样例评估 / prompt tuning follow-up，对比不同产品材料下的获客分析质量。
3. 若要继续 Android polish，优先处理 ProductLearning 页面剩余工程词汇，而不是新增功能模块。
