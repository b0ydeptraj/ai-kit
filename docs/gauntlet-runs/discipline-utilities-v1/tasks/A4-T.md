# A4-T

## Identity

- task-id: A4-T
- repo: pallets/markupsafe
- repo slot: Track A
- skill-under-test: test-first-development
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: test-first-development
- target files: tests/test_ext_init.py, tests/conftest.py
- starting evidence: see frozen task matrix
- initial hypothesis: tighten the distinction between ?speedups importable? and ?speedups active? before any import-path or packaging change.
- success condition: add explicit coverage for the inactive-but-present state.
- failure condition: the distinction cannot be exercised cleanly on the pilot machine.

## Baseline

- setup command: see calibration.md
- test command: `uv run --group tests pytest tests/test_ext_init.py -q -rs`
- lint or typing command: not run in this trial
- baseline status: 1 passed, 1 skipped
- reproduction status: confirmed during Round 2

## Execution log

- exact commands run:
  - `uv run --group tests pytest tests/test_ext_init.py -q -rs`
- exact files inspected:
  - `tests/test_ext_init.py:14-32`
  - `tests/conftest.py:29-39`
  - `src/markupsafe/__init__.py`
- false starts:
  - none
- pivot moments:
  - Inspecting the autouse fixture made it clear that the missing coverage was the inactive-yet-importable path, not the extension-init path itself.
- final explanation of what happened:
  - The new test documents that `_speedups` can be present while `markupsafe._escape_inner` still points at the native fallback. That sharpens the contract around the existing skip.

## Evidence

- command output that matters:
  - `3 passed, 1 skipped`
- test result before:
  - 1 passed, 1 skipped
- test result after:
  - 3 passed, 1 skipped
- proof that the behavior changed or stayed correct:
  - behavior stayed the same; the trial added coverage for the mixed state.
- regression evidence:
  - the original extension-init pass/skip behavior remains intact.

## Skill evaluation

- how did the skill help:
  - It pushed the repo from environment-dependent interpretation to explicit coverage of the fallback path.
- what would likely have happened without it:
  - Any later packaging change would still argue from skip reasons instead of a locked behavior check.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - medium-high
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - most relevant to optional-extension projects

## Timing

- time-to-first-solid-hypothesis: ~3m
- time-to-first-valid-evidence: ~6m
- time-to-finish: ~8m

## Decision for this task

- result: focused green test added
- confidence: medium-high
- baseline fold signal: positive

## Notes

- follow-up risk: the local build produced `_speedups.cp311-win_amd64.pyd`; treat that as environment artifact, not product evidence by itself.
- unresolved questions: none for the trial.
