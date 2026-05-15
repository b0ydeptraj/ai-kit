# lane-registry

## Usage rules
- One lane owns one artifact lock at a time.
- Record the narrowest useful lock scope, not whole-repo ownership by default.
- Release or reassign the lock before a different lane edits the same artifact section.

## Active lanes
| Lane | Owner skill | Source orchestrator | Target hub | Primary artifact | Lock scope | depends_on | wave_id | resume_condition | Merge prerequisite | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| primary | unassigned | workflow-router | none | none | none | none | wave-1 | active | none | active |
| lane-2 | unassigned | team | none | none | none | primary | wave-2 | explicitly routed by team | none | parked |
| lane-3 | unassigned | team | none | none | none | primary | wave-2 | explicitly routed by team | none | parked |

## Released locks
| Lane | Artifact | Previous scope | Released because |
|---|---|---|---|
| primary | runtime/docs/tests naming surfaces | relay-only hard-cut scope | PR #100 merged; lane returned to idle baseline |
| primary | shell compaction and skill proof surfaces | real-world-token-proof scope | PR #103 merged; main CI `25922588929` green |
