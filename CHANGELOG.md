# Changelog

All notable changes to `python-kit` are documented here.

## v3.2.0 - 2026-03-13

### Added

- Added round 4 bundles: `utility-providers`, `round4-core`, and `round4`.
- Added first-class layer-3 utility providers to the registry and runtime generation:
  `research`, `docs-seeker`, `sequential-thinking`, `problem-solving`,
  `ai-multimodal`, `chrome-devtools`, `repomix`, `context-engineering`,
  `mermaidjs-v11`, `ui-ux-pro-max`, and `media-processing`.
- Added durable multi-lane state files:
  `.ai-kit/state/lane-registry.md` and `.ai-kit/state/handoff-log.md`.
- Added round 4 runtime docs:
  `.ai-kit/docs/utility-provider-model.md`,
  `.ai-kit/docs/standalone-taxonomy.md`,
  `.ai-kit/docs/parallelism-rules.md`,
  `.ai-kit/docs/bundle-gating.md`,
  `.ai-kit/docs/round4-changelog.md`.
- Added `ai_kit_v3/registry/gating.py` to centralize bundle-aware contract, doc,
  and reference emission rules.

### Changed

- Hardened the 4-layer topology so orchestrators, workflow hubs, utility
  providers, and specialists are represented explicitly in the generator and
  runtime outputs.
- Kept `python_kit.py` as the active registry-driven v3 entrypoint and
  preserved `python_kit_legacy.py` unchanged for legacy kits.
- Updated `workflow-state.md` and `team-board.md` to support lane ownership,
  handoffs, lock scopes, and active utility-provider tracking.
- Refreshed the public README to present the repository as `Python Kit v3.2`
  with round 4 status and bundle coverage.

### Fixed

- Fixed bundle gating so clean `round2` outputs no longer emit round3 or round4
  contracts and docs.
- Fixed bundle gating so clean `round3` outputs include round3 extras but not
  round4-only state or docs.
- Cleaned up public documentation drift between the repo landing page and the
  actual round 4 implementation.

