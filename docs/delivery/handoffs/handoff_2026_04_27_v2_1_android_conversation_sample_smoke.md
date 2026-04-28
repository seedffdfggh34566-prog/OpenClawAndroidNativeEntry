# Handoff: V2.1 Android Conversation Sample Smoke

日期：2026-04-27

## Summary

Defined the Android-side V2.1 conversation sample smoke for the final device acceptance pass.

## Scenario

Use the existing Workspace screen with backend-created `ws_demo`.

Representative samples:

- 工业设备维保软件。
- 中小企业财税 SaaS。

Expected Android-visible checkpoints:

- insufficient input shows Sales Agent follow-up questions;
- product turn returns a Draft Review;
- accept/apply makes product profile visible;
- direction turn returns a Draft Review;
- accept/apply makes lead direction visible;
- workspace explanation turn shows a grounded answer without enabling apply.

## Validation

The actual device commands and screenshots are recorded by the follow-up device acceptance task.

## Boundaries

- No Android auto-workspace creation.
- No real LLM.
- No V2.2 search / ContactPoint / CRM.
- No Android free-edit write path.
