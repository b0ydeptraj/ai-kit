# workflow-state

## Current request
Add OTLP artifact generation to readiness and support diagnostics so commercial evidence covers external-observability outputs.

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
- Why selected: the next slice is a bounded commercial-readiness code change with clear tests.

## Complexity level
- Level: L3
- Reasoning: readiness and support diagnostics are commercial gates; changes must preserve release evidence behavior.

## Chosen track
- Track: enterprise-flow
- Why this track fits: the slice changes readiness/support evidence surfaces used for paid/team release claims.

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
- Latest confirmed main CI before this bootstrap: https://github.com/b0ydeptraj/Relay-kit/actions/runs/24956568795, conclusion `success`.
- PR #1 merged release readiness and package smoke gates: https://github.com/b0ydeptraj/Relay-kit/pull/1.
- PR #2 merged Relay OTLP signal export: https://github.com/b0ydeptraj/Relay-kit/pull/2.
- PR #3 merged next-dev version hygiene: https://github.com/b0ydeptraj/Relay-kit/pull/3.
- Bootstrap local verification: `python scripts\runtime_doctor.py . --strict --state-mode live`, `python relay_kit_public_cli.py doctor . --skip-tests --policy-pack enterprise`, and `python -m pytest -q --basetemp=.tmp\pytest-bootstrap-current-state-2` passed.
- Current branch: `codex/otlp-readiness-support`.

## Recommended next lane
After this slice merges and CI passes, route through `workflow-router` to pick the next implementation slice. Highest-value candidates are dashboard/eval expansion or package publication workflow hardening.
