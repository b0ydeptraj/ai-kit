# lane-registry

## Usage rules
- One lane owns one artifact lock at a time.
- Record the narrowest useful lock scope, not whole-repo ownership by default.
- Release or reassign the lock before a different lane edits the same artifact section.

## Active lanes
| Lane | Owner skill | Source orchestrator | Target hub | Primary artifact | Lock scope | depends_on | wave_id | resume_condition | Merge prerequisite | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| primary | bootstrap | workflow-router | developer | post-lane audit state refresh | live state and next-lane pointer | none | wave-1 | active | runtime doctor, enterprise doctor, readiness, and PR CI | active |
| lane-2 | unassigned | team | none | none | none | primary | wave-2 | explicitly routed by team | none | parked |
| lane-3 | unassigned | team | none | none | none | primary | wave-2 | explicitly routed by team | none | parked |

## Released locks
| Lane | Artifact | Previous scope | Released because |
|---|---|---|---|
| primary | `relay_kit_v3/commercial_dossier.py`, `relay_kit_public_cli.py`, `relay_kit_v3/release_lane.py`, readiness/support/publication docs/tests | commercial proof dossier | PR #39 merged and CI passed |
| primary | `relay_kit_v3/pulse.py`, `relay_kit_v3/signal_export.py`, `relay_kit_public_cli.py`, Pulse/signal docs/tests | commercial dossier Pulse/signal visibility | PR #41 merged and CI passed |
| primary | `.github/ISSUE_TEMPLATE/support.yml`, `docs/relay-kit-commercial-ownership.md`, `docs/relay-kit-support-sla.md`, GitHub release assets | external commercial proof | PR #43 merged, CI passed, and commercial dossier internal channel returned ready |
| primary | `relay_kit_public_cli.py`, README/install docs, enterprise/readiness/upgrade docs, CLI/package tests, GitHub release assets | default enterprise install | PR #45 merged, CI passed, and refreshed `v3.4.0.dev0` wheel install generated enterprise bundle by default |
| primary | `relay_kit_v3/registry/skills.py`, generated `skill-evolution` adapter skills, skill-evolution docs/tests | skill evolution utility | PR #47 merged and CI passed |
| primary | `scripts/skill_gauntlet.py`, high-risk generated skills, registry tool profiles, skill-evolution docs/tests | skill permission profile gate | PR #49 merged and CI passed |
| primary | `scripts/skill_gauntlet.py`, support generated skills, registry tool profiles, skill-evolution docs/tests | risk-sensitive skill profile expansion | PR #51 merged and CI passed |
| primary | `relay_kit_v3/eval_fixtures/workflow_scenarios.json`, skill gauntlet/workflow eval tests, workflow eval docs | profiled support routing scenarios | PR #54 merged and CI passed |
| primary | `scripts/eval_workflows.py`, workflow eval tests, workflow eval docs, Claude adoption matrix | support route-noise review | PR #56 merged and CI passed |
| primary | `scripts/eval_workflows.py`, `relay_kit_v3/pulse.py`, `relay_kit_v3/signal_export.py`, workflow eval fixtures/docs/tests | support evidence-contract checks | PR #58 merged and CI passed |
| primary | `relay_kit_v3/eval_fixtures/workflow_scenarios.json`, workflow eval docs/tests, skill gauntlet semantic tests | support evidence real-world fixtures | PR #60 merged and CI passed |
| primary | `scripts/eval_workflows.py`, `relay_kit_v3/pulse.py`, `relay_kit_v3/signal_export.py`, workflow eval/Pulse/signal docs/tests | support fixture depth review | PR #62 merged and CI passed |
| primary | `relay_kit_v3/eval_fixtures/workflow_scenarios.json`, workflow eval docs/tests, skill gauntlet semantic tests | workflow role coverage fixtures | PR #64 merged and CI passed |
| primary | `relay_kit_v3/eval_fixtures/workflow_scenarios.json`, workflow eval docs/tests, skill gauntlet semantic tests | workflow utility skill coverage fixtures | PR #66 merged and CI passed |
| primary | `relay_kit_v3/eval_fixtures/workflow_scenarios.json`, `tests/test_workflow_eval.py`, workflow eval docs/backlog | workflow route-quality tightening | PR #71 merged and CI passed |
| primary | `relay_kit_v3/readiness.py`, `tests/test_readiness_check.py`, readiness docs/backlog | readiness route-quality gate | PR #73 merged and CI passed |
| primary | `pyproject.toml`, `.relay-kit/version.json`, `relay_kit_public_cli.py`, `scripts/runtime_doctor.py`, publication artifacts | PyPI publication and installed doctor smoke fix | PR #75, PR #76, and PR #77 merged; `v3.4.1` PyPI install smoke, publish status, and commercial dossier passed |
| primary | `pyproject.toml`, `.relay-kit/version.json` | next-dev version bump | PR #3 merged and CI passed |
| primary | `relay_kit_v3/pulse.py`, `relay_kit_v3/signal_export.py`, `relay_kit_public_cli.py`, Pulse/signal docs/tests | package-index Pulse/signal visibility | PR #81 merged and CI passed |
| primary | `relay_kit_v3/context_governance.py`, `relay_kit_public_cli.py`, context/memory scripts, docs/tests/state | context and memory governance | PR #83 merged; main CI needs shallow ancestry guard follow-up |
| primary | `scripts/runtime_doctor.py`, `relay_kit_v3/context_governance.py`, `tests/test_context_governance.py`, live state artifacts | runtime doctor shallow ancestry guard | PR #84 merged and main CI `25608436233` passed |
| primary | `relay_kit_v3/lane_audit.py`, `relay_kit_public_cli.py`, `scripts/runtime_doctor.py`, team/lane templates, docs/tests/state | multi-lane coordination hardening | PR #86 merged and main CI `25620406371` passed |
| primary | `scripts/eval_workflows.py`, `relay_kit_v3/pulse.py`, `relay_kit_v3/signal_export.py`, Pulse/signal docs/tests | workflow focus dashboard | PR #37 merged and CI passed |
| primary | `relay_kit_v3/support_triage.py`, `relay_kit_v3/readiness.py`, `relay_kit_public_cli.py`, support docs/tests | support operations soak | PR #35 merged and CI passed |
| primary | `relay_kit_v3/eval_fixtures/workflow_scenarios.json`, temp path helpers, workflow eval docs/tests | workflow eval scenario expansion | PR #33 merged and CI passed |
| primary | `relay_kit_v3/pulse.py`, `relay_kit_v3/signal_export.py`, Pulse/signal docs/tests | Pulse gate drilldowns | PR #31 merged and CI passed |
| primary | `relay_kit_v3/pulse.py`, `relay_kit_v3/signal_export.py`, Pulse/signal docs/tests | Pulse gate summary | PR #29 merged and CI passed |
| primary | `relay_kit_v3/support_triage.py`, `relay_kit_public_cli.py`, support docs/tests | support triage readiness gate | PR #27 merged and CI passed |
| primary | `relay_kit_v3/readiness.py`, readiness docs/tests | readiness pytest output hygiene | PR #25 merged and CI passed |
| primary | `relay_kit_v3/publication.py`, `relay_kit_public_cli.py`, publication docs/tests | publication trail status | PR #23 merged and CI passed |
| primary | `scripts/eval_workflows.py`, `relay_kit_v3/pulse.py`, `relay_kit_v3/signal_export.py`, workflow eval docs/tests | workflow eval layer/role coverage signals | PR #21 merged and CI passed |
| primary | `relay_kit_v3/support_bundle.py`, support docs/tests | support bundle request-summary diagnostics | PR #19 merged and CI passed |
| primary | `relay_kit_v3/pulse.py`, `relay_kit_v3/signal_export.py`, `relay_kit_public_cli.py`, Pulse/signal docs/tests | support request Pulse/signal visibility | PR #17 merged and CI passed |
| primary | `relay_kit_v3/signal_export.py`, `relay_kit_public_cli.py`, signal export docs/tests | OTLP signal export | PR #2 merged and CI passed |
| primary | release readiness/package smoke/readiness gate files | `v3.3.0` release readiness | PR #1 merged and release published |
| primary | `.relay-kit/contracts/project-context.md`, `.relay-kit/state/*.md` | bootstrap state refresh | local runtime doctor, enterprise doctor, and pytest passed |
