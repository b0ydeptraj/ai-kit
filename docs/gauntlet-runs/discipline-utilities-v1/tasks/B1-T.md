# B1-T

## Identity

- task-id: B1-T
- repo: httpie/cli
- repo slot: Track B
- skill-under-test: test-first-development
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: test-first-development
- target files: httpie/core.py, tests/test_errors.py
- starting evidence: see frozen task matrix
- initial hypothesis: lock the generic unexpected-error path with a test before touching core error handling.
- success condition: prove the fallback handler contract through a focused command-level test.
- failure condition: the path cannot be exercised without booting a much larger CLI scenario.

## Baseline

- setup command: see calibration.md
- test command: `uv run --with-editable ".[test]" pytest tests/test_errors.py -q`
- lint or typing command: not run in this trial
- baseline status: 12 passed
- reproduction status: confirmed during Round 2

## Execution log

- exact commands run:
  - `uv run --with-editable ".[test]" pytest tests/test_errors.py -q -k unexpected_error_falls_back_to_generic_handler`
- exact files inspected:
  - `httpie/core.py:165-182`
  - `tests/test_errors.py:1-80`
- false starts:
  - none
- pivot moments:
  - Instead of chasing redirect plumbing, the trial narrowed to the exact branch that distinguishes known request errors from unexpected exceptions.
- final explanation of what happened:
  - The added test proves an unexpected `ValueError` is still surfaced through the generic handler and mapped to `ExitStatus.ERROR`.

## Evidence

- command output that matters:
  - `1 passed, 12 deselected`
- test result before:
  - no dedicated test for the generic fallback branch
- test result after:
  - focused fallback test passes
- proof that the behavior changed or stayed correct:
  - behavior stayed correct; the trial only locked the path with coverage.
- regression evidence:
  - no collateral failures in the targeted error suite.

## Skill evaluation

- how did the skill help:
  - It turned a broad ?error handling? concern into one narrow branch with executable proof.
- what would likely have happened without it:
  - Future cleanup could collapse expected and unexpected paths without anyone noticing.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - high
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - broad for CLI or service error boundaries

## Timing

- time-to-first-solid-hypothesis: ~3m
- time-to-first-valid-evidence: ~6m
- time-to-finish: ~8m

## Decision for this task

- result: focused green test added
- confidence: high
- baseline fold signal: positive

## Notes

- follow-up risk: the redirect/error interaction still deserves separate workflow testing, but the generic fallback is now locked.
- unresolved questions: none for this trial.
