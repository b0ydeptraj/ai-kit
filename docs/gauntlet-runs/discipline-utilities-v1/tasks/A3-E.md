# A3-E

## Identity

- task-id: A3-E
- repo: pallets-eco/blinker
- repo slot: Track A
- skill-under-test: evidence-before-completion
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: evidence-before-completion
- target files: tests/test_signals.py, src/blinker/base.py
- starting evidence: see frozen task matrix
- initial hypothesis: see frozen task matrix
- success condition: accept a completion claim only if the scoped proof is actually present.
- failure condition: approve a completion claim based on nearby or partial evidence.

## Baseline

- setup command: see calibration.md
- test command: see calibration.md
- lint or typing command: not run in this trial
- baseline status: 19 passed
- reproduction status: confirmed during Round 2 review

## Execution log

- exact commands run:
  - `uv run --group tests pytest tests/test_signals.py -q`
  - `inspection of ANY/weak/receiver_connected coverage in test_signals.py`

- exact files inspected:
  - `tests/test_signals.py:39-127`
  - `tests/test_signals.py:423-449`
  - `src/blinker/base.py:128-137,336`


- false starts:
  - none
- pivot moments:
  - The key pivot was comparing the scope of the implied completion claim with the scope of the proof actually exercised.
- final explanation of what happened:
  - The suite has useful weak-ref and ANY-sender coverage, but it still lacks the exact `receivers_for(ANY)` TODO path and the TypeError cleanup branch. Completion evidence for signal behavior changes is therefore incomplete.

## Evidence

- command output that matters:
  - ANY and weak-ref tests exist; the exact TODO paths remain unproven
- test result before:
  - 19 passed
- test result after:
  - 19 passed
- proof that the behavior changed or stayed correct:
  - Evidence is insufficient to call a signal-behavior change complete.
- regression evidence:
  - A change could desynchronize weak cleanup and ANY-sender behavior without the suite noticing.

## Skill evaluation

- how did the skill help:
  - It forced the review to ask for the missing proof instead of accepting adjacent tests as enough.
- what would likely have happened without it:
  - Without the skill, nearby coverage could be mistaken for direct proof of the missing edge cases.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - high
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - broad for event-system review gates

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
