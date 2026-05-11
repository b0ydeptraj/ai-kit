# Relay-kit Pulse Report

`relay-kit pulse build` writes a static JSON and HTML report for local quality review.

Pulse is Relay-kit's own report surface. It is not a copy of an external dashboard system, and it does not require a server.

## Command

```bash
relay-kit pulse build /path/to/project
relay-kit pulse build /path/to/project --include-readiness
relay-kit pulse build /path/to/project --workflow-eval-file workflow-eval.json --readiness-file readiness.json
relay-kit pulse build /path/to/project --include-publication
relay-kit pulse build /path/to/project --publication-file publication-plan.json
relay-kit pulse build /path/to/project --include-package-index
relay-kit pulse build /path/to/project --package-index-file .relay-kit/release/package-index-check.json
relay-kit pulse build /path/to/project --include-support-request
relay-kit pulse build /path/to/project --support-request-file .relay-kit/support/support-request.json
relay-kit pulse build /path/to/project --include-commercial-dossier
relay-kit pulse build /path/to/project --commercial-dossier-file .relay-kit/commercial/commercial-dossier.json
relay-kit pulse build /path/to/project --include-context-audit --include-lane-audit --include-adapter-diagnostics --include-token-audit --include-query-search --query-search-text "dashboard eval polish" --include-service-boundaries
relay-kit pulse build /path/to/project --context-audit-file context-audit.json --lane-audit-file lane-audit.json --adapter-diagnostics-file adapter-diagnostics.json --token-audit-file token-audit.json --query-search-file query-search.json --service-boundaries-file service-boundaries.json
relay-kit pulse build /path/to/project --history-limit 50
relay-kit pulse build /path/to/project --no-history
```

Default output:

```text
.relay-kit/pulse/pulse-report.json
.relay-kit/pulse/index.html
.relay-kit/pulse/history.jsonl
```

## Signals

Pulse combines:

- workflow eval status, pass rate, route margin, route confidence, evidence coverage, layer coverage, role coverage, and skill distribution
- workflow focus signals for weak route candidates, eval coverage gaps, support evidence gaps, and support fixture-depth gaps
- readiness status and verdict when `--include-readiness` or `--readiness-file` is used
- publication plan status, channel, version, and finding count when `--include-publication` or `--publication-file` is used
- package-index status, target version, latest version, release file count, and finding count when `--include-package-index` or `--package-index-file` is used
- support request status, severity, diagnostic count, and finding count when `--include-support-request` or `--support-request-file` is used
- commercial dossier status, channel, external proof field count, and finding count when `--include-commercial-dossier` or `--commercial-dossier-file` is used
- context health from `relay-kit context audit`, including stale and missing source counts
- lane health from `relay-kit lane audit`, including conflicts, broad locks, and incomplete handoffs
- adapter health from `relay-kit adapter diagnose`, including missing skills and metadata drift
- token health from `relay-kit token audit`, including estimated tokens, compressed tokens, raw-required blocks, signal retention, and budget violations
- query health from `relay-kit query search`, including authoritative hit count
- service-boundary health from `relay-kit service boundaries`, including boundary findings
- gate summary status for workflow eval, readiness, publication, package index, support request, commercial dossier, and evidence ledger
- evidence ledger event counts, gate counts, and recent events
- Pulse history snapshots from previous report builds

## Status

- `pass`: workflow eval passed, readiness passed when included, and no recent failed evidence events are present
- `attention`: core quality gates passed, but recent evidence contains failed events, included readiness is only `limited-beta`, included publication plan is not `ready`, included package-index check is not `published`, included support request is not `ready`, or included commercial dossier is not `ready`
- `hold`: workflow eval or readiness is failing

`pulse_score` is a local summary score built from pass rate, evidence coverage, readiness status, and recent evidence failures. Treat it as a triage signal, not a release attestation.

## Gate Summary

The JSON report includes `gate_summary`:

- `status_counts`: count of gates in `pass`, `attention`, `hold`, and `not-run`
- `gates`: per-gate status and short summary for workflow eval, readiness, publication, package index, support request, commercial dossier, and evidence
- `gates[].drilldown`: degraded scenarios, gates, findings, diagnostics, or recent failed evidence events for that gate
- `drilldown_item_count`: total number of drilldown rows across the gate summary
- `next_actions`: concrete follow-up items for `attention` or `hold` gates

