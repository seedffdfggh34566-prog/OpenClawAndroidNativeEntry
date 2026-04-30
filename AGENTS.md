# AGENTS.md

## 1. Purpose

This repository is developed in an agent-assisted workflow.

Primary environment:

- Single source workspace: `jianglab`
- Primary control surface: Codex app over SSH
- Auxiliary terminal: FinalShell
- Canonical repository: this Git repository on `jianglab`

This file is a stable repository operating contract. It is not a product spec, roadmap, PRD, ADR, API contract, or architecture document.

---

## 2. Product And Task Routing

Do not treat `AGENTS.md` as product truth.

For current product direction, status, architecture, and task authorization, start from:

1. `docs/README.md`
2. `docs/product/project_status.md`
3. `docs/delivery/tasks/_active.md`
4. The current task and matching handoff, if any

Then follow links from those documents to the relevant PRD, ADR, architecture, API, or reference docs.

Historical documents under `docs/` may contain useful evidence, but they are not current direction unless the current task explicitly reopens them.

---

## 3. Source Of Truth

All formal code, docs, and task outputs must live in this repository.

The authoritative working copy is this repository on `jianglab`. Do not assume a Windows-local checkout is canonical.

Repository docs under `docs/` are the source of truth for product direction, ADRs, architecture boundaries, API contracts, task status, and handoffs. Skills may support repeatable workflows, but skills are not the source of truth for product meaning, priority, schema, API, or ADR-level decisions.

---

## 4. Startup Checklist

Before non-trivial implementation work:

1. Read this `AGENTS.md`.
2. Read `docs/README.md`.
3. Read `docs/delivery/tasks/_active.md`.
4. Read the current task and relevant handoff/spec files.
5. Read subtree rules if touching a scoped area.
6. Confirm the work is authorized by the user or current task.

When the next task is unclear, stop and ask instead of inventing a queue.

---

## 5. Task Authorization And Scope

Implementation work must come from:

- explicit user instruction in the current thread, or
- the current task in `docs/delivery/tasks/_active.md`, or
- a follow-up task explicitly referenced by current delivery docs.

Do not:

- expand the current scope without explicit instruction
- convert a small task into a broad refactor
- silently introduce new product requirements
- replace runtime, API, persistence, platform, or deployment assumptions unless asked
- start implementation only because direction docs exist
- continue work from historical task or handoff files unless reopened by current authorization

When uncertain, prefer the smallest reversible step that preserves product learning and future optionality.

---

## 6. Task, Handoff, And Completion Wording

Task files and handoffs are execution records. They may state:

- what task was completed
- what changed
- what was validated
- known limits
- recommended next step

Ordinary task files and handoffs must not casually declare a version, milestone, product phase, product experience, or production readiness complete. If the user explicitly asks for a milestone or release review, create a dedicated review document and keep evidence tied to the relevant PRD, ADR, architecture, and validation results.

---

## 7. Git Rules

Do not treat `main` as a scratchpad.

Preferred branch names:

- `codex/...` for Codex / Dev Agent branches
- `feat/...`
- `fix/...`
- `docs/...`
- `chore/...`

Do not push, merge, reset, delete branches, or remove worktrees unless explicitly asked.

Before starting unrelated work, inspect `git status --short`. Existing changes may belong to the user or another task; do not revert them unless explicitly requested.

Use short conventional commit messages when commits are requested, for example:

- `docs: rebaseline agent workflow`
- `feat: add sales memory prototype`
- `fix: correct runtime status handling`

---

## 8. Secret And File Safety

Never read, print, copy, summarize, or paste contents from:

- `backend/.env`
- `backend/.env.*`

Never write API keys, bearer tokens, authorization headers, private keys, console metric IDs treated as secret, or other credentials into docs, task files, handoffs, PR descriptions, logs, or final answers.

To verify local secret setup, only check presence or ignore status, for example:

- `test -f backend/.env`
- `git check-ignore -v backend/.env`

If a secret or secret-like value may have been committed or pushed, stop normal work and surface the exposure.

---

## 9. Documentation Rules

Documentation updates should be proportional to the change.

Update the current task and handoff for meaningful work. Update higher-level docs only when the change affects product direction, architecture, API/schema contracts, execution authorization, navigation, or project status.

Do not leave:

- code changed but relevant docs stale
- task completed without recording actual outcome
- new assumptions undocumented
- historical wording presented as current direction

Human-owned direction documents require care:

- `docs/product/overview.md`
- `docs/product/*`
- `docs/adr/*`

Agents may edit them when explicitly asked, but must not silently redefine product intent.

---

## 10. Validation Rules

Before declaring work complete, run the lightest meaningful validation available.

Examples:

```bash
git diff --check
git status --short
./gradlew assembleDebug
backend/.venv/bin/python -m pytest backend/tests
```

Use only the subset relevant to the task. Do not claim validation passed without checking command results.

---

## 11. Handoff Requirements

For meaningful tasks, create or update a handoff under:

```text
docs/delivery/handoffs/
```

A handoff should include:

- what changed
- files or areas touched
- what was validated
- known limitations
- recommended next step

Keep handoffs concise and factual.

---

## 12. Scoped Rules

This is a product-level monorepo. The root file carries repository-wide rules only.

When touching a scoped area, read and follow both this file and the local rule file:

- `app/AGENTS.md` for Android work
- `backend/AGENTS.md` for backend work

If scoped rules and root rules appear to conflict, follow the stricter safety rule and surface the conflict.

---

## 13. Skills And MCP

Use skills for reusable procedures and focused validation flows. Skills augment repo docs; they do not replace source-of-truth documents.

Current common skills:

- `repo-task-bootstrap`: structure non-backend task scope before implementation.
- `backend-task-bootstrap`: structure backend task scope before implementation.
- `task-handoff-sync`: check task, handoff, docs navigation, validation notes, and completion wording before closeout.
- `android-build-verify`, `android-logcat-triage`, `android-runtime-integration-guard`: Android validation and risk checks.
- `backend-local-verify`, `backend-api-change-check`, `backend-db-risk-check`, `backend-runtime-boundary-guard`, `backend-contract-sync`: backend validation and boundary checks.

When working with OpenAI APIs, Codex, Agents SDK, Apps SDK, or other OpenAI products, use the `openai-docs` skill and official OpenAI documentation.

If a skill and repository docs diverge, repository docs and the current task context win.

---

## 14. Default Decision Rule

Prefer small, reviewable, reversible changes.

Use `docs/` and the current task to decide product meaning. Use this file only to decide how to operate safely in the repository.
