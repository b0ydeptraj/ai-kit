from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from relay_kit_v3 import real_world_eval


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REAL_WORLD_CASES = 8


def run_command(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_real_world_skill_eval_reports_pass_schema() -> None:
    report = real_world_eval.build_report(ROOT)

    assert report["schema_version"] == "relay-kit.real-world-skill-eval.v1"
    assert report["status"] == "pass"
    assert report["case_count"] == EXPECTED_REAL_WORLD_CASES
    assert report["passed"] == EXPECTED_REAL_WORLD_CASES
    assert report["failed"] == 0
    assert report["findings"] == []
    assert {case["skill"] for case in report["results"]} >= {
        "go-service-engineering",
        "next-product-frontend",
        "growth-marketing",
        "market-research",
        "mmo-browser-fleet-automation",
        "mmo-http-api-automation",
        "mmo-cloud-operations-automation",
        "token-economy",
    }


def test_real_world_skill_eval_flags_unknown_skill_and_missing_terms() -> None:
    report = real_world_eval.build_report(
        ROOT,
        cases=[
            {
                "id": "bad-skill",
                "skill": "missing-skill",
                "task": "Route a real task to a missing skill.",
                "required_artifacts": ["artifact"],
                "required_evidence": ["evidence"],
                "pass_rubric": ["rubric"],
            },
            {
                "id": "thin-go",
                "skill": "go-service-engineering",
                "task": "Build a Go backend service.",
                "required_artifacts": ["go service implementation plan"],
                "required_evidence": ["unit tests", "integration tests", "nonexistent proof term"],
                "pass_rubric": ["observability", "made up rubric term"],
            },
        ],
    )

    assert report["status"] == "fail"
    assert report["case_count"] == 2
    assert report["passed"] == 0
    assert report["failed"] == 2
    assert {finding["case_id"] for finding in report["findings"]} == {"bad-skill", "thin-go"}
    assert any(finding["check"] == "skill-exists" for finding in report["findings"])
    assert any(finding["check"] == "contract-terms" for finding in report["findings"])


def test_real_world_skill_eval_cli_emits_json() -> None:
    result = run_command("-m", "relay_kit_v3.real_world_eval", ".", "--strict", "--json")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "relay-kit.real-world-skill-eval.v1"
    assert payload["status"] == "pass"
    assert payload["case_count"] == EXPECTED_REAL_WORLD_CASES


def test_public_cli_real_world_eval_emits_json() -> None:
    result = run_command("relay_kit_public_cli.py", "eval", "real-world", ".", "--strict", "--json")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "relay-kit.real-world-skill-eval.v1"
    assert payload["status"] == "pass"
    assert payload["case_count"] == EXPECTED_REAL_WORLD_CASES
