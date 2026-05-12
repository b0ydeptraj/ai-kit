# Changelog

All notable changes to `Relay-kit` are documented here.

## Next - 3.4.0.dev0

### Added

- Added Pulse publication-plan visibility and a `relay.publication.ready`
  signal export metric for package release dashboards.
- Added Pulse support-request visibility and a `relay.support_request.ready`
  signal export metric for paid-support operations review.
- Added support-request summary data to support bundles when a structured
  intake artifact exists.
- Added workflow eval layer/role coverage signals and exposed expected-layer
  coverage in Pulse and signal export.
- Added Pulse gate summary data and `relay.gates.*` signal metrics so dashboard
  review can see pass, attention, hold, and not-run gate counts.
- Added Pulse gate drilldowns and a `relay.gates.drilldown_items` metric so
  degraded gates point to concrete scenarios, findings, diagnostics, or events.
- Expanded bundled workflow eval coverage from 20 to 28 production/team
  scenarios, including bootstrap, debug/fix/review hubs, PM, architect,
  scrum-master, and runtime-doctor routing.
- Added `relay-kit publish status` to read publication trail/evidence artifacts
  and report complete, pending, failed, and not-observable publication steps
  without uploading packages.
- Added `relay-kit support triage` to validate support request and support
  bundle artifacts before paid-support handoff.
- Added `relay-kit publish trail` to write a publication runbook with
  deterministic capture paths and copyable commands for build, twine check,
  upload logging, plan, and evidence generation.
- Added `relay-kit publish evidence` to write a publication execution evidence
  artifact with dist hashes, twine-check proof, upload log proof, and external
  CI/release/package URLs.
- Added `relay-kit support request` to write a redacted structured support
  intake artifact with severity, environment, diagnostics, and readiness
  findings.
- Added `relay-kit publish plan` to verify package publication prerequisites
  without uploading artifacts.
- Added `relay-kit signal export --otlp` to write dependency-free Relay OTLP
  signal artifacts for external observability pipelines.
- Added OTLP artifact generation to readiness and support diagnostics so
  commercial evidence includes external-observability output paths.

### Changed

- Hardened local pytest/runtime temp handling for Windows by routing Relay-kit
  temp artifacts through workspace `.tmp` paths and disabling pytest cache
  writes.
- Readiness now runs pytest with a stable `.tmp/readiness-pytest` base temp
  directory so Windows temp-cleanup noise does not pollute readiness evidence.
- Updated the runtime validation workflow to use Node 24-ready GitHub Actions
  major versions for checkout and Python setup.
- Extended release-lane generated-artifact ignore checks to include publication
  trail and evidence artifacts under `.relay-kit/release/`.
- Extended release-lane generated-artifact ignore checks to include
  `.relay-kit/support/support-request.json`.
- Bumped post-`v3.3.0` mainline package metadata to `3.4.0.dev0` so new
  development builds cannot be confused with the published `v3.3.0` release.

## v3.3.0 - 2026-04-14

### Added

- Added `scripts/migration_guard.py` and `scripts/migration_guard_allowlist.txt`
  as the post-cutover token gate for phase-3 migration safety.
- Added the `migration-guard` utility provider skill into runtime generation and
  baseline bundles.

### Changed

- Switched canonical runtime artifact root from `.legacy-runtime/` to `.relay-kit/`.
- Switched generic prompt output to canonical `.relay-kit-prompts/` only
  (dual-write removed).
- Updated generator, registry, runtime docs, and validation gates to post-cutover
  rules.
- Updated `scripts/validate_runtime.py` to enforce `migration-guard` and the new
  canonical paths.

### Removed

- Removed compatibility entrypoints `legacy_runtime_entry.py` and `legacy_runtime_compat.py`.
- Removed compatibility generic path `.legacy-generic-prompts/` from runtime output.

## v3.2.4 - 2026-03-17

### Added

- Added `docs/relay-kit-compatibility-cycle.md` to make the Relay-kit rename
  soak period explicit.

### Changed

- Defined the deprecation/removal gate for:
  - `legacy_runtime_entry.py`
  - `legacy_runtime_compat.py`
  - `.legacy-generic-prompts`
- Documented that the physical repo-folder rename remains deferred until the
  compatibility cycle is complete.

## v3.2.3 - 2026-03-16

### Added

- Added `relay_kit.py` as the preferred Relay-kit v3 entrypoint.
- Added `relay_kit_legacy.py` as the preferred preserved legacy generator.
- Added a compatibility-safe dual-write path for generic output:
  `.relay-kit-prompts/` plus mirrored `.legacy-generic-prompts/`.

