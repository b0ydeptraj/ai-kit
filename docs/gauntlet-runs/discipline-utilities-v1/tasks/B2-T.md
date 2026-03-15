# B2-T

## Identity

- task-id: B2-T
- repo: encode/httpx
- repo slot: Track B
- skill-under-test: test-first-development
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: test-first-development
- target files: tests/test_auth.py, httpx/_auth.py
- starting evidence: see frozen task matrix
- initial hypothesis: encode the unsupported `auth-int` behavior before changing digest auth semantics.
- success condition: add a tight test that proves the current explicit unsupported path.
- failure condition: the seed is too entangled with broader digest auth flows.

## Baseline

- setup command: see calibration.md
- test command: `uv run --with-requirements requirements.txt pytest tests/test_auth.py -q`
- lint or typing command: not run in this trial
- baseline status: 8 passed
- reproduction status: confirmed during Round 2

## Execution log

- exact commands run:
  - `uv run --with-requirements requirements.txt pytest tests/test_auth.py -q -k auth_int_only_is_explicitly_unsupported`
- exact files inspected:
  - `httpx/_auth.py:267-305`
  - `tests/test_auth.py:120-147`
- false starts:
  - none
- pivot moments:
  - The trial stopped trying to guess whether support should be added and instead first locked the current unsupported behavior.
- final explanation of what happened:
  - The new test proves the `auth-int`-only path raises the explicit unsupported exception, which is the minimal contract needed before any behavior discussion.

## Evidence

- command output that matters:
  - `1 passed`
- test result before:
  - no narrow test for the `auth-int`-only branch
- test result after:
  - focused branch test passes
- proof that the behavior changed or stayed correct:
  - behavior stayed the same; the trial added coverage only.
- regression evidence:
  - no collateral auth failures in the targeted run.

## Skill evaluation

- how did the skill help:
  - It kept the repo from jumping directly into RFC interpretation or implementation changes without first pinning the current branch.
- what would likely have happened without it:
  - The next change could widen scope from one digest branch into the full auth stack.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - high
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - broad for protocol-heavy libraries

## Timing

- time-to-first-solid-hypothesis: ~2m
- time-to-first-valid-evidence: ~4m
- time-to-finish: ~5m

## Decision for this task

- result: focused green test added
- confidence: high
- baseline fold signal: positive

## Notes

- follow-up risk: any future implementation to support `auth-int` will need a new red test beyond this characterization.
- unresolved questions: none.
