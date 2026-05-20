from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from relay_kit_v3.competency_catalog import (
    CATALOG_SCHEMA_VERSION,
    MIN_CORE_COMPETENCIES,
    MIN_FAILURE_TRAPS,
    build_competency_catalog,
    competency_coverage_for_skill,
    load_competency_profile,
    validate_competency_profile,
)
from relay_kit_v3.registry.skills import ALL_V3_SKILLS
from relay_kit_v3.skill_battle import build_skill_battle


SCHEMA_VERSION = "relay-kit.competency-battle.v1"


def build_competency_battle(
    project_root: Path | str,
    *,
    skill: str = "all",
    suite: str = "core",
    cleanup: bool = True,
) -> dict[str, Any]:
    if suite not in {"core", "deep"}:
        raise ValueError(f"Unknown competency suite: {suite}")
    root = Path(project_root).resolve()
    skill_names = _selected_skills(skill)
    skill_battle_report = build_skill_battle(root, skill=skill, suite="deep", cleanup=cleanup) if suite == "deep" else None
    battle_scores = {
        str(item.get("skill")): float(item.get("score", 0))
        for item in (skill_battle_report or {}).get("skills", [])
    }
    skills = [
        _score_skill(skill_name, battle_scores.get(skill_name))
        for skill_name in skill_names
    ]
    findings = [finding for item in skills for finding in item.get("findings", [])]
    covered = [item for item in skills if item.get("claim_status") == "competency-covered"]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass" if not findings else "fail",
        "project_path": str(root),
        "suite": suite,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "skill_count": len(skills),
            "competency_covered": len(covered),
            "needs_competency_hardening": len(skills) - len(covered),
            "finding_count": len(findings),
            "min_core_competencies": MIN_CORE_COMPETENCIES,
            "min_failure_traps": MIN_FAILURE_TRAPS,
        },
        "skills": skills,
        "findings": findings,
    }


def build_competency_catalog_report(project_root: Path | str = ".") -> dict[str, Any]:
    root = Path(project_root).resolve()
    catalog = build_competency_catalog()
    catalog["project_path"] = str(root)
    return catalog


def write_competency_battle(project_root: Path | str, report: Mapping[str, Any], output_file: Path | str) -> Path:
    root = Path(project_root).resolve()
    target = Path(output_file)
    if not target.is_absolute():
        target = root / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return target


def render_competency_battle(report: Mapping[str, Any]) -> str:
    summary = report.get("summary", {})
    lines = [
        "Relay-kit competency battle",
        f"- status: {report.get('status')}",
        f"- suite: {report.get('suite')}",
        f"- skills: {summary.get('skill_count', 0)}",
        f"- competency covered: {summary.get('competency_covered', 0)}",
        f"- needs hardening: {summary.get('needs_competency_hardening', 0)}",
    ]
    for item in report.get("skills", [])[:12]:
        lines.append(f"  - {item.get('skill')}: {item.get('coverage_score')} {item.get('claim_status')}")
    return "\n".join(lines)


def _selected_skills(skill: str) -> list[str]:
    if skill == "all":
        return sorted(ALL_V3_SKILLS)
    if skill not in ALL_V3_SKILLS:
        raise ValueError(f"Unknown skill: {skill}")
    return [skill]


def _score_skill(skill_name: str, battle_score: float | None) -> dict[str, Any]:
    profile = load_competency_profile(skill_name)
    validation_findings = validate_competency_profile(profile)
    coverage = competency_coverage_for_skill(skill_name)
    deep_gate_ok = battle_score is None or battle_score >= 8.0
    findings: list[dict[str, Any]] = []
    for finding in validation_findings:
        findings.append(
            {
                "severity": "high",
                "skill": skill_name,
                "finding": finding,
                "suggested_fix": "Refresh the skill competency profile and rerun competency-battle.",
            }
        )
    if not deep_gate_ok:
        findings.append(
            {
                "severity": "high",
                "skill": skill_name,
                "finding": "deep-skill-battle-below-threshold",
                "suggested_fix": "Harden resource/eval/routing evidence before claiming competency coverage.",
            }
        )
    core = profile.get("core_competencies", [])
    traps = profile.get("failure_traps", [])
    covered_competencies = coverage["covered_competencies"] if deep_gate_ok else []
    missing_competencies = coverage["missing_competencies"] if deep_gate_ok else [str(item.get("id")) for item in core]
    coverage_score = round(len(covered_competencies) / max(len(core), 1), 3)
    claim_status = "competency-covered" if coverage_score >= 1.0 and not findings else "needs-competency-hardening"
    return {
        "skill": skill_name,
        "category": profile.get("category"),
        "claim_status": claim_status,
        "coverage_score": coverage_score,
        "covered_competencies": covered_competencies,
        "missing_competencies": missing_competencies,
        "failure_trap_count": len(traps),
        "unknown_domain_mode": False,
        "deep_skill_battle_score": battle_score,
        "findings": findings,
    }

