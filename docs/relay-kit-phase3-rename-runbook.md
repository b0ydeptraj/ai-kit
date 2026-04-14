# Relay-kit Phase 3 Physical Rename Runbook

This runbook is for Batch 4 only.

## Goal
Perform the final physical folder rename after code-level cutover is already green.

## Preconditions
- `python scripts/validate_runtime.py` is passing.
- `python scripts/migration_guard.py . --strict` is passing.
- Working tree changes are committed or intentionally parked.

## Steps
1. Close active terminals/editors that lock files in the repo directory.
2. Rename folder:
   - from: `...\python-kit`
   - to: `...\relay-kit`
3. Reopen terminal in the renamed folder.
4. Reinstall editable or pipx package from new path if needed.
5. Run full gate:
   - `python scripts/validate_runtime.py`
6. Run adapter smoke on at least 2 real target projects:
   - `relay-kit <project-a> --codex`
   - `relay-kit <project-a> --claude`
   - `relay-kit <project-b> --antigravity`
   - `relay-kit <project-b> --generic`
7. Confirm generated outputs are canonical:
   - `.relay-kit/`
   - `.relay-kit-prompts/` (for generic mode)
8. Capture evidence and append to `docs/relay-kit-phase3-cutover-log.md`.

## Rollback
If any gate fails after physical rename:
1. Restore folder name to previous value.
2. Reopen terminal at previous path.
3. Re-run validation to confirm baseline state.
4. Fix issues in a new commit and repeat Batch 4.
