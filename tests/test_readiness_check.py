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
    (root / "README.md").write_text("# Relay-kit\n", encoding="utf-8")
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "relay-kit-support-sla.md").write_text("# Support\n", encoding="utf-8")
    (root / "docs" / "relay-kit-enterprise-bundle.md").write_text("# Enterprise Bundle\n", encoding="utf-8")
    (root / "docs" / "relay-kit-contract-sync.md").write_text("# Contract Sync\n", encoding="utf-8")
    (root / "docs" / "relay-kit-readiness-check.md").write_text("# Readiness Check\n", encoding="utf-8")
    (root / "docs" / "relay-kit-pulse-report.md").write_text("# Pulse Report\n", encoding="utf-8")
    (root / "docs" / "relay-kit-signal-export.md").write_text("# Signal Export\n", encoding="utf-8")
    (root / "docs" / "relay-kit-release-readiness.md").write_text("# Release Readiness\n", encoding="utf-8")
    (root / "docs" / "relay-kit-release-lane.md").write_text("# Release Lane\n", encoding="utf-8")
    (root / "docs" / "relay-kit-publication-plan.md").write_text("# Publication Plan\n", encoding="utf-8")
    (root / ".relay-kit" / "contracts").mkdir(parents=True, exist_ok=True)
    (root / ".relay-kit" / "contracts" / "support-request.md").write_text("# Support Request\n", encoding="utf-8")
    (root / "pyproject.toml").write_text(
        """
[project]
name = "relay-kit"
version = "3.3.0"

[project.scripts]
relay-kit = "relay_kit_public_cli:main"

[tool.setuptools.packages.find]
include = ["relay_kit_v3*", "scripts*"]
        """.strip()
        + "\n",
        encoding="utf-8",
    )
    workflow = root / ".github" / "workflows"
    workflow.mkdir(parents=True, exist_ok=True)
    (workflow / "validate-runtime.yml").write_text(
        "\n".join(
            [
                "python scripts/validate_runtime.py",
                "python scripts/runtime_doctor.py . --strict",
                "python scripts/runtime_doctor.py . --strict --state-mode live",
                "python scripts/migration_guard.py . --strict",
                "python scripts/policy_guard.py . --strict",
                "python scripts/skill_gauntlet.py . --strict --semantic",
                "python scripts/eval_workflows.py . --strict",
                "python relay_kit_public_cli.py doctor . --skip-tests --policy-pack enterprise",
                "python -m pip wheel . --no-deps -w .tmp/wheelhouse",
                "python scripts/package_smoke.py .",
                "python -m pytest tests -q",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    manifest = root / ".relay-kit" / "manifest"
    manifest.mkdir(parents=True, exist_ok=True)
    (manifest / "bundles.json").write_text("{}\n", encoding="utf-8")
    (manifest / "trust.json").write_text("{}\n", encoding="utf-8")
    (root / ".relay-kit" / "version.json").write_text("{}\n", encoding="utf-8")
    support = root / ".relay-kit" / "support"
    support.mkdir(parents=True, exist_ok=True)
    (support / ".gitignore").write_text("support-bundle.json\n", encoding="utf-8")
    signals = root / ".relay-kit" / "signals"
    signals.mkdir(parents=True, exist_ok=True)
    (signals / ".gitignore").write_text(
        "relay-signals.json\nrelay-signals.jsonl\nrelay-signals-otlp.json\n",
        encoding="utf-8",
    )
    release = root / ".relay-kit" / "release"
    release.mkdir(parents=True, exist_ok=True)
    (release / ".gitignore").write_text(
        "publication-evidence.json\npublication-trail.json\npublication-trail.md\n",
        encoding="utf-8",
    )


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
        "signal-export",
        "release-lane",
        "commercial-docs",
    }
    signal_gate = next(gate for gate in report["gates"] if gate["id"] == "signal-export")
    assert signal_gate["status"] == "pass"
    assert signal_gate["details"]["signal_count"] > 0
    assert Path(signal_gate["details"]["otlp"]).exists()


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
    signal_gate = next(gate for gate in report["gates"] if gate["id"] == "signal-export")
    assert Path(signal_gate["details"]["otlp"]).name == "relay-signals-otlp.json"


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
