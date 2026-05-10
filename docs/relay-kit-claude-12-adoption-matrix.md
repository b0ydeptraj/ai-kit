# Relay-kit Claude 12 Adoption Matrix

This document translates the local `claude-12-reports-markdown` export into Relay-kit-owned product work.

It is not a Claude compatibility plan and it does not copy Claude skill names, prompts, permission modes, storage internals, or product concepts. The reports are used as source material for Relay-kit's own runtime governance, skill-system quality, DX, safety, observability, and commercial-readiness roadmap.

## Scope Boundary

Source folder:

- local Desktop/OneDrive folder named `claude-12-reports-markdown`

Relay-kit target surfaces:

- `relay_kit_v3/registry/skills.py`
- `scripts/skill_gauntlet.py`
- `scripts/eval_workflows.py`
- `scripts/policy_guard.py`
- `relay_kit_v3/pulse.py`
- `relay_kit_v3/signal_export.py`
- `.relay-kit/state/*.md`
- `.relay-kit/contracts/*.md`
- `docs/relay-kit-*.md`
- `tests/test_*`

Rules:

- Use Relay-kit names and contracts.
- Keep raw Claude reports unchanged.
- Treat every adoption as a Relay-kit capability with tests, gates, and docs.
- Mark unimplemented ideas as backlog, not as completed runtime behavior.

## Current Adoption Status

Already implemented:

- `skill-evolution` as a Relay-kit-owned discipline utility.
- Path-scoped skill activation metadata for skill evolution work.
- Forked-context stance for review-heavy skill changes.
- Machine-checked `allowed-tools` frontmatter for profiled risk-sensitive skills.
- Semantic skill gauntlet checks for profile drift and skill routing scenarios.
- Risk-sensitive support skill profiles for API, data, dependency, media, browser, and multimodal evidence utilities.
- Bundled workflow scenarios covering all profiled support skills, including browser, media, and multimodal evidence routes.
- Workflow eval support-route review for duplicate/noisy nearby support-skill triggers.
- Context governance first slice with `relay-kit context audit`, source freshness/confidence metadata, continuity manifest source metadata, and guarded stale-main-pointer detection.
- Multi-lane coordination first slice with `relay-kit lane audit`, lock-conflict checks, wave/dependency metadata, parked-lane resume conditions, and runtime-doctor live integration.
- Adapter/IDE bridge diagnostics first slice with `relay-kit adapter diagnose`, generated skill parity checks, metadata drift checks, and explicit advisory metadata reporting for Agent/Antigravity.
- Query/service boundary first slice with `relay-kit query search`, ranked source lookup, and `relay-kit service boundaries` static dependency checks.

Latest verified implementation evidence:

- PR #47: `skill-evolution` utility.
- PR #49: high-risk skill profile gate.
- PR #51: risk-sensitive support skill profile expansion.
- PR #52: state/context refresh after PR #51.
- PR #83: context and memory governance first slice.
- PR #84: runtime-doctor shallow ancestry guard for context governance.
- PR #86: multi-lane coordination hardening with `relay-kit lane audit`.
- Local context-governance slice evidence: `python -m pytest tests -q` passed 200 tests.
- Local context-governance slice evidence: `python relay_kit_public_cli.py context audit . --strict --json` returned `status: pass`.
- Local context-governance slice evidence: enterprise readiness returned `commercial-ready-candidate`.
- Local lane-coordination slice evidence: `python -m pytest tests -q` passed 209 tests, live lane audit returned `status: pass`, and main CI `25620406371` passed.
- Local adapter-diagnostics slice evidence: `python relay_kit_public_cli.py adapter diagnose . --adapter all --strict --json` returned `status: pass`; enterprise readiness included required `adapter-diagnostics` gate with 0 findings.

## 12-Report Relay-kit Translation Matrix

