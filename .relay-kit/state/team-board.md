# team-board

## Shared objective
Complete Claude-adoption phase 2 without mixing it into the already-complete core commercial backlog.

## Active orchestrator
- workflow-router

## Lanes
| Lane | Owner skill | Current hub | Current artifact | Lock scope | Status | depends_on | wave_id | resume_condition | Handoff status | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| primary | developer | fix-hub | dashboard/eval polish advanced | Pulse/signal/eval code, docs, tests, and live state | active | none | wave-1 | active | PR CI next | Focused governance tests, live Pulse/signal/eval proof, full pytest, runtime gates, enterprise doctor, readiness, and diff hygiene pass locally. |
| lane-2 | unassigned | none | none | none | parked | primary | wave-2 | explicitly routed by team | none | No parallel work active. |
| lane-3 | unassigned | none | none | none | parked | primary | wave-2 | explicitly routed by team | none | No parallel work active. |

## Shared artifacts that must stay authoritative
- `.relay-kit/contracts/project-context.md`
- `.relay-kit/state/workflow-state.md`
- `.relay-kit/state/lane-registry.md`
- `.relay-kit/state/handoff-log.md`
- `.relay-kit/state/team-board.md`

## Merge order
Primary dashboard/eval lane first. Parked lanes depend_on primary and resume only when explicitly routed by team.

## Merge prerequisites
Feature slice must pass focused Pulse/signal/eval tests, live Pulse/signal/eval proof, full pytest, runtime doctor, semantic gauntlet, enterprise doctor, readiness enterprise, and `git diff --check`. Remote PR CI must pass before merge.

## Conflict risks
Medium. This slice changes dashboard inputs, signal metrics, workflow eval fixture count, public Pulse CLI options, docs, and state.

