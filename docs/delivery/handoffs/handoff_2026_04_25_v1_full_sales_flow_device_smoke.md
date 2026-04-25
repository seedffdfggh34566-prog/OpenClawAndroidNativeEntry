# 阶段性交接：V1 Full Sales Flow Device Smoke

更新时间：2026-04-25

## 1. 本次做了什么

- 新增并完成 `task_v1_full_sales_flow_device_smoke.md`。
- 使用独立 smoke DB 从空库开始跑通真机 Android 主闭环：
  - 创建产品画像
  - 提交一轮补充信息
  - 确认产品画像
  - 生成获客分析
  - 生成分析报告
  - 回首页确认最终状态
- 未修改 backend API、persisted schema、Android DTO / parser、导航或功能代码。

---

## 2. 本次验证了什么

1. `backend/.env` 存在，未读取或打印 secret 内容。
2. backend 使用 `/tmp/openclaw_v1_full_sales_flow_device_smoke.db` 启动，`/health` 返回 `{"status":"ok"}`。
3. 初始 `/history` 为空库。
4. `./gradlew :app:assembleDebug`
   - 结果：成功。
5. `adb devices`
   - 结果：检测到真机 `f3b59f04`。
6. `adb reverse tcp:8013 tcp:8013`
   - 结果：成功。
7. `adb install -r app/build/outputs/apk/debug/app-debug.apk`
   - 结果：成功。
8. Android UI create / enrich：
   - create run：`run_4d517bc6`，`succeeded`
   - enrich run：`run_5857cb62`，`succeeded`
   - ProductProfile：`pp_2966a345`，最终 `confirmed` / v4
9. Android UI lead_analysis：
   - run：`run_f47cf4be`，`succeeded`
   - LeadAnalysisResult：`lar_5d4304b4`，`published`
10. Android UI report_generation：
    - run：`run_f97620f3`，`succeeded`
    - AnalysisReport：`rep_b7d058e1`，`published`
11. UIAutomator 抽查：
    - 产品画像页可见 `我们理解你的产品`、`适合卖给谁`
    - 结果页可见 `优先尝试方向`
    - 报告页可见 `执行摘要`、`重点建议`、`状态：可复看`
    - 首页可见 `销售分析报告已生成。`
12. `adb logcat -d -t 300`
    - 结果：未发现 `FATAL EXCEPTION` / `AndroidRuntime: FATAL` / app process crash 信号。
13. `git diff --check`
    - 结果：通过。

---

## 3. 已知限制

- 当前设备通过 `adb shell input text` 输入中文仍不可靠，本次沿用无空格 ASCII 等价样例。
- UI 输入过程中，初始材料被设备输入到“一句话描述”字段后方，没有单独落入 `source_notes`；但信息仍由 Android UI 提交到后端，且完整链路目标不受影响。
- ProductLearning 页面仍有少量工程词汇和输入体验可打磨，未在本任务内处理。
- 本次 smoke 使用真实 TokenHub `minimax-m2.5`，但没有做 prompt tuning 或多模型对比。

---

## 4. 推荐下一步

1. 优先拆真实样例评估 / prompt tuning follow-up，验证不同产品输入下的 LLM 输出质量和稳定性。
2. 其次可拆 ProductLearning UI polish，改善输入区、状态刷新和工程词汇表达。
3. 若后续需要重复做真机自动 smoke，单独评估更稳定的测试输入机制。