| Report | Relay-kit capability to extract | Status | Priority | Target implementation |
|---|---|---:|---:|---|
| 01 Lessons Learned | Skill operating rules: context budget discipline, worktree/lane hygiene, evidence before claims, avoid context pollution. | Partially implemented | P1 | Strengthen `skill-evolution`, `workflow-router`, `team`, and state-refresh rules. |
| 02 Bridge / IDE Integration | Adapter-neutral editor bridge guidance for Codex, Claude, Cursor/Roo/OpenCode-style tools without binding to one IDE. | Implemented first slice | P2 | `relay-kit adapter diagnose` checks generated skill parity, extra skills, metadata drift, and adapter metadata stance. |
| 03 Context Building | Better context packing, relevance scoring, and handoff minimization for long Relay-kit lanes. | Implemented first slice | P1 | `relay-kit context audit` and continuity source metadata now classify authority/freshness; remaining work is Pulse/signal visibility. |
| 04 Memory System | Memory lifecycle rules: source ranking, stale memory labels, conflict handling, and state-vs-memory boundaries. | Implemented first slice | P1 | `memory-search` now returns source type, age, confidence, and stale warning; remaining work is dashboard surfacing. |
| 05 Multi-agent Coordinator | Lane ownership, parallel work locks, merge order, collision prevention, and handoff return conditions. | Implemented first slice | P2 | `relay-kit lane audit` checks lock conflicts, broad lock scopes, parked-lane resume conditions, waves/dependencies, and handoff return conditions. |
| 06 QueryEngine | Search/query ranking over docs, state, registry, scenarios, and evidence without relying on broad text dumps. | Implemented first slice | P2 | `relay-kit query search` ranks state, contracts, docs, evidence, and registry hits with authority/freshness metadata. |
| 07 Service Layer | Clearer runtime service boundaries for CLI, registry, gates, support, release, telemetry, and publication modules. | Implemented first slice | P2 | `relay-kit service boundaries` reports the boundary map and static import findings. |
| 08 Session Storage | Resume, session snapshot, handoff ledger, and state persistence contracts. | Partially implemented | P1 | Upgrade `context-continuity`, evidence ledger, and live-state schemas. |
| 09 Skills & Plugin System | Trigger metadata, paths, context mode, allowed tools, dynamic discovery concepts, and skill evolution rules. | Implemented first slice | P0 | Done via `skill-evolution`, generated frontmatter, and semantic gauntlet. |
| 10 Multi-agent Coordinator duplicate | Duplicate of report 05; use only to confirm coordinator patterns, not as independent evidence. | Deduped | P3 | Keep excluded from scoring to avoid double-counting. |
| 11 Tool System | Tool registry, tool risk classification, invocation contracts, and safer tool profiles. | Partially implemented | P1 | Expand `policy_guard`, `skill_gauntlet`, and support-skill semantic fixtures. |
| 12 Permission System | Deny-by-default safety thinking, dangerous command stripping, permission scope, and explicit tool stance. | Implemented first slice | P0 | Done via `allowed-tools` profiles, policy packs, and enterprise doctor gates. |

## Relay-kit-Specific Work Packages

### Package A: Skill-System Runtime Quality

Goal: Make skill behavior provable, not prose-only.

Already done:

- `skill-evolution`
- semantic route to `skill-evolution`
- generated `allowed-tools`
- risk-sensitive support profiles
- support-route noise review in workflow eval
- support evidence-contract checks

Next:

- Done: add semantic fixtures proving API/data/dependency/media/browser/multimodal prompts route to the right skill.
- Done: add duplicate/noisy-trigger detection across nearby support skills.
- Done: add evidence-contract checks for these fixtures, not only predicted-skill checks.

Candidate files:

- `tests/fixtures/skill_gauntlet/scenarios.json`
- `tests/test_skill_gauntlet_semantic.py`
- `scripts/skill_gauntlet.py`
- `relay_kit_v3/registry/skills.py`

### Package B: Context And Memory Governance

Goal: Make long Relay-kit sessions resume with clean, ranked, non-stale context.

Adopt from reports 03, 04, and 08:

- context pack should say what is authoritative, stale, inferred, or missing
- memory search should label source age and confidence
- handoff state should distinguish live state from reusable memory
- runtime doctor should catch stale source-of-truth pointers after merge

Implemented first slice:

- `relay-kit context audit <project> --strict --json`
- context source classification: `authoritative`, `recent`, `stale`, `inferred`, `missing`
- `memory-search` source type, age, confidence, and stale warning
- continuity checkpoint source metadata in `context-manifest.json`
- guarded runtime-doctor stale-main-pointer helper

Candidate files:

- `.relay-kit/state/workflow-state.md`
- `.relay-kit/state/handoff-log.md`
- `.relay-kit/contracts/project-context.md`
- `.codex/skills/context-continuity/SKILL.md`
- `.codex/skills/memory-search/SKILL.md`
- `scripts/runtime_doctor.py`

### Package C: Multi-Lane Coordination

Goal: Make team/parallel execution safer when multiple agents or branches are active.

Adopt from reports 01, 05, and 10:

- lane locks must name artifact scope, not whole repo
- merge order must be explicit
- parked lanes must have clear resume conditions
- handoffs must include expected return condition
- duplicate coordinator source should be deduped in analysis

