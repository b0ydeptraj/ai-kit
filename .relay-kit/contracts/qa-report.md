# qa-report

> Path: `.relay-kit/contracts/qa-report.md`
> Purpose: Record acceptance coverage, risk review, regression impact, and remaining gaps before declaring work complete.
> Used by: qa-governor, developer, test-hub, review-hub

## Scope checked
Post-context governance follow-up after PR #83:
- refresh live state after context/memory governance merged
- fix runtime-doctor stale-main-pointer behavior for shallow GitHub checkout

Changed surfaces:
- `scripts/runtime_doctor.py`
- `relay_kit_v3/context_governance.py`
- `tests/test_context_governance.py`
- live state artifacts and project context

## Acceptance coverage
- Runtime doctor still flags a known stale baseline on `main` when a concrete non-ancestor HEAD is supplied.
- Runtime doctor does not fail when Git cannot determine ancestry, such as shallow GitHub checkout.
- Context audit uses the same tri-state ancestor stance so unknown ancestry is not misreported as stale.
- Live state now records PR #83, merge commit `e972ea3d516cb3584e028ff5b82c173009131c9e`, and the failed main CI run `25608258138` that this branch repairs.

## Risk matrix
- State drift risk: lower after refresh.
- CI risk: lower. Unknown ancestry is treated as non-actionable instead of a hard stale finding.
- Regression risk: low-medium. The fix touches runtime doctor and context audit helper behavior; covered by focused tests and live runtime doctor.

## Regression surface
- Runtime doctor live mode on GitHub Actions shallow checkout.
- Context audit stale-main-baseline finding behavior.
- Future post-merge state refresh flow.

## Evidence collected
- Focused tests: `python -m pytest tests\test_context_governance.py -q` passed with 7 tests.
- Runtime doctor live: `python scripts\runtime_doctor.py . --strict --state-mode live` returned 0 findings.
- Context audit: `python relay_kit_public_cli.py context audit . --strict --json` returned `status: pass`.
- Full tests: `python -m pytest tests -q` passed with 201 tests.
- Runtime validation: `python scripts\validate_runtime.py` passed.
- Semantic gauntlet: `python scripts\skill_gauntlet.py . --strict --semantic` checked 141 skill files and 55 scenario fixtures with 0 findings.
- Enterprise doctor: `python relay_kit_public_cli.py doctor . --skip-tests --policy-pack enterprise` passed all gates.
- Enterprise readiness: `python relay_kit_public_cli.py readiness check . --profile enterprise --json` returned `status: pass` and `verdict: commercial-ready-candidate`.
- Diff hygiene: `git diff --check` returned exit code 0.

## Go / no-go recommendation
Go for PR. Remaining gate is PR CI and final main CI after merge.
