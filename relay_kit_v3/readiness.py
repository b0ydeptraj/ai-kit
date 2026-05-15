"""Commercial readiness checks for Relay-kit."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from relay_kit_v3.contract_export import SCHEMA_VERSION as CONTRACT_EXPORT_SCHEMA_VERSION
from relay_kit_v3.contract_export import export_contracts
from relay_kit_v3.contract_import import IMPORT_SCHEMA_VERSION as CONTRACT_IMPORT_SCHEMA_VERSION
from relay_kit_v3.contract_import import import_contracts
from relay_kit_v3.release_lane import build_release_lane_report
from relay_kit_v3.adapter_diagnostics import build_adapter_diagnostics
from relay_kit_v3.agent_profiles import build_agent_diagnostics
from relay_kit_v3.runtime_locale import inspect_runtime_locale
from relay_kit_v3.real_world_eval import build_report as build_real_world_eval_report
from relay_kit_v3.skill_proof import build_report as build_skill_proof_report
from relay_kit_v3.support_bundle import SCHEMA_VERSION as SUPPORT_SCHEMA_VERSION
from relay_kit_v3.support_bundle import build_support_bundle
from relay_kit_v3.support_triage import support_bundle_findings
from relay_kit_v3.temp_paths import temp_dir
from relay_kit_v3.token_economy import build_token_audit
from relay_kit_v3.upgrade import build_upgrade_report


SCHEMA_VERSION = "relay-kit.readiness-report.v1"
PROFILES = {"team", "enterprise"}
REPO_ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DOCS = [
    "docs/relay-kit-support-sla.md",
    "docs/relay-kit-enterprise-bundle.md",
    "docs/relay-kit-contract-sync.md",
    "docs/relay-kit-commercial-dossier.md",
    "docs/relay-kit-adapter-diagnostics.md",
    "docs/relay-kit-locale-policy.md",
    ".relay-kit/contracts/support-request.md",
]
READINESS_PYTEST_BASETEMP = Path(".tmp") / "readiness-pytest"
READINESS_MAX_WORKFLOW_WEAK_ROUTES = 0
READINESS_MIN_WORKFLOW_ROUTE_MARGIN = 4

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
    gates.append(_adapter_diagnostics_gate(root))
    gates.append(_agent_profiles_gate(root))
    gates.append(_runtime_locale_gate(root))
    gates.append(_token_economy_gate(root))
    gates.append(_real_world_skill_eval_gate(root))
    gates.append(_skill_proof_audit_gate(root))
    gates.append(_signal_export_gate(root, selected_profile))
    gates.append(_release_lane_gate(root))
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
        "Remote CI result, release upload, and paid support operations are not verified by this local gate.",
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
                [sys.executable, "-m", "pytest", "-q", "--basetemp", str(READINESS_PYTEST_BASETEMP)],
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
        if gate_id == "workflow-eval":
            gates.append(_run_workflow_eval_gate(command, REPO_ROOT, runner))
        else:
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


def _run_workflow_eval_gate(
    command: list[str],
    cwd: Path,
    runner: CommandRunner,
) -> dict[str, Any]:
    started = time.perf_counter()
    result = runner(command, cwd)
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    summary = _summarize_output(result.stdout, result.stderr)
    gate: dict[str, Any] = {
        "id": "workflow-eval",
        "label": "workflow eval",
        "status": "pass" if result.returncode == 0 else "fail",
        "required": True,
        "exit_code": result.returncode,
        "elapsed_ms": elapsed_ms,
        "summary": summary,
        "command": _command_text(command),
    }
    if result.returncode != 0:
        return gate

    details, findings = _workflow_eval_quality_details(result.stdout)
    gate["details"] = details
    if findings:
        gate["status"] = "fail"
        gate["summary"] = "; ".join(findings)
    else:
        gate["summary"] = (
            f"workflow eval route quality ok; scenarios: {details.get('scenario_count', 0)}; "
            f"min route margin: {details.get('min_route_margin', 0)}; "
            f"weak routes: {details.get('weak_route_count', 0)}"
        )
    return gate


def _workflow_eval_quality_details(stdout: str) -> tuple[dict[str, Any], list[str]]:
    findings: list[str] = []
    details: dict[str, Any] = {
        "scenario_count": 0,
        "min_route_margin": 0,
        "weak_route_count": 0,
        "weak_routes": [],
        "min_route_margin_required": READINESS_MIN_WORKFLOW_ROUTE_MARGIN,
        "max_weak_routes_allowed": READINESS_MAX_WORKFLOW_WEAK_ROUTES,
    }
    try:
        payload = json.loads(stdout.strip())
    except json.JSONDecodeError as exc:
        findings.append(f"workflow eval JSON parse failed: {exc.msg}")
        return details, findings
    if not isinstance(payload, Mapping):
        findings.append("workflow eval output is not a JSON object")
        return details, findings

    quality = payload.get("quality", {})
    if not isinstance(quality, Mapping):
        findings.append("workflow eval quality block missing")
        return details, findings

    scenario_count = _int_value(payload.get("scenario_count"))
    min_route_margin = _int_value(quality.get("min_route_margin"))
    weak_route_count = _int_value(quality.get("weak_route_count"))
    weak_routes = quality.get("weak_routes", [])
    if not isinstance(weak_routes, list):
        weak_routes = []

    details.update(
        {
            "scenario_count": scenario_count,
            "min_route_margin": min_route_margin,
            "weak_route_count": weak_route_count,
            "weak_routes": weak_routes[:8],
        }
    )
    if weak_route_count > READINESS_MAX_WORKFLOW_WEAK_ROUTES:
        findings.append(
            f"workflow eval weak routes: {weak_route_count} "
            f"(allowed: {READINESS_MAX_WORKFLOW_WEAK_ROUTES})"
        )
    if min_route_margin < READINESS_MIN_WORKFLOW_ROUTE_MARGIN:
        findings.append(
            f"workflow eval min route margin: {min_route_margin} "
            f"(required: {READINESS_MIN_WORKFLOW_ROUTE_MARGIN})"
        )
    return details, findings


def _support_bundle_gate(root: Path, profile: str, support_builder: SupportBuilder) -> dict[str, Any]:
    try:
        payload = support_builder(root, profile)
        schema_ok = payload.get("schema_version") == SUPPORT_SCHEMA_VERSION
        findings = support_bundle_findings(payload) if schema_ok else []
        ok = schema_ok and not findings
        return {
            "id": "support-bundle",
            "label": "support bundle",
            "status": "pass" if ok else "fail",
            "required": True,
            "summary": _support_bundle_summary(schema_ok, findings),
            "details": {"findings_count": len(findings), "findings": findings},
        }
    except Exception as exc:  # pragma: no cover - defensive gate summary
        return _exception_gate("support-bundle", "support bundle", exc)


def _support_bundle_summary(schema_ok: bool, findings: Sequence[Mapping[str, str]]) -> str:
    if not schema_ok:
        return "support bundle schema mismatch"
    if findings:
        return f"support bundle diagnostics have {len(findings)} findings"
    return "support bundle diagnostics ok"


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


def _adapter_diagnostics_gate(root: Path) -> dict[str, Any]:
    try:
        report = build_adapter_diagnostics(root, adapter="all")
        findings = report.get("findings", [])
        ok = report.get("status") == "pass"
        return {
            "id": "adapter-diagnostics",
            "label": "adapter diagnostics",
            "status": "pass" if ok else "fail",
            "required": True,
            "summary": (
                "adapter diagnostics ok"
                if ok
                else f"adapter diagnostics findings: {len(findings)}"
            ),
            "details": {
                "findings_count": len(findings),
                "summary": report.get("summary", {}),
                "adapters": report.get("adapters", []),
                "findings": findings[:12],
            },
        }
    except Exception as exc:  # pragma: no cover - defensive gate summary
        return _exception_gate("adapter-diagnostics", "adapter diagnostics", exc)


def _signal_export_gate(root: Path, profile: str) -> dict[str, Any]:
    try:
        from relay_kit_v3.pulse import build_pulse_report, write_pulse_report
        from relay_kit_v3.signal_export import SCHEMA_VERSION as SIGNAL_EXPORT_SCHEMA_VERSION
        from relay_kit_v3.signal_export import build_signal_export, write_signal_export

        with temp_dir(root, "readiness-pulse") as work_dir:
            pulse_report = build_pulse_report(
                root,
                profile=profile,
                include_readiness=False,
                skip_tests=True,
                output_dir=work_dir,
            )
            pulse_outputs = write_pulse_report(
                root,
                pulse_report,
                output_dir=work_dir,
                record_history=False,
            )
            payload = build_signal_export(root, pulse_file=pulse_outputs["json"])
        outputs = write_signal_export(root, payload, include_otlp=True)
        summary = payload.get("summary", {})
        signal_count = int(summary.get("signal_count", 0))
        ok = (
            payload.get("schema_version") == SIGNAL_EXPORT_SCHEMA_VERSION
            and signal_count > 0
            and outputs["json"].exists()
            and outputs["jsonl"].exists()
            and outputs["otlp"].exists()
        )
        return {
            "id": "signal-export",
            "label": "signal export",
            "status": "pass" if ok else "fail",
            "required": True,
            "summary": f"signals: {signal_count}; schema: {payload.get('schema_version')}",
            "details": {
                "signal_count": signal_count,
                "metric_count": summary.get("metric_count", 0),
                "event_count": summary.get("event_count", 0),
                "json": str(outputs["json"]),
                "jsonl": str(outputs["jsonl"]),
                "otlp": str(outputs["otlp"]),
            },
        }
    except Exception as exc:  # pragma: no cover - defensive gate summary
        return _exception_gate("signal-export", "signal export", exc)


def _token_economy_gate(root: Path) -> dict[str, Any]:
    try:
        # Enterprise readiness uses a wider budget envelope than the interactive
        # default so repositories with complete governance artifacts do not fail
        # purely due to baseline context volume.
        report = build_token_audit(root, max_tokens=40000)
        metrics = report.get("metrics", {})
        findings = report.get("findings", [])
        ok = report.get("status") == "pass"
        return {
            "id": "token-economy",
            "label": "token economy",
            "status": "pass" if ok else "fail",
            "required": True,
            "summary": (
                "token economy audit ok"
                if ok
                else f"token economy findings: {len(findings)}"
            ),
            "details": {
                "metrics": metrics,
                "findings_count": len(findings),
                "findings": findings[:12],
            },
        }
    except Exception as exc:  # pragma: no cover - defensive gate summary
        return _exception_gate("token-economy", "token economy", exc)


def _real_world_skill_eval_gate(root: Path) -> dict[str, Any]:
    try:
        report = build_real_world_eval_report(root)
        findings = report.get("findings", [])
        ok = report.get("status") == "pass"
        return {
            "id": "real-world-skill-eval",
            "label": "real-world skill eval",
            "status": "pass" if ok else "fail",
            "required": True,
            "summary": (
                f"real-world skill cases passed: {report.get('passed', 0)}/{report.get('case_count', 0)}"
                if ok
                else f"real-world skill eval findings: {len(findings)}"
            ),
            "details": {
                "case_count": report.get("case_count", 0),
                "passed": report.get("passed", 0),
                "failed": report.get("failed", 0),
                "findings_count": len(findings),
                "findings": findings[:12],
            },
        }
    except Exception as exc:  # pragma: no cover - defensive gate summary
        return _exception_gate("real-world-skill-eval", "real-world skill eval", exc)


def _skill_proof_audit_gate(root: Path) -> dict[str, Any]:
    try:
        report = build_skill_proof_report(root, strict=True)
        findings = report.get("findings", [])
        summary = report.get("summary", {})
        ok = report.get("status") == "pass"
        return {
            "id": "skill-proof-audit",
            "label": "skill proof audit",
            "status": "pass" if ok else "fail",
            "required": True,
            "summary": (
                "skill proof audit ok"
                if ok
                else f"theoretical skills: {summary.get('theoretical', 0)}"
            ),
            "details": {
                "summary": summary,
                "findings_count": len(findings),
                "findings": findings[:12],
            },
        }
    except Exception as exc:  # pragma: no cover - defensive gate summary
        return _exception_gate("skill-proof-audit", "skill proof audit", exc)


def _agent_profiles_gate(root: Path) -> dict[str, Any]:
    try:
        report = build_agent_diagnostics(root, adapter="all")
        findings = report.get("findings", [])
        ok = report.get("status") == "pass"
        return {
            "id": "agent-profiles",
            "label": "agent profiles",
            "status": "pass" if ok else "fail",
            "required": True,
            "summary": (
                "agent profile diagnostics ok"
                if ok
                else f"agent profile diagnostics findings: {len(findings)}"
            ),
            "details": {
                "findings_count": len(findings),
                "summary": report.get("summary", {}),
                "adapters": report.get("adapters", []),
                "findings": findings[:12],
            },
        }
    except Exception as exc:  # pragma: no cover - defensive gate summary
        return _exception_gate("agent-profiles", "agent profiles", exc)


def _runtime_locale_gate(root: Path) -> dict[str, Any]:
    try:
        report = inspect_runtime_locale(root)
        findings = report.get("findings", [])
        ok = report.get("status") == "pass"
        return {
            "id": "runtime-locale",
            "label": "runtime locale",
            "status": "pass" if ok else "fail",
            "required": True,
            "summary": (
                "runtime locale policy ok"
                if ok
                else f"runtime locale findings: {len(findings)}"
            ),
            "details": {
                "summary": report.get("summary", {}),
                "findings_count": len(findings),
                "findings": findings[:12],
            },
        }
    except Exception as exc:  # pragma: no cover - defensive gate summary
        return _exception_gate("runtime-locale", "runtime locale", exc)


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


def _release_lane_gate(root: Path) -> dict[str, Any]:
    try:
        report = build_release_lane_report(root)
        return {
            "id": "release-lane",
            "label": "release lane",
            "status": "pass" if report.get("status") == "pass" else "fail",
            "required": True,
            "summary": f"release lane status: {report.get('status')}; findings: {len(report.get('findings', []))}",
            "details": {
                "findings": report.get("findings", []),
                "residual_risks": report.get("residual_risks", []),
            },
        }
    except Exception as exc:  # pragma: no cover - defensive gate summary
        return _exception_gate("release-lane", "release lane", exc)


def _default_support_builder(root: Path, policy_pack: str) -> Mapping[str, Any]:
    return build_support_bundle(root, policy_pack=policy_pack)


def _default_upgrade_builder(root: Path) -> Mapping[str, Any]:
    return build_upgrade_report(root)


def _default_contract_exporter(root: Path) -> Mapping[str, Any]:
    return export_contracts(root)


def _default_contract_importer(root: Path, payload: Mapping[str, Any]) -> Mapping[str, Any]:
    with temp_dir(root, "contract-sync") as work_dir:
        tmp_path = work_dir / "readiness-contracts.json"
        tmp_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
        return import_contracts(root, contract_file=tmp_path, apply=False)


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


def _int_value(value: object) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0


def _command_text(command: Sequence[str]) -> str:
    return " ".join(str(part) for part in command)
