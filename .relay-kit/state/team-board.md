# team-board

## Shared objective
Harden real-world skill eval coverage and backend realism checks before PR.

## Active orchestrator
- team

## Lanes
| Lane | Owner skill | Current hub | Current artifact | Lock scope | Status | depends_on | wave_id | resume_condition | Handoff status | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| primary | developer | test-hub | registry and generated skill surfaces | backend realism and skill proof eval scope | active | none | wave-1 | PR merge and main CI green | review pending | full real-world eval 62/62; backend realism guard added |
| lane-2 | unassigned | none | none | none | parked | primary | wave-2 | explicitly routed by team | none | empty lane |
| lane-3 | unassigned | none | none | none | parked | primary | wave-2 | explicitly routed by team | none | empty lane |

## Shared artifacts that must stay authoritative
- `.relay-kit/state/workflow-state.md`
- `.relay-kit/state/lane-registry.md`
- `.relay-kit/state/handoff-log.md`
- `.relay-kit/contracts/project-context.md`
- `.relay-kit/contracts/PRD.md`
- `.relay-kit/contracts/architecture.md`

## Merge order
wave-1 before wave-2 by default; parallel lanes must record depends_on before merge.

## Merge prerequisites
Passing gates, no active lock conflicts, handoff evidence linked, and lane audit pass.

## Conflict risks
Generated adapter skill surfaces must stay in parity with `relay_kit_v3/registry/skills.py`.

## Decision log
- 2026-05-12: Closed Relay-kit-only naming hard-cut in PR #100 and returned board to idle baseline.
- 2026-05-15: Closed proof-hardening lane in PR #103; shell compaction, real-world skill eval, and skill proof audit are merged with main CI green.
- 2026-05-15: Opened follow-up proof hardening on `codex/full-real-world-skill-eval` to expand real-world skill coverage to 62/62 and add backend realism guard.
