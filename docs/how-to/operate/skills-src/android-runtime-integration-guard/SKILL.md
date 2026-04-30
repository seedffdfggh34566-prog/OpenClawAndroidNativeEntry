---
name: android-runtime-integration-guard
description: Use before or during high-risk Android integration changes involving Manifest, navigation, MainActivity, OpenClawApp, Termux, permissions, deep links, backend URLs, or device-only behavior.
---

# Android Runtime Integration Guard

Use this skill as the front-door risk check for Android changes that could break runtime or device behavior.

Read these repo files first:

1. `AGENTS.md`
2. `app/AGENTS.md`
3. `docs/architecture/clients/android-client-implementation-constraints.md`
4. the current task and handoff

V3 direction does not automatically open Android UI or control-entry rewrites. Treat OpenClaw, Termux, and Dashboard paths as historical/control-entry risk areas unless the current task explicitly reopens them.

If the decision depends on current Manifest, permission, deep-link, or platform behavior, consult official Android docs or Android Knowledge Base before giving the final guard conclusion.

## High-risk areas

Trigger when changes touch:

- `AndroidManifest.xml`
- `MainActivity`
- `OpenClawApp`
- `navigation/*`
- `termux/*`
- OpenClaw startup or Dashboard URL handling
- V3 runtime API or backend URL handling from Android
- permissions, exported components, intents, or deep links

## Workflow

1. Classify the changed path and behavior risk.
2. Decide whether verification must upgrade to device evidence.
3. Decide whether `android-build-verify` should run assemble, connected tests, or device checks.
4. Decide whether `android-logcat-triage` is needed for runtime evidence.
5. Stop if the change alters product/backend contract or Android's control-entry role.

## What to report

Report:

- risk category
- required validation level
- whether real device evidence is mandatory
- what evidence is currently missing
- whether the task must be split or escalated

## Stop conditions

Stop and escalate if:

- high-risk integration changed without real device evidence
- Manifest or permission boundaries are being redefined
- backend/API contract meaning changes from Android code
- Android is being expanded beyond control-entry responsibilities
- V3 Android implementation is being started without an opened task
