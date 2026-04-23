---
name: android-build-verify
description: Use when Android work needs the lightest meaningful build, lint, unit, connected, or adb device verification based on app/AGENTS.md risk levels.
---

# Android Build Verify

Use this skill to select and run the smallest safe Android verification for changes under `app/`.

Read these repo files first:

1. `AGENTS.md`
2. `app/AGENTS.md`
3. `docs/README.md`
4. the current task and handoff

If the change touches Manifest, navigation, Termux/OpenClaw, runtime integration, permissions, deep links, or device behavior, run `android-runtime-integration-guard` first.

## Commands

Use only the subset required by risk:

- `./gradlew :app:assembleDebug`
- `./gradlew :app:lintDebug`
- `./gradlew :app:testDebugUnitTest`
- `./gradlew :app:connectedDebugAndroidTest`
- `adb devices`

Prefer the bundled script for deterministic command selection:

```bash
python3 scripts/run_android_verify.py --workspace "$PWD" --mode devices
python3 scripts/run_android_verify.py --workspace "$PWD" --mode assemble
python3 scripts/run_android_verify.py --workspace "$PWD" --mode lint
python3 scripts/run_android_verify.py --workspace "$PWD" --mode unit
python3 scripts/run_android_verify.py --workspace "$PWD" --mode connected
python3 scripts/run_android_verify.py --workspace "$PWD" --mode full-local
```

`full-local` runs assemble, lint, and unit tests. It does not run connected device tests.

## What to report

Always report:

- selected verification level
- commands that actually ran
- what passed
- what failed
- what was skipped
- why any step was skipped
- whether true device evidence is still required

## Stop conditions

Stop and escalate if:

- the required validation level needs a device but no device is available
- high-risk runtime integration changed without real device evidence
- the task conflicts with `app/AGENTS.md`
- guidance depends on recent Android behavior and Android Knowledge Base has not been checked
