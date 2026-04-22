#!/usr/bin/env python3
"""Prompt fidelity guard for Relay-kit projects.

Validates intent-lock/entity-lock artifacts and asked-vs-delivered drift evidence
for edit requests when fidelity policy is enforced.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from relay_kit_compat import CANONICAL_ARTIFACT_ROOT
from relay_kit_v3.fidelity_policy import (
    load_fidelity_policy,
    policy_file,
    should_enforce_fidelity,
    workflow_marker,
)


INTENT_REQUIRED_SECTIONS = [
    "Primary request",
    "Allowed changes",
    "Forbidden changes",
    "Target objects",
    "Done signal",
    "Ambiguities and holds",
]

ENTITY_REQUIRED_SECTIONS = [
    "Entity IDs",
    "Allowed edit scope",
    "Forbidden edit scope",
    "Ambiguous regions",
    "Verification checklist",
]


@dataclass(frozen=True)
class Finding:
    path: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate intent-fidelity lock artifacts and drift evidence for edit requests.",
    )
    parser.add_argument("project_path", nargs="?", default=".", help="Target project root")
    parser.add_argument("--strict", action="store_true", help="Compatibility flag; gate behavior remains policy-driven")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    return parser.parse_args()


def rel(base: Path, path: Path) -> str:
    return path.relative_to(base).as_posix()


def has_section(markdown: str, section: str) -> bool:
    pattern = rf"^##\s+{re.escape(section)}\s*$"
    return re.search(pattern, markdown, flags=re.MULTILINE | re.IGNORECASE) is not None


def _lower(value: str | None, fallback: str = "unknown") -> str:
    if value is None:
        return fallback
    cleaned = value.strip().lower()
    return cleaned if cleaned else fallback


def _collect_required_markers(base: Path) -> dict[str, str]:
    return {
        "request_class": _lower(workflow_marker(base, "Request class")),
        "media_involved": _lower(workflow_marker(base, "Media involved")),
        "intent_required": _lower(workflow_marker(base, "Intent-lock required"), fallback="no"),
        "intent_status": _lower(workflow_marker(base, "Intent-lock status")),
        "entity_required": _lower(workflow_marker(base, "Entity-lock required"), fallback="no"),
        "entity_status": _lower(workflow_marker(base, "Entity-lock status")),
        "fidelity_status": _lower(workflow_marker(base, "Prompt-fidelity-check status")),
    }


def _is_yes(value: str) -> bool:
    return value in {"yes", "true", "required"}


def _status_is_pass(value: str) -> bool:
    return value in {"pass", "passed", "ok", "done"}


def collect_findings(base: Path) -> tuple[dict[str, object], List[Finding]]:
    policy = load_fidelity_policy(base)
    gate = str(policy.get("gate", "hard"))
    enabled = bool(policy.get("enabled", True))
    scope = str(policy.get("scope", "all-edits"))
    enforce = should_enforce_fidelity(policy, base)

    markers = _collect_required_markers(base)
    meta: dict[str, object] = {
        "enabled": enabled,
        "gate": gate,
        "scope": scope,
        "enforced": enforce,
        "policy_path": rel(base, policy_file(base)),
        "workflow_markers": markers,
    }

    if not enforce:
        meta["status"] = "skipped"
        return meta, []

    findings: List[Finding] = []
    contracts_dir = base / CANONICAL_ARTIFACT_ROOT / "contracts"
    intent_path = contracts_dir / "intent-contract.md"
    entity_path = contracts_dir / "entity-map.md"
    qa_path = contracts_dir / "qa-report.md"

    intent_required = _is_yes(markers["intent_required"]) or markers["request_class"] == "edit"
    media_involved = _is_yes(markers["media_involved"]) or markers["request_class"] in {"media-ui", "edit-media"}
    entity_required = _is_yes(markers["entity_required"]) or media_involved

    if intent_required and not _status_is_pass(markers["intent_status"]):
        findings.append(
            Finding(
                rel(base, base / CANONICAL_ARTIFACT_ROOT / "state" / "workflow-state.md"),
                "Intent-lock status must be pass for enforced edit request",
            )
        )

    if intent_required:
        if not intent_path.exists():
            findings.append(Finding(rel(base, intent_path), "Missing required intent-contract artifact"))
        else:
            intent_content = intent_path.read_text(encoding="utf-8", errors="ignore")
            for section in INTENT_REQUIRED_SECTIONS:
                if not has_section(intent_content, section):
                    findings.append(Finding(rel(base, intent_path), f"Missing required section: {section}"))

    if entity_required and not _status_is_pass(markers["entity_status"]):
        findings.append(
            Finding(
                rel(base, base / CANONICAL_ARTIFACT_ROOT / "state" / "workflow-state.md"),
                "Entity-lock status must be pass when media/UI entities are involved",
            )
        )

    if entity_required:
        if not entity_path.exists():
            findings.append(Finding(rel(base, entity_path), "Missing required entity-map artifact"))
        else:
            entity_content = entity_path.read_text(encoding="utf-8", errors="ignore")
            for section in ENTITY_REQUIRED_SECTIONS:
                if not has_section(entity_content, section):
                    findings.append(Finding(rel(base, entity_path), f"Missing required section: {section}"))

    if not qa_path.exists():
        findings.append(Finding(rel(base, qa_path), "Missing qa-report for prompt-fidelity verification"))
    else:
        qa_content = qa_path.read_text(encoding="utf-8", errors="ignore")
        if not has_section(qa_content, "Asked vs Delivered"):
            findings.append(Finding(rel(base, qa_path), "Missing required section: Asked vs Delivered"))
        if not has_section(qa_content, "Drift verdict (pass/fail + reason)"):
            findings.append(Finding(rel(base, qa_path), "Missing required section: Drift verdict (pass/fail + reason)"))
        drift_match = re.search(
            r"^##\s+Drift verdict \(pass/fail \+ reason\)\s*$",
            qa_content,
            flags=re.IGNORECASE | re.MULTILINE,
        )
        if drift_match is not None:
            tail = qa_content[drift_match.end() :].splitlines()
            drift_text = " ".join(line.strip() for line in tail[:6] if line.strip()).lower()
            if "pass" not in drift_text:
                findings.append(Finding(rel(base, qa_path), "Drift verdict must explicitly include pass"))

    if not _status_is_pass(markers["fidelity_status"]):
        findings.append(
            Finding(
                rel(base, base / CANONICAL_ARTIFACT_ROOT / "state" / "workflow-state.md"),
                "Prompt-fidelity-check status must be pass before completion claim",
            )
        )

    meta["status"] = "ok" if not findings else "failed"
    return meta, findings


def render_text(meta: dict[str, object], findings: List[Finding]) -> str:
    markers = meta.get("workflow_markers", {})
    lines = [
        "Prompt fidelity guard report",
        f"- policy: enabled={meta.get('enabled')} gate={meta.get('gate')} scope={meta.get('scope')}",
        f"- enforced: {meta.get('enforced')}",
        f"- policy_path: {meta.get('policy_path')}",
        f"- workflow_markers: {markers}",
        f"- findings: {len(findings)}",
    ]
    if meta.get("status") == "skipped":
        lines.append("- status: skipped (policy disabled, gate off, or scope does not apply)")
        return "\n".join(lines)
    if findings:
        lines.append("")
        lines.append("Top findings:")
        for item in findings[:50]:
            lines.append(f"- {item.path}: {item.detail}")
        if len(findings) > 50:
            lines.append(f"- ... and {len(findings) - 50} more")
    return "\n".join(lines)


def render_json(meta: dict[str, object], findings: List[Finding]) -> str:
    payload = {
        "policy": {
            "enabled": meta.get("enabled"),
            "gate": meta.get("gate"),
            "scope": meta.get("scope"),
            "policy_path": meta.get("policy_path"),
        },
        "enforced": meta.get("enforced"),
        "workflow_markers": meta.get("workflow_markers"),
        "status": meta.get("status"),
        "findings_count": len(findings),
        "findings": [{"path": item.path, "detail": item.detail} for item in findings],
    }
    return json.dumps(payload, ensure_ascii=True, indent=2)


def main() -> int:
    args = parse_args()
    base = Path(args.project_path).resolve()
    meta, findings = collect_findings(base)

    if args.json:
        print(render_json(meta, findings))
    else:
        print(render_text(meta, findings))

    gate = str(meta.get("gate", "off"))
    if findings and gate == "hard":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
