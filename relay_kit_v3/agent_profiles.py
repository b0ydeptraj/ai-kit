from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from relay_kit_v3.registry.skills import ALL_V3_SKILLS


SCHEMA_VERSION = "relay-kit.agent-diagnostics.v1"
REGISTRY_SCHEMA_VERSION = "relay-kit.agent-registry.v1"
PROFILE_SCHEMA_VERSION = "relay-kit.agent-profile.v1"

ADAPTER_AGENT_ROOTS: dict[str, dict[str, str]] = {
    "codex": {"path": ".codex/agents", "display": "Codex"},
    "claude": {"path": ".claude/agents", "display": "Claude"},
    "agent": {"path": ".agent/agents", "display": "Agent/Antigravity"},
}

GENERATION_TARGETS = {
    "codex": ["codex"],
    "claude": ["claude"],
    "antigravity": ["agent"],
    "all": ["codex", "claude", "agent"],
}


@dataclass(frozen=True)
class AgentProfileSpec:
    profile_id: str
    display_name: str
    intent: str
    route_contract: tuple[str, ...]
    required_skills: tuple[str, ...]
    optional_skills: tuple[str, ...]
    expected_evidence: tuple[str, ...]
    adapter_support: tuple[str, ...]


AGENT_PROFILES: tuple[AgentProfileSpec, ...] = (
    AgentProfileSpec(
        profile_id="relay-engineer",
        display_name="Relay Engineer",
        intent="Deliver implementation work with strict planning, verification, and readiness gates.",
        route_contract=(
            "workflow-router",
            "scout-hub",
            "plan-hub",
            "fix-hub",
            "developer",
            "test-hub",
            "review-hub",
            "qa-governor",
            "release-readiness",
        ),
        required_skills=(
            "workflow-router",
            "scout-hub",
            "plan-hub",
            "fix-hub",
            "developer",
            "test-hub",
            "review-hub",
            "qa-governor",
            "release-readiness",
        ),
        optional_skills=(
            "context-continuity",
            "policy-guard",
            "evidence-before-completion",
        ),
        expected_evidence=(
            "scoped implementation diff with tests or verification output",
            "review findings with residual risk or explicit pass",
            "readiness and policy gates mapped to release decision",
        ),
        adapter_support=("codex", "claude", "agent"),
    ),
    AgentProfileSpec(
        profile_id="relay-growth",
        display_name="Relay Growth",
        intent="Drive research-backed growth execution with measurable launch and support artifacts.",
        route_contract=(
            "research",
            "market-research",
            "growth-marketing",
            "automation-ops",
        ),
        required_skills=(
            "research",
            "market-research",
            "growth-marketing",
            "automation-ops",
        ),
        optional_skills=(
            "vietnamese-product-localization",
            "qa-governor",
            "release-readiness",
        ),
        expected_evidence=(
            "source-ranked research findings with pricing and ICP implications",
            "campaign and funnel plan with launch QA checklist",
            "automation runbook with dry-run and rollback discipline",
        ),
        adapter_support=("codex", "claude", "agent"),
    ),
)


def agent_profiles() -> list[AgentProfileSpec]:
    return list(AGENT_PROFILES)


def agent_profile_ids() -> list[str]:
    return [profile.profile_id for profile in AGENT_PROFILES]


def agent_profile_records() -> list[dict[str, Any]]:
    return [_profile_record(profile) for profile in AGENT_PROFILES]


def render_agent_surface(profile: AgentProfileSpec, *, adapter: str) -> str:
    route_text = " -> ".join(profile.route_contract)
    required = ", ".join(f"`{name}`" for name in profile.required_skills)
    optional = ", ".join(f"`{name}`" for name in profile.optional_skills) or "-"
    evidence = "\n".join(f"- {item}" for item in profile.expected_evidence)
    return (
        f"# {profile.profile_id}\n\n"
        f"- display-name: `{profile.display_name}`\n"
        f"- adapter: `{adapter}`\n"
        f"- intent: {profile.intent}\n\n"
        "## Route Contract\n\n"
        f"`{route_text}`\n\n"
        "## Required Skills\n\n"
        f"{required}\n\n"
        "## Optional Skills\n\n"
        f"{optional}\n\n"
        "## Expected Evidence\n\n"
        f"{evidence}\n"
    )


