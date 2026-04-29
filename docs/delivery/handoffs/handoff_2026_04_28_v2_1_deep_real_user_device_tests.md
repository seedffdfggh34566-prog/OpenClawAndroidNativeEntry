# Handoff: V2.1 Sales Workspace Deep Real User Device Tests

日期：2026-04-28

## Scope

本 handoff 记录一次深度真实用户测试。测试目标是评估当前 Android Sales Workspace + backend true LLM runtime 是否能在不同使用风格下持续产出有价值的拓客分析，并记录 bug。

本次只做测试和记录，不修代码，不新增 API / schema / migration，不进入 V2.2 search / contact / CRM / formal LangGraph。

## Environment

- Backend：`127.0.0.1:8013`
- Store：JSON store，`OPENCLAW_BACKEND_SALES_WORKSPACE_STORE_DIR=/tmp/openclaw_deep_device_tests/store`
- Runtime：true LLM，`OPENCLAW_BACKEND_SALES_AGENT_RUNTIME_MODE=llm`
- Prompt：`OPENCLAW_BACKEND_SALES_AGENT_LLM_PROMPT_VERSION=sales_agent_turn_llm_v1`
- Diagnostics：`OPENCLAW_BACKEND_DEV_SALES_WORKSPACE_DIAGNOSTICS_ENABLED=true`
- Device：ADB device `f3b59f04`
- Android evidence：`/tmp/openclaw_deep_device_tests/screenshots/`
- Raw result JSON：`/tmp/openclaw_deep_device_tests/results.json`

重要限制：当前 Android App 仍固定进入默认 workspace `ws_demo`，不能从产品 UI 选择任意 workspace ID。因此 5 个独立 workspace 的 75 轮深测通过 backend API 驱动真实 LLM 和真实 JSON store 完成；真机 App 用于验证 Android 主路径、composer、thinking、LLM 回复、Draft Review 附件和新对话弹窗。这个限制本身是后续产品化 bug。

## Device Evidence

- `/tmp/openclaw_deep_device_tests/screenshots/android_01_launch.png`：Home 首屏可见“开始销售工作区”。
- `/tmp/openclaw_deep_device_tests/screenshots/android_02_workspace.png`：默认 `ws_demo` 不存在时，Workspace 显示连接成功但需要创建默认 workspace。
- `/tmp/openclaw_deep_device_tests/screenshots/android_03_workspace_chat.png`：创建 `ws_demo` 后进入聊天页，显示 `主对话`、`新对话`、composer 和 welcome。
- `/tmp/openclaw_deep_device_tests/screenshots/android_04_composer_filled.png`：ADBKeyboard 输入中文后，composer 可显示中文。
- `/tmp/openclaw_deep_device_tests/screenshots/android_07_after_send_correct_tap.png`：发送后用户消息立即进入 transcript，显示 `Sales Agent 正在思考...`。
- `/tmp/openclaw_deep_device_tests/screenshots/android_08_after_llm_response.png`：真实 LLM 回复后显示自然语言回答和 `可保存到工作区` 附件。
- `/tmp/openclaw_deep_device_tests/screenshots/android_09_settings_open.png`：尝试点击 `设置` 后未展开设置面板，记录为 UI bug。
- `/tmp/openclaw_deep_device_tests/screenshots/android_10_new_thread_dialog.png`：点击 `新对话` 后出现 `命名新对话` dialog。

## Case 1: 急躁型早期创业者

- Workspace：`ws_deep_01_opc_sales_agent`
- Thread：`拓客AI 找客户验证`
- 使用风格：短句、多追问、希望直接答案，不愿意补很多资料。
- 结果：15/15 agent runs，15/15 context packs，6 次写入，workspace version `6`。
- 沉淀：product profile `ppr_llm_v4`，lead direction `dir_llm_v6`，projection 生成 `product/current.md`、`directions/current.md`、`rankings/current.md`、`candidates/index.md`。

