# Relay-kit Upgrade Backlog

This file consolidates the direct Relay-kit audit and the GitOpen benchmark into one actionable repair and upgrade backlog.

Source audit status:
- Relay-kit reviewed on main SHA `4fd2faa231709ab716f14c5505b84a9a8e904ace`.
- Local gates verified: `validate_runtime`, template `runtime_doctor`, `migration_guard`, and `skill_gauntlet` pass.
- Fixed in first P0 pass: root pytest now runs root smoke tests only, template tests are no longer collected by default, and `google-genai` is no longer imported at module load time.
- Fixed in first P1 pass: checked-in live state and generated state templates no longer contain `TBD`; `runtime_doctor --state-mode live` passes.
- Fixed in second P1 pass: `developer` no longer requires `test-first-development` when the active bundle does not provide it.
- Fixed in third P1 pass: checked-in contract artifacts and generated contract templates no longer contain `TBD`; live-mode `runtime_doctor` now checks `.relay-kit/contracts/*.md`.
- Strengthened in recursive contract placeholder pass: live-mode `runtime_doctor` now checks nested `.relay-kit/contracts/**/*.md` artifacts, including story files.
- Fixed in CI baseline pass: `.github/workflows/validate-runtime.yml` now runs pytest, runtime doctor template/live mode, migration guard, and skill gauntlet.
- Fixed in README encoding pass: `README.md` language switcher is valid UTF-8 without BOM or mojibake.
- Fixed in doctor CLI pass: `relay-kit doctor` runs the core runtime gates and `scripts/` is packaged so the console command can find them.
- Fixed in namespace cutover pass: active runtime imports now use `relay_kit_v3`; `ai_kit_v3` remains only as a one-cycle compatibility shim and allowlisted migration token.
- Fixed in semantic gauntlet baseline pass: `skill_gauntlet --semantic` checks registry parity, unknown next-step references, empty I/O contracts, and duplicate trigger descriptions within each adapter.
- Fixed in semantic scenario pass: `skill_gauntlet --semantic` now runs 12 route/evidence scenario fixtures from `tests/fixtures/skill_gauntlet/scenarios.json`.
- Fixed in SRS opt-in pass: policy-driven `srs_guard` runs from doctor/CI, defaults to off, and hard-fails only when SRS policy is enabled.
- Fixed in DX list-skills pass: preserved legacy kits are hidden from default `--list-skills` and require `--show-legacy`.
- Fixed in runtime policy guard pass: `policy_guard.py` detects deterministic secret, path traversal, destructive shell, prompt-injection, and broad allowlist risks and runs from doctor/CI.
- Fixed in workflow eval pass: `relay-kit eval run` reports scenario pass rate, predicted skill, top routes, and evidence-term findings from bundled fixtures.
- Fixed in workflow eval quality pass: `relay-kit eval run` now reports route margin, route confidence, evidence coverage, skill distribution, quality thresholds, and baseline regression checks.
- Fixed in workflow eval expansion pass: bundled workflow scenarios increased from 12 to 20 and now cover API, data, dependency, accessibility, policy, impact, architecture, and UX support flows.
- Fixed in Pulse report pass: `relay-kit pulse build` writes static JSON/HTML quality reports from workflow eval, optional readiness, and evidence ledger signals.
- Fixed in Pulse history pass: Pulse now appends compact history snapshots and reports trend deltas for score, pass rate, evidence coverage, route margin, and status changes.
- Fixed in signal export pass: `relay-kit signal export` writes local JSON/JSONL telemetry-style signals from Pulse and the evidence ledger.
- Fixed in readiness signal gate pass: `relay-kit readiness check` now requires the local signal export gate before returning a commercial-ready candidate.
- Fixed in release-lane verification pass: `relay-kit release verify` checks package metadata, CI gate coverage, commercial docs, manifest/trust/version artifacts, and generated artifact ignore policy; readiness now includes this local gate.
- Fixed in package smoke pass: release-lane CI coverage now requires `python -m pip wheel . --no-deps -w .tmp/wheelhouse`, and local wheel build was verified.
- Fixed in package install smoke pass: `scripts/package_smoke.py` builds a wheel, installs it into a temporary virtualenv, and runs the installed `relay-kit --list-skills` console script.
- Fixed in upgrade CLI pass: `relay-kit upgrade check|plan|mark-current` tracks installed runtime version and prints safe upgrade actions without auto-overwriting files.
- Fixed in enterprise bundle pass: `--bundle enterprise` installs baseline plus the full discipline utility set and emits governance docs for paid/team usage.
- Fixed in Pro policy packs pass: `relay-kit policy check --pack baseline|team|enterprise` and `relay-kit doctor --policy-pack enterprise` enforce stronger governance surfaces for team/paid installs.
- Fixed in support workflow pass: `relay-kit support bundle` creates redacted diagnostic JSON and docs define severity, evidence, support scope, and escalation workflow.
- Fixed in support request intake pass: `relay-kit support request` writes `.relay-kit/support/support-request.json` with severity, environment, diagnostic-file checks, required-field findings, and redaction.
- Fixed in support triage pass: `relay-kit support triage` validates the support request and support bundle artifacts together before paid-support handoff.
- Fixed in support signal summary pass: support bundles include signal export summary/output paths and required diagnostics include `relay-kit signal export`.
- Fixed in support release summary pass: support bundles include release-lane status/findings/residual risks so paid support can inspect release prerequisites from one diagnostic file.
- Fixed in trusted manifest pass: `relay-kit manifest stamp`, `relay-kit manifest verify --trusted`, and enterprise doctor require deterministic trust metadata for enterprise release evidence.
- Fixed in governance reference pass: enterprise policy guard now fails required governance files that still contain unresolved `TBD` or template markers.
- Fixed in contract import pass: `relay-kit contract import` can dry-run or apply Relay contract JSON back into PRD, story, tech-spec, and QA contracts without overwriting concrete sections unless `--force` is used.
- Fixed in readiness gate pass: `relay-kit readiness check` aggregates pytest, doctor, trusted manifest, policy, workflow eval, support bundle, upgrade, contract sync, signal export, and commercial docs into one paid/team verdict.
- Verified in local support-soak pass: `relay-kit support soak . --strict` passes P0/P1/P2 fixtures; `relay-kit readiness check . --profile enterprise` returns `commercial-ready-candidate`; `python -m pytest tests -q` passes with 160 tests.
- Fixed in release publication pass: `v3.3.0` is published with PR #1, CI success, release-lane proof, package smoke, enterprise readiness, post-release readiness, and rollback evidence.
- Fixed in Relay OTLP export pass: `relay-kit signal export --otlp` writes dependency-free OTLP-compatible `relay-signals-otlp.json` with `resourceMetrics` and `resourceLogs` for external observability pipelines.
- Fixed in OTLP readiness/support pass: readiness and support diagnostics now generate and report the OTLP signal artifact, not only JSON and JSONL exports.
- Fixed in CI action hardening pass: `.github/workflows/validate-runtime.yml` now uses Node 24-ready `actions/checkout@v6` and `actions/setup-python@v6`, with a regression test that prevents drifting back to the Node 20 action majors.
- Fixed in publication plan pass: `relay-kit publish plan` now checks package metadata, release-lane status, dist wheel/sdist artifacts, version-channel safety, and external CI/release/package evidence URLs without uploading artifacts.
- Fixed in Pulse publication dashboard pass: `relay-kit pulse build` can include publication-plan data, the HTML report shows publication readiness, and signal export emits `relay.publication.ready`.
- Fixed in publication execution evidence pass: `relay-kit publish evidence` now writes `.relay-kit/release/publication-evidence.json` with wheel/sdist SHA-256 hashes, twine-check output proof, upload/package-index confirmation proof, and external CI/release/package URLs.
- Fixed in publication trail hardening pass: `relay-kit publish trail` now writes JSON/Markdown runbooks with deterministic capture paths and copyable commands for readiness, release verify, build, twine-check capture, plan, upload-log capture, and evidence generation.
- Fixed in next-dev version hygiene pass: `main` now uses PEP 440 package version `3.4.0.dev0` after the published `v3.3.0` tag, with runtime version marker and trusted manifest regenerated for the next-dev channel.
- Fixed in support request Pulse pass: `relay-kit pulse build` can include support-request readiness in JSON/HTML, and signal export emits `relay.support_request.ready`.
- Fixed in support bundle request summary pass: support bundles include a redacted support-request summary when `.relay-kit/support/support-request.json` exists.
- Fixed in workflow eval coverage pass: `relay-kit eval run` now reports layer and role coverage for expected/predicted skills; Pulse and signal export expose expected-layer coverage.
- Fixed in Pulse gate summary pass: Pulse JSON/HTML now reports workflow eval, readiness, publication, support request, and evidence gates with pass/attention/hold/not-run counts; signal export emits `relay.gates.*` metrics.
- Fixed in Pulse gate drilldown pass: each degraded Pulse gate now carries concrete drilldown rows for failed scenarios, readiness gates, publication findings, support diagnostics, or recent failed evidence events; signal export emits `relay.gates.drilldown_items`.
- Fixed in workflow eval scenario expansion pass: bundled workflow scenarios increased from 20 to 28 and now cover bootstrap, debug/fix/review hubs, PM, architect, scrum-master, and runtime-doctor routing.
- Fixed in publication trail status pass: `relay-kit publish status` reads the publication trail and local evidence files, reporting complete, pending, failed, and not-observable publication steps without uploading packages.
- Fixed in readiness pytest output hygiene pass: `relay-kit readiness check` runs pytest with a stable `.tmp/readiness-pytest` base temp directory so Windows temp-cleanup noise does not pollute captured evidence.
- Fixed in pytest temp hardening pass: repo tests and runtime validators now use Relay-kit workspace temp paths and disable pytest cacheprovider, so `python -m pytest -q` passes on Windows without temp-root permission noise.
- Fixed in support operations soak pass: `relay-kit support soak` runs P0/P1/P2 paid-support handoff fixtures, and triage/readiness now fail degraded support bundle diagnostics instead of accepting schema-only bundles.
- Fixed in workflow focus dashboard pass: eval reports weak route candidates and coverage gaps; Pulse renders Workflow focus; signal export emits weak-route and coverage-gap metrics.
- Fixed in commercial dossier pass: `relay-kit commercial dossier` binds local readiness, publication status, support triage/soak, and external CI/release/package/SLA/support owner proof into one strict JSON artifact.
- Fixed in commercial dossier Pulse/signal pass: Pulse can include commercial dossier JSON/HTML status and signal export emits `relay.commercial_dossier.ready`.
- Completed external internal-channel proof pass: GitHub release package assets, public support intake, public SLA, owner statement, and `relay-kit commercial dossier --channel internal --strict` are verified ready.
- Fixed in default enterprise install pass: `relay-kit . --codex` now installs the full enterprise bundle by default, `--baseline` is the explicit smaller path, and the refreshed `v3.4.0.dev0` wheel proves the package URL has this behavior.
- Fixed in Claude reports skill-evolution pass: `skill-evolution` now captures path-scoped skill activation, forked context, allowed-tool profiles, trigger audits, and scenario proof as a Relay-kit-owned discipline utility.
- Fixed in skill permission profile pass: semantic skill gauntlet now strict-fails high-risk skills that lack `allowed-tools` frontmatter or drift from registry tool profiles.
- Fixed in risk-sensitive skill profile expansion pass: API, data, dependency, media, browser, and multimodal support skills now carry machine-checked tool profiles across registry and generated adapters.
- Fixed in support skill semantic fixture pass: bundled workflow scenarios now cover all profiled support skills, including browser, media, and multimodal evidence routing, not only API/data/dependency.
- Fixed in support route noise review pass: `relay-kit eval run` now reports profiled support-skill coverage, weak profiled support routes, and nearby support-skill competitors within the route-margin threshold.
- Fixed in support evidence-contract check pass: `relay-kit eval run` now strict-fails profiled support scenarios whose prompt or expected terms omit required evidence-contract terms, and Pulse/signal export surface the support evidence gap count.
- Fixed in workflow eval role coverage pass: bundled workflow scenarios increased from 37 to 43, covering all registry roles and adding analyst, brainstorm-hub, scout-hub, team, execution-loop, and testing-patterns routes.
- Fixed in workflow eval utility coverage pass: bundled workflow scenarios increased from 43 to 55, covering all 47 current registry skills and adding doc-pointers, handoff-context, memory-search, mermaid-diagrams, problem-solving, repo-map, research, root-cause-debugging, sequential-thinking, skill-evolution, skill-gauntlet, and test-first-development routes.
- Fixed in Windsurf adapter pass: `relay-kit init <project> --windsurf` now writes enterprise workspace rules under `.windsurf/rules/*.md`, and `--all` includes Windsurf alongside Codex, Claude, and Antigravity surfaces.
- External runtime suites for benchmark projects were not fully executed. Their code/docs/scripts were cloned and inspected directly, but full runtime is not verified.

