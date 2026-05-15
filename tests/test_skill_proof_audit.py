from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from relay_kit_v3 import skill_proof
from relay_kit_v3.registry.skills import ALL_V3_SKILLS


ROOT = Path(__file__).resolve().parents[1]


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def test_skill_proof_audit_classifies_synthetic_real_world_and_field_evidence(tmp_path: Path) -> None:
    write_json(
        tmp_path / "relay_kit_v3" / "eval_fixtures" / "workflow_scenarios.json",
        [{"id": "developer-route", "expected_skill": "developer"}],
    )
    write_json(
        tmp_path / "relay_kit_v3" / "eval_fixtures" / "real_world_skill_cases.json",
        [{"id": "go-case", "skill": "go-service-engineering"}],
    )
    write_json(
        tmp_path / ".relay-kit" / "evidence" / "skill-field-evidence.json",
        [
            {
                "skill": "token-economy",
                "evidence_type": "field-tested",
                "source": "customer-runbook-2026-05",
            }
        ],
    )

    report = skill_proof.build_report(tmp_path)
    records = {record["skill"]: record for record in report["skills"]}

    assert report["schema_version"] == "relay-kit.skill-proof-audit.v1"
    assert records["developer"]["status"] == "validated"
    assert records["developer"]["proof_sources"] == [
        "synthetic:relay_kit_v3/eval_fixtures/workflow_scenarios.json#developer-route"
    ]
    assert records["go-service-engineering"]["status"] == "validated"
    assert records["go-service-engineering"]["proof_sources"] == [
        "real-world-case:relay_kit_v3/eval_fixtures/real_world_skill_cases.json#go-case"
    ]
    assert records["token-economy"]["status"] == "field-tested"
    assert records["token-economy"]["proof_sources"] == [
        ".relay-kit/evidence/skill-field-evidence.json#customer-runbook-2026-05"
    ]
    assert records["workflow-router"]["status"] == "theoretical"
    assert records["workflow-router"]["missing_proof_reason"] == "no validation or field evidence found"
    assert report["counts"]["field-tested"] == 1


def test_skill_proof_strict_fails_when_any_canonical_skill_is_theoretical(tmp_path: Path) -> None:
    write_json(
        tmp_path / "relay_kit_v3" / "eval_fixtures" / "workflow_scenarios.json",
        [{"id": "developer-route", "expected_skill": "developer"}],
    )

    report = skill_proof.build_report(tmp_path, strict=True)

    assert report["status"] == "fail"
    assert report["counts"]["theoretical"] == len(ALL_V3_SKILLS) - 1
    assert any(finding["check"] == "theoretical-production-skill" for finding in report["findings"])


def test_skill_proof_strict_passes_with_validated_canonical_skills_and_no_field_requirement(tmp_path: Path) -> None:
    write_json(
        tmp_path / "relay_kit_v3" / "eval_fixtures" / "workflow_scenarios.json",
        [
            {"id": f"{skill}-route", "expected_skill": skill}
            for skill in sorted(ALL_V3_SKILLS)
        ],
    )

    report = skill_proof.build_report(tmp_path, strict=True)

    assert report["status"] == "pass"
    assert report["counts"]["validated"] == len(ALL_V3_SKILLS)
    assert report["counts"]["field-tested"] == 0
    assert report["findings"] == []


def test_skill_proof_reports_honest_zero_field_tested_without_field_evidence() -> None:
    report = skill_proof.build_report(Path(__file__).resolve().parents[1])

    assert report["counts"]["field-tested"] == 0
    assert not any(record["status"] == "field-tested" for record in report["skills"])


def test_public_cli_skill_proof_audit_emits_json() -> None:
    result = subprocess.run(
        [sys.executable, "relay_kit_public_cli.py", "proof", "audit", ".", "--strict", "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "relay-kit.skill-proof-audit.v1"
    assert payload["status"] == "pass"
    assert payload["counts"]["theoretical"] == 0
    assert payload["counts"]["field-tested"] == 0
