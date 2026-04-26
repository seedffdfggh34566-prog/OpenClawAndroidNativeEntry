# app/AGENTS.md

## 1. Purpose

This file defines Android-specific Dev Agent / Execution Agent rules for everything under `app/`.

Dev Agents / Execution Agents editing files inside `app/` must follow:

1. the root `AGENTS.md`
2. this `app/AGENTS.md`

If the two files overlap, this file is the Android-specific refinement for `app/`.

---

## 2. Android Architecture Stance

Unless a task explicitly requires otherwise, treat the current Android client as:

- a **lightweight control-entry client**
- a **Compose-first UI**
- a client that should move toward **lightweight UDF / modern MVI-style state flow**
- a client that should avoid unnecessary framework and module expansion

For new Android code and small refactors, prefer:

- immutable `UiState` style models or similarly clear screen state objects
- event -> state-holder -> UI update flow
- screen-level `ViewModel` or an equivalent state holder when a screen needs long-lived state or access to backend/data work
- simple UI-scoped state holders for UI-only behavior that depends on Android UI types
- keeping Android SDK/UI behavior logic in the UI layer when it directly depends on `Context`, navigation, snackbar, or similar UI concerns

Do **not** default to:

- heavy MVI frameworks
- Redux-like global state stores
- one-use-case-per-action Clean Architecture expansion
- broad package rewrites just to match a pattern
- introducing multiple Gradle modules before there is a clear reuse, ownership, or build-speed reason

The domain layer is optional, not mandatory. Add it only when reuse or complexity clearly justifies it.

---

## 3. Android Tool Boundaries

For Android work, prefer the lightest relevant commands on `jianglab`.

For Android architecture, SDK/API, Jetpack/Compose, Navigation, `AndroidManifest.xml`,
testing, and best-practice questions, prefer **official Android documentation /
Android Knowledge Base** as the first external reference layer.

When the question is about the **latest** version, the latest guidance, or a newly
added Android capability, consult Android Knowledge Base or equivalent official
Android docs before making a recommendation.

Android Knowledge Base is a reference layer, not the project source of truth.
Repository facts still come from the root `AGENTS.md`, this file, `docs/`, and the
current task / handoff set.

Generally allowed:

- `./gradlew :app:tasks`
- `./gradlew :app:assembleDebug`
- `./gradlew :app:testDebugUnitTest`
- `./gradlew :app:lintDebug`
- `./gradlew :app:connectedDebugAndroidTest`
- `adb devices`
- `adb install -r <apk>`
- `adb shell am start ...`
- `adb logcat -d`
- `adb shell getprop ...`

Use additional commands only when the task clearly needs them.

Do **not** make the following kinds of changes casually:

- signing / keystore changes
- package name changes
- SDK / AGP / Kotlin version upgrades
- manifest permission model changes
- destructive `adb` operations such as clearing app data or uninstalling, unless the task requires it and the action is recorded
- device-global setting changes
- treating Android CLI as a required toolchain dependency without a separate follow-up task

---

## 4. Validation Ladder For Android Changes

Agents must choose the **lightest meaningful validation** that still matches the risk of the change.

### Level 0: docs-only / non-Android behavior

Use for:

- `docs/` only changes
- task / handoff / runbook updates
- comments or wording changes that do not affect Android behavior

Typical validation:

- link / path review
- `git diff --check`

### Level 1: low-risk Android source changes

Use for:

- text-only Compose/UI tweaks
- isolated Kotlin refactors
- placeholder/state mapping changes that do not alter app entry, manifest, or device integration

Typical validation:

- `./gradlew :app:assembleDebug`

### Level 2: medium-risk Android changes

Use for:

- navigation changes
- resource changes
- screen wiring changes
- changes to app startup flow that are still host-verifiable

Typical validation:

- `./gradlew :app:assembleDebug`
- `./gradlew :app:lintDebug` when relevant
- relevant unit tests if they exist

### Level 3: behavior changes requiring a running app

Use for:

- user-visible flow changes
- interaction changes
- backend integration changes
- instrumented/UI test additions

Typical validation:

- `adb devices`
- install/run evidence on emulator or device, or `./gradlew :app:connectedDebugAndroidTest`
- concise runtime evidence summary

### Level 4: device-sensitive / environment-sensitive Android changes

Use for:

- `termux/` integration
- OpenClaw launch / dashboard connection flow
- `AndroidManifest.xml` changes affecting permissions, exported components, deep links, or process behavior
- anything depending on the current `adb` + real device workflow

Typical validation:

- `adb devices`
- install / launch evidence on a real device when the behavior is device-specific
- relevant `adb logcat -d` or shell evidence
- explicit note of what could **not** be verified if the environment is incomplete

If the required validation level cannot be met, do not over-claim completion.

---

## 5. High-Risk Android Files And Directories

Be especially conservative when editing the following categories:

- Gradle and build files
- `app/src/main/AndroidManifest.xml`
- app entry and top-level navigation files
- `MainActivity`
- files that dispatch Termux / shell / OpenClaw runtime commands
- permission, intent, deep-link, process, or exported-component code
- future Android-backend contract adapters and persistence layers

In the current repo, examples include:

- `app/build.gradle.kts`
- `app/src/main/AndroidManifest.xml`
- `app/src/main/java/com/openclaw/android/nativeentry/MainActivity.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/ui/OpenClawApp.kt`
- `app/src/main/java/com/openclaw/android/nativeentry/navigation/*`
- `app/src/main/java/com/openclaw/android/nativeentry/termux/*`

---

## 6. Real-Device Evidence Requirements

For Android tasks that affect real device behavior, provide evidence rather than generic claims.

At minimum, the handoff or final summary should record the subset that was actually checked:

- whether `adb devices` detected a target device
- whether the app was built and installed
- whether the relevant screen, flow, or command was launched
- whether there was useful `adb logcat` or shell evidence
- what was **not** verified

If a task specifically changes device-only behavior, Termux dispatch, OpenClaw launch, manifest permissions, or dashboard connectivity, emulator-only confidence is not enough unless the task explicitly says so.

---

## 7. Stop Or Escalate Conditions

Stop and ask for confirmation, or explicitly mark the task as blocked, when the work would require:

- introducing Hilt, Room, Retrofit, WorkManager, or similarly broad infrastructure without explicit approval
- introducing a heavy MVI framework
- converting the project into a large multi-module setup
- broad Clean Architecture restructuring
- changing signing, release packaging, Play-related config, package id, or SDK baselines
- changing device assumptions that are not covered by current docs
- claiming real-device correctness without real-device evidence
- changing product or backend contract meaning when the current docs have not been updated first

---

## 8. Android Definition Of Done

An Android task is not complete unless all of the following are true:

- the task stayed within the approved scope
- the smallest reasonable blast radius was used
- the required validation level was run and summarized honestly
- device evidence is included when the task risk requires it
- related docs, task, or handoff files were updated when behavior or workflow changed
- any residual risk, missing verification, or follow-up dependency is stated explicitly
