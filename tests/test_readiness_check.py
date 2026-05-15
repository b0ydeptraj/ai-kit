from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3 import readiness
from relay_kit_v3.generator import emit_core_skills
from relay_kit_v3.runtime_locale import write_runtime_locale
from relay_kit_v3.support_bundle import SCHEMA_VERSION as SUPPORT_SCHEMA_VERSION
from relay_kit_v3.contract_export import SCHEMA_VERSION as CONTRACT_EXPORT_SCHEMA_VERSION
from relay_kit_v3.contract_import import IMPORT_SCHEMA_VERSION as CONTRACT_IMPORT_SCHEMA_VERSION


def passing_command_runner(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    text = " ".join(command)
    if "eval_workflows.py" in text:
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps(healthy_workflow_eval_payload()) + "\n", stderr="")
    return subprocess.CompletedProcess(command, 0, stdout="ok\n", stderr="")


def failing_policy_runner(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    text = " ".join(command)
    if "policy_guard.py" in text:
        return subprocess.CompletedProcess(command, 2, stdout="Policy guard report\n- findings: 1\n", stderr="")
    if "eval_workflows.py" in text:
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps(healthy_workflow_eval_payload()) + "\n", stderr="")
    return subprocess.CompletedProcess(command, 0, stdout="ok\n", stderr="")


def weak_workflow_eval_runner(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    text = " ".join(command)
    if "eval_workflows.py" in text:
        payload = healthy_workflow_eval_payload()
        quality = payload["quality"]
        assert isinstance(quality, dict)
        quality["min_route_margin"] = 2
        quality["weak_route_count"] = 1
        quality["weak_routes"] = [
            {
                "id": "developer-implementation-ready",
                "expected_skill": "developer",
                "predicted_skill": "developer",
                "route_margin": 2,
            }
        ]
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps(payload) + "\n", stderr="")
    return subprocess.CompletedProcess(command, 0, stdout="ok\n", stderr="")


def healthy_workflow_eval_payload() -> dict[str, object]:
    return {
        "schema_version": "relay-kit.workflow-eval.v1",
        "status": "pass",
        "scenario_count": 55,
        "passed": 55,
        "failed": 0,
        "pass_rate": 1.0,
        "quality": {
            "min_route_margin": 5,
            "weak_route_count": 0,
            "weak_routes": [],
        },
    }


def write_required_docs(root: Path) -> None:
    emit_core_skills(root, "all", "enterprise")
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
    (root / "docs" / "relay-kit-commercial-dossier.md").write_text("# Commercial Dossier\n", encoding="utf-8")
    (root / "docs" / "relay-kit-adapter-diagnostics.md").write_text("# Adapter Diagnostics\n", encoding="utf-8")
    (root / "docs" / "relay-kit-locale-policy.md").write_text("# Locale Policy\n", encoding="utf-8")
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
                "python scripts/naming_guard.py . --strict",
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
    write_runtime_locale(root, locale="en")
    support = root / ".relay-kit" / "support"
    support.mkdir(parents=True, exist_ok=True)
    (support / ".gitignore").write_text("support-bundle.json\nsupport-request.json\n", encoding="utf-8")
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
    commercial = root / ".relay-kit" / "commercial"
    commercial.mkdir(parents=True, exist_ok=True)
    (commercial / ".gitignore").write_text("commercial-dossier.json\n", encoding="utf-8")


def healthy_support_bundle_payload() -> dict[str, object]:
    return {
        "schema_version": SUPPORT_SCHEMA_VERSION,
        "diagnostics": {
            "manifest": {"status": "valid"},
            "policy": {"findings_count": 0},
            "workflow_eval": {"status": "pass"},
            "signal_export": {"status": "pass", "summary": {"signal_count": 3}},
            "release_lane": {"status": "pass"},
        },
    }


def test_readiness_report_returns_candidate_when_required_gates_pass(tmp_path: Path) -> None:
    write_required_docs(tmp_path)

    report = readiness.build_readiness_report(
        tmp_path,
        profile="enterprise",
        command_runner=passing_command_runner,
        support_builder=lambda root, policy_pack: healthy_support_bundle_payload(),
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
        "adapter-diagnostics",
        "agent-profiles",
        "runtime-locale",
        "token-economy",
        "real-world-skill-eval",
        "skill-proof-audit",
    }
    signal_gate = next(gate for gate in report["gates"] if gate["id"] == "signal-export")
    assert signal_gate["status"] == "pass"
    assert signal_gate["details"]["signal_count"] > 0
    assert Path(signal_gate["details"]["otlp"]).exists()


