# C3-T

## Identity

- task-id: C3-T
- repo: sindresorhus/p-limit
- repo slot: Track C
- skill-under-test: test-first-development
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: test-first-development
- target files: test.js, index.js
- starting evidence: see frozen task matrix
- initial hypothesis: add a queue-clear rejection test that is less coupled to the current environment-specific skip.
- success condition: encode the rejection semantics directly, without depending on `throwsAsync` behavior.
- failure condition: the only runnable evidence remains tied to the original skip.

## Baseline

- setup command: see calibration.md
- test command: `npx ava test.js`
- lint or typing command: not run in this trial
- baseline status: 21 passed
- reproduction status: confirmed during Round 2

## Execution log

- exact commands run:
  - `npx ava test.js --match="clearQueue rejectOnClear exposes AbortError without throwsAsync coupling"`
- exact files inspected:
  - `test.js:197-218`
  - `index.js`
- false starts:
  - none
- pivot moments:
  - The trial deliberately removed coupling to AVA's async assertion helper and asserted the library outcome instead.
- final explanation of what happened:
  - The new test proves `clearQueue` rejects queued work with `AbortError` even without the original helper pattern. That isolates library semantics from runner quirks.

## Evidence

- command output that matters:
  - `1 test passed`
- test result before:
  - only the environment-sensitive skip covered this area indirectly
- test result after:
  - focused semantics test passes
- proof that the behavior changed or stayed correct:
  - behavior stayed correct; coverage now targets the library surface directly.
- regression evidence:
  - no collateral failure in the targeted run.

## Skill evaluation

- how did the skill help:
  - It forced the queue-clear behavior to be specified directly instead of leaning on a flaky harness shape.
- what would likely have happened without it:
  - The issue might stay classified as ?Node 20 weirdness? rather than a library contract question.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - high
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - broad for async queue and concurrency libraries

## Timing

- time-to-first-solid-hypothesis: ~3m
- time-to-first-valid-evidence: ~5m
- time-to-finish: ~6m

## Decision for this task

- result: focused green test added
- confidence: high
- baseline fold signal: positive

## Notes

- follow-up risk: cross-version Node behavior should still be checked separately if the library changes error types.
- unresolved questions: none.
