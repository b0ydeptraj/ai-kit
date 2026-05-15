# project-context

> Path: `.relay-kit/contracts/project-context.md`
> Purpose: Document current codebase patterns, constraints, and rules that every later step must respect.
> Used by: workflow-router, bootstrap, cook, analyst, pm, architect, scrum-master, developer, qa-governor, scout-hub

## Existing architecture
Fill in only with evidence, decisions, or open questions relevant to this artifact.

- Decision (2026-05-12): `relay_kit_v3` is the canonical runtime namespace after the Relay-kit-only naming hard-cut (`v4.0.0`, PR #100).
- Decision (2026-05-15): shell output compaction, real-world skill eval, and skill proof audit are first-class runtime proof surfaces after PR #103; PR #105 hardens that proof with 62/62 full skill coverage and backend realism checks.

## Coding conventions
Fill in only with evidence, decisions, or open questions relevant to this artifact.

- Decision (2026-05-12): new code/docs/tests use Relay-kit naming only; retired legacy labels are treated as violations.

## Dependency and toolchain rules
Fill in only with evidence, decisions, or open questions relevant to this artifact.

- Guarding rule: naming hygiene is enforced by `scripts/naming_guard.py` and is part of runtime validation gates.
- Guarding rule: enterprise readiness requires `real-world-skill-eval` and `skill-proof-audit` gates so new skills cannot rely only on optimistic descriptions.

## Domain and compliance constraints
Fill in only with evidence, decisions, or open questions relevant to this artifact.

No evidence recorded yet.

## Known sharp edges
Fill in only with evidence, decisions, or open questions relevant to this artifact.

- Breaking change: legacy bundle labels and legacy-kit CLI compatibility surfaces are retired in the `4.0.0` hard-cut.
- Proof boundary: `field-tested` skill status requires explicit `.relay-kit/evidence/skill-field-evidence.json` metadata; Relay-kit does not infer customer deployment proof from synthetic or real-world fixture coverage.

## Files or modules to mirror
Fill in only with evidence, decisions, or open questions relevant to this artifact.

- `scripts/naming_guard.py`
- `tests/test_naming_guard.py`
- `relay_kit_public_cli.py` (list-skills and gate surfaces)
- `relay_kit_v3/shell_compaction.py`
- `relay_kit_v3/real_world_eval.py`
- `relay_kit_v3/skill_proof.py`
