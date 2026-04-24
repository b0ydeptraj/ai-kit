[English](README.md) | [Tiếng Việt](README.vi.md)

# Relay-kit

Relay-kit is a workflow operating system for teams that build with coding agents.

It does not try to make the model magically smarter. It makes the work more disciplined.

With Relay-kit, an agent gets:

- a clearer starting point
- better reusable skills
- a stricter way to plan, build, debug, and review
- shared artifacts so work does not live only in chat memory

The result is simple: agents work with more structure, fewer random moves, and stronger proof before anything is called done.

## Install and use (GitHub)

For users who just want to install and run:

```bash
pipx install "git+https://github.com/b0ydeptraj/Relay-kit.git"
relay-kit "C:\\path\\to\\my-app" --codex
relay-kit "C:\\path\\to\\my-app" --claude
relay-kit "C:\\path\\to\\my-app" --antigravity
relay-kit doctor "C:\\path\\to\\my-app"
```

Use one adapter flag per run.

## Why use Relay-kit

Most agent workflows break in the same places:

- work starts before the problem is clear
- implementation drifts away from the approved direction
- bugs get patched without finding the root cause
- "done" gets claimed before there is enough proof

Relay-kit exists to stop that.

It is for:

- solo builders using coding agents seriously
- product and engineering teams that want repeatable output
- people using Claude, Codex, or Antigravity-style agent workflows who need more than prompt packs

Relay-kit gives them a clear operating flow for:

- new work
- bug fixing
- review
- completion

It makes agents behave less like improvising interns and more like engineers working inside a defined system.

## What you get

- a small public skill surface that is easy to remember
- reusable runtime skills for `.claude`, `.agent`, and `.codex`
- shared workflow artifacts in `.relay-kit/`
- a read-only `memory-search` utility for retrieving prior decisions and handoffs
- a `release-readiness` utility for pre/post deploy smoke gates and rollback signals
- an `accessibility-review` gate so frontend quality is not only visual
- a `skill-gauntlet` regression gate to keep skill routing behavior stable
- a `context-continuity` utility for checkpoint, rehydrate, handoff, and diff flows
- an active baseline that is validated instead of loosely assembled
- a way to make work more consistent without forcing everything through raw chat memory

## Quick start

List available skills and bundles:

```bash
python relay_kit.py --list-skills
```

Generate the active baseline:

```bash
python relay_kit.py . --bundle baseline --ai codex --emit-contracts --emit-docs --emit-reference-templates
```

Public installer surface (local repo checkout):

```bash
pipx install .
relay-kit /path/to/project --codex
relay-kit /path/to/project --claude
relay-kit /path/to/project --antigravity
```

Install directly from GitHub:

```bash
pipx install "git+https://github.com/b0ydeptraj/Relay-kit.git"
relay-kit /path/to/project --codex
```

The public wrapper maps:
- `--codex` -> `--ai codex`
- `--claude` -> `--ai claude`
- `--antigravity` -> `--ai antigravity` (runtime target: `.agent/skills`)

Validate the runtime contract:

```bash
relay-kit doctor /path/to/project
python scripts/validate_runtime.py
```

## Start flow

If you only remember a few names, remember these:

| Goal | Public name | Behind the scenes |
|---|---|---|
| find the right path | `start-here` | `workflow-router` |
| shape a rough idea | `brainstorm` | `brainstorm-hub` |
| turn approved work into buildable steps | `write-steps` | `scrum-master` |
| implement the approved slice | `build-it` | `developer` |
| review a branch or PR before merge or sign-off | `review-pr` | `review-hub` |
| debug without guessing | `debug-systematically` | `debug-hub` + `root-cause-debugging` |
| decide if work is actually ready | `ready-check` | `review-hub` + `qa-governor` |
| force a final proof pass | `prove-it` | `evidence-before-completion` |

Default path for new work:

