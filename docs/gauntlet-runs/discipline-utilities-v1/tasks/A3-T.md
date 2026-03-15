# A3-T

## Identity

- task-id: A3-T
- repo: pallets-eco/blinker
- repo slot: Track A
- skill-under-test: test-first-development
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: test-first-development
- target files: tests/test_signals.py, src/blinker/base.py
- starting evidence: see frozen task matrix
- initial hypothesis: add the missing `ANY` sender regression before any behavior discussion.
- success condition: lock the currently implied behavior with a focused test.
- failure condition: the behavior cannot be observed independently from broader signal plumbing.

## Baseline

- setup command: see calibration.md
- test command: `uv run --group tests pytest tests/test_signals.py -q`
- lint or typing command: not run in this trial
- baseline status: 19 passed
- reproduction status: confirmed during Round 2

## Execution log

- exact commands run:
  - `uv run --group tests pytest tests/test_signals.py -q`
- exact files inspected:
  - `src/blinker/base.py:331-347`
  - `tests/test_signals.py:417-453`
- false starts:
  - none
- pivot moments:
  - none; the missing case was direct and isolated.
- final explanation of what happened:
  - The new test verifies that `receivers_for(ANY)` yields only receivers bound to `ANY`, which closes an obvious gap in the signal behavior contract.

## Evidence

- command output that matters:
  - `20 passed`
- test result before:
  - 19 passed
- test result after:
  - 20 passed
- proof that the behavior changed or stayed correct:
  - behavior stayed correct; the trial tightened coverage only.
- regression evidence:
  - full targeted signal suite still passes.

## Skill evaluation

- how did the skill help:
  - It forced the missing behavior to be codified before any speculative refactor.
- what would likely have happened without it:
  - The gap would remain implicit in code review rather than explicit in tests.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - high
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - broad for event systems and dispatch code

## Timing

- time-to-first-solid-hypothesis: ~2m
- time-to-first-valid-evidence: ~4m
- time-to-finish: ~5m

## Decision for this task

- result: focused green test added
- confidence: high
- baseline fold signal: positive

## Notes

- follow-up risk: low
- unresolved questions: none.