## Decision log
- 2026-04-27: Refresh state artifacts instead of starting a new feature slice because project-context was empty and workflow-state still referenced completed branch work.
- 2026-04-30: Refresh state artifacts after PR #17 merged and main CI `25173791427` passed.
- 2026-04-30: Refresh state artifacts after PR #19 merged and main CI `25174419399` passed.
- 2026-05-01: Refresh state artifacts after PR #21 merged and main CI `25208682877` passed.
- 2026-05-01: Refresh state artifacts after PR #23 merged and main CI `25210492548` passed.
- 2026-05-01: Refresh state artifacts after PR #25 merged and main CI `25210793716` passed.
- 2026-05-01: Refresh state artifacts after PR #27 merged and main CI `25211668550` passed.
- 2026-05-01: Refresh state artifacts after PR #29 merged and main CI `25215207136` passed.
- 2026-05-01: Refresh state artifacts after PR #31 merged and main CI `25216356829` passed.
- 2026-05-01: Start workflow eval scenario expansion from 20 to 28 bundled scenarios on `codex/eval-scenario-expansion-v2`.
- 2026-05-01: Verify eval scenario expansion locally with root pytest, eval, doctor, runtime doctor, readiness, Pulse, and signal export.
- 2026-05-01: Refresh state artifacts after PR #33 merged and main CI `25224916323` passed.
- 2026-05-02: Start support operations soak on `codex/support-operations-soak`; local evidence includes support triage/soak strict, readiness enterprise full, doctor enterprise, runtime doctor live, and full pytest `160 passed`.
- 2026-05-02: Refresh state artifacts after PR #35 merged and main CI `25245871501` passed.
- 2026-05-02: Start workflow focus dashboard polish on `codex/dashboard-eval-polish`; full local evidence passes and CLI output includes weak-route and coverage-gap metrics.
- 2026-05-02: Refresh state artifacts after PR #37 merged and main CI `25247371453` passed.
- 2026-05-02: Refresh state artifacts after PR #39 merged and main CI `25248046721` passed.
- 2026-05-03: Refresh state artifacts after PR #41 merged and main CI `25270978879` passed.
- 2026-05-03: Refresh state artifacts after PR #43, GitHub release package assets, and internal-channel commercial dossier `ready`.
- 2026-05-03: Refresh state artifacts after PR #45 made enterprise the default install bundle, main CI `25273209967` passed, and the `v3.4.0.dev0` wheel was re-uploaded with default enterprise install proof.
- 2026-05-03: Refresh state artifacts after PR #47 added `skill-evolution`, main CI `25276702012` passed, and local readiness returned `commercial-ready-candidate`.
- 2026-05-03: Refresh state artifacts after PR #49 added high-risk skill `allowed-tools` enforcement, main CI `25277117107` passed, and local readiness returned `commercial-ready-candidate`.
- 2026-05-04: Refresh state artifacts after PR #51 added risk-sensitive support skill `allowed-tools` profiles, main CI `25280359277` passed, and local readiness returned `commercial-ready-candidate`.
- 2026-05-04: Refresh state artifacts after PR #54 added profiled support skill semantic fixtures, main CI `25311526666` passed, and local readiness returned `commercial-ready-candidate`.
- 2026-05-04: Refresh state artifacts after PR #56 added support route-noise review, main CI `25312872220` passed, and local readiness returned `commercial-ready-candidate`.
- 2026-05-05: Refresh state artifacts after PR #58 added support evidence-contract checks, main CI `25369174857` passed, and local readiness returned `commercial-ready-candidate`.
- 2026-05-05: Refresh state artifacts after PR #60 expanded support evidence fixtures to 37 workflow scenarios, main CI `25384576909` passed, and local readiness returned `commercial-ready-candidate`.
- 2026-05-06: Refresh state artifacts after PR #62 added support fixture depth review, main CI `25420592300` passed, and local readiness returned `commercial-ready-candidate`.
- 2026-05-06: Refresh state artifacts after PR #64 expanded workflow eval to 43 scenarios with all registry roles covered, main CI `25421305874` passed, and local readiness returned `commercial-ready-candidate`.
- 2026-05-06: Refresh state artifacts after PR #66 expanded workflow eval to 55 scenarios with all 47 current registry skills covered, main CI `25421911099` passed, and local readiness returned `commercial-ready-candidate`.
- 2026-05-08: Refresh state artifacts after PR #71 tightened workflow route quality to `weak_route_count=0`, main CI `25536489943` passed, and local readiness returned `commercial-ready-candidate`.
- 2026-05-08: Refresh state artifacts after PR #73 made enterprise readiness fail weak workflow routes or `min_route_margin < 4`, main CI `25537111543` passed, and local readiness returned `commercial-ready-candidate`.
- 2026-05-08: Refresh state artifacts after PR #77/PR #78 published smoke-clean PyPI `relay-kit==3.4.1`; main CI `25549224195`, PyPI install smoke, publish status, and commercial dossier passed.
- 2026-05-08: Start package-index maintenance on `codex/package-index-maintenance`; `relay-kit publish index-check` live PyPI proof returned `status: published` for `3.4.1`.
- 2026-05-08: Package-index maintenance local gates passed: 191 pytest tests, runtime validation, runtime doctor live, enterprise doctor, readiness enterprise, live index-check, and commercial dossier strict.
- 2026-05-08: Refresh state artifacts after PR #79 merged package-index maintenance; main CI `25564536474` passed.
- 2026-05-08: Start package-index Pulse/signal visibility on `codex/package-index-pulse-signals`; focused tests pass and live Pulse/signal proof shows package-index `published`.
- 2026-05-08: Refresh state artifacts after PR #81 merged package-index Pulse/signal visibility; main CI `25568791057` passed.
- 2026-05-09: Start Claude-adoption phase 2 context/memory governance on `codex/context-memory-governance`; focused tests, context audit, memory search metadata, continuity metadata, full pytest, and validate runtime pass locally.
- 2026-05-09: PR #83 merged context/memory governance; main CI `25608258138` failed in runtime doctor live because shallow checkout ancestry was treated as stale.
- 2026-05-09: Start post-context governance state refresh and runtime-doctor shallow ancestry guard on `codex/post-context-governance-state-refresh`.
- 2026-05-09: PR #84 merged runtime-doctor shallow ancestry guard; main CI `25608436233` passed.
- 2026-05-09: Start multi-lane coordination hardening on `codex/lane-coordination-audit`; target artifact is `relay-kit lane audit`.
- 2026-05-10: Refresh state artifacts after PR #86 merged multi-lane coordination hardening; main CI `25620406371` passed and next slice is adapter/IDE bridge diagnostics.
- 2026-05-10: Start adapter/IDE bridge diagnostics on `codex/adapter-bridge-diagnostics`; target artifact is `relay-kit adapter diagnose`.
- 2026-05-10: Refresh state artifacts after PR #88 merged adapter/IDE bridge diagnostics; main CI `25620846850` passed and next slice is query search plus service-boundary mapping.
- 2026-05-10: Start query search and service-boundary mapping on `codex/query-service-boundary-map`; focused tests pass and full runtime gates are next.
- 2026-05-10: Query search and service-boundary mapping local gates passed: 221 pytest tests, live query/service CLI proof, validate runtime, runtime doctor live, semantic gauntlet, enterprise doctor, readiness enterprise, Pulse, signal export, and diff hygiene.
- 2026-05-10: Refresh state artifacts after PR #90 merged query search and service-boundary mapping; main CI `25621218408` passed and next slice is dashboard/eval polish advanced.
- 2026-05-10: Start dashboard/eval polish advanced on `codex/dashboard-eval-polish-advanced`; focused Pulse/signal/eval tests pass and live Pulse/signal proof shows governance health plus 79 exported signals.
- 2026-05-10: Dashboard/eval polish advanced full local gates pass: 223 pytest tests, validate runtime, runtime doctor live, semantic gauntlet with 60 fixtures, enterprise doctor, readiness enterprise, Pulse governance, signal export, and diff hygiene.
