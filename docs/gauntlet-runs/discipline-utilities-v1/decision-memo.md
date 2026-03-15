# discipline-utilities-v1 decision memo

## Verdict summary

- `root-cause-debugging` -> `fold-next-baseline`
- `test-first-development` -> `keep-overlay-next-cycle`
- `evidence-before-completion` -> `fold-next-baseline`

## Why

### `root-cause-debugging`
- passed 12/12 isolated tasks with positive fold signals
- passed all 3 pressure-round cases
- stayed low-noise and cleanly layer-3
- improved decision quality before any fix attempt

### `test-first-development`
- produced useful evidence in all 12 trials
- pressure round stayed positive
- but the adoption cost was not uniformly low
- several cases needed harness work, characterization tests, or a separate test file to make the loop practical
- that is strong enough to keep it, not strong enough yet to make it baseline by default

### `evidence-before-completion`
- passed 12/12 isolated tasks with positive fold signals
- pressure round was the strongest of the three skills
- correctly blocked over-broad completion claims in 11 cases
- correctly approved 1 narrow scoped claim when evidence was actually sufficient
- adds very little ceremony while materially raising workflow discipline

## Bundle decision

- keep `discipline-utilities` as an overlay bundle for now
- prepare the next baseline to absorb:
  - `root-cause-debugging`
  - `evidence-before-completion`
- keep `test-first-development` in `discipline-utilities` for at least one more cycle

## Required follow-up to act on this memo

1. update `docs/discipline-utilities-baseline-proposal.md` so it matches the gauntlet verdict
2. if a future baseline is cut, fold only:
   - `root-cause-debugging`
   - `evidence-before-completion`
3. leave `test-first-development` out of that baseline unless a later cycle proves lower ceremony on ordinary implementation work

## Decision confidence

- `root-cause-debugging`: high
- `test-first-development`: medium-high
- `evidence-before-completion`: high

## Evidence anchors

- isolated-task logs: `docs/gauntlet-runs/discipline-utilities-v1/tasks/`
- pressure round: `docs/gauntlet-runs/discipline-utilities-v1/pressure-round.md`
- scorecards:
  - `docs/gauntlet-runs/discipline-utilities-v1/scorecards/root-cause-debugging.md`
  - `docs/gauntlet-runs/discipline-utilities-v1/scorecards/test-first-development.md`
  - `docs/gauntlet-runs/discipline-utilities-v1/scorecards/evidence-before-completion.md`
