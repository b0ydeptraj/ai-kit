# qa-report

> Path: `.relay-kit/contracts/qa-report.md`
> Purpose: Record acceptance coverage, risk review, regression impact, and remaining gaps before declaring work complete.
> Used by: qa-governor, developer, test-hub, review-hub

## Scope checked
Claude-adoption phase 2 slice 3: adapter/IDE bridge diagnostics.

Changed surfaces:
- `relay_kit_v3/adapter_diagnostics.py`
- `relay_kit_public_cli.py`
- `relay_kit_v3/readiness.py`
- `tests/test_adapter_diagnostics.py`
- `tests/test_readiness_check.py`
- adapter diagnostics docs, README, Claude adoption matrix, backlog
- live state artifacts and project context

## Acceptance coverage
- `relay-kit adapter diagnose <project> --adapter all --strict --json` reports missing expected generated skills, unexpected non-allowlisted skills, metadata drift, and adapter metadata stance.
- Codex, Claude, and Agent/Antigravity surfaces are checked from the same enterprise skill registry.
- Agent/Antigravity advisory metadata is reported explicitly instead of silently implied as IDE-enforced.
- Enterprise readiness includes adapter diagnostics as a required gate.

## Risk matrix
- Adapter false-confidence risk: lower because generated skill parity and frontmatter drift are executable checks.
- CI risk: medium. Readiness now has a new required gate.
- Regression risk: medium. Public CLI, readiness, docs, and adapter metadata interpretation changed.

## Regression surface
- Public CLI command dispatch for `adapter diagnose`.
- Enterprise readiness gate aggregation.
- Generated adapter skill frontmatter expectations.
- Future Pulse/signal adapter-health consumption.

## Evidence collected
- Red test: `python -m pytest tests\test_adapter_diagnostics.py tests\test_readiness_check.py -q` first failed because `relay_kit_v3.adapter_diagnostics`, CLI `adapter diagnose`, and readiness adapter gate were missing.
- Focused green: `python -m pytest tests\test_adapter_diagnostics.py tests\test_readiness_check.py -q` passed with 13 tests.
- Live adapter diagnostics: `python relay_kit_public_cli.py adapter diagnose . --adapter all --strict --json` returned `status: pass`, 3 adapters, 47 expected skills each, 0 missing, 0 unexpected, and 0 metadata drift.
- Full test suite: `python -m pytest tests -q` passed with 214 tests.
- Runtime validation: `python scripts\validate_runtime.py` passed.
- Runtime doctor live: `python scripts\runtime_doctor.py . --strict --state-mode live` returned 0 findings.
- Semantic gauntlet: `python scripts\skill_gauntlet.py . --strict --semantic` checked 141 skill files and 55 scenario fixtures with 0 findings.
- Enterprise doctor: `python relay_kit_public_cli.py doctor . --skip-tests --policy-pack enterprise` passed.
- Enterprise readiness: `python relay_kit_public_cli.py readiness check . --profile enterprise --json` returned `verdict: commercial-ready-candidate` and included required `adapter-diagnostics` gate with 0 findings.
- Pulse: `python relay_kit_public_cli.py pulse build . --json --no-history` returned `status: pass`, `pulse_score: 93`, and 0 recent evidence failures.
- Signal export: `python relay_kit_public_cli.py signal export . --otlp --json` exported 74 signals.
- Diff hygiene: `git diff --check` passed.

## Go / no-go recommendation
Go for PR after local gates; final go remains conditional on PR CI and post-merge main CI.
