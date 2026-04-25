# Tencent TokenHub TTFT Latency Analysis：2026-04-25

## 1. 数据来源

- 原始文件：`docs/product/research/tencent_tokenhub_uin_ttft_2026_04_25.csv`
- 来源：腾讯云控制台首 token 延迟数据
- 时间范围：2026-04-25 00:00:00 到 2026-04-25 23:59:00
- 粒度：按分钟聚合
- 数据列：`时间`、`100048398763`

说明：CSV 中大部分分钟为 `null`，应理解为该分钟没有可展示的统计值或没有请求样本；本分析只统计非 `null` 的 27 个分钟点。

## 2. 统计结果

按控制台首 token 延迟常见口径，以下数值按毫秒理解：

| 指标 | 数值 |
|---|---:|
| 非空分钟点 | 27 |
| null 分钟点 | 1413 |
| 最小值 | 4063 ms |
| 中位数 | 9895.75 ms |
| 平均值 | 10833.31 ms |
| P75 | 13699.75 ms |
| P90 | 14673 ms |
| P95 | 15867.5 ms |
| 最大值 | 35936 ms |

最高延迟点：

| 时间 | 首 token 延迟 |
|---|---:|
| 2026-04-25 17:06 | 35936 ms |
| 2026-04-25 17:01 | 15867.5 ms |
| 2026-04-25 17:03 | 15006 ms |
| 2026-04-25 17:00 | 14673 ms |
| 2026-04-25 11:44 | 14471 ms |

## 3. 判断

这批数据能说明：当前 TokenHub `minimax-m2.5` 调用存在明显偏高的首 token 延迟。

对当前 V1 的影响：

- 现阶段 backend 调用为 `stream=false`，用户不会直接看到“首 token 到达”，但 TTFT 偏高通常也会拉长整体 completion 时间。
- `lead_analysis` LLM phase 1 中 sample 08 曾出现两次 `tokenhub_request_timeout`，与控制台 17:06 的 35936 ms 峰值方向一致。
- 已在 `lead_analysis` 路径把最小 timeout 提升到 60s，并限制 prompt 输出长度；该修复后 sample 08 重试成功。

当前不建议把它判断为“不可用”，但应判断为“存在需要持续观测的明显延迟风险”。V1 内测可以继续，但 demo / smoke 时不应假设 30s 内一定完成。

## 4. 建议

1. 短期继续保留 lead_analysis 60s timeout。
2. 后续 eval 继续记录 `llm_usage`，并补充 run duration / latency 统计。
3. 若 TTFT 高峰持续超过 20s 或继续触发 timeout，再拆任务评估：
   - prompt 压缩
   - lead_analysis heuristic fallback
   - 更快模型或供应商对照
4. Android UI 侧应继续把 run 状态当作异步任务展示，不要做同步等待式体验。
