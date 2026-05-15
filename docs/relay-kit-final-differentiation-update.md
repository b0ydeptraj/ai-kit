# Relay-kit Final Differentiation Update Plan

Status: complete (PR #94-#98 merged; post-phase Relay-kit-only naming hard-cut PR #100 merged; latest main CI green).
Owner flow: `workflow-router -> plan-hub -> developer -> test-hub -> review-hub`.
Last planning pass: 2026-05-12.

This file records the next differentiation phase after the core backlog,
package proof, support proof, Claude-adoption governance, and PyPI/publication
proof work. It is intentionally separate from `relay-kit-upgrade-backlog.md`
so the previous 100% status does not hide this new product-expansion phase.

## Goal

Make Relay-kit feel like a paid, practical AI workflow kit for production teams,
not only a governance/runtime proof kit.

The phase adds four missing first-class surfaces:

- domain productivity skills for dev, marketing, research, and automation
- lifecycle slash-command entrypoints
- explicit Engineer and Marketing agent profiles
- token/context economy that saves tokens without losing signal

## Current Baseline

Relay-kit already has:

- 54 canonical skills generated into `.codex/skills`, `.claude/skills`, and
  `.agent/skills`
- 4-layer topology: orchestrators, workflow hubs, utility providers,
  specialists/standalones
- enterprise gates: runtime doctor, semantic skill gauntlet, workflow eval,
  adapter diagnostics, readiness, Pulse, signal export
- governance commands such as `context audit`, `lane audit`, `adapter diagnose`,
  `query search`, and `service boundaries`
- workflow eval suite with 70 scenarios

Relay-kit delivered in PR 1-PR 4:

- dedicated marketing/growth skill
- dedicated automation operations skill
- first-class Go backend skill
- first-class Next.js/shadcn skill
- profile-based Vietnamese localization skill
- global runtime locale switch (`relay-kit locale set ... --locale <code>`) with readiness/runtime-doctor coverage
- slash-command lifecycle layer
- explicit Engineer and Growth agent profiles
- token-budget/context-pack/token-audit commands

## Competitive Gap Matrix

| Area | Relay-kit now | Benchmark gap | Upgrade target |
|---|---|---|---|
| Vietnamese support | Vietnamese localization skill + global runtime locale switch (default `en`, one-switch override) | User-supplied Claudex benchmark has hard Vietnamese rule | Keep Relay-owned global locale policy with explicit fallback and gates |
| Go backend | Generic developer/API/data skills | User-supplied Claudex benchmark treats Go as first-class | Add `go-service-engineering` |
| Next.js | UI skills mention React/shadcn patterns, but no Next.js specialist | User-supplied Claudex/Claude-kit benchmark compares Next stack depth | Add `next-product-frontend` |
| Marketing | No canonical marketing skill | Product lifecycle is incomplete for launch/growth users | Add `growth-marketing` and campaign evidence contracts |
| Research | Has generic `research` utility | Market/competitor research is not a standalone product skill | Add `market-research` with source-quality scoring |
| Automation | No canonical automation operations skill | Paid users expect workflow/webhook/script automation guidance | Add `automation-ops` |
| Slash commands | Skills can be invoked, but no Relay-owned lifecycle command registry | Claude Code/MakerKit-style kits expose `.claude/commands` or slash workflows | Add command registry and generated adapter surfaces |
| Agent profiles | Adapter skills exist, but no role profiles | MakerKit-style kits expose agents/commands/skills separately | Add `relay-engineer` and `relay-growth` profiles |
| Token economy | Context audit/handoff-context exist, but no token budget optimizer | RTK/Distill/Caveman/Graphify optimize command output/context | Add safe token economy skill and CLI commands |

Competitor evidence status:

- Claudex and Claude kit rows above use the user-supplied comparison table.
  Mark as `Chua xac minh runtime` until the exact repos are cloned and checked.
- RTK, Distill, Caveman, MakerKit, and token-cost study are external public
  references from the planning pass; they are inspiration only, not copied
  naming or prompt text.

## PR 1: Domain Skill Pack

Branch: `codex/domain-skill-pack`

Add Relay-owned domain skills:

- `go-service-engineering`
- `next-product-frontend`
- `growth-marketing`
- `market-research`
- `automation-ops`
- `vietnamese-product-localization`

Primary files:

- `relay_kit_v3/registry/skills.py`
- `relay_kit_v3/registry/topology.py`
- `relay_kit_v3/eval_fixtures/workflow_scenarios.json`
- `tests/test_domain_skill_pack.py`
- `tests/test_skill_gauntlet_semantic.py`
- `tests/test_workflow_eval.py`
- `README.md`

Implementation rules:

- Use Relay-kit-owned names only.
- Do not copy Claudex, Claude kit, RTK, Distill, Caveman, or MakerKit prompts.
- New skills must have clear trigger text, input/output contract, handoff
  contract, and evidence discipline.
- Vietnamese support is profile-based, not global default.
- Add generated `.codex`, `.claude`, and `.agent` copies through the existing
  generator flow.

Acceptance:

- semantic gauntlet routes Go prompts to `go-service-engineering`
- semantic gauntlet routes Next.js/shadcn prompts to `next-product-frontend`
- campaign/SEO/funnel prompts route to `growth-marketing`
- competitor/ICP/pricing prompts route to `market-research`
- scheduler/webhook/script automation prompts route to `automation-ops`
- Vietnamese docs/support/copy prompts route to `vietnamese-product-localization`

## PR 2: Slash Command Lifecycle Layer

Branch: `codex/lifecycle-command-registry`

Add a Relay-owned command registry and generator.

Lifecycle commands:

- `/relay-start`
- `/relay-brief`
- `/relay-plan`
- `/relay-architect`
- `/relay-build`
- `/relay-test`
- `/relay-review`
- `/relay-ship`
- `/relay-support`
- `/relay-research`
- `/relay-grow`
- `/relay-automate`
- `/relay-token-audit`

Primary files:

- new registry module under `relay_kit_v3/`
- `relay_kit_public_cli.py`
- generated `.claude/commands` where supported
- adapter-neutral command docs for Codex and Agent
- `tests/test_slash_command_registry.py`
- `tests/test_adapter_diagnostics.py`

CLI additions:

```bash
relay-kit command list .
relay-kit command diagnose . --adapter all --strict --json
```

Implementation rules:

- Commands are short entrypoints into existing skills/hubs.
- Skills remain the deeper workflow units.
- Adapter diagnostics must flag missing/extra command surfaces.
- Claude command support should not become a dependency for Codex/Agent.

Acceptance:

- command list returns the 13 lifecycle commands
- `.claude/commands` generation is deterministic
- Codex/Agent receive adapter-neutral command documentation
- adapter diagnose reports command parity

## PR 3: Agent Profiles

Branch: `codex/agent-profile-pack`

Add explicit role profiles:

- `relay-engineer`
- `relay-growth`

Primary files:

- new profile registry module under `relay_kit_v3/`
- `relay_kit_public_cli.py`
- `.relay-kit/agents/*.json` generated output
- adapter docs for supported surfaces
- `tests/test_agent_profiles.py`
- `tests/test_readiness_check.py`

CLI additions:

```bash
relay-kit agent list .
relay-kit agent diagnose . --adapter all --strict --json
```

Profile contracts:

- `relay-engineer` routes through workflow-router, scout/plan/fix/test/review,
  developer, qa-governor, and readiness.
- `relay-growth` routes through research, market-research, growth-marketing,
  Vietnamese localization when configured, automation-ops, and evidence ledger.

Implementation rules:

- Agent profiles are role contracts, not claims of autonomous runtime.
- No fake multi-agent execution claim unless there is a real execution surface.
- Readiness must fail if required profile metadata is missing.

Acceptance:

- profile list is deterministic
- profile diagnose passes for generated repo surfaces
- readiness enterprise includes agent-profile gate

## PR 4: Token Economy Pack

Branch: `codex/token-economy-pack`
Status: done (PR #97 merged, main CI green)

Add `token-economy` skill and context-budget commands.

Primary files:

- `relay_kit_v3/registry/skills.py`
- new token economy module under `relay_kit_v3/`
- `relay_kit_public_cli.py`
- `relay_kit_v3/pulse.py`
- `relay_kit_v3/signal_export.py`
- `tests/test_token_economy.py`
- `tests/test_pulse_report.py`
- `tests/test_signal_export.py`

CLI additions:

```bash
relay-kit context budget . --max-tokens 8000 --json
relay-kit context pack . --task "ship release safely" --max-tokens 8000 --json
relay-kit token audit . --json
```

Safety rules:

- Never hide failing command details without a raw-output pointer.
- Classify output as `raw-required`, `compressible`, or `summary-only`.
- Failed tests/builds must preserve raw log path.
- Compression must keep file paths, line numbers, commands, exit codes,
  failing assertions, and remediation hints.
- If signal retention is uncertain, fail open to raw output.

Pulse/signal metrics:

- `relay.context.estimated_tokens`
- `relay.context.compressed_tokens`
- `relay.context.signal_retention`
- `relay.context.raw_required_blocks`
- `relay.token.budget_violations`

Acceptance:

- token audit reports estimated raw/compressed token counts
- context budget reports over-budget sources
- context pack returns a task-scoped source pack with authority/freshness
- failing command fixture keeps raw-output pointer
- Pulse and signal export include the five token economy metrics
- merge evidence: PR #97 https://github.com/b0ydeptraj/Relay-kit/pull/97
- main CI evidence: https://github.com/b0ydeptraj/Relay-kit/actions/runs/25684183141 (success)

## PR 5: Competitive Matrix And State Refresh

Branch: `codex/final-differentiation-state-refresh`
Status: done (PR #98 merged; main CI https://github.com/b0ydeptraj/Relay-kit/actions/runs/25685234847 passed)

Update docs and live state only after PRs 1-4 merge and main CI is green.

Primary files:

- `docs/relay-kit-final-differentiation-update.md`
- `docs/relay-kit-upgrade-backlog.md`
- `docs/relay-kit-claude-12-adoption-matrix.md`
- `.relay-kit/contracts/project-context.md`
- `.relay-kit/state/workflow-state.md`
- `.relay-kit/state/team-board.md`
- `.relay-kit/state/lane-registry.md`
- `.relay-kit/state/handoff-log.md`

Acceptance:

- note says previous core backlog is 100%
- note says this final differentiation phase is complete only after PR 5
- competitor claims are marked with evidence status
- live state points to the latest merged main CI, not stale branches

## Post-Phase: Relay-kit-Only Naming Hard-Cut (v4.0.0)

Branch: `codex/relay-only-naming-hardcut-v4`
Status: done (PR #100 merged; main CI https://github.com/b0ydeptraj/Relay-kit/actions/runs/25729643395 passed)

Scope:

- remove runtime/CLI legacy bundle aliases from active surfaces
- enforce fail-closed naming guard for retired legacy tokens
- keep Relay-kit-only naming contract in runtime/docs/tests for active workflows

Acceptance:

- PR #100 merged into `main`
- merge commit: `a55fed3df8b5bdde307697f0d05a67ec307bb807`
- latest main CI green after merge

## Required Gates Per PR

Run before opening each PR:

```bash
python -m pytest tests -q
python scripts/validate_runtime.py
python scripts/runtime_doctor.py . --strict --state-mode live
python scripts/skill_gauntlet.py . --strict --semantic
python scripts/eval_workflows.py . --strict --json
python relay_kit_public_cli.py adapter diagnose . --adapter all --strict --json
python relay_kit_public_cli.py readiness check . --profile enterprise --json
python relay_kit_public_cli.py pulse build . --json --no-history
python relay_kit_public_cli.py signal export . --otlp --json
git diff --check
```

Remote done criteria:

- PR CI green
- merge to `main`
- final main CI green
- state refresh PR merged for PR 5

## Risks

| Risk | Mitigation |
|---|---|
| Routing noise from six new skills | Add semantic fixtures and route margin checks in the same PR |
| Slash commands duplicate skills | Commands only delegate to skills/hubs; skills remain authoritative |
| Agent profiles overclaim runtime | Document as role profiles and diagnose metadata only |
| Token compression hides evidence | Preserve raw pointer and fail open to raw output |
| Vietnamese profile leaks into global default | Keep locale/profile explicit |
| Generated adapter drift | Run adapter diagnose and semantic gauntlet per PR |

## Seven-Day Quick Wins

1. Add the six domain skill specs and generated skill files.
2. Add six semantic route fixtures for domain skill routing.
3. Add README section for domain skill pack.
4. Add command registry data model without full adapter generation.
5. Add `relay-kit command list`.
6. Add `relay-engineer` and `relay-growth` profile JSON schema.
7. Add `relay-kit agent list`.
8. Add token audit estimator with no compression yet.
9. Add Pulse/signal placeholders for token economy metrics.
10. Update this file with completion checkboxes after each merged PR.

## Final Definition Of Done

Relay-kit final differentiation phase is complete only when:

- all six domain skills exist and pass semantic routing
- lifecycle commands are generated and diagnosable
- Engineer and Growth agent profiles are generated and diagnosable
- token economy commands preserve signal and expose metrics
- workflow eval covers domain, commands, agents, and token economy
- enterprise readiness includes the new gates

## Post-phase Proof Hardening: Shell Compaction, Real-World Eval, Skill Proof

Branch: `codex/real-world-token-proof`

Status: done via PR #103.

Purpose:

- add Relay-owned shell compaction that keeps raw command logs under `.relay-kit/evidence/raw` and only compresses presentation output
- add production-shaped real-world skill cases so every registered skill is not evaluated only by route prompts
- add skill proof audit so every skill is labeled `theoretical`, `validated`, or `field-tested`

Commands:

```bash
relay-kit shell compact . --json -- python -m pytest tests -q
relay-kit eval real-world . --strict --json
relay-kit proof audit . --strict --json
```

Done criteria:

- `relay-kit eval real-world` passes all bundled real-world cases: done, 62/62 with full registered-skill coverage.
- `relay-kit proof audit --strict` reports zero theoretical skills: done, 62 validated / 0 theoretical / 0 field-tested.
- `field-tested` remains zero unless explicit field evidence exists: done; no deployment proof was invented.
- enterprise readiness includes `real-world-skill-eval` and `skill-proof-audit` required gates: done.
- PR #103 merged to `main` at `8e5586df2569d5ef0961b1105306132931ac21dc`.
- Main CI `Validate Runtime` run `25922588929` is green after merge.
