# Relay-kit Signal Export

`relay-kit signal export` writes local JSON and JSONL signal artifacts from Pulse and the evidence ledger.

This is Relay-kit's first telemetry export surface. It is intentionally local-only: no network calls, no backend, and no external dashboard dependency.

## Command

```bash
relay-kit signal export /path/to/project
relay-kit signal export /path/to/project --json
relay-kit signal export /path/to/project --pulse-file /path/to/pulse-report.json
relay-kit signal export /path/to/project --output-dir /path/to/signals
relay-kit signal export /path/to/project --event-limit 100
```

Default output:

```text
.relay-kit/signals/relay-signals.json
.relay-kit/signals/relay-signals.jsonl
```

## Inputs

Signal export reads:

- `.relay-kit/pulse/pulse-report.json`
- `.relay-kit/evidence/events.jsonl`

Build Pulse first if the report does not exist:

```bash
relay-kit pulse build /path/to/project --include-readiness
relay-kit signal export /path/to/project
```

## Signal Types

Metric signals include:

- `relay.pulse.score`
- `relay.workflow.pass_rate`
- `relay.workflow.scenario_count`
- `relay.workflow.failed_count`
- `relay.workflow.evidence_coverage`
- `relay.workflow.average_route_margin`
- `relay.workflow.min_route_margin`
- `relay.evidence.total_events`
- `relay.evidence.failures_total`
- `relay.evidence.failures_recent`
- `relay.readiness.ready`

Event signals include recent evidence ledger events under:

- `relay.evidence.event`

Each JSONL row contains the shared resource metadata and one signal object.

## Release Use

Use this command after Pulse when a support bundle, release review, or future dashboard needs machine-readable quality signals:

```bash
relay-kit readiness check /path/to/project --profile enterprise
relay-kit pulse build /path/to/project --include-readiness
relay-kit signal export /path/to/project
```

The export is a measurement artifact, not a readiness verdict. Use `relay-kit readiness check` for the commercial-ready gate.

Enterprise readiness also runs a required `signal-export` gate to prove these artifacts can be generated for the current release lane.
