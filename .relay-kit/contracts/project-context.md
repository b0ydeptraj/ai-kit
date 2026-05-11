# project-context

> Path: `.relay-kit/contracts/project-context.md`
> Purpose: Current source-of-truth context for Relay-kit work after PyPI publication and `3.4.1` patch release proof.
> Last refreshed: 2026-05-11

## Existing architecture

- Relay-kit is a Python packaging/runtime-generation repo. Public package metadata lives in `pyproject.toml`; the installed console script is `relay-kit = "relay_kit_public_cli:main"`.
- Active runtime package code lives under `relay_kit_v3/`. The historical v3 shim package remains only for compatibility and is not the active namespace.
- Public CLI orchestration lives in `relay_kit_public_cli.py`; default runtime generation is the full enterprise bundle, while `--baseline` explicitly opts into the smaller install. Legacy generation compatibility remains in `relay_kit.py`, `relay_kit_legacy.py`, and `relay_kit_compat.py`.
- Runtime skills are generated from registry data under `relay_kit_v3/registry/` and validated by `scripts/validate_runtime.py`, `scripts/runtime_doctor.py`, `scripts/migration_guard.py`, `scripts/skill_gauntlet.py`, `scripts/policy_guard.py`, and `scripts/eval_workflows.py`.
- Adapter diagnostics live in `relay_kit_v3/adapter_diagnostics.py` and the public command is `relay-kit adapter diagnose`; enterprise readiness requires this gate to catch generated skill parity and frontmatter drift.
- Query search lives in `relay_kit_v3/query_search.py` and the public command is `relay-kit query search`; service-boundary checks live in `relay_kit_v3/service_boundaries.py` and the public command is `relay-kit service boundaries`.
- The discipline utility bundle includes `skill-evolution`, a Relay-kit-owned skill for creating, upgrading, reviewing, and pruning skills with path-scoped activation, fork context, allowed-tool stance, and semantic route proof.
- Semantic skill gauntlet now enforces `allowed-tools` frontmatter for configured profiled risk-sensitive skills and fails drift against registry tool profiles. Current profiled support skills include API, data, dependency, media, browser, and multimodal evidence utilities.
- Workflow eval now reports `quality.support_route_review` for profiled support-skill coverage, weak support routes, and nearby support-skill collisions within the support margin threshold. It also reports `quality.support_evidence_contract_review` for profiled support-skill prompt and expected-term gaps, plus `quality.support_fixture_depth_review` for report-level support fixture depth gaps. The default 70-scenario suite currently reports `weak_route_count=0` and `min_route_margin=5`, and enterprise readiness fails if weak routes appear or `min_route_margin` drops below `4`.
- Context governance first slice adds `relay-kit context audit`, source authority/freshness metadata, enriched memory-search results, continuity checkpoint source metadata, and guarded stale-main-pointer detection.
- Final differentiation PR1-PR4 added six domain skills, lifecycle command registry (13 commands), generated agent profiles (`relay-engineer`, `relay-growth`), and token-economy services (`context budget`, `context pack`, `token audit`) wired into readiness/Pulse/signal.
- Current released tag: `v3.4.1` at commit `30b34bb0361723dc65a1001f9c72ba216624c881`.
- Current package version: `3.4.1`, set in `pyproject.toml` and `.relay-kit/version.json`.

## Coding conventions

- Prefer small, verifiable slices with tests and a GitHub PR per slice.
- Use `apply_patch` for source/docs edits.
- Keep checked-in source/docs ASCII unless an existing file requires otherwise.
- Preserve generated/local artifacts under ignored paths such as `.tmp/`, `.relay-kit/signals/`, `.relay-kit/support/`, `.relay-kit/pulse/`, and `.relay-kit/manifest/`.
- For Python package versions, use PEP 440 syntax. Future post-release development lines should use `.dev0` syntax, not hyphenated dev versions.

## Dependency and toolchain rules

- Runtime supports Python `>=3.10`; local verification is currently run with Python 3.12.
- Root pytest is scoped to `tests/` through `pyproject.toml`.
- CI workflow `.github/workflows/validate-runtime.yml` is the remote release gate and runs runtime validation, pytest, runtime doctor, migration guard, policy guard, semantic skill gauntlet, workflow eval, package wheel, and package smoke checks.
- Pytest disables cacheprovider through `pyproject.toml` and tests use a workspace temp fixture so Windows temp/cache permission noise does not block root test proof.
- GitHub CLI is available at `C:\Program Files\GitHub CLI\gh.exe` in this workspace.
- `rg` may be unavailable on this Windows machine because prior calls hit access errors; PowerShell `Select-String` is the reliable fallback.

