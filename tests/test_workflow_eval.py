from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import relay_kit_public_cli


ROOT = Path(__file__).resolve().parents[1]


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
    assert payload["scenario_count"] == 20
    assert payload["passed"] == 20
    assert payload["failed"] == 0
    assert payload["pass_rate"] == 1.0
    assert payload["quality"]["min_route_margin"] >= 1
    assert payload["quality"]["evidence_term_coverage"] == 1.0
    assert payload["thresholds"]["min_route_margin"] == 1
    assert "qa-governor" in payload["quality"]["expected_skill_counts"]
    assert payload["results"][0]["top_routes"][0]["skill"] == payload["results"][0]["expected_skill"]
    assert payload["results"][0]["route_margin"] >= 1
    assert payload["results"][0]["evidence_coverage"] == 1.0


def test_workflow_eval_default_suite_covers_production_team_skills() -> None:
    result = run_command("scripts/eval_workflows.py", ".", "--strict", "--json")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    expected_skills = set(payload["quality"]["unique_expected_skills"])
    for skill in {
        "api-integration",
        "data-persistence",
        "dependency-management",
        "accessibility-review",
        "policy-guard",
        "impact-radar",
        "project-architecture",
        "ux-structure",
    }:
        assert skill in expected_skills


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