def emit_agent_surfaces(project_path: Path | str, ai: str) -> list[Path]:
    project = Path(project_path).resolve()
    if ai not in GENERATION_TARGETS:
        return []
    written: list[Path] = []
    canonical_root = project / ".relay-kit" / "agents"
    canonical_root.mkdir(parents=True, exist_ok=True)
    for profile in AGENT_PROFILES:
        canonical_path = canonical_root / f"{profile.profile_id}.json"
        canonical_payload = {
            "schema_version": PROFILE_SCHEMA_VERSION,
            **_profile_record(profile),
        }
        canonical_path.write_text(json.dumps(canonical_payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
        written.append(canonical_path)

    for adapter in GENERATION_TARGETS[ai]:
        adapter_root = project / ADAPTER_AGENT_ROOTS[adapter]["path"]
        adapter_root.mkdir(parents=True, exist_ok=True)
        for profile in AGENT_PROFILES:
            output = adapter_root / f"{profile.profile_id}.md"
            output.write_text(render_agent_surface(profile, adapter=adapter), encoding="utf-8")
            written.append(output)
    return written


def build_agent_diagnostics(root: Path | str, *, adapter: str = "all") -> dict[str, Any]:
    project = Path(root).resolve()
    selected = _selected_adapters(adapter)
    expected_records = {profile["id"]: profile for profile in agent_profile_records()}
    expected_ids = set(expected_records.keys())
    findings: list[dict[str, Any]] = []

    canonical_root = project / ".relay-kit" / "agents"
    canonical_ids = _profile_json_files(canonical_root)
    missing_canonical = sorted(expected_ids - canonical_ids)
    unexpected_canonical = sorted(canonical_ids - expected_ids)

    for profile_id in missing_canonical:
        findings.append(
            {
                "id": "missing-canonical-profile",
                "status": "hold",
                "path": f".relay-kit/agents/{profile_id}.json",
                "profile_id": profile_id,
                "summary": f"missing canonical profile {profile_id}",
            }
        )
    for profile_id in unexpected_canonical:
        findings.append(
            {
                "id": "unexpected-canonical-profile",
                "status": "hold",
                "path": f".relay-kit/agents/{profile_id}.json",
                "profile_id": profile_id,
                "summary": f"unexpected canonical profile {profile_id}",
            }
        )

    invalid_profile_contracts = 0
    for profile_id in sorted(expected_ids & canonical_ids):
        profile_path = canonical_root / f"{profile_id}.json"
        expected_payload = {
            "schema_version": PROFILE_SCHEMA_VERSION,
            **expected_records[profile_id],
        }
        payload = _load_json(profile_path)
        if payload is None:
            invalid_profile_contracts += 1
            findings.append(
                {
                    "id": "invalid-canonical-profile",
                    "status": "hold",
                    "path": f".relay-kit/agents/{profile_id}.json",
                    "profile_id": profile_id,
                    "summary": f"invalid canonical profile JSON for {profile_id}",
                }
            )
            continue
        if payload != expected_payload:
            invalid_profile_contracts += 1
            findings.append(
                {
                    "id": "profile-contract-drift",
                    "status": "hold",
                    "path": f".relay-kit/agents/{profile_id}.json",
                    "profile_id": profile_id,
                    "summary": f"canonical profile contract drift for {profile_id}",
                }
            )

    for profile in agent_profile_records():
        profile_findings = _profile_contract_findings(profile)
        invalid_profile_contracts += len(profile_findings)
        findings.extend(profile_findings)

    adapter_reports: list[dict[str, Any]] = []
    for adapter_name in selected:
        config = ADAPTER_AGENT_ROOTS[adapter_name]
        relative_root = config["path"]
        profile_root = project / relative_root
        existing = _profile_markdown_files(profile_root)
        missing = sorted(expected_ids - existing)
        unexpected = sorted(existing - expected_ids)
        for profile_id in missing:
            findings.append(
                {
                    "id": "missing-profile-surface",
                    "status": "hold",
                    "adapter": adapter_name,
                    "path": f"{relative_root}/{profile_id}.md",
                    "profile_id": profile_id,
                    "summary": f"{adapter_name} missing profile surface {profile_id}",
                }
            )
        for profile_id in unexpected:
            findings.append(
                {
                    "id": "unexpected-profile-surface",
                    "status": "hold",
                    "adapter": adapter_name,
                    "path": f"{relative_root}/{profile_id}.md",
                    "profile_id": profile_id,
                    "summary": f"{adapter_name} has unexpected profile surface {profile_id}",
                }
            )
        adapter_reports.append(
            {
                "adapter": adapter_name,
                "display": config["display"],
                "path": relative_root,
                "expected_profile_count": len(expected_ids),
                "generated_profile_count": len(existing & expected_ids),
                "missing_profile_count": len(missing),
                "unexpected_profile_count": len(unexpected),
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "hold" if findings else "pass",
        "project_path": str(project),
        "adapter": adapter,
        "summary": {
            "adapter_count": len(adapter_reports),
            "expected_profile_count": len(expected_ids),
            "missing_profiles": sum(item["missing_profile_count"] for item in adapter_reports),
            "unexpected_profiles": sum(item["unexpected_profile_count"] for item in adapter_reports),
            "missing_canonical_profiles": len(missing_canonical),
            "unexpected_canonical_profiles": len(unexpected_canonical),
            "invalid_profile_contracts": invalid_profile_contracts,
            "findings": len(findings),
        },
        "adapters": adapter_reports,
        "findings": findings,
        "profiles": agent_profile_records(),
    }


def render_agent_diagnostics(report: Mapping[str, Any]) -> str:
    summary = report.get("summary", {})
    lines = [
        "Relay-kit agent profile diagnostics",
        f"- status: {report.get('status')}",
        f"- adapters: {summary.get('adapter_count', 0)}",
        f"- expected profiles: {summary.get('expected_profile_count', 0)}",
        f"- missing profiles: {summary.get('missing_profiles', 0)}",
        f"- unexpected profiles: {summary.get('unexpected_profiles', 0)}",
        f"- missing canonical profiles: {summary.get('missing_canonical_profiles', 0)}",
        f"- unexpected canonical profiles: {summary.get('unexpected_canonical_profiles', 0)}",
        f"- invalid profile contracts: {summary.get('invalid_profile_contracts', 0)}",
    ]
    for adapter in report.get("adapters", []):
        lines.append(
            f"  - {adapter.get('adapter')}: generated={adapter.get('generated_profile_count')} "
            f"missing={adapter.get('missing_profile_count')} "
            f"unexpected={adapter.get('unexpected_profile_count')}"
        )
    for finding in report.get("findings", [])[:12]:
        lines.append(f"  - {finding.get('summary', finding.get('id', 'finding'))}")
    return "\n".join(lines)


def write_agent_diagnostics(
    root: Path | str,
    report: Mapping[str, Any],
    output_file: Path | str | None = None,
) -> Path:
    project = Path(root).resolve()
    target = Path(output_file) if output_file else project / ".relay-kit" / "agents" / "agent-diagnostics.json"
    if not target.is_absolute():
        target = project / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return target


def _profile_record(profile: AgentProfileSpec) -> dict[str, Any]:
    return {
        "id": profile.profile_id,
        "display_name": profile.display_name,
        "intent": profile.intent,
        "route_contract": list(profile.route_contract),
        "required_skills": list(profile.required_skills),
        "optional_skills": list(profile.optional_skills),
        "expected_evidence": list(profile.expected_evidence),
        "adapter_support": list(profile.adapter_support),
    }


def _selected_adapters(adapter: str) -> list[str]:
    value = str(adapter).strip().lower()
    if value == "antigravity":
        value = "agent"
    if value == "all":
        return ["codex", "claude", "agent"]
    if value not in ADAPTER_AGENT_ROOTS:
        raise ValueError(f"Unknown adapter: {adapter!r}")
    return [value]


def _profile_json_files(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {
        entry.stem
        for entry in path.iterdir()
        if entry.is_file() and entry.suffix.lower() == ".json" and entry.name != "agent-diagnostics.json"
    }


def _profile_markdown_files(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {
        entry.stem
        for entry in path.iterdir()
        if entry.is_file() and entry.suffix.lower() == ".md"
    }


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _profile_contract_findings(profile: Mapping[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    profile_id = str(profile.get("id", "unknown"))
    for skill_name in profile.get("route_contract", []):
        if skill_name not in ALL_V3_SKILLS:
            findings.append(
                {
                    "id": "invalid-route-skill",
                    "status": "hold",
                    "profile_id": profile_id,
                    "skill": skill_name,
                    "summary": f"{profile_id} route references unknown skill {skill_name}",
                }
            )
    for skill_name in profile.get("required_skills", []):
        if skill_name not in ALL_V3_SKILLS:
            findings.append(
                {
                    "id": "invalid-required-skill",
                    "status": "hold",
                    "profile_id": profile_id,
                    "skill": skill_name,
                    "summary": f"{profile_id} required_skills references unknown skill {skill_name}",
                }
            )
    for skill_name in profile.get("optional_skills", []):
        if skill_name not in ALL_V3_SKILLS:
            findings.append(
                {
                    "id": "invalid-optional-skill",
                    "status": "hold",
                    "profile_id": profile_id,
                    "skill": skill_name,
                    "summary": f"{profile_id} optional_skills references unknown skill {skill_name}",
                }
            )
    return findings
