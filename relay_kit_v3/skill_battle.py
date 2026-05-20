from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from relay_kit_v3.competency_catalog import competency_coverage_for_skill
from relay_kit_v3.context_index import build_context_index, build_context_search, write_context_index
from relay_kit_v3.intent_enhancer import build_prompt_enhancement
from relay_kit_v3.registry.skills import ALL_V3_SKILLS


SCHEMA_VERSION = "relay-kit.skill-battle.v1"
WEAKNESS_SCHEMA_VERSION = "relay-kit.skill-weakness-report.v1"
RESOURCE_ROOT = Path(__file__).resolve().parent / "skill_resources"
TEMP_ROOT = ".tmp/relay-kit-skill-battle"

GENERIC_TRAPS = (
    "usual checklist",
    "looks like",
    "should be fine",
    "guess from the name",
    "no file path",
)

OVERCLAIM_TRAPS = (
    "field-tested",
    "expert guarantee",
    "guaranteed expert",
    "replaces augment",
    "full context engine",
)


@dataclass(frozen=True)
class SkillBattleCase:
    id: str
    skill: str
    repo_profile: str
    task: str
    query: str
    expected_files: tuple[str, ...]
    expected_symbols: tuple[str, ...]
    expected_tests: tuple[str, ...]
    expected_evidence_terms: tuple[str, ...]
    bad_answer_traps: tuple[str, ...]


def build_skill_battle(
    project_root: Path | str,
    *,
    skill: str = "all",
    suite: str = "deep",
    cleanup: bool = False,
    min_score: float = 8.0,
) -> dict[str, Any]:
    if suite != "deep":
        raise ValueError(f"Unknown skill battle suite: {suite}")
    project = Path(project_root).resolve()
    skill_names = _selected_skills(skill)
    temp_root = project / TEMP_ROOT
    temp_root.mkdir(parents=True, exist_ok=True)
    reports: list[dict[str, Any]] = []
    try:
        for skill_name in skill_names:
            reports.append(_run_skill(project, temp_root, skill_name))
    finally:
        if cleanup:
            _cleanup_temp_root(project, temp_root)
    weak = [item for item in reports if float(item.get("score", 0)) < min_score]
    maxed = [item for item in reports if float(item.get("score", 0)) >= 10.0]
    strong = [item for item in reports if 8.0 <= float(item.get("score", 0)) < 10.0]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass" if not weak else "fail",
        "project_path": str(project),
        "suite": suite,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scoring": {
            "retrieval_file_evidence": 3,
            "symbol_test_evidence": 2,
            "domain_evidence_terms": 2,
            "routing_ask_act": 1,
            "generic_overclaim_guard": 2,
            "min_score": min_score,
        },
        "summary": {
            "skill_count": len(reports),
            "battle_max_on_suite": len(maxed),
            "battle_strong_needs_more_cases": len(strong),
            "needs_hardening": len([item for item in reports if 6 <= float(item.get("score", 0)) < 8]),
            "generic_or_routing_weak": len([item for item in reports if float(item.get("score", 0)) < 6]),
            "weakest_score": min((float(item.get("score", 0)) for item in reports), default=0.0),
        },
        "skills": reports,
        "findings": [finding for item in reports for finding in item.get("findings", [])],
    }


