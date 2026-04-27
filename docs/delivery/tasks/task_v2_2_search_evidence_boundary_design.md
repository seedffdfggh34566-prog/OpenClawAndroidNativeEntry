# Task: V2.2 Search Evidence Boundary Design

状态：planned / blocked

更新时间：2026-04-27

## Objective

设计 V2.2 中联网搜索、来源证据、候选客户与 ContactPoint 的边界，避免无来源候选或高风险联系方式进入 formal workspace。

## Scope Placeholder

- 定义 search provider 输出如何进入 Runtime draft。
- 定义 `ResearchSource`、`CandidateObservation`、candidate evidence completeness 的最低要求。
- 定义 source fetch / source verification 的失败语义。
- 定义 ContactPoint 只读展示、人工验证和禁止自动触达边界。

## Out Of Scope Until Unblocked

- 不接真实 search provider。
- 不抓取联系方式。
- 不实现 CRM。
- 不实现自动触达。
- 不改 Android。

## Blocker

必须等待 Runtime / LangGraph design 明确后再开放。
