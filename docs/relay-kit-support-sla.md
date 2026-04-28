# Relay-kit Support Workflow and SLA

This document defines the support workflow for paid/team Relay-kit usage.

It is not a legal SLA by itself. It is the operational support contract that tells a team what evidence to collect and how issues are triaged.

## Severity Levels

| Severity | Meaning | Triage target |
|---|---|---|
| P0 | Runtime install, doctor, policy, or upgrade path is blocked for a production-critical team. | Same business day target for paid support. |
| P1 | Upgrade, manifest, policy, or routing regression blocks a planned release. | Next business day target for paid support. |
| P2 | Workflow quality, docs, generated artifacts, or support tooling is degraded but has a workaround. | Two business day target. |
| P3 | Question, enhancement request, documentation issue, or non-blocking polish. | Best-effort triage in the next support review window. |

## Required Diagnostics

Run these before opening a support request:

```bash
relay-kit support bundle /path/to/project --policy-pack enterprise
relay-kit doctor /path/to/project --policy-pack enterprise --json
relay-kit policy check /path/to/project --pack enterprise --strict --json
relay-kit manifest verify /path/to/project --trusted
relay-kit upgrade check /path/to/project --json
relay-kit eval run /path/to/project --strict --json
relay-kit pulse build /path/to/project --include-readiness
relay-kit signal export /path/to/project --otlp --json
relay-kit release verify /path/to/project --json
relay-kit publish plan /path/to/project --channel pypi --json
```

Attach:

- `.relay-kit/support/support-bundle.json`
- `.relay-kit/signals/relay-signals.json`
- `.relay-kit/signals/relay-signals.jsonl`
- `.relay-kit/signals/relay-signals-otlp.json`
- the failing command output
- the support request template from `.relay-kit/contracts/support-request.md`

## Support Request Template

Use:

```text
.relay-kit/contracts/support-request.md
```

The request must include:

- severity
- package version
- installed bundle
- adapter target
- policy pack
- expected behavior
- actual behavior
- recent Relay-kit/runtime changes
- workaround, if any

## Included Support Scope

Included:

- Relay-kit install and generation issues
- doctor, policy, manifest, upgrade, eval, signal export, release-lane, and evidence-ledger failures
- bundle and generated skill drift
- support-bundle interpretation
- guidance for moving from baseline to enterprise bundle

Excluded:

- debugging the user's application logic unless the failure is caused by Relay-kit runtime generation
- custom private registry hosting unless separately contracted
- guaranteed response windows without a commercial agreement
- legal, compliance, or security certification claims

## Escalation Flow

1. User runs `relay-kit support bundle`.
2. User opens a support request with severity and required diagnostics.
3. Triage validates the bundle schema, package version, manifest status, upgrade status, policy findings, workflow eval status, signal export summary, and release-lane summary.
4. If the issue is reproducible in Relay-kit, it becomes a fix lane.
5. If the issue is project-specific, support returns a scoped recommendation and the evidence gap.