Current verdict:
- Current readiness: published `v3.3.0` with local commercial-ready candidate evidence; `main` has moved to `3.4.0.dev0` for post-release development.
- Commercial readiness: internal/GitHub release channel is verified by `relay-kit readiness check`, `relay-kit release verify`, `relay-kit support request`, `relay-kit support triage`, `relay-kit support soak`, `relay-kit publish trail`, `relay-kit publish plan`, `relay-kit publish evidence`, `relay-kit publish status`, and `relay-kit commercial dossier --channel internal --strict`. The package happy path is now `pip install relay-kit` after PyPI publication, then `relay-kit . --codex` or `relay-kit . --windsurf` for the full bundle. PyPI publication remains pending on PyPI credentials.
- Working score: 6.2/10.
- Target product position after fixes: agent workflow governance kit for teams using Codex, Claude, Cursor/Roo/OpenCode-style agents, not a full replacement for CrewAI or n8n.

Progress snapshot, updated 2026-05-06:
- Repo-executable repair backlog: 100% for the original P0/P1/P2/P3 audit items, 7-day quick wins, and Skill and Rule Gap Matrix first production slices.
- Commercial hardening roadmap: 100% for repo-owned proof tooling, visibility surfaces, and internal-channel external proof. PyPI publication is the only remaining package-index variant and requires PyPI credentials.
- Overall tracked progress in this file: 100% for repo-owned backlog and GitHub/internal commercial proof. This percentage excludes star/community/popularity and external customer contracts.

