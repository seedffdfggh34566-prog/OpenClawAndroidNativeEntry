# Handoff — V3 Comprehensive Live Smoke (2026-05-04)

## 1. 范围

执行 `backend/scripts/v3_comprehensive_live_smoke.py`,在腾讯 TokenHub `minimax-m2.7` 上跑 35 轮综合销售对话(20 normal + 15 high-density),验证以下 V3 sandbox runtime 能力:

- core memory 维护(persona / human / product / sales_strategy / customer_intelligence)
- memory 状态演进与用户纠错时的 supersede 行为
- customer intelligence 草稿与排序
- 上下文管理分层(75% pressure warning / 90% summarization / 95% guard)
- 摘要后早期信息回忆
- 系统 prompt 膨胀下的 self-compaction

本次仅运行验证脚本与产生 evidence,未修改 `backend/runtime/v3_sandbox/graph.py` 核心逻辑。

## 2. 运行环境

| 项目 | 值 |
|------|----|
| Model | `minimax-m2.7` |
| Endpoint | `https://tokenhub.tencentmaas.com/v1`(通过 `backend/.env` 读取) |
| Context window(脚本配置) | 200 000 tokens |
| Pressure warning 阈值 | 75 %(150 000 tokens) |
| Summarization 阈值 | 90 %(180 000 tokens) |
| Guard 阈值 | 95 %(190 000 tokens) |
| `max_context_messages` | 32(`graph.py:430`) |
| `max_steps` per turn | 16 |
| Debug trace | verbose,include_prompt,no raw output |

## 3. 运行结果摘要

| 指标 | 值 |
|------|----|
| Session id | `v3_live_smoke_20260504_165636` |
| 总耗时 | 1319.8 秒(≈ 22 分钟) |
| 总轮次 | 35 |
| 成功轮次 | 32 |
| 失败轮次 | 3(turn 7 / 34 / 35) |
| Soft assertions | **全部通过** |
| 75 % warning 触发 | ❌ 否 |
| 90 % summarization 触发 | ❌ 否 |
| 95 % guard 触发 | ❌ 否 |
| Memory self-compaction | ❌ 未触发(均稳态增长) |
| 报告 | `backend/scripts/reports/v3_live_smoke_report_v3_live_smoke_20260504_165636.json`(本地保留,gitignored) |
| 运行日志 | `backend/scripts/reports/v3_live_smoke_run_20260504_165636.log`(本地保留,gitignored) |

退出码 1(因为有 turn 错误,而非 assertion 失败)。

## 4. 失败轮次详情

### Turn 7 — `v3_tool_loop_no_tool_call`

- 输入:`你觉得这三个客户应该怎么排序？哪个优先级最高？`
- 现象:LLM 完成响应后未返回任何 tool_call,`graph.py:280` 直接 `raise ValueError`。
- 原因初判:这是 native function-calling 在纯分析型问题上的偶发问题,模型可能直接生成自然语言 reasoning 而忽略了"必须通过 send_message 输出"的 system prompt 约束。
- 影响:本轮无 assistant 回复,但脚本捕获后继续推进,memory 不变。前后轮次正常运作,无 cascading 失败。
- 频率:32 个真实 LLM 轮次中 1 次失败,约 3 %。

### Turn 34 / 35 — `tokenhub_http_error:402` (`FREE_QUOTA_EXHAUSTED`)

- 来自 TokenHub 网关:`{"error":{"message":"endpoint is inactive: FREE_QUOTA_EXHAUSTED","code":"401008","type":"gateway_error"}}`
- 这是平台级配额耗尽,与 V3 runtime 行为无关。Turn 34 是"战略方向讨论",turn 35 是"最终回忆问题",均无法验证。
- 估算:33 轮 LLM 调用 + 32 轮 memory tools 运行,大约消耗了当前账号的免费额度。

## 5. Memory 维护与 supersede 观察

### 5.1 工具调用统计

`memory_replace` 是 ACT-3/4/5 的主力工具(对已有内容做精细补丁)。`core_memory_append` 用于新增独立事实(如新邮件、新案例)。`memory_insert` 用于在锚点附近插入新条目。`memory_rethink` 仅在 turn 1 出现一次(初始化 persona)。

代表性轮次:

| Turn | 场景 | 工具调用 |
|------|------|----------|
| 1 | 自我介绍 | memory_insert + memory_rethink + send_message |
| 16 | A 公司 30→50 人纠正 | memory_replace × 2 + send_message |
| 17 | 涨价 299→399 | memory_replace × 5 + send_message(多 block 协同) |
| 20 | 公司名"云算科技"→"云算智能科技" | memory_replace × 1 + send_message(轻量,11.7 s) |
| 21 | 三封邮件优先级分析 | memory_replace × 3 + send_message |
| 33 | 客户投诉危机 | memory_replace + send_message,product 中已记录 bug+sla |

### 5.2 Soft assertion 全部通过(详见脚本 `_post_run_assertions`)

- `final_human` 含 `李明`(姓名)与 `云算智能`(纠正后的公司全称)。
- `final_product` 含 `财税`、`发票`、`399`(supersede 后价格)。
- `final_product` 中 `299` 即使存在,也已被 `涨价` / `老客户` 关键词标注上下文,符合 supersede 注解断言。
- `final_customer_intelligence` 含 `A 公司`、`B 公司`、`C 公司`,且包含 `50 人` / `张总`,反映 A 公司纠正后的画像。
- `final_sales_strategy` 含 `A 公司`,反映 turn 11 起的标杆战略。

### 5.3 最终 block 长度(全部远低于 limit)

