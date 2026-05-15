"""Skill proof audit for Relay-kit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from relay_kit_v3.real_world_eval import DEFAULT_CASE_FIXTURE, load_cases
from relay_kit_v3.registry.skills import ALL_V3_SKILLS


SCHEMA_VERSION = "relay-kit.skill-proof-audit.v1"
STATUSES = ("theoretical", "validated", "field-tested")
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENARIO_FIXTURE = Path("relay_kit_v3") / "eval_fixtures" / "workflow_scenarios.json"


def build_report(
    project_root: Path | str,
    *,
    workflow_fixture: Path | str | None = None,
    real_world_cases_file: Path | str | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    workflow_coverage = _workflow_coverage(root, workflow_fixture)
    real_world_coverage = _real_world_coverage(root, real_world_cases_file)
    field_evidence = _field_evidence(root)

    records: list[dict[str, Any]] = []
    for skill_name in sorted(ALL_V3_SKILLS):
        proof_sources: list[str] = []
        if skill_name in workflow_coverage:
            proof_sources.extend(workflow_coverage[skill_name])
        if skill_name in real_world_coverage:
            proof_sources.extend(real_world_coverage[skill_name])
        if skill_name in field_evidence:
            proof_sources.extend(field_evidence[skill_name])

        if skill_name in field_evidence:
            status = "field-tested"
            missing_reason = ""
        elif skill_name in workflow_coverage or skill_name in real_world_coverage:
            status = "validated"
            missing_reason = ""
        else:
            status = "theoretical"
            missing_reason = "no validation or field evidence found"

        records.append(
            {
                "skill": skill_name,
                "status": status,
                "proof_sources": proof_sources,
                "missing_proof_reason": missing_reason,
            }
        )

    counts = {status: sum(1 for record in records if record["status"] == status) for status in STATUSES}
    findings = [
        {
            "check": "theoretical-production-skill",
            "skill": record["skill"],
            "status": record["status"],
            "summary": record["missing_proof_reason"],
        }
        for record in records
        if record["status"] == "theoretical"
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "fail" if strict and findings else "pass",
        "project_path": str(root),
        "counts": counts,
        "summary": {
            "skill_count": len(records),
            "theoretical": counts["theoretical"],
            "validated": counts["validated"],
            "field_tested": counts["field-tested"],
            "findings": len(findings),
        },
        "findings": findings,
        "skills": records,
    }


def _workflow_coverage(root: Path, workflow_fixture: Path | str | None) -> dict[str, list[str]]:
    fixture = workflow_fixture if workflow_fixture is not None else DEFAULT_SCENARIO_FIXTURE
    fixture_path = _resolve_fixture(root, Path(fixture))
    fixture_label = _source_label(root, fixture_path)
    coverage: dict[str, list[str]] = {}
    for scenario in _load_json_list(fixture_path):
        skill = str(scenario.get("expected_skill", "")).strip()
        scenario_id = str(scenario.get("id", "")).strip()
        if skill:
            coverage.setdefault(skill, []).append(f"synthetic:{fixture_label}#{scenario_id}")
    return coverage


def _real_world_coverage(root: Path, real_world_cases_file: Path | str | None) -> dict[str, list[str]]:
    coverage: dict[str, list[str]] = {}
    if real_world_cases_file is None:
        local_fixture = root / "relay_kit_v3" / "eval_fixtures" / "real_world_skill_cases.json"
        if local_fixture.exists():
            case_file: Path | str = local_fixture
        elif (root / "relay_kit_v3" / "eval_fixtures").exists():
            return coverage
        else:
            case_file = DEFAULT_CASE_FIXTURE
    else:
        case_file = real_world_cases_file
    case_path = Path(case_file)
    display_path = case_path if case_path.is_absolute() else root / case_path
    case_label = _source_label(root, display_path)
    try:
        cases = load_cases(root, case_file)
    except FileNotFoundError:
        return coverage
    for case in cases:
        skill = str(case.get("skill", "")).strip()
        case_id = str(case.get("id", "")).strip()
        if skill:
            coverage.setdefault(skill, []).append(f"real-world-case:{case_label}#{case_id}")
    return coverage


def _field_evidence(root: Path) -> dict[str, list[str]]:
    evidence_file = root / ".relay-kit" / "evidence" / "skill-field-evidence.json"
    if not evidence_file.exists():
        return {}
    try:
        payload = json.loads(evidence_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    rows = payload.get("skills", payload) if isinstance(payload, Mapping) else payload
    if not isinstance(rows, list):
        return {}
    evidence: dict[str, list[str]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            continue
        skill = str(row.get("skill", "")).strip()
        if not skill:
            continue
        evidence_id = str(row.get("source", "")).strip() or str(row.get("id", "")).strip() or f"field-evidence-{index + 1}"
        evidence.setdefault(skill, []).append(f".relay-kit/evidence/skill-field-evidence.json#{evidence_id}")
    return evidence


def _source_label(root: Path, path: Path) -> str:
    resolved = path.resolve()
    candidates = [root.resolve(), Path.cwd().resolve(), Path(__file__).resolve().parents[1]]
    for candidate in candidates:
        try:
            return resolved.relative_to(candidate).as_posix()
        except ValueError:
            continue
    return path.as_posix()


def _resolve_fixture(root: Path, fixture_path: Path) -> Path:
    if fixture_path.is_absolute():
        candidates = [fixture_path]
    else:
        candidates = [root / fixture_path, REPO_ROOT / fixture_path, fixture_path]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    raise FileNotFoundError(f"Skill proof fixture not found: {fixture_path}")


def _load_json_list(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Skill proof fixture must contain a list: {path}")
    return [dict(item) for item in payload if isinstance(item, Mapping)]


def render_report(report: Mapping[str, Any]) -> str:
    summary = report.get("summary", {})
    if not isinstance(summary, Mapping):
        summary = {}
    lines = [
        "Relay-kit skill proof audit",
        f"- status: {report.get('status')}",
        f"- skills: {summary.get('skill_count', 0)}",
        f"- theoretical: {summary.get('theoretical', 0)}",
        f"- validated: {summary.get('validated', 0)}",
        f"- field-tested: {summary.get('field_tested', 0)}",
        f"- findings: {summary.get('findings', 0)}",
    ]
    for finding in list(report.get("findings", []))[:12]:
        if isinstance(finding, Mapping):
            lines.append(f"  - {finding.get('skill', '-')}: {finding.get('summary', '-')}")
    return "\n".join(lines)


def write_report(root: Path | str, report: Mapping[str, Any], output_file: Path | str | None = None) -> Path:
    project = Path(root).resolve()
    path = Path(output_file) if output_file else project / ".relay-kit" / "eval" / "skill-proof-audit.json"
    if not path.is_absolute():
        path = project / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit proof status for Relay-kit skills.")
    parser.add_argument("project_path", nargs="?", default=".", help="Project root")
    parser.add_argument("--workflow-fixture", default=None, help="Optional workflow scenario fixture JSON")
    parser.add_argument("--real-world-cases-file", default=None, help="Optional real-world skill case fixture JSON")
    parser.add_argument("--output-file", default=None, help="Optional JSON report path")
    parser.add_argument("--strict", action="store_true", help="Return non-zero if any skill is theoretical")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable report")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(
        args.project_path,
        workflow_fixture=args.workflow_fixture,
        real_world_cases_file=args.real_world_cases_file,
        strict=args.strict,
    )
    if args.output_file:
        write_report(args.project_path, report, args.output_file)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_report(report))
    if args.strict and report["status"] != "pass":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
