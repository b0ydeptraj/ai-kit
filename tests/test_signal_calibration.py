from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3 import signal_calibration
from relay_kit_v3.generator import BUNDLES, emit_core_skills
from relay_kit_v3.registry.skills import ALL_V3_SKILLS, render_skill


ROOT = Path(__file__).resolve().parents[1]


def test_signal_calibration_skill_is_canonical_and_generated(tmp_path: Path) -> None:
    assert "signal-calibration" in ALL_V3_SKILLS
    assert "signal-calibration" in BUNDLES["enterprise"]

    rendered = render_skill(ALL_V3_SKILLS["signal-calibration"])
    assert "overclaim" in rendered
    assert "field-tested" in rendered
    assert "proof_level" in rendered

    emit_core_skills(tmp_path, "all", "enterprise")
    for adapter_root in (".codex", ".claude", ".agent"):
        assert (tmp_path / adapter_root / "skills" / "signal-calibration" / "SKILL.md").exists()


def test_signal_calibration_blocks_field_tested_claim_without_field_evidence(tmp_path: Path) -> None:
    report = signal_calibration.build_report(
        tmp_path,
        mode="claims",
        claims=["Relay-kit skills are field-tested and production-ready."],
        strict=True,
    )

    assert report["schema_version"] == "relay-kit.signal-calibration.v1"
    assert report["status"] == "fail"
    claim = report["claims"][0]
    assert claim["verdict"] == "unsupported"
    assert claim["proof_level"] == "none"
    assert claim["confidence"] == "blocked"
    assert "field-tested" in claim["overclaim_flags"]
    assert claim["evidence_sources"] == []


def test_signal_calibration_skill_report_keeps_validated_separate_from_field_tested() -> None:
    report = signal_calibration.build_report(
        ROOT,
        mode="skill",
        skill="signal-calibration",
        strict=True,
    )

    assert report["status"] == "pass"
    assert report["summary"]["field_tested_claims"] == 0
    claim = report["claims"][0]
    assert claim["claim_type"] == "skill_quality"
    assert claim["proof_level"] == "real-world-fixture"
    assert claim["verdict"] == "proven"
    assert claim["confidence"] == "high"


def test_signal_calibration_readiness_reports_public_overclaim_findings(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("Relay-kit has field-tested proof.\n", encoding="utf-8")

    report = signal_calibration.build_report(tmp_path, mode="readiness", strict=True)

    assert report["status"] == "fail"
    assert report["summary"]["unsupported_claims"] >= 1
    assert any(finding["check"] == "public-overclaim" for finding in report["findings"])


def test_public_cli_calibrate_readiness_json() -> None:
    result = subprocess.run(
        [sys.executable, "relay_kit_public_cli.py", "calibrate", "readiness", ".", "--strict", "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "relay-kit.signal-calibration.v1"
    assert payload["status"] == "pass"
    assert payload["summary"]["blocked_claims"] == 0


def test_public_cli_calibrate_claims_strict_fails_on_unproven_commercial_claim(capsys) -> None:
    exit_code = relay_kit_public_cli.main(
        [
            "calibrate",
            "claims",
            ".",
            "--claim",
            "Relay-kit is commercial-ready and field-tested.",
            "--strict",
            "--json",
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 2
    assert payload["status"] == "fail"
    assert payload["summary"]["blocked_claims"] == 1