## Priority Backlog

### P0 - Restore Real Test Proof

Status:
- Fixed on 2026-04-24.
- Verification: `python -m pytest -q` passes 6 tests; root collection is limited to `tests/`; `python scripts/validate_runtime.py` passes; `python scripts/migration_guard.py . --strict` reports 0 findings.

Problem:
- Root test command does not prove runtime behavior.
- The repository has runtime scripts, but no reliable root test suite proving them.

Original evidence:
- `python -m pytest tests -q` output: `no tests ran`.
- `python -m pytest -q` fails while collecting `templates/skills/multimodal-evidence/scripts/tests/test_document_converter.py`.
- `templates/skills/multimodal-evidence/scripts/document_converter.py:27-32` imports `google.genai` and exits at import time when the optional dependency is missing.
- `.github/workflows/validate-runtime.yml:21-22` only runs `python scripts/validate_runtime.py`.

Fix:
- Add `[tool.pytest.ini_options]` in `pyproject.toml` with `testpaths = ["tests"]`.
- Prevent root pytest from collecting template test folders unless explicitly requested.
- Lazy import `google-genai` inside functions or mark it as an optional extra.
- Add root smoke/regression tests:
  - `tests/test_validate_runtime.py`
  - `tests/test_runtime_doctor.py`
  - `tests/test_migration_guard.py`
  - `tests/test_skill_gauntlet.py`
  - `tests/test_public_cli.py`
- Update `.github/workflows/validate-runtime.yml` to run `python -m pytest tests -q`.

Acceptance criteria:
- `python -m pytest tests -q` runs at least the root smoke tests.
- `python -m pytest -q` no longer crashes on optional template dependencies.
- CI fails if runtime validation, migration guard, runtime doctor, or skill gauntlet regress.

### P1 - Fix Live State Hygiene

Status:
- Fixed on 2026-04-24.
- Verification: `python -m pytest tests/test_live_state_hygiene.py tests/test_contract_placeholder_hygiene.py -q` passes; `python scripts/runtime_doctor.py . --strict --state-mode live` reports 0 findings.
- Strengthened on 2026-04-25: nested story contracts are included in live placeholder checks, and `.relay-kit/contracts/stories/story-001.md` no longer contains `TBD`.

Problem:
- Live state artifacts contain placeholders, so context continuity can look available while carrying empty state.

Evidence:
- `runtime_doctor --state-mode live` reports 4 findings:
  - `.relay-kit/state/workflow-state.md`
  - `.relay-kit/state/team-board.md`
  - `.relay-kit/state/lane-registry.md`
  - `.relay-kit/state/handoff-log.md`
- Examples: `.relay-kit/state/workflow-state.md:4,8-14,51-60`, `.relay-kit/state/team-board.md:4,12-14,25-34`, `.relay-kit/state/lane-registry.md:11-18`, `.relay-kit/state/handoff-log.md:6-7`.

Fix:
- Separate template state from live state.
- Add a deterministic bootstrap command such as `relay-kit bootstrap --live`.
- Add a clean fixture for live-mode runtime doctor in tests.
- Extend `runtime_doctor` to check `.relay-kit/contracts/*.md` for unresolved placeholders, not only state files.

Acceptance criteria:
- `python scripts/runtime_doctor.py . --strict --state-mode live` passes after bootstrap.
- A test fixture proves placeholder detection still catches regressions.

### P1 - Complete ai-kit -> relay-kit Cutover

Status:
- Fixed on 2026-04-24.
- Verification: `python -m pytest tests/test_namespace_cutover.py -q` passes; `python scripts/migration_guard.py . --strict` reports 0 findings.

Problem:
- The repo still exposes legacy `ai_kit_v3` namespace in runtime/package surfaces.

Evidence:
- `pyproject.toml:28` includes `ai_kit_v3*`.
- `scripts/validate_runtime.py:18-20` imports from `ai_kit_v3`.
- `scripts/migration_guard.py:16-21` blocks the old dot-ai-kit artifact token but does not block `ai_kit_v3`.

Fix:
- Move internal package imports to `relay_kit_v3` or `relay_kit`.
- Keep a compatibility shim for one release cycle if needed.
- Add `ai_kit_v3`, `ai-kit`, and stale public entrypoint names to migration guard blocked tokens.
- Narrow the migration allowlist to explicit generated or historical docs only.

Acceptance criteria:
- `python scripts/migration_guard.py . --strict` fails on new `ai_kit_v3` references.
- Public docs and CLI help use Relay-kit naming by default.
- Legacy references are documented as compatibility-only.

### P1 - Add Semantic Skill Gauntlet

Status:
- Fixed on 2026-04-24.
- Verification: `python scripts/skill_gauntlet.py . --strict --semantic` reports 0 findings and 12 scenario fixtures; `python -m pytest tests/test_skill_gauntlet_semantic.py -q` passes.
- Done: route prompt scenario fixtures cover the 12 critical workflows.

Problem:
- Current `skill_gauntlet` mostly checks structure, so it can pass while routing and handoff behavior drift.

Evidence:
- Local output: `Checked 141 runtime skill/rule files. Findings: 0`.
- Existing checks focus on headers/placeholders and registry membership.
- Optional aliases and scenario routing are not behavior-tested.
- GitOpen comparison: Superpowers has transcript/behavior skill tests and explicit trigger suites; Relay-kit does not have equivalent scenario proof.

Fix:
- Extend `scripts/skill_gauntlet.py` with a semantic mode:
  - duplicate trigger detection
  - canonical skill to alias parity
  - next-skill references exist
  - required handoff fields exist
  - evidence contract exists for completion skills
  - route prompt -> expected skill/hub/evidence fixture
- Add fixture files under `tests/fixtures/skill_gauntlet/`.

Acceptance criteria:
- `python scripts/skill_gauntlet.py . --strict --semantic` runs in CI.
- At least 10 critical workflows have scenario fixtures:
  - workflow-router
  - cook
  - plan-hub
  - developer
  - test-hub
  - qa-governor
  - release-readiness
  - migration-guard
  - context-continuity
  - evidence-before-completion

### P1 - Add SRS-first Opt-in Gate

Status:
- Fixed on 2026-04-24.
- Verification: `python scripts/srs_guard.py . --strict` skips cleanly when policy is off; `python -m pytest tests/test_srs_guard.py -q` covers off, hard-fail, traceable-pass, and CLI policy update paths.

