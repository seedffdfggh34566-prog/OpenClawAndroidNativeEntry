# Handoff: V2 Android Draft Review ID Flow Prototype

日期：2026-04-27

## Summary

本次将 Android Workspace 页面从 raw `patch_draft` apply 切换为 backend-managed `draft_review_id` flow。

Android 仍只是人工审阅入口。Runtime / Product Sales Agent execution layer 只产出 `WorkspacePatchDraft`，backend Draft Review routes 管理 review lifecycle，Sales Workspace Kernel 负责正式 workspace 写回。

## Changed

- Android client：
  - create Draft Review from runtime preview
  - accept Draft Review
  - reject Draft Review
  - apply Draft Review by id
- Android DTO / parser：
  - `SalesWorkspaceDraftReviewDto`
  - Draft Review preview / review / apply result parsing
- Workspace UI：
  - 展示 `draft_review_id`、status、preview top candidate、review decision、apply result
  - apply 成功后刷新 workspace snapshot
- Delivery docs：
  - task / handoff / docs navigation / `_active.md`

## Boundary Notes

- Android 不构造 `WorkspacePatch`。
- Android 不再调用 `/runtime/patch-drafts/prototype/apply`。
- Backend route、DB、Alembic、LangGraph、LLM/search/contact/CRM 均未改。
- Draft Review storage 仍是 prototype storage，不是正式 persistence baseline。

## Validation

- Backend targeted tests: `31 passed`
  - `PYTHONPATH=$PWD backend/.venv/bin/python -m pytest backend/tests/sales_workspace backend/tests/test_sales_workspace_api.py backend/tests/test_sales_workspace_draft_reviews_api.py -q`
- Backend full tests: `78 passed`
  - `PYTHONPATH=$PWD backend/.venv/bin/python -m pytest backend/tests -q`
- Android build:
  - `./gradlew :app:assembleDebug` passed
  - `./gradlew :app:lintDebug` passed
- Local backend smoke:
  - backend started on `127.0.0.1:8013` with JSON store
  - `scripts/seed_sales_workspace_demo.py` seeded `ws_demo` to version `3`
  - API flow verified: runtime preview -> create Draft Review -> accept -> apply by `draft_review_id`
  - final workspace version was `4`, `cand_runtime_001` ranked first, projection and ContextPack remained readable
- Device smoke:
  - `adb devices` detected `f3b59f04`
  - `adb reverse tcp:8013 tcp:8013` succeeded
  - debug APK installed successfully
  - app launched and `MainActivity` was resumed
  - full manual Workspace screen click-through was not performed by the Dev Agent

## Known Limitations

- 当前仍依赖 local backend + seeded `ws_demo`。
- 当前不实现 draft review list / history UI。
- 当前不实现 Android 自由编辑 workspace。
- Device-level 验证覆盖 install / launch；Workspace 页面完整人工点击流仍需人工确认。

## Recommended Next Step

完成本 PR review 后，下一步应先做 post-demo / post-review-id flow planning，决定是否进入 persistence decision refresh、Android UX refinement，或正式 Runtime / LangGraph integration design。
