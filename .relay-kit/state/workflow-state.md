# workflow-state

## Current request
Expand the Pulse dashboard and signal export so publication-plan readiness is visible alongside workflow eval, readiness, and evidence signals.

## Active lane
- Lane id: primary
- Mode: serial
- Lane owner: Codex

## Active orchestration
- Layer-1 orchestrator: workflow-router
- Layer-2 workflow hub: fix-hub
- Active specialist: developer

## Active utility providers
- Primary utility provider: testing-patterns
- Additional utilities in play: evidence-before-completion

## Active standalone/domain skill
- Skill: developer
- Why selected: the next slice is the planned dashboard/eval expansion after publication workflow hardening.

## Complexity level
- Level: L2
- Reasoning: the change touches Pulse report generation, CLI options, signal export metrics, docs, and tests.

## Chosen track
- Track: product-flow
- Why this track fits: the slice expands the user-facing quality dashboard without changing release gates.

## Completed artifacts
- [ ] product-brief
- [ ] PRD
- [ ] architecture
- [ ] epics
- [ ] story
- [ ] tech-spec
- [ ] investigation-notes
- [x] project-context
- [x] qa-report
- [x] team-board
- [x] lane-registry
- [x] handoff-log

## Ownership locks
| Artifact | Owner lane | Lock scope | Status |
|---|---|---|---|
| none | none | none | none |

## Next skill
test-hub

## Known blockers
Package upload, marketplace publication, and legal SLA commitments remain external release actions outside the local repo gates.

## Escalation triggers noticed
Future work that changes package metadata, release artifacts, trusted manifest data, readiness gates, CI gates, or support diagnostics should remain on an enterprise-flow path.

## Current source of truth
- Published release: https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.3.0.
- Published tag commit: `d46f9c934805010cbf64fca00c28c6bc9dc233a9`.
- Current mainline package version: `3.4.0.dev0`.
- Latest confirmed main CI: https://github.com/b0ydeptraj/Relay-kit/actions/runs/25064747698, conclusion `success`.
- PR #1 merged release readiness and package smoke gates: https://github.com/b0ydeptraj/Relay-kit/pull/1.
- PR #2 merged Relay OTLP signal export: https://github.com/b0ydeptraj/Relay-kit/pull/2.
- PR #3 merged next-dev version hygiene: https://github.com/b0ydeptraj/Relay-kit/pull/3.
- PR #5 merged OTLP readiness/support evidence: https://github.com/b0ydeptraj/Relay-kit/pull/5.
- PR #6 merged CI action hardening: https://github.com/b0ydeptraj/Relay-kit/pull/6.
- PR #7 merged publication plan gate: https://github.com/b0ydeptraj/Relay-kit/pull/7.
- PR #8 merged backlog note hygiene: https://github.com/b0ydeptraj/Relay-kit/pull/8.
- Bootstrap local verification: `python scripts\runtime_doctor.py . --strict --state-mode live`, `python relay_kit_public_cli.py doctor . --skip-tests --policy-pack enterprise`, and `python -m pytest -q --basetemp=.tmp\pytest-bootstrap-current-state-2` passed.
- Current main baseline: `a999ce90c00b050b63f85c7d348e559aa4f3d0da`.

## Recommended next lane
After this Pulse publication dashboard slice merges and CI passes, route through `workflow-router` for the next commercial-polish lane.
