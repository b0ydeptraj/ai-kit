# A2-D

## Identity

- task-id: A2-D
- repo: pallets/itsdangerous
- repo slot: Track A
- skill-under-test: root-cause-debugging
- round: Round 2 / single-skill trial complete
- evaluator: Codex
- date: 2026-03-14

## Task definition

- task family: root-cause-debugging
- target files: src/itsdangerous/timed.py, src/itsdangerous/serializer.py, tests/test_itsdangerous/test_timed.py
- starting evidence: see frozen task matrix
- initial hypothesis: see frozen task matrix
- success condition: reproduce or tightly explain the failure surface before proposing any fix.
- failure condition: the task collapses into speculation without a concrete explanation.

## Baseline

- setup command: see calibration.md
- test command: see calibration.md
- lint or typing command: not run in this trial
- baseline status: 101 passed
- reproduction status: confirmed during Round 2

## Execution log

- exact commands run:
  - `uv run --group tests pytest tests/test_itsdangerous/test_timed.py -q`
  - `Serializer vs TimedSerializer positional-salt repro via uv run python`

- exact files inspected:
  - `src/itsdangerous/timed.py:55-80`
  - `src/itsdangerous/serializer.py`
  - `tests/test_itsdangerous/test_timed.py`


- false starts:
  - The earlier hypothesis expected a TypeError; the actual failure mode is subtler: a positional-argument mismatch that ends in BadTimeSignature.
- pivot moments:
  - Comparing Serializer.loads(..., legacy-salt) with TimedSerializer.loads(..., legacy-salt) isolated the signature drift immediately.
- final explanation of what happened:
  - Serializer.loads still accepts positional salt, but TimedSerializer.loads interprets the second positional argument as max_age. The old call shape no longer means the same thing and fails signature validation.

## Evidence

- command output that matters:
  - Serializer positional salt works; TimedSerializer positional call fails with BadTimeSignature
- test result before:
  - 101 passed
- test result after:
  - 101 passed
- proof that the behavior changed or stayed correct:
  - Behavior stayed inconsistent; no code change was made.
- regression evidence:
  - Timed serializer tests remain green.

## Skill evaluation

- how did the skill help:
  - It prevented treating the issue as random signature failure and pinned it to the overloaded positional parameter contract.
- what would likely have happened without it:
  - Without the skill, this is easy to misclassify as a bad token or salt mismatch.
- did it reduce guessing:
  - yes
- did it improve evidence quality:
  - high
- did it add unwanted ceremony:
  - low
- would this help most repos or only some repos:
  - broad for compatibility-sensitive APIs

## Timing

- time-to-first-solid-hypothesis: ~3m
- time-to-first-valid-evidence: ~5m
- time-to-finish: ~7m

## Decision for this task

- result: root-cause confirmed
- confidence: high
- baseline fold signal: positive

## Notes

- follow-up risk: none for the trial itself; any future implementation work belongs in a separate fix task.
- unresolved questions: see the paired test-first or evidence-before-completion task for this repo.