| Round | Mode | User intent | Key result | Draft |
| --- | --- | --- | --- | --- |
| 1 | 产品理解 | 描述拓客AI / Sales Agent | 识别产品、目标客户和核心功能 | yes, wrote v1 |
| 2 | 找客户建议 | 我的客户是谁 | 给出第一批客户群体和方向 | yes |
| 3 | 找客户建议 | 不要追问，直接建议 | 收敛到教育咨询、B2B 服务、小制造老板 | yes, wrote v2 |
| 4 | 找客户建议 | 第一周怎么做 | 输出第一周行动计划 | yes |
| 5 | 找客户建议 | 一个人每天怎么排 | 给出单人每日动作排班 | yes, wrote v3 |
| 6 | 找客户建议 | 哪些客户不要找 | 给出排除客户类型 | yes |
| 7 | 找客户建议 | 小红书/微信群/企查查/百度优先级 | 给出渠道优先级 | yes |
| 8 | 解释当前判断 | 为什么不是中大型企业 | 解释产品匹配、采购链路和预算问题 | no |
| 9 | 找客户建议 | 客单价 3000-12000 是否改变客户 | 解释价格对客户筛选的影响 | yes |
| 10 | 产品+找客户 | 补充功能和无 CRM 集成 | 更新产品和方向 | yes, wrote v4 |
| 11 | 找客户建议 | 下午找 10 个潜在客户 | 给出立即筛选方法 | yes |
| 12 | 找客户建议 | 手工筛选清单 | 给出不搜索具体公司的筛选清单 | yes, wrote v5 |
| 13 | 解释当前判断 | 工作区沉淀了什么 | 能解释已保存产品画像和方向 | no |
| 14 | 找客户建议 | 收敛最容易成交的一类 | 收敛第一批客户方向 | yes, wrote v6 |
| 15 | 解释当前判断 | 三句话最终判断 | 给出可读最终判断 | no |

Bug：未发现阻断性产品 bug。观察：部分轮次 LLM 延迟高，最长约 66 秒。

## Case 2: 谨慎型传统服务老板

- Workspace：`ws_deep_02_local_training`
- Thread：`本地培训获客`
- 使用风格：信息碎片化，经常否定前一轮，关心线下本地获客。
- 结果：15/15 agent runs，15/15 context packs，3 次写入，workspace version `3`。
- 沉淀：lead direction `dir_llm_v3`；未沉淀正式 product profile。

| Round | Mode | User intent | Key result | Draft |
| --- | --- | --- | --- | --- |
| 1 | 产品理解 | 本地企业销售和管理培训 | 只追问目标客户/行业/痛点，未生成 draft | no |
| 2 | 产品理解 | 补充杭州和交付半径 | 继续要求回答前置问题，未生成 draft | no |
| 3 | 找客户建议 | 先找什么企业 | 给出本地中小企业方向 | yes, wrote v1 |
| 4 | 找客户建议 | 不想找大企业 | 固化排除大企业约束 | yes |
| 5 | 找客户建议 | 老板还是 HR | 建议先找 HR 并解释原因 | yes, wrote v2 |
| 6 | 找客户建议 | 怎么找到这些人 | LLM runtime 503 timeout | failed |
| 7 | 找客户建议 | 排除方向 | 给出排除项 | yes |
| 8 | 找客户建议 | 客单价 2-5 万影响 | LLM runtime 503 timeout | failed |
| 9 | 产品+找客户 | 强项是成交率培训 | 重新定位为销售团队成交率 | yes |
| 10 | 解释当前判断 | 为什么先找这类客户 | 解释 HR/培训负责人的决策逻辑 | no |
| 11 | 找客户建议 | 是否做异地城市 | 给出本地优先、异地谨慎建议 | yes |
| 12 | 找客户建议 | 老客户转介绍动作 | 设计转介绍动作 | yes, wrote v3 |
| 13 | 找客户建议 | 一周本地获客动作 | 输出一周可执行动作 | yes |
| 14 | 解释当前判断 | 产品和方向是否一致 | 明确 product profile 尚未创建 | no |
| 15 | 找客户建议 | 更新为本地 30-200 人销售团队老板 | 更新方向草稿 | yes |

