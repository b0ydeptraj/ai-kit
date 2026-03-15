# A2-E

## Identity

- task-id: A2-E
- repo: pallets/itsdangerous
- repo slot: Track A
- skill-under-test: evidence-before-completion
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: evidence-before-completion
- target files: tests/test_itsdangerous/test_timed.py, src/itsdangerous/timed.py
- starting evidence: see frozen task matrix
- initial hypothesis: see frozen task matrix
- success condition: accept a completion claim only if the scoped proof is actually present.
- failure condition: approve a completion claim based on nearby or partial evidence.

## Baseline

- setup command: see calibration.md
- test command: see calibration.md
- lint or typing command: not run in this trial
- baseline status: 101 passed
- reproduction status: confirmed during Round 2 review

## Execution log

- exact commands run:
  - `uv run --group tests pytest tests/test_itsdangerous/test_timed.py -q`
  - `inspection of timed serializer tests for max_age/return_timestamp versus positional salt`

- exact files inspected:
  - `tests/test_itsdangerous/test_timed.py:101-115`
  - `src/itsdangerous/timed.py:55-80`


- false starts:
  - none
- pivot moments:
  - The key pivot was comparing the scope of the implied completion claim with the scope of the proof actually exercised.
- final explanation of what happened:
  - The suite proves max_age and return_timestamp behavior, but it does not prove legacy positional-salt compatibility. That gap is large enough that no completion claim around timed loading semantics is justified yet.

## Evidence

- command output that matters:
  - tests cover max_age and return_timestamp; no positional-salt coverage found
- test result before:
  - 101 passed
- test result after:
  - 101 passed
- proof that the behavior changed or stayed correct:
  - Evidence is insufficient for a compatibility-safe completion claim.
- regression evidence:
  - A change could fix one call style while silently breaking another without any test catching it.

## Skill evaluation

- how did the skill help:
  - It converted a green test suite into the correct verdict: not enough evidence for this specific claim.
- what would likely have happened without it:
  - Without the skill, the all-green suite could be misread as proof that timed serializer loading semantics are fully covered.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - high
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - broad for compatibility-sensitive review work

## Timing

- time-to-first-solid-hypothesis: ~2m
- time-to-first-valid-evidence: ~4m
- time-to-finish: ~5m

## Decision for this task

- result: completion blocked
- confidence: high
- baseline fold signal: positive

## Notes

- follow-up risk: any future implementation claim should reuse this proof boundary instead of broadening it by implication.
- unresolved questions: see the paired debugging or test-first task for this repo.
