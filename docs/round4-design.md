# round4-design

Round 4 focuses on hardening the 4-layer model rather than adding more disconnected prompts.

## Objectives

1. Fix bundle gating so `round2`, `round3`, and `round4` emit the right scope of contracts and docs.
2. Promote layer-3 utility providers to first-class registry-native skills.
3. Give `team` durable state for multi-lane work via `lane-registry.md` and `handoff-log.md`.
4. Keep backward compatibility with round2 and round3 bundles.

## New bundles

- `utility-providers`
- `round4-core`
- `round4`

## New state files

- `.ai-kit/state/lane-registry.md`
- `.ai-kit/state/handoff-log.md`

## New docs

- `.ai-kit/docs/utility-provider-model.md`
- `.ai-kit/docs/standalone-taxonomy.md`
- `.ai-kit/docs/parallelism-rules.md`
- `.ai-kit/docs/bundle-gating.md`
- `.ai-kit/docs/round4-changelog.md`

## Compatibility intent

- `round2` should keep working and should not implicitly emit round3 or round4 extras in a clean output directory.
- `round3` should keep working and should not emit round4-only extras in a clean output directory.
- `round4` should emit the full hardened topology.
