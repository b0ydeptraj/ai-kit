# Relay-kit v3.2

`Relay-kit` now runs with a registry-driven v3 entrypoint while preserving a one-cycle compatibility layer for the old names.

Compatibility note:
- the product brand is now `Relay-kit`
- preferred CLI entrypoints are now `relay_kit.py` and `relay_kit_legacy.py`
- `python_kit.py` and `python_kit_legacy.py` remain as compatibility aliases for one cycle
- generic prompt output now prefers `.relay-kit-prompts/` and mirrors `.python-kit-prompts/` for one cycle

## Status snapshot

- Current baseline: `baseline` / `v3.2`
- Compatibility baseline still supported: `round4`
- Compatibility alias retained for one cycle: `baseline-next`
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
- preserves legacy kits through `relay_kit_legacy.py` while keeping `python_kit_legacy.py` as an alias

## Runtime layout

After running v3 generation, the repo uses these runtime folders:

- `.claude/skills/` -> Claude runtime skills
- `.agent/skills/` -> Gemini-compatible runtime skills and the active compatibility target for Antigravity-style usage
- `.codex/skills/` -> Codex runtime skills
- `.ai-kit/contracts/` -> shared workflow contracts
- `.ai-kit/state/` -> workflow state, lane registry, handoff log, and multi-lane coordination state
- `.ai-kit/references/` -> living support references
- `.ai-kit/docs/` -> topology, migration, gating, and runtime helper docs

## Quick start

### list bundles and kits

```bash
python relay_kit.py --list-skills
```

### generate the full round 4 layer set

```bash
python relay_kit.py . --bundle round4 --ai claude --emit-contracts --emit-docs --emit-reference-templates
python relay_kit.py . --bundle round4 --ai gemini --emit-contracts --emit-docs --emit-reference-templates
python relay_kit.py . --bundle round4 --ai codex --emit-contracts --emit-docs --emit-reference-templates
```

### generate utility overlays or compatibility bundles

```bash
python relay_kit.py . --bundle utility-providers --ai claude --emit-docs
python relay_kit.py . --bundle discipline-utilities --ai claude --emit-docs
python relay_kit.py . --bundle baseline --ai codex --emit-contracts --emit-docs --emit-reference-templates
python relay_kit.py . --bundle round3 --ai codex --emit-contracts --emit-docs --emit-reference-templates
python relay_kit.py . --bundle round2 --ai codex --emit-contracts --emit-docs --emit-reference-templates
```

### legacy kits

```bash
python relay_kit.py . --legacy-kit python --ai claude
python relay_kit.py . --legacy-kit flutter --ai claude
python relay_kit.py . --legacy-kit antigravity --ai gemini
python relay_kit.py . --legacy-kit claudekit --ai claude
python relay_kit.py . --legacy-kit ui-ux --ai codex
python relay_kit.py . --legacy-kit full --ai all
```

Legacy kits are migration and compatibility flows. They can materialize ClaudeKit or Antigravity-shaped assets, but they do not redefine the active v3 runtime model.

### one-cycle compatibility aliases

```bash
python python_kit.py --list-skills
python python_kit.py . --bundle baseline --ai codex --emit-contracts --emit-docs --emit-reference-templates
python python_kit.py . --legacy-kit python --ai claude
```

### validate adapter parity and bundle gating

```bash
python scripts/validate_runtime.py
```

This validation checks the active v3 runtime contract:
- `--ai all` writes `.claude/skills`, `.agent/skills`, and `.codex/skills`
- checked-in runtime skill folders stay in parity across the three adapters
- `round4` does not leak discipline utilities
- `discipline-utilities` stays overlay-only
- `baseline-next` contains only the approved discipline additions

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
| `baseline` | official baseline: `round4` plus `root-cause-debugging` and `evidence-before-completion` |
| `baseline-next` | compatibility alias for `baseline` during the promotion cycle |

Use `--emit-contracts`, `--emit-docs`, and `--emit-reference-templates` to materialize `.ai-kit/` outputs alongside skill generation.

`discipline-utilities` is intentionally additive: it strengthens execution discipline without changing the behavior or scope of `round2`, `round3`, or `round4`.

`baseline` is now the official active baseline. It leaves `round4` untouched and adds only the two discipline utilities approved by the gauntlet.

`baseline-next` is retained as a compatibility alias for one promotion cycle so earlier commands and notes do not break immediately.

For v3 bundle generation, `--ai all` writes `.claude/skills`, `.agent/skills`, and `.codex/skills`. Legacy kits keep their legacy compatibility behavior, so use `--ai codex` explicitly when you need Codex output from the preserved generator.

See also: [`docs/discipline-utilities-baseline-proposal.md`](docs/discipline-utilities-baseline-proposal.md)
See also: [`docs/relay-kit-compatibility-cycle.md`](docs/relay-kit-compatibility-cycle.md)

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

- `relay_kit.py` is the preferred Relay-kit v3 entrypoint.
- `python_kit.py` remains a compatibility alias for one cycle.
- `relay_kit_legacy.py` is the preferred preserved legacy generator.
- `python_kit_legacy.py` remains a compatibility alias for one cycle.
- `.relay-kit-prompts/` is the preferred generic output path; `.python-kit-prompts/` is mirrored for one cycle.
- `round2` and `round3` behavior stay available.
- `round4` adds utility providers, bundle gating, and stronger multi-lane state on top of the round 3 base instead of replacing it.
- renaming the physical repo folder is deferred to a later manual migration after the compatibility cycle so current absolute Windows paths remain truthful.
- use `docs/relay-kit-compatibility-cycle.md` as the removal gate before deleting old names or renaming the physical repo folder.
