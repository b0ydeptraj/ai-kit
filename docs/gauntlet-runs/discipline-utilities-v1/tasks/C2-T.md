# C2-T

## Identity

- task-id: C2-T
- repo: axios/axios
- repo slot: Track C
- skill-under-test: test-first-development
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: test-first-development
- target files: tests/unit/composeSignals.test.js, lib/helpers/composeSignals.js
- starting evidence: see frozen task matrix
- initial hypothesis: add a focused abort-message regression before changing signal composition behavior.
- success condition: lock one concrete composeSignals branch with a targeted test.
- failure condition: the behavior depends on larger adapter suites.

## Baseline

- setup command: see calibration.md
- test command: `npx vitest run tests/unit/composeSignals.test.js tests/unit/axiosHeaders.test.js`
- lint or typing command: not run in this trial
- baseline status: 40 passed across the calibration subset
- reproduction status: confirmed during Round 2

## Execution log

- exact commands run:
  - `npx vitest run tests/unit/composeSignals.test.js`
- exact files inspected:
  - `tests/unit/composeSignals.test.js:1-36`
  - `lib/helpers/composeSignals.js`
- false starts:
  - none
- pivot moments:
  - The trial ignored skipped browser/adapter branches and instead locked a small composeSignals behavior that is fully runnable on this machine.
- final explanation of what happened:
  - The new test verifies that an abort propagated from a source signal preserves the original error message. That keeps the signal-composition contract concrete.

## Evidence

- command output that matters:
  - `4 passed`
- test result before:
  - no dedicated message-preservation regression in the modern composeSignals suite
- test result after:
  - composeSignals file passes with the new coverage
- proof that the behavior changed or stayed correct:
  - behavior stayed correct; the trial added coverage.
- regression evidence:
  - targeted composeSignals suite remains green.

## Skill evaluation

- how did the skill help:
  - It converted a broad ?adapter regression? seed into one executable signal-path check.
- what would likely have happened without it:
  - The next change might chase browser/node parity without first locking a core helper behavior.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - medium-high
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - broad for cancellation-heavy clients

## Timing

- time-to-first-solid-hypothesis: ~3m
- time-to-first-valid-evidence: ~6m
- time-to-finish: ~7m

## Decision for this task

- result: focused green test added
- confidence: high
- baseline fold signal: positive

## Notes

- follow-up risk: adapter-level parity still needs separate evidence if behavior changes span both browser and node.
- unresolved questions: none.
