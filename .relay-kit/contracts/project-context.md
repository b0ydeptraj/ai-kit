# project-context

> Path: `.relay-kit/contracts/project-context.md`
> Purpose: Current source-of-truth context for Relay-kit work after the `v3.3.0` release and `3.4.0.dev0` next-dev bump.
> Last refreshed: 2026-04-29

## Existing architecture

- Relay-kit is a Python packaging/runtime-generation repo. Public package metadata lives in `pyproject.toml`; the installed console script is `relay-kit = "relay_kit_public_cli:main"`.
- Active runtime package code lives under `relay_kit_v3/`. The historical v3 shim package remains only for compatibility and is not the active namespace.
- Public CLI orchestration lives in `relay_kit_public_cli.py`; legacy generation compatibility remains in `relay_kit.py`, `relay_kit_legacy.py`, and `relay_kit_compat.py`.
- Runtime skills are generated from registry data under `relay_kit_v3/registry/` and validated by `scripts/validate_runtime.py`, `scripts/runtime_doctor.py`, `scripts/migration_guard.py`, `scripts/skill_gauntlet.py`, `scripts/policy_guard.py`, and `scripts/eval_workflows.py`.
- Current released tag: `v3.3.0` at commit `d46f9c934805010cbf64fca00c28c6bc9dc233a9`.
- Current mainline package version: `3.4.0.dev0`, set in `pyproject.toml` and `.relay-kit/version.json`.

## Coding conventions

- Prefer small, verifiable slices with tests and a GitHub PR per slice.
- Use `apply_patch` for source/docs edits.
- Keep checked-in source/docs ASCII unless an existing file requires otherwise.
- Preserve generated/local artifacts under ignored paths such as `.tmp/`, `.relay-kit/signals/`, `.relay-kit/support/`, `.relay-kit/pulse/`, and `.relay-kit/manifest/`.
- For Python package versions, use PEP 440 syntax. The post-release development line uses `3.4.0.dev0`, not `3.4.0-dev0`.

## Dependency and toolchain rules

- Runtime supports Python `>=3.10`; local verification is currently run with Python 3.12.
- Root pytest is scoped to `tests/` through `pyproject.toml`.
- CI workflow `.github/workflows/validate-runtime.yml` is the remote release gate and runs runtime validation, pytest, runtime doctor, migration guard, policy guard, semantic skill gauntlet, workflow eval, package wheel, and package smoke checks.
- GitHub CLI is available at `C:\Program Files\GitHub CLI\gh.exe` in this workspace.
- `rg` may be unavailable on this Windows machine because prior calls hit access errors; PowerShell `Select-String` is the reliable fallback.

## Domain and compliance constraints

- Relay-kit is positioned as an agent workflow governance kit, not a CrewAI/n8n-style full agent runtime.
- Commercial readiness is gated by `relay-kit readiness check . --profile enterprise --json`, `relay-kit release verify . --json`, `relay-kit publish plan . --channel pypi --json`, and `relay-kit publish evidence . --channel pypi --json` when package upload evidence exists.
- Enterprise trust metadata is deterministic, not cryptographic. `relay-kit manifest verify . --trusted` is required before enterprise readiness claims.
- Release/publication evidence must distinguish local readiness from external package upload, marketplace publication, and legal SLA commitments.

## Current release evidence

- PR #1 merged: https://github.com/b0ydeptraj/Relay-kit/pull/1, merge commit `d717898ed216bdb0c0655f68478c02557b169a3f`.
- GitHub release `v3.3.0` published: https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.3.0.
- PR #2 merged OTLP signal export: https://github.com/b0ydeptraj/Relay-kit/pull/2, merge commit `2d28d98c5f14cacd512688ca62abe601cf64ad4a`.
- PR #3 merged the next-dev version bump: https://github.com/b0ydeptraj/Relay-kit/pull/3, merge commit `aaaac9b4f43dd6e96c181f1bc917994fac887f14`.
- PR #5 merged OTLP readiness/support evidence: https://github.com/b0ydeptraj/Relay-kit/pull/5, merge commit `59d699d3a60daf41366ac3f4e9c8a2723340f9ab`.
- PR #6 merged CI action hardening: https://github.com/b0ydeptraj/Relay-kit/pull/6, merge commit `a2353e0d39f23a319deb5d341e9eff7189638021`.
- PR #7 merged publication plan gate: https://github.com/b0ydeptraj/Relay-kit/pull/7, merge commit `ee18c590524154df9747787272b11cfc6b69b416`.
- PR #8 merged backlog note hygiene: https://github.com/b0ydeptraj/Relay-kit/pull/8, merge commit `a999ce90c00b050b63f85c7d348e559aa4f3d0da`.
- PR #9 merged Pulse publication dashboard: https://github.com/b0ydeptraj/Relay-kit/pull/9, merge commit `cd74d94c527f7e2c1f38c857f822221664da1bb6`.
- PR #10 merged post-dashboard state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/10, merge commit `17de1b6cbd4b65049316305388233e0533daf281`.
- Latest confirmed main CI: https://github.com/b0ydeptraj/Relay-kit/actions/runs/25100614237, conclusion `success`.

## Known sharp edges

- `v3.3.0` remains the published release tag, while `main` is now `3.4.0.dev0`. Do not publish or package from `main` as `3.3.0`.
- `.relay-kit/manifest/bundles.json` and `.relay-kit/manifest/trust.json` are ignored generated artifacts. Regenerate and verify them locally when version, skill hashes, or trust metadata changes.
- Package smoke on Windows may emit a harmless virtualenv path casing or 8.3-name warning after successful JSON output.
- `.relay-kit/contracts/project-context.md`, `.relay-kit/state/workflow-state.md`, `.relay-kit/state/team-board.md`, `.relay-kit/state/lane-registry.md`, and `.relay-kit/state/handoff-log.md` should stay synchronized after release or branch merges.

## Files or modules to mirror

- CLI patterns: `relay_kit_public_cli.py`
- Version and upgrade logic: `relay_kit_v3/upgrade.py`, `.relay-kit/version.json`, `pyproject.toml`
- Release readiness logic: `relay_kit_v3/release_lane.py`, `relay_kit_v3/readiness.py`, `scripts/release_readiness.py`
- Publication planning and evidence logic: `relay_kit_v3/publication.py`
- Signal and observability logic: `relay_kit_v3/signal_export.py`, `relay_kit_v3/pulse.py`, `relay_kit_v3/evidence_ledger.py`
- Tests to mirror for new CLI slices: `tests/test_signal_export.py`, `tests/test_release_lane.py`, `tests/test_readiness_check.py`, `tests/test_public_cli_doctor.py`
