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
The **AI Sales Assistant App V1** has been closed out as a demo-ready release candidate / learning milestone.

The repository is now in **V2 planning baseline**:

- define V2 product direction before implementation
- align docs, ADRs, data model drafts, and task entrypoints
- keep V1 assets as the validated baseline
- do not start V2 implementation unless a formal task is created under `docs/delivery/tasks/` and queued in `_active.md`

### V1 completed baseline
V1 validated the following core flow:

1. **Product learning**
2. **Lead analysis**
3. **Structured sales analysis output / report**

V1 is no longer the active implementation track. Agents may fix severe demo reproduction bugs if explicitly tasked, but must not continue adding V1 features by default.

### V2 planning baseline
V2 currently explores:

1. **AI-guided product learning**
2. **Lightweight lead research**
3. **Chinese public-web search with source evidence**
4. **Concrete company / organization candidates**
5. **Traceable contact points with manual verification boundaries**

V2 is not yet an MVP, schema baseline, API contract, or implementation queue.

### Out of scope unless explicitly approved
Do **not** proactively expand V2 into:

- full CRM
- Web frontend
- automatic outreach
- bulk contact scraping
- bulk contact export
- large-scale crawler infrastructure
- phone bot / auto-calling
- enterprise workflow platform
- complete native chat client rewrite
- large architecture rewrite without explicit approval

### V2 guardrails

- Web / search output must preserve source evidence before a candidate enters formal results.
- Company candidates without sources must remain runtime drafts, not formal lead research results.
- Contact points must be traceable to public sources and default to manual verification.
- Personal contact points are high-risk and must be explicitly marked, sourced, and never auto-contacted.
- Android remains the control entry; backend remains the formal truth layer.
- Runtime / agents may produce draft payloads and tool outputs, but backend services own formal object writeback.

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

### Agent roles

This repository uses a layered agent workflow, but the rules are written against
**responsibilities**, not tool identities.

There are 3 default roles:

- **Execution agent**: implements the current task, runs the lightest meaningful
  validation, updates task status, writes handoff notes, and creates atomic commits
- **Planning layer**: maintains direction, priorities, task queue, boundary rules,
  and stop conditions in repo docs
- **Human decision layer**: resolves product direction changes, major architecture
  changes, deployment/release decisions, and other high-risk final calls

Any agent may act as the execution agent if it follows these rules.
Do not assume the workflow depends on a specific tool name.

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

### Default execution model

The default execution model is **lightly-governed autonomy**:

- the planning layer defines boundaries, priorities, task queue, and stop conditions
- the execution agent may continue through the already-documented task queue without
  asking for per-task approval
- the execution agent must not invent new product goals or jump to undocumented
  large tasks

The next task must come from repository docs such as:

- `docs/delivery/tasks/_active.md`
- the current task's "next step" section
- another already-created follow-up task explicitly referenced from current delivery docs

When the queue is exhausted or unclear, stop and hand control back to the planning layer.

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

### Default autonomous Git model

For long-running autonomous development:

- do not use `main` as the default execution branch
- it is acceptable to continue multiple already-queued tasks on the same working branch
- each completed task must still be closed out separately with:
  - the lightest meaningful validation
  - task status update
  - handoff update
  - one atomic commit

Do not merge multiple tasks into one commit just because they were executed in one continuous run.

---

## 9. File Change Rules

### Secret handling

Agents must treat local secrets as high-risk even when they are ignored by Git.

- Never read, print, copy, summarize, or paste `backend/.env` or `backend/.env.*` contents.
- Never write API keys, Bearer tokens, Authorization headers, private keys, console metric IDs treated as secret, or other credentials into docs, task files, handoffs, PR descriptions, logs, or final answers.
- Never use `git add -f` to add ignored secret files.
- To verify local secret setup, only check presence or ignore status, for example `test -f backend/.env` or `git check-ignore -v backend/.env`.
- If a secret or secret-like identifier may have been committed or pushed, stop normal work and surface the exposure so the human can decide whether to rotate/revoke it and whether history cleanup is required.

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

In addition, the current delivery entrypoint should preferably record:

- current task
- next queued tasks
- auto-continue allowed conditions
- stop conditions

This is the minimum structure that allows an execution agent to continue safely
without per-task manual scheduling.

---

## 14. Stop Conditions For Autonomous Execution

The execution agent should stop and return control to the planning layer when:

- a product direction change is needed
- the next task is not already defined in repository docs
- docs, contract, and implementation disagree in a way that changes task meaning
- a new infrastructure dependency, migration, deployment change, or environment assumption is required
- repeated validation failures suggest the task boundary is wrong
- the work would cross a documented architecture or scope boundary
- a release, push, merge, or other high-risk irreversible action is required

The execution agent may continue without re-approval only while none of the stop conditions above are met.

---

## 14. Current Priority for Agents

At the current stage, the highest priority is **V2 planning baseline clarity**, not aggressive feature expansion.

Agents should prefer tasks that improve:

- repository clarity
- documentation structure
- task discipline
- handoff quality
- small, reviewable changes

Before large feature work, ensure the repository operating model is stable.

### Current execution emphasis

After V1 closeout, the next recommended engineering priority is:

> **V2 direction, search/contact boundaries, data model, ADR, and backend contract definition before implementation**

Agents should treat:

- backend-first repo alignment
- active task clarity
- V2 planning baseline consistency
- source-evidence and contact-boundary guardrails

as higher priority than Android UI expansion or backend feature implementation.

---

## 15. Default Decision Rule

When multiple implementation options exist:

- choose the option with **smaller blast radius**
- preserve current working infrastructure
- prefer explicit docs over implicit assumptions
- prefer incremental progress over ambitious rewrites

This repository values controllability and maintainability over unnecessary speed.

---

## 16. Scoped Rules And Platform-Specific Instructions

This repository is now a product-level mono-repo rather than an Android-only repo.

Use this root `AGENTS.md` for:

- repository-wide workflow rules
- source-of-truth rules
- Git and validation expectations
- documentation and handoff requirements
- cross-cutting escalation rules

When a task touches a platform or subsystem with its own local rule file, agents must obey both:

- this root `AGENTS.md`
- the more specific `AGENTS.md` inside the relevant subtree

Current scoped rule files:

- `app/AGENTS.md`

Therefore:

- when editing `app/`, read and follow `app/AGENTS.md`
- if future `backend/` or `ios/` local rule files are added, use the same layered rule model

This root file should not carry detailed Android implementation defaults unless they are truly repository-wide concerns.

---

## 17. Docs And Skills Boundary

This repository remains **docs-driven first**.

### 17.1 What stays in `AGENTS.md`

Keep repository-wide, stable instructions here, such as:

- workspace and environment assumptions
- validation rules
- escalation rules
- high-risk file categories
- subtree rule entry points

### 17.2 What stays in `docs/`

Keep source-of-truth project content in `docs/`, including:

- product direction and non-goals
- architecture boundaries
- API / schema references
- task status
- handoffs
- runbooks

### 17.3 What belongs in Skills

Skills are appropriate for **reusable procedures**, especially when they bundle:

- repeatable instructions
- resource references
- scripts or command sequences
- recurring evidence collection workflows

Skills should **augment** the repository workflow, not replace it.

Do **not** treat Skills as the source of truth for:

- version scope
- active task priority
- product meaning
- ADR-level decisions
- canonical API or schema definitions

If a Skill and repository docs diverge, the repository docs and current task context win.