Bug：

- P1：Round 6、Round 8 出现 `llm_runtime_unavailable / tokenhub_request_timeout`。
- P2：前两轮产品理解信息足够形成初版产品草稿，但未自动生成 product profile draft，导致 case 结束后 `current_product_profile_revision_id = null`。

## Case 3: 分析型 SaaS 创始人

- Workspace：`ws_deep_03_tax_saas`
- Thread：`财税 SaaS 客户分层`
- 使用风格：结构化信息多，要求客户分层、筛选标准和排除项。
- 结果：15/15 agent runs，15/15 context packs，5 次写入，workspace version `5`。
- 沉淀：product profile `ppr_llm_v5`，lead direction `dir_llm_v5`。

| Round | Mode | User intent | Key result | Draft |
| --- | --- | --- | --- | --- |
| 1 | 产品+找客户 | 一次性给产品、客户、痛点 | 同时生成产品和客户方向初稿 | yes, wrote v1 |
| 2 | 找客户建议 | 第一批客户分层 | 按老板/财务/渠道方向分层 | yes |
| 3 | 找客户建议 | 老板/财务/代账公司比较 | 给出比较和优先级 | yes, wrote v2 |
| 4 | 找客户建议 | 具体筛选信号 | 输出可操作筛选信号 | yes |
| 5 | 找客户建议 | 不适合客户 | 给出排除项 | yes, wrote v3 |
| 6 | 产品理解 | 无银行流水，只能导 Excel/发票 | 更新产品限制 | yes |
| 7 | 找客户建议 | 无银行流水是否影响找客户 | 调整客户方向和卖点 | yes |
| 8 | 解释当前判断 | 为什么不是大型 ERP 客户 | 解释功能深度和采购复杂度 | no |
| 9 | 找客户建议 | 第一周验证动作 | 给出按优先级的验证动作 | yes |
| 10 | 找客户建议 | 代账公司渠道风险 | 分析利益冲突和渠道风险 | yes, wrote v4 |
| 11 | 找客户建议 | A/B/C 三层客户 | 收敛客户分层 | yes |
| 12 | 产品+找客户 | 补充客单价和人工导入 | 更新产品和方向 | yes, wrote v5 |
| 13 | 找客户建议 | 最优第一批客户 | 给出当前最优 ICP | yes |
| 14 | 解释当前判断 | 正式对象还缺什么 | 能说明缺失字段 | no |
| 15 | 找客户建议 | 排除重度 ERP 和大型集团 | 更新排除方向 | yes |

Bug：未发现阻断性 bug。观察：长回复总体可读，但在真机窄屏上长列表仍需要更好的排版压缩。

## Case 4: 探索型工业软件 PM

- Workspace：`ws_deep_04_industrial_maintenance`
- Thread：`工业维保 ICP 探索`
- 使用风格：不断改变行业假设，在设备部、维保商、设备厂商售后之间摇摆。
- 结果：15/15 agent runs，15/15 context packs，3 次写入，workspace version `3`。
- 沉淀：lead direction `dir_llm_v3`；未写入正式 product profile。