def build_skill_weakness_report(
    project_root: Path | str,
    *,
    battle_report: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    project = Path(project_root).resolve()
    report = dict(battle_report or build_skill_battle(project, skill="all", suite="deep", cleanup=True))
    findings = list(report.get("findings", []))
    weak_skills = [
        {
            "skill": item.get("skill"),
            "score": item.get("score"),
            "status": item.get("status"),
            "suggested_fixes": sorted({finding.get("suggested_fix") for finding in item.get("findings", []) if finding.get("suggested_fix")}),
        }
        for item in report.get("skills", [])
        if float(item.get("score", 0)) < 10.0
    ]
    return {
        "schema_version": WEAKNESS_SCHEMA_VERSION,
        "status": "pass" if not findings else "fail",
        "project_path": str(project),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_schema_version": report.get("schema_version"),
        "summary": {
            "skill_count": report.get("summary", {}).get("skill_count", 0),
            "weak_skill_count": len(weak_skills),
            "finding_count": len(findings),
        },
        "weak_skills": weak_skills,
        "findings": findings,
    }


def write_skill_battle(project_root: Path | str, report: Mapping[str, Any], output_file: Path | str) -> Path:
    project = Path(project_root).resolve()
    target = Path(output_file)
    if not target.is_absolute():
        target = project / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return target


def render_skill_battle(report: Mapping[str, Any]) -> str:
    summary = report.get("summary", {})
    lines = [
        "Relay-kit skill battle",
        f"- status: {report.get('status')}",
        f"- suite: {report.get('suite')}",
        f"- skills: {summary.get('skill_count', 0)}",
        f"- max: {summary.get('battle_max_on_suite', 0)}",
        f"- strong: {summary.get('battle_strong_needs_more_cases', 0)}",
        f"- weak: {summary.get('needs_hardening', 0) + summary.get('generic_or_routing_weak', 0)}",
    ]
    for item in report.get("skills", [])[:12]:
        lines.append(f"  - {item.get('skill')}: {item.get('score')}/10 {item.get('status')}")
    return "\n".join(lines)


def render_skill_weakness_report(report: Mapping[str, Any]) -> str:
    lines = [
        "Relay-kit skill weakness report",
        f"- status: {report.get('status')}",
        f"- weak skills: {report.get('summary', {}).get('weak_skill_count', 0)}",
        f"- findings: {report.get('summary', {}).get('finding_count', 0)}",
    ]
    for item in report.get("weak_skills", [])[:12]:
        lines.append(f"  - {item.get('skill')}: {item.get('score')}/10 {item.get('status')}")
    return "\n".join(lines)


def _selected_skills(skill: str) -> list[str]:
    if skill == "all":
        return sorted(ALL_V3_SKILLS)
    if skill not in ALL_V3_SKILLS:
        raise ValueError(f"Unknown skill: {skill}")
    return [skill]


def _run_skill(project: Path, temp_root: Path, skill_name: str) -> dict[str, Any]:
    cases = _load_cases(skill_name)
    case_reports = [_run_case(project, temp_root, case) for case in cases]
    average_score = round(sum(float(item.get("score", 0)) for item in case_reports) / max(len(case_reports), 1), 2)
    findings = [finding for case in case_reports for finding in case.get("findings", [])]
    status = _status_for_score(average_score)
    competency = competency_coverage_for_skill(skill_name)
    for finding in competency.get("findings", []):
        findings.append(
            {
                "severity": "high",
                "skill": skill_name,
                "case": "competency-profile",
                "finding": str(finding),
                "suggested_fix": "Refresh the skill competency profile before claiming battle max.",
            }
        )
    if competency.get("coverage_score", 0) < 1:
        status = "needs-hardening"
    return {
        "skill": skill_name,
        "score": average_score,
        "status": status,
        "claim_status": status,
        "covered_competencies": competency.get("covered_competencies", []),
        "missing_competencies": competency.get("missing_competencies", []),
        "coverage_score": competency.get("coverage_score", 0),
        "unknown_domain_mode": competency.get("unknown_domain_mode", False),
        "case_count": len(case_reports),
        "cases": case_reports,
        "findings": findings,
    }


def _run_case(project: Path, temp_root: Path, case: SkillBattleCase) -> dict[str, Any]:
    fixture = _write_case_fixture(temp_root, case)
    index = build_context_index(fixture)
    write_context_index(fixture, index)
    search = build_context_search(fixture, query=case.query, limit=20)
    prompt = build_prompt_enhancement(fixture, prompt=case.task)
    resource_text = _resource_text(case.skill)
    guard_text = _resource_text(case.skill, include_bad=False)
    result_paths = [str(item.get("path")) for item in search.get("results", [])]
    indexed_symbols = {str(symbol) for item in index.get("files", []) for symbol in item.get("symbols", [])}
    evidence_text = _case_evidence_text(search, prompt, resource_text)
    matched_files = [expected for expected in case.expected_files if any(expected in path for path in result_paths)]
    matched_symbols = [symbol for symbol in case.expected_symbols if symbol in indexed_symbols]
    matched_tests = [expected for expected in case.expected_tests if any(expected in path for path in result_paths)]
    matched_evidence = [term for term in case.expected_evidence_terms if _evidence_term_present(term, evidence_text)]
    findings: list[dict[str, Any]] = []
    score_breakdown = {
        "retrieval_file_evidence": _ratio_score(len(matched_files), len(case.expected_files), 3),
        "symbol_test_evidence": _symbol_test_score(matched_symbols, case.expected_symbols, matched_tests, case.expected_tests),
        "domain_evidence_terms": _ratio_score(len(matched_evidence), len(case.expected_evidence_terms), 2),
        "routing_ask_act": _routing_score(case, prompt),
        "generic_overclaim_guard": _generic_guard_score(guard_text, resource_text, case.bad_answer_traps, findings, case),
    }
    if score_breakdown["retrieval_file_evidence"] < 3:
        findings.append(_finding(case, "retrieval", "Expected files were not all found.", "Update eval expected_files or context search terms."))
    if score_breakdown["symbol_test_evidence"] < 2:
        findings.append(_finding(case, "symbol-test", "Expected symbols or tests were not proven.", "Add stronger symbol/test anchors to the resource eval."))
    if score_breakdown["domain_evidence_terms"] < 2:
        findings.append(_finding(case, "evidence", "Expected evidence terms were not fully present.", "Rewrite examples/contracts with concrete evidence terms."))
    if score_breakdown["routing_ask_act"] < 1:
        findings.append(_finding(case, "routing", "Prompt enhancement did not route to the expected skill.", "Update workflow route fixtures or trigger text."))
    score = round(sum(score_breakdown.values()), 2)
    return {
        "id": case.id,
        "skill": case.skill,
        "status": "pass" if score >= 8 else "fail",
        "score": score,
        "score_breakdown": score_breakdown,
        "repo_profile": case.repo_profile,
        "task": case.task,
        "query": case.query,
        "matched_files": matched_files,
        "matched_symbols": matched_symbols,
        "matched_tests": matched_tests,
        "matched_evidence_terms": matched_evidence,
        "prompt_enhance": {
            "recommended_skill": prompt.get("recommended_skill"),
            "top_candidates": prompt.get("top_candidates", [])[:3],
            "ask_or_act": prompt.get("ask_or_act"),
            "context_index_status": prompt.get("context_index_status"),
        },
        "search_results": search.get("results", [])[:8],
        "findings": findings,
    }


def _load_cases(skill_name: str) -> list[SkillBattleCase]:
    cases_path = RESOURCE_ROOT / skill_name / "evals" / f"{skill_name}-cases.json"
    raw_cases = json.loads(cases_path.read_text(encoding="utf-8"))
    loaded = [_case_from_mapping(skill_name, raw) for raw in raw_cases if isinstance(raw, Mapping)]
    while len(loaded) < 3:
        loaded.append(_synthesized_case(skill_name, len(loaded)))
    return loaded[:3]


def _case_from_mapping(skill_name: str, raw: Mapping[str, Any]) -> SkillBattleCase:
    expected_files = tuple(str(item) for item in raw.get("expected_files", []) if item)
    expected_tests = tuple(str(item) for item in raw.get("expected_tests", []) if item)
    if not expected_tests:
        expected_tests = tuple(path for path in expected_files if re.search(r"test|spec", path, flags=re.IGNORECASE))
    query_parts = [raw.get("task", ""), *raw.get("expected_files", []), *raw.get("expected_evidence_terms", []), *raw.get("expected_symbols", [])]
    return SkillBattleCase(
        id=str(raw.get("id") or f"{skill_name}-case"),
        skill=str(raw.get("skill") or skill_name),
        repo_profile=str(raw.get("repo_profile") or "deep skill battle fixture"),
        task=str(raw.get("task") or f"Use {skill_name} with concrete evidence."),
        query=" ".join(str(part) for part in query_parts if part),
        expected_files=expected_files,
        expected_symbols=tuple(str(item) for item in raw.get("expected_symbols", []) if item),
        expected_tests=expected_tests,
        expected_evidence_terms=tuple(str(item) for item in raw.get("expected_evidence_terms", []) if item),
        bad_answer_traps=tuple(str(item) for item in raw.get("bad_answer_traps", GENERIC_TRAPS) if item),
    )


def _synthesized_case(skill_name: str, index: int) -> SkillBattleCase:
    return SkillBattleCase(
        id=f"{skill_name}-deep-evidence-{index + 1}",
        skill=skill_name,
        repo_profile="deep Relay-kit suite fixture with source, test, docs, and overclaim traps",
        task=f"Use `{skill_name}` on a deep repo case and prove file, symbol, test, and evidence anchors before claiming strength.",
        query=f"{skill_name} evidence test residual risk generated skill",
        expected_files=("src/battle/source.py", "tests/test_battle.py", "docs/battle.md"),
        expected_symbols=("battle_entrypoint", "test_battle_evidence"),
        expected_tests=("tests/test_battle.py",),
        expected_evidence_terms=("evidence", "residual risk", "verified", "test"),
        bad_answer_traps=GENERIC_TRAPS,
    )


def _write_case_fixture(temp_root: Path, case: SkillBattleCase) -> Path:
    root = temp_root / _safe_name(case.skill) / _safe_name(case.id)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    terms = " ".join(case.expected_evidence_terms)
    symbols = list(case.expected_symbols) or ["battle_entrypoint"]
    for expected in case.expected_files:
        path = root / expected
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_fixture_text(path, case, symbols, terms), encoding="utf-8")
    for expected in case.expected_tests:
        path = root / expected
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_fixture_text(path, case, symbols, terms), encoding="utf-8")
    (root / "README.md").write_text(
        f"# {case.skill} battle fixture\n\n{case.repo_profile}\n\n{case.task}\n\nEvidence: {terms}\n",
        encoding="utf-8",
    )
    return root


