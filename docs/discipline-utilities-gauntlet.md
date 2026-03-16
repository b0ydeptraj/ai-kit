# discipline-utilities-gauntlet

## Status

- Proposed execution plan
- Decision owner: `Relay-kit` architecture
- Purpose: produce one high-confidence fold or keep decision for `discipline-utilities`

## Goal

Run one large, fixed-scope gauntlet that is strong enough to decide whether any `discipline-utilities` skill should be folded into a future baseline.

Skills in scope:

- `root-cause-debugging`
- `test-first-development`
- `evidence-before-completion`

This gauntlet is designed to avoid three failure modes:

1. deciding from theory instead of repo evidence
2. deciding from one or two hand-picked tasks
3. changing the rules after seeing the results

## Non-negotiable rules

1. Freeze the repo list and task list before execution starts.
2. Do not swap out tasks because a task looks too easy or too hard.
3. Log evidence per task, not only per repo.
4. Do not fold a skill because it "feels right".
5. Treat `round4` as the baseline control and `discipline-utilities` as the treatment.
6. A skill may be folded only if it clears the thresholds in this document and still satisfies `docs/discipline-utilities-baseline-proposal.md`.

## Gauntlet shape

- 12 repos
- 36 tasks
- 4 rounds
- 3 adapters smoke-checked for runtime parity
- 1 final verdict per skill

## Success standard

At the end of the gauntlet, each skill must land in exactly one state:

- `fold-next-baseline`
- `keep-overlay-next-cycle`
- `keep-overlay-long-term`

## Repo matrix

Use 12 repos so the result is not tied to one coding style, one framework family, or one maintenance culture.

### Track A: Python library / core utility

1. `pallets/click`
   - type: CLI library
   - main pressure: real bug investigation, generator behavior, compatibility
2. `pallets/itsdangerous`
   - type: security and serialization library
   - main pressure: API compatibility, evidence, contract confidence
3. `pallets-eco/blinker`
   - type: event/signaling library
   - main pressure: narrow edge cases, tests, public API behavior
4. `pallets/markupsafe`
   - type: low-level library
   - main pressure: correctness, edge-case testing, regression risk

### Track B: Python app / tooling / service

5. `httpie/cli`
   - type: CLI application
   - main pressure: bugfix plus integration-style verification
6. `encode/httpx`
   - type: HTTP client
   - main pressure: public API behavior, regression discipline, evidence
7. `pallets/flask`
   - type: web framework / application backbone
   - main pressure: routing, integration behavior, compatibility, docs-to-runtime drift
8. `fastapi/fastapi`
   - type: API framework / service-heavy codebase
   - main pressure: type-driven behavior, API surface, verification discipline

### Track C: TypeScript / web / frontend-adjacent

9. `sindresorhus/ky`
   - type: browser-focused HTTP client
   - main pressure: test-first on JS/TS and review evidence
10. `axios/axios`
   - type: larger HTTP client / cross-environment package
   - main pressure: multi-path compatibility and review discipline
11. `sindresorhus/p-limit`
   - type: small async utility
   - main pressure: edge-case correctness, low-level test discipline, low-noise baseline fit
12. `date-fns/date-fns`
   - type: broadly used utility package
   - main pressure: API stability, regression evidence, noisy-change detection

If a repo cannot be cloned or built reliably on the pilot machine, replace it with a repo of the same slot type. Do not replace a Python slot with a frontend slot or vice versa.

## Task matrix

Total tasks: 36

- 12 for `root-cause-debugging`
- 12 for `test-first-development`
- 12 for `evidence-before-completion`

Each repo contributes exactly 3 tasks:

- 1 debugging task
- 1 test-first task
- 1 completion-evidence task

## Task sourcing rules

For each repo, source tasks from one of these places:

1. an in-code `TODO`, `FIXME`, or edge-case comment
2. a nearby missing test or obvious untested branch
3. a suspicious API or compatibility edge that can be demonstrated
4. an open issue, if it is localizable and reproducible quickly

Do not use vague "improve code quality" tasks. Every task must be falsifiable.

## Required task template

Every task must be created with:

- `task-id`
- `repo`
- `skill-under-test`
- `task-type`
- `target files`
- `initial hypothesis`
- `baseline evidence available before work`
- `success condition`
- `failure condition`

