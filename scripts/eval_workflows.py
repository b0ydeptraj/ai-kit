#!/usr/bin/env python3
"""Scenario evaluation harness for Relay-kit workflow routing."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from relay_kit_v3.registry.skills import ALL_V3_SKILLS
from scripts.skill_gauntlet import (
    DEFAULT_SCENARIO_FIXTURE,
    load_scenario_fixtures,
    rank_prompt_routes,
    rendered_skill_contract,
    resolve_scenario_fixture_path,
)


SCHEMA_VERSION = "relay-kit.workflow-eval.v1"
DEFAULT_MIN_PASS_RATE = 1.0
DEFAULT_MIN_ROUTE_MARGIN = 1
DEFAULT_MIN_EVIDENCE_COVERAGE = 1.0
WEAK_ROUTE_MARGIN_THRESHOLD = 3
SUPPORT_ROUTE_MARGIN_THRESHOLD = 3
WEAK_ROUTE_LIMIT = 8
PROFILED_SUPPORT_SKILLS = {
    "api-integration",
    "browser-inspector",
    "data-persistence",
    "dependency-management",
    "media-tooling",
    "multimodal-evidence",
}
PROFILED_SUPPORT_EVIDENCE_TERMS = {
    "api-integration": ("clients", "auth", "retries"),
    "browser-inspector": ("console", "network", "reproduction confidence"),
    "data-persistence": ("schemas", "migrations", "transactions"),
    "dependency-management": ("lockfiles", "version pinning", "dependency risks"),
    "media-tooling": ("transformations", "asset sources", "outputs"),
    "multimodal-evidence": ("visible observations", "confidence", "follow-up checks"),
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate Relay-kit workflow routing scenarios and report pass-rate signals.",
    )
    parser.add_argument("project_path", nargs="?", default=".", help="Target project root")
    parser.add_argument(
        "--scenario-fixtures",
        default=str(DEFAULT_SCENARIO_FIXTURE),
        help="JSON scenario fixture file.",
    )
    parser.add_argument("--output-file", default=None, help="Optional JSON report output path")
    parser.add_argument("--baseline-file", default=None, help="Optional prior workflow eval JSON used for regression checks")
    parser.add_argument("--min-pass-rate", type=float, default=DEFAULT_MIN_PASS_RATE, help="Minimum accepted scenario pass rate")
    parser.add_argument("--min-route-margin", type=int, default=DEFAULT_MIN_ROUTE_MARGIN, help="Minimum top-route score margin")
    parser.add_argument(
        "--min-evidence-coverage",
        type=float,
        default=DEFAULT_MIN_EVIDENCE_COVERAGE,
        help="Minimum expected-term coverage across all scenarios",
    )
    parser.add_argument("--min-scenarios", type=int, default=None, help="Minimum scenario count")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when any scenario fails")
    return parser.parse_args(argv)


def evaluate_scenario(
    scenario: Mapping[str, object],
    registry: Mapping[str, object],
    *,
    top_limit: int = 5,
) -> dict[str, object]:
    scenario_id = str(scenario.get("id", "")).strip() or "unnamed-scenario"
    prompt = str(scenario.get("prompt", "")).strip()
    expected_skill = str(scenario.get("expected_skill", "")).strip()
    expected_layer = skill_metadata(registry, expected_skill, "layer")
    expected_role = skill_metadata(registry, expected_skill, "role")
    expected_terms = scenario.get("expected_terms", [])
    findings: list[dict[str, str]] = []
    ranked: list[tuple[int, str]] = []
    predicted_skill = ""
    top_score = 0
    second_score = 0
    route_margin = 0
    route_confidence = 0.0
    missing_terms: list[str] = []

    if not prompt:
        findings.append({"check": "scenario-contract", "detail": "Missing prompt"})
    if not expected_skill:
        findings.append({"check": "scenario-contract", "detail": "Missing expected_skill"})
    elif expected_skill not in registry:
        findings.append({"check": "scenario-contract", "detail": f"Unknown expected_skill: {expected_skill}"})

    if not isinstance(expected_terms, list):
        findings.append({"check": "scenario-contract", "detail": "expected_terms must be a list"})
        expected_terms = []

    if prompt and expected_skill in registry:
        ranked = rank_prompt_routes(prompt, registry)
        top_score, predicted_skill = ranked[0] if ranked else (0, "")
        second_score = ranked[1][0] if len(ranked) > 1 else 0
        route_margin = max(top_score - second_score, 0)
        route_confidence = round(top_score / (top_score + second_score), 4) if top_score + second_score else 0.0
        if predicted_skill != expected_skill:
            top = ", ".join(f"{name}:{score}" for score, name in ranked[:top_limit])
            findings.append(
                {
                    "check": "scenario-route",
                    "detail": (
                        f"Expected {expected_skill}, predicted {predicted_skill or '-'} "
                        f"with score {top_score}. Top routes: {top}"
                    ),
                }
            )

        contract = rendered_skill_contract(registry[expected_skill])
        missing_terms = [
            str(term)
            for term in expected_terms
            if str(term).strip() and str(term).lower() not in contract
        ]
        if missing_terms:
            findings.append(
                {
                    "check": "scenario-evidence-contract",
                    "detail": f"Expected skill {expected_skill} is missing scenario terms: {', '.join(missing_terms)}",
                }
            )
    else:
        missing_terms = []

    expected_term_values = [str(term) for term in expected_terms if str(term).strip()]
    evidence_terms_count = len(expected_term_values)
    matched_terms_count = max(evidence_terms_count - len(missing_terms), 0)
    evidence_coverage = round(matched_terms_count / evidence_terms_count, 4) if evidence_terms_count else 1.0

    return {
        "id": scenario_id,
        "prompt": prompt,
        "expected_skill": expected_skill,
        "expected_layer": expected_layer,
        "expected_role": expected_role,
        "predicted_skill": predicted_skill,
        "predicted_layer": skill_metadata(registry, predicted_skill, "layer"),
        "predicted_role": skill_metadata(registry, predicted_skill, "role"),
        "passed": not findings,
        "top_score": top_score,
        "second_score": second_score,
        "route_margin": route_margin,
        "route_confidence": route_confidence,
        "top_routes": [{"skill": name, "score": score} for score, name in ranked[:top_limit]],
        "expected_terms": expected_term_values,
        "missing_terms": missing_terms,
        "evidence_terms_count": evidence_terms_count,
        "matched_terms_count": matched_terms_count,
        "evidence_coverage": evidence_coverage,
        "findings": findings,
    }


def build_report(
    project_path: Path | str,
    *,
    scenario_fixtures: Path | str | None = None,
    baseline_file: Path | str | None = None,
    min_pass_rate: float = DEFAULT_MIN_PASS_RATE,
    min_route_margin: int = DEFAULT_MIN_ROUTE_MARGIN,
    min_evidence_coverage: float = DEFAULT_MIN_EVIDENCE_COVERAGE,
    min_scenarios: int | None = None,
) -> dict[str, object]:
    base = Path(project_path).resolve()
    fixture_path = Path(scenario_fixtures) if scenario_fixtures is not None else DEFAULT_SCENARIO_FIXTURE
    resolved_fixture = resolve_scenario_fixture_path(base, fixture_path)
    scenarios = load_scenario_fixtures(base, fixture_path)
    results = [evaluate_scenario(scenario, ALL_V3_SKILLS) for scenario in scenarios]
    failed = sum(1 for result in results if not result["passed"])
    passed = len(results) - failed
    scenario_count = len(results)
    pass_rate = round(passed / scenario_count, 4) if scenario_count else 0.0
    quality = quality_metrics(results)
    thresholds = {
        "min_pass_rate": min_pass_rate,
        "min_route_margin": min_route_margin,
        "min_evidence_coverage": min_evidence_coverage,
        "min_scenarios": min_scenarios,
    }

    harness_findings: list[dict[str, str]] = []
    if resolved_fixture is None:
        harness_findings.append(
            {
                "check": "scenario-fixtures",
                "detail": f"Scenario fixture file not found: {fixture_path}",
            }
        )
    elif scenario_count == 0:
        harness_findings.append(
            {
                "check": "scenario-fixtures",
                "detail": f"Scenario fixture file contains no scenarios: {resolved_fixture}",
            }
        )
    harness_findings.extend(
        threshold_findings(
            pass_rate=pass_rate,
            scenario_count=scenario_count,
            quality=quality,
            min_pass_rate=min_pass_rate,
            min_route_margin=min_route_margin,
            min_evidence_coverage=min_evidence_coverage,
            min_scenarios=min_scenarios,
        )
    )
    baseline = compare_baseline(base, baseline_file, pass_rate=pass_rate, scenario_count=scenario_count, quality=quality)
    if baseline:
        harness_findings.extend(baseline["findings"])

    scenario_findings_count = sum(
        len(result.get("findings", []))
        for result in results
        if isinstance(result.get("findings", []), list)
    )
    findings_count = scenario_findings_count + len(harness_findings)
    status = "pass" if findings_count == 0 else "fail"

    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "project_path": str(base),
        "fixture_path": str(resolved_fixture) if resolved_fixture else str(fixture_path),
        "scenario_count": scenario_count,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "quality": quality,
        "thresholds": thresholds,
        "baseline": baseline,
        "findings_count": findings_count,
        "findings": harness_findings,
        "results": results,
    }


def quality_metrics(results: list[dict[str, object]]) -> dict[str, object]:
    route_margins = [int(result.get("route_margin", 0)) for result in results if result.get("top_routes")]
    confidences = [float(result.get("route_confidence", 0.0)) for result in results if result.get("top_routes")]
    expected_terms = sum(int(result.get("evidence_terms_count", 0)) for result in results)
    matched_terms = sum(int(result.get("matched_terms_count", 0)) for result in results)
    expected_skills = [str(result.get("expected_skill", "")) for result in results if str(result.get("expected_skill", ""))]
    predicted_skills = [str(result.get("predicted_skill", "")) for result in results if str(result.get("predicted_skill", ""))]
    expected_layers = [str(result.get("expected_layer", "")) for result in results if str(result.get("expected_layer", ""))]
    predicted_layers = [str(result.get("predicted_layer", "")) for result in results if str(result.get("predicted_layer", ""))]
    expected_roles = [str(result.get("expected_role", "")) for result in results if str(result.get("expected_role", ""))]
    predicted_roles = [str(result.get("predicted_role", "")) for result in results if str(result.get("predicted_role", ""))]

    return {
        "min_route_margin": min(route_margins) if route_margins else 0,
        "average_route_margin": round(sum(route_margins) / len(route_margins), 4) if route_margins else 0.0,
        "max_route_margin": max(route_margins) if route_margins else 0,
        "mean_route_confidence": round(sum(confidences) / len(confidences), 4) if confidences else 0.0,
        "weak_route_threshold": WEAK_ROUTE_MARGIN_THRESHOLD,
        "weak_route_count": len(weak_routes(results)),
        "weak_routes": weak_routes(results),
        "support_route_review": support_route_review(results),
        "support_evidence_contract_review": support_evidence_contract_review(results),
        "coverage_gaps": coverage_gaps(
            expected_skills=expected_skills,
            expected_layers=expected_layers,
            expected_roles=expected_roles,
        ),
        "evidence_terms_count": expected_terms,
        "matched_terms_count": matched_terms,
        "evidence_term_coverage": round(matched_terms / expected_terms, 4) if expected_terms else 1.0,
        "unique_expected_skills": sorted(set(expected_skills)),
        "unique_predicted_skills": sorted(set(predicted_skills)),
        "unique_expected_layers": sorted(set(expected_layers)),
        "unique_predicted_layers": sorted(set(predicted_layers)),
        "unique_expected_roles": sorted(set(expected_roles)),
        "unique_predicted_roles": sorted(set(predicted_roles)),
        "expected_skill_counts": count_values(expected_skills),
        "predicted_skill_counts": count_values(predicted_skills),
        "expected_layer_counts": count_values(expected_layers),
        "predicted_layer_counts": count_values(predicted_layers),
        "expected_role_counts": count_values(expected_roles),
        "predicted_role_counts": count_values(predicted_roles),
    }


def support_route_review(results: list[dict[str, object]]) -> dict[str, object]:
    profiled = sorted(PROFILED_SUPPORT_SKILLS)
    covered = sorted(
        {
            str(result.get("expected_skill", ""))
            for result in results
            if str(result.get("expected_skill", "")) in PROFILED_SUPPORT_SKILLS
        }
    )
    missing = sorted(PROFILED_SUPPORT_SKILLS - set(covered))
    profiled_routes: list[dict[str, object]] = []
    weak_profiled: list[dict[str, object]] = []
    nearby_support: list[dict[str, object]] = []

    for result in results:
        expected_skill = str(result.get("expected_skill", ""))
        if expected_skill not in PROFILED_SUPPORT_SKILLS:
            continue

        top_routes = result.get("top_routes", [])
        support_competitors: list[dict[str, object]] = []
        if isinstance(top_routes, list):
            top_score = 0
            if top_routes and isinstance(top_routes[0], Mapping):
                top_score = _int_value(top_routes[0].get("score"))
            for route in top_routes[1:]:
                if not isinstance(route, Mapping):
                    continue
                route_skill = str(route.get("skill", ""))
                route_score = _int_value(route.get("score"))
                if (
                    route_skill in PROFILED_SUPPORT_SKILLS
                    and top_score - route_score <= SUPPORT_ROUTE_MARGIN_THRESHOLD
                ):
                    support_competitors.append(
                        {
                            "skill": route_skill,
                            "score": route_score,
                        }
                    )

        route_margin = _int_value(result.get("route_margin"))
        row = {
            "id": str(result.get("id", "")),
            "expected_skill": expected_skill,
            "predicted_skill": str(result.get("predicted_skill", "")),
            "route_margin": route_margin,
            "route_confidence": _float_value(result.get("route_confidence")),
            "top_routes": top_routes if isinstance(top_routes, list) else [],
            "support_competitors": support_competitors,
        }
        profiled_routes.append(row)

        if route_margin <= SUPPORT_ROUTE_MARGIN_THRESHOLD:
            weak_profiled.append(row)
            if support_competitors:
                nearby_support.append(row)

    weak_profiled = sorted(
        weak_profiled,
        key=lambda item: (
            _int_value(item.get("route_margin")),
            _float_value(item.get("route_confidence")),
            str(item.get("id", "")),
        ),
    )
    nearby_support = sorted(
        nearby_support,
        key=lambda item: (
            _int_value(item.get("route_margin")),
            _float_value(item.get("route_confidence")),
            str(item.get("id", "")),
        ),
    )
    return {
        "profiled_support_skills": profiled,
        "covered_profiled_support_skills": covered,
        "missing_profiled_support_skills": missing,
        "support_route_margin_threshold": SUPPORT_ROUTE_MARGIN_THRESHOLD,
        "profiled_support_route_count": len(profiled_routes),
        "profiled_support_routes": profiled_routes,
        "weak_profiled_support_route_count": len(weak_profiled),
        "weak_profiled_support_routes": weak_profiled[:WEAK_ROUTE_LIMIT],
        "nearby_support_route_count": len(nearby_support),
        "nearby_support_routes": nearby_support[:WEAK_ROUTE_LIMIT],
    }


def support_evidence_contract_review(results: list[dict[str, object]]) -> dict[str, object]:
    profiled = sorted(PROFILED_SUPPORT_EVIDENCE_TERMS)
    scenarios: list[dict[str, object]] = []
    term_gaps: list[dict[str, object]] = []
    prompt_gaps: list[dict[str, object]] = []

    for result in results:
        expected_skill = str(result.get("expected_skill", ""))
        if expected_skill not in PROFILED_SUPPORT_EVIDENCE_TERMS:
            continue

        scenario_id = str(result.get("id", ""))
        prompt = str(result.get("prompt", ""))
        expected_terms = [str(term) for term in _list_value(result.get("expected_terms")) if str(term).strip()]
        required_terms = list(PROFILED_SUPPORT_EVIDENCE_TERMS[expected_skill])
        lower_expected_terms = {term.lower() for term in expected_terms}
        lower_prompt = prompt.lower()
        missing_expected_terms = [
            term for term in required_terms if term.lower() not in lower_expected_terms
        ]
        missing_prompt_terms = [
            term for term in required_terms if term.lower() not in lower_prompt
        ]
        scenario = {
            "id": scenario_id,
            "expected_skill": expected_skill,
            "required_terms": required_terms,
            "expected_terms": expected_terms,
            "missing_expected_terms": missing_expected_terms,
            "missing_prompt_terms": missing_prompt_terms,
        }
        scenarios.append(scenario)
        if missing_expected_terms:
            term_gaps.append(
                {
                    "id": scenario_id,
                    "expected_skill": expected_skill,
                    "missing_terms": missing_expected_terms,
                }
            )
        if missing_prompt_terms:
            prompt_gaps.append(
                {
                    "id": scenario_id,
                    "expected_skill": expected_skill,
                    "missing_terms": missing_prompt_terms,
                }
            )

    return {
        "profiled_support_skills": profiled,
        "required_terms_by_skill": {
            skill: list(terms)
            for skill, terms in sorted(PROFILED_SUPPORT_EVIDENCE_TERMS.items())
        },
        "profiled_support_scenario_count": len(scenarios),
        "scenarios": scenarios,
        "term_gap_count": len(term_gaps),
        "term_gaps": term_gaps[:WEAK_ROUTE_LIMIT],
        "prompt_gap_count": len(prompt_gaps),
        "prompt_gaps": prompt_gaps[:WEAK_ROUTE_LIMIT],
    }


def weak_routes(results: list[dict[str, object]]) -> list[dict[str, object]]:
    candidates = [
        result
        for result in results
        if result.get("top_routes")
        and (
            not bool(result.get("passed", False))
            or int(result.get("route_margin", 0) or 0) <= WEAK_ROUTE_MARGIN_THRESHOLD
        )
    ]
    ranked = sorted(
        candidates,
        key=lambda result: (
            int(result.get("route_margin", 0) or 0),
            float(result.get("route_confidence", 0.0) or 0.0),
            str(result.get("id", "")),
        ),
    )
    return [
        {
            "id": str(result.get("id", "")),
            "expected_skill": str(result.get("expected_skill", "")),
            "predicted_skill": str(result.get("predicted_skill", "")),
            "route_margin": int(result.get("route_margin", 0) or 0),
            "route_confidence": float(result.get("route_confidence", 0.0) or 0.0),
            "top_routes": result.get("top_routes", []),
        }
        for result in ranked[:WEAK_ROUTE_LIMIT]
    ]


def coverage_gaps(
    *,
    expected_skills: list[str],
    expected_layers: list[str],
    expected_roles: list[str],
) -> dict[str, object]:
    registry_skills = sorted(ALL_V3_SKILLS)
    registry_layers = sorted(
        {str(getattr(spec, "layer", "")) for spec in ALL_V3_SKILLS.values() if str(getattr(spec, "layer", ""))}
    )
    registry_roles = sorted(
        {str(getattr(spec, "role", "")) for spec in ALL_V3_SKILLS.values() if str(getattr(spec, "role", ""))}
    )
    covered_skills = sorted(set(expected_skills))
    covered_layers = sorted(set(expected_layers))
    covered_roles = sorted(set(expected_roles))
    return {
        "registry_skill_count": len(registry_skills),
        "covered_skill_count": len(covered_skills),
        "covered_skill_ratio": round(len(covered_skills) / len(registry_skills), 4) if registry_skills else 1.0,
        "missing_skills": sorted(set(registry_skills) - set(covered_skills)),
        "missing_layers": sorted(set(registry_layers) - set(covered_layers)),
        "missing_roles": sorted(set(registry_roles) - set(covered_roles)),
    }


def threshold_findings(
    *,
    pass_rate: float,
    scenario_count: int,
    quality: Mapping[str, object],
    min_pass_rate: float,
    min_route_margin: int,
    min_evidence_coverage: float,
    min_scenarios: int | None,
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if pass_rate < min_pass_rate:
        findings.append(
            {
                "check": "quality-threshold",
                "detail": f"pass_rate {pass_rate:.4f} is below min_pass_rate {min_pass_rate:.4f}",
            }
        )
    if int(quality.get("min_route_margin", 0)) < min_route_margin:
        findings.append(
            {
                "check": "quality-threshold",
                "detail": (
                    f"min_route_margin {quality.get('min_route_margin')} is below "
                    f"min_route_margin threshold {min_route_margin}"
                ),
            }
        )
    if float(quality.get("evidence_term_coverage", 0.0)) < min_evidence_coverage:
        findings.append(
            {
                "check": "quality-threshold",
                "detail": (
                    f"evidence_term_coverage {quality.get('evidence_term_coverage')} is below "
                    f"min_evidence_coverage {min_evidence_coverage:.4f}"
                ),
            }
        )
    if min_scenarios is not None and scenario_count < min_scenarios:
        findings.append(
            {
                "check": "quality-threshold",
                "detail": f"scenario_count {scenario_count} is below min_scenarios {min_scenarios}",
            }
        )
    support_review = quality.get("support_route_review", {})
    if isinstance(support_review, Mapping):
        missing_support_skills = support_review.get("missing_profiled_support_skills", [])
        if isinstance(missing_support_skills, list) and missing_support_skills:
            findings.append(
                {
                    "check": "support-route-coverage",
                    "detail": (
                        "profiled support skills missing workflow scenarios: "
                        + ", ".join(str(skill) for skill in missing_support_skills)
                    ),
                }
            )
    support_contract_review = quality.get("support_evidence_contract_review", {})
    if isinstance(support_contract_review, Mapping):
        term_gap_count = _int_value(support_contract_review.get("term_gap_count"))
        prompt_gap_count = _int_value(support_contract_review.get("prompt_gap_count"))
        if term_gap_count or prompt_gap_count:
            findings.append(
                {
                    "check": "support-evidence-contract",
                    "detail": (
                        "profiled support scenarios have thin evidence contracts: "
                        f"{term_gap_count} expected_terms gaps, {prompt_gap_count} prompt gaps"
                    ),
                }
            )
    return findings


def compare_baseline(
    base: Path,
    baseline_file: Path | str | None,
    *,
    pass_rate: float,
    scenario_count: int,
    quality: Mapping[str, object],
) -> dict[str, object] | None:
    if baseline_file is None:
        return None

    path = Path(baseline_file)
    if not path.is_absolute():
        path = base / path
    summary: dict[str, object] = {"path": str(path), "loaded": False, "findings": []}
    findings: list[dict[str, str]] = []

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        findings.append({"check": "baseline-contract", "detail": f"Baseline file not found: {path}"})
        summary["findings"] = findings
        return summary
    except json.JSONDecodeError as exc:
        findings.append({"check": "baseline-contract", "detail": f"Baseline file is not valid JSON: {exc.msg}"})
        summary["findings"] = findings
        return summary

    if not isinstance(payload, Mapping):
        findings.append({"check": "baseline-contract", "detail": "Baseline report must be a JSON object"})
        summary["findings"] = findings
        return summary

    baseline_pass_rate = _float_value(payload.get("pass_rate"))
    baseline_scenario_count = _int_value(payload.get("scenario_count"))
    baseline_quality = payload.get("quality", {})
    baseline_average_margin = 0.0
    if isinstance(baseline_quality, Mapping):
        baseline_average_margin = _float_value(baseline_quality.get("average_route_margin"))

    pass_rate_delta = round(pass_rate - baseline_pass_rate, 4)
    scenario_count_delta = scenario_count - baseline_scenario_count
    average_margin = _float_value(quality.get("average_route_margin"))
    average_route_margin_delta = round(average_margin - baseline_average_margin, 4)

    if pass_rate_delta < 0:
        findings.append(
            {
                "check": "baseline-regression",
                "detail": f"pass_rate regressed by {abs(pass_rate_delta):.4f}",
            }
        )
    if scenario_count_delta < 0:
        findings.append(
            {
                "check": "baseline-regression",
                "detail": f"scenario_count dropped by {abs(scenario_count_delta)}",
            }
        )
    if average_route_margin_delta < 0:
        findings.append(
            {
                "check": "baseline-regression",
                "detail": f"average_route_margin regressed by {abs(average_route_margin_delta):.4f}",
            }
        )

    summary.update(
        {
            "loaded": True,
            "pass_rate_delta": pass_rate_delta,
            "scenario_count_delta": scenario_count_delta,
            "average_route_margin_delta": average_route_margin_delta,
            "findings": findings,
        }
    )
    return summary


def count_values(values: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def skill_metadata(registry: Mapping[str, object], skill_name: str, field: str) -> str:
    spec = registry.get(skill_name)
    if spec is None:
        return ""
    value = getattr(spec, field, "")
    return str(value)


def _float_value(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _int_value(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def render_text(report: Mapping[str, object]) -> str:
    lines = [
        "Relay-kit workflow eval",
        f"- project: {report['project_path']}",
        f"- fixture: {report['fixture_path']}",
        f"- scenarios: {report['scenario_count']}",
        f"- passed: {report['passed']}",
        f"- failed: {report['failed']}",
        f"- pass rate: {float(report['pass_rate']):.2f}",
        f"- findings: {report['findings_count']}",
    ]
    quality = report.get("quality", {})
    if isinstance(quality, Mapping):
        lines.extend(
            [
                f"- min route margin: {quality.get('min_route_margin', 0)}",
                f"- avg route margin: {float(quality.get('average_route_margin', 0.0)):.2f}",
                f"- evidence coverage: {float(quality.get('evidence_term_coverage', 0.0)):.2f}",
                f"- weak routes: {quality.get('weak_route_count', 0)}",
            ]
        )
        gaps = quality.get("coverage_gaps", {})
        if isinstance(gaps, Mapping):
            lines.append(f"- missing eval layers: {len(gaps.get('missing_layers', []))}")
    baseline = report.get("baseline")
    if isinstance(baseline, Mapping):
        lines.append(f"- baseline: {'loaded' if baseline.get('loaded') else 'not loaded'}")

    findings = list(report.get("findings", []))
    for result in report.get("results", []):
        if isinstance(result, dict) and not result.get("passed", False):
            for finding in result.get("findings", []):
                if isinstance(finding, dict):
                    findings.append(
                        {
                            "check": str(finding.get("check", "scenario")),
                            "detail": f"{result.get('id', 'unnamed-scenario')}: {finding.get('detail', '')}",
                        }
                    )

    if findings:
        lines.append("")
        lines.append("Top findings:")
        for finding in findings[:20]:
            lines.append(f"- {finding['check']}: {finding['detail']}")
        if len(findings) > 20:
            lines.append(f"- ... and {len(findings) - 20} more")
    return "\n".join(lines)


def write_report(report: Mapping[str, object], output_file: Path | str) -> Path:
    path = Path(output_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(
        args.project_path,
        scenario_fixtures=args.scenario_fixtures,
        baseline_file=args.baseline_file,
        min_pass_rate=args.min_pass_rate,
        min_route_margin=args.min_route_margin,
        min_evidence_coverage=args.min_evidence_coverage,
        min_scenarios=args.min_scenarios,
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


if __name__ == "__main__":
    raise SystemExit(main())