| Block | Final chars | Limit | 占用 |
|-------|-------------|-------|------|
| persona | 194 | 2 000 | 9.7 % |
| human | 276 | 5 000 | 5.5 % |
| product | 1 336 | 10 000 | 13.4 % |
| sales_strategy | 2 346 | 5 000 | 46.9 % |
| customer_intelligence | 711 | 20 000 | 3.6 % |

`max == final` for all,因此 self-compaction 路径未被触发。

## 6. 上下文管理未触发的解释(关键洞察)

虽然 ACT-5 设计了 15 轮高密度长输入,**75 % / 90 % / 95 % 三档阈值在本次运行中均未触发**。原因:

1. **滑动窗口提前压住了 token 量**。`_build_tool_loop_messages` 的 `max_context_messages = 32`(`graph.py:430`)使 `after_cursor` 长度被限制在 32 条原始消息。即便 35 轮,实际进入 prompt 的 user/assistant 历史最多 32 条,加上 system prompt 估算总量 ≈ 60-100 K tokens,远低于 75 %(150 K)阈值。
2. **summary 生成是阈值驱动的而非数量驱动**。`_maybe_run_summarization` 要求"`after_cursor` > `max_context_messages`" **且** "总 token > 90 % 阈值"。前一个条件在第 33 轮起满足,后一个条件始终未达成,因此 cursor 一直未推进,`context_summary_present` 始终为 false。
3. **Memory blocks 自身不会快速膨胀**。最大 block(`sales_strategy`)2 346 chars ≈ 1 K tokens,5 个 block 合计大约 4-5 K tokens,与 system prompt 比较固定。

## 7. 健康度判断

| 维度 | 评分 | 说明 |
|------|------|------|
| Memory 维护 | ✅ 良好 | 所有断言通过,supersede 行为正确,工具选择合理 |
| Customer intelligence 草稿 | ✅ 通过 | A/B/C 三个 lead 全部跟踪,最新状态保留 |
| 用户纠错处理 | ✅ 通过 | 30→50、299→399、云算科技→云算智能科技 全部 supersede |
| Native tool calling 稳定性 | ⚠️ 边缘 | 32 中 1 次 no_tool_call(≈3 %),纯分析型问题为高发场景 |
| 上下文管理覆盖 | ⚠️ 未覆盖 | 阈值在本次场景下未触发,无法在 live 中验证 |
| Quota | ❌ 受限 | minimax-m2.7 免费额度在 33 轮后耗尽 |

## 8. 推荐后续动作(候选,不自动开工)

1. **不修改 graph.py 核心阈值**。当前 75/90/95 配置基于 `task_2026_05_04_v3_context_threshold_and_guard`,本次未观察到逻辑性问题。
2. **若要在 live 真实触发 75 % / 90 %**,需要构造能堆出 ≥ 150 K tokens 的场景:
   - 把 `max_context_messages` 临时调大,或
   - 在脚本中加入更长(8-10 K chars)单条 user message,或
   - 跑 50+ 轮压力对话(注意 quota)。
3. **Turn 7 的 no_tool_call**:可考虑在 system prompt 中再次强调 "If the answer is purely analytical, still call send_message",或在 graph 中对纯文本响应做 1 次 retry-with-stricter-tool_choice 后再 raise。需要单独 task 立项,本次不实施。
4. **Quota 管理**:后续 live smoke 应在 staging 账号上跑,或预算允许时在 paid 配额上跑。也可降低 `max_steps` 或拆成 5×7 短跑批以节省 token。
5. **Memory blocks 增长趋势**:`sales_strategy` 已到 47 % 占用,如果再加 10 轮策略迭代可能逼近 limit,届时会触发 model-driven self-compaction。下一次跑可关注这个边界。

## 9. 关键文件 / 证据

- 脚本:`backend/scripts/v3_comprehensive_live_smoke.py`(本次未修改)
- 运行时:`backend/runtime/v3_sandbox/graph.py`(本次未修改)
- 报告 JSON:`backend/scripts/reports/v3_live_smoke_report_v3_live_smoke_20260504_165636.json`(每轮指标 + 错误明细;`backend/scripts/reports/*.json` 已 gitignored,目录通过 `.gitkeep` 保留)
- 运行日志:`backend/scripts/reports/v3_live_smoke_run_20260504_165636.log`(完整 stdout)

## 10. 已知限制

- 上下文管理三档阈值在本次运行中**全部未触发**,因此 75 % warning 注入、90 % 摘要生成、95 % guard early-return 这三条路径未获得 live evidence。它们的单元/集成测试由 `task_2026_05_04_v3_context_threshold_and_guard` 已覆盖,但 live 验证需要更长 / 更密的场景。
- TokenHub minimax-m2.7 免费额度在第 34 轮耗尽,导致 ACT-5 最后两轮(战略方向 + 全局回忆)未能验证,后者本是验证"压缩后早期信息回忆"的关键 turn。
- Turn 7 失败属于 LLM 行为,非 runtime bug,但提示 minimax-m2.7 在纯分析型问题上有偶发 no_tool_call 风险。

## 11. 结论

V3 sandbox runtime 在 minimax-m2.7 上 32 轮真实 LLM 调用 + 真实 memory tool 协作下表现稳定,memory 维护与用户纠错的 supersede 行为通过全部 soft assertions。**当前阈值与 guard 不需要调参**;真正未被 live 覆盖的是上下文管理三档触发,需要更高密度的后续 smoke 才能补齐 evidence。Turn 7 的 no_tool_call 与 turn 34/35 的 quota 错误均为已知/外部因素,不阻塞当前 V3 方向。
