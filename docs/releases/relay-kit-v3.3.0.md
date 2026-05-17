# Relay-kit v3.3.0 Release Evidence

Date: 2026-04-26
Tag: v3.3.0
Tag commit: d46f9c934805010cbf64fca00c28c6bc9dc233a9
Implementation baseline commit: d717898ed216bdb0c0655f68478c02557b169a3f
PR: https://github.com/b0ydeptraj/Relay-kit/pull/1
Final GitHub Actions: https://github.com/b0ydeptraj/Relay-kit/actions/runs/24955362678
Baseline GitHub Actions: https://github.com/b0ydeptraj/Relay-kit/actions/runs/24953893415
Release URL: https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.3.0
Published: 2026-04-26T12:01:08Z

## Verdict

Release status: published.
Local release lane: pass.
Enterprise profile readiness: local-governance-ready-candidate.
GitHub Actions Validate Runtime: success.
Post-release readiness: pass.

## Major Changes

- Real root pytest/runtime proof and CI expansion.
- Clean ai-kit to relay-kit namespace cutover with compatibility shim.
- Semantic skill gauntlet and workflow eval expanded to 20 scenarios.
- Policy guard, SRS opt-in guard, strict release/a11y evidence gates.
- Evidence ledger, Pulse report/history, and signal export.
- Readiness check requires signal export and release-lane gates.
- Support bundle includes signal export and release-lane diagnostics.
- Release-lane verification, wheel build smoke, and package install smoke.
- Contract export/import, support/SLA docs, trusted manifest, and upgrade CLI.

## Evidence Commands

- `python -m pytest -q --basetemp=.tmp\pytest-release-v3-3-0` -> 123 passed.
- `python -m pytest -q --basetemp=.tmp\pytest-release-note-commit` -> 123 passed.
- `python scripts\validate_runtime.py` -> pass.
- `python scripts\migration_guard.py . --strict` -> findings: 0.
- `python scripts\package_smoke.py . --json` -> pass; wheel `relay_kit-3.3.0-py3-none-any.whl`; installed CLI smoke passed.
- `python relay_kit_public_cli.py release verify . --require-clean --json` -> pass.
- `python relay_kit_public_cli.py readiness check . --profile enterprise --json` -> local-governance-ready-candidate, 123 passed.
- `python scripts\release_readiness.py . --phase pre --signals-file .tmp\release-v3.3.0-signals.json --strict --json` -> pass.
- `python scripts\release_readiness.py . --phase post --signals-file .tmp\release-v3.3.0-post-signals.json --strict --json` -> pass.
- GitHub Actions `Validate Runtime` run `24955362678` -> success.

## Residual Risks

- Package upload or marketplace publication is not performed by this release.
- Paid support operations are documented and diagnostically supported, but not a legal SLA.

## Rollback

- If a published release regresses, delete or supersede tag `v3.3.0`, restore main to prior stable commit `4fd2faa231709ab716f14c5505b84a9a8e904ace`, and rerun `relay-kit release verify`.
- Rollback triggers: CI failure on the release commit, package smoke failure, enterprise readiness failure, or a support-diagnosed P0 runtime regression.
