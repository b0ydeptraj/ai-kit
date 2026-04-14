# Relay-kit Phase 3 Cutover Log

Date opened: 2026-04-14
Owner: runtime-core
Policy override: approved to start on 2026-04-14

## Objective
Complete phase-3 cutover with canonical runtime paths and no active compatibility aliases.

## Batch status

### Batch 0 - Baseline and freeze
- Status: complete
- Gates locked:
  - `python scripts/validate_runtime.py`
  - `python scripts/skill_gauntlet.py --strict`
  - `python scripts/migration_guard.py . --strict`
  - adapter smoke: codex, claude, antigravity, generic
- Rollback policy:
  - stop batch on first failed gate
  - rollback to previous stable commit tag and rerun full gate before merge

### Batch 1 - Pre-cutover guard
- Status: complete
- Deliverables:
  - `scripts/migration_guard.py`
  - `scripts/migration_guard_allowlist.txt`
  - `migration-guard` runtime skill
  - validate gate now enforces migration guard

### Batch 2 - Canonical path cutover
- Status: complete
- Deliverables:
  - canonical artifact root switched to `.relay-kit/`
  - generic output switched to `.relay-kit-prompts/`
  - generator/runtime/docs updated for canonical paths

### Batch 3 - Remove compatibility layer
- Status: complete
- Deliverables:
  - removed `python_kit.py`
  - removed `python_kit_legacy.py`
  - removed `.python-kit-prompts` dual-write from runtime output
  - post-cutover validation script updated

### Batch 4 - Physical repo rename
- Status: pending manual execution
- Scope:
  - rename physical repo folder `python-kit -> relay-kit`
  - refresh any machine-specific absolute paths
  - run real-project smoke checks after rename
- Runbook:
  - `docs/relay-kit-phase3-rename-runbook.md`

## Acceptance checklist
- [x] canonical runtime path switched to `.relay-kit`
- [x] compatibility entrypoints removed from runtime and packaging
- [x] migration guard passes with historical allowlist
- [x] adapter smoke passed on active repo and one real project (`apps/python-kit-sales-web`)
- [ ] physical folder rename executed and verified on at least 2 real projects

## Verification evidence (2026-04-14)
- `py -3.12 scripts/skill_gauntlet.py . --strict` -> pass
- `py -3.12 scripts/migration_guard.py . --strict` -> pass
- `py -3.12 scripts/validate_runtime.py` -> pass
- `py -3.12 relay_kit_public_cli.py apps/python-kit-sales-web --codex` -> pass
- `py -3.12 relay_kit_public_cli.py apps/python-kit-sales-web --claude` -> pass
- `py -3.12 relay_kit_public_cli.py apps/python-kit-sales-web --antigravity` -> pass
- `py -3.12 relay_kit_public_cli.py apps/python-kit-sales-web --generic` -> pass
- `py -3.12 relay_kit_public_cli.py . --codex` -> pass
- `py -3.12 relay_kit_public_cli.py . --generic` -> pass

## Notes
- Historical compatibility docs remain intentionally allowlisted for traceability.
- Active runtime surfaces are expected to contain no old compatibility tokens.
