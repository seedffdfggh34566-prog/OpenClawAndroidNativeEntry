---
name: android-logcat-triage
description: Use when Android install, launch, crash, Termux/OpenClaw, Dashboard, backend connection, or device-only failures need adb/logcat evidence and a concise triage summary.
---

# Android Logcat Triage

Use this skill to gather and interpret Android device evidence without destructive device operations.

Read these repo files first:

1. `AGENTS.md`
2. `app/AGENTS.md`
3. the current task and related handoff or runbook

V3 direction does not automatically open Android implementation. Use this skill for evidence gathering only when the current task involves Android runtime behavior, device evidence, or backend/runtime connection symptoms.

Use Android Knowledge Base only when log interpretation depends on recent platform behavior, permissions, or system policy.

## Allowed commands

Safe default commands:

- `adb devices`
- `adb logcat -d`
- read-only `adb shell` commands when needed

Do not run destructive device commands. Do not clear logs unless the user or task explicitly asks for it.

## Workflow

1. Capture device availability with `adb devices`.
2. Collect the smallest relevant log evidence.
3. Extract key errors or warnings instead of pasting full logs.
4. Classify the failure:
   - install or launch
   - Manifest, permission, exported, or deep link
   - WebView or Dashboard
   - Termux or command dispatch
   - backend, network, or connection
   - V3 runtime API connection symptoms
5. State what is supported by evidence and what remains uncertain.

## What to report

Report:

- reproduction context
- relevant log snippets
- initial classification
- evidence-supported conclusions
- unknowns
- next evidence needed

## Stop conditions

Stop and escalate if:

- the issue cannot be reproduced
- logs are insufficient for a conclusion
- the issue is actually backend, runtime, device setup, or network environment
- interpreting the behavior requires current Android docs and they have not been checked
