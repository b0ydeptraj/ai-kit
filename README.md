# Relay-kit v3.2

`Relay-kit` is a workflow system for coding agents.

It helps you do five things well:
- clarify work before building
- cut approved work into safe steps
- implement with evidence instead of vibes
- debug from root cause instead of guesswork
- block weak completion claims

The internal system is deep. The public face should still be simple.

## Start here in 30 seconds

If you only remember one thing, remember these names:

| If you want to... | Use this public name | Behind the scenes |
|---|---|---|
| figure out where to start | `start-here` | `workflow-router` |
| turn a rough idea into a clear direction | `brainstorm` | `brainstorm-hub` |
| slice approved work into buildable steps | `write-steps` | `scrum-master` |
| implement an approved slice | `build-it` | `developer` |
| debug a bug or mismatch properly | `debug-systematically` | `debug-hub` + `root-cause-debugging` |
| decide whether work is actually ready | `ready-check` | `review-hub` + `qa-governor` |
| force one last proof pass | `prove-it` | `evidence-before-completion` |

See also: [`docs/relay-kit-start-flow.md`](docs/relay-kit-start-flow.md)

## Default paths

### New work

1. `start-here`
2. `brainstorm`
3. `write-steps`
4. `build-it`
5. `ready-check`
6. `prove-it` when the completion claim still needs a stricter proof pass

### Bug or regression

1. `start-here`
2. `debug-systematically`
3. `build-it` once the fix path is real
4. `ready-check`

### Final confidence check

1. `prove-it`
2. `ready-check`

## CLI quick start

### list bundles and kits

```bash
python relay_kit.py --list-skills
```

### generate the active baseline

```bash
python relay_kit.py . --bundle baseline --ai codex --emit-contracts --emit-docs --emit-reference-templates
```

### validate the runtime contract

```bash
python scripts/validate_runtime.py
```

## Compatibility note

- the product brand is now `Relay-kit`
- preferred CLI entrypoints are now `relay_kit.py` and `relay_kit_legacy.py`
- `python_kit.py` and `python_kit_legacy.py` remain compatibility aliases for one cycle
- generic prompt output now prefers `.relay-kit-prompts/` and mirrors `.python-kit-prompts/` for one cycle
- the public names above are convenience aliases in the repo-local skill surface for day-to-day use; the canonical runtime skills and bundles remain unchanged

## Status snapshot

- Current baseline: `baseline` / `v3.2`
- Compatibility baseline still supported: `round4`
- Compatibility alias retained for one cycle: `baseline-next`
- Hardened topology: orchestrators + workflow hubs + utility providers + specialists
- Optional discipline overlay available through `discipline-utilities`

## Runtime layout

After running v3 generation, the repo uses these runtime folders:

- `.claude/skills/` -> Claude runtime skills
- `.agent/skills/` -> Gemini-compatible runtime skills and the active compatibility target for Antigravity-style usage
- `.codex/skills/` -> Codex runtime skills
- `.ai-kit/contracts/` -> shared workflow contracts
- `.ai-kit/state/` -> workflow state, lane registry, handoff log, and multi-lane coordination state
- `.ai-kit/references/` -> living support references
- `.ai-kit/docs/` -> topology, migration, gating, and runtime helper docs

## Legacy kits

```bash
python relay_kit.py . --legacy-kit python --ai claude
python relay_kit.py . --legacy-kit flutter --ai claude
python relay_kit.py . --legacy-kit antigravity --ai gemini
python relay_kit.py . --legacy-kit claudekit --ai claude
python relay_kit.py . --legacy-kit ui-ux --ai codex
python relay_kit.py . --legacy-kit full --ai all
```

Legacy kits are migration and compatibility flows. They can materialize ClaudeKit or Antigravity-shaped assets, but they do not redefine the active v3 runtime model.

## One-cycle compatibility aliases

```bash
python python_kit.py --list-skills
python python_kit.py . --bundle baseline --ai codex --emit-contracts --emit-docs --emit-reference-templates
python python_kit.py . --legacy-kit python --ai claude
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

This keeps orchestration separate from execution, while still using BMAD-style context handoff through shared artifacts.

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
