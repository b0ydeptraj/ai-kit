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

## 5-minute start

For users who just want to install Relay-kit and generate one runtime:

```bash
pipx install "git+https://github.com/b0ydeptraj/Relay-kit.git"
relay-kit init "C:\\path\\to\\my-app" --codex
relay-kit locale set "C:\\path\\to\\my-app" --locale vi
relay-kit doctor "C:\\path\\to\\my-app"
```

Use one adapter flag per run. Replace `--codex` with `--claude` or `--antigravity` when that is the target agent.
The default install is the full enterprise governance bundle. Use `--baseline` only when you want the smaller first-install surface.

For a local repo checkout:

```bash
pipx install .
relay-kit init /path/to/project --codex
relay-kit doctor /path/to/project
```

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

## Domain Skill Pack

PR 1 expands the enterprise runtime with Relay-kit-owned domain skills:

- `go-service-engineering`
- `next-product-frontend`
- `growth-marketing`
- `market-research`
- `automation-ops`
- `vietnamese-product-localization`

These names and contracts are Relay-kit-owned and are not copied from external kits.
Vietnamese support remains explicit/opt-in; use one global locale switch when you want runtime-wide language enforcement.

## Global Locale Switch

Relay-kit now supports one global runtime locale switch for all adapters:

- default locale profile: `en`
- set once per project: `relay-kit locale set <project> --locale <code>`
- locale packs v1: `en`, `vi` only
- runtime policy accepts only `en` or `vi`; unsupported values are rejected by `relay-kit locale set`
- applies metadata localization only (skill descriptions, command/agent surface intent/evidence) after normal generation flow
- canonical routing IDs/contracts stay in English and stable
- `relay-kit command list` and `relay-kit agent list` stay English by default for stable machine parsing

Examples:

```bash
relay-kit locale show /path/to/project --json
relay-kit locale set /path/to/project --locale vi --json
relay-kit init /path/to/project --codex --locale vi
```

## What you get

- a small public skill surface that is easy to remember
- reusable runtime skills for `.claude`, `.agent`, and `.codex`
- shared workflow artifacts in `.relay-kit/`
- a read-only `memory-search` utility for retrieving prior decisions and handoffs
- a `context audit` gate for checking source authority, freshness, and missing handoff context
- a `lane audit` gate for checking lock conflicts, parked-lane resume conditions, and handoff return contracts
- an `adapter diagnose` gate for checking generated Codex, Claude, and Agent skill parity plus frontmatter drift
- a lifecycle command registry with deterministic command surfaces for `.claude`, `.codex`, and `.agent`
- a `command diagnose` gate for strict command parity across adapters
- explicit `relay-engineer` and `relay-growth` agent profiles with deterministic surfaces for `.relay-kit`, `.claude`, `.codex`, and `.agent`
- an `agent diagnose` gate for strict profile parity and profile-contract drift
- a `query search` utility for ranked lookup across state, contracts, docs, evidence, and registry sources
- a `service boundaries` gate for checking module ownership and static dependency rules
- a `release-readiness` utility for pre/post deploy smoke gates and rollback signals
- an `accessibility-review` gate so frontend quality is not only visual
- a `skill-gauntlet` regression gate to keep skill routing behavior stable
- a `context-continuity` utility for checkpoint, rehydrate, handoff, and diff flows
- a `readiness check` gate that combines tests, doctor, policy, manifest trust, upgrade, support, contract sync, and signal export proof
- local Pulse reports and signal exports for quality review and support diagnostics
- an active baseline that is validated instead of loosely assembled
- a way to make work more consistent without forcing everything through raw chat memory

## Useful commands

List active runtime bundles:

```bash
relay-kit --list-skills
```

Generate all active adapters:

```bash
relay-kit init /path/to/project --all
```

Run the enterprise governance gates after the default full install:

```bash
relay-kit init /path/to/project --all
relay-kit manifest write /path/to/project
relay-kit manifest stamp /path/to/project --issuer relay-kit --channel enterprise
relay-kit doctor /path/to/project --policy-pack enterprise
relay-kit upgrade mark-current /path/to/project --adapter all
relay-kit readiness check /path/to/project --profile enterprise
```

Run the support gate:

```bash
relay-kit doctor /path/to/project
relay-kit manifest verify /path/to/project --trusted
relay-kit doctor /path/to/project --policy-pack enterprise
```

Show recent gate evidence:

```bash
relay-kit evidence summary /path/to/project
relay-kit doctor /path/to/project --json
```

Doctor writes local JSONL events to `.relay-kit/evidence/events.jsonl`.

Audit context freshness before continuing a long-running lane:

```bash
relay-kit context audit /path/to/project --strict --json
relay-kit context budget /path/to/project --max-tokens 8000 --strict --json
relay-kit context pack /path/to/project --task "ship release safely" --max-tokens 8000 --strict --json
relay-kit token audit /path/to/project --max-tokens 8000 --strict --json
```

Audit lane coordination before trusting parallel work:

```bash
relay-kit lane audit /path/to/project --strict --json
```

Audit adapter runtime surfaces before trusting editor handoff:

```bash
relay-kit adapter diagnose /path/to/project --adapter all --strict --json
```

Inspect lifecycle command routing and parity:

```bash
relay-kit command list /path/to/project --json
relay-kit command diagnose /path/to/project --adapter all --strict --json
```

Inspect agent profile routing contracts and parity:

```bash
relay-kit agent list /path/to/project --json
relay-kit agent diagnose /path/to/project --adapter all --strict --json
```

