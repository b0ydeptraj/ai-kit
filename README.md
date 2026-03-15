# Python Kit v3.2

`python-kit` now runs with a registry-driven v3 entrypoint while preserving the previous generator as `python_kit_legacy.py`.

## Status snapshot

- Current baseline: `round4` / `v3.2`
- Next baseline candidate bundle: `baseline-next`
- Compatibility bundles still supported: `round2`, `round3`
- Hardened topology: orchestrators + workflow hubs + utility providers + specialists
- Optional discipline overlay available through `discipline-utilities`

## What changed in round 4

- keeps the round 3 BMAD-lite base in place
- hardens **bundle gating** so `round2`, `round3`, and `round4` emit the right contract/doc scopes
- promotes **layer 3 utility providers** to first-class registry skills:
  - `research`, `docs-seeker`, `sequential-thinking`, `problem-solving`, `ai-multimodal`, `chrome-devtools`, `repomix`, `context-engineering`, `mermaidjs-v11`, `ui-ux-pro-max`, `media-processing`
- upgrades **team parallelism** with:
  - `.ai-kit/state/lane-registry.md`
  - `.ai-kit/state/handoff-log.md`
  - richer `workflow-state.md` and `team-board.md`
- adds topology docs for utility providers, standalone taxonomy, bundle gating, and parallelism rules
- preserves legacy kits through `python_kit_legacy.py`

## Runtime layout

After running v3 generation, the repo uses these runtime folders:

- `.claude/skills/` -> Claude runtime skills
- `.agent/skills/` -> Gemini/Antigravity runtime skills
- `.codex/skills/` -> Codex runtime skills
- `.ai-kit/contracts/` -> shared workflow contracts
- `.ai-kit/state/` -> workflow state, lane registry, handoff log, and multi-lane coordination state
- `.ai-kit/references/` -> living support references
- `.ai-kit/docs/` -> topology, migration, gating, and runtime helper docs

## Quick start

### list bundles and kits

```bash
python python_kit.py --list-skills
```

### generate the full round 4 layer set

```bash
python python_kit.py . --bundle round4 --ai claude --emit-contracts --emit-docs --emit-reference-templates
python python_kit.py . --bundle round4 --ai gemini --emit-contracts --emit-docs --emit-reference-templates
python python_kit.py . --bundle round4 --ai codex --emit-contracts --emit-docs --emit-reference-templates
```

### generate utility overlays or compatibility bundles

```bash
python python_kit.py . --bundle utility-providers --ai claude --emit-docs
python python_kit.py . --bundle discipline-utilities --ai claude --emit-docs
python python_kit.py . --bundle baseline-next --ai codex --emit-contracts --emit-docs --emit-reference-templates
python python_kit.py . --bundle round3 --ai codex --emit-contracts --emit-docs --emit-reference-templates
python python_kit.py . --bundle round2 --ai codex --emit-contracts --emit-docs --emit-reference-templates
```

### legacy kits

```bash
python python_kit.py . --legacy-kit python --ai claude
python python_kit.py . --legacy-kit flutter --ai claude
python python_kit.py . --legacy-kit antigravity --ai gemini
python python_kit.py . --legacy-kit claudekit --ai claude
python python_kit.py . --legacy-kit ui-ux --ai codex
python python_kit.py . --legacy-kit full --ai all
```

## v3 bundles

| Bundle | What it writes |
|---|---|
| `bmad-core` | round 2 compatibility core skills |
| `bmad-lite` | round 2 core + cleaned `agentic-loop` |
| `cleanup` | cleanup-only runtime skills |
| `legacy-native` | native support skills (`project-architecture`, `dependency-management`, `api-integration`, `data-persistence`, `testing-patterns`) |
| `round2` | strict round 2 compatibility bundle |
| `orchestrators` | layer 1 orchestration skills |
| `workflow-hubs` | layer 2 workflow hubs |
| `role-core` | layer 4 role specialists including `developer` |
| `round3-core` | orchestrators + hubs + role specialists |
| `round3` | full round 3 set: orchestrators + hubs + roles + cleanup + native support |
| `utility-providers` | layer 3 stateless utility providers |
| `discipline-utilities` | optional root-cause / test-first / completion-evidence overlay plus operational discipline docs |
| `round4-core` | orchestrators + hubs + roles + utility providers |
| `round4` | full round 4 set: round4-core + cleanup + native support |
| `baseline-next` | `round4` plus approved discipline utilities: `root-cause-debugging` and `evidence-before-completion` |

Use `--emit-contracts`, `--emit-docs`, and `--emit-reference-templates` to materialize `.ai-kit/` outputs alongside skill generation.

`discipline-utilities` is intentionally additive: it strengthens execution discipline without changing the behavior or scope of `round2`, `round3`, or `round4`.

`baseline-next` is also additive: it leaves `round4` untouched and exposes the smallest future-baseline candidate bundle approved by the gauntlet.

See also: `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\docs\discipline-utilities-baseline-proposal.md`

## 4-layer usage model

1. `workflow-router` chooses track and entrypoint.
2. `bootstrap`, `cook`, or `team` own orchestration.
3. one workflow hub runs the current playbook (`plan-hub`, `debug-hub`, `test-hub`, etc.) and pulls utility providers as needed.
4. specialists, standalones, and native support skills produce or refresh the real artifacts.

This keeps orchestration separate from execution, while still using BMAD-style context handoff through shared artifacts. BMAD's official workflow map similarly emphasizes routing by phase/track and passing artifacts forward as context instead of relying on raw chat memory.

## Round 4 intent

Round 4 is a **hardening pass**, not a random prompt dump:

- layer 3 becomes explicit instead of implied
- team parallelism has durable state (`lane-registry`, `handoff-log`)
- bundle scopes become cleaner (`round2` no longer needs to spray round3/round4 docs)
- layer 4 standalones get a taxonomy without forcing you to ship every domain skill in one jump

## Migration notes

- `python_kit.py` remains the active v3 entrypoint.
- `python_kit_legacy.py` remains the preserved old generator.
- `round2` and `round3` behavior stay available.
- `round4` adds utility providers, bundle gating, and stronger multi-lane state on top of the round 3 base instead of replacing it.
