from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from relay_kit_v3.registry.skills import ALL_V3_SKILLS


SCHEMA_VERSION = "relay-kit.battle-audit.v1"

RESOURCE_ROOT = Path(__file__).resolve().parent / "skill_resources"
PUBLIC_SURFACES = (
    "README.md",
    "README.vi.md",
    "docs/site/index.md",
    "docs/site/skill-catalog.md",
    "docs/site/context-graph.md",
    "docs/site/prompt-enhance.md",
    "docs/site/install.md",
    "docs/site/readiness.md",
    "docs/site/battle-benchmark.md",
)

GENERIC_RESOURCE_PATTERNS = (
    r"\bgood response shape\b",
    r"\bbad response shape\b",
    r"\bhandle a compact\b",
    r"\bcontext-anchored-output\b",
    r"\bhandoff-and-risk-control\b",
    r"\buse this contract when\b",
    r"\buse this reference when\b",
    r"\bthe output must cite task-specific context\b",
)

PUBLIC_OVERCLAIM_PATTERNS = (
    r"\bcommercial-ready-candidate\b",
    r"\bfield-tested proof\b",
    r"\bexpert guarantee\b",
    r"\bguaranteed expert\b",
    r"\bfull context engine\b",
    r"\breplaces augment\b",
)


def build_battle_audit(
    project_root: Path | str,
    *,
    resource_root: Path | str | None = None,
    skill_names: Sequence[str] | None = None,
) -> dict[str, Any]:
    project = Path(project_root).resolve()
    resources = Path(resource_root).resolve() if resource_root else RESOURCE_ROOT
    names = sorted(skill_names or ALL_V3_SKILLS)
    skill_reports = [_audit_skill(resources, name) for name in names]
    surface_findings = _audit_public_surfaces(project)
    all_findings = [finding for report in skill_reports for finding in report["findings"]]
    all_findings.extend(surface_findings)
    summary = {
        "skill_count": len(skill_reports),
        "resource_complete_count": sum(1 for report in skill_reports if report["resource_complete"]),
        "battle_ready_count": sum(1 for report in skill_reports if report["status"] == "battle-ready"),
        "high_findings": sum(1 for finding in all_findings if finding["severity"] == "high"),
        "medium_findings": sum(1 for finding in all_findings if finding["severity"] == "medium"),
        "low_findings": sum(1 for finding in all_findings if finding["severity"] == "low"),
    }
    status = "pass" if summary["high_findings"] == 0 else "fail"
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "project_path": str(project),
        "resource_root": str(resources),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "skills": skill_reports,
        "findings": all_findings,
    }


def write_battle_audit(
    project_root: Path | str,
    report: Mapping[str, Any],
    output_file: Path | str,
) -> Path:
    project = Path(project_root).resolve()
    target = Path(output_file)
    if not target.is_absolute():
        target = project / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return target


def render_battle_audit(report: Mapping[str, Any]) -> str:
    summary = report.get("summary", {})
    lines = [
        "Relay-kit battle audit",
        f"- status: {report.get('status')}",
        f"- skills: {summary.get('skill_count', 0)}",
        f"- battle-ready skills: {summary.get('battle_ready_count', 0)}",
        f"- high findings: {summary.get('high_findings', 0)}",
        f"- medium findings: {summary.get('medium_findings', 0)}",
    ]
    for finding in report.get("findings", [])[:12]:
        lines.append(
            f"  - [{finding.get('severity')}] {finding.get('skill', 'public-surface')}: "
            f"{finding.get('message')} ({finding.get('file')})"
        )
    return "\n".join(lines)


