# Handoff: V2.1 Android Conversation Polish

日期：2026-04-27

## Summary

Polished the existing Android Workspace screen so V2.1 chat-first turns distinguish follow-up questions, explanation answers, and Draft Review creation.

## Changed

- Added a `workspace_question` selector in the existing Workspace screen.
- Updated copy so Android does not imply every chat-first turn creates a Draft Review.
- Displayed `clarifying_question` as Sales Agent follow-up questions.
- Displayed `workspace_question` as explanation answers.
- Clarified that no-patch turns do not enable review/apply and do not write workspace state.

## Validation

```bash
./gradlew :app:assembleDebug
./gradlew :app:lintDebug
```

Result:

- Both commands passed.
- Existing Android Gradle plugin / compileSdk warning remains unchanged.

## Boundaries

- No Manifest changes.
- No navigation changes.
- No Retrofit/Hilt/Room.
- No backend route or contract changes.
- No Android formal workspace write path.

## Next

Proceed to Android conversation sample smoke and device acceptance.
