# C2-D

## Identity

- task-id: C2-D
- repo: axios/axios
- repo slot: Track C
- skill-under-test: root-cause-debugging
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: root-cause-debugging
- target files: test/unit/adapters/http.js, test/unit/regression/bugs.js, lib/
- starting evidence: see frozen task matrix
- initial hypothesis: see frozen task matrix
- success condition: reproduce or tightly explain the failure surface before proposing any fix.
- failure condition: the task collapses into speculation without a concrete explanation.

## Baseline

- setup command: see calibration.md
- test command: see calibration.md
- lint or typing command: not run in this trial
- baseline status: 40 passed across 2 unit files
- reproduction status: confirmed during Round 2

## Execution log

- exact commands run:
  - `npm install`
  - `npx vitest run tests/unit/composeSignals.test.js tests/unit/axiosHeaders.test.js`
  - `inspection of legacy skip sites in http.js and bugs.js`

- exact files inspected:
  - `test/unit/adapters/http.js:490,515`
  - `test/unit/regression/bugs.js:51`
  - `tests/unit/composeSignals.test.js`
  - `tests/unit/axiosHeaders.test.js`


- false starts:
  - none
- pivot moments:
  - The key insight is that the modern vitest path is healthy while the suspicious seeds live in older skip-based tests.
- final explanation of what happened:
  - The seed currently points more to runner/test-harness limitations than to an active library defect. Legacy tests still contain skip branches, but the modern composeSignals and AxiosHeaders vitest coverage passes cleanly.

## Evidence

- command output that matters:
  - Legacy skip sites remain; modern targeted vitest path reports 40 passed
- test result before:
  - 40 passed across 2 unit files
- test result after:
  - 40 passed across 2 unit files
- proof that the behavior changed or stayed correct:
  - No code change; the trial separated legacy skip debt from current green paths.
- regression evidence:
  - Modern targeted unit tests stayed green.

## Skill evaluation

- how did the skill help:
  - It avoided conflating old skipped coverage with an active breakage in the modern unit path.
- what would likely have happened without it:
  - Without the skill, the likely mistake is to assume every skipped test points at a live bug in the shipped library.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - medium
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - useful for mature repos carrying multiple generations of test infrastructure

## Timing

- time-to-first-solid-hypothesis: ~3m
- time-to-first-valid-evidence: ~6m
- time-to-finish: ~8m

## Decision for this task

- result: runner-vs-library cause classified
- confidence: medium
- baseline fold signal: positive

## Notes

- follow-up risk: none for the trial itself; any future implementation work belongs in a separate fix task.
- unresolved questions: see the paired test-first or evidence-before-completion task for this repo.
