from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from relay_kit_v3.agent_profiles import build_agent_diagnostics
from relay_kit_v3.command_registry import build_command_diagnostics
from relay_kit_v3.generator import BUNDLES
from relay_kit_v3.localized_metadata import localized_skill_description, resolve_metadata_locale
from relay_kit_v3.registry.skills import ALL_V3_SKILLS, SkillSpec
from relay_kit_v3.runtime_locale import load_runtime_locale


SCHEMA_VERSION = "relay-kit.adapter-diagnostics.v1"

ADAPTERS: dict[str, dict[str, Any]] = {
    "codex": {
        "path": ".codex/skills",
        "display": "Codex",
        "metadata_policy": {
            "name": "preserved",
            "description": "preserved",
            "paths": "preserved",
            "context": "preserved",
            "allowed-tools": "preserved",
            "effort": "preserved",
        },
    },
    "claude": {
        "path": ".claude/skills",
        "display": "Claude",
        "metadata_policy": {
            "name": "preserved",
            "description": "preserved",
            "paths": "preserved",
            "context": "preserved",
            "allowed-tools": "preserved",
            "effort": "preserved",
        },
    },
    "agent": {
        "path": ".agent/skills",
        "display": "Agent/Antigravity",
        "metadata_policy": {
            "name": "preserved",
            "description": "preserved",
            "paths": "advisory",
            "context": "advisory",
            "allowed-tools": "advisory",
            "effort": "advisory",
        },
    },
}

ALLOWED_OPTIONAL_SKILLS = {
    "aesthetic",
    "brainstorm",
    "build-it",
    "debug-systematically",
    "frontend-design",
    "prove-it",
    "ready-check",
    "review-pr",
    "start-here",
    "ui-styling",
    "write-steps",
}


