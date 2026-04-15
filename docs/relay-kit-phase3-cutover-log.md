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
- Status: complete
- Scope:
  - activate new physical repo path `...\relay-kit`
  - refresh any machine-specific absolute paths
  - run real-project smoke checks after rename
- Execution notes (2026-04-14):
  - in-place rename was blocked by file lock on `...\python-kit`
  - created full mirror at `...\relay-kit` and switched execution there
  - old locked path cleanup completed after releasing file handles
- Runbook:
  - `docs/relay-kit-phase3-rename-runbook.md`

## Acceptance checklist
- [x] canonical runtime path switched to `.relay-kit`
- [x] compatibility entrypoints removed from runtime and packaging
- [x] migration guard passes with historical allowlist
- [x] adapter smoke passed on active repo and one real project (`apps/python-kit-sales-web`)
- [x] operational runtime from `...\relay-kit` verified on at least 2 real projects
- [x] old locked path `...\python-kit` removed after process lock release

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

## Batch 4 evidence (2026-04-14 18:53 +07)
- rollback tag before physical cutover:
  - `git tag -a phase3-pre-batch4-20260414 -m "Rollback point before Batch 4 physical repo rename"`
- path activation:
  - `robocopy C:\Users\b0ydeptrai\OneDrive\Documents\python-kit C:\Users\b0ydeptrai\OneDrive\Documents\relay-kit /MIR ...` -> success
- CLI reinstall from new path:
  - `pipx install --force C:\Users\b0ydeptrai\OneDrive\Documents\relay-kit` -> installed `relay-kit 3.3.0`
- post-activation gates:
  - `py -3.12 scripts/validate_runtime.py` -> pass
  - `py -3.12 scripts/skill_gauntlet.py . --strict` -> pass
  - `py -3.12 scripts/migration_guard.py . --strict` -> pass
- real-project smoke (2 projects):
  - `relay-kit C:\Users\b0ydeptrai\OneDrive\Documents\relay-kit\apps\python-kit-sales-web --codex` -> pass
  - `relay-kit C:\Users\b0ydeptrai\OneDrive\Documents\relay-kit\apps\python-kit-sales-web --claude` -> pass
  - `relay-kit C:\Users\b0ydeptrai\OneDrive\Documents\prompt-genius --antigravity` -> pass
  - `relay-kit C:\Users\b0ydeptrai\OneDrive\Documents\prompt-genius --generic` -> pass
- old-path cleanup completion (2026-04-14 19:58 +07):
  - `handle64.exe ...\python-kit` identified lock holders (`powershell.exe`, `git.exe`)
  - stopped lock-holder PIDs, then `Remove-Item ...\python-kit -Force` -> success
  - `Test-Path ...\python-kit` -> `False`

## Notes
- Historical compatibility docs remain intentionally allowlisted for traceability.
- Active runtime surfaces are expected to contain no old compatibility tokens.

## Post-cutover extension update (2026-04-15)
- Medium-risk template scrub batch completed and validated.
- Added and activated utility providers:
  - impact-radar
  - runtime-doctor
- Runtime regeneration completed for `.claude/skills`, `.agent/skills`, `.codex/skills`, and `.relay-kit/docs`.
- Additional validation evidence:
  - `py -3.12 scripts/runtime_doctor.py . --strict` -> pass
  - adapter smoke for codex, claude, antigravity, generic -> pass
