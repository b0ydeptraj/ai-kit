# B3-T

## Identity

- task-id: B3-T
- repo: pallets/flask
- repo slot: Track B
- skill-under-test: test-first-development
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: test-first-development
- target files: src/flask/app.py, tests/test_async_optional.py
- starting evidence: see frozen task matrix
- initial hypothesis: add a minimal regression test for the missing-`asgiref` path before any async-support change.
- success condition: prove the runtime error contract when the optional dependency is absent.
- failure condition: the path cannot be isolated without breaking the rest of the async suite.

## Baseline

- setup command: see calibration.md
- test command: `uv run --group tests pytest tests/test_async.py tests/test_config.py tests/test_reqctx.py -q`
- lint or typing command: not run in this trial
- baseline status: 41 passed
- reproduction status: confirmed during Round 2

## Execution log

- exact commands run:
  - `uv run --group tests pytest tests/test_async_optional.py -q`
- exact files inspected:
  - `src/flask/app.py:1079-1100`
  - `tests/test_async.py:11`
  - `tests/test_async_optional.py:1-19`
- false starts:
  - The original matrix pointed at config/request-context files, but calibration showed the sharper seed was the optional dependency branch in `async_to_sync`.
- pivot moments:
  - Creating a standalone test file avoided the global `importorskip("asgiref")` in the async suite.
- final explanation of what happened:
  - The new test monkeypatches import resolution so `asgiref.sync` is unavailable and confirms Flask raises the documented runtime error immediately.

## Evidence

- command output that matters:
  - `1 passed`
- test result before:
  - no direct coverage for the missing-async-extra branch
- test result after:
  - focused branch test passes
- proof that the behavior changed or stayed correct:
  - behavior stayed the same; the trial added missing coverage.
- regression evidence:
  - the targeted optional-dependency check passes independently of the async suite.

## Skill evaluation

- how did the skill help:
  - It forced the optional dependency contract to be expressed as code instead of remaining implicit in the implementation.
- what would likely have happened without it:
  - Async-path changes could ship without any proof that the missing-dependency experience remains correct.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - high
- did it add unwanted ceremony:
  - low-medium because it required a dedicated file to bypass suite-level skips
- would this help most repos or only some repos:
  - broad for optional-dependency features

## Timing

- time-to-first-solid-hypothesis: ~4m
- time-to-first-valid-evidence: ~8m
- time-to-finish: ~10m

## Decision for this task

- result: focused green test added
- confidence: high
- baseline fold signal: positive

## Notes

- follow-up risk: any async behavior change still needs the normal async suite plus this missing-extra check.
- unresolved questions: none for the pilot scope.