## Domain and compliance constraints

- Relay-kit is positioned as an agent workflow governance kit, not a CrewAI/n8n-style full agent runtime.
- Commercial readiness is gated by `relay-kit readiness check . --profile enterprise --json`, `relay-kit release verify . --json`, `relay-kit support request . --json`, `relay-kit support triage . --json`, `relay-kit support soak . --json`, `relay-kit publish trail . --channel pypi --json`, `relay-kit publish plan . --channel pypi --json`, `relay-kit publish evidence . --channel pypi --json`, `relay-kit publish status . --json` when package upload evidence exists, `relay-kit publish index-check . --channel pypi --strict --json` for public package-index metadata proof, `relay-kit context audit . --strict --json` for source freshness/authority proof, `relay-kit adapter diagnose . --adapter all --strict --json` for adapter parity/metadata proof, `relay-kit query search . --query <terms> --json` for ranked source lookup, `relay-kit service boundaries . --strict --json` for service-boundary proof, and `relay-kit commercial dossier . --strict --json` when external CI/release/package/SLA/support owner proof exists.
- Pulse can include package-index checks through `relay-kit pulse build . --package-index-file <path>` or `--include-package-index`, and signal export emits `relay.package_index.published` for dashboard or OTLP consumers.
- Pulse can include the commercial dossier through `relay-kit pulse build . --commercial-dossier-file <path>`, and signal export emits `relay.commercial_dossier.ready` for dashboard or OTLP consumers.
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
- PR #11 merged publication execution evidence: https://github.com/b0ydeptraj/Relay-kit/pull/11, merge commit `649c11f0117a191ddbc8b3ccfe3dcb2cdf6f3bf9`.
- PR #12 merged post-publication-evidence state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/12, merge commit `e2a823b2ec21d3b9acac1d315ae39a7be49fe3d8`.
- PR #13 merged publication trail hardening: https://github.com/b0ydeptraj/Relay-kit/pull/13, merge commit `ba765d77af7367550f18785fde3243d1b0b7af8f`.
- PR #14 merged post-publication-trail state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/14, merge commit `877d236c0c15fb0503494ef896237c41562f9ae4`.
- PR #15 merged support request intake: https://github.com/b0ydeptraj/Relay-kit/pull/15, merge commit `51aa01985d7bbac06c944dfeef1f948e7a6eddbf`.
- PR #16 merged post-support-request state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/16, merge commit `a9661a0db13deb73ead95177a72c479042e0e241`.
- PR #17 merged support request Pulse/signal visibility: https://github.com/b0ydeptraj/Relay-kit/pull/17, merge commit `c3b693a7a1ee141039f4bbaa81fea69b95cb1e07`.
- PR #18 merged post-support-Pulse state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/18, merge commit `7b1d74df5c1e66e7e21c2fff9b51dcee3437d67c`.
- PR #19 merged support bundle request-summary diagnostics: https://github.com/b0ydeptraj/Relay-kit/pull/19, merge commit `0499a66f73b51fd37b83f20575817d35f91ae2d0`.
- PR #20 merged post-support-bundle state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/20, merge commit `9b8613472bf34e0cd381fb838b999809faa15fb0`.
- PR #21 merged workflow eval layer/role coverage signals: https://github.com/b0ydeptraj/Relay-kit/pull/21, merge commit `f9cc9fa452719473389bf091a52e110626bbfa31`.
- PR #22 merged post-workflow-eval state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/22, merge commit `83e60cbe16bbf3ece194d83734969b7ade6d720c`.
- PR #23 merged publication trail status: https://github.com/b0ydeptraj/Relay-kit/pull/23, merge commit `55ead4d83215a41ec5468a78fb99f2c34330ddbb`.
- PR #24 merged post-publication-status state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/24, merge commit `10d14f31e1666f056a2fd9260d934e583ef18cdc`.
- PR #25 merged readiness pytest output hygiene: https://github.com/b0ydeptraj/Relay-kit/pull/25, merge commit `cfa83987490288b7381c4a90a685f84573ceb687`.
- PR #26 merged post-readiness-output state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/26, merge commit `b3316d0d26370e9d56ffa6c6375bd0edb271d2e0`.
- PR #27 merged support triage readiness gate: https://github.com/b0ydeptraj/Relay-kit/pull/27, merge commit `23a54d70089efc062b531db9a65d777423d9a233`.
- PR #28 merged post-support-triage state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/28, merge commit `bb64950`.
- PR #29 merged Pulse gate summary: https://github.com/b0ydeptraj/Relay-kit/pull/29, merge commit `e88a29e63b72cb250421e248edd4dce67514a868`.
- PR #30 merged post-Pulse-gate-summary state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/30, merge commit `64a8c6a`.
- PR #31 merged Pulse gate drilldowns: https://github.com/b0ydeptraj/Relay-kit/pull/31, merge commit `535be14c95f8551d42b972db160a1a1c4b251217`.
- PR #32 merged post-Pulse-drilldowns state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/32, merge commit `19f24493e300c42eefe8bc01e10aef8a8a755902`.
- PR #33 merged workflow eval scenario expansion and pytest temp hardening: https://github.com/b0ydeptraj/Relay-kit/pull/33, merge commit `8b14b6e88bb26bc6d8c972d40ec80cd8c9ee6ad0`.
- PR #34 merged post-eval-expansion state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/34, merge commit `785afcd200790bb78e08480530f2b594e2b81245`.
- PR #35 merged support operations soak: https://github.com/b0ydeptraj/Relay-kit/pull/35, merge commit `baab1a7e576cf24eaa04534f8b7f879efe79ce5d`.
- PR #36 merged post-support-soak state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/36, merge commit `a80a21298913aa8f0a4f58081ccf0b99be462222`.
- PR #37 merged workflow focus dashboard polish: https://github.com/b0ydeptraj/Relay-kit/pull/37, merge commit `585029a04505e6200f4ae0eece2303271c4f8936`.
- PR #39 merged commercial proof dossier: https://github.com/b0ydeptraj/Relay-kit/pull/39, merge commit `8a1f32ed6275f6363b405d523061e827091be89a`.
- PR #41 merged commercial dossier Pulse/signal visibility: https://github.com/b0ydeptraj/Relay-kit/pull/41, merge commit `5dc9aaa3576a53d14cde18cebaa0891efe6ae69e`.
- PR #43 merged public support proof: https://github.com/b0ydeptraj/Relay-kit/pull/43, merge commit `7a2b0a7`.
- PR #45 merged default enterprise install behavior: https://github.com/b0ydeptraj/Relay-kit/pull/45, merge commit `0712966bb510625579237c737a66cbcb0f5ae5f4`.
- PR #47 merged skill evolution utility: https://github.com/b0ydeptraj/Relay-kit/pull/47, merge commit `12ed3e9799a1f4a526db6b4b0817cb946d7defc9`.
- PR #49 merged high-risk skill tool profile gate: https://github.com/b0ydeptraj/Relay-kit/pull/49, merge commit `bd4fa1aceaebdecdce10e865aedf90d8a3e96ba1`.
- PR #51 merged risk-sensitive skill profile expansion: https://github.com/b0ydeptraj/Relay-kit/pull/51, merge commit `be367cbec5ea0f570108d25c9749329c4b622300`.
- PR #53 merged Relay-kit Claude 12 adoption matrix: https://github.com/b0ydeptraj/Relay-kit/pull/53, merge commit `5eb2065f124369958e08ddb1df704ca524431a12`.
- PR #54 merged profiled support routing scenarios: https://github.com/b0ydeptraj/Relay-kit/pull/54, merge commit `158e3ecd777e85d34717b056e3f1a77f887e9966`.
- PR #56 merged support route-noise review: https://github.com/b0ydeptraj/Relay-kit/pull/56, merge commit `350b5d57355183cf9b21f0b8c23a70f8fa1be7bf`.
- PR #58 merged support evidence-contract checks: https://github.com/b0ydeptraj/Relay-kit/pull/58, merge commit `b7a1c87e562a6de3794c82261c1de255f237882e`.
- PR #60 merged support evidence real-world fixture expansion: https://github.com/b0ydeptraj/Relay-kit/pull/60, merge commit `2fb6518271f56ffe16c3be0dde966432c61c74bc`.
- PR #62 merged support fixture depth review: https://github.com/b0ydeptraj/Relay-kit/pull/62, merge commit `a01f92aecaea48188a74fabc4ed9114b91ebe956`.
- PR #64 merged workflow role coverage fixtures: https://github.com/b0ydeptraj/Relay-kit/pull/64, merge commit `cb8f79ab17d12fca31e09d74b5c154406ab41a4e`.
- PR #66 merged workflow utility skill coverage fixtures: https://github.com/b0ydeptraj/Relay-kit/pull/66, merge commit `a13b2e248725806852c0ceb36e2f91c0bc71851b`.
- PR #71 merged workflow route-quality tightening: https://github.com/b0ydeptraj/Relay-kit/pull/71, merge commit `d089beb44f7518c191357225d72ba5729a3618ff`.
- PR #73 merged readiness route-quality gating: https://github.com/b0ydeptraj/Relay-kit/pull/73, merge commit `b59ee9a533af6dfcc0362d243b733adfccf452ca`.
- PR #75 merged stable `3.4.0` PyPI release preparation: https://github.com/b0ydeptraj/Relay-kit/pull/75, merge commit `6bf8f15a9df5287c565c5f68a1877cf5b8f0dff3`.
- PR #76 merged publication status proof hardening: https://github.com/b0ydeptraj/Relay-kit/pull/76, merge commit `ae758c52bef2cc6851b16d7bdb2d5021603bc0b7`.
- PR #77 merged installed-package doctor smoke fix and `3.4.1` patch metadata: https://github.com/b0ydeptraj/Relay-kit/pull/77, merge commit `30b34bb0361723dc65a1001f9c72ba216624c881`.
- PR #79 merged package-index maintenance and commercial dossier package-index gate: https://github.com/b0ydeptraj/Relay-kit/pull/79, merge commit `84df24cdfcfad44190abf64c110f1b0585486b85`.
- PR #80 merged post-package-index state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/80, merge commit `b659973d812589abd092aeec8887ffb5665d4e29`.
- PR #81 merged package-index Pulse/signal visibility: https://github.com/b0ydeptraj/Relay-kit/pull/81, merge commit `51ac7240b9c3b41f9e39fd3afb2a4b3a0f728d11`.
- PR #83 merged context and memory governance: https://github.com/b0ydeptraj/Relay-kit/pull/83, merge commit `e972ea3d516cb3584e028ff5b82c173009131c9e`.
- PR #84 merged runtime-doctor shallow ancestry guard: https://github.com/b0ydeptraj/Relay-kit/pull/84, merge commit `d8d428eeb57490e452e46cd36b7ba20a8dc1e0db`.
- PR #85 merged post-runtime ancestry state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/85, merge commit `9f6b5dbce8f6bf755108dc678b0528659311b14a`.
- PR #86 merged multi-lane coordination hardening: https://github.com/b0ydeptraj/Relay-kit/pull/86, merge commit `d582a7a9505ffb648f3a830232d6a0c43c3f1c71`.
- PR #87 merged post-lane audit state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/87, merge commit `5b42a377f772f3f4f5f6a41ae086253c3761347e`.
- PR #88 merged adapter/IDE bridge diagnostics: https://github.com/b0ydeptraj/Relay-kit/pull/88, merge commit `abc8eb934ab2059865c88eb4ab46b9a6e8f270d1`.
- PR #89 merged post-adapter diagnostics state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/89, merge commit `2c21dad41825783e37a3097a065f755ed7106bd8`.
- PR #90 merged query search and service-boundary mapping: https://github.com/b0ydeptraj/Relay-kit/pull/90, merge commit `91dec7608101269c7dd9bffb524b0b8a088ca1b8`.
- PR #92 merged dashboard/eval polish advanced: https://github.com/b0ydeptraj/Relay-kit/pull/92, merge commit `1653696009b3b3bda8d457b162e01e7d3ff6eda7`.
- PR #94 merged domain skill pack foundation: https://github.com/b0ydeptraj/Relay-kit/pull/94, merge commit `9dc2bab9cb79990922f25f4af67bef4f75377309`.
- PR #95 merged lifecycle command registry: https://github.com/b0ydeptraj/Relay-kit/pull/95, merge commit `b79680cfb6472116cfafff349f79399c302e1add`.
- PR #96 merged agent profile pack: https://github.com/b0ydeptraj/Relay-kit/pull/96, merge commit `608e27867884249819eed5c471eef00cdae068e7`.
- PR #97 merged token economy pack: https://github.com/b0ydeptraj/Relay-kit/pull/97, merge commit `b45a8e537b00747b53b15e4d6ce52dec26257f34`.
- PR #98 merged final differentiation docs/state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/98, merge commit `bc5975d86b869fc7cbd38eca206b85b438512f3e`.
- GitHub release `v3.4.0.dev0` pre-release published with wheel and sdist assets: https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.4.0.dev0.
- GitHub release `v3.4.0.dev0` package assets were refreshed after PR #45; a fresh venv install from the wheel URL proved `relay-kit . --codex` generates the enterprise bundle by default.
- GitHub release `v3.4.0` published: https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.4.0.
- PyPI release `3.4.0` published: https://pypi.org/project/relay-kit/3.4.0/.
- GitHub release `v3.4.1` published: https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.4.1.
- PyPI release `3.4.1` published and latest: https://pypi.org/project/relay-kit/3.4.1/.
- `python -m pip --no-cache-dir index versions relay-kit` reported `relay-kit (3.4.1)` with available versions `3.4.1, 3.4.0`.
- `python relay_kit_public_cli.py publish index-check . --channel pypi --target-version 3.4.1 --package-url https://pypi.org/project/relay-kit/3.4.1/ --strict --json` returned `status: published`, HTTP `200`, latest version `3.4.1`, release versions `3.4.0, 3.4.1`, and target file count `2`.
- Fresh PyPI venv smoke installed `relay-kit==3.4.1` from PyPI, imported `relay_kit_public_cli.py` from the venv `site-packages`, ran `relay-kit --help`, generated a Codex enterprise project with `relay-kit init <project> --codex`, and passed `relay-kit doctor <project>`.
- Publication evidence is complete for `3.4.1`: `python relay_kit_public_cli.py publish status . --strict --json` returned `status: complete`.
- Commercial dossier is ready for PyPI: `python relay_kit_public_cli.py commercial dossier . --channel pypi ... --strict --json` returned `status: ready`.
- Package-index Pulse/signal proof: focused Pulse/signal tests passed with 26 tests; live `publish index-check` returned `status: published`; Pulse build included package-index `pass`; signal export emitted `relay.package_index.published=1`.
- Latest confirmed main CI after PR #98: https://github.com/b0ydeptraj/Relay-kit/actions/runs/25685234847, conclusion `success`.

