# Relay-kit Signal Export

`relay-kit signal export` writes local JSON, JSONL, and optional Relay OTLP signal artifacts from Pulse and the evidence ledger.

This is Relay-kit's first telemetry export surface. It is intentionally local-only: no network calls, no backend, and no external dashboard dependency.

## Command

```bash
relay-kit signal export /path/to/project
relay-kit signal export /path/to/project --json
relay-kit signal export /path/to/project --pulse-file /path/to/pulse-report.json
relay-kit signal export /path/to/project --output-dir /path/to/signals
relay-kit signal export /path/to/project --event-limit 100
relay-kit signal export /path/to/project --otlp
```

Default output:

```text
.relay-kit/signals/relay-signals.json
.relay-kit/signals/relay-signals.jsonl
```

With `--otlp`, Relay-kit also writes:

```text
.relay-kit/signals/relay-signals-otlp.json
```

## Inputs

Signal export reads:

- `.relay-kit/pulse/pulse-report.json`
- `.relay-kit/evidence/events.jsonl`

Build Pulse first if the report does not exist:

```bash
relay-kit pulse build /path/to/project --include-readiness
relay-kit pulse build /path/to/project --include-context-audit --include-lane-audit --include-adapter-diagnostics --include-token-audit --include-query-search --include-service-boundaries
relay-kit signal export /path/to/project
```

## Signal Types

Metric signals include:

- `relay.pulse.score`
- `relay.workflow.pass_rate`
- `relay.workflow.scenario_count`
- `relay.workflow.failed_count`
- `relay.workflow.evidence_coverage`
- `relay.workflow.expected_layer_count`
- `relay.workflow.average_route_margin`
- `relay.workflow.min_route_margin`
- `relay.workflow.weak_route_count`
- `relay.workflow.coverage_gap_count`
- `relay.workflow.support_evidence_gap_count`
- `relay.workflow.support_fixture_depth_gap_count`
- `relay.evidence.total_events`
- `relay.evidence.failures_total`
- `relay.evidence.failures_recent`
- `relay.readiness.ready`
- `relay.publication.ready`
- `relay.package_index.published`
- `relay.support_request.ready`
- `relay.commercial_dossier.ready`
- `relay.context.stale_sources`
- `relay.lanes.conflicts`
- `relay.adapter.metadata_drift`
- `relay.context.estimated_tokens`
- `relay.context.compressed_tokens`
- `relay.context.signal_retention`
- `relay.context.raw_required_blocks`
- `relay.token.budget_violations`
- `relay.query.authoritative_hits`
- `relay.service.boundary_findings`

Event signals include recent evidence ledger events under:

- `relay.evidence.event`

Each JSONL row contains the shared resource metadata and one signal object.

The OTLP file uses OpenTelemetry-compatible `resourceMetrics` and `resourceLogs` JSON sections. It is dependency-free and local-only; Relay-kit does not send telemetry over the network.

## Release Use

Use this command after Pulse when a support bundle, release review, or future dashboard needs machine-readable quality signals:

```bash
relay-kit readiness check /path/to/project --profile enterprise
relay-kit publish plan /path/to/project --channel pypi --json > publication-plan.json
relay-kit publish index-check /path/to/project --channel pypi --target-version X.Y.Z --package-url https://pypi.org/project/relay-kit/X.Y.Z/ --strict --json > package-index.json
relay-kit support request /path/to/project --severity P1 --policy-pack enterprise --json > support-request.json
relay-kit commercial dossier /path/to/project --channel pypi --strict --json > commercial-dossier.json
relay-kit pulse build /path/to/project --include-readiness --publication-file publication-plan.json --package-index-file package-index.json --support-request-file support-request.json --commercial-dossier-file commercial-dossier.json --include-context-audit --include-lane-audit --include-adapter-diagnostics --include-token-audit --include-query-search --include-service-boundaries
relay-kit signal export /path/to/project --otlp
```

The export is a measurement artifact, not a readiness verdict. Use `relay-kit readiness check` for the commercial-ready gate.

Enterprise readiness also runs a required `signal-export` gate to prove JSON, JSONL, and OTLP artifacts can be generated for the current release lane.
