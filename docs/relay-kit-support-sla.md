# Relay-kit Support Workflow and SLA

This document defines the support workflow for paid/team Relay-kit usage.

It is not a legal SLA by itself. It is the operational support contract that tells a team what evidence to collect and how issues are triaged.

## Public Support Intake

- Support intake: `https://github.com/b0ydeptraj/Relay-kit/issues/new?template=support.yml`
- Support owner: `b0ydeptraj`
- Commercial ownership statement: `docs/relay-kit-commercial-ownership.md`

The public issue template is the default intake path for beta and public proof review. Private paid customers can use a separate contracted support channel when one exists, but the same diagnostic requirements still apply.

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
relay-kit publish trail /path/to/project --channel pypi --json
relay-kit publish plan /path/to/project --channel pypi --json
relay-kit publish evidence /path/to/project --channel pypi --twine-check-file .tmp/twine-check.txt --upload-log-file .tmp/upload-log.txt --publication-plan-file .relay-kit/release/publication-plan.json --json
relay-kit commercial dossier /path/to/project --channel pypi --ci-url <ci-url> --release-url <release-url> --package-url <package-url> --sla-url <sla-url> --support-url <support-url> --legal-owner <owner> --support-owner <owner> --strict --json
relay-kit support request /path/to/project --severity P1 --policy-pack enterprise --json
relay-kit support triage /path/to/project --strict --json
relay-kit support soak /path/to/project --strict --json
```

Attach:

- `.relay-kit/support/support-bundle.json`
- `.relay-kit/signals/relay-signals.json`
- `.relay-kit/signals/relay-signals.jsonl`
- `.relay-kit/signals/relay-signals-otlp.json`
- `.relay-kit/release/publication-trail.json` when the issue involves package publication workflow
- `.relay-kit/release/publication-evidence.json` when the issue involves package publication
- `.relay-kit/commercial/commercial-dossier.json` when the issue involves commercial release readiness
- `.relay-kit/support/support-request.json`
- the failing command output
- the support request template from `.relay-kit/contracts/support-request.md`

When `.relay-kit/support/support-request.json` already exists, the support bundle
also includes a redacted `diagnostics.support_request` summary with status,
severity, environment, diagnostic count, and finding count.

Run `relay-kit support triage` after the bundle and request exist. It returns
`ready` only when both local artifacts are valid and the request diagnostics are
present.

Run `relay-kit support soak` after the bundle exists to prove the operational
handoff path across P0, P1, and P2 fixtures. The soak report fails if the support
bundle diagnostics are degraded or if the synthetic P0/P1/P2 support requests do
not have complete diagnostic attachments.

## Support Request Template

Use:

```text
.relay-kit/contracts/support-request.md
```

Or generate the structured request artifact:

```bash
relay-kit support request /path/to/project \
  --severity P1 \
  --summary "Enterprise doctor fails after manifest trust metadata drift." \
  --package-version 3.4.0 \
  --os Windows \
  --shell PowerShell \
  --bundle enterprise \
  --adapter codex \
  --policy-pack enterprise \
  --expected "Enterprise doctor should pass with trusted manifest metadata." \
  --actual "Trusted manifest verification fails after a local skill edit." \
  --recent-changes "Regenerated skills and edited manifest metadata." \
  --workaround "Regenerate manifest trust metadata before release." \
  --strict \
  --json
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
3. User runs `relay-kit support triage` to validate the support request and bundle artifacts before handoff.
4. User runs `relay-kit support soak` to validate P0/P1/P2 paid-support fixtures against the current support bundle.
5. Triage validates the support request schema, bundle schema, manifest status, policy findings, workflow eval status, signal export summary, release-lane summary, and publication evidence when applicable.
6. If the issue is reproducible in Relay-kit, it becomes a fix lane.
7. If the issue is project-specific, support returns a scoped recommendation and the evidence gap.
