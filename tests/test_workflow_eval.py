from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import relay_kit_public_cli
from scripts.eval_workflows import (
    PROFILED_SUPPORT_EVIDENCE_TERMS,
    SUPPORT_FIXTURE_MIN_EXPECTED_TERMS,
    SUPPORT_FIXTURE_MIN_PROMPT_WORDS,
    SUPPORT_FIXTURE_MIN_SCENARIOS_PER_SKILL,
    SUPPORT_ROUTE_MARGIN_THRESHOLD,
    support_evidence_contract_review,
    support_fixture_depth_review,
    support_route_review,
)


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DEFAULT_SCENARIOS = 43
EXPECTED_PROFILED_SUPPORT_SCENARIOS = len(PROFILED_SUPPORT_EVIDENCE_TERMS) * 2


def run_command(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_workflow_eval_reports_pass_rate_and_top_routes() -> None:
    result = run_command("scripts/eval_workflows.py", ".", "--strict", "--json")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "relay-kit.workflow-eval.v1"
    assert payload["status"] == "pass"
    assert payload["scenario_count"] == EXPECTED_DEFAULT_SCENARIOS
    assert payload["passed"] == EXPECTED_DEFAULT_SCENARIOS
    assert payload["failed"] == 0
    assert payload["pass_rate"] == 1.0
    assert payload["quality"]["min_route_margin"] >= 1
    assert payload["quality"]["evidence_term_coverage"] == 1.0
    assert payload["thresholds"]["min_route_margin"] == 1
    assert payload["quality"]["expected_layer_counts"]["layer-1-orchestrators"] >= 1
    assert payload["quality"]["expected_layer_counts"]["layer-4-specialists-and-standalones"] >= 1
    assert payload["quality"]["expected_role_counts"]["implementation"] >= 1
    assert "qa-governor" in payload["quality"]["expected_skill_counts"]
    assert payload["quality"]["weak_route_threshold"] == 3
    assert payload["quality"]["weak_route_count"] >= 1
    assert payload["quality"]["weak_routes"][0]["route_margin"] <= 3
    support_review = payload["quality"]["support_route_review"]
    assert support_review["support_route_margin_threshold"] == SUPPORT_ROUTE_MARGIN_THRESHOLD
    assert support_review["missing_profiled_support_skills"] == []
    assert support_review["nearby_support_route_count"] == 0
    assert support_review["weak_profiled_support_route_count"] == 0
    support_contract = payload["quality"]["support_evidence_contract_review"]
    assert support_contract["profiled_support_skills"] == sorted(PROFILED_SUPPORT_EVIDENCE_TERMS)
    assert support_contract["profiled_support_scenario_count"] == EXPECTED_PROFILED_SUPPORT_SCENARIOS
    profiled_support_counts = Counter(
        scenario["expected_skill"] for scenario in support_contract["scenarios"]
    )
    assert all(
        profiled_support_counts[skill] >= 2
        for skill in PROFILED_SUPPORT_EVIDENCE_TERMS
    )
    assert support_contract["term_gap_count"] == 0
    assert support_contract["prompt_gap_count"] == 0
    support_depth = payload["quality"]["support_fixture_depth_review"]
    assert support_depth["min_scenarios_per_skill"] == SUPPORT_FIXTURE_MIN_SCENARIOS_PER_SKILL
    assert support_depth["min_prompt_words"] == SUPPORT_FIXTURE_MIN_PROMPT_WORDS
    assert support_depth["min_expected_terms"] == SUPPORT_FIXTURE_MIN_EXPECTED_TERMS
    assert support_depth["profiled_support_scenario_count"] == EXPECTED_PROFILED_SUPPORT_SCENARIOS
    assert support_depth["depth_gap_count"] == 0
    assert support_depth["duplicate_prompt_pair_count"] == 0
    assert all(
        support_depth["skills"][skill]["scenario_count"] >= SUPPORT_FIXTURE_MIN_SCENARIOS_PER_SKILL
        for skill in PROFILED_SUPPORT_EVIDENCE_TERMS
    )
    assert all(
        support_depth["skills"][skill]["min_expected_terms_count"] >= SUPPORT_FIXTURE_MIN_EXPECTED_TERMS
        for skill in PROFILED_SUPPORT_EVIDENCE_TERMS
    )
    assert payload["quality"]["coverage_gaps"]["missing_layers"] == []
    assert payload["quality"]["coverage_gaps"]["missing_roles"] == []
    assert payload["quality"]["coverage_gaps"]["covered_skill_count"] == len(payload["quality"]["unique_expected_skills"])
    assert payload["results"][0]["top_routes"][0]["skill"] == payload["results"][0]["expected_skill"]
    assert payload["results"][0]["expected_layer"] == "layer-1-orchestrators"
    assert payload["results"][0]["predicted_layer"] == "layer-1-orchestrators"
    assert payload["results"][0]["route_margin"] >= 1
    assert payload["results"][0]["evidence_coverage"] == 1.0


def test_workflow_eval_default_suite_covers_production_team_skills() -> None:
    result = run_command("scripts/eval_workflows.py", ".", "--strict", "--json")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    expected_skills = set(payload["quality"]["unique_expected_skills"])
    expected_layers = set(payload["quality"]["unique_expected_layers"])
    assert "layer-1-orchestrators" in expected_layers
    assert "layer-2-workflow-hubs" in expected_layers
    assert "layer-3-utility-providers" in expected_layers
    assert "layer-4-specialists-and-standalones" in expected_layers
    for skill in {
        "api-integration",
        "browser-inspector",
        "data-persistence",
        "dependency-management",
        "media-tooling",
        "multimodal-evidence",
        "accessibility-review",
        "policy-guard",
        "impact-radar",
        "project-architecture",
        "ux-structure",
        "bootstrap",
        "debug-hub",
        "fix-hub",
        "review-hub",
        "pm",
        "architect",
        "scrum-master",
        "runtime-doctor",
        "analyst",
        "brainstorm-hub",
        "execution-loop",
        "scout-hub",
        "team",
        "testing-patterns",
    }:
        assert skill in expected_skills

    support_review = payload["quality"]["support_route_review"]
    assert set(support_review["profiled_support_skills"]).issubset(expected_skills)
    assert set(support_review["covered_profiled_support_skills"]) == set(support_review["profiled_support_skills"])
    assert support_review["missing_profiled_support_skills"] == []


def test_support_route_review_detects_nearby_profiled_support_noise() -> None:
    review = support_route_review(
        [
            {
                "id": "media-static-proof",
                "expected_skill": "media-tooling",
                "predicted_skill": "media-tooling",
                "route_margin": 1,
                "route_confidence": 0.5128,
                "top_routes": [
                    {"skill": "media-tooling", "score": 20},
                    {"skill": "multimodal-evidence", "score": 19},
                    {"skill": "browser-inspector", "score": 4},
                ],
            },
            {
                "id": "external-api-client",
                "expected_skill": "api-integration",
                "predicted_skill": "api-integration",
                "route_margin": 12,
                "route_confidence": 0.8,
                "top_routes": [
                    {"skill": "api-integration", "score": 18},
                    {"skill": "dependency-management", "score": 6},
                ],
            },
        ]
    )

    assert review["missing_profiled_support_skills"] == [
        "browser-inspector",
        "data-persistence",
        "dependency-management",
        "multimodal-evidence",
    ]
    assert review["weak_profiled_support_route_count"] == 1
    assert review["nearby_support_route_count"] == 1
    assert review["nearby_support_routes"][0]["id"] == "media-static-proof"
    assert review["nearby_support_routes"][0]["support_competitors"] == [
        {"skill": "multimodal-evidence", "score": 19}
    ]


def test_support_evidence_contract_review_detects_thin_profiled_support_terms() -> None:
    review = support_evidence_contract_review(
        [
            {
                "id": "thin-api",
                "expected_skill": "api-integration",
                "prompt": "Use api-integration for network-facing code and clients.",
                "expected_terms": ["clients"],
            }
        ]
    )

    assert review["profiled_support_scenario_count"] == 1
    assert review["term_gap_count"] == 1
    assert review["prompt_gap_count"] == 1
    assert review["term_gaps"][0]["missing_terms"] == ["auth", "retries"]
    assert review["prompt_gaps"][0]["missing_terms"] == ["auth", "retries"]


def test_support_fixture_depth_review_detects_report_level_fixture_gaps() -> None:
    duplicated_prompt = (
        "Use api-integration for payment webhook clients. Document auth, retries, "
        "timeouts, idempotency, request and response patterns, and error mapping."
    )
    review = support_fixture_depth_review(
        [
            {
                "id": "api-webhook-one",
                "expected_skill": "api-integration",
                "prompt": duplicated_prompt,
                "expected_terms": ["clients", "auth", "retries"],
            },
            {
                "id": "api-webhook-copy",
                "expected_skill": "api-integration",
                "prompt": duplicated_prompt,
                "expected_terms": ["clients", "auth", "retries"],
            },
            {
                "id": "thin-data",
                "expected_skill": "data-persistence",
                "prompt": "Use data-persistence for schemas.",
                "expected_terms": ["schemas"],
            },
        ]
    )

    assert review["profiled_support_scenario_count"] == 3
    assert review["missing_profiled_support_skills"] == [
        "browser-inspector",
        "dependency-management",
        "media-tooling",
        "multimodal-evidence",
    ]
    assert "data-persistence" in review["undercovered_profiled_support_skills"]
    assert review["duplicate_prompt_pair_count"] == 1
    assert review["depth_gap_count"] >= 3
    assert any(gap["check"] == "support-fixture-skill-count" for gap in review["depth_gaps"])
    assert any(gap["check"] == "support-fixture-prompt-depth" for gap in review["depth_gaps"])
    assert any(gap["check"] == "support-fixture-expected-terms-depth" for gap in review["depth_gaps"])


def test_workflow_eval_strict_fails_thin_profiled_support_contract(tmp_path: Path) -> None:
    fixture = tmp_path / "scenarios.json"
    fixture.write_text(
        """
        [
          {
            "id": "thin-api-contract",
            "prompt": "Use api-integration for network-facing code and clients.",
            "expected_skill": "api-integration",
            "expected_terms": ["clients"]
          }
        ]
        """,
        encoding="utf-8",
    )

    result = run_command(
        "scripts/eval_workflows.py",
        ".",
        "--scenario-fixtures",
        str(fixture),
        "--strict",
        "--json",
    )

    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert any(finding["check"] == "support-evidence-contract" for finding in payload["findings"])
    review = payload["quality"]["support_evidence_contract_review"]
    assert review["term_gap_count"] == 1
    assert review["prompt_gap_count"] == 1


def test_workflow_eval_strict_fails_shallow_support_fixture_depth(tmp_path: Path) -> None:
    fixture = tmp_path / "scenarios.json"
    fixture.write_text(
        """
        [
          {
            "id": "shallow-api-fixture",
            "prompt": "Use api-integration for network clients, auth, and retries.",
            "expected_skill": "api-integration",
            "expected_terms": ["clients", "auth", "retries"]
          }
        ]
        """,
        encoding="utf-8",
    )

    result = run_command(
        "scripts/eval_workflows.py",
        ".",
        "--scenario-fixtures",
        str(fixture),
        "--strict",
        "--json",
    )

    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert any(finding["check"] == "support-fixture-depth" for finding in payload["findings"])
    review = payload["quality"]["support_fixture_depth_review"]
    assert review["depth_gap_count"] >= 1
    assert "browser-inspector" in review["missing_profiled_support_skills"]


def test_workflow_eval_strict_fails_bad_route_fixture(tmp_path: Path) -> None:
    fixture = tmp_path / "scenarios.json"
    fixture.write_text(
        """
        [
          {
            "id": "bad-route",
            "prompt": "Work is about to be called done. Check acceptance criteria and write a QA report.",
            "expected_skill": "workflow-router",
            "expected_terms": ["workflow-state"]
          }
        ]
        """,
        encoding="utf-8",
    )

    result = run_command(
        "scripts/eval_workflows.py",
        ".",
        "--scenario-fixtures",
        str(fixture),
        "--strict",
        "--json",
    )

    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "fail"
    assert payload["scenario_count"] == 1
    assert payload["failed"] == 1
    assert payload["results"][0]["passed"] is False
    assert payload["results"][0]["predicted_skill"] == "qa-governor"
    assert any(finding["check"] == "scenario-route" for finding in payload["results"][0]["findings"])


def test_workflow_eval_writes_report_file(tmp_path: Path) -> None:
    output_file = tmp_path / "workflow-eval.json"

    result = run_command("scripts/eval_workflows.py", ".", "--output-file", str(output_file))

    assert result.returncode == 0, result.stdout + result.stderr
    assert output_file.exists()
    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert payload["status"] == "pass"
    assert "- pass rate: 1.00" in result.stdout
    assert "- findings: 0" in result.stdout


def test_workflow_eval_strict_fails_when_route_margin_is_below_threshold() -> None:
    result = run_command(
        "scripts/eval_workflows.py",
        ".",
        "--min-route-margin",
        "2",
        "--strict",
        "--json",
    )

    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "fail"
    assert payload["quality"]["min_route_margin"] == 1
    assert any(finding["check"] == "quality-threshold" for finding in payload["findings"])


def test_workflow_eval_detects_baseline_regression(tmp_path: Path) -> None:
    fixture = tmp_path / "scenarios.json"
    fixture.write_text(
        """
        [
          {
            "id": "one-pass",
            "prompt": "A new request arrived and the scope is unclear. Choose the track and next skill.",
            "expected_skill": "workflow-router",
            "expected_terms": ["track", "next skill"]
          }
        ]
        """,
        encoding="utf-8",
    )
    baseline = tmp_path / "baseline.json"
    baseline.write_text(
        json.dumps({"pass_rate": 1.0, "scenario_count": 2, "quality": {"average_route_margin": 99.0}}),
        encoding="utf-8",
    )

    result = run_command(
        "scripts/eval_workflows.py",
        ".",
        "--scenario-fixtures",
        str(fixture),
        "--baseline-file",
        str(baseline),
        "--strict",
        "--json",
    )

    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["baseline"]["scenario_count_delta"] == -1
    assert any(finding["check"] == "baseline-regression" for finding in payload["findings"])


def test_public_cli_eval_run_uses_workflow_eval(monkeypatch, capsys) -> None:
    from scripts import eval_workflows

    def fake_run_workflow_eval(args):  # noqa: ANN001
        assert "--min-route-margin" in args
        assert "--baseline-file" in args
        print("fake workflow eval")
        return 0

    monkeypatch.setattr(eval_workflows, "main", fake_run_workflow_eval)

    exit_code = relay_kit_public_cli.main(
        ["eval", "run", ".", "--strict", "--min-route-margin", "2", "--baseline-file", "baseline.json"]
    )

    assert exit_code == 0
    assert "fake workflow eval" in capsys.readouterr().out
