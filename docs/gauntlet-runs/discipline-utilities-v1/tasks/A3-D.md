# A3-D

## Identity

- task-id: A3-D
- repo: pallets-eco/blinker
- repo slot: Track A
- skill-under-test: root-cause-debugging
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: root-cause-debugging
- target files: src/blinker/base.py, tests/test_signals.py
- starting evidence: see frozen task matrix
- initial hypothesis: see frozen task matrix
- success condition: reproduce or tightly explain the failure surface before proposing any fix.
- failure condition: the task collapses into speculation without a concrete explanation.

## Baseline

- setup command: see calibration.md
- test command: see calibration.md
- lint or typing command: not run in this trial
- baseline status: 19 passed
- reproduction status: confirmed during Round 2

## Execution log

- exact commands run:
  - `uv run --group tests pytest tests/test_signals.py -q`
  - `malformed receiver_connected listener repro via uv run python`

- exact files inspected:
  - `src/blinker/base.py:128-137`
  - `tests/test_signals.py`


- false starts:
  - The first repro used a RuntimeError and did not hit the disconnect path; the code only special-cases TypeError.
- pivot moments:
  - Switching to a listener with the wrong signature hit the actual branch under the TODO.
- final explanation of what happened:
  - When receiver_connected.send raises TypeError, Signal.connect disconnects the attempted receiver and re-raises. The missing test is about that cleanup behavior, not generic signal exceptions.

## Evidence

- command output that matters:
  - TypeError raised and receiver_list became empty
- test result before:
  - 19 passed
- test result after:
  - 19 passed
- proof that the behavior changed or stayed correct:
  - Behavior stayed as implemented; no code change was made.
- regression evidence:
  - Existing signal tests stayed green.

## Skill evaluation

- how did the skill help:
  - It narrowed the seed from any exception path to the exact TypeError cleanup branch.
- what would likely have happened without it:
  - Without the skill, the investigation would likely stop at any exception path and miss the branch-specific disconnect semantics.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - high
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - broad for callback-signature bugs in event systems

## Timing

- time-to-first-solid-hypothesis: ~2m
- time-to-first-valid-evidence: ~4m
- time-to-finish: ~6m

## Decision for this task

- result: root-cause confirmed
- confidence: high
- baseline fold signal: positive

## Notes

- follow-up risk: none for the trial itself; any future implementation work belongs in a separate fix task.
- unresolved questions: see the paired test-first or evidence-before-completion task for this repo.
