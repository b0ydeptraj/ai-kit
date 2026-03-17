# Relay-kit compatibility-cycle checklist

This document defines the one-cycle soak period for the technical rename from
`python_kit.py` / `python_kit_legacy.py` / `.python-kit-prompts` to
`relay_kit.py` / `relay_kit_legacy.py` / `.relay-kit-prompts`.

Use this checklist before:
- renaming the physical repo folder on disk
- removing the old entrypoint filenames
- removing the old generic prompt path alias

## What stays deferred in this cycle

- Physical repo folder rename on disk:
  - `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit`
- Absolute Windows paths in docs that still need to match the real folder
- `.python-kit-research` wording in legacy prompt text
- Any removal of `python_kit.py`, `python_kit_legacy.py`, or `.python-kit-prompts`

## Automated checks that must keep passing

Run these from:
- `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit`

```bash
python relay_kit.py --list-skills
python python_kit.py --list-skills
python relay_kit_legacy.py --list-skills
python python_kit_legacy.py --list-skills
python scripts/validate_runtime.py
```

Expected outcome:
- both new and old entrypoints succeed
- `scripts/validate_runtime.py` passes
- generic generation creates both:
  - `.relay-kit-prompts`
  - `.python-kit-prompts`
- mirrored generic output stays byte-equivalent

## Real-use soak checks

These checks should be collected over one real cycle, not in one terminal session.

### Command adoption

- [ ] New examples in active docs use `relay_kit.py` as the primary command.
- [ ] Day-to-day usage from this repo uses `relay_kit.py` first, not `python_kit.py`.
- [ ] Legacy-kit usage works through `relay_kit.py --legacy-kit ...`.
- [ ] At least one real run still succeeds through `python_kit.py` after the rename.

### Generic output compatibility

- [ ] A real generic generation run produced `.relay-kit-prompts`.
- [ ] The same run also produced `.python-kit-prompts`.
- [ ] No downstream tool or manual flow was found to depend on `.python-kit-prompts` as the only accepted path.

### Docs and scripts drift

- [ ] README keeps `relay_kit.py` as the preferred command.
- [ ] Old names appear only in compatibility/deprecation sections.
- [ ] Internal validation/scripts use `relay_kit.py` as the canonical entrypoint.
- [ ] No new docs or scripts were added that reintroduce old names as the primary path.

### Breakage watch

- [ ] No CI failures tied to the new entrypoint names.
- [ ] No reported confusion between `relay_kit.py` and `python_kit.py`.
- [ ] No runtime mismatch between `relay_kit_legacy.py` and `python_kit_legacy.py`.
- [ ] No bug reports caused by dual-write generic output.

## Removal gate for the old names

Do not remove old names until every item below is true:

- [ ] One compatibility cycle has completed.
- [ ] `relay_kit.py` has been the primary command in active docs/scripts throughout that cycle.
- [ ] `python_kit.py` and `python_kit_legacy.py` were exercised at least once after the rename and still worked.
- [ ] No downstream/manual process still requires `.python-kit-prompts` as the only location.
- [ ] CI and `scripts/validate_runtime.py` stayed green for the full cycle.
- [ ] The repo-folder rename plan is ready, because absolute path examples depend on it.

## When the removal phase starts

Only then should the next migration batch do this:

1. stop dual-writing `.python-kit-prompts`
2. remove `python_kit.py`
3. remove `python_kit_legacy.py`
4. update docs to remove compatibility examples
5. rename the physical repo folder on disk and then refresh absolute path references

## Decision record

If the cycle ends cleanly, record:
- cycle start commit
- cycle end commit
- whether any downstream command still needed the old names
- whether repo-folder rename is approved as the next batch