### Changed

- Switched docs, help text, and validation to present `relay_kit.py` and
  `relay_kit_legacy.py` as the preferred commands.
- Kept `legacy_runtime_entry.py`, `legacy_runtime_compat.py`, and `.legacy-generic-prompts/`
  as compatibility aliases for one migration cycle.

### Fixed

- Extended runtime validation to assert both canonical and compatibility
  entrypoints still work.
- Added generic output validation so `.relay-kit-prompts/` and
  `.legacy-generic-prompts/` stay equivalent during the migration cycle.

## v3.2.2 - 2026-03-15

### Added

- Added the official `baseline` bundle as the promoted active baseline.
- Retained `baseline-approved` as a compatibility alias during the promotion cycle.

### Changed

- Switched the public baseline status from `runtime` / `baseline-approved candidate` to
  `baseline` plus `runtime` compatibility support.
- Updated the baseline proposal, README, manifest, and bundle-gating docs to
  reflect the completed promotion.

### Fixed

- Extended runtime validation so CI now checks both the official `baseline`
  bundle and the `baseline-approved` compatibility alias.

## v3.2.1 - 2026-03-15

### Added

- Added the `baseline-approved` bundle as the smallest future-baseline candidate:
  `runtime` plus `root-cause-debugging` and `evidence-before-completion`.
- Added the `discipline-utilities` gauntlet records under
  `docs/gauntlet-runs/discipline-utilities-v1/`, including scorecards,
  pressure-round notes, and the final decision memo.
- Added runtime validation tooling:
  `scripts/validate_runtime.py` and
  `.github/workflows/validate-runtime.yml`.

### Changed

- Updated the baseline proposal so the next-baseline recommendation now follows
  gauntlet evidence instead of a provisional ranking.
- Clarified active runtime docs and the manifest so they match the current v3.2
  adapter model, bundle model, and state files.
- Labeled migration-only Codex/legacy docs as historical so they are not read
  as current runtime truth.

### Fixed

- Fixed `--ai all` for active v3 bundle generation so it now emits
  `.claude/skills`, `.agent/skills`, and `.codex/skills`.
- Fixed the remaining public docs drift around `.agent` compatibility wording,
  `bundle-gating`, and Codex adapter expectations.
- Added CI coverage for runtime parity and bundle gating so drift is caught
  before `runtime`, `baseline-approved`, or adapter outputs silently diverge.

## v3.2.0 - 2026-03-13

### Added

- Added round 4 bundles: `utility-providers`, `runtime-core`, and `runtime`.
- Added first-class layer-3 utility providers to the registry and runtime generation:
  `research`, `doc-pointers`, `sequential-thinking`, `problem-solving`,
  `multimodal-evidence`, `browser-inspector`, `repo-map`, `handoff-context`,
  `mermaid-diagrams`, `ux-structure`, and `media-tooling`.
- Added durable multi-lane state files:
  `.legacy-runtime/state/lane-registry.md` and `.legacy-runtime/state/handoff-log.md`.
- Added round 4 runtime docs:
  `.legacy-runtime/docs/utility-provider-model.md`,
  `.legacy-runtime/docs/standalone-taxonomy.md`,
  `.legacy-runtime/docs/parallelism-rules.md`,
  `.legacy-runtime/docs/bundle-gating.md`,
  `.legacy-runtime/docs/runtime-changelog.md`.
- Added `legacy_runtime_v3_namespace/registry/gating.py` to centralize bundle-aware contract, doc,
  and reference emission rules.

### Changed

- Hardened the 4-layer topology so orchestrators, workflow hubs, utility
  providers, and specialists are represented explicitly in the generator and
  runtime outputs.
- Kept `legacy_runtime_entry.py` as the active registry-driven v3 entrypoint and
  preserved `legacy_runtime_compat.py` unchanged for legacy kits.
- Updated `workflow-state.md` and `team-board.md` to support lane ownership,
  handoffs, lock scopes, and active utility-provider tracking.
- Refreshed the public README to present the repository as `Relay-kit v3.2`
  with round 4 status and bundle coverage.

### Fixed

- Fixed bundle gating so clean `core` outputs no longer emit orchestration or runtime
  contracts and docs.
- Fixed bundle gating so clean `orchestration` outputs include orchestration extras but not
  runtime-only state or docs.
- Cleaned up public documentation drift between the repo landing page and the
  actual round 4 implementation.