## Round structure

### Round 1: Calibration

Purpose:

- make sure the repo runs
- identify the right test command
- confirm the task is real and scoped

Required outputs:

- repo setup notes
- command used for tests
- command used for lint or type checks if relevant
- baseline reproduction or baseline test status

### Round 2: Single-skill trials

Purpose:

- evaluate each skill in isolation on its own task family

Execution rule:

- when testing `root-cause-debugging`, do not bring in `test-first-development` as the primary method
- when testing `test-first-development`, do not let the task quietly degrade into generic implementation
- when testing `evidence-before-completion`, do not accept "it seems fine" as evidence

Required output per task:

- exact commands run
- exact files inspected
- exact evidence gathered
- whether the skill reduced ambiguity
- whether the skill added noise

### Round 3: Pressure round

Purpose:

- verify that the skill still helps when used inside a real workflow rather than in isolation

Required pairings:

- `root-cause-debugging` with `debug-hub`
- `test-first-development` with `developer` and `test-hub`
- `evidence-before-completion` with `qa-governor` and `review-hub`

Pressure conditions:

- a task with incomplete or misleading local evidence
- a task with at least one false lead
- a task where the cheapest-looking answer is not yet proven

### Round 4: Decision round

Purpose:

- convert evidence into a strict verdict

Required output:

- one scorecard per skill
- one final recommendation per skill
- one final bundle decision for `discipline-utilities`

## Adapter parity checks

Even though the gauntlet is repo-centric, runtime parity still matters.

Before the decision round, verify that the three overlay skills still generate correctly into:

- `.claude/skills/`
- `.agent/skills/`
- `.codex/skills/`

Also verify that the old bundles still do not emit `discipline-utilities` content unless explicitly requested.

## Required measurements

Each task must record these fields:

- `time-to-first-solid-hypothesis`
- `time-to-first-valid-evidence`
- `time-to-finish`
- `number-of-false-starts`
- `did-the-skill-prevent-a-guess`
- `did-the-skill-force-better-proof`
- `did-the-skill-add-unwanted-ceremony`
- `would-this-help-most-repos-or-only-disciplined-teams`

Do not skip any field.

## Scoring rules

Each skill is scored on:

- `layer-fit`
- `cross-cutting-value`
- `noise-cost`
- `adapter-parity`
- `gating-safety`
- `workflow-benefit`
- `repeatability`

The detailed template lives in `docs/discipline-utilities-gauntlet-scorecard.md`.

## Fold thresholds

A skill may be marked `fold-next-baseline` only if all of these are true:

1. it passes layer-fit with no major objections
2. it shows clear benefit in at least 9 of 12 tasks in its own task family
3. it still shows value in the pressure round
4. it does not create high noise for simple or medium tasks
5. it does not require new contracts or state files
6. it keeps bundle gating clean
7. adapter behavior remains symmetric enough to ship
8. its positive results are spread across at least 3 repo tracks, not concentrated in only one ecosystem

If any of those fail, the skill does not get folded.

## Expected decision bias

This gauntlet intentionally favors caution.

That means:

- "useful" is not enough to fold
- "good for experts" is not enough to fold
- "helped on one repo" is not enough to fold
- only "reliably improves the baseline without making it noisier" is enough to fold

## Current prediction before the gauntlet

This is a prediction, not a verdict:

- `evidence-before-completion` is the strongest fold candidate
- `root-cause-debugging` is the second candidate
- `test-first-development` is the most likely to remain an overlay

The gauntlet exists to confirm or overturn that prediction.

## Execution order

Recommended order:

1. run all calibration steps
2. run all 12 debugging tasks
3. run all 12 test-first tasks
4. run all 12 completion-evidence tasks
5. run pressure round re-checks on the most representative tasks from each track
6. complete the scorecards
7. update `docs/discipline-utilities-baseline-proposal.md` only after the verdict is locked

## Final deliverables

At the end of the gauntlet, produce:

1. a repo-by-repo evidence log
2. a per-task results table
3. one scorecard per skill
4. one final decision memo
5. an update to `docs/discipline-utilities-baseline-proposal.md` only if the verdict changes

## Final rule

Do not fold any `discipline-utilities` skill into the baseline during execution.

The gauntlet is an evaluation instrument, not a hidden migration.