def _fixture_text(path: Path, case: SkillBattleCase, symbols: Sequence[str], terms: str) -> str:
    suffix = path.suffix.lower()
    safe_symbols = [_safe_symbol(symbol) for symbol in symbols]
    if suffix == ".py":
        lines: list[str] = []
        for symbol in safe_symbols:
            lines.extend([f"def {symbol}():", f"    return '{case.skill} {terms} verified residual risk test'", ""])
        return "\n".join(lines) + "\n"
    if suffix in {".ts", ".tsx", ".js", ".jsx"}:
        return "\n".join(
            f"export function {symbol}() {{ return '{case.skill} {terms} verified residual risk test'; }}"
            for symbol in safe_symbols
        ) + "\n"
    if suffix == ".go":
        return "package battle\n\n" + "\n".join(
            f"func {symbol}() string {{ return \"{case.skill} {terms} verified residual risk test\" }}"
            for symbol in safe_symbols
        ) + "\n"
    headings = "\n".join(f"## {_safe_symbol(symbol)}" for symbol in symbols)
    return f"{case.skill}\n{case.task}\n{headings}\n{terms}\nverified residual risk test\n"


def _resource_text(skill_name: str, *, include_bad: bool = True) -> str:
    root = RESOURCE_ROOT / skill_name
    paths = [
        root / "references" / f"{skill_name}-operator-contract.md",
        root / "examples" / f"{skill_name}-good-output.md",
    ]
    if include_bad:
        paths.append(root / "examples" / f"{skill_name}-bad-output.md")
    parts: list[str] = []
    for path in paths:
        if path.exists():
            parts.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts).casefold()


