# handoff-log

## Handoff entries
| From | To | Lane | Trigger | Artifact touched | Evidence linked | Expected return condition |
|---|---|---|---|---|---|---|
| workflow-router | cook | primary | route selected | workflow-state | none recorded | hub chosen |
| review-hub | workflow-router | primary | PR #100 merged to main | workflow-state, team-board, lane-registry, docs backlog note | main CI run `25729643395` | state refreshed and lane idle |
| review-hub | workflow-router | primary | PR #103 merged to main | workflow-state, team-board, lane-registry, differentiation note | main CI run `25922588929` | state refreshed and lane idle |

## Rules
- Every non-trivial handoff should update this log before the receiving skill starts work.
- Link to the authoritative artifact, not only a chat summary.
- If a handoff changes scope or ownership, update `workflow-state.md` and `lane-registry.md` in the same pass.