def build_adapter_diagnostics(root: Path | str, *, adapter: str = "all") -> dict[str, Any]:
    project = Path(root).resolve()
    selected = _selected_adapters(adapter)
    locale_policy = load_runtime_locale(project)
    locale_profile = resolve_metadata_locale(locale_policy)
    fallback_locale = str(locale_policy.get("fallback_locale", "en"))
    expected = list(BUNDLES["enterprise"])
    expected_set = set(expected)
    command_report = build_command_diagnostics(project, adapter=adapter)
    profile_report = build_agent_diagnostics(project, adapter=adapter)
    command_adapter_reports = {
        str(item.get("adapter")): item for item in command_report.get("adapters", [])
    }
    profile_adapter_reports = {
        str(item.get("adapter")): item for item in profile_report.get("adapters", [])
    }
    command_findings = list(command_report.get("findings", []))
    profile_findings = list(profile_report.get("findings", []))
    command_summary = command_report.get("summary", {})
    profile_summary = profile_report.get("summary", {})
    findings: list[dict[str, Any]] = []
    adapter_reports: list[dict[str, Any]] = []

    for adapter_name in selected:
        config = ADAPTERS[adapter_name]
        relative_root = str(config["path"])
        adapter_root = project / relative_root
        existing = _skill_dirs(adapter_root)
        missing = sorted(expected_set - existing)
        unexpected = sorted((existing - expected_set) - ALLOWED_OPTIONAL_SKILLS)
        metadata_drift = 0
        advisory_present: list[str] = []

        for skill_name in missing:
            findings.append(
                {
                    "id": "missing-skill",
                    "status": "hold",
                    "adapter": adapter_name,
                    "path": f"{relative_root}/{skill_name}/SKILL.md",
                    "skill": skill_name,
                    "summary": f"{adapter_name} is missing generated skill {skill_name}",
                }
            )
        for skill_name in unexpected:
            findings.append(
                {
                    "id": "unexpected-skill",
                    "status": "hold",
                    "adapter": adapter_name,
                    "path": f"{relative_root}/{skill_name}/SKILL.md",
                    "skill": skill_name,
                    "summary": f"{adapter_name} has unexpected generated skill {skill_name}",
                }
            )

        for skill_name in sorted(expected_set & existing):
            spec = ALL_V3_SKILLS[skill_name]
            path = adapter_root / skill_name / "SKILL.md"
            frontmatter = _parse_frontmatter(path)
            if frontmatter is None:
                metadata_drift += 1
                findings.append(
                    {
                        "id": "frontmatter-missing",
                        "status": "hold",
                        "adapter": adapter_name,
                        "path": _display_path(project, path),
                        "skill": skill_name,
                        "summary": f"{adapter_name}/{skill_name} is missing parseable frontmatter",
                    }
                )
                continue

            expected_frontmatter = _expected_frontmatter(
                spec,
                locale_profile=locale_profile,
                fallback_locale=fallback_locale,
            )
            metadata_policy = config["metadata_policy"]
            for field, expected_value in expected_frontmatter.items():
                actual_value = frontmatter.get(field)
                if metadata_policy.get(field) == "advisory" and field not in advisory_present:
                    advisory_present.append(field)
                if actual_value != expected_value:
                    metadata_drift += 1
                    findings.append(
                        {
                            "id": "frontmatter-drift",
                            "status": "hold",
                            "adapter": adapter_name,
                            "path": _display_path(project, path),
                            "skill": skill_name,
                            "field": field,
                            "expected": expected_value,
                            "actual": actual_value,
                            "summary": f"{adapter_name}/{skill_name} frontmatter {field} drifted",
                        }
                    )
            for field in _frontmatter_fields_to_check(frontmatter):
                if field not in expected_frontmatter:
                    metadata_drift += 1
                    findings.append(
                        {
                            "id": "frontmatter-extra",
                            "status": "hold",
                            "adapter": adapter_name,
                            "path": _display_path(project, path),
                            "skill": skill_name,
                            "field": field,
                            "actual": frontmatter.get(field),
                            "summary": f"{adapter_name}/{skill_name} has unexpected frontmatter {field}",
                        }
                    )

        adapter_reports.append(
            {
                "adapter": adapter_name,
                "display": config["display"],
                "path": relative_root,
                "expected_skill_count": len(expected),
                "generated_skill_count": len(existing & expected_set),
                "allowed_optional_skill_count": len(existing & ALLOWED_OPTIONAL_SKILLS),
                "missing_skill_count": len(missing),
                "unexpected_skill_count": len(unexpected),
                "metadata_drift_count": metadata_drift,
                "metadata_policy": dict(config["metadata_policy"]),
                "advisory_metadata_present": sorted(advisory_present),
                "expected_command_count": int(
                    command_adapter_reports.get(adapter_name, {}).get("expected_command_count", 0)
                ),
                "generated_command_count": int(
                    command_adapter_reports.get(adapter_name, {}).get("generated_command_count", 0)
                ),
                "missing_command_count": int(
                    command_adapter_reports.get(adapter_name, {}).get("missing_command_count", 0)
                ),
                "unexpected_command_count": int(
                    command_adapter_reports.get(adapter_name, {}).get("unexpected_command_count", 0)
                ),
                "expected_profile_count": int(
                    profile_adapter_reports.get(adapter_name, {}).get("expected_profile_count", 0)
                ),
                "generated_profile_count": int(
                    profile_adapter_reports.get(adapter_name, {}).get("generated_profile_count", 0)
                ),
                "missing_profile_count": int(
                    profile_adapter_reports.get(adapter_name, {}).get("missing_profile_count", 0)
                ),
                "unexpected_profile_count": int(
                    profile_adapter_reports.get(adapter_name, {}).get("unexpected_profile_count", 0)
                ),
            }
        )

    findings.extend(command_findings)
    findings.extend(profile_findings)

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "hold" if findings else "pass",
        "project_path": str(project),
        "adapter": adapter,
        "summary": {
            "adapter_count": len(adapter_reports),
            "expected_skill_count": len(expected),
            "missing_skills": sum(item["missing_skill_count"] for item in adapter_reports),
            "unexpected_skills": sum(item["unexpected_skill_count"] for item in adapter_reports),
            "metadata_drift": sum(item["metadata_drift_count"] for item in adapter_reports),
            "expected_command_count": int(command_summary.get("expected_command_count", 0)),
            "missing_commands": int(command_summary.get("missing_commands", 0)),
            "unexpected_commands": int(command_summary.get("unexpected_commands", 0)),
            "expected_profile_count": int(profile_summary.get("expected_profile_count", 0)),
            "missing_profiles": int(profile_summary.get("missing_profiles", 0)),
            "unexpected_profiles": int(profile_summary.get("unexpected_profiles", 0)),
            "findings": len(findings),
        },
        "adapters": adapter_reports,
        "findings": findings,
    }