def _audit_skill(resource_root: Path, skill_name: str) -> dict[str, Any]:
    root = resource_root / skill_name
    required = [
        root / "references" / f"{skill_name}-operator-contract.md",
        root / "examples" / f"{skill_name}-good-output.md",
        root / "examples" / f"{skill_name}-bad-output.md",
        root / "evals" / f"{skill_name}-cases.json",
    ]
    findings: list[dict[str, Any]] = []
    for path in required:
        if not path.exists():
            findings.append(_finding("high", skill_name, path, "Missing required resource file.", "Create the resource pack file."))
    if findings:
        return _skill_report(skill_name, root, findings, resource_complete=False)

    for path in required[:3]:
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in GENERIC_RESOURCE_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                findings.append(
                    _finding(
                        "high",
                        skill_name,
                        path,
                        f"Resource still contains generic skeleton phrase matching `{pattern}`.",
                        "Rewrite with a concrete repo/task case, evidence checklist, and failure mode.",
                    )
                )
    cases_path = required[3]
    try:
        cases = json.loads(cases_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        findings.append(_finding("high", skill_name, cases_path, "Eval cases are not valid JSON.", "Fix the JSON fixture."))
        cases = []
    if not isinstance(cases, list) or len(cases) < 2:
        findings.append(_finding("high", skill_name, cases_path, "Eval pack has fewer than two scenarios.", "Add at least two scenarios."))
    else:
        for index, case in enumerate(cases):
            findings.extend(_audit_case(skill_name, cases_path, index, case))
    return _skill_report(skill_name, root, findings, resource_complete=True)


def _audit_case(skill_name: str, path: Path, index: int, case: object) -> list[dict[str, Any]]:
    if not isinstance(case, dict):
        return [_finding("high", skill_name, path, f"Eval case {index} is not an object.", "Use a structured case object.")]
    findings: list[dict[str, Any]] = []
    required_fields = ["repo_profile", "task", "expected_files", "expected_symbols", "expected_evidence_terms"]
    for field in required_fields:
        if not case.get(field):
            findings.append(
                _finding(
                    "medium",
                    skill_name,
                    path,
                    f"Eval case `{case.get('id', index)}` is missing `{field}`.",
                    "Add repo profile, expected files, symbols, and evidence terms.",
                )
            )
    raw_evidence = case.get("expected_evidence_terms", [])
    evidence = [str(item).casefold() for item in raw_evidence] if isinstance(raw_evidence, list) else []
    if evidence and len([term for term in evidence if len(term) >= 4]) < 3:
        findings.append(
            _finding(
                "medium",
                skill_name,
                path,
                f"Eval case `{case.get('id', index)}` has weak evidence terms.",
                "Use terms tied to files, symbols, commands, or residual risk.",
            )
        )
    return findings


def _audit_public_surfaces(project: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for relative in PUBLIC_SURFACES:
        path = project / relative
        if not path.exists():
            if relative == "docs/site/battle-benchmark.md":
                findings.append(
                    _finding("medium", "public-surface", path, "Battle benchmark docs page is missing.", "Add docs/site/battle-benchmark.md.")
                )
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in PUBLIC_OVERCLAIM_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                findings.append(
                    _finding(
                        "high",
                        "public-surface",
                        path,
                        f"Public surface contains overclaim phrase matching `{pattern}`.",
                        "Replace with local benchmark evidence and explicit non-field-tested wording.",
                    )
                )
    return findings


def _skill_report(skill_name: str, root: Path, findings: Sequence[Mapping[str, Any]], *, resource_complete: bool) -> dict[str, Any]:
    high = sum(1 for finding in findings if finding["severity"] == "high")
    medium = sum(1 for finding in findings if finding["severity"] == "medium")
    low = sum(1 for finding in findings if finding["severity"] == "low")
    score = max(0, 100 - high * 40 - medium * 15 - low * 5)
    status = "battle-ready" if score >= 90 and high == 0 and medium == 0 else "needs-hardening"
    return {
        "skill": skill_name,
        "score": score,
        "status": status,
        "resource_complete": resource_complete,
        "resource_root": str(root),
        "findings": list(findings),
    }


def _finding(severity: str, skill: str, path: Path, message: str, suggested_fix: str) -> dict[str, Any]:
    return {
        "severity": severity,
        "skill": skill,
        "file": path.as_posix(),
        "message": message,
        "suggested_fix": suggested_fix,
    }
