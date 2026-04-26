# workflow-state

## Current request
Continue post-release commercial polish after publishing Relay-kit v3.3.0; current slice adds Relay OTLP export for signal observability.

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
- Why selected: the release is published; remaining work is bounded code polish with tests.

## Complexity level
- Level: L4
- Reasoning: release, packaging, CI, support diagnostics, and commercial-readiness gates are enterprise-sensitive.

## Chosen track
- Track: enterprise-flow
- Why this track fits: the next step is integration and release proof, not another isolated runtime feature.

## Completed artifacts
- [ ] product-brief
- [ ] PRD
- [ ] architecture
- [ ] epics
- [ ] story
- [ ] tech-spec
- [ ] investigation-notes
- [x] qa-report
- [ ] team-board
- [ ] lane-registry
- [ ] handoff-log

## Ownership locks
| Artifact | Owner lane | Lock scope | Status |
|---|---|---|---|
| none | none | none | none |

## Next skill
test-hub

## Known blockers
Package upload or marketplace publication remains a separate external release action.

## Escalation triggers noticed
Release and packaging changes touch CI workflow, public CLI, support diagnostics, readiness gates, and package installation proof.

## Notes
Merged PR: https://github.com/b0ydeptraj/Relay-kit/pull/1.
Release: https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.3.0.
Tag commit: d46f9c934805010cbf64fca00c28c6bc9dc233a9.
Remote CI: https://github.com/b0ydeptraj/Relay-kit/actions/runs/24955362678 completed successfully.
Local release evidence: release verify passed, runtime validation passed, migration guard passed, package install smoke passed, pre-release and post-release readiness strict gates passed, and enterprise readiness returned `commercial-ready-candidate`.
Current branch: `codex/relay-otlp-export`.
Current post-release polish evidence: `python -m pytest tests\test_signal_export.py -q` passed; `python -m pytest -q --basetemp=.tmp\pytest-otlp-export` passed with 125 tests.