def render_adapter_diagnostics(report: Mapping[str, Any]) -> str:
    summary = report.get("summary", {})
    lines = [
        "Relay-kit adapter diagnostics",
        f"- status: {report.get('status')}",
        f"- adapters: {summary.get('adapter_count', 0)}",
        f"- missing skills: {summary.get('missing_skills', 0)}",
        f"- unexpected skills: {summary.get('unexpected_skills', 0)}",
        f"- missing commands: {summary.get('missing_commands', 0)}",
        f"- unexpected commands: {summary.get('unexpected_commands', 0)}",
        f"- missing profiles: {summary.get('missing_profiles', 0)}",
        f"- unexpected profiles: {summary.get('unexpected_profiles', 0)}",
        f"- metadata drift: {summary.get('metadata_drift', 0)}",
    ]
    for adapter in report.get("adapters", []):
        lines.append(
            f"  - {adapter.get('adapter')}: generated={adapter.get('generated_skill_count')} "
            f"commands={adapter.get('generated_command_count')} "
            f"profiles={adapter.get('generated_profile_count')} "
            f"optional={adapter.get('allowed_optional_skill_count')} "
            f"metadata_drift={adapter.get('metadata_drift_count')}"
        )
    for finding in report.get("findings", [])[:12]:
        lines.append(f"  - {finding.get('summary', finding.get('id', 'finding'))}")
    return "\n".join(lines)


def write_adapter_diagnostics(
    root: Path | str,
    report: Mapping[str, Any],
    output_file: Path | str | None = None,
) -> Path:
    project = Path(root).resolve()
    target = Path(output_file) if output_file else project / ".relay-kit" / "adapters" / "adapter-diagnostics.json"
    if not target.is_absolute():
        target = project / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return target


def _selected_adapters(adapter: str) -> list[str]:
    value = str(adapter).strip().lower()
    if value == "antigravity":
        value = "agent"
    if value == "all":
        return ["codex", "claude", "agent"]
    if value not in ADAPTERS:
        raise ValueError(f"Unknown adapter: {adapter!r}")
    return [value]


def _skill_dirs(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {entry.name for entry in path.iterdir() if entry.is_dir()}


def _parse_frontmatter(path: Path) -> dict[str, str] | None:
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break
    if end_index is None:
        return None
    fields: dict[str, str] = {}
    for raw in lines[1:end_index]:
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def _expected_frontmatter(
    spec: SkillSpec,
    *,
    locale_profile: str,
    fallback_locale: str,
) -> dict[str, str]:
    expected_description = localized_skill_description(
        spec.name,
        spec.description,
        locale=locale_profile,
        fallback_locale=fallback_locale,
    )
    expected = {
        "name": spec.name,
        "description": expected_description,
    }
    if spec.paths:
        expected["paths"] = _inline_list(spec.paths)
    if spec.context:
        expected["context"] = spec.context
    if spec.allowed_tools:
        expected["allowed-tools"] = _inline_list(spec.allowed_tools)
    if spec.effort:
        expected["effort"] = spec.effort
    return expected


def _frontmatter_fields_to_check(frontmatter: Mapping[str, str]) -> set[str]:
    return set(frontmatter) & {"name", "description", "paths", "context", "allowed-tools", "effort"}


def _inline_list(values: list[str]) -> str:
    return "[" + ", ".join(f'"{value}"' for value in values) + "]"


def _display_path(project: Path, path: Path) -> str:
    try:
        return path.relative_to(project).as_posix()
    except ValueError:
        return path.as_posix()