def test_readiness_pytest_gate_uses_stable_basetemp(tmp_path: Path) -> None:
    write_required_docs(tmp_path)
    commands: list[list[str]] = []

    def recording_runner(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="ok\n", stderr="")

    readiness.build_readiness_report(
        tmp_path,
        profile="enterprise",
        command_runner=recording_runner,
        support_builder=lambda root, policy_pack: healthy_support_bundle_payload(),
        upgrade_builder=lambda root: {"status": "pass", "findings_count": 0},
        contract_exporter=lambda root: {"schema_version": CONTRACT_EXPORT_SCHEMA_VERSION},
        contract_importer=lambda root, payload: {
            "schema_version": CONTRACT_IMPORT_SCHEMA_VERSION,
            "status": "pass",
            "findings": [],
        },
    )

    pytest_command = next(command for command in commands if command[:3] == [readiness.sys.executable, "-m", "pytest"])

    assert "--basetemp" in pytest_command
    assert str(Path(".tmp") / "readiness-pytest") in pytest_command


def test_readiness_report_holds_when_required_gate_fails(tmp_path: Path) -> None:
    write_required_docs(tmp_path)

    report = readiness.build_readiness_report(
        tmp_path,
        profile="enterprise",
        command_runner=failing_policy_runner,
        support_builder=lambda root, policy_pack: healthy_support_bundle_payload(),
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


def test_readiness_report_holds_when_workflow_eval_has_weak_routes(tmp_path: Path) -> None:
    write_required_docs(tmp_path)

    report = readiness.build_readiness_report(
        tmp_path,
        profile="enterprise",
        command_runner=weak_workflow_eval_runner,
        support_builder=lambda root, policy_pack: healthy_support_bundle_payload(),
        upgrade_builder=lambda root: {"status": "pass", "findings_count": 0},
        contract_exporter=lambda root: {"schema_version": CONTRACT_EXPORT_SCHEMA_VERSION},
        contract_importer=lambda root, payload: {
            "schema_version": CONTRACT_IMPORT_SCHEMA_VERSION,
            "status": "pass",
            "findings": [],
        },
    )

    workflow_gate = next(gate for gate in report["gates"] if gate["id"] == "workflow-eval")

    assert report["status"] == "hold"
    assert report["verdict"] == "hold"
    assert workflow_gate["status"] == "fail"
    assert "weak routes: 1" in workflow_gate["summary"]
    assert workflow_gate["details"]["weak_route_count"] == 1
    assert workflow_gate["details"]["min_route_margin"] == 2


def test_readiness_report_holds_when_support_bundle_diagnostics_are_degraded(tmp_path: Path) -> None:
    write_required_docs(tmp_path)
    support_payload = healthy_support_bundle_payload()
    diagnostics = support_payload["diagnostics"]
    assert isinstance(diagnostics, dict)
    diagnostics["workflow_eval"] = {"status": "fail"}

    report = readiness.build_readiness_report(
        tmp_path,
        profile="enterprise",
        command_runner=passing_command_runner,
        support_builder=lambda root, policy_pack: support_payload,
        upgrade_builder=lambda root: {"status": "pass", "findings_count": 0},
        contract_exporter=lambda root: {"schema_version": CONTRACT_EXPORT_SCHEMA_VERSION},
        contract_importer=lambda root, payload: {
            "schema_version": CONTRACT_IMPORT_SCHEMA_VERSION,
            "status": "pass",
            "findings": [],
        },
    )

    gate = next(gate for gate in report["gates"] if gate["id"] == "support-bundle")

    assert report["status"] == "hold"
    assert gate["status"] == "fail"
    assert gate["details"]["findings_count"] == 1
    assert "diagnostics" in gate["summary"]


def test_readiness_report_holds_when_adapter_diagnostics_findings_exist(tmp_path: Path) -> None:
    write_required_docs(tmp_path)
    shutil.rmtree(tmp_path / ".codex" / "skills" / "developer")

    report = readiness.build_readiness_report(
        tmp_path,
        profile="enterprise",
        command_runner=passing_command_runner,
        support_builder=lambda root, policy_pack: healthy_support_bundle_payload(),
        upgrade_builder=lambda root: {"status": "pass", "findings_count": 0},
        contract_exporter=lambda root: {"schema_version": CONTRACT_EXPORT_SCHEMA_VERSION},
        contract_importer=lambda root, payload: {
            "schema_version": CONTRACT_IMPORT_SCHEMA_VERSION,
            "status": "pass",
            "findings": [],
        },
    )

    gate = next(gate for gate in report["gates"] if gate["id"] == "adapter-diagnostics")

    assert report["status"] == "hold"
    assert gate["status"] == "fail"
    assert gate["details"]["findings_count"] == 1
    assert "adapter diagnostics findings: 1" in gate["summary"]


def test_readiness_report_holds_when_agent_profile_diagnostics_findings_exist(tmp_path: Path) -> None:
    write_required_docs(tmp_path)
    (tmp_path / ".claude" / "agents" / "relay-growth.md").unlink()

    report = readiness.build_readiness_report(
        tmp_path,
        profile="enterprise",
        command_runner=passing_command_runner,
        support_builder=lambda root, policy_pack: healthy_support_bundle_payload(),
        upgrade_builder=lambda root: {"status": "pass", "findings_count": 0},
        contract_exporter=lambda root: {"schema_version": CONTRACT_EXPORT_SCHEMA_VERSION},
        contract_importer=lambda root, payload: {
            "schema_version": CONTRACT_IMPORT_SCHEMA_VERSION,
            "status": "pass",
            "findings": [],
        },
    )

    gate = next(gate for gate in report["gates"] if gate["id"] == "agent-profiles")

    assert report["status"] == "hold"
    assert gate["status"] == "fail"
    assert gate["details"]["findings_count"] == 1
    assert "agent profile diagnostics findings: 1" in gate["summary"]


def test_readiness_report_holds_when_real_world_skill_eval_fails(tmp_path: Path, monkeypatch) -> None:
    write_required_docs(tmp_path)

    monkeypatch.setattr(
        readiness,
        "build_real_world_eval_report",
        lambda root: {
            "schema_version": "relay-kit.real-world-skill-eval.v1",
            "status": "fail",
            "case_count": 1,
            "passed": 0,
            "failed": 1,
            "findings": [{"case_id": "thin-case", "detail": "missing evidence terms"}],
        },
    )

    report = readiness.build_readiness_report(
        tmp_path,
        profile="enterprise",
        command_runner=passing_command_runner,
        support_builder=lambda root, policy_pack: healthy_support_bundle_payload(),
        upgrade_builder=lambda root: {"status": "pass", "findings_count": 0},
        contract_exporter=lambda root: {"schema_version": CONTRACT_EXPORT_SCHEMA_VERSION},
        contract_importer=lambda root, payload: {
            "schema_version": CONTRACT_IMPORT_SCHEMA_VERSION,
            "status": "pass",
            "findings": [],
        },
    )

    gate = next(gate for gate in report["gates"] if gate["id"] == "real-world-skill-eval")

    assert report["status"] == "hold"
    assert gate["status"] == "fail"
    assert gate["details"]["failed"] == 1


def test_readiness_report_holds_when_skill_proof_audit_finds_theoretical_skill(tmp_path: Path, monkeypatch) -> None:
    write_required_docs(tmp_path)

    monkeypatch.setattr(
        readiness,
        "build_skill_proof_report",
        lambda root, strict=False: {
            "schema_version": "relay-kit.skill-proof-audit.v1",
            "status": "fail",
            "summary": {"skill_count": 1, "theoretical": 1, "validated": 0, "field_tested": 0},
            "findings": [{"skill": "thin-skill", "summary": "no validation or field evidence found"}],
        },
    )

    report = readiness.build_readiness_report(
        tmp_path,
        profile="enterprise",
        command_runner=passing_command_runner,
        support_builder=lambda root, policy_pack: healthy_support_bundle_payload(),
        upgrade_builder=lambda root: {"status": "pass", "findings_count": 0},
        contract_exporter=lambda root: {"schema_version": CONTRACT_EXPORT_SCHEMA_VERSION},
        contract_importer=lambda root, payload: {
            "schema_version": CONTRACT_IMPORT_SCHEMA_VERSION,
            "status": "pass",
            "findings": [],
        },
    )

    gate = next(gate for gate in report["gates"] if gate["id"] == "skill-proof-audit")

    assert report["status"] == "hold"
    assert gate["status"] == "fail"
    assert gate["details"]["summary"]["theoretical"] == 1


def test_readiness_report_is_limited_beta_when_tests_are_skipped(tmp_path: Path) -> None:
    write_required_docs(tmp_path)

    report = readiness.build_readiness_report(
        tmp_path,
        profile="enterprise",
        skip_tests=True,
        command_runner=passing_command_runner,
        support_builder=lambda root, policy_pack: healthy_support_bundle_payload(),
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
        support_builder=lambda root, policy_pack: healthy_support_bundle_payload(),
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
