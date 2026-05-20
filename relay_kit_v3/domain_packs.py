from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from relay_kit_v3.repo_profile import build_repo_profile


SCHEMA_VERSION = "relay-kit.domain-pack.v1"

DOMAIN_PACKS: dict[str, dict[str, Any]] = {
    "mmo-safe-ops": {
        "status": "pilot",
        "skills": (
            "mmo-account-operations",
            "mmo-browser-fleet-automation",
            "mmo-cloud-operations-automation",
            "mmo-http-api-automation",
            "mmo-lowcode-automation",
            "mmo-mobile-app-automation",
            "mmo-reup-automation",
            "mmo-social-marketing-automation",
        ),
        "competencies": (
            "mmo-safe-ops.profile-inventory",
            "mmo-safe-ops.quota-dedupe",
            "mmo-safe-ops.policy-safe-api",
            "mmo-safe-ops.operator-ledger",
            "mmo-safe-ops.manual-review-gate",
        ),
        "archetypes": ("automation-worker", "api-client", "security-policy"),
    },
    "commerce-api": {
        "status": "pilot",
        "skills": ("api-integration", "data-persistence", "policy-guard", "automation-ops", "release-readiness"),
        "competencies": (
            "api-integration.client-endpoint-contract",
            "api-integration.auth-scope",
            "api-integration.idempotency",
            "data-persistence.transaction-boundary",
            "automation-ops.execution-history",
        ),
        "archetypes": ("backend-api", "database-heavy", "security-policy", "automation-worker"),
    },
}


def build_domain_pack_list(project_root: Path | str = ".") -> dict[str, Any]:
    root = Path(project_root).resolve()
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "project_path": str(root),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "packs": [
            {"name": name, **pack}
            for name, pack in sorted(DOMAIN_PACKS.items())
        ],
    }


def run_domain_pack(project_root: Path | str, pack_name: str) -> dict[str, Any]:
    if pack_name not in DOMAIN_PACKS:
        raise ValueError(f"Unknown domain pack: {pack_name}")
    root = Path(project_root).resolve()
    pack = DOMAIN_PACKS[pack_name]
    profile = build_repo_profile(root)
    matched_archetypes = [
        item.get("archetype")
        for item in profile.get("archetypes", [])
        if item.get("archetype") in set(pack.get("archetypes", ()))
    ]
    matched_competencies = sorted(set(profile.get("suggested_competencies", [])) & set(pack.get("competencies", ())))
    status = "pass" if matched_archetypes else "needs-scout"
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "project_path": str(root),
        "pack": pack_name,
        "pack_status": pack.get("status"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "matched_archetypes": matched_archetypes,
        "matched_competencies": matched_competencies,
        "required_competencies": list(pack.get("competencies", ())),
        "claim_status": f"domain-pack-tested:{pack_name}" if status == "pass" else "domain-pack-needs-scout",
        "repo_profile": profile,
    }


def write_domain_pack_report(project_root: Path | str, report: Mapping[str, Any], output_file: Path | str) -> Path:
    root = Path(project_root).resolve()
    target = Path(output_file)
    if not target.is_absolute():
        target = root / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return target


def render_domain_pack_report(report: Mapping[str, Any]) -> str:
    if "packs" in report:
        lines = ["Relay-kit domain packs", f"- status: {report.get('status')}"]
        for pack in report.get("packs", []):
            lines.append(f"  - {pack.get('name')}: {pack.get('status')} skills={len(pack.get('skills', []))}")
        return "\n".join(lines)
    return "\n".join(
        [
            "Relay-kit domain pack",
            f"- status: {report.get('status')}",
            f"- pack: {report.get('pack')}",
            f"- claim status: {report.get('claim_status')}",
            f"- matched archetypes: {report.get('matched_archetypes')}",
        ]
    )

