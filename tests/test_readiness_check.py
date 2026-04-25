from __future__ import annotations

import json
import subprocess
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3 import readiness
from relay_kit_v3.support_bundle import SCHEMA_VERSION as SUPPORT_SCHEMA_VERSION
from relay_kit_v3.contract_export import SCHEMA_VERSION as CONTRACT_EXPORT_SCHEMA_VERSION
from relay_kit_v3.contract_import import IMPORT_SCHEMA_VERSION as CONTRACT_IMPORT_SCHEMA_VERSION


def passing_command_runner(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(command, 0, stdout="ok\n", stderr="")


def failing_policy_runner(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    text = " ".join(command)
    if "policy_guard.py" in text:
        return subprocess.CompletedProcess(command, 2, stdout="Policy guard report\n- findings: 1\n", stderr="")
    return subprocess.CompletedProcess(command, 0, stdout="ok\n", stderr="")


def write_required_docs(root: Path) -> None:
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "relay-kit-support-sla.md").write_text("# Support\n", encoding="utf-8")
    (root / "docs" / "relay-kit-enterprise-bundle.md").write_text("# Enterprise Bundle\n", encoding="utf-8")
    (root / "docs" / "relay-kit-contract-sync.md").write_text("# Contract Sync\n", encoding="utf-8")
    (root / ".relay-kit" / "contracts").mkdir(parents=True, exist_ok=True)
    (root / ".relay-kit" / "contracts" / "support-request.md").write_text("# Support Request\n", encoding="utf-8")


def test_readiness_report_returns_candidate_when_required_gates_pass(tmp_path: Path) -> None:
    write_required_docs(tmp_path)

    report = readiness.build_readiness_report(
        tmp_path,
        profile="enterprise",
        command_runner=passing_command_runner,
        support_builder=lambda root, policy_pack: {"schema_version": SUPPORT_SCHEMA_VERSION},
        upgrade_builder=lambda root: {"status": "pass", "findings_count": 0},
        contract_exporter=lambda root: {"schema_version": CONTRACT_EXPORT_SCHEMA_VERSION},
        contract_importer=lambda root, payload: {
            "schema_version": CONTRACT_IMPORT_SCHEMA_VERSION,
            "status": "pass",
            "findings": [],
        },
    )

    assert report["schema_version"] == "relay-kit.readiness-report.v1"
    assert report["status"] == "pass"
    assert report["verdict"] == "commercial-ready-candidate"
    assert {gate["id"] for gate in report["gates"]} >= {
        "pytest",
        "doctor-enterprise",
        "trusted-manifest",
        "policy-enterprise",
        "workflow-eval",
        "support-bundle",
        "upgrade-check",
        "contract-sync",
        "commercial-docs",
    }


def test_readiness_report_holds_when_required_gate_fails(tmp_path: Path) -> None:
    write_required_docs(tmp_path)

    report = readiness.build_readiness_report(
        tmp_path,
        profile="enterprise",
        command_runner=failing_policy_runner,
        support_builder=lambda root, policy_pack: {"schema_version": SUPPORT_SCHEMA_VERSION},
        upgrade_builder=lambda root: {"status": "pass", "findings_count": 0},
        contract_exporter=lambda root: {"schema_version": CONTRACT_EXPORT_SCHEMA_VERSION},
        contract_importer=lambda root, payload: {
            "schema_version": CONTRACT_IMPORT_SCHEMA_VERSION,
            "status": "pass",
            "findings": [],
        },
    )

    assert report["status"] == "hold"
    assert report["verdict"] == "hold"
    assert any(gate["id"] == "policy-enterprise" and gate["status"] == "fail" for gate in report["gates"])


def test_readiness_report_is_limited_beta_when_tests_are_skipped(tmp_path: Path) -> None:
    write_required_docs(tmp_path)

    report = readiness.build_readiness_report(
        tmp_path,
        profile="enterprise",
        skip_tests=True,
        command_runner=passing_command_runner,
        support_builder=lambda root, policy_pack: {"schema_version": SUPPORT_SCHEMA_VERSION},
        upgrade_builder=lambda root: {"status": "pass", "findings_count": 0},
        contract_exporter=lambda root: {"schema_version": CONTRACT_EXPORT_SCHEMA_VERSION},
        contract_importer=lambda root, payload: {
            "schema_version": CONTRACT_IMPORT_SCHEMA_VERSION,
            "status": "pass",
            "findings": [],
        },
    )

    assert report["status"] == "pass"
    assert report["verdict"] == "limited-beta"
    assert any(gate["id"] == "pytest" and gate["status"] == "skipped" for gate in report["gates"])


def test_readiness_report_team_profile_uses_non_enterprise_manifest_gate(tmp_path: Path) -> None:
    write_required_docs(tmp_path)

    report = readiness.build_readiness_report(
        tmp_path,
        profile="team",
        command_runner=passing_command_runner,
        support_builder=lambda root, policy_pack: {"schema_version": SUPPORT_SCHEMA_VERSION},
        upgrade_builder=lambda root: {"status": "pass", "findings_count": 0},
        contract_exporter=lambda root: {"schema_version": CONTRACT_EXPORT_SCHEMA_VERSION},
        contract_importer=lambda root, payload: {
            "schema_version": CONTRACT_IMPORT_SCHEMA_VERSION,
            "status": "pass",
            "findings": [],
        },
    )

    gate_ids = {gate["id"] for gate in report["gates"]}

    assert report["verdict"] == "commercial-ready-candidate"
    assert "doctor-team" in gate_ids
    assert "policy-team" in gate_ids
    assert "bundle-manifest" in gate_ids
    assert "trusted-manifest" not in gate_ids


def test_public_cli_readiness_check_json(monkeypatch, capsys) -> None:
    def fake_report(project_root, profile, skip_tests=False):  # noqa: ANN001
        return {
            "schema_version": "relay-kit.readiness-report.v1",
            "status": "pass",
            "verdict": "commercial-ready-candidate",
            "project_path": str(Path(project_root).resolve()),
            "profile": profile,
            "gates": [],
            "findings": [],
        }

    monkeypatch.setattr(relay_kit_public_cli, "build_readiness_report", fake_report)

    exit_code = relay_kit_public_cli.main(["readiness", "check", ".", "--profile", "enterprise", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["profile"] == "enterprise"
    assert payload["verdict"] == "commercial-ready-candidate"
