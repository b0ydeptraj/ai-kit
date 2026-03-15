# C1-E

## Identity

- task-id: C1-E
- repo: sindresorhus/ky
- repo slot: Track C
- skill-under-test: evidence-before-completion
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: evidence-before-completion
- target files: source/types/ResponsePromise.ts, type tests
- starting evidence: see frozen task matrix
- initial hypothesis: see frozen task matrix
- success condition: accept a completion claim only if the scoped proof is actually present.
- failure condition: approve a completion claim based on nearby or partial evidence.

## Baseline

- setup command: see calibration.md
- test command: see calibration.md
- lint or typing command: not run in this trial
- baseline status: 3 passed, 1 known failure
- reproduction status: confirmed during Round 2 review

## Execution log

- exact commands run:
  - `npm install`
  - `npx ava test/methods.ts`
  - `inspection of ResponsePromise typing references and test tree`

- exact files inspected:
  - `source/types/ResponsePromise.ts:21-65`
  - `test/headers.ts`
  - `distribution/types/ResponsePromise.d.ts`


- false starts:
  - none
- pivot moments:
  - The key pivot was comparing the scope of the implied completion claim with the scope of the proof actually exercised.
- final explanation of what happened:
  - There are usage examples for generic json typing, but no dedicated proof in this trial that a typing change would preserve all intended call sites. Completion evidence for a ResponsePromise.json typing change is therefore insufficient.

## Evidence

- command output that matters:
  - typing references found; no dedicated completion-grade type assertion for the proposed change was executed
- test result before:
  - 3 passed, 1 known failure
- test result after:
  - 3 passed, 1 known failure
- proof that the behavior changed or stayed correct:
  - Evidence is insufficient for a typing-change completion claim.
- regression evidence:
  - A subtle typing change could improve one usage style while regressing another generic call shape.

## Skill evaluation

- how did the skill help:
  - It prevented docs and examples from being mistaken for proof of type-level compatibility.
- what would likely have happened without it:
  - Without the skill, a reviewer might accept a typing tweak because runtime tests are green.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - high
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - broad for TS typing review work

## Timing

- time-to-first-solid-hypothesis: ~3m
- time-to-first-valid-evidence: ~5m
- time-to-finish: ~6m

## Decision for this task

- result: completion blocked
- confidence: high
- baseline fold signal: positive

## Notes

- follow-up risk: any future implementation claim should reuse this proof boundary instead of broadening it by implication.
- unresolved questions: see the paired debugging or test-first task for this repo.
