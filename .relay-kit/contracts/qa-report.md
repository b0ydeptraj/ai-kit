# qa-report

> Path: `.relay-kit/contracts/qa-report.md`
> Purpose: Record acceptance coverage, risk review, regression impact, and remaining gaps before declaring work complete.
> Used by: qa-governor, developer, test-hub, review-hub

## Scope checked
Package-index maintenance slice after PyPI `relay-kit==3.4.1` publication.

Changed surfaces:
- `relay_kit_v3/publication.py`
- `relay_kit_v3/commercial_dossier.py`
- `relay_kit_public_cli.py`
- `tests/test_publication_plan.py`
- `tests/test_commercial_dossier.py`
- `docs/relay-kit-publication-plan.md`
- `docs/relay-kit-commercial-dossier.md`
- `docs/relay-kit-upgrade-backlog.md`
- `README.md`
- `.relay-kit/contracts/qa-report.md`
- `.relay-kit/state/workflow-state.md`
- `.relay-kit/state/team-board.md`
- `.relay-kit/state/lane-registry.md`
- `.relay-kit/state/handoff-log.md`

## Acceptance coverage
- `relay-kit publish index-check` queries PyPI/TestPyPI JSON metadata through the publication module.
- `relay-kit commercial dossier` includes the package-index gate for PyPI/TestPyPI channels.
- Strict mode fails unless the target version is present, has release files, and matches the package-index latest version.
- CLI writes `.relay-kit/release/package-index-check.json` by default, and this generated proof file is ignored.
- Docs distinguish local publication proof (`publish status`) from remote package-index metadata proof (`publish index-check`).

## Risk matrix
- State drift risk: low. This slice updates the publication tooling and live state together.
- Commercial claim risk: lower. PyPI metadata is now checked directly instead of relying only on URL and upload-log evidence.
- Regression risk: low-medium. The changed surface is CLI/publication logic, covered by focused tests and a live PyPI command run.

## Regression surface
- `relay-kit publish plan|trail|evidence|status` argument parsing and publication report rendering.
- Publication docs and commercial dossier docs.
- Live state/runtime doctor placeholder checks over `.relay-kit/state` and `.relay-kit/contracts`.

## Evidence collected
- Focused tests: `python -m pytest tests\test_publication_plan.py -q` passed with 17 tests.
- Focused tests: `python -m pytest tests\test_publication_plan.py tests\test_commercial_dossier.py -q` passed with 23 tests.
- Full tests: `python -m pytest tests -q` passed with 191 tests.
- Live package-index check: `python relay_kit_public_cli.py publish index-check . --channel pypi --target-version 3.4.1 --package-url https://pypi.org/project/relay-kit/3.4.1/ --strict --json` returned `status: published`, HTTP `200`, latest version `3.4.1`, release versions `3.4.0, 3.4.1`, and target file count `2`.
- Commercial dossier: `python relay_kit_public_cli.py commercial dossier . --channel pypi ... --strict --json` returned `status: ready` with `package-index` gate `pass`.
- Runtime validation: `python scripts\validate_runtime.py` passed.
- Runtime doctor: `python scripts\runtime_doctor.py . --strict --state-mode live` passed with findings 0.
- Enterprise doctor: `python relay_kit_public_cli.py doctor . --skip-tests --policy-pack enterprise` passed.
- Enterprise readiness: `python relay_kit_public_cli.py readiness check . --profile enterprise --json` returned `commercial-ready-candidate` with 191 pytest tests.
- PR #79 merged: https://github.com/b0ydeptraj/Relay-kit/pull/79.
- Main after PR #79: `84df24cdfcfad44190abf64c110f1b0585486b85`, with main CI https://github.com/b0ydeptraj/Relay-kit/actions/runs/25564536474 passing.

## Go / no-go recommendation
Go for post-package-index state-refresh PR after live runtime doctor, enterprise doctor, readiness, and CI pass.