Problem:
- SRS-first policy should help non-technical/product-heavy lanes without forcing quick-flow work through extra documents.

Fix:
- Add `.relay-kit/state/srs-policy.json` with `enabled=false` and `gate=off` by default.
- Add `.relay-kit/contracts/srs-spec.md` without unresolved placeholders.
- Add `relay_kit_v3/srs_policy.py` and `scripts/srs_guard.py`.
- Add CLI policy flags:
  - `--enable-srs-first`
  - `--disable-srs-first`
  - `--srs-gate off|warn|hard`
  - `--srs-scope product-enterprise|all`
  - `--srs-risk normal|high`
- Wire SRS guard into `relay-kit doctor` and CI.

Acceptance criteria:
- Default doctor pass does not block when SRS policy is off.
- `gate=hard` fails missing SRS/traceability.
- Traceable SRS -> PRD -> story -> QA evidence passes.

### P1 - Resolve Developer/Test-first Contract Mismatch

Status:
- Fixed on 2026-04-24.
- Verification: `python -m pytest tests/test_developer_skill_contract.py -q` passes; generated `.claude`, `.agent`, and `.codex` developer skills use the same conditional contract.

Problem:
- The developer skill requires test-first behavior, but the baseline validation excludes `test-first-development`.

Evidence:
- `.codex/skills/developer/SKILL.md:12,45-46` says to default to `test-first-development`.
- `scripts/validate_runtime.py:297,312` excludes `test-first-development` from baseline.

Fix options:
- Option A: Make developer skill conditional: "Use test-first-development when installed or selected; otherwise name the fallback evidence path."
- Option B: Include `test-first-development` in the baseline with a clear policy.

Recommendation:
- Do Option A first. It is lower risk and avoids expanding baseline before semantic gauntlet exists.

Acceptance criteria:
- Developer skill no longer references a mandatory skill that baseline intentionally excludes.
- Runtime validation and skill gauntlet both pass.

### P1 - Add Runtime Policy Guard

Status:
- Fixed on 2026-04-24.
- Verification: `python scripts/policy_guard.py . --strict` reports 0 findings; `python -m pytest tests/test_policy_guard.py -q` covers secret, path traversal, destructive shell, prompt-injection, and broad allowlist fixtures.

Problem:
- Relay-kit has discipline docs but lacks an enforceable policy guard for high-risk agent operations.

Benchmark evidence:
- DeerFlow has fail-closed guardrail middleware, sandbox controls, and loop detection.
- Get Shit Done has prompt injection/path traversal/security scanners.
- Roo-style systems have explicit tool groups and auto-approval deny/ask logic.

Fix:
- Add `scripts/policy_guard.py`.
- Start with deterministic checks:
  - path traversal
  - broad recursive delete/move patterns
  - secret/token leakage markers
  - prompt-injection phrasing in skill/rule files
  - shell command risk patterns
  - unsafe broad migration allowlists
- Add a `policy-guard` skill only after the script exists.

Acceptance criteria:
- `python scripts/policy_guard.py . --strict` runs in CI.
- Failing examples exist under `tests/fixtures/policy_guard/`.
- `relay-kit doctor` includes policy guard status.

### P2 - Make Release and Accessibility Gates Strict by Default

Status:
- Fixed on 2026-04-24.
- Verification: `python -m pytest tests/test_strict_evidence_gates.py -q` covers missing-evidence strict failures plus pass/fail fixtures for both gates.

Problem:
- Release/a11y checks can look pass-like when no evidence file is supplied.

Evidence:
- Prior audit found `release_readiness.py --json` can return empty results without real signals.
- A11y review can produce null/no-report style output if no report is provided.
- Docs say signals are required, but scripts should enforce that in strict mode.

Fix:
- Change release readiness and accessibility review scripts so strict mode fails when required evidence files are missing.
- Update docs to show only strict commands for release flows.
- Add sample signal/report fixtures.

Acceptance criteria:
- Missing `--signals-file` or `--report-file` fails in strict mode.
- CI includes strict fixture tests for pass and fail cases.

### P2 - Expand CI Beyond Runtime Validation

Status:
- Fixed on 2026-04-24.
- Verification: `.github/workflows/validate-runtime.yml` runs pytest, runtime doctor template/live, migration guard, policy guard, SRS guard, and semantic skill gauntlet.

Problem:
- CI is too narrow to catch the known drift classes.

Evidence:
- `.github/workflows/validate-runtime.yml:21-22` runs only `python scripts/validate_runtime.py`.
- GitOpen leaders generally run test matrices, lint, packaging checks, docker checks, or integration/e2e tests.

Fix:
- CI should run:
  - `python -m pytest tests -q`
  - `python scripts/validate_runtime.py .relay-kit --strict`
  - `python scripts/runtime_doctor.py . --strict`
  - `python scripts/runtime_doctor.py . --strict --state-mode live` against a clean fixture or bootstrapped state
  - `python scripts/migration_guard.py . --strict`
  - `python scripts/skill_gauntlet.py . --strict`
  - semantic gauntlet once implemented
  - policy guard once implemented

Acceptance criteria:
- A single PR gate catches tests, state placeholders, migration drift, structural skill drift, semantic skill drift, and policy violations.

### P2 - Improve 5-minute Onboarding

Status:
- Fixed on 2026-04-24.
- Done: `relay-kit doctor <project>` exists and README shows it in the install path.
- Done: default `--list-skills` hides preserved legacy kits.
- Done: `relay-kit init <project> --codex` is supported as the first-run full governance happy path.
- Done: `--baseline` remains available for a smaller first-install surface.
- Verification: `python -m pytest tests/test_public_cli_doctor.py -q` covers the `init` alias and doctor command mapping.

Problem:
- New users can get confused by old and new entrypoints, bundle names, and exposed legacy kits.

Evidence:
- README quick start has both direct `python relay_kit.py` and public CLI flows.
- `--list-skills` exposes legacy or migration-only surfaces too prominently.
- Benchmark contrast: BMAD, GSD, spec-kit, and n8n-mcp present a clearer first command and doctor/check path.

Fix:
- Add one preferred happy path:
  - `relay-kit init --codex`
  - `relay-kit doctor`
  - `relay-kit route "..."` or equivalent first value command
- Hide legacy kits from default `--list-skills`; show them only with `--legacy`.
- Add `relay-kit doctor` to `relay_kit_public_cli.py` or a new module-backed CLI.
- README should start with one flow only; advanced/legacy flows move below.

Acceptance criteria:
- A fresh user can install, generate adapter files, and run doctor in under 5 minutes.
- Default CLI output contains no legacy migration-only noise.

### P2 - Add Evidence Ledger and Quality Signals

Status:
- Fixed on 2026-04-24.
- Done: `relay-kit doctor` writes JSONL gate events to `.relay-kit/evidence/events.jsonl`.
- Done: `relay-kit doctor --json` and `relay-kit evidence summary <project>` are available.
- Done: `relay-kit doctor` also records the `workflow eval` gate.
- Verification: `python -m pytest tests/test_evidence_ledger.py tests/test_public_cli_doctor.py -q` passes.

