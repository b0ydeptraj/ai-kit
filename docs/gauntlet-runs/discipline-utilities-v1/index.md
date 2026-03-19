# discipline-utilities-v1

## Status

- round-0: complete
- round-1-calibration: complete
- round-2-single-skill-trials: complete
- round-3-pressure-round: complete
- round-4-decision-round: complete
- evaluator: Codex
- workspace: `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot`
- run-date: `2026-03-14`

## Round 0 summary

- `python python_kit.py --list-skills` passed and listed `discipline-utilities` with exactly 3 skills.
- Clean temp-generation passed for `round2`, `round3`, `round4`, and `discipline-utilities`.
- Overlay gating checks passed:
  - `round2` did not emit `discipline-utilities` skills or docs.
  - `round3` did not emit `discipline-utilities` skills or docs.
  - `round4` kept round4 topology/state/docs but did not leak `discipline-utilities` content.
  - `discipline-utilities` emitted only the 3 overlay skills plus 5 overlay docs.
- Runtime wiring checks passed in the live repo for:
  - `debug-hub -> root-cause-debugging`
  - `developer -> test-first-development`
  - `test-hub -> evidence-before-completion`
  - `qa-governor -> evidence-before-completion`
  - `team -> parallel-execution.md`
  - `plan-hub -> planning-discipline.md`
  - `review-hub -> review-loop.md` and `branch-completion.md`
  - `scrum-master -> planning-discipline.md`
  - `execution-loop -> root-cause-debugging` and `evidence-before-completion`

## Round 1 summary

- 12/12 repos calibrated.
- No repo replacement was required.
- One repo (`date-fns/date-fns`) required submodule initialization before it became usable.
- One repo (`sindresorhus/p-limit`) required a scope adjustment inside the same repo because the original Node-20-specific skip is not observable on Node 22.
- One repo (`pallets-eco/blinker`) had a prior pilot-only local test addition; it was restored before calibration.

## Repo status overview

| Repo | Slot | Calibration status | Notes |
|---|---|---|---|
| `pallets/click` | Track A | `ready` | All three click tasks retained. A1-E stays conditional because there is no candidate fix under review yet. |
| `pallets/itsdangerous` | Track A | `ready` | All three tasks retained. |
| `pallets-eco/blinker` | Track A | `ready` | Restored a prior pilot-only local test addition before calibration, then kept all three tasks. |
| `pallets/markupsafe` | Track A | `conditional` | A4-D and A4-E retained. A4-T stays conditional because the useful branch is packaging/import-path sensitive. |
| `httpie/cli` | Track B | `conditional` | B1-D retained. B1-T and B1-E remain conditional until the exact redirect/error branch under review is chosen. |
| `encode/httpx` | Track B | `ready` | All three tasks retained. |
| `pallets/flask` | Track B | `conditional` | All three Flask tasks retained but kept conditional because the missing-dependency path is environment dependent. |
| `fastapi/fastapi` | Track B | `ready` | All three tasks retained. |
| `sindresorhus/ky` | Track C | `conditional` | C1-D and C1-T retained. C1-E remains conditional because the `ResponsePromise.json` typing question is review-driven rather than runtime-failing today. |
| `axios/axios` | Track C | `conditional` | C2-T and C2-E retained as ready. C2-D remains conditional because the skip-based seed is split across legacy runner paths. |
| `sindresorhus/p-limit` | Track C | `adjusted` | Kept the same files and skill family, but reframed C3-D/C3-T around `rejectOnClear` semantics instead of the Node-20-only skip gate. |
| `date-fns/date-fns` | Track C | `ready` | All three tasks retained. |

## Round 2 summary

- Completed all `36/36` isolated task logs.
- `root-cause-debugging`: `12/12` positive fold signals.
- `test-first-development`: `12/12` positive fold signals, but with non-trivial baseline-noise differences across tasks.
- `evidence-before-completion`: `12/12` positive fold signals, including one narrow approval case (`C3-E`) and 11 justified blocks.

## Round 3 summary

- Re-ran 9 representative pressure cases:
  - `3` for `root-cause-debugging + debug-hub`
  - `3` for `test-first-development + developer + test-hub`
  - `3` for `evidence-before-completion + qa-governor + review-hub`
- Pressure-round result:
  - `root-cause-debugging`: strong promotion signal
  - `test-first-development`: positive signal, but still noisy for baseline use
  - `evidence-before-completion`: strongest promotion signal

## Round 4 summary

- Final scorecards completed for all three skills.
- Final verdicts:
  - `root-cause-debugging` -> `fold-next-baseline`
  - `test-first-development` -> `keep-overlay-next-cycle`
  - `evidence-before-completion` -> `fold-next-baseline`


## Output index

- `calibration.md` contains the locked repo-by-repo baseline.
- `tasks/` contains the full `36` task logs.
- `pressure-round.md` contains the 9-case workflow-pressure rerun.
- `scorecards/` contains the per-skill Round 4 verdicts.
- `decision-memo.md` contains the final fold / keep decisions.

