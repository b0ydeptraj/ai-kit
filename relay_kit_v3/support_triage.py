"""Support triage readiness report for Relay-kit paid/team support."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from relay_kit_v3.support_bundle import DEFAULT_OUTPUT as DEFAULT_BUNDLE_OUTPUT
from relay_kit_v3.support_bundle import SCHEMA_VERSION as SUPPORT_BUNDLE_SCHEMA_VERSION
from relay_kit_v3.support_bundle import redact_value, severity_levels
from relay_kit_v3.support_request import DEFAULT_DIAGNOSTICS, build_support_request
from relay_kit_v3.support_request import DEFAULT_OUTPUT as DEFAULT_REQUEST_OUTPUT
from relay_kit_v3.support_request import SCHEMA_VERSION as SUPPORT_REQUEST_SCHEMA_VERSION


SCHEMA_VERSION = "relay-kit.support-triage.v1"
SOAK_SCHEMA_VERSION = "relay-kit.support-soak.v1"
SOAK_SEVERITIES = ("P0", "P1", "P2")


def build_support_triage(
    project_root: Path | str,
    *,
    request_file: Path | str | None = None,
    bundle_file: Path | str | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    request_path = _resolve_path(root, request_file, DEFAULT_REQUEST_OUTPUT)
    bundle_path = _resolve_path(root, bundle_file, DEFAULT_BUNDLE_OUTPUT)
    request_payload = _read_json_object(request_path)
    bundle_payload = _read_json_object(bundle_path)

    request_check = support_request_check(request_path, request_payload)
    bundle_check = support_bundle_check(bundle_path, bundle_payload)
    checks = [request_check, bundle_check]
    request = request_payload if isinstance(request_payload, Mapping) else {}
    severity = str(request.get("severity") or "")
    sla = severity_sla(severity)
    findings = [
        {
            "gate": str(check["id"]),
            "status": str(check["status"]),
            "summary": str(check["summary"]),
        }
        for check in checks
        if check["status"] != "pass"
    ]
    status = "ready" if not findings else "hold"
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "project_path": str(root),
        "severity": severity,
        "sla": sla,
        "request_file": str(request_path),
        "bundle_file": str(bundle_path),
        "checks": checks,
        "checks_by_id": {str(check["id"]): check for check in checks},
        "findings": findings,
        "next_actions": support_triage_next_actions(status, request_check, bundle_check),
        "residual_risks": [
            "Support triage validates local artifacts only; it does not create a legal SLA commitment.",
            "Private customer environment access and reproduction steps remain external support workflow inputs.",
        ],
    }
    return redact_value(report)


def build_support_soak_report(
    project_root: Path | str,
    *,
    bundle_file: Path | str | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    bundle_path = _resolve_path(root, bundle_file, DEFAULT_BUNDLE_OUTPUT)
    bundle_payload = _read_json_object(bundle_path)
    bundle_check = support_bundle_check(bundle_path, bundle_payload)
    cases = [_support_soak_case(root, severity, bundle_check) for severity in SOAK_SEVERITIES]
    findings = [
        {
            "gate": str(case_finding["gate"]),
            "severity": str(case["severity"]),
            "summary": str(case_finding["summary"]),
        }
        for case in cases
        for case_finding in case["findings"]
    ]
    status = "pass" if not findings else "hold"
    report = {
        "schema_version": SOAK_SCHEMA_VERSION,
        "status": status,
        "project_path": str(root),
        "bundle_file": str(bundle_path),
        "case_count": len(cases),
        "cases": cases,
        "findings": findings,
        "next_actions": support_soak_next_actions(status, bundle_check),
    }
    return redact_value(report)


def render_support_triage(report: Mapping[str, Any]) -> str:
    sla = _mapping(report.get("sla"))
    lines = [
        "Relay-kit support triage",
        f"- project: {report.get('project_path')}",
        f"- severity: {report.get('severity') or '-'}",
        f"- target: {sla.get('target', '-')}",
        f"- status: {report.get('status')}",
        f"- findings: {len(report.get('findings', []))}",
    ]
    for finding in report.get("findings", []):
        if isinstance(finding, Mapping):
            lines.append(f"  - {finding.get('gate')}: {finding.get('summary')}")
    actions = report.get("next_actions", [])
    if actions:
        lines.append("- next actions:")
        lines.extend(f"  - {action}" for action in actions)
    return "\n".join(lines)


def render_support_soak_report(report: Mapping[str, Any]) -> str:
    lines = [
        "Relay-kit support soak",
        f"- project: {report.get('project_path')}",
        f"- status: {report.get('status')}",
        f"- cases: {report.get('case_count')}",
        f"- findings: {len(report.get('findings', []))}",
    ]
    for case in report.get("cases", []):
        if isinstance(case, Mapping):
            lines.append(f"  - {case.get('severity')}: {case.get('status')} ({case.get('summary')})")
    actions = report.get("next_actions", [])
    if actions:
        lines.append("- next actions:")
        lines.extend(f"  - {action}" for action in actions)
    return "\n".join(lines)


def support_request_check(path: Path, payload: Mapping[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return check("support-request", "support request", "hold", "missing or invalid support request", path=path)
    if payload.get("schema_version") != SUPPORT_REQUEST_SCHEMA_VERSION:
        return check("support-request", "support request", "hold", "support request schema does not match", path=path)
    if payload.get("status") != "ready":
        findings = payload.get("findings", [])
        count = len(findings) if isinstance(findings, list) else 0
        return check(
            "support-request",
            "support request",
            "hold",
            f"support request is {payload.get('status', 'unknown')} with {count} findings",
            path=path,
            details={"findings_count": count},
        )
    diagnostics = payload.get("diagnostics", [])
    missing = [
        str(item.get("path", ""))
        for item in diagnostics
        if isinstance(item, Mapping) and item.get("status") != "present"
    ]
    if missing:
        return check(
            "support-request",
            "support request",
            "hold",
            "support request has missing diagnostics",
            path=path,
            details={"missing_diagnostics": missing},
        )
    return check("support-request", "support request", "pass", "support request is ready", path=path)


def support_bundle_check(path: Path, payload: Mapping[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return check("support-bundle", "support bundle", "hold", "missing or invalid support bundle", path=path)
    if payload.get("schema_version") != SUPPORT_BUNDLE_SCHEMA_VERSION:
        return check("support-bundle", "support bundle", "hold", "support bundle schema does not match", path=path)
    findings = support_bundle_findings(payload)
    if findings:
        return check(
            "support-bundle",
            "support bundle",
            "hold",
            "support bundle diagnostics need attention",
            path=path,
            details={"findings_count": len(findings), "findings": findings},
        )
    return check("support-bundle", "support bundle", "pass", "support bundle is present", path=path)


def support_bundle_findings(payload: Mapping[str, Any]) -> list[dict[str, str]]:
    diagnostics = payload.get("diagnostics")
    if not isinstance(diagnostics, Mapping):
        return [bundle_finding("diagnostics", "support bundle diagnostics object is required")]

    findings: list[dict[str, str]] = []
    manifest = _mapping(diagnostics.get("manifest"))
    if manifest.get("status") != "valid":
        findings.append(bundle_finding("manifest", "manifest status must be valid"))

    policy = _mapping(diagnostics.get("policy"))
    policy_findings = _int_or_none(policy.get("findings_count"))
    if policy_findings is None:
        findings.append(bundle_finding("policy", "policy findings_count is required"))
    elif policy_findings != 0:
        findings.append(bundle_finding("policy", f"policy findings_count must be 0, got {policy_findings}"))

    workflow_eval = _mapping(diagnostics.get("workflow_eval"))
    if workflow_eval.get("status") != "pass":
        findings.append(bundle_finding("workflow-eval", "workflow eval status must be pass"))

    signal_export = _mapping(diagnostics.get("signal_export"))
    if signal_export.get("status") != "pass":
        findings.append(bundle_finding("signal-export", "signal export status must be pass"))

    release_lane = _mapping(diagnostics.get("release_lane"))
    if release_lane.get("status") != "pass":
        findings.append(bundle_finding("release-lane", "release lane status must be pass"))

    return findings


def bundle_finding(gate: str, summary: str) -> dict[str, str]:
    return {"gate": gate, "status": "hold", "summary": summary}


def support_triage_next_actions(
    status: str,
    request_check: Mapping[str, Any],
    bundle_check: Mapping[str, Any],
) -> list[str]:
    if status == "ready":
        return [
            "Open the support case with .relay-kit/support/support-request.json and .relay-kit/support/support-bundle.json.",
            "Include the failing command output and any private reproduction notes outside the repository.",
        ]
    actions: list[str] = []
    if bundle_check.get("status") != "pass":
        actions.append("Run relay-kit support bundle <project> --policy-pack enterprise before triage.")
        actions.extend(_bundle_next_actions(bundle_check))
    if request_check.get("status") != "pass":
        actions.append("Run relay-kit support request <project> --severity P1 --policy-pack enterprise --strict --json and fill missing fields.")
    return actions


def support_soak_next_actions(status: str, bundle_check: Mapping[str, Any]) -> list[str]:
    if status == "pass":
        return [
            "Use the P0, P1, and P2 soak cases as paid-support handoff fixtures.",
            "Attach the support soak output with the support bundle when validating support readiness.",
        ]
    actions = ["Run relay-kit support bundle <project> --policy-pack enterprise before support soak."]
    actions.extend(_bundle_next_actions(bundle_check))
    return actions


def severity_sla(severity: str) -> dict[str, str]:
    for item in severity_levels():
        if item.get("severity") == severity:
            return dict(item)
    return {
        "severity": severity,
        "meaning": "Unknown or missing severity.",
        "target": "triage target unavailable until severity is set",
    }


def _support_soak_case(root: Path, severity: str, bundle_check: Mapping[str, Any]) -> dict[str, Any]:
    scenario = _soak_scenario(severity)
    request = build_support_request(
        root,
        severity=severity,
        summary=scenario["summary"],
        package_version=scenario["package_version"],
        operating_system=scenario["operating_system"],
        shell=scenario["shell"],
        installed_bundle=scenario["installed_bundle"],
        adapter_target=scenario["adapter_target"],
        policy_pack=scenario["policy_pack"],
        expected_behavior=scenario["expected_behavior"],
        actual_behavior=scenario["actual_behavior"],
        recent_changes=scenario["recent_changes"],
        workaround=scenario["workaround"],
        diagnostic_files=[root / path for path in DEFAULT_DIAGNOSTICS],
    )
    request_check = support_request_check(
        root / ".relay-kit" / "support" / f"support-request-soak-{severity.lower()}.json",
        request,
    )
    findings = []
    if request_check["status"] != "pass":
        findings.append(
            {
                "gate": "support-request",
                "status": "hold",
                "summary": str(request_check["summary"]),
            }
        )
    if bundle_check["status"] != "pass":
        findings.append(
            {
                "gate": "support-bundle",
                "status": "hold",
                "summary": str(bundle_check["summary"]),
            }
        )
    return {
        "severity": severity,
        "status": "pass" if not findings else "hold",
        "summary": scenario["summary"],
        "sla": severity_sla(severity),
        "request_check": request_check,
        "bundle_check": bundle_check,
        "findings": findings,
    }


def _soak_scenario(severity: str) -> dict[str, str]:
    scenarios = {
        "P0": {
            "summary": "Production team cannot run Relay-kit doctor after a paid bundle upgrade.",
            "actual_behavior": "Doctor exits non-zero before the team can generate a release support bundle.",
            "workaround": "Pin the previous Relay-kit runtime bundle while support triages the blocker.",
        },
        "P1": {
            "summary": "Enterprise manifest trust verification fails during a planned release.",
            "actual_behavior": "Trusted manifest verification reports drift after a skill regeneration.",
            "workaround": "Regenerate and stamp manifest trust metadata before release.",
        },
        "P2": {
            "summary": "Workflow dashboard quality signals are degraded but the team can continue manually.",
            "actual_behavior": "Pulse shows attention because workflow eval coverage dropped below the expected threshold.",
            "workaround": "Use direct eval JSON while the dashboard signal is repaired.",
        },
    }
    selected = scenarios[severity]
    return {
        "package_version": "3.4.0",
        "operating_system": "Windows",
        "shell": "PowerShell",
        "installed_bundle": "enterprise",
        "adapter_target": "codex",
        "policy_pack": "enterprise",
        "expected_behavior": "Relay-kit support diagnostics should produce a complete paid-support handoff.",
        "recent_changes": "Updated support, readiness, dashboard, or publication gates before the support request.",
        **selected,
    }


def _bundle_next_actions(bundle_check: Mapping[str, Any]) -> list[str]:
    details = _mapping(bundle_check.get("details"))
    findings = details.get("findings", [])
    actions: list[str] = []
    for finding in findings if isinstance(findings, list) else []:
        if not isinstance(finding, Mapping):
            continue
        gate = str(finding.get("gate") or "")
        if gate == "policy":
            actions.append("Resolve policy findings and rerun relay-kit support bundle.")
        elif gate == "workflow-eval":
            actions.append("Rerun relay-kit eval run <project> --strict --json and fix failed workflow scenarios.")
        elif gate == "signal-export":
            actions.append("Regenerate signal export with relay-kit signal export <project> --otlp --json.")
        elif gate == "release-lane":
            actions.append("Run relay-kit release verify <project> --json and attach the release-lane findings.")
        elif gate == "manifest":
            actions.append("Regenerate or verify the bundle manifest before support triage.")
    return actions


def check(
    check_id: str,
    label: str,
    status: str,
    summary: str,
    *,
    path: Path,
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": check_id,
        "label": label,
        "status": status,
        "summary": summary,
        "details": {"path": str(path), **dict(details or {})},
    }


def _resolve_path(root: Path, value: Path | str | None, default: Path) -> Path:
    path = Path(value) if value is not None else root / default
    return path if path.is_absolute() else root / path


def _read_json_object(path: Path) -> Mapping[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, Mapping) else None


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _int_or_none(value: object) -> int | None:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