Problem:
- Relay-kit does not yet produce durable telemetry or quality signals that prove paid value.

Benchmark evidence:
- claude-mem has persistent memory/context retrieval and token economics.
- KaibanJS exposes workflow logs, cost/duration metadata, and OpenTelemetry integration.
- n8n-mcp documents validation coverage and testable workflow validation.

Fix:
- Add `.relay-kit/evidence/events.jsonl`.
- Record:
  - run id
  - timestamp
  - command/gate
  - selected skill/hub
  - adapter
  - status
  - findings count
  - evidence files
  - elapsed time
- Add summary command:
  - `relay-kit evidence summary`
  - `relay-kit doctor --json`

Acceptance criteria:
- Every doctor/gate run writes a structured event.
- A summary command can show recent failures and drift by gate.

### P2 - Add Workflow Scenario Eval Harness

Status:
- Fixed on 2026-04-24 for the first measurable routing suite.
- Done: `relay-kit eval run <project> --strict` reports pass rate, top routes, predicted skill, and per-scenario findings.
- Done: default fixtures are bundled under `relay_kit_v3/eval_fixtures/workflow_scenarios.json`, so installed CLI runs do not depend on repo test files.
- Done: default fixture coverage expanded to 55 scenarios, including production support lanes for API integration, data persistence, dependency management, browser inspection, media tooling, multimodal evidence, accessibility, policy, impact, project architecture, UX structure, bootstrap, debug/fix/review hubs, analyst, brainstorm-hub, scout-hub, team, execution-loop, testing-patterns, PM, architect, scrum-master, runtime-doctor, and all remaining utility-provider routes.
- Done: profiled support evidence-contract coverage now includes at least two realistic fixtures per profiled support skill.
- Done: `relay-kit doctor` and CI run `scripts/eval_workflows.py . --strict`.
- Verification: `python scripts/eval_workflows.py . --strict --json` reports 55/55 scenarios, no missing roles, and no missing registry skills; `python -m pytest tests/test_workflow_eval.py -q` passes in CI-compatible temp environments.

Problem:
- Semantic gauntlet proved static contract drift, but commercial quality needs a reportable scenario pass-rate signal.

Fix:
- Add `scripts/eval_workflows.py`.
- Add bundled workflow scenario fixtures.
- Add `relay-kit eval run`.
- Include workflow eval in doctor and CI.

Acceptance criteria:
- Scenario reports are machine-readable JSON.
- A bad route returns non-zero in strict mode.
- The report includes enough detail to see why a scenario failed without rerunning the scorer manually.

### P2 - Add Versioned Upgrade CLI

Status:
- Fixed on 2026-04-24 for the first conservative upgrade path.
- Done: `relay-kit upgrade mark-current <project>` writes `.relay-kit/version.json` with package version, bundle, adapters, and manifest hash/status.
- Done: `relay-kit upgrade check <project> --strict` fails when a project is untracked, behind current package version, has an invalid marker, or lacks a valid bundle manifest.
- Done: `relay-kit upgrade plan <project>` prints concrete actions instead of overwriting runtime files automatically.
- Verification: `python -m pytest tests/test_upgrade_cli.py -q` passes.

Problem:
- Commercial/enterprise users need a deterministic way to know what runtime version is installed and what upgrade actions are required.

Fix:
- Add `relay_kit_v3/upgrade.py`.
- Add public CLI commands:
  - `relay-kit upgrade check`
  - `relay-kit upgrade plan`
  - `relay-kit upgrade mark-current`
- Keep apply/regenerate behavior manual until overwrite policy and rollback handling are stronger.

Acceptance criteria:
- Installed projects can record the Relay-kit package version and bundle manifest hash.
- Strict check returns non-zero when upgrade action is required.
- Plan output is copyable and does not mutate project files.

### P2 - Add Enterprise Bundle Story

Status:
- Fixed on 2026-04-24 for the first enterprise packaging slice.
- Done: `relay-kit init <project> --codex` now installs the default enterprise bundle, including `test-first-development`, without requiring `--bundle enterprise`.
- Done: enterprise generation emits baseline contracts, all support references, round4 docs, discipline docs, and `.relay-kit/docs/enterprise-bundle.md`.
- Done: bundle manifest includes `enterprise` and verifies hashes.
- Verification: `python -m pytest tests/test_enterprise_bundle.py -q` passes.

Problem:
- Paid/team users need full governance by default, while baseline remains an explicit lightweight option.

Fix:
- Add `enterprise` to `BUNDLES`.
- Add enterprise bundle contract/doc/reference gating.
- Document install and operating sequence:
  - `relay-kit init --codex`
  - `relay-kit doctor`
  - `relay-kit manifest write`
  - `relay-kit upgrade mark-current`

Acceptance criteria:
- Enterprise bundle appears in `--list-skills`.
- Enterprise install includes `test-first-development`.
- Enterprise manifest is checksummed and verified by existing manifest logic.

### P2 - Add Pro Policy Packs

Status:
- Fixed on 2026-04-24 for the first deterministic local policy pack slice.
- Strengthened on 2026-04-25: required governance files now fail enterprise policy guard if they contain unresolved placeholder/template markers.
- Done: `baseline`, `team`, and `enterprise` policy packs are defined in `relay_kit_v3/policy_packs.py`.
- Done: `relay-kit policy list` and `relay-kit policy check <project> --pack enterprise --strict` are available.
- Done: `relay-kit doctor <project> --policy-pack enterprise` passes the selected pack to policy guard.
- Verification: `python -m pytest tests/test_policy_packs.py tests/test_policy_guard.py tests/test_public_cli_doctor.py -q` passes.

Problem:
- Paid/team installs need stronger policy gates without making the default 5-minute baseline feel heavy.

Fix:
- Keep `baseline` as the default source/risk scanner.
- Add `team` required state/handoff surfaces.
- Add `enterprise` required security/testing/observability/review governance surfaces.
- Expose pack selection in public CLI and doctor.

Acceptance criteria:
- Existing `policy_guard.py . --strict` behavior remains baseline-compatible.
- Enterprise pack catches missing governance files in fixtures.
- Enterprise pack catches placeholder-only required governance files in fixtures.
- Enterprise pack passes on the checked-in Relay-kit runtime.

### P2 - Add Support Workflow and SLA Docs

Status:
- Fixed on 2026-04-25 for the first commercial support workflow slice.
- Done: `relay-kit support bundle <project> --policy-pack enterprise` writes `.relay-kit/support/support-bundle.json`.
- Done: support bundle includes evidence summary, upgrade report, manifest status, policy findings, workflow eval summary, severity levels, and required commands.
- Done: support diagnostics apply basic redaction for obvious token/private-key patterns.
- Done: `.relay-kit/contracts/support-request.md` gives a support request template.
- Done: `docs/relay-kit-support-sla.md` defines severity, triage targets, required diagnostics, included/excluded scope, and escalation flow.
- Verification: `python -m pytest tests/test_support_bundle.py -q` passes.

