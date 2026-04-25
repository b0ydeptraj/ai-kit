# logging-observability

> Path: `.relay-kit/references/logging-observability.md`
> Purpose: Document how this codebase emits logs, metrics, traces, health signals, alerts, and other runtime evidence so debugging and review work can rely on concrete signals instead of guesswork.
> Used by: developer, debug-hub, review-hub, qa-governor, test-hub

## Logs, metrics, traces, and health signals
- `relay-kit doctor` writes structured gate events to `.relay-kit/evidence/events.jsonl`.
- `relay-kit evidence summary` reads the local ledger and reports status counts, gate counts, and recent events.
- `scripts/eval_workflows.py` reports workflow scenario pass rate, findings count, and route details.

## Where to inspect runtime evidence
- Gate history: `.relay-kit/evidence/events.jsonl`.
- Support diagnostics: `.relay-kit/support/support-bundle.json`.
- Bundle checksum evidence: `.relay-kit/manifest/bundles.json`.
- Trust metadata evidence: `.relay-kit/manifest/trust.json`.

## Structured logging and correlation rules
- Doctor events include `run_id`, gate label, status, exit code, findings count, evidence files, and elapsed milliseconds.
- Support bundles include recent evidence events plus upgrade, manifest, policy, and workflow eval summaries.
- New gates should emit stable labels so evidence summaries remain comparable across releases.

## Alerting, dashboards, and noisy signals
- Relay-kit has local evidence summaries, not a hosted dashboard or remote telemetry pipeline.
- Treat repeated doctor failures, strict policy findings, failed trusted manifest verification, and workflow eval regressions as release-blocking signals.
- Avoid adding noisy checks to baseline; stronger governance belongs in named policy packs or explicit strict gates.

## Common blind spots during debugging
- Commands run directly outside doctor may not append evidence ledger events.
- Generated ignored files can make a local doctor pass; CI must generate trusted manifest evidence before enterprise doctor.
- A support bundle can summarize manifest validity but cannot prove external signer identity.

## Observability follow-ups when behavior changes
- Add a test for every new gate result label or evidence payload shape.
- Update support bundle diagnostics when a new release-critical gate is added.
- Keep docs and CI commands aligned with the strictest supported enterprise flow.
