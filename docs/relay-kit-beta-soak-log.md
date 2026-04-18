# Relay-kit beta soak log

Track real-project soak checkpoints before broader rollout.

## Required run shape

- Run on at least 2 real target projects.
- Use canonical command path (`relay_kit.py` / public `relay-kit`).
- Keep the same baseline bundle across runs (`baseline`).
- Record pass/fail and missing output directories.

## Recommended command

```bash
python scripts/soak_beta.py /path/to/project-a /path/to/project-b --append-report --json
```

## Pass criteria for Beta gate

- 0 failed projects in a checkpoint run.
- Each project has all runtime outputs:
  - `.claude/skills`
  - `.agent/skills`
  - `.codex/skills`
  - `.relay-kit/contracts`
  - `.relay-kit/state`
  - `.relay-kit/docs`
  - `.relay-kit/references`
- `scripts/validate_runtime.py` still passes at repo root after soak.

## Soak checkpoint 2026-04-17 15:39:50

| Project | Status | Duration (s) | Missing dirs |
|---|---|---:|---|
| `C:\Users\b0ydeptrai\OneDrive\Documents\prompt-genius` | `pass` | `0.13` | - |
| `C:\Users\b0ydeptrai\OneDrive\Documents\fakeinfo-fix` | `pass` | `0.11` | - |
| `C:\Users\b0ydeptrai\OneDrive\Documents\donut` | `pass` | `0.11` | - |

## Soak checkpoint 2026-04-18 10:09:35

| Project | Status | Duration (s) | Missing dirs |
|---|---|---:|---|
| `C:\Users\b0ydeptrai\OneDrive\Documents\prompt-genius` | `pass` | `0.15` | - |
| `C:\Users\b0ydeptrai\OneDrive\Documents\fakeinfo-fix` | `pass` | `0.13` | - |
| `C:\Users\b0ydeptrai\OneDrive\Documents\donut` | `pass` | `0.12` | - |
| `D:\Download\VIN-Pair-Tool` | `pass` | `0.1` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-1` | `pass` | `0.1` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-2` | `pass` | `0.1` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-3` | `pass` | `0.09` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-4` | `pass` | `0.09` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-5` | `pass` | `0.1` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-6` | `pass` | `0.11` | - |

## Soak checkpoint 2026-04-18 10:09:37

| Project | Status | Duration (s) | Missing dirs |
|---|---|---:|---|
| `C:\Users\b0ydeptrai\OneDrive\Documents\prompt-genius` | `pass` | `0.1` | - |
| `C:\Users\b0ydeptrai\OneDrive\Documents\fakeinfo-fix` | `pass` | `0.09` | - |
| `C:\Users\b0ydeptrai\OneDrive\Documents\donut` | `pass` | `0.09` | - |
| `D:\Download\VIN-Pair-Tool` | `pass` | `0.09` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-1` | `pass` | `0.07` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-2` | `pass` | `0.07` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-3` | `pass` | `0.08` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-4` | `pass` | `0.09` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-5` | `pass` | `0.07` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-6` | `pass` | `0.07` | - |

## Soak checkpoint 2026-04-18 10:09:39

| Project | Status | Duration (s) | Missing dirs |
|---|---|---:|---|
| `C:\Users\b0ydeptrai\OneDrive\Documents\prompt-genius` | `pass` | `0.09` | - |
| `C:\Users\b0ydeptrai\OneDrive\Documents\fakeinfo-fix` | `pass` | `0.09` | - |
| `C:\Users\b0ydeptrai\OneDrive\Documents\donut` | `pass` | `0.08` | - |
| `D:\Download\VIN-Pair-Tool` | `pass` | `0.07` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-1` | `pass` | `0.07` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-2` | `pass` | `0.07` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-3` | `pass` | `0.08` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-4` | `pass` | `0.09` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-5` | `pass` | `0.07` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-6` | `pass` | `0.07` | - |

## Soak checkpoint 2026-04-18 10:09:41

| Project | Status | Duration (s) | Missing dirs |
|---|---|---:|---|
| `C:\Users\b0ydeptrai\OneDrive\Documents\prompt-genius` | `pass` | `0.1` | - |
| `C:\Users\b0ydeptrai\OneDrive\Documents\fakeinfo-fix` | `pass` | `0.09` | - |
| `C:\Users\b0ydeptrai\OneDrive\Documents\donut` | `pass` | `0.09` | - |
| `D:\Download\VIN-Pair-Tool` | `pass` | `0.09` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-1` | `pass` | `0.07` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-2` | `pass` | `0.07` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-3` | `pass` | `0.07` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-4` | `pass` | `0.07` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-5` | `pass` | `0.07` | - |
| `D:\relay-kit-checkpoint\projects\synthetic-proj-6` | `pass` | `0.07` | - |