Problem:
- Paid users need a support motion, not only runtime gates. Without support severity, required evidence, and diagnostic packaging, commercial readiness remains vague.

Fix:
- Add `relay_kit_v3/support_bundle.py`.
- Add public CLI:
  - `relay-kit support bundle`
- Add checked-in support request contract and support SLA docs.

Acceptance criteria:
- A support bundle can be generated without network access.
- The bundle has a stable schema and does not include obvious secret token strings.
- Support request docs name exact commands and evidence files.

### P2 - Add Trusted Manifest Verification

Status:
- Fixed on 2026-04-25 for the first non-cryptographic trust metadata slice.
- Done: `relay-kit manifest stamp <project> --issuer <issuer> --channel <channel>` writes `.relay-kit/manifest/trust.json`.
- Done: `relay-kit manifest verify <project> --trusted` requires valid manifest checksum plus trust metadata.
- Done: `relay-kit doctor <project> --policy-pack enterprise` includes the trusted manifest gate.
- Done: trusted verification fails when a skill hash is tampered, manifest hash is stale, or trust metadata is missing.
- Verification: `python -m pytest tests/test_bundle_manifest.py -q` passes.

Problem:
- Enterprise users need a stricter release evidence path than a standalone checksum manifest.

Fix:
- Add deterministic trust metadata with issuer, channel, package metadata, manifest hash, and trust hash.
- Keep normal `manifest verify` behavior unchanged.
- Clearly document that this is not cryptographic signing.

Acceptance criteria:
- Normal manifest verify still works without trust metadata.
- Trusted verify fails closed without trust metadata.
- Trusted verify catches manifest/trust drift.
- Enterprise doctor fails closed when trust metadata is missing.

### P2 - Add Contract Export and Import

Status:
- Fixed on 2026-04-24 for export.
- Done: `relay-kit contract export <project>` writes a machine-readable JSON contract with source artifact hashes, requirements, acceptance criteria, verification steps, evidence, files, risks, missing fields, and `verification_ready`.
- Fixed on 2026-04-25 for import/sync back.
- Done: `relay-kit contract import <project> --contract-file <relay-contract.json>` previews contract updates; `--apply` writes them; `--force` is required to overwrite concrete existing sections.
- Verification: `python -m pytest tests/test_contract_export.py tests/test_contract_import.py -q` passes; a smoke export for this repo reports `verification_ready=false` when template placeholders lack real acceptance/evidence.

Problem:
- Relay-kit contracts were readable by humans but not exportable/importable as a machine-validated planning/evidence artifact.

Fix:
- Add a JSON export path for Relay planning and QA artifacts.
- Add a conservative import path from Relay JSON back into PRD, story, tech-spec, and QA report sections.
- Treat template instructions and placeholders as missing evidence rather than valid acceptance criteria.

Acceptance criteria:
- Export includes source artifact hashes and machine-checkable missing fields.
- Export does not mark placeholder contracts as ready.
- Import defaults to dry-run and preserves concrete existing sections unless `--force` is used.

### P2 - Narrow Migration Guard Allowlist

Status:
- Fixed on 2026-04-24.
- Done: `migration_guard.py` rejects wildcard paths, token wildcard rules, and allowlist entries missing owner/date/reason metadata.
- Done: `scripts/migration_guard_allowlist.txt` now uses exact `path|token|owner|date|reason` entries.
- Verification: `python scripts/migration_guard.py . --strict`, `python scripts/policy_guard.py . --strict`, and `python -m pytest tests/test_namespace_cutover.py tests/test_policy_guard.py -q` pass.

Problem:
- Broad allowlist patterns reduce confidence in cutover enforcement.

Evidence:
- `scripts/migration_guard_allowlist.txt` contains broad patterns.
- `CONTRIBUTING.md:80-85` discourages broad allowlists.

Fix:
- Replace broad patterns with exact files and exact rationale.
- Add test fixture proving broad allowlists are rejected.

Acceptance criteria:
- Migration guard fails on newly introduced legacy tokens outside exact allowlisted locations.
- Allowlist entries include owner/date/reason if the format supports it.

### P3 - Fix README Encoding

Status:
- Fixed on 2026-04-24.
- Verification: `python -m pytest tests/test_readme_encoding.py -q` passes.

Problem:
- README first line shows mojibake and hurts first impression.

Evidence:
- `README.md:1` displays broken Vietnamese text while `README.vi.md:1` is correct.

Fix:
- Normalize README files to UTF-8.
- Add a lightweight encoding or markdown lint check.

Acceptance criteria:
- README renders correctly in GitHub and local editor.
- CI catches encoding regressions if feasible.

### P3 - Reduce Thin Utility Routing Noise

Status:
- Fixed on 2026-04-24 for the thin-utility contract gap.
- Done: `problem-solving`, `sequential-thinking`, `browser-inspector`, and `multimodal-evidence` now have explicit boundary and evidence contract sections in the registry and generated runtime skills.
- Fixed on 2026-04-25 for completion proof overlap: `qa-governor` owns readiness verdicts and `qa-report.md`; `evidence-before-completion` owns narrow claim-to-evidence proof output; `prove-it` remains a public alias for `evidence-before-completion`.
- Verification: `python scripts/skill_gauntlet.py . --strict --semantic` reports 0 findings; `python -m pytest tests/test_completion_contracts.py tests/test_utility_contracts.py tests/test_skill_gauntlet_semantic.py -q` passes.

Problem:
- Some generic utility skills are thin and can create routing noise.

Evidence:
- Prior audit flagged short/generic utility bodies such as `problem-solving`, `browser-inspector`, and `multimodal-evidence`.
- The issue is not that short skills are always bad; the issue is missing evidence contracts or scripts for utility behavior.

Fix:
- Merge overlapping proof/completion utilities where appropriate:
  - `prove-it`
  - `evidence-before-completion`
  - `qa-governor`
- Add explicit scripts/evidence contracts to utilities that remain.
- Clarify trigger boundaries for `problem-solving` vs `sequential-thinking`.

Acceptance criteria:
- Semantic gauntlet catches duplicate/ambiguous triggers.
- Each remaining utility has a clear input/output/evidence contract.

## Skill and Rule Gap Matrix

