# test-first-development

## Skill

- name: test-first-development
- current bundle: discipline-utilities
- current layer: layer-3 utility provider

## Usage summary

- repos covered: 12
- total tasks: 12
- isolated tasks completed: 12
- pressure-round tasks completed: 3

## Quantitative summary

- tasks with clear benefit: 10
- tasks with neutral result: 2
- tasks with negative or noisy result: 0
- tasks where the skill prevented a guess: 12
- tasks where the skill improved evidence quality: 12
- tasks where the skill added noticeable ceremony: 3

## Score by criterion

Use a 1-5 scale.

- `1` = poor or failed
- `2` = weak
- `3` = mixed
- `4` = strong
- `5` = very strong

### layer-fit

- score: 5
- evidence: The skill stayed a pure implementation utility that paired cleanly with `developer` and `test-hub`.

### cross-cutting-value

- score: 4
- evidence: It worked across Python, TS, CLI, framework, and library repos, but several wins were characterization/tightening tests rather than classic red-green feature work.

### noise-cost

- score: 3
- evidence: A1-T, A4-T, and B3-T each needed extra harness work or a dedicated test file. The value is real, but the baseline cost is not uniformly low.

### adapter-parity

- score: 4
- evidence: Round 0 proved the runtime wiring across `.claude`, `.agent`, and `.codex`, and no gating issue appeared. Live workflow evaluation still happened through Codex only.

### gating-safety

- score: 5
- evidence: Round 0 confirmed no leakage into `round2`, `round3`, or `round4`, and the skill needs no extra state/contracts.

### workflow-benefit

- score: 4
- evidence: Pressure round was positive, especially on the itsdangerous red-test case, but the skill is clearly strongest when there is a crisp behavior target rather than every implementation task.

### repeatability

- score: 4
- evidence: All 12 trials produced useful tests, but the mode of value varied: some were red-first blockers, some were green characterizations, and some were semantics-tightening checks.

## Verdict gates

Answer each with `yes` or `no`.

- does it remain a clean layer-3 utility: yes
- does it help across more than one workflow family: yes
- does it improve evidence or decision quality: yes
- does it avoid adding too much baseline ceremony: no
- does it preserve current bundle boundaries: yes
- does it avoid needing new state/contracts: yes

## Final verdict

Choose exactly one:

- `keep-overlay-next-cycle`

## Reasoning

- strongest evidence for the verdict: the skill clearly improves work quality and keeps developers honest, especially when a bug or behavior change can be expressed as a tight red-green loop.
- strongest counterargument: the gauntlet did not show uniformly low-cost adoption. Several good outcomes required extra harness work, which means promoting it to baseline now would make simple lanes heavier by default.
- what would need to change to promote it later: another cycle should show the skill staying low-noise on a larger share of ordinary feature work, not just bug, compatibility, and semantics tasks.

## Decision note

This scorecard is filled from actual task logs in `docs/gauntlet-runs/discipline-utilities-v1/tasks/*-T.md` plus `pressure-round.md`.
