# Readiness

Relay-kit readiness checks local governance evidence:

```bash
relay-kit readiness check /path/to/project --profile enterprise --json
```

Current readiness language is intentionally bounded. The high-confidence local verdict is `local-governance-ready-candidate`, not proof of external commercial adoption.

The readiness report separates local checks from missing external evidence. Remote CI history, release upload, paid support, and field evidence must be verified outside a local run before stronger claims are made.

Recommended local gates:

```bash
python scripts/validate_runtime.py
python scripts/skill_gauntlet.py . --strict --semantic
python scripts/runtime_doctor.py . --strict --state-mode live
python scripts/eval_workflows.py . --strict --json
python relay_kit_public_cli.py readiness check . --profile enterprise --json
```