def _case_evidence_text(search: Mapping[str, Any], prompt: Mapping[str, Any], resource_text: str) -> str:
    return " ".join(
        [
            json.dumps(search.get("results", []), ensure_ascii=True),
            json.dumps(prompt, ensure_ascii=True),
            resource_text,
        ]
    ).casefold()


def _evidence_term_present(term: str, evidence_text: str) -> bool:
    normalized = term.casefold()
    if normalized in evidence_text:
        return True
    parts = [part for part in re.findall(r"[a-z0-9]+", normalized) if len(part) >= 3]
    return bool(parts) and all(part in evidence_text for part in parts)


def _ratio_score(matched: int, expected: int, weight: float) -> float:
    if expected <= 0:
        return weight
    return round(weight * min(matched / expected, 1.0), 2)


def _symbol_test_score(
    matched_symbols: Sequence[str],
    expected_symbols: Sequence[str],
    matched_tests: Sequence[str],
    expected_tests: Sequence[str],
) -> float:
    symbol_score = _ratio_score(len(matched_symbols), len(expected_symbols), 1)
    test_score = _ratio_score(len(matched_tests), len(expected_tests), 1)
    return round(symbol_score + test_score, 2)


def _routing_score(case: SkillBattleCase, prompt: Mapping[str, Any]) -> float:
    skill_name = case.skill
    if skill_name in case.task or f"`{skill_name}`" in case.task:
        return 1.0
    recommended = str(prompt.get("recommended_skill", ""))
    candidates = [str(item.get("skill", "")) for item in prompt.get("top_candidates", []) if isinstance(item, Mapping)]
    if recommended == skill_name or skill_name in candidates:
        return 1.0
    return 0.0


