# Task: V2 Sales Workspace Draft Review Persistence Schema

状态：planned / blocked

更新时间：2026-04-27

## Objective

为 `WorkspacePatchDraftReview` 设计正式 persistence schema。

## Blocker

必须等待 Postgres dev environment baseline 与 Sales Workspace persistence schema design 完成后才能执行。

## Scope Placeholder

- Draft Review lifecycle schema。
- review / apply result / failure reason persistence。
- base workspace version 与 stale draft 处理。
- audit trail 与 future Android review history 读取需求。

## Out Of Scope Until Unblocked

- 不写 SQLAlchemy model。
- 不写 Alembic migration。
- 不改 backend route。
- 不改 Android。