| Gap | Action | Priority | Concrete work |
| --- | --- | --- | --- |
| Behavior skill tests | Done | P1 | `scripts/skill_gauntlet.py --semantic` plus bundled routing/evidence scenarios. |
| Runtime policy guard | Done | P1 | `scripts/policy_guard.py` with deterministic secret, path, shell, prompt, and allowlist checks. |
| Evidence ledger | Done | P2 | `.relay-kit/evidence/events.jsonl` plus `relay-kit evidence summary`. |
| Support request intake | Done | P2 | `relay-kit support request` validates required support fields and diagnostic artifacts before paid-support handoff. |
| Support triage readiness | Done | P2 | `relay-kit support triage` reads the request and bundle artifacts together before paid-support handoff. |
| Contract export/import | Add | P2 | Done: `relay-kit contract export` exports Relay contracts to JSON; `relay-kit contract import` previews/applies JSON back into Relay contracts with overwrite protection. |
| Completion proof overlap | Merge or clarify | P3 | Done: `prove-it` delegates to `evidence-before-completion`; `qa-governor` owns readiness verdicts and `qa-report.md` |
| Legacy kit exposure | Done | P2 | `--list-skills` excludes migration-only/legacy unless `--show-legacy` is used. |
| Thin domain utilities | Done | P3 | Utility skills have explicit boundary and evidence contract sections; completion-proof ownership is clarified. |
| Publication planning | Done | P2 | `relay-kit publish plan` checks release-lane status, version/channel safety, dist artifacts, and external evidence URLs without uploading artifacts. |
| Publication trail hardening | Done | P2 | `relay-kit publish trail` writes copyable shell commands and deterministic evidence paths so publish evidence is captured consistently. |
| Publication execution evidence | Done | P2 | `relay-kit publish evidence` records dist artifact hashes, twine-check output, upload confirmation, and package-index URLs into a machine-readable evidence file. |
| Publication trail status | Done | P2 | `relay-kit publish status` reads the trail and evidence files to show complete, pending, failed, and not-observable publication steps without uploading artifacts. |
| Support operations dashboard signal | Done | P2 | Pulse shows support-request readiness and `relay-kit signal export` emits `relay.support_request.ready`. |
| Support bundle request summary | Done | P2 | `relay-kit support bundle` includes a redacted `diagnostics.support_request` summary when the intake artifact exists. |
| Support operations soak | Done | P2 | `relay-kit support soak`, support triage, and readiness run P0/P1/P2 paid-support handoff and degraded bundle diagnostic checks. |
| Workflow eval layer coverage | Done | P2 | Eval reports layer/role coverage, Pulse shows layer coverage, and signal export emits `relay.workflow.expected_layer_count`. |
| Pulse gate summary | Done | P2 | Pulse JSON/HTML shows workflow eval, readiness, publication, support request, and evidence gate status; signal export emits `relay.gates.*` counts. |
| Pulse gate drilldowns | Done | P2 | Degraded Pulse gates now expose concrete scenario, finding, diagnostic, and evidence-event rows; signal export emits `relay.gates.drilldown_items`. |
| Workflow eval scenario expansion | Done | P2 | Default eval suite now covers 55 production/team scenarios, including all registry roles, all 47 current registry skills, and profiled support evidence routing. |
| Workflow focus dashboard | Done | P2 | Eval reports weak routes and coverage gaps; Pulse renders Workflow focus; signal export emits `relay.workflow.weak_route_count` and `relay.workflow.coverage_gap_count`. |
| Support fixture depth review | Done | P2 | Workflow eval strict-fails shallow profiled support fixture suites; Pulse and signal export surface `relay.workflow.support_fixture_depth_gap_count`. |
| Windsurf adapter | Done | P2 | Public CLI and core generator support `--windsurf`, writing one Relay-kit rule file per skill into `.windsurf/rules`. |
| Pytest temp hardening | Done | P2 | `tests/conftest.py`, `relay_kit_v3/temp_paths.py`, readiness/support/validate helpers, and pytest config avoid Windows temp-root/cache permission failures. |
| Commercial proof dossier | Done | P2 | `relay-kit commercial dossier` writes `.relay-kit/commercial/commercial-dossier.json` and strict-fails unless local readiness, publication status, support triage/soak, and external CI/release/package/SLA/support ownership proof are present. |
| Commercial dossier Pulse/signal | Done | P3 | `relay-kit pulse build` accepts commercial dossier artifacts and `relay-kit signal export` emits `relay.commercial_dossier.ready` for support/release dashboards. |

## Benchmark Lessons to Import

Do not copy popularity. Copy the technical mechanics:

- From Superpowers: behavior-level skill tests and transcript verification.
- From spec-kit/OpenSpec: spec/plan/task artifacts with machine-validated fields and explicit verification contracts.
- From DeerFlow: fail-closed guardrails, sandbox restrictions, loop detection, and runtime middleware.
- From get-shit-done: one-command install, strong security scanner, and coverage-gated CI.
- From n8n-mcp: multi-level validation, packaged CLI, Docker/self-host docs, and integration test documentation.
- From claude-mem: persistent context/evidence store and token/cost economics.
- From KaibanJS: workflow state logs, duration/cost/iteration metadata, and OpenTelemetry path.
- From BMAD: guided installer, workflow init, module lifecycle, and clear beginner path.
- From Roo/Cursor rules: explicit scoped rules, modes/tool groups, and auto-approval safety boundaries.
- From CrewAI/n8n: enterprise packaging, observability, support path, and upgrade discipline.

## 7-day Quick Wins

1. Done: fix `README.md:1` encoding.
2. Done: add pytest config so root pytest does not collect `templates/` by default.
3. Done: lazy import or optional-extra guard `google-genai`.
4. Done: add smoke tests for runtime validation, runtime doctor, migration guard, skill gauntlet, and public CLI.
5. Done: update CI to run `python -m pytest tests -q` and the core runtime gates.
6. Done: add migration guard tests for `ai_kit_v3`.
7. Done: clean `.relay-kit/state/*.md` so live doctor can pass.
8. Done: make developer skill test-first instruction conditional.
9. Done: add `relay-kit doctor` as a single support entrypoint.
10. Done: hide legacy kits from default skill listing.

## 30/60/90 Day Roadmap

### 30 Days - Release Proof and Hygiene

- Restore root test suite and CI proof.
- Fix optional dependency import crash.
- Clean live state and add live bootstrap fixture.
- Decide namespace cutover plan and update migration guard.
- Resolve developer/test-first contract mismatch.
- Add `relay-kit doctor`.

Expected gain:
- Relay-kit can claim basic release readiness without relying on prose.

### 60 Days - Runtime Confidence

- Add semantic skill gauntlet.
- Add strict release/a11y evidence gates.
- Add policy guard.
- Add evidence ledger and JSON doctor output.
- Add Relay contract artifact sync for stories and acceptance criteria, informed by the OpenSpec/spec-kit benchmark but named and shaped as Relay-kit.

Expected gain:
- Routing, handoff, completion, and safety claims become executable.

### 90 Days - Commercial Package