def _generic_guard_score(
    guard_text: str,
    full_resource_text: str,
    traps: Sequence[str],
    findings: list[dict[str, Any]],
    case: SkillBattleCase,
) -> float:
    for trap in traps:
        if trap and trap.casefold() in guard_text and trap.casefold() not in {"no file path"}:
            findings.append(_finding(case, "generic-overclaim", f"Resource contains trap phrase `{trap}`.", "Rewrite bad examples as traps without leaking weak wording into good guidance."))
            return 0.0
    for trap in OVERCLAIM_TRAPS:
        if trap and trap.casefold() in full_resource_text:
            findings.append(_finding(case, "generic-overclaim", f"Resource contains overclaim phrase `{trap}`.", "Remove overclaim and tie the skill claim to battle-suite evidence."))
            return 0.0
    return 2.0


def _status_for_score(score: float) -> str:
    if score >= 10:
        return "battle-max-on-suite"
    if score >= 8:
        return "battle-strong-needs-more-cases"
    if score >= 6:
        return "needs-hardening"
    return "generic-or-routing-weak"


def _finding(case: SkillBattleCase, finding_type: str, message: str, suggested_fix: str) -> dict[str, Any]:
    return {
        "severity": "high" if finding_type in {"generic-overclaim", "retrieval"} else "medium",
        "skill": case.skill,
        "case": case.id,
        "type": finding_type,
        "message": message,
        "suggested_fix": suggested_fix,
        "resource_candidates": [
            f"relay_kit_v3/skill_resources/{case.skill}/references/{case.skill}-operator-contract.md",
            f"relay_kit_v3/skill_resources/{case.skill}/examples/{case.skill}-good-output.md",
            f"relay_kit_v3/skill_resources/{case.skill}/evals/{case.skill}-cases.json",
        ],
    }


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-") or "case"


def _safe_symbol(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_]+", "_", value).strip("_")
    if not safe or not re.match(r"[A-Za-z_]", safe):
        safe = f"symbol_{safe}"
    return safe


def _cleanup_temp_root(project: Path, target: Path) -> None:
    resolved_project = project.resolve()
    resolved_target = target.resolve()
    allowed_root = (resolved_project / TEMP_ROOT).resolve()
    if resolved_target != allowed_root and allowed_root not in resolved_target.parents:
        raise ValueError(f"Refusing to remove path outside skill battle temp root: {resolved_target}")
    if resolved_target.exists():
        shutil.rmtree(resolved_target)
