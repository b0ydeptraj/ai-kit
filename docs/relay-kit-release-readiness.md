# Relay-kit release-readiness / deploy-smoke (v1)

`release-readiness` adds explicit pre-deploy and post-deploy gates so release decisions are backed by signals, not assumptions.

## Why this exists

- `ready-check` is for code review and merge readiness.
- production safety needs a separate release gate with rollback signals.

## Generate checklist only

```bash
python scripts/release_readiness.py /path/to/project --phase both
```

Checklist-only output is non-strict and must not be used as a release verdict.

## Evaluate with machine-checkable signals

Prepare a JSON file with booleans:

```json
{
  "build_passed": true,
  "tests_passed": true,
  "migration_plan_checked": true,
  "rollback_plan_ready": true,
  "healthcheck_ok": true,
  "critical_user_flow_ok": true,
  "error_rate_within_budget": true,
  "rollback_signals_clear": true
}
```

Run evaluation:

```bash
python scripts/release_readiness.py /path/to/project --phase both --signals-file release-signals.json --strict
```

Exit code:

- `0`: gate passed
- `2`: hold (one or more signals failed or are missing)
- `2`: strict mode was requested without `--signals-file`
