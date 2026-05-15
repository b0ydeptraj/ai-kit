from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from relay_kit_v3 import real_world_eval
from relay_kit_v3.registry.skills import ALL_V3_SKILLS


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REAL_WORLD_CASES = len(ALL_V3_SKILLS)


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
    assert report["coverage"]["expected_skill_count"] == len(ALL_V3_SKILLS)
    assert report["coverage"]["covered_skill_count"] == len(ALL_V3_SKILLS)
    assert report["coverage"]["missing_skills"] == []
    assert report["findings"] == []
    assert {case["skill"] for case in report["results"]} == set(ALL_V3_SKILLS)


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
        require_all_registered_skills=False,
    )

    assert report["status"] == "fail"
    assert report["case_count"] == 2
    assert report["passed"] == 0
    assert report["failed"] == 2
    assert {finding["case_id"] for finding in report["findings"]} == {"bad-skill", "thin-go"}
    assert any(finding["check"] == "skill-exists" for finding in report["findings"])
    assert any(finding["check"] == "contract-terms" for finding in report["findings"])


def test_real_world_skill_eval_fails_when_registered_skill_has_no_case() -> None:
    report = real_world_eval.build_report(
        ROOT,
        cases=[
            {
                "id": "developer-only",
                "skill": "developer",
                "task": "Implement one production change with evidence.",
                "required_artifacts": ["working code"],
                "required_evidence": ["test evidence"],
                "pass_rubric": ["execution-loop"],
            }
        ],
    )

    assert report["status"] == "fail"
    assert report["coverage"]["covered_skill_count"] == 1
    assert "workflow-router" in report["coverage"]["missing_skills"]
    assert any(finding["check"] == "skill-coverage" for finding in report["findings"])


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
