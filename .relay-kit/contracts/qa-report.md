# qa-report

> Path: `.relay-kit/contracts/qa-report.md`
> Purpose: Record acceptance coverage, risk review, regression impact, and remaining gaps before declaring work complete.
> Used by: qa-governor, developer, test-hub, review-hub

## Scope checked
Claude-adoption phase 2 dashboard/eval polish advanced.

Changed surfaces:
- `relay_kit_v3/pulse.py`
- `relay_kit_v3/signal_export.py`
- `relay_kit_public_cli.py`
- `relay_kit_v3/eval_fixtures/workflow_scenarios.json`
- `tests/test_pulse_report.py`
- `tests/test_signal_export.py`
- `tests/test_workflow_eval.py`
- `README.md`
- `docs/relay-kit-pulse-report.md`
- `docs/relay-kit-signal-export.md`
- `docs/relay-kit-workflow-eval.md`
- `docs/relay-kit-upgrade-backlog.md`
- `docs/relay-kit-claude-12-adoption-matrix.md`
- `.relay-kit/contracts/project-context.md`
- `.relay-kit/contracts/qa-report.md`
- `.relay-kit/state/workflow-state.md`
- `.relay-kit/state/team-board.md`
- `.relay-kit/state/lane-registry.md`
- `.relay-kit/state/handoff-log.md`

## Acceptance coverage
- Pulse accepts context audit, lane audit, adapter diagnostics, query search, and service-boundary artifacts through include flags or JSON files.
- Pulse JSON/HTML surfaces Context Health, Lane Health, Adapter Health, Query Health, and Service Boundaries.
- Signal export emits `relay.context.stale_sources`, `relay.lanes.conflicts`, `relay.adapter.metadata_drift`, `relay.query.authoritative_hits`, and `relay.service.boundary_findings`.
- Workflow eval expands from 55 to 60 scenarios with context governance, lane audit, adapter diagnostics, query lookup, and service-boundary routing fixtures.
- Claude adoption matrix can be marked complete after PR/CI/state refresh.

## Risk matrix
- Pulse schema risk: medium. This adds top-level governance health fields while preserving prior gate summary and workflow focus fields.
- Signal metric risk: low. New metrics are additive and read existing Pulse health summaries.
- Workflow eval risk: medium. Scenario count changes from 55 to 60 and route-quality thresholds must stay green.
- State drift risk: low locally after runtime doctor live and enterprise readiness passed; remote PR CI and post-merge state refresh remain required.

## Regression surface
- Public Pulse CLI argument parsing.
- Pulse JSON/HTML rendering.
- Signal export JSON/JSONL/OTLP metrics.
- Workflow eval scenario count and route quality.
- Runtime doctor live stale-pointer and lane-audit checks.

## Evidence collected
- Red signal: focused tests first failed because Pulse had no governance artifact inputs, signal export lacked governance metrics, and workflow eval still expected 55 scenarios.
- Focused green tests: Pulse governance tests, signal metric test, and workflow eval focused test passed.
- Related tests: `python -m pytest tests\test_pulse_report.py tests\test_signal_export.py tests\test_workflow_eval.py -q` passed with 40 tests.
- Live Pulse proof: `python relay_kit_public_cli.py pulse build . --include-context-audit --include-lane-audit --include-adapter-diagnostics --include-query-search --query-search-text "dashboard eval polish" --include-service-boundaries --json --no-history` returned `status: pass`, `pulse_score: 93`, and `governance_health.status: pass`.
- Live workflow eval proof: `python scripts\eval_workflows.py . --strict --json` returned 60/60 scenarios, `weak_route_count: 0`, and `min_route_margin: 5`.
- Live signal proof: `python relay_kit_public_cli.py signal export . --otlp --json` emitted 79 signals, including the 5 new governance metrics.
- Full pytest: `python -m pytest tests -q` passed with 223 tests.
- Runtime gates: `python scripts\validate_runtime.py`, `python scripts\runtime_doctor.py . --strict --state-mode live`, and `python scripts\skill_gauntlet.py . --strict --semantic` passed; semantic gauntlet checked 141 skill files and 60 scenario fixtures with 0 findings.
- Enterprise gates: `python relay_kit_public_cli.py doctor . --skip-tests --policy-pack enterprise` passed; `python relay_kit_public_cli.py readiness check . --profile enterprise --json` returned `status: pass` and `verdict: commercial-ready-candidate`.
- Diff hygiene: `git diff --check` passed.

## Go / no-go recommendation
Go for PR CI. Do not mark Claude-adoption phase 2 complete until PR CI, merge, final main CI, and post-merge state refresh pass.