| Round | Mode | User intent | Key result | Draft |
| --- | --- | --- | --- | --- |
| 1 | 产品理解 | 工业设备维保软件 | LLM runtime 503 timeout | failed |
| 2 | 产品理解 | 补充设备类型和地区 | 生成产品 profile 草稿，但未写入 | yes |
| 3 | 找客户建议 | 设备部/维保商/设备厂商 | LLM runtime 503 timeout | failed |
| 4 | 找客户建议 | 设备部 vs 维保商 | 建议优先设备部 | yes |
| 5 | 找客户建议 | 改为维保服务商 | 接受用户假设变化并更新方向 | yes, wrote v1 |
| 6 | 找客户建议 | 设备厂商售后假设 | 分析售后方向 | yes |
| 7 | 找客户建议 | 三种方向比较 | 给出并行探索假设 | yes |
| 8 | 解释当前判断 | 解释为什么维保服务商优先 | 能基于正式方向解释 | no |
| 9 | 找客户建议 | 第一周验证维保商 | 输出验证计划 | yes |
| 10 | 找客户建议 | 小维保商是否值得找 | 调整客户规模假设 | yes, wrote v2 |
| 11 | 产品+找客户 | 工单/备件/设备档案，无 IoT | 识别能力边界 | yes |
| 12 | 找客户建议 | 无 IoT 怎么调整方向 | 排除 IoT 依赖客户 | yes, wrote v3 |
| 13 | 找客户建议 | 排除行业和设备 | 给出排除项 | yes |
| 14 | 解释当前判断 | 工作区是否被假设污染 | 能解释当前正式假设 | no |
| 15 | 找客户建议 | 收敛早期试点客户 | 收敛到一类早期试点客户 | yes |

Bug：

- P1：Round 1、Round 3 出现 `llm_runtime_unavailable / tokenhub_request_timeout`。
- P2：Round 2 生成 product profile draft 但测试未写入；case 结束后正式 product profile 为空。用户真实使用中如果忽略或未理解附件，产品沉淀会缺失。

## Case 5: 执行型制造外包老板

- Workspace：`ws_deep_05_manufacturing_outsource`
- Thread：`制造外包第一批客户`
- 使用风格：非常实操，反复要名单前动作、关键词和筛选标准，但不能进入 V2.2 真实公司/联系人。
- 结果：15/15 agent runs，15/15 context packs，6 次写入，workspace version `6`。
- 沉淀：lead direction `dir_llm_v6`；未沉淀正式 product profile。

| Round | Mode | User intent | Key result | Draft |
| --- | --- | --- | --- | --- |
| 1 | 产品理解 | 制造外包服务 | 只追问，未生成 product draft | no |
| 2 | 找客户建议 | 第一批客户是谁 | 给出初步方向 | yes |
| 3 | 找客户建议 | 第一周动作 | 给出一周执行动作 | yes, wrote v1 |
| 4 | 找客户建议 | 关键词自己搜 | LLM runtime 503 timeout | failed |
| 5 | 找客户建议 | 判断客户是否有需求 | 给出需求判断信号 | yes, wrote v2 |
| 6 | 找客户建议 | 不要名单，给筛选标准 | 给出筛选标准 | yes |
| 7 | 找客户建议 | 能不能找具体公司 | 没有给具体公司，但暴露内部术语 | yes |
| 8 | 找客户建议 | 手动去哪里找 | 给出手动渠道 | yes, wrote v3 |
| 9 | 找客户建议 | 行业优先级排序 | 给出行业优先级 | yes |
| 10 | 找客户建议 | 排除汽车主机厂和超大工厂 | 更新排除条件 | yes, wrote v4 |
| 11 | 找客户建议 | 只能接 50 万以下订单 | 调整优先级 | yes |
| 12 | 找客户建议 | 电话前准备清单，不自动触达 | 给出准备清单 | yes, wrote v5 |
| 13 | 解释当前判断 | 为什么不能直接给联系人 | 解释边界，但暴露内部 blocked_capabilities 术语 | no |
| 14 | 找客户建议 | 保存小批量多品种客户画像 | 生成方向草稿 | yes, wrote v6 |
| 15 | 解释当前判断 | 明天三件事 | 给出三件可执行动作，但暴露 `revision_id` / `patch_operations` | no |

Bug：

