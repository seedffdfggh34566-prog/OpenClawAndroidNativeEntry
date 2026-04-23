# AGENTS.md

## 1. Purpose

This repository is developed in an agent-assisted workflow.

The primary execution environment is:

- **Single source workspace:** `jianglab`
- **Primary control surface:** Codex app (remote project over SSH)
- **Auxiliary terminal:** FinalShell
- **Canonical repository:** the Git repository on `jianglab`

Agents working in this repository must follow the rules in this file before making changes.

---

## 2. Current Project Status

This project is no longer centered on a generic OpenClaw native entry experiment.

### Current primary direction
Build the **V1 of an AI Sales Assistant App**.

### V1 focus
V1 should validate only the following core flow:

1. **Product learning**
2. **Lead analysis**
3. **Structured sales analysis output / report**

### Out of scope for V1
Do **not** proactively expand V1 into:

- full CRM
- contact scraping
- automatic outreach
- phone bot / auto-calling
- enterprise workflow platform
- complete native chat client rewrite
- large architecture rewrite without explicit approval

Agents must treat scope control as a top-level rule.

---

## 3. Source of Truth

### Repository source of truth
All formal code, docs, and task outputs must live in this repository.

### Workspace source of truth
The only authoritative working copy is the repository on `jianglab`.

Do not assume a Windows-local working copy is authoritative.

---

## 4. Document Ownership

### Human-owned documents
Agents may suggest edits, but must **not silently redefine** intent in these files:

- `docs/product/overview.md`
- `docs/product/*`
- `docs/adr/*`

These files define product direction, version scope, and key decisions.  
Changes to meaning or scope must be explicit.

### Agent-maintained documents
Agents are expected to create and update these when relevant:

- `docs/README.md`
- `docs/architecture/*`
- `docs/reference/*`
- `docs/delivery/tasks/*`
- `docs/how-to/*`
- `docs/delivery/handoffs/*`

Agents should keep these documents aligned with the current code and workflow reality.

---

## 5. Required Working Style

### Before starting any implementation task
An agent should first:

1. read this `AGENTS.md`
2. read `docs/README.md`
3. inspect relevant files under `docs/`
4. identify the active task from `docs/delivery/tasks/_active.md`
5. confirm current scope and non-goals
6. avoid editing unrelated areas

### Preferred execution order
For non-trivial work, use this sequence:

1. clarify task boundary
2. update or create task/spec doc if needed
3. implement the smallest viable code change
4. validate locally
5. update affected docs
6. produce a concise handoff summary

---

## 6. Scope Discipline

Agents must not:

- expand the current milestone without explicit instruction
- convert a small task into a broad refactor
- rewrite unrelated architecture “for cleanliness”
- replace current runtime assumptions unless explicitly requested
- silently introduce new product requirements

When uncertain, prefer the **smaller change**.

---

## 7. Current Runtime / Environment Assumptions

The repository is currently developed around the following environment assumptions:

- main development host: `jianglab`
- Git operations run on `jianglab`
- Android build environment runs on `jianglab`
- `adb` and device deployment run on `jianglab`
- Codex works against the remote repository on `jianglab`

Agents should not assume a local Windows build environment is canonical.

---

## 8. Git Rules

### Branching
Do not treat `main` as a scratchpad.

Preferred branch naming:

- `feat/...`
- `fix/...`
- `docs/...`
- `chore/...`

### Commit style
Use short, conventional, descriptive commit messages, for example:

- `docs: add initial AGENTS and project overview`
- `feat: add product profile data model`
- `fix: correct gateway status handling`

### Push behavior
Do not push automatically unless explicitly requested.

---

## 9. File Change Rules

### Safe areas for agent-led drafting
These are generally safe for structured drafting and iteration:

- `docs/architecture/*`
- `docs/reference/*`
- `docs/delivery/tasks/*`
- `docs/how-to/*`
- `docs/delivery/handoffs/*`

### Higher-risk areas
Be more conservative when editing:

- app entry/navigation
- build configuration
- Gradle files
- runtime integration code
- environment-sensitive scripts

Avoid touching these unless the task clearly requires it.

---

## 10. Documentation Update Rules

When a task changes behavior, structure, or workflow, the agent must update the relevant docs.

### At minimum, update:
- the active task file in `docs/delivery/tasks/`
- a handoff note in `docs/delivery/handoffs/` for non-trivial work
- a spec/runbook file if the change affects architecture or execution flow
- `docs/delivery/tasks/_active.md` if task priority or active status changes

### Do not leave:
- code updated but docs stale
- task completed without recording actual outcome
- new assumptions undocumented

---

## 11. Validation Rules

Before declaring a task complete, the agent should run the lightest meaningful validation available.

Typical commands may include:

```bash
git status
./gradlew tasks
./gradlew assembleDebug
adb devices
```

Use only the subset relevant to the task.

Do not claim success without checking the result.

---

## 12. Handoff Requirements

For meaningful tasks, create or update a handoff file under:

```text
docs/delivery/handoffs/
```

A handoff should include:

- what was changed
- which files were touched
- what was validated
- known limitations
- recommended next step

Keep handoffs concise and factual.

---

## 13. Task File Expectations

Each active task file under `docs/delivery/tasks/` should ideally include:

- objective
- scope
- out of scope
- files likely involved
- validation criteria
- current status

Agents should update task status as work progresses.

Suggested status values:

- `planned`
- `in_progress`
- `blocked`
- `done`

---

## 14. Current Priority for Agents

At the current stage, the highest priority is **workflow standardization**, not aggressive feature expansion.

Agents should prefer tasks that improve:

- repository clarity
- documentation structure
- task discipline
- handoff quality
- small, reviewable changes

Before large feature work, ensure the repository operating model is stable.

### Current execution emphasis

After the initial workflow bootstrap and API contract freeze, the next recommended engineering priority is:

> **formal backend implementation with the client remaining a control entry**

Agents should treat:

- backend-first repo alignment
- active task clarity
- minimal backend implementation readiness

as higher priority than additional Android shell expansion.

---

## 15. Default Decision Rule

When multiple implementation options exist:

- choose the option with **smaller blast radius**
- preserve current working infrastructure
- prefer explicit docs over implicit assumptions
- prefer incremental progress over ambitious rewrites

This repository values controllability and maintainability over unnecessary speed.
