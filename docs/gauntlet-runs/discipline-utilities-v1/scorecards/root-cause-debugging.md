# root-cause-debugging

## Skill

- name: root-cause-debugging
- current bundle: discipline-utilities
- current layer: layer-3 utility provider

## Usage summary

- repos covered: 12
- total tasks: 12
- isolated tasks completed: 12
- pressure-round tasks completed: 3

## Quantitative summary

- tasks with clear benefit: 12
- tasks with neutral result: 0
- tasks with negative or noisy result: 0
- tasks where the skill prevented a guess: 12
- tasks where the skill improved evidence quality: 12
- tasks where the skill added noticeable ceremony: 0

## Score by criterion

Use a 1-5 scale.

- `1` = poor or failed
- `2` = weak
- `3` = mixed
- `4` = strong
- `5` = very strong

### layer-fit

- score: 5
- evidence: Every task used the skill as a lane-support utility, not as a planner or router. See `A2-D.md`, `B2-D.md`, `C3-D.md` and the pressure-round root-cause section.

### cross-cutting-value

- score: 5
- evidence: It worked across Python libraries, services, CLI tooling, TS utilities, and web-adjacent repos. All 12 `*-D.md` logs ended with a positive fold signal.

### noise-cost

- score: 5
- evidence: The logs consistently rate ceremony as low, and none of the pressure-round cases required expanding scope or adding state/contracts.

### adapter-parity

- score: 4
- evidence: Round 0 proved the runtime wiring is present for `.claude`, `.agent`, and `.codex`, and no adapter-specific gating issue appeared. The gauntlet itself ran through Codex, so this is strong but not perfect parity evidence.

### gating-safety

- score: 5
- evidence: Round 0 confirmed `round2`, `round3`, and `round4` do not leak this skill, and `discipline-utilities` emits it cleanly.

### workflow-benefit

- score: 5
- evidence: Pressure round showed clean interaction with `debug-hub`: classify, narrow, and only then decide whether a fix lane is warranted.

### repeatability

- score: 5
- evidence: The same reproduce ? narrow ? explain pattern held across all 12 isolated tasks and all 3 pressure cases.

## Verdict gates

Answer each with `yes` or `no`.

- does it remain a clean layer-3 utility: yes
- does it help across more than one workflow family: yes
- does it improve evidence or decision quality: yes
- does it avoid adding too much baseline ceremony: yes
- does it preserve current bundle boundaries: yes
- does it avoid needing new state/contracts: yes

## Final verdict

Choose exactly one:

- `fold-next-baseline`

## Reasoning

- strongest evidence for the verdict: 12/12 isolated tasks and 3/3 pressure cases show the skill turns ambiguous bug reports into bounded explanations before any fix attempt.
- strongest counterargument: some teams already apply similar discipline informally, so the baseline gain can look redundant at first glance.
- what would need to change to promote it later: nothing material; the gauntlet already meets the promotion threshold.

## Decision note

This scorecard is filled from actual task logs in `docs/gauntlet-runs/discipline-utilities-v1/tasks/*-D.md` plus `pressure-round.md`.
