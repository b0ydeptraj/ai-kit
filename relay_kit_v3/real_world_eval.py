"""Real-world skill contract evaluation for Relay-kit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping, Sequence

from relay_kit_v3.registry.skills import ALL_V3_SKILLS, render_skill


SCHEMA_VERSION = "relay-kit.real-world-skill-eval.v1"
DEFAULT_CASE_FIXTURE = Path("relay_kit_v3") / "eval_fixtures" / "real_world_skill_cases.json"
REPO_ROOT = Path(__file__).resolve().parents[1]


def load_cases(project_path: Path | str, fixture_path: Path | str | None = None) -> list[dict[str, object]]:
    root = Path(project_path)
    path = _resolve_fixture_path(root, Path(fixture_path) if fixture_path is not None else DEFAULT_CASE_FIXTURE)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Real-world skill fixture must contain a list: {path}")
    cases: list[dict[str, object]] = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError(f"Real-world skill fixture item must be an object: {path}")
        cases.append(item)
    return cases


def build_report(
    project_path: Path | str,
    *,
    fixture_path: Path | str | None = None,
    cases_file: Path | str | None = None,
    cases: Sequence[Mapping[str, object]] | None = None,
    min_term_coverage: float = 1.0,
) -> dict[str, object]:
    root = Path(project_path)
    selected_fixture = fixture_path if fixture_path is not None else cases_file
    fixture = Path(selected_fixture) if selected_fixture is not None else DEFAULT_CASE_FIXTURE
    case_rows = [dict(case) for case in cases] if cases is not None else load_cases(root, fixture)
    results = [
        evaluate_case(case, ALL_V3_SKILLS, min_term_coverage=min_term_coverage)
        for case in case_rows
    ]
    findings = [
        {
            "case_id": str(result["id"]),
            "skill": str(result["skill"]),
            "check": str(finding["check"]),
            "detail": str(finding["detail"]),
        }
        for result in results
        for finding in result["findings"]
        if isinstance(finding, Mapping)
    ]
    passed = sum(1 for result in results if result["passed"])
    failed = len(results) - passed
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass" if failed == 0 and not findings else "fail",
        "project_path": str(root),
        "fixture_path": str(fixture),
        "case_count": len(results),
        "passed": passed,
        "failed": failed,
        "min_term_coverage": min_term_coverage,
        "findings_count": len(findings),
        "findings": findings,
        "results": results,
    }


def evaluate_case(
    case: Mapping[str, object],
    registry: Mapping[str, object],
    *,
    min_term_coverage: float = 1.0,
) -> dict[str, object]:
    case_id = str(case.get("id", "")).strip() or "unnamed-case"
    skill = str(case.get("skill", "")).strip()
    task = str(case.get("task", "")).strip()
    required_artifacts = _string_list(case.get("required_artifacts"))
    required_evidence = _string_list(case.get("required_evidence"))
    pass_rubric = _string_list(case.get("pass_rubric"))
    findings: list[dict[str, str]] = []

    if not str(case.get("id", "")).strip():
        findings.append({"check": "case-contract", "detail": "Missing id"})
    if not skill:
        findings.append({"check": "case-contract", "detail": "Missing skill"})
    if not task:
        findings.append({"check": "case-contract", "detail": "Missing task"})
    _require_nonempty_list(case, "required_artifacts", required_artifacts, findings)
    _require_nonempty_list(case, "required_evidence", required_evidence, findings)
    _require_nonempty_list(case, "pass_rubric", pass_rubric, findings)

    matched_terms: list[str] = []
    required_terms = required_evidence + pass_rubric
    missing_terms: list[str] = []
    if skill and skill not in registry:
        term_coverage = 0.0
        missing_terms = required_terms
        findings.append({"check": "skill-exists", "detail": f"Unknown skill: {skill}"})
    elif skill:
        contract = render_skill(registry[skill]).lower()
        for term in required_terms:
            if term.lower() in contract:
                matched_terms.append(term)
            else:
                missing_terms.append(term)

        term_coverage = _coverage(len(matched_terms), len(required_terms))
        if term_coverage < min_term_coverage:
            findings.append(
                {
                    "check": "contract-terms",
                    "detail": (
                        f"Skill {skill} matched {len(matched_terms)}/{len(required_terms)} "
                        f"required evidence/rubric terms; missing: {', '.join(missing_terms)}"
                    ),
                }
            )
    else:
        term_coverage = 0.0
        missing_terms = required_terms

    return {
        "id": case_id,
        "skill": skill,
        "task": task,
        "required_artifacts": required_artifacts,
        "required_evidence": required_evidence,
        "pass_rubric": pass_rubric,
        "required_term_count": len(required_terms),
        "matched_term_count": len(matched_terms),
        "term_coverage": term_coverage,
        "missing_terms": missing_terms,
        "passed": not findings,
        "findings": findings,
    }


def render_text(report: Mapping[str, object]) -> str:
    lines = [
        "Relay-kit real-world skill eval",
        f"- project: {report['project_path']}",
        f"- fixture: {report['fixture_path']}",
        f"- cases: {report['case_count']}",
        f"- passed: {report['passed']}",
        f"- failed: {report['failed']}",
        f"- status: {report['status']}",
    ]
    findings = list(report.get("findings", []))
    if findings:
        lines.append("")
        lines.append("Top findings:")
        for finding in findings[:20]:
            if isinstance(finding, Mapping):
                lines.append(f"- {finding['case_id']} {finding['check']}: {finding['detail']}")
        if len(findings) > 20:
            lines.append(f"- ... and {len(findings) - 20} more")
    return "\n".join(lines)


def render_report(report: Mapping[str, object]) -> str:
    return render_text(report)


def write_report(*args: object) -> Path:
    if len(args) == 2:
        report, output_file = args
        path = Path(str(output_file))
    elif len(args) == 3:
        root, report, output_file = args
        path = Path(str(output_file))
        if not path.is_absolute():
            path = Path(str(root)) / path
    else:
        raise TypeError("write_report expects (report, output_file) or (root, report, output_file)")
    if not isinstance(report, Mapping):
        raise TypeError("report must be a mapping")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate real-world Relay-kit skill fixture contracts.",
    )
    parser.add_argument("project_path", nargs="?", default=".", help="Target project root")
    parser.add_argument(
        "--case-fixtures",
        default=str(DEFAULT_CASE_FIXTURE),
        help="JSON real-world case fixture file.",
    )
    parser.add_argument("--output-file", default=None, help="Optional JSON report output path")
    parser.add_argument("--min-term-coverage", type=float, default=1.0, help="Minimum evidence/rubric term coverage")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when any case fails")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(
        args.project_path,
        fixture_path=args.case_fixtures,
        min_term_coverage=args.min_term_coverage,
    )
    if args.output_file:
        write_report(report, args.output_file)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_text(report))
    if args.strict and report["status"] != "pass":
        return 2
    return 0


def _resolve_fixture_path(root: Path, fixture_path: Path) -> Path:
    candidates = [fixture_path]
    if not fixture_path.is_absolute():
        candidates.append(root / fixture_path)
        candidates.append(REPO_ROOT / fixture_path)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Real-world skill fixture not found: {fixture_path}")


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _require_nonempty_list(
    case: Mapping[str, object],
    field: str,
    parsed: Sequence[str],
    findings: list[dict[str, str]],
) -> None:
    if not isinstance(case.get(field), list):
        findings.append({"check": "case-contract", "detail": f"{field} must be a list"})
    elif not parsed:
        findings.append({"check": "case-contract", "detail": f"{field} must not be empty"})


def _coverage(matched: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round(matched / total, 4)


if __name__ == "__main__":
    raise SystemExit(main())
