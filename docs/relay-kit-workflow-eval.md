# Relay-kit Workflow Eval

`relay-kit eval run` turns bundled workflow scenarios into a machine-readable quality signal.

It is intentionally separate from `skill-gauntlet`:

- `skill-gauntlet --semantic` protects the runtime skill files from drift.
- `workflow eval` reports scenario pass rate, predicted skill, top routes, layer/role coverage, and missing evidence terms.
- The bundled default suite covers 60 scenarios across routing, implementation, QA, release, policy, architecture, UX, dependency, API, data, media, browser evidence, multimodal evidence, bootstrap, debug/fix/review hubs, analyst, brainstorm-hub, scout-hub, team, execution-loop, testing-patterns, PM, scrum, runtime diagnostics, context governance, lane audit, adapter diagnostics, query lookup, service-boundary review, and the remaining utility workflows such as doc-pointers, repo-map, memory-search, handoff-context, research, problem-solving, root-cause-debugging, sequential-thinking, mermaid-diagrams, skill-evolution, skill-gauntlet, and test-first-development.
- The quality block also reviews profiled support-skill routing noise, evidence-contract coverage, and report-level fixture depth across API, data, dependency, media, browser, and multimodal evidence utilities. The default suite includes at least two evidence-contract fixtures for each profiled support skill.
- The default suite currently has no weak route candidates: `weak_route_count=0` and `min_route_margin=5` after tightening the developer and test-hub routing fixtures.

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
- per-scenario `expected_layer`
- per-scenario `expected_role`
- per-scenario `predicted_skill`
- per-scenario `predicted_layer`
- per-scenario `predicted_role`
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
- `expected_layer_counts`
- `predicted_layer_counts`
- `expected_role_counts`
- `predicted_role_counts`
- `support_route_review`
- `support_evidence_contract_review`
- `support_fixture_depth_review`

The `support_route_review` block includes:

- `profiled_support_skills`
- `covered_profiled_support_skills`
- `missing_profiled_support_skills`
- `profiled_support_route_count`
- `weak_profiled_support_route_count`
- `weak_profiled_support_routes`
- `nearby_support_route_count`
- `nearby_support_routes`

`nearby_support_routes` only reports profiled support-skill competitors that are within the support route margin threshold. This is meant to expose duplicate/noisy triggers without treating every distant top-route neighbor as a real collision.

The `support_evidence_contract_review` block includes:

- `profiled_support_skills`
- `required_terms_by_skill`
- `profiled_support_scenario_count`
- `term_gap_count`
- `term_gaps`
- `prompt_gap_count`
- `prompt_gaps`

`term_gaps` reports profiled support scenarios whose `expected_terms` omit required evidence-contract terms. `prompt_gaps` reports scenarios whose prompt shape does not mention those required terms, even if the expected route still passes.

The `support_fixture_depth_review` block includes:

- `profiled_support_skills`
- `min_scenarios_per_skill`
- `min_prompt_words`
- `min_expected_terms`
- `max_prompt_similarity`
- `profiled_support_scenario_count`
- `missing_profiled_support_skills`
- `undercovered_profiled_support_skills`
- `skills`
- `duplicate_prompt_pair_count`
- `duplicate_prompt_pairs`
- `depth_gap_count`
- `depth_gaps`

`depth_gaps` reports report-level fixture weaknesses: too few scenarios for a profiled support skill, shallow prompts, too few expected terms, or prompt pairs that are too similar to prove meaningful coverage.

Default thresholds are:

- `min_pass_rate=1.0`
- `min_route_margin=1`
- `min_evidence_coverage=1.0`

The default threshold is intentionally lower than the current bundled-suite margin so teams can add local scenarios without immediately failing; release lanes can raise it with `--min-route-margin`.

Use `--min-scenarios <count>` when a release lane must prove a minimum scenario suite size.
Use `--baseline-file <previous-report.json>` to fail on pass-rate, scenario-count, or average-route-margin regression.

`--strict` returns exit code `2` when any scenario fails or the fixture file is missing/empty.
It also returns exit code `2` when quality thresholds, support evidence-contract checks, support fixture-depth checks, or baseline regression checks fail.

## Fixture Location

Bundled fixtures live at:

```text
relay_kit_v3/eval_fixtures/workflow_scenarios.json
```

Use `--scenario-fixtures <file>` to run a custom scenario suite.
