# team-board

## Shared objective
Keep Relay-kit post-release state current and ready for the next single-lane implementation slice.

## Active orchestrator
- workflow-router

## Lanes
| Lane | Owner skill | Current hub | Current artifact | Lock scope | Status | Handoff status | Notes |
|---|---|---|---|---|---|---|---|
| primary | bootstrap | none | project-context/workflow-state/team-board/lane-registry/handoff-log | none | ready for merge | verified | Source-of-truth refreshed after `v3.3.0`, OTLP export, and `3.4.0.dev0`. |
| lane-2 | unassigned | none | none | none | parked | none | No parallel work active. |
| lane-3 | unassigned | none | none | none | parked | none | No parallel work active. |

## Shared artifacts that must stay authoritative
- `.relay-kit/contracts/project-context.md`
- `.relay-kit/state/workflow-state.md`
- `.relay-kit/state/lane-registry.md`
- `.relay-kit/state/handoff-log.md`
- `.relay-kit/state/team-board.md`

## Merge order
Primary lane only. Parallel lanes are parked until explicitly routed.

## Merge prerequisites
Runtime doctor live mode passed, enterprise doctor passed, root pytest passed. Remote CI must pass after merge.

## Conflict risks
Low. This slice edits state/context artifacts only.

## Decision log
- 2026-04-27: Refresh state artifacts instead of starting a new feature slice because project-context was empty and workflow-state still referenced completed branch work.
