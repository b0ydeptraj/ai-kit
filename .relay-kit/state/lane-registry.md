# lane-registry

## Usage rules
- One lane owns one artifact lock at a time.
- Record the narrowest useful lock scope, not whole-repo ownership by default.
- Release or reassign the lock before a different lane edits the same artifact section.

## Active lanes
| Lane | Owner skill | Source orchestrator | Target hub | Primary artifact | Lock scope | Merge prerequisite | Status |
|---|---|---|---|---|---|---|---|
| primary | unassigned | workflow-router | none | none | none | none | active |
| lane-2 | unassigned | team | none | none | none | none | parked |
| lane-3 | unassigned | team | none | none | none | none | parked |

## Released locks
| Lane | Artifact | Previous scope | Released because |
|---|---|---|---|
| none | none | none | none |
