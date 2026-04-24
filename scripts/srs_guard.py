#!/usr/bin/env python3
"""Policy-driven SRS traceability guard for Relay-kit projects."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from relay_kit_compat import CANONICAL_ARTIFACT_ROOT
from relay_kit_v3.srs_policy import load_srs_policy, policy_file, should_enforce_srs


REQUIRED_SECTIONS = [
    "Goal",
    "Actors",
    "Use Cases",
    "Preconditions",
    "Main Flows",
    "Postconditions",
    "Exception Flows",
    "Business Rules",
    "Acceptance Examples",
    "Open Questions",
]

UC_ID_PATTERN = re.compile(r"\bUC-[A-Z0-9][A-Z0-9_-]*\b", re.IGNORECASE)


@dataclass(frozen=True)
class Finding:
    path: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate SRS-first structure and traceability based on .relay-kit/state/srs-policy.json",
    )
    parser.add_argument("project_path", nargs="?", default=".", help="Target project root")
    parser.add_argument("--strict", action="store_true", help="Compatibility flag; gate behavior is policy-driven")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    return parser.parse_args()


def rel(base: Path, path: Path) -> str:
    return path.relative_to(base).as_posix()


def has_section(markdown: str, section: str) -> bool:
    pattern = rf"^##\s+{re.escape(section)}\s*$"
    return re.search(pattern, markdown, flags=re.MULTILINE | re.IGNORECASE) is not None


def extract_uc_ids(text: str) -> List[str]:
    return sorted({match.group(0).upper() for match in UC_ID_PATTERN.finditer(text)})


def story_files(stories_dir: Path) -> Iterable[Path]:
    if not stories_dir.exists():
        return []
    return sorted(path for path in stories_dir.glob("*.md") if path.is_file())


def collect_findings(base: Path) -> tuple[dict[str, object], List[Finding]]:
    policy = load_srs_policy(base)
    gate = str(policy.get("gate", "off"))
    enabled = bool(policy.get("enabled", False))
    scope = str(policy.get("scope", "product-enterprise"))
    risk_profile = str(policy.get("risk_profile", "normal"))
    enforce = should_enforce_srs(policy, base)

    meta: dict[str, object] = {
        "enabled": enabled,
        "gate": gate,
        "scope": scope,
        "risk_profile": risk_profile,
        "enforced": enforce,
        "policy_path": rel(base, policy_file(base)),
    }

    if not enforce:
        meta["status"] = "skipped"
        return meta, []

    findings: List[Finding] = []
    contracts_dir = base / CANONICAL_ARTIFACT_ROOT / "contracts"
    srs_path = contracts_dir / "srs-spec.md"
    prd_path = contracts_dir / "PRD.md"
    qa_path = contracts_dir / "qa-report.md"
    stories_dir = contracts_dir / "stories"

    if not srs_path.exists():
        findings.append(Finding(rel(base, srs_path), "Missing required SRS contract file"))
        meta["status"] = "failed"
        return meta, findings

    srs_content = srs_path.read_text(encoding="utf-8", errors="ignore")
    for section in REQUIRED_SECTIONS:
        if not has_section(srs_content, section):
            findings.append(Finding(rel(base, srs_path), f"Missing required section: {section}"))

    uc_ids = extract_uc_ids(srs_content)
    if not uc_ids:
        findings.append(Finding(rel(base, srs_path), "No UC-ID found. Add stable IDs such as UC-CHECKOUT-01."))

    if not prd_path.exists():
        findings.append(Finding(rel(base, prd_path), "Missing PRD for SRS traceability check"))
    else:
        prd_content = prd_path.read_text(encoding="utf-8", errors="ignore")
        if "SRS Traceability" not in prd_content:
            findings.append(Finding(rel(base, prd_path), "Missing 'SRS Traceability' section in PRD"))
        for uc_id in uc_ids:
            if uc_id not in prd_content:
                findings.append(Finding(rel(base, prd_path), f"UC-ID not mapped in PRD: {uc_id}"))

    story_paths = list(story_files(stories_dir))
    story_mentions: set[str] = set()
    if not story_paths:
        findings.append(Finding(rel(base, stories_dir), "Missing stories for SRS traceability check"))

    for path in story_paths:
        story_content = path.read_text(encoding="utf-8", errors="ignore")
        mentioned = set(extract_uc_ids(story_content))
        if not mentioned:
            findings.append(Finding(rel(base, path), "Story is missing UC-ID reference"))
            continue
        story_mentions.update(mentioned)
        if uc_ids and mentioned.isdisjoint(uc_ids):
            findings.append(Finding(rel(base, path), "Story references UC-ID values that do not exist in srs-spec"))

    for uc_id in uc_ids:
        if story_paths and uc_id not in story_mentions:
            findings.append(Finding(rel(base, stories_dir), f"UC-ID missing from story traceability: {uc_id}"))

    if not qa_path.exists():
        findings.append(Finding(rel(base, qa_path), "Missing qa-report for SRS coverage check"))
    else:
        qa_content = qa_path.read_text(encoding="utf-8", errors="ignore")
        if "SRS coverage table".lower() not in qa_content.lower():
            findings.append(Finding(rel(base, qa_path), "Missing 'SRS coverage table' section in qa-report"))
        for uc_id in uc_ids:
            if uc_id not in qa_content:
                findings.append(Finding(rel(base, qa_path), f"UC-ID missing from QA coverage table: {uc_id}"))

    meta["status"] = "ok" if not findings else "failed"
    meta["uc_ids"] = uc_ids
    return meta, findings


def render_text(meta: dict[str, object], findings: List[Finding]) -> str:
    lines = [
        "SRS guard report",
        f"- policy: enabled={meta.get('enabled')} gate={meta.get('gate')} scope={meta.get('scope')} risk={meta.get('risk_profile')}",
        f"- enforced: {meta.get('enforced')}",
        f"- policy_path: {meta.get('policy_path')}",
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
            "risk_profile": meta.get("risk_profile"),
            "policy_path": meta.get("policy_path"),
        },
        "enforced": meta.get("enforced"),
        "status": meta.get("status"),
        "uc_ids": meta.get("uc_ids", []),
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
