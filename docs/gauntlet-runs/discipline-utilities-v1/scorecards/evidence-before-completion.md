# evidence-before-completion

## Skill

- name: evidence-before-completion
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
- tasks where the skill prevented a guess: 11
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
- evidence: The skill consistently acted as a readiness/evidence utility for `qa-governor` and `review-hub`, never as a lane owner.

### cross-cutting-value

- score: 5
- evidence: It worked across compatibility checks, deprecation reviews, async/config paths, concurrency semantics, and date/semantics review work.

### noise-cost

- score: 5
- evidence: The logs rate ceremony as low, because the skill mostly changes the acceptance bar rather than adding implementation overhead.

### adapter-parity

- score: 4
- evidence: Round 0 proved the runtime exists in all three adapters and the gauntlet found no parity issue, but the live workflow evaluation still happened through Codex only.

### gating-safety

- score: 5
- evidence: Round 0 confirmed no leakage into `round2`, `round3`, or `round4`, and the skill needs no extra state/contracts.

### workflow-benefit

- score: 5
- evidence: Pressure round showed the skill does both required jobs: block bad completion claims and approve narrow claims when the proof is actually sufficient.

### repeatability

- score: 5
- evidence: 11 tasks correctly blocked over-broad claims and 1 task (`C3-E`) correctly approved a narrow claim. The pattern is stable, not random.

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

- strongest evidence for the verdict: the skill was correct in both directions: it blocked 11 unsafe completion claims and approved 1 narrow, well-proven claim. That is exactly the baseline gate behavior the system needs.
- strongest counterargument: some teams may feel the baseline becomes stricter, especially when they are used to broad ?good enough? completion claims.
- what would need to change to promote it later: nothing material; the gauntlet already meets the promotion threshold.

## Decision note

This scorecard is filled from actual task logs in `docs/gauntlet-runs/discipline-utilities-v1/tasks/*-E.md` plus `pressure-round.md`.
