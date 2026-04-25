# Relay-kit Workflow Eval

`relay-kit eval run` turns bundled workflow scenarios into a machine-readable quality signal.

It is intentionally separate from `skill-gauntlet`:

- `skill-gauntlet --semantic` protects the runtime skill files from drift.
- `workflow eval` reports scenario pass rate, predicted skill, top routes, and missing evidence terms.

## Commands

```bash
relay-kit eval run /path/to/project --strict
relay-kit eval run /path/to/project --json --output-file workflow-eval.json
relay-kit eval run /path/to/project --strict --min-route-margin 2
relay-kit eval run /path/to/project --baseline-file previous-workflow-eval.json --strict
python scripts/eval_workflows.py . --strict
```

## Report Contract

The JSON report uses `schema_version=relay-kit.workflow-eval.v1` and includes:

- `status`
- `scenario_count`
- `passed`
- `failed`
- `pass_rate`
- `quality`
- `thresholds`
- `baseline`
- `findings_count`
- per-scenario `expected_skill`
- per-scenario `predicted_skill`
- per-scenario `route_margin`
- per-scenario `route_confidence`
- per-scenario `top_routes`
- per-scenario `missing_terms`
- per-scenario `evidence_coverage`

The `quality` block includes:

- `min_route_margin`
- `average_route_margin`
- `mean_route_confidence`
- `evidence_term_coverage`
- `expected_skill_counts`
- `predicted_skill_counts`

Default thresholds are:

- `min_pass_rate=1.0`
- `min_route_margin=1`
- `min_evidence_coverage=1.0`

Use `--min-scenarios <count>` when a release lane must prove a minimum scenario suite size.
Use `--baseline-file <previous-report.json>` to fail on pass-rate, scenario-count, or average-route-margin regression.

`--strict` returns exit code `2` when any scenario fails or the fixture file is missing/empty.
It also returns exit code `2` when quality thresholds or baseline regression checks fail.

## Fixture Location

Bundled fixtures live at:

```text
relay_kit_v3/eval_fixtures/workflow_scenarios.json
```

Use `--scenario-fixtures <file>` to run a custom scenario suite.
