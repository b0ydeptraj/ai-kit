# Relay-kit vs GSD flow matrix (2026-04-02)

> Historical comparison note: produced during pre-cutover hardening and retained for architectural context.


This note compares Relay-kit against:

- https://github.com/gsd-build/gsd-2
- https://github.com/gsd-build/get-shit-done

Goal: identify equivalent flows already present in Relay-kit and tighten them without adding new skills.

## Flow equivalence

| GSD concept | Relay-kit equivalent | Status before | Status now |
|---|---|---|---|
| `map-codebase` style reconnaissance | `scout-hub` + `repo-map` + `project-architecture` | Present | Tightened with freshness + impact emphasis |
| discuss before planning (lock assumptions) | `brainstorm-hub` / `analyst` / `plan-hub` | Partial | Tightened by assumption-lock rule in `plan-hub` |
| plan into small executable units | `scrum-master` stories + `tech-spec` | Present | Tightened with `depends_on`, `parallel-safe`, wave placement |
| dependency-aware wave execution | `team` + `cook` lane orchestration | Partial | Tightened with explicit `wave_id` + `depends_on` gate |
| context rot mitigation | `context-continuity` + `memory-search` | Present | Already strong (kept) |
| no fake completion claims | `evidence-before-completion` + `qa-governor` | Present | Tightened with no-op completion guard (no delta/no evidence) |
| implementation loop discipline | `execution-loop` | Present | Tightened with per-cycle objective/file expectation rule |

## What changed in this batch

1. Routing/orchestration discipline:
   - `workflow-router` now requires explicit lane mode (`discovery`, `planning`, `implementation`, `verification`).
   - Existing-codebase guidance now favors `scout-hub` + `repo-map` before deeper planning when boundaries are unclear.

2. Parallel execution discipline:
   - `team` now enforces wave-based coordination (`depends_on`, `wave_id`, wave gate before next wave).
   - `team` now rejects lane completion claims with no artifact delta and no verification evidence.

3. Planning/slicing discipline:
   - `plan-hub` now requires assumption lock before slicing and dependency metadata in plan outputs.
   - `scrum-master` stories now require `depends_on`, `parallel-safe`, and wave placement clarity.

4. Completion evidence discipline:
   - `execution-loop` now rejects code-change completion claims when there is no file delta and no verification output.
   - `evidence-before-completion` now explicitly checks artifact delta presence for code-change claims.

## Out of scope for this batch

- No new skills created.
- No topology or bundle rename.
- No `.ai-kit` -> `.relay-kit` physical rename in this phase.