Candidate files:

- `.relay-kit/state/team-board.md`
- `.relay-kit/state/lane-registry.md`
- `.codex/skills/team/SKILL.md`
- `.relay-kit/docs/parallel-execution.md`
- `scripts/runtime_doctor.py`

Implemented first slice:

- `relay-kit lane audit <project> --strict --json`
- active-lane lock conflict and broad lock-scope checks
- parked-lane `resume_condition` checks
- active-lane `wave_id` checks and `depends_on`/`wave_id`/`resume_condition` template columns
- handoff expected-return-condition checks
- live runtime doctor calls lane audit without breaking single-lane projects

### Package D: Tool And Permission Hardening

Goal: Make tool access and shell risk visible before enterprise users trust the kit.

Adopt from reports 11 and 12:

- classify tools by read/analyze/edit/test/external side effects
- require tool stance for every risk-sensitive skill
- detect dangerous shell intent and broad allowlists
- report unsupported adapter-level permission enforcement clearly

Candidate files:

- `scripts/policy_guard.py`
- `scripts/skill_gauntlet.py`
- `relay_kit_v3/registry/skills.py`
- `docs/relay-kit-policy-packs.md`
- `docs/relay-kit-trusted-manifest.md`

### Package E: Adapter And IDE Bridge

Goal: Keep Relay-kit adapter-neutral while making install and runtime behavior predictable across Codex, Claude, and Agent surfaces.

Adopt from report 02:

- document what each adapter supports
- show what metadata each adapter preserves or ignores
- add doctor findings when adapter output lacks expected metadata
- keep generated skills consistent across `.codex`, `.claude`, and `.agent`

Candidate files:

- `relay_kit_public_cli.py`
- `relay_kit_v3/registry/bundles.py`
- `scripts/validate_runtime.py`
- `docs/relay-kit-bundle-manifest.md`

Implemented first slice:

- `relay-kit adapter diagnose <project> --adapter all --strict --json`
- generated skill parity checks for `.codex`, `.claude`, and `.agent`
- non-allowlisted extra skill checks
- frontmatter drift checks for `name`, `description`, `paths`, `context`, `allowed-tools`, and `effort`
- explicit metadata policy reporting for Codex, Claude, and Agent/Antigravity
- required enterprise readiness gate for adapter diagnostics

### Package F: Query And Service Boundaries

Goal: Make Relay-kit easier to maintain as runtime gates grow.

Adopt from reports 06 and 07:

- query layer for docs/state/evidence lookup
- service-boundary map for CLI, registry, gates, support, release, telemetry, and publication
- module-boundary tests for public CLI flows

Candidate files:

- `relay_kit_v3/*`
- `docs/relay-kit-architecture-map.md`
- `tests/test_public_cli_doctor.py`
- `tests/test_readiness_check.py`

Implemented first slice:

- `relay-kit query search <project> --query "..."`
- default scopes: state, contracts, docs, evidence, and registry
- ranked results include score, authority, freshness, source type, file, and line
- `relay-kit service boundaries <project> --strict --json`
- service-boundary map for public CLI, registry, gates, support, release, publication, telemetry/Pulse, and query
- static tests for registry-to-CLI and runtime-to-scripts boundary violations

## Not Adopted

These ideas are deliberately not adopted as-is:

- Claude-specific names, prompts, or skill text.
- Claude permission modes as Relay-kit runtime modes.
- Hot reload or resident file watcher as a core Relay-kit runtime requirement.
- Inline shell execution from skill markdown.
- Treating report 05 and report 10 as independent evidence.

## Next Implementation Slice

Recommended next slice:

Continue from query/service boundaries into dashboard/eval polish advanced.

Acceptance criteria:

- Done: `relay-kit query search <project> --query "..."`
- Done: `relay-kit service boundaries <project> --strict --json`
- Next: surface context, lane, adapter, query, and service-boundary artifacts in Pulse/signal export and workflow eval scenarios.

## Progress Definition

Completed means:

- The idea has a Relay-kit-owned name.
- It is implemented in registry/scripts/docs.
- Generated adapter surfaces are refreshed when relevant.
- Tests or semantic fixtures prove the behavior.
- Runtime doctor, skill gauntlet, and enterprise readiness still pass.

Not completed means:

- The idea is only mentioned in a Claude report.
- The idea is only described in this matrix.
- The behavior depends on external Claude-specific runtime behavior.
- There is no Relay-kit test, gate, or CLI proof.
