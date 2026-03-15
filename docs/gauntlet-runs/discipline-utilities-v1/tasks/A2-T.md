# A2-T

## Identity

- task-id: A2-T
- repo: pallets/itsdangerous
- repo slot: Track A
- skill-under-test: test-first-development
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: test-first-development
- target files: tests/test_itsdangerous/test_timed.py, src/itsdangerous/timed.py
- starting evidence: see frozen task matrix
- initial hypothesis: write the legacy positional-salt compatibility expectation as a red test before debating API intent.
- success condition: produce a failing test that pins the compatibility drift to one call shape.
- failure condition: the compatibility concern cannot be expressed as a stable test.

## Baseline

- setup command: see calibration.md
- test command: `uv run --group tests pytest tests/test_itsdangerous/test_timed.py -q`
- lint or typing command: not run in this trial
- baseline status: 101 passed
- reproduction status: confirmed during Round 2

## Execution log

- exact commands run:
  - `uv run --group tests pytest tests/test_itsdangerous/test_timed.py -q -k legacy_positional_salt_compatibility`
- exact files inspected:
  - `tests/test_itsdangerous/test_timed.py:96-120`
  - `src/itsdangerous/timed.py:55-80`
  - `src/itsdangerous/serializer.py:328-343`
- false starts:
  - none beyond the earlier assumption that the failure might be a plain `TypeError`.
- pivot moments:
  - The test was written against the historical call shape first, then run to discover the real failure mode.
- final explanation of what happened:
  - The added compatibility test fails with `BadTimeSignature`, which is exactly the point of the trial: it captures the contract drift before any fix or policy decision.

## Evidence

- command output that matters:
  - the new targeted test fails with `itsdangerous.exc.BadTimeSignature`
- test result before:
  - no explicit coverage for positional salt compatibility on timed serializers
- test result after:
  - red by design
- proof that the behavior changed or stayed correct:
  - no production code changed; the trial only added failing evidence.
- regression evidence:
  - existing timed serializer coverage stayed intact aside from the intentional new failure.

## Skill evaluation

- how did the skill help:
  - It converted a vague compatibility argument into a precise failing assertion.
- what would likely have happened without it:
  - The issue would be argued abstractly, or worse, ?fixed? without a locked behavior target.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - high
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - broad for public APIs and compatibility-sensitive libraries

## Timing

- time-to-first-solid-hypothesis: ~2m
- time-to-first-valid-evidence: ~4m
- time-to-finish: ~6m

## Decision for this task

- result: red test captured
- confidence: high
- baseline fold signal: strong-positive

## Notes

- follow-up risk: any implementation decision now has to choose between preserving or explicitly rejecting the legacy call shape.
- unresolved questions: none for the trial itself.