## Known sharp edges

- `v3.4.1` is the current published release tag and PyPI latest. Do not claim `3.4.0` as the smoke-clean public package; it was superseded by `3.4.1`.
- Query search, service-boundary mapping, and dashboard/eval governance surfacing are implemented. Future work should not rename the Relay-kit-owned command surface.
- `.relay-kit/manifest/bundles.json` and `.relay-kit/manifest/trust.json` are ignored generated artifacts. Regenerate and verify them locally when version, skill hashes, or trust metadata changes.
- Package smoke on Windows may emit a harmless virtualenv path casing or 8.3-name warning after successful JSON output.
- Pulse now includes `gate_summary`, per-gate `drilldown` rows, `workflow_focus`, optional `commercial_dossier`, and governance health sections for context, lanes, adapters, query, and service boundaries; signal export emits `relay.gates.*`, `relay.workflow.weak_route_count`, `relay.workflow.coverage_gap_count`, `relay.workflow.support_evidence_gap_count`, `relay.workflow.support_fixture_depth_gap_count`, `relay.commercial_dossier.ready`, `relay.context.stale_sources`, `relay.lanes.conflicts`, `relay.adapter.metadata_drift`, `relay.query.authoritative_hits`, and `relay.service.boundary_findings`.
- Workflow eval default fixtures now cover 70 production/team scenarios, cover all current registry roles and all 54 current registry skills, report `weak_route_count=0` with `min_route_margin=5`, and signal export should report `relay.workflow.scenario_count=70` after a fresh Pulse build.
- Enterprise readiness now parses workflow-eval JSON and fails the `workflow-eval` gate if weak routes are present or `min_route_margin < 4`, even when the eval command exits `0`.
- Workflow eval also reports weak route candidates and registry coverage gaps under `quality.weak_routes` and `quality.coverage_gaps`; the current bundled suite has no weak route candidates.
- Workflow eval support route review currently covers 12 profiled support routes across 6/6 profiled support skills and reports 0 weak profiled support routes and 0 nearby support route collisions after PR #60.
- Workflow eval support evidence-contract review currently covers 12 profiled support scenarios across 6/6 profiled support skills and reports 0 term gaps and 0 prompt gaps after PR #60.
- Workflow eval support fixture-depth review currently covers 12 profiled support scenarios across 6/6 profiled support skills and reports 0 depth gaps and 0 duplicate prompt pairs after PR #62.
- Lane coordination now includes `relay-kit lane audit`, which checks active-lane lock conflicts, broad lock scopes, parked-lane `resume_condition`, active-lane `wave_id`, required `depends_on`/`wave_id`/`resume_condition` columns, and handoff expected return conditions.
- Support operations now include `relay-kit support soak`, which validates P0/P1/P2 paid-support handoff fixtures and fails degraded support bundle diagnostics.
- Commercial proof now includes `relay-kit commercial dossier`, which writes `.relay-kit/commercial/commercial-dossier.json` and strict-fails unless local readiness, publication status, support triage/soak, and external CI/release/package/SLA/support owner proof are present.
- Commercial dossier proof is visible in Pulse JSON/HTML and signal export when included from the generated dossier file.
- Internal-channel commercial dossier is verified ready with GitHub release asset package URL, public support SLA, public issue intake, and owner `b0ydeptraj`.
- Default package onboarding is now full by default: install the package, then run `relay-kit . --codex`; use `relay-kit . --codex --baseline` only for the smaller bundle.
- Skill changes should use `skill-evolution` and include trigger/frontmatter/allowed-tool review plus semantic gauntlet or route proof before claiming behavior changed. Profiled risk-sensitive skills must keep registry `allowed_tools` and generated `allowed-tools` frontmatter in sync.
- PyPI publication is verified. Future package claims should cite `https://pypi.org/project/relay-kit/3.4.1/`, the publish status artifact, the `publish index-check` output, and the fresh venv install smoke.
- `.relay-kit/contracts/project-context.md`, `.relay-kit/state/workflow-state.md`, `.relay-kit/state/team-board.md`, `.relay-kit/state/lane-registry.md`, and `.relay-kit/state/handoff-log.md` should stay synchronized after release or branch merges.
- Runtime doctor's stale-main-pointer check must not treat shallow checkout or unknown ancestor status as a stale-state finding. In full-history local repos it should still flag a known non-ancestor baseline.