Search Relay-kit sources without broad context dumping:

```bash
relay-kit query search /path/to/project --query "support handoff" --json
```

Check service-boundary drift:

```bash
relay-kit service boundaries /path/to/project --strict --json
```

Export planning and QA contracts as machine-readable JSON:

```bash
relay-kit contract export /path/to/project
relay-kit contract import /path/to/project --contract-file /path/to/relay-contract.json
relay-kit contract import /path/to/project --contract-file /path/to/relay-contract.json --apply
```

Write and verify the bundle checksum manifest:

```bash
relay-kit manifest write /path/to/project
relay-kit manifest verify /path/to/project
relay-kit manifest stamp /path/to/project --issuer relay-kit --channel enterprise
relay-kit manifest verify /path/to/project --trusted
```

Run policy guard packs:

```bash
relay-kit policy list
relay-kit policy check /path/to/project --pack enterprise --strict
```

Prepare a support diagnostics bundle:

```bash
relay-kit support bundle /path/to/project --policy-pack enterprise
relay-kit support request /path/to/project --severity P1 --policy-pack enterprise --json
relay-kit support triage /path/to/project --strict --json
```

When the support request artifact already exists, the support bundle includes a
redacted support-request summary for triage. `support triage` reads the request
and bundle artifacts together before the case is handed to paid support.

Build a local Pulse quality report:

```bash
relay-kit pulse build /path/to/project
relay-kit pulse build /path/to/project --include-readiness --json
relay-kit pulse build /path/to/project --include-package-index --json
relay-kit pulse build /path/to/project --support-request-file .relay-kit/support/support-request.json
relay-kit pulse build /path/to/project --include-context-audit --include-lane-audit --include-adapter-diagnostics --include-token-audit --include-query-search --include-service-boundaries --json
relay-kit pulse build /path/to/project --history-limit 50
```

Pulse includes a gate summary for workflow eval, readiness, publication,
package-index, support request, and evidence ledger status so dashboard review
can see which gate is pass, attention, hold, or not-run. The report also includes gate
details for degraded scenarios, findings, diagnostics, and failed evidence
events. Governance health sections can also surface stale context sources, lane
conflicts, adapter metadata drift, token budget violations, authoritative query hits, and
service-boundary findings.

Export Pulse and evidence ledger signals:

```bash
relay-kit signal export /path/to/project
relay-kit signal export /path/to/project --json
```

Run the paid/team readiness gate:

```bash
relay-kit readiness check /path/to/project --profile enterprise
relay-kit readiness check /path/to/project --profile enterprise --json
```

Verify local release-lane prerequisites:

```bash
relay-kit release verify /path/to/project
relay-kit release verify /path/to/project --json
```

Plan and record package publication evidence:

```bash
relay-kit publish trail /path/to/project --channel pypi --json
relay-kit publish plan /path/to/project --channel pypi --json
relay-kit publish evidence /path/to/project --channel pypi --twine-check-file .tmp/twine-check.txt --upload-log-file .tmp/upload-log.txt --publication-plan-file .relay-kit/release/publication-plan.json --json
relay-kit publish status /path/to/project --strict --json
relay-kit publish index-check /path/to/project --channel pypi --target-version X.Y.Z --package-url https://pypi.org/project/relay-kit/X.Y.Z/ --strict --json
```

Measure workflow routing quality with bundled scenarios:

```bash
relay-kit eval run /path/to/project --strict
relay-kit eval run /path/to/project --json --output-file workflow-eval.json
relay-kit eval run /path/to/project --strict --baseline-file previous-workflow-eval.json
```

The bundled default eval suite covers 70 production/team scenarios across
orchestration, hubs, utility providers, specialists, runtime diagnostics,
context governance, lane audit, adapter diagnostics, query lookup, and
service-boundary review.

Track installed runtime version and print upgrade actions:

```bash
relay-kit manifest write /path/to/project
relay-kit upgrade mark-current /path/to/project --bundle baseline --adapter codex
relay-kit upgrade check /path/to/project --strict
relay-kit upgrade plan /path/to/project
```

Maintainer-only core entrypoint:

```bash
python relay_kit.py /path/to/project --bundle baseline --ai codex --emit-contracts --emit-docs --emit-reference-templates
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

Use `prove-it` for a narrow claim-to-evidence pass. Use `ready-check` when you need a go / no-go readiness verdict and `qa-report.md`.

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

Current active baseline:

- `baseline`
- runtime family: `core`, `orchestration`, `runtime`

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

## Naming status

Relay-kit v4 uses Relay-kit-only naming across runtime bundles and guards.

Canonical runtime paths:

- `relay_kit.py`
- `.relay-kit/`
- `.relay-kit-prompts/`

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
- Release lane verification:
  - [`docs/relay-kit-release-lane.md`](docs/relay-kit-release-lane.md)
- Publication planning and evidence:
  - [`docs/relay-kit-publication-plan.md`](docs/relay-kit-publication-plan.md)
- Accessibility gate:
  - [`docs/relay-kit-accessibility-review.md`](docs/relay-kit-accessibility-review.md)
- Commercial readiness gate:
  - [`docs/relay-kit-readiness-check.md`](docs/relay-kit-readiness-check.md)
- Pulse quality report:
  - [`docs/relay-kit-pulse-report.md`](docs/relay-kit-pulse-report.md)
- Signal export:
  - [`docs/relay-kit-signal-export.md`](docs/relay-kit-signal-export.md)
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
