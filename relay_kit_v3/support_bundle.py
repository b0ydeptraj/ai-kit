"""Support bundle generation for Relay-kit paid/team diagnostics."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from relay_kit_v3 import bundle_manifest
from relay_kit_v3.evidence_ledger import summarize_events
from relay_kit_v3.policy_packs import DEFAULT_POLICY_PACK, get_policy_pack
from relay_kit_v3.upgrade import build_upgrade_report, inspect_manifest
from scripts import eval_workflows, policy_guard


SCHEMA_VERSION = "relay-kit.support-bundle.v1"
DEFAULT_OUTPUT = Path(".relay-kit") / "support" / "support-bundle.json"

REDACTION_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
)


def build_support_bundle(
    project_root: Path | str,
    *,
    policy_pack: str = DEFAULT_POLICY_PACK,
    evidence_limit: int = 20,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    pack = get_policy_pack(policy_pack)
    evidence_summary = summarize_events(root, limit=evidence_limit)
    manifest_status = inspect_manifest(root)
    policy_findings = policy_guard.collect_findings(root, pack_name=pack.name)
    workflow_eval = eval_workflows.build_report(root)

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _utc_timestamp(),
        "project_path": str(root),
        "package": dict(bundle_manifest.create_manifest()["package"]),
        "support": {
            "severity_levels": severity_levels(),
            "required_commands": required_commands(root, pack.name),
            "include_this_file": str(root / DEFAULT_OUTPUT),
        },
        "diagnostics": {
            "evidence_summary": {
                "ledger_path": str(evidence_summary.ledger_path),
                "total_events": evidence_summary.total_events,
                "status_counts": evidence_summary.status_counts,
                "gate_counts": evidence_summary.gate_counts,
                "recent_events": evidence_summary.recent_events,
            },
            "upgrade_report": build_upgrade_report(root),
            "manifest": {
                "status": manifest_status["status"],
                "path": str(manifest_status["path"]),
                "hash": manifest_status["hash"],
                "findings": manifest_status["findings"],
            },
            "policy": {
                "pack": pack.name,
                "description": pack.description,
                "findings_count": len(policy_findings),
                "findings": [
                    {
                        "path": finding.path,
                        "line": finding.line,
                        "check": finding.check,
                        "detail": finding.detail,
                    }
                    for finding in policy_findings
                ],
            },
            "workflow_eval": {
                "schema_version": workflow_eval["schema_version"],
                "status": workflow_eval["status"],
                "scenario_count": workflow_eval["scenario_count"],
                "passed": workflow_eval["passed"],
                "failed": workflow_eval["failed"],
                "pass_rate": workflow_eval["pass_rate"],
                "findings_count": workflow_eval["findings_count"],
                "findings": workflow_eval["findings"],
            },
        },
    }
    return redact_value(payload)


def write_support_bundle(
    project_root: Path | str,
    *,
    policy_pack: str = DEFAULT_POLICY_PACK,
    output_file: Path | str | None = None,
    evidence_limit: int = 20,
) -> Path:
    root = Path(project_root).resolve()
    output_path = Path(output_file) if output_file is not None else root / DEFAULT_OUTPUT
    if not output_path.is_absolute():
        output_path = root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_support_bundle(root, policy_pack=policy_pack, evidence_limit=evidence_limit)
    output_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return output_path


def severity_levels() -> list[dict[str, str]]:
    return [
        {
            "severity": "P0",
            "meaning": "Runtime install, doctor, or policy gate is blocked for a production-critical team.",
            "target": "same business day triage target for paid support",
        },
        {
            "severity": "P1",
            "meaning": "Upgrade, manifest, policy, or routing regression blocks a planned release.",
            "target": "next business day triage target for paid support",
        },
        {
            "severity": "P2",
            "meaning": "Workflow quality, docs, generated artifacts, or support tooling is degraded but has a workaround.",
            "target": "two business day triage target",
        },
        {
            "severity": "P3",
            "meaning": "Question, enhancement request, documentation issue, or non-blocking polish.",
            "target": "best-effort triage in the next support review window",
        },
    ]


def required_commands(project_root: Path, policy_pack: str) -> list[str]:
    project = _shell_arg(project_root)
    manifest_verify = f"relay-kit manifest verify {project}"
    if policy_pack == "enterprise":
        manifest_verify += " --trusted"
    return [
        f"relay-kit doctor {project} --policy-pack {policy_pack} --json",
        f"relay-kit policy check {project} --pack {policy_pack} --strict --json",
        manifest_verify,
        f"relay-kit upgrade check {project} --json",
        f"relay-kit eval run {project} --strict --json",
        f"relay-kit support bundle {project} --policy-pack {policy_pack}",
    ]


def redact_value(value: Any) -> Any:
    if isinstance(value, str):
        redacted = value
        for pattern in REDACTION_PATTERNS:
            redacted = pattern.sub("[REDACTED]", redacted)
        return redacted
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): redact_value(item) for key, item in value.items()}
    return value


def _shell_arg(path: Path) -> str:
    value = str(path)
    if any(char.isspace() for char in value):
        return f'"{value}"'
    return value


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
