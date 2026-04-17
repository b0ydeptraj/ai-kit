# relay-kit release gate snapshot (2026-04-17)

This is the current go/no-go snapshot generated after P0-P3 hardening batches.

## Gate verdict

- pre-deploy: PASS
- post-deploy smoke: PASS
- overall: GO (limited beta)

## Evidence references

- runtime gate: `python scripts/validate_runtime.py` -> PASS
- skill gate: `python scripts/skill_gauntlet.py --strict` -> PASS
- migration guard: `python scripts/migration_guard.py . --strict` -> PASS
- srs guard: `python scripts/srs_guard.py . --json` -> skipped by policy (`enabled=false`, `gate=off`)
- tests: `python -m pytest -q tests` -> PASS (`7 passed`)
- soak beta log: `docs/relay-kit-beta-soak-log.md` (checkpoint `2026-04-17 15:39:50`, pass 3/3 projects)

## Release constraints

- This verdict is for current branch/runtime state only.
- Re-run all gates after any change touching registry/generator/runtime docs.
- Keep migration tokens restricted to `docs/history/**`, `docs/gauntlet-runs/**`, and explicit allowlist paths.

## Generated readiness report

See machine-generated checklist and signal evaluation:

- `docs/relay-kit-release-gate-2026-04-17.md`
- `docs/release-signals-2026-04-17.json`
