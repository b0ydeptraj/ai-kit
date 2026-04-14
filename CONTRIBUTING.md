# Contributing to Relay-kit

Relay-kit is not a random prompt dump.

Treat changes as changes to a workflow system with:

- adapter runtime parity
- shared artifacts under `.relay-kit/`
- bundle gating
- migration safety gates for technical renames

## Before you change anything

Read the current public and runtime docs first:

- `README.md`
- `docs/relay-kit-start-flow.md`
- `docs/how-to-write-skills.md`
- `.relay-kit/docs/folder-structure.md`
- `.relay-kit/docs/bundle-gating.md`

## Contribution rules

### Skills

If you add or edit a skill:

- follow `docs/how-to-write-skills.md`
- keep descriptions in `Use when...` trigger style
- do not define the skill by persona language like "become an expert" or "act as a senior X"; define it by trigger, workflow, artifact I/O, stop condition, and next handoff
- prefer improving an existing skill or adding an alias before creating a new
  canonical skill
- keep the public surface small and easy to remember
- keep `SKILL.md` lean and move depth into `references/` or `scripts/` instead of building monolithic skill files
- do not let the same authoring path be the only reviewer; new or heavily rewritten skills must be checked by a different path such as `review-hub`, `oracle`, a gauntlet, or another review prompt path

### Docs

If you edit docs:

- prefer repo-relative paths over machine-local absolute paths
- update current docs, not stale historical notes
- keep public onboarding simple and move deep internals into docs

### Runtime and bundles

If you touch runtime generation, bundles, or validation:

- explain why the change belongs in the current bundle
- explain why it should or should not affect `baseline`
- do not break adapter parity casually
- run `scripts/migration_guard.py --strict` whenever naming or path cutover tokens could drift

## Validation

Run this before submitting a change:

```bash
python scripts/validate_runtime.py
```

If your change affects runtime naming or migration docs, also check:

```bash
python relay_kit.py --list-skills
python scripts/migration_guard.py . --strict
```

## Pull request checklist

- [ ] The change matches the current Relay-kit structure.
- [ ] Public docs and public naming stay consistent.
- [ ] No stale local path leaked into public docs.
- [ ] Bundle placement is intentional.
- [ ] New or rewritten skills are defined by workflow, not persona.
- [ ] Large skill content was split into references or scripts where appropriate.
- [ ] Skill review used a different path than the path that created the skill.
- [ ] Validation passed locally.

## What not to do

- do not turn Relay-kit into a plugin runtime
- do not import large persona systems just because they look popular
- do not expand the public surface without clear value
- do not bypass migration guard by adding broad allowlist globs
