"""Support request intake artifact for Relay-kit paid/team support."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from relay_kit_v3.support_bundle import redact_value, severity_levels


SCHEMA_VERSION = "relay-kit.support-request.v1"
DEFAULT_OUTPUT = Path(".relay-kit") / "support" / "support-request.json"
SEVERITIES = {"P0", "P1", "P2", "P3"}
DEFAULT_DIAGNOSTICS = [
    Path(".relay-kit") / "support" / "support-bundle.json",
    Path(".relay-kit") / "signals" / "relay-signals.json",
    Path(".relay-kit") / "signals" / "relay-signals.jsonl",
    Path(".relay-kit") / "signals" / "relay-signals-otlp.json",
]
TEXT_FIELDS = [
    "summary",
    "expected_behavior",
    "actual_behavior",
    "recent_changes",
    "workaround",
]
ENVIRONMENT_FIELDS = [
    "package_version",
    "operating_system",
    "shell",
    "installed_bundle",
    "adapter_target",
    "policy_pack",
]
PLACEHOLDER_VALUES = {"", "tbd", "todo", "n/a", "none", "describe", "one sentence"}


def build_support_request(
    project_root: Path | str,
    *,
    severity: str | None = None,
    summary: str | None = None,
    package_version: str | None = None,
    operating_system: str | None = None,
    shell: str | None = None,
    installed_bundle: str | None = None,
    adapter_target: str | None = None,
    policy_pack: str | None = None,
    expected_behavior: str | None = None,
    actual_behavior: str | None = None,
    recent_changes: str | None = None,
    workaround: str | None = None,
    diagnostic_files: Sequence[Path | str] | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    diagnostics = diagnostic_file_status(root, diagnostic_files)
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "ready",
        "project_path": str(root),
        "severity": _clean(severity),
        "severity_levels": severity_levels(),
        "summary": _clean(summary),
        "environment": {
            "package_version": _clean(package_version),
            "operating_system": _clean(operating_system),
            "shell": _clean(shell),
            "installed_bundle": _clean(installed_bundle),
            "adapter_target": _clean(adapter_target),
            "policy_pack": _clean(policy_pack),
        },
        "expected_behavior": _clean(expected_behavior),
        "actual_behavior": _clean(actual_behavior),
        "recent_changes": _clean(recent_changes),
        "workaround": _clean(workaround),
        "diagnostics": diagnostics,
        "findings": [],
    }
    findings = support_request_findings(payload)
    payload["status"] = "ready" if not findings else "hold"
    payload["findings"] = findings
    return redact_value(payload)


def write_support_request(
    project_root: Path | str,
    report: Mapping[str, Any],
    *,
    output_file: Path | str | None = None,
) -> Path:
    root = Path(project_root).resolve()
    output_path = Path(output_file) if output_file is not None else root / DEFAULT_OUTPUT
    if not output_path.is_absolute():
        output_path = root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return output_path


def render_support_request(report: Mapping[str, Any]) -> str:
    lines = [
        "Relay-kit support request",
        f"- project: {report.get('project_path')}",
        f"- severity: {report.get('severity')}",
        f"- status: {report.get('status')}",
        f"- diagnostics: {len(report.get('diagnostics', []))}",
        f"- findings: {len(report.get('findings', []))}",
    ]
    for finding in report.get("findings", []):
        if isinstance(finding, Mapping):
            lines.append(f"  - {finding.get('gate')}: {finding.get('summary')}")
    return "\n".join(lines)


def support_request_findings(report: Mapping[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    severity = str(report.get("severity") or "")
    if severity not in SEVERITIES:
        findings.append(finding("severity", f"severity must be one of {', '.join(sorted(SEVERITIES))}"))
    for field in TEXT_FIELDS:
        if _is_missing(report.get(field)):
            findings.append(finding(field, f"{field} is required"))
    environment = report.get("environment", {})
    env = environment if isinstance(environment, Mapping) else {}
    for field in ENVIRONMENT_FIELDS:
        if _is_missing(env.get(field)):
            findings.append(finding(field, f"environment.{field} is required"))
    diagnostics = report.get("diagnostics", [])
    missing_diagnostics = [
        item.get("path", "")
        for item in diagnostics
        if isinstance(item, Mapping) and item.get("status") != "present"
    ]
    if missing_diagnostics:
        findings.append(finding("diagnostics", "missing diagnostics: " + ", ".join(missing_diagnostics)))
    if not diagnostics:
        findings.append(finding("diagnostics", "at least one diagnostic file is required"))
    return findings


def diagnostic_file_status(root: Path, diagnostic_files: Sequence[Path | str] | None) -> list[dict[str, Any]]:
    paths = [Path(value) for value in diagnostic_files] if diagnostic_files is not None else DEFAULT_DIAGNOSTICS
    diagnostics: list[dict[str, Any]] = []
    for path in paths:
        resolved = path if path.is_absolute() else root / path
        diagnostics.append(
            {
                "path": str(resolved),
                "status": "present" if resolved.exists() else "missing",
                "size_bytes": resolved.stat().st_size if resolved.exists() else 0,
            }
        )
    return diagnostics


def finding(gate: str, summary: str) -> dict[str, str]:
    return {"gate": gate, "status": "hold", "summary": summary}


def _clean(value: object) -> str:
    return str(value or "").strip()


def _is_missing(value: object) -> bool:
    text = _clean(value)
    lowered = text.lower()
    if lowered in PLACEHOLDER_VALUES:
        return True
    return any(lowered == placeholder for placeholder in PLACEHOLDER_VALUES)
