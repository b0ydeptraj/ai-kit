"""Commercial readiness checks for Relay-kit."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from relay_kit_v3.contract_export import SCHEMA_VERSION as CONTRACT_EXPORT_SCHEMA_VERSION
from relay_kit_v3.contract_export import export_contracts
from relay_kit_v3.contract_import import IMPORT_SCHEMA_VERSION as CONTRACT_IMPORT_SCHEMA_VERSION
from relay_kit_v3.contract_import import import_contracts
from relay_kit_v3.support_bundle import SCHEMA_VERSION as SUPPORT_SCHEMA_VERSION
from relay_kit_v3.support_bundle import build_support_bundle
from relay_kit_v3.upgrade import build_upgrade_report


SCHEMA_VERSION = "relay-kit.readiness-report.v1"
PROFILES = {"team", "enterprise"}
REPO_ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DOCS = [
    "docs/relay-kit-support-sla.md",
    "docs/relay-kit-enterprise-bundle.md",
    "docs/relay-kit-contract-sync.md",
    ".relay-kit/contracts/support-request.md",
]

CommandRunner = Callable[[list[str], Path], subprocess.CompletedProcess[str]]
SupportBuilder = Callable[[Path, str], Mapping[str, Any]]
UpgradeBuilder = Callable[[Path], Mapping[str, Any]]
ContractExporter = Callable[[Path], Mapping[str, Any]]
ContractImporter = Callable[[Path, Mapping[str, Any]], Mapping[str, Any]]


def build_readiness_report(
    project_root: Path | str,
    *,
    profile: str = "enterprise",
    skip_tests: bool = False,
    command_runner: CommandRunner | None = None,
    support_builder: SupportBuilder | None = None,
    upgrade_builder: UpgradeBuilder | None = None,
    contract_exporter: ContractExporter | None = None,
    contract_importer: ContractImporter | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    selected_profile = _normalize_profile(profile)
    runner = command_runner or run_command
    support = support_builder or _default_support_builder
    upgrade = upgrade_builder or _default_upgrade_builder
    contract_export = contract_exporter or _default_contract_exporter
    contract_import = contract_importer or _default_contract_importer

    gates: list[dict[str, Any]] = []
    gates.extend(_run_command_gates(root, selected_profile, skip_tests, runner))
    gates.append(_support_bundle_gate(root, selected_profile, support))
    gates.append(_upgrade_gate(root, upgrade))
    gates.append(_contract_sync_gate(root, contract_export, contract_import))
    gates.append(_commercial_docs_gate(root))

    required_failures = [gate for gate in gates if gate["required"] and gate["status"] not in {"pass", "skipped"}]
    advisory_failures = [gate for gate in gates if not gate["required"] and gate["status"] not in {"pass", "skipped"}]
    skipped_required = [gate for gate in gates if gate["required"] and gate["status"] == "skipped"]

    if required_failures:
        status = "hold"
        verdict = "hold"
    elif skipped_required or advisory_failures:
        status = "pass"
        verdict = "limited-beta"
    else:
        status = "pass"
        verdict = "commercial-ready-candidate"

    findings = [
        {
            "gate": gate["id"],
            "status": gate["status"],
            "summary": gate.get("summary", ""),
        }
        for gate in gates
        if gate["status"] not in {"pass", "skipped"}
    ]
    residual_risks = [
        "Remote CI, release upload, and paid support operations are not verified by this local gate.",
        "This gate produces a commercial-ready candidate verdict, not a cryptographic release attestation.",
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "verdict": verdict,
        "profile": selected_profile,
        "project_path": str(root),
        "gates": gates,
        "findings": findings,
        "residual_risks": residual_risks,
    }


def render_readiness_report(report: Mapping[str, Any]) -> str:
    lines = [
        "Relay-kit readiness check",
        f"- project: {report.get('project_path')}",
        f"- profile: {report.get('profile')}",
        f"- status: {report.get('status')}",
        f"- verdict: {report.get('verdict')}",
        f"- gates: {len(report.get('gates', []))}",
        f"- findings: {len(report.get('findings', []))}",
    ]
    gates = report.get("gates", [])
    if gates:
        lines.append("- gate results:")
        for gate in gates:
            label = gate.get("label", gate.get("id", "unknown"))
            required = "required" if gate.get("required") else "advisory"
            lines.append(f"  - {label}: {gate.get('status')} ({required})")
            if gate.get("summary") and gate.get("status") != "pass":
                lines.append(f"    {gate['summary']}")
    risks = report.get("residual_risks", [])
    if risks:
        lines.append("- residual risks:")
        lines.extend(f"  - {risk}" for risk in risks)
    return "\n".join(lines)


def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def _run_command_gates(root: Path, profile: str, skip_tests: bool, runner: CommandRunner) -> list[dict[str, Any]]:
    policy_pack = "enterprise" if profile == "enterprise" else "team"
    gates: list[dict[str, Any]] = []
    if skip_tests:
        gates.append(
            {
                "id": "pytest",
                "label": "pytest",
                "status": "skipped",
                "required": True,
                "summary": "Skipped by --skip-tests",
                "elapsed_ms": 0,
            }
        )
    else:
        gates.append(
            _run_subprocess_gate(
                "pytest",
                "pytest",
                [sys.executable, "-m", "pytest", "-q"],
                REPO_ROOT,
                runner,
            )
        )

    command_specs = [
        (
            f"doctor-{policy_pack}",
            f"doctor {policy_pack}",
            [
                sys.executable,
                str(REPO_ROOT / "relay_kit_public_cli.py"),
                "doctor",
                str(root),
                "--skip-tests",
                "--policy-pack",
                policy_pack,
            ],
        ),
        (
            f"policy-{policy_pack}",
            f"policy {policy_pack}",
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "policy_guard.py"),
                str(root),
                "--strict",
                "--pack",
                policy_pack,
            ],
        ),
        (
            "workflow-eval",
            "workflow eval",
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "eval_workflows.py"),
                str(root),
                "--strict",
                "--json",
            ],
        ),
    ]
    manifest_command = [
        sys.executable,
        str(REPO_ROOT / "relay_kit_public_cli.py"),
        "manifest",
        "verify",
        str(root),
    ]
    if profile == "enterprise":
        manifest_command.append("--trusted")
        command_specs.insert(1, ("trusted-manifest", "trusted manifest", manifest_command))
    else:
        command_specs.insert(1, ("bundle-manifest", "bundle manifest", manifest_command))
    for gate_id, label, command in command_specs:
        gates.append(_run_subprocess_gate(gate_id, label, command, REPO_ROOT, runner))
    return gates


def _run_subprocess_gate(
    gate_id: str,
    label: str,
    command: list[str],
    cwd: Path,
    runner: CommandRunner,
) -> dict[str, Any]:
    started = time.perf_counter()
    result = runner(command, cwd)
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    status = "pass" if result.returncode == 0 else "fail"
    return {
        "id": gate_id,
        "label": label,
        "status": status,
        "required": True,
        "exit_code": result.returncode,
        "elapsed_ms": elapsed_ms,
        "summary": _summarize_output(result.stdout, result.stderr),
        "command": _command_text(command),
    }


def _support_bundle_gate(root: Path, profile: str, support_builder: SupportBuilder) -> dict[str, Any]:
    try:
        payload = support_builder(root, profile)
        ok = payload.get("schema_version") == SUPPORT_SCHEMA_VERSION
        return {
            "id": "support-bundle",
            "label": "support bundle",
            "status": "pass" if ok else "fail",
            "required": True,
            "summary": "support bundle schema ok" if ok else "support bundle schema mismatch",
        }
    except Exception as exc:  # pragma: no cover - defensive gate summary
        return _exception_gate("support-bundle", "support bundle", exc)


def _upgrade_gate(root: Path, upgrade_builder: UpgradeBuilder) -> dict[str, Any]:
    try:
        report = upgrade_builder(root)
        status = "pass" if report.get("status") == "pass" else "fail"
        return {
            "id": "upgrade-check",
            "label": "upgrade check",
            "status": status,
            "required": True,
            "summary": f"upgrade status: {report.get('status')}; findings: {report.get('findings_count', 0)}",
            "details": {
                "upgrade_status": report.get("upgrade_status"),
                "findings": report.get("findings", []),
                "actions": report.get("actions", []),
            },
        }
    except Exception as exc:  # pragma: no cover - defensive gate summary
        return _exception_gate("upgrade-check", "upgrade check", exc)


def _contract_sync_gate(
    root: Path,
    contract_exporter: ContractExporter,
    contract_importer: ContractImporter,
) -> dict[str, Any]:
    try:
        payload = contract_exporter(root)
        export_ok = payload.get("schema_version") == CONTRACT_EXPORT_SCHEMA_VERSION
        import_report = contract_importer(root, payload)
        import_ok = (
            import_report.get("schema_version") == CONTRACT_IMPORT_SCHEMA_VERSION
            and import_report.get("status") in {"pass", "hold"}
        )
        return {
            "id": "contract-sync",
            "label": "contract sync",
            "status": "pass" if export_ok and import_ok else "fail",
            "required": True,
            "summary": f"export schema: {payload.get('schema_version')}; import status: {import_report.get('status')}",
        }
    except Exception as exc:  # pragma: no cover - defensive gate summary
        return _exception_gate("contract-sync", "contract sync", exc)


def _commercial_docs_gate(root: Path) -> dict[str, Any]:
    missing = [rel for rel in COMMERCIAL_DOCS if not (root / rel).exists()]
    return {
        "id": "commercial-docs",
        "label": "commercial docs",
        "status": "pass" if not missing else "fail",
        "required": True,
        "summary": "all required commercial docs exist" if not missing else f"missing: {', '.join(missing)}",
        "details": {"missing": missing},
    }


def _default_support_builder(root: Path, policy_pack: str) -> Mapping[str, Any]:
    return build_support_bundle(root, policy_pack=policy_pack)


def _default_upgrade_builder(root: Path) -> Mapping[str, Any]:
    return build_upgrade_report(root)


def _default_contract_exporter(root: Path) -> Mapping[str, Any]:
    return export_contracts(root)


def _default_contract_importer(root: Path, payload: Mapping[str, Any]) -> Mapping[str, Any]:
    tmp_dir = root / ".relay-kit" / "contract-sync"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            delete=False,
            dir=tmp_dir,
            prefix="readiness-",
            suffix=".json",
        ) as handle:
            json.dump(payload, handle, ensure_ascii=True, indent=2)
            handle.write("\n")
            tmp_path = Path(handle.name)
        return import_contracts(root, contract_file=tmp_path, apply=False)
    finally:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink()


def _exception_gate(gate_id: str, label: str, exc: Exception) -> dict[str, Any]:
    return {
        "id": gate_id,
        "label": label,
        "status": "fail",
        "required": True,
        "summary": f"{type(exc).__name__}: {exc}",
    }


def _normalize_profile(profile: str) -> str:
    value = str(profile).strip().lower()
    if value not in PROFILES:
        raise ValueError(f"Unknown readiness profile: {profile!r}")
    return value


def _summarize_output(stdout: str, stderr: str) -> str:
    combined = "\n".join(part.strip() for part in [stdout, stderr] if part and part.strip())
    if not combined:
        return ""
    lines = combined.splitlines()
    return "\n".join(lines[:12])


def _command_text(command: Sequence[str]) -> str:
    return " ".join(str(part) for part in command)