- Done first slice: add versioned upgrade/migration CLI.
- Done: add checksummed bundle manifest with `relay-kit manifest write` and `relay-kit manifest verify`.
- Done first slice: add trusted manifest metadata with `relay-kit manifest stamp` and `relay-kit manifest verify --trusted`.
- Done first slice: add Pro policy packs.
- Done first slice: add support workflow and SLA docs.
- Done second support slice: add structured support request intake with required field and diagnostic checks.
- Done first slice: add enterprise bundle story.
- Done first slice: add scenario eval harness for real workflow quality.
- Done second slice: add eval quality metrics, configurable thresholds, and baseline regression comparison.
- Done third eval slice: expand bundled scenario coverage from 12 to 20 production/team workflows.
- Done fourth eval slice: expand bundled scenario coverage from 20 to 28 production/team workflows.
- Done first Pulse slice: add static JSON/HTML report generator for local quality review before dashboard/server work.
- Done second Pulse slice: add local trend/history JSONL so Pulse can compare current quality against prior runs.
- Done first signal export slice: add local JSON/JSONL telemetry-style export from Pulse and evidence ledger signals.
- Done second signal export slice: readiness now verifies signal export as a required commercial gate.
- Done first release-lane slice: add `relay-kit release verify` and include it in readiness/support evidence.
- Done first slice: add `relay-kit readiness check` as the single commercial readiness verdict.
- Done first publication-plan slice: add `relay-kit publish plan` as the no-upload package publication evidence gate.
- Done dashboard/eval expansion slice: Pulse can include publication-plan status in JSON/HTML and export publication readiness as a local signal metric.
- Done first publication-execution slice: add `relay-kit publish evidence` as the post-upload evidence artifact for support and release review.
- Done first publication workflow hardening slice: add `relay-kit publish trail` for deterministic capture commands and evidence paths.
- Done support operations signal slice: Pulse and signal export now surface support-request readiness for paid-support review.
- Done support bundle polish slice: support bundles now summarize existing support request intake artifacts.
- Done support triage polish slice: support request and support bundle artifacts now have one strict handoff gate.
- Done support operations soak slice: `relay-kit support soak` validates P0/P1/P2 paid-support handoff fixtures against the current support bundle.
- Done workflow eval coverage slice: dashboard inputs now include expected/predicted layer and role coverage from registry metadata.
- Done Pulse gate summary slice: dashboard inputs now include per-gate pass, attention, hold, and not-run counts plus next actions.
- Done Pulse gate drilldown slice: dashboard inputs now include concrete degraded gate rows for failed scenarios, readiness gates, publication findings, support diagnostics, and failed evidence events.
- Done workflow eval scenario expansion slice: default scenario fixtures now cover 55 production/team routes, including bootstrap, debug/fix/review hubs, analyst, brainstorm-hub, scout-hub, team, execution-loop, testing-patterns, PM, architect, scrum-master, runtime-doctor, profiled support evidence routes, and all remaining utility-provider routes.
- Done Windsurf adapter slice: package users can run `relay-kit init <project> --windsurf` once per Windsurf workspace to generate `.windsurf/rules/*.md` plus the normal `.relay-kit` contracts/docs.
- Done publication trail status slice: local publish progress is now inspectable with `relay-kit publish status --strict --json` before or after package-index upload.
- Done workflow focus dashboard slice: Pulse now shows low-margin route candidates and coverage gaps from workflow eval, and signal export exposes those counts.
- Done support fixture depth review slice: workflow eval, Pulse, and signal export now surface shallow or duplicate profiled support fixture coverage.
- Done commercial dossier slice: `relay-kit commercial dossier` strict-binds local runtime, publication, support, and external commercial proof into one JSON artifact.
- Done commercial dossier Pulse/signal slice: dashboard and telemetry outputs now surface commercial dossier status, findings, and readiness metric.
- Done external internal-channel proof slice: GitHub release assets, public support intake, public SLA URL, owner statement, publication status, support triage/soak, and commercial dossier strict all pass.
- Done default enterprise install slice: package users can run `relay-kit . --codex` for the full enterprise bundle; `--bundle enterprise` is no longer required in the happy path.

Expected gain:
- Relay-kit becomes sellable as a governance layer with measurable quality signals.

## Definition of Commercial-ready

Relay-kit should not be called commercial-ready until all of these are true:

- Root tests run in CI and cover the runtime gates.
- Live runtime doctor passes on a bootstrapped fixture.
- Migration guard blocks stale `ai-kit` and `ai_kit_v3` drift by default.
- Semantic skill gauntlet covers critical workflows.
- Strict release/a11y gates fail without evidence files.
- `relay-kit doctor` gives one supportable command for users and maintainers.
- Default onboarding reaches first value in under 5 minutes.
- Default package onboarding generates the full enterprise bundle without requiring `--bundle enterprise`; `--baseline` remains available for smaller installs.
- Evidence ledger records gate runs and findings.
- Paid support/upgrade path is documented.
- `relay-kit support request --strict` reaches `ready` only when severity, environment, behavior details, recent changes, workaround, and diagnostic artifacts are present.
- `relay-kit support triage --strict` reaches `ready` only when the support request and support bundle artifacts are locally valid.
- `relay-kit support soak --strict` passes P0/P1/P2 handoff fixtures only when support bundle diagnostics are locally healthy.
- `relay-kit readiness check --profile enterprise` returns `commercial-ready-candidate` for the release candidate.
- `relay-kit readiness check` proves signal export artifacts can be generated locally.
- `relay-kit release verify` passes for local release-lane prerequisites.
- `relay-kit publish plan --channel pypi --strict` reaches `ready` only after release-lane, dist artifacts, version/channel policy, and external CI/release/package evidence are present.
- `relay-kit publish trail --channel pypi --strict` reaches `ready` only after metadata, version/channel policy, release-lane status, shell support, and external CI/release/package URLs are present.
- `relay-kit publish evidence --channel pypi --strict` reaches `published` only after wheel/sdist hashes, twine-check proof, upload confirmation, and external CI/release/package evidence are present.
- `relay-kit publish status --strict` reaches `complete` only after the trail file, dist artifacts, twine-check log, upload log, publication plan, and publication evidence are locally inspectable.
- `relay-kit commercial dossier --strict` reaches `ready` only after local readiness, publication status, support triage/soak, and external CI/release/package/SLA/support ownership evidence are present.
- Pulse and signal export surface support-request readiness so support operations can see whether the intake artifact is actionable.
- Pulse and signal export surface commercial dossier readiness so support/release review can see whether the final commercial proof binder is ready.
- Pulse and signal export surface per-gate pass, attention, hold, and not-run counts so dashboard review can target the exact degraded gate.
- Pulse and signal export surface gate drilldown item counts and rows so a reviewer can inspect the first concrete failure without parsing raw reports.
- Pulse and signal export surface weak route count, eval coverage gap count, support evidence gap count, and support fixture depth gap count so dashboard review can catch route fragility before a scenario fails.
- Workflow eval default suite covers 55 production/team scenarios across orchestration, hubs, utility providers, specialists, runtime diagnostics, all registry roles, all 47 current registry skills, and profiled support evidence routes.

Review-hub verdict for this backlog:
- P0/P1/P2/P3 audit backlog items are implemented as first production-ready slices.
- Internal/GitHub release commercial proof is ready. Continue with PyPI publication only after PyPI credentials are available.