1. `start-here`
2. `brainstorm`
3. `write-steps`
4. `build-it`
5. `ready-check`

Default path for bugs:

1. `start-here`
2. `debug-systematically`
3. `build-it`
4. `ready-check`

Default path for branch or PR review:

1. `review-pr`
2. `ready-check` if you need a real readiness or shipability verdict
3. `prove-it` if the completion claim still sounds stronger than the proof

More detail:
- [`docs/relay-kit-start-flow.md`](docs/relay-kit-start-flow.md)
- [`docs/relay-kit-review-flow.md`](docs/relay-kit-review-flow.md)
- [`docs/relay-kit-memory-search.md`](docs/relay-kit-memory-search.md)
- [`docs/relay-kit-release-readiness.md`](docs/relay-kit-release-readiness.md)
- [`docs/relay-kit-accessibility-review.md`](docs/relay-kit-accessibility-review.md)
- [`docs/relay-kit-skill-gauntlet.md`](docs/relay-kit-skill-gauntlet.md)
- [`docs/relay-kit-context-continuity.md`](docs/relay-kit-context-continuity.md)

## How it works

Relay-kit separates the work into a small number of reliable stages:

1. route the request
2. clarify or investigate
3. slice the work into safe steps
4. implement with evidence
5. review before calling it done

Under the hood, the system uses runtime skills plus shared state, contracts, references, and docs in `.relay-kit/`.

## Configuration

Main entrypoints:

- `relay_kit.py`
- `relay_kit_legacy.py`

Current active baseline:

- `baseline`
- compatibility alias: `baseline-next`

Generated output includes:

- `.codex/skills/`
- `.claude/skills/`
- `.agent/skills/`
- `.relay-kit/contracts/`
- `.relay-kit/state/`
- `.relay-kit/references/`
- `.relay-kit/docs/`

Generate all active adapter runtimes together with `--ai all`:

```bash
python relay_kit.py . --bundle baseline --ai all
```

## Migration status

Phase 3 cutover is active and canonical runtime paths are now:

- `relay_kit.py`
- `relay_kit_legacy.py`
- `.relay-kit/`
- `.relay-kit-prompts/`

Historical compatibility timeline and removal log:
- [`docs/relay-kit-compatibility-cycle.md`](docs/relay-kit-compatibility-cycle.md)

## Public docs index

- [docs/public-docs-index.md](docs/public-docs-index.md)

## Deeper docs

- Start flow:
  - [`docs/relay-kit-start-flow.md`](docs/relay-kit-start-flow.md)
- Review flow:
  - [`docs/relay-kit-review-flow.md`](docs/relay-kit-review-flow.md)
- Memory retrieval utility:
  - [`docs/relay-kit-memory-search.md`](docs/relay-kit-memory-search.md)
- Release readiness and deploy smoke:
  - [`docs/relay-kit-release-readiness.md`](docs/relay-kit-release-readiness.md)
- Accessibility gate:
  - [`docs/relay-kit-accessibility-review.md`](docs/relay-kit-accessibility-review.md)
- Skill behavior gauntlet:
  - [`docs/relay-kit-skill-gauntlet.md`](docs/relay-kit-skill-gauntlet.md)
- Context continuity:
  - [`docs/relay-kit-context-continuity.md`](docs/relay-kit-context-continuity.md)
  - [`docs/relay-kit-context-continuity-design-note.md`](docs/relay-kit-context-continuity-design-note.md)
- Skill authoring:
  - [`docs/how-to-write-skills.md`](docs/how-to-write-skills.md)
- Contributing:
  - [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Folder structure:
  - [`.relay-kit/docs/folder-structure.md`](.relay-kit/docs/folder-structure.md)
- Bundle gating:
  - [`.relay-kit/docs/bundle-gating.md`](.relay-kit/docs/bundle-gating.md)

## Legacy note

Legacy kits still exist for migration and compatibility work. They are not the main Relay-kit runtime story.

