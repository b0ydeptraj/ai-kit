# Relay-kit compatibility-cycle checklist (Archived)

This document is kept for migration history.

The one-cycle soak period for renaming from
`python_kit.py` / `python_kit_legacy.py` / `.python-kit-prompts` to
`relay_kit.py` / `relay_kit_legacy.py` / `.relay-kit-prompts`
was closed on `2026-04-14` during phase-3 cutover.

## Final decision (2026-04-14)

- compatibility aliases removed from active runtime:
  - `python_kit.py`
  - `python_kit_legacy.py`
  - `.python-kit-prompts`
- canonical runtime paths:
  - `relay_kit.py`
  - `relay_kit_legacy.py`
  - `.relay-kit/`
  - `.relay-kit-prompts/`

## Post-cutover mandatory gates

Run these from repo root:

```bash
python scripts/validate_runtime.py
python scripts/skill_gauntlet.py --strict
python scripts/migration_guard.py . --strict
```

Expected outcome:
- all commands pass
- no stale compatibility tokens outside allowlist
- adapter runtime generation stays parity-safe

## Batch-4 completion note

- Physical repo folder rename on disk (`python-kit -> relay-kit`) was completed on `2026-04-14`.
- Runbook retained as historical evidence: `docs/relay-kit-phase3-rename-runbook.md`

## Evidence references

- `docs/relay-kit-phase3-cutover-log.md`
- `docs/relay-kit-compatibility-log.md`
- `.relay-kit-cycle/events.jsonl`

