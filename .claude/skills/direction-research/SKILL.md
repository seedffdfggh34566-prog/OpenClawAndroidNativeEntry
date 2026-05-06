---
name: direction-research
description: Research external agent systems (Letta, Hermes, Codex, Claude Code, etc.) or internal architecture gaps to produce feasibility analysis and actionable direction recommendations. Trigger phrases: "research Letta", "compare with Hermes", "feasibility study", "direction research", "how does X handle memory".
---

# Direction Research

Investigate external agent architectures or internal implementation gaps to inform V3 product and technical decisions.

## Read first

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/adr/ADR-009-v3-memory-native-sales-agent-direction.md`
4. `docs/architecture/v3/memory-native-sales-agent.md`
5. `docs/delivery/tasks/_active.md`
6. Any user-provided links, files, or specific questions

## Scope

Blend external research with internal context:
- Identify specific mechanisms in the target system (memory management, tool use, sandbox/working state, persistence, runtime).
- Compare against the current V3 implementation or planned direction.
- Highlight concrete practices that are adoptable, inapplicable, or require further investigation.

## Information sources

Priority order:
1. User-provided files, links, or quotes
2. Local project docs and code (`backend/`, `web/`, `docs/`)
3. `WebFetch` / `WebSearch` for external reference material

Do not guess at implementation details. If the source is unclear, state the uncertainty.

## Output

Keep the structure flexible, but the report must include:
- A concise summary of the target system's relevant mechanism(s)
- A direct comparison to current V3 status (what we have, what we lack, what differs)
- A clear recommendation: adopt / adapt / defer / reject, with reasoning

Do not produce open-ended lists without a conclusion.

## Persistence

Before writing to disk, ask the user for confirmation. Preferred locations:
- `docs/research/<topic>.md` for general architecture research
- Adjacent to the relevant ADR or task file if the research feeds a pending decision

## Stop conditions

Stop and escalate if:
- the research question is too broad to yield an actionable conclusion
- the user has not provided a specific target system or internal area to compare
- the conclusion would require deciding product priority or scope beyond the current task