- P1：Round 4 出现 `llm_runtime_unavailable / tokenhub_request_timeout`。
- P2：Round 7 / Round 13 的边界说明没有越界生成具体公司名单，但暴露了 `workspace_goal`、`V2.2 runtime`、`blocked_capabilities` 等开发者术语。
- P2：Round 15 暴露 `revision_id` 和 `patch_operations`，且把“生成 patch_operations”作为用户动作建议，产品语言不自然。
- P2：Round 1 未自动生成 product profile draft，case 结束后 `current_product_profile_revision_id = null`。

## Cross-Case Findings

### P1

1. True LLM runtime 稳定性不足：5 个案例 75 轮中至少 5 轮返回 `llm_runtime_unavailable / tokenhub_request_timeout`。这些失败没有导致测试整体中断，但真实用户会看到某轮无结果。
2. Android 不能选择 workspace ID，只能进入 `ws_demo`。因此无法用产品 UI 完成 5 个独立 workspace 的真实测试，这是多 workspace 产品化阻断。

### P2

1. 部分回复泄露内部实现术语，例如 `workspace_goal`、`V2.2 runtime`、`blocked_capabilities`、`revision_id`、`patch_operations`。应在 assistant formatter 层统一转成产品语言。
2. Product profile 沉淀不稳定。Case 2、4、5 都提供了产品信息，但最终没有正式 product profile；原因包括 LLM 只追问、不生成 draft，或生成 draft 后用户未写入。
3. Android 设置按钮在真机上多次点击后未展开设置面板，截图见 `android_09_settings_open.png`。
4. Android 仍存在默认 `ws_demo` 未创建中间页，首次从 Home 点击后不是直接进入聊天体验，而是需要再点一次“开始销售工作区”。

### P3

1. 长回复和 Draft Review 附件在窄屏上仍显得拥挤；附件虽然比之前轻，但长自然语言回复 + 附件会快速挤压 composer 上方区域。
2. LLM 回复中仍混用英文字段风格短语，例如 `target industries`、`company sizes`，应转为纯中文业务语言。

## Validation

- `./gradlew :app:assembleDebug` passed。
- `adb devices` detected `f3b59f04 device`。
- `adb reverse tcp:8013 tcp:8013` configured。
- `adb install -r app/build/outputs/apk/debug/app-debug.apk` passed。
- `adb shell am start -n com.openclaw.android.nativeentry/.MainActivity` passed。
- True LLM JSON-store backend stayed running on `127.0.0.1:8013` during the test.
- 5 cases completed 75 total rounds through backend API with true LLM runtime:
  - 75 agent runs recorded in diagnostics.
  - 75 context packs recorded in diagnostics.
  - 23 draft reviews applied across cases.
  - Projection files available for all five workspaces.
- ADBKeyboard was temporarily selected for Chinese input and restored to `com.baidu.input_oppo/.ImeService` after device smoke.

## Known Limits

- The 5 independent workspace deep tests were API-driven, not fully Android UI-driven, because Android currently hardcodes `ws_demo`.
- Screenshots are stored under `/tmp/openclaw_deep_device_tests/screenshots/`, outside the repository.
- JSON store evidence under `/tmp/openclaw_deep_device_tests/store/` is local test data and not committed.
- LLM content quality is nondeterministic; this handoff records observed behavior from the run on 2026-04-28.
- This handoff is validation evidence only and does not declare V2.1 product or milestone completion.

## Recommended Next Steps

1. Fix Android workspace selection / creation so real device can create or select the intended workspace ID, not only `ws_demo`.
2. Add assistant response sanitization to remove internal fields and blocked capability names from user-facing text.
3. Improve product profile draft policy so sufficient product info reliably generates a lightweight product draft.
4. Add retry / user-visible recovery for `llm_runtime_unavailable / tokenhub_request_timeout`.
5. Re-test settings panel click behavior on device and fix if reproducible.