The HTML report renders the same gate summary as a table so dashboard reviews can
spot the blocking or degraded surface without reading raw JSON. It also renders
Gate details so a reviewer can see the first failing scenario, release check,
support diagnostic, or evidence event attached to each degraded gate.

## Workflow Focus

The JSON report includes `workflow_focus`:

- `weak_route_count`: count of low-margin routing scenarios that still pass but are close to another route
- `weak_routes`: scenario id, expected skill, predicted skill, route margin, confidence, and top routes
- `coverage_gap_count`: count of missing eval layers and roles
- `coverage_gaps`: missing layers, roles, skills, and covered-skill ratio from the registry
- `support_evidence_gap_count`: count of profiled support-skill evidence-contract term or prompt gaps
- `support_fixture_depth_gap_count`: count of report-level profiled support fixture depth gaps
- `support_fixture_depth`: first fixture-depth rows, including duplicate prompt pairs and shallow fixture gaps
- `next_actions`: concrete dashboard follow-ups for strengthening weak routes, support evidence contracts, fixture depth, or missing scenario coverage

The HTML report renders Workflow focus as a table before Gate summary so a
reviewer can spot route fragility even when the full workflow eval suite passes.

## Governance Health

The JSON report includes these additive top-level summaries when the matching artifact is included:

- `context_health`: source count, authoritative source count, stale sources, and missing sources
- `lane_health`: active lanes, parked lanes, conflicts, broad locks, and incomplete handoffs
- `adapter_health`: adapter count, missing skills, unexpected skills, and metadata drift
- `token_health`: estimated tokens, compressed tokens, signal retention, raw-required blocks, and budget violations
- `query_health`: query text, total hits, returned hits, and authoritative hits
- `service_boundary_health`: boundary count, module count, and finding count
- `governance_health`: combined status across the six governance sections

The HTML report renders Context Health, Lane Health, Adapter Health, Token Health, Query Health, and Service Boundaries as separate sections.

## History

Each normal `pulse build` appends one compact snapshot to `.relay-kit/pulse/history.jsonl`.

The current report includes a `trend` block with:

- prior snapshot count
- previous snapshot
- score delta
- pass-rate delta
- evidence-coverage delta
- average-route-margin delta
- status-change flag

Use `--no-history` for dry runs or screenshots that should not affect trend. Use `--history-limit <n>` to control how many prior snapshots are loaded into the report.

## Release Use

Run Pulse after eval/readiness evidence exists:

```bash
relay-kit eval run /path/to/project --strict --json --output-file workflow-eval.json
relay-kit readiness check /path/to/project --profile enterprise --json > readiness.json
relay-kit publish plan /path/to/project --channel pypi --json > publication-plan.json
relay-kit publish index-check /path/to/project --channel pypi --target-version X.Y.Z --package-url https://pypi.org/project/relay-kit/X.Y.Z/ --strict --json > package-index.json
relay-kit support request /path/to/project --severity P1 --policy-pack enterprise --json > support-request.json
relay-kit commercial dossier /path/to/project --channel pypi --strict --json > commercial-dossier.json
relay-kit pulse build /path/to/project --workflow-eval-file workflow-eval.json --readiness-file readiness.json --publication-file publication-plan.json --package-index-file package-index.json --support-request-file support-request.json --commercial-dossier-file commercial-dossier.json
```

Use the HTML file for human review and the JSON file for support bundles or future dashboards.

To export Pulse plus recent evidence events as local telemetry-style artifacts, run:

```bash
relay-kit signal export /path/to/project
```

Signal export includes `relay.gates.pass`, `relay.gates.attention`,
`relay.gates.hold`, `relay.gates.not_run`, `relay.gates.drilldown_items`,
`relay.workflow.weak_route_count`, `relay.workflow.coverage_gap_count`,
`relay.workflow.support_evidence_gap_count`,
`relay.workflow.support_fixture_depth_gap_count`, `relay.context.stale_sources`,
`relay.lanes.conflicts`, `relay.adapter.metadata_drift`,
`relay.context.estimated_tokens`, `relay.context.compressed_tokens`,
`relay.context.signal_retention`, `relay.context.raw_required_blocks`,
`relay.token.budget_violations`,
`relay.query.authoritative_hits`, `relay.service.boundary_findings`,
`relay.publication.ready`, `relay.package_index.published`,
`relay.support_request.ready`, and `relay.commercial_dossier.ready` when a
Pulse report contains those surfaces.
