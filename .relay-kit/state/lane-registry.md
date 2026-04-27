# lane-registry

## Usage rules
- One lane owns one artifact lock at a time.
- Record the narrowest useful lock scope, not whole-repo ownership by default.
- Release or reassign the lock before a different lane edits the same artifact section.

## Active lanes
| Lane | Owner skill | Source orchestrator | Target hub | Primary artifact | Lock scope | Merge prerequisite | Status |
|---|---|---|---|---|---|---|---|
| primary | bootstrap | workflow-router | none | `.relay-kit/contracts/project-context.md` | none | CI after merge | ready-for-merge |
| lane-2 | unassigned | none | none | none | none | none | parked |
| lane-3 | unassigned | none | none | none | none | none | parked |

## Released locks
| Lane | Artifact | Previous scope | Released because |
|---|---|---|---|
| primary | `pyproject.toml`, `.relay-kit/version.json` | next-dev version bump | PR #3 merged and CI passed |
| primary | `relay_kit_v3/signal_export.py`, `relay_kit_public_cli.py`, signal export docs/tests | OTLP signal export | PR #2 merged and CI passed |
| primary | release readiness/package smoke/readiness gate files | `v3.3.0` release readiness | PR #1 merged and release published |
| primary | `.relay-kit/contracts/project-context.md`, `.relay-kit/state/*.md` | bootstrap state refresh | local runtime doctor, enterprise doctor, and pytest passed |