## Files or modules to mirror

- CLI patterns: `relay_kit_public_cli.py`
- Version and upgrade logic: `relay_kit_v3/upgrade.py`, `.relay-kit/version.json`, `pyproject.toml`
- Release readiness logic: `relay_kit_v3/release_lane.py`, `relay_kit_v3/readiness.py`, `scripts/release_readiness.py`
- Publication planning and evidence logic: `relay_kit_v3/publication.py`, `relay_kit_v3/commercial_dossier.py`
- Support diagnostics, request intake, and triage logic: `relay_kit_v3/support_bundle.py`, `relay_kit_v3/support_request.py`, `relay_kit_v3/support_triage.py`
- Lane coordination logic: `relay_kit_v3/lane_audit.py`, `scripts/runtime_doctor.py`, `.relay-kit/state/team-board.md`, `.relay-kit/state/lane-registry.md`, `.relay-kit/state/handoff-log.md`
- Adapter diagnostics logic: `relay_kit_v3/adapter_diagnostics.py`, `relay_kit_public_cli.py`, `relay_kit_v3/readiness.py`, `docs/relay-kit-adapter-diagnostics.md`
- Query/service logic: `relay_kit_v3/query_search.py`, `relay_kit_v3/service_boundaries.py`, `relay_kit_public_cli.py`, `docs/relay-kit-query-search.md`, `docs/relay-kit-service-boundaries.md`
- Signal and observability logic: `relay_kit_v3/signal_export.py`, `relay_kit_v3/pulse.py`, `relay_kit_v3/evidence_ledger.py`
- Tests to mirror for new CLI slices: `tests/test_publication_plan.py`, `tests/test_commercial_dossier.py`, `tests/test_signal_export.py`, `tests/test_release_lane.py`, `tests/test_readiness_check.py`, `tests/test_public_cli_doctor.py`
- Skill-system slices should mirror `tests/test_enterprise_bundle.py` and `tests/test_skill_gauntlet_semantic.py`.
