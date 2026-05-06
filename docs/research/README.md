# 实现缺口与源码机制研究

- 更新时间：2026-05-05

## 1. 范围

本目录存放**实现缺口源码研究**（implementation gap research）：

> 深入外部系统源码或内部实现，分析具体机制差异，定位当前实现缺口，为 upcoming implementation task 提供证据和方案参考。

典型内容：

- 外部系统的源码级机制分析（如 Letta agent loop、Codex context manager、Claude Code transcript 协议）。
- 内部实现缺口的根因定位与改造建议（如跨 turn tool loop 丢失、context 压缩策略缺失）。
- 具体技术机制的对比表格、代码路径引用、数据流追踪。

**不放入本目录的内容**：

- 产品/业务验证（eval、probe、acceptance、milestone closeout）→ 归入 `docs/product/research/`。
- 架构方向决策、系统分层、技术选型 → 归入 `docs/architecture/` 或 `docs/adr/`。
- 正式的 API contract、schema 定义 → 归入 `docs/reference/`。

## 2. 与相邻目录的区别

| 维度 | `docs/research/`（本目录） | `docs/product/research/` | `docs/architecture/` |
|---|---|---|---|
| **核心问题** | "参考系统实际上是怎么做的，我们缺什么，怎么补" | "产品是否可行/模型好不好/用户是否满意" | "系统应该长什么样/往哪走" |
| **内容形态** | 源码路径引用、机制对照表、数据流分析、改造建议 | 实验报告、eval 结果、probe 数据、验收结论 | 架构图、分层设计、ADR、方向文档 |
| **受众** | 实现工程师 | PM / 产品决策者 | 架构师 / 技术决策者 |
| **生命周期** | 中（与 upcoming task 绑定） | 短（与 milestone 绑定） | 长（与 ADR 强耦合） |
| **是否授权实现** | **不自动授权**。研究结论只提供证据，implementation 仍需通过 `_active.md` 或用户显式授权。 | 不授权实现，只提供产品决策依据。 | 部分授权方向，但具体实现仍需 task 授权。 |

## 3. 文件准入条件

满足以下全部条件时，可以写入本目录：

1. 有明确的外部参考系统或内部实现区域作为分析对象。
2. 包含具体的源码路径、代码行号、数据结构或协议格式引用（而非笼统概念描述）。
3. 有直接的 V3 现状对比（"我们有什么 / 缺什么 / 差异在哪"）。
4. 有明确的 recommendation（adopt / adapt / defer / reject），而非开放式列表。
5. 文档头部声明 `性质：Research-only / 不自动开放实现授权`。

## 4. 文件命名规范

```
<topic>[_<optional_subtopic>].md
```

- 全小写，单词间用下划线连接。
- 日期或版本号不加在文件名中（用文档内 frontmatter 标注）。
- 例子：
  - `cross_turn_tool_loop_persistence.md`
  - `letta_agent_loop_step_control.md`
  - `context_compression_strategies.md`

## 5. 引用规范

- 引用外部源码时，必须标注：仓库名、版本号 / commit SHA、文件路径、行号范围。
- 引用内部代码时，必须标注：文件路径、行号范围。
- 引用 ADR / architecture / product 文档时，必须标注相对路径，并说明对位关系。

## 6. 维护规则

- 当研究结论已被转化为 implementation task 并完成时，在文档末尾追加 **"Implementation status"** 小节，说明哪些结论已落地、哪些已过时。
- 当外部参考系统升级（如 Letta pin 版本变更）时，同步更新文档中的版本号与行号引用，或标注 `"verified at <version>"`。
- 不删除已过时文档；通过追加状态说明保持可追溯性。
