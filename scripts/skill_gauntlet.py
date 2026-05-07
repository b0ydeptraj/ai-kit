#!/usr/bin/env python3
"""Behavior regression checks for Relay-kit runtime skills."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from relay_kit_v3.registry.skills import ALL_V3_SKILLS


RUNTIME_ROOTS = [".claude/skills", ".agent/skills", ".codex/skills"]
REQUIRED_HEADERS = [
    "# Mission",
    "## Role",
    "## Layer",
    "## Inputs",
    "## Outputs",
    "## Reference skills and rules",
    "## Likely next step",
]
DEFAULT_SCENARIO_FIXTURE = Path("relay_kit_v3") / "eval_fixtures" / "workflow_scenarios.json"
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "before",
    "by",
    "for",
    "from",
    "has",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "this",
    "to",
    "with",
}
OPTIONAL_ALIAS_CONTRACTS = {
    "prove-it": [
        "canonical skill: `evidence-before-completion`",
        "claim-to-evidence",
        "not a readiness verdict",
        "does not write `qa-report.md`",
    ],
    "ready-check": [
        "quality gate: `qa-governor`",
        "go / no-go readiness",
        "not a claim-to-evidence pass",
    ],
}
REQUIRED_TOOL_PROFILE_SKILLS = {
    "accessibility-review",
    "api-integration",
    "browser-inspector",
    "data-persistence",
    "dependency-management",
    "developer",
    "execution-loop",
    "media-tooling",
    "migration-guard",
    "multimodal-evidence",
    "policy-guard",
    "release-readiness",
    "root-cause-debugging",
    "runtime-doctor",
    "skill-evolution",
    "skill-gauntlet",
    "test-first-development",
}
VALID_TOOL_NAMES = {"Read", "Write", "Edit", "Grep", "Glob", "Bash"}


@dataclass(frozen=True)
class Finding:
    path: str
    check: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run SKILL.md behavior regression checks across runtime surfaces.",
    )
    parser.add_argument("project_path", nargs="?", default=".", help="Target project root")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero exit code when any finding is detected",
    )
    parser.add_argument(
        "--semantic",
        action="store_true",
        help="Also check registry parity, next-step references, and duplicate trigger descriptions.",
    )
    parser.add_argument(
        "--scenario-fixtures",
        default=str(DEFAULT_SCENARIO_FIXTURE),
        help="JSON scenario fixture file used by --semantic checks.",
    )
    return parser.parse_args()


def check_skill_file(path: Path, base: Path) -> List[Finding]:
    findings: List[Finding] = []
    content = path.read_text(encoding="utf-8")
    rel_path = path.relative_to(base).as_posix()
    frontmatter = parse_frontmatter(content)
    if frontmatter is None:
        findings.append(Finding(rel_path, "frontmatter", "Missing or malformed frontmatter"))
        return findings

    name = frontmatter.get("name", "").strip()
    description = frontmatter.get("description", "").strip()
    if not name:
        findings.append(Finding(rel_path, "frontmatter-name", "Missing name in frontmatter"))
    if not description:
        findings.append(Finding(rel_path, "frontmatter-description", "Missing description in frontmatter"))
    expected_name = path.parent.name
    if name != expected_name:
        findings.append(
            Finding(
                rel_path,
                "name-match",
                f"Frontmatter name {name!r} does not match folder name {expected_name!r}",
            )
        )
    if not description.startswith("Use when "):
        findings.append(
            Finding(
                rel_path,
                "trigger-description",
                "Description must start with 'Use when '",
            )
        )

    for header in REQUIRED_HEADERS:
        if header not in content:
            findings.append(Finding(rel_path, "required-section", f"Missing section: {header}"))

    if "- TBD" in content or "TBD" in content:
        findings.append(Finding(rel_path, "placeholder", "Contains unresolved placeholder text"))

    return findings


def parse_frontmatter(content: str) -> Dict[str, str] | None:
    lines = content.splitlines()
    if not lines:
        return None
    first = lines[0].lstrip("\ufeff").strip()
    if first != "---":
        return None
    end_index = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_index = idx
            break
    if end_index is None:
        return None

    frontmatter_lines = lines[1:end_index]
    data: Dict[str, str] = {}
    i = 0
    while i < len(frontmatter_lines):
        raw = frontmatter_lines[i]
        if ":" not in raw:
            i += 1
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value in {">", ">-", "|", "|-"}:
            i += 1
            block: List[str] = []
            while i < len(frontmatter_lines):
                next_line = frontmatter_lines[i]
                if not next_line.startswith((" ", "\t")):
                    break
                block.append(next_line.strip())
                i += 1
            data[key] = " ".join(block).strip()
            continue
        data[key] = value
        i += 1
    return data


def parse_inline_list(value: str) -> List[str]:
    value = value.strip()
    if not value:
        return []
    if not (value.startswith("[") and value.endswith("]")):
        return []
    inner = value[1:-1].strip()
    if not inner:
        return []
    items: List[str] = []
    for item in inner.split(","):
        stripped = item.strip()
        if len(stripped) >= 2 and stripped[0] == stripped[-1] == '"':
            stripped = stripped[1:-1]
        items.append(stripped)
    return items


def section_bullets(content: str, section_name: str) -> List[str]:
    lines = content.splitlines()
    header = f"## {section_name}"
    start_index = None
    for idx, line in enumerate(lines):
        if line.strip() == header:
            start_index = idx + 1
            break
    if start_index is None:
        return []

    bullets: List[str] = []
    for line in lines[start_index:]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
    return bullets


def check_expected_bullets(
    findings: List[Finding],
    rel_path: str,
    check: str,
    section_name: str,
    actual: Sequence[str],
    expected: Sequence[str],
) -> None:
    actual_list = list(actual)
    expected_list = list(expected)
    if actual_list != expected_list:
        findings.append(
            Finding(
                rel_path,
                check,
                f"{section_name} drift: expected={expected_list!r} actual={actual_list!r}",
            )
        )


def check_semantic_skill_file(path: Path, base: Path, spec, known_skill_names: set[str]) -> List[Finding]:
    findings: List[Finding] = []
    content = path.read_text(encoding="utf-8")
    rel_path = path.relative_to(base).as_posix()
    frontmatter = parse_frontmatter(content)
    if frontmatter is None:
        return [Finding(rel_path, "frontmatter", "Missing or malformed frontmatter")]

    description = frontmatter.get("description", "").strip()
    if description != spec.description:
        findings.append(
            Finding(
                rel_path,
                "registry-description-drift",
                f"Expected registry description {spec.description!r}, found {description!r}",
            )
        )

    check_expected_bullets(findings, rel_path, "registry-role-drift", "Role", section_bullets(content, "Role"), [spec.role])
    check_expected_bullets(findings, rel_path, "registry-layer-drift", "Layer", section_bullets(content, "Layer"), [spec.layer])
    check_expected_bullets(findings, rel_path, "registry-inputs-drift", "Inputs", section_bullets(content, "Inputs"), spec.inputs)
    check_expected_bullets(findings, rel_path, "registry-outputs-drift", "Outputs", section_bullets(content, "Outputs"), spec.outputs)

    next_steps = section_bullets(content, "Likely next step")
    check_expected_bullets(findings, rel_path, "registry-next-steps-drift", "Likely next step", next_steps, spec.next_steps)
    for step in next_steps:
        if step not in known_skill_names:
            findings.append(Finding(rel_path, "unknown-next-step", f"Unknown next-step skill: {step}"))

    if not section_bullets(content, "Inputs"):
        findings.append(Finding(rel_path, "empty-input-contract", "Inputs section has no bullet contract"))
    if not section_bullets(content, "Outputs"):
        findings.append(Finding(rel_path, "empty-output-contract", "Outputs section has no bullet contract"))

    return findings


def collect_tool_profile_findings(
    base: Path,
    skill_files: Sequence[Path],
    registry: Mapping[str, object],
) -> List[Finding]:
    findings: List[Finding] = []
    seen_skill_names: set[str] = set()

    for path in skill_files:
        if not path.exists():
            continue
        skill_name = path.parent.name
        spec = registry.get(skill_name)
        if spec is None:
            continue
        seen_skill_names.add(skill_name)
        rel_path = path.relative_to(base).as_posix()
        content = path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(content)
        if frontmatter is None:
            continue

        raw_profile = frontmatter.get("allowed-tools", "").strip()
        actual_profile = parse_inline_list(raw_profile)
        expected_profile = list(getattr(spec, "allowed_tools", None) or [])

        if skill_name in REQUIRED_TOOL_PROFILE_SKILLS and not raw_profile:
            findings.append(
                Finding(
                    rel_path,
                    "missing-tool-profile",
                    "Profiled risk-sensitive skill must declare allowed-tools frontmatter",
                )
            )
        if raw_profile and not actual_profile:
            findings.append(
                Finding(
                    rel_path,
                    "invalid-tool-profile",
                    "allowed-tools must be an inline YAML list",
                )
            )
        invalid_tools = [tool for tool in actual_profile if tool not in VALID_TOOL_NAMES]
        if invalid_tools:
            findings.append(
                Finding(
                    rel_path,
                    "invalid-tool-profile",
                    f"Unknown allowed tool names: {', '.join(invalid_tools)}",
                )
            )
        if expected_profile and actual_profile and actual_profile != expected_profile:
            findings.append(
                Finding(
                    rel_path,
                    "tool-profile-drift",
                    f"allowed-tools drift: expected={expected_profile!r} actual={actual_profile!r}",
                )
            )

    for skill_name in sorted(REQUIRED_TOOL_PROFILE_SKILLS & set(registry)):
        spec = registry[skill_name]
        if not list(getattr(spec, "allowed_tools", None) or []):
            findings.append(
                Finding(
                    f"registry:{skill_name}",
                    "missing-registry-tool-profile",
                    "Profiled risk-sensitive skill registry spec must define allowed_tools",
                )
            )
        elif skill_name not in seen_skill_names:
            findings.append(
                Finding(
                    f"registry:{skill_name}",
                    "missing-tool-profile-surface",
                    "Profiled risk-sensitive skill was not present in generated runtime surfaces",
                )
            )

    return findings


def collect_semantic_findings(base: Path, skill_files: Sequence[Path]) -> List[Finding]:
    findings: List[Finding] = []
    known_skill_names = set(ALL_V3_SKILLS)
    description_paths: Dict[tuple[str, str], List[str]] = {}

    for path in skill_files:
        if not path.exists():
            continue
        skill_name = path.parent.name
        spec = ALL_V3_SKILLS.get(skill_name)
        if spec is None:
            continue

        content = path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(content)
        description = (frontmatter or {}).get("description", "").strip()
        if description:
            rel_path = path.relative_to(base).as_posix()
            parts = rel_path.split("/")
            adapter = "/".join(parts[:2]) if len(parts) >= 2 else "unknown"
            description_paths.setdefault((adapter, description), []).append(rel_path)

        findings.extend(check_semantic_skill_file(path, base, spec, known_skill_names))

    for (_adapter, description), paths in sorted(description_paths.items()):
        if len(paths) > 1:
            findings.append(
                Finding(
                    paths[0],
                    "duplicate-trigger-description",
                    f"Description is shared by {len(paths)} skills: {', '.join(paths)}",
                )
            )

    return findings


def collect_optional_alias_findings(base: Path) -> List[Finding]:
    findings: List[Finding] = []
    for root in RUNTIME_ROOTS:
        for alias_name, required_terms in OPTIONAL_ALIAS_CONTRACTS.items():
            path = base / root / alias_name / "SKILL.md"
            if not path.exists():
                continue
            rel_path = path.relative_to(base).as_posix()
            content = path.read_text(encoding="utf-8")
            frontmatter = parse_frontmatter(content)
            if frontmatter is None:
                findings.append(Finding(rel_path, "optional-alias-contract", "Missing or malformed alias frontmatter"))
                continue
            description = frontmatter.get("description", "").strip()
            if not description.startswith("Use when "):
                findings.append(
                    Finding(rel_path, "optional-alias-contract", "Alias description must start with 'Use when '")
                )
            for term in required_terms:
                if term not in content:
                    findings.append(
                        Finding(rel_path, "optional-alias-contract", f"Missing required alias contract term: {term}")
                    )
    return findings


def tokenize(text: str) -> set[str]:
    tokens = {
        token.lower()
        for token in re.findall(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", text)
        if len(token) > 2
    }
    expanded: set[str] = set()
    for token in tokens:
        expanded.add(token)
        if "-" in token:
            expanded.update(part for part in token.split("-") if len(part) > 2)
    return {token for token in expanded if token not in STOPWORDS}


def skill_search_text(spec) -> str:
    return "\n".join(
        [
            spec.name.replace("-", " "),
            spec.description,
            spec.role,
            spec.layer,
            *spec.inputs,
            *spec.outputs,
            *spec.references,
            *spec.next_steps,
            spec.body,
        ]
    )


def skill_route_text(spec) -> str:
    return "\n".join(
        [
            spec.name.replace("-", " "),
            spec.description,
            spec.role,
            spec.layer,
            *spec.inputs,
            *spec.outputs,
            *spec.next_steps,
        ]
    )


def score_prompt_against_skill(prompt: str, spec) -> int:
    prompt_tokens = tokenize(prompt)
    if not prompt_tokens:
        return 0
    spec_tokens = tokenize(skill_route_text(spec))
    score = len(prompt_tokens & spec_tokens)

    prompt_lower = prompt.lower()
    for phrase_source, bonus in ((spec.name, 25), (spec.role, 20), (spec.layer, 10)):
        phrase = str(phrase_source).replace("-", " ").lower()
        if str(phrase_source).lower() in prompt_lower or phrase in prompt_lower:
            score += bonus

    description_tokens = tokenize(spec.description)
    score += len(prompt_tokens & description_tokens) * 2
    return score


def rank_prompt_routes(prompt: str, registry: Mapping[str, object]) -> List[tuple[int, str]]:
    ranked = [(score_prompt_against_skill(prompt, spec), name) for name, spec in registry.items()]
    return sorted(ranked, key=lambda item: (-item[0], item[1]))


def resolve_scenario_fixture_path(base: Path, fixture_path: Path) -> Path | None:
    if fixture_path.is_absolute():
        candidates = [fixture_path]
    else:
        candidates = [base / fixture_path, REPO_ROOT / fixture_path]

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def load_scenario_fixtures(base: Path, fixture_path: Path) -> list[dict[str, object]]:
    path = resolve_scenario_fixture_path(base, fixture_path)
    if path is None:
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Scenario fixture must contain a list: {path}")
    scenarios: list[dict[str, object]] = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError(f"Scenario fixture item must be an object: {path}")
        scenarios.append(item)
    return scenarios


def rendered_skill_contract(spec) -> str:
    return skill_search_text(spec).lower()


def check_scenario_fixture(scenario: Mapping[str, object], registry: Mapping[str, object]) -> List[Finding]:
    findings: List[Finding] = []
    scenario_id = str(scenario.get("id", "")).strip() or "unnamed-scenario"
    prompt = str(scenario.get("prompt", "")).strip()
    expected_skill = str(scenario.get("expected_skill", "")).strip()

    if not prompt:
        return [Finding(f"scenario:{scenario_id}", "scenario-contract", "Missing prompt")]
    if not expected_skill:
        return [Finding(f"scenario:{scenario_id}", "scenario-contract", "Missing expected_skill")]
    if expected_skill not in registry:
        return [Finding(f"scenario:{scenario_id}", "scenario-contract", f"Unknown expected_skill: {expected_skill}")]

    ranked = rank_prompt_routes(prompt, registry)
    top_score, predicted = ranked[0] if ranked else (0, "")
    if predicted != expected_skill:
        top = ", ".join(f"{name}:{score}" for score, name in ranked[:5])
        findings.append(
            Finding(
                f"scenario:{scenario_id}",
                "scenario-route",
                f"Expected {expected_skill}, predicted {predicted or '-'} with score {top_score}. Top routes: {top}",
            )
        )

    expected_terms = scenario.get("expected_terms", [])
    if not isinstance(expected_terms, list):
        findings.append(Finding(f"scenario:{scenario_id}", "scenario-contract", "expected_terms must be a list"))
        return findings

    contract = rendered_skill_contract(registry[expected_skill])
    missing_terms = [
        str(term)
        for term in expected_terms
        if str(term).strip() and str(term).lower() not in contract
    ]
    if missing_terms:
        findings.append(
            Finding(
                f"scenario:{scenario_id}",
                "scenario-evidence-contract",
                f"Expected skill {expected_skill} is missing scenario terms: {', '.join(missing_terms)}",
            )
        )

    return findings


def collect_scenario_findings(
    base: Path,
    registry: Mapping[str, object],
    fixture_path: Path | None = None,
) -> tuple[List[Finding], int]:
    fixture_path = fixture_path or DEFAULT_SCENARIO_FIXTURE
    scenarios = load_scenario_fixtures(base, fixture_path)
    findings: List[Finding] = []
    for scenario in scenarios:
        findings.extend(check_scenario_fixture(scenario, registry))
    return findings, len(scenarios)


def collect_skills(base: Path) -> List[Path]:
    paths: List[Path] = []
    required_names = sorted(ALL_V3_SKILLS.keys())
    for root in RUNTIME_ROOTS:
        skill_root = base / root
        if not skill_root.exists():
            continue
        for name in required_names:
            path = skill_root / name / "SKILL.md"
            if path.exists():
                paths.append(path)
            else:
                missing_path = skill_root / name / "SKILL.md"
                paths.append(missing_path)
    return paths


def report_payload(findings: List[Finding], checked_files: int, semantic: bool, scenario_count: int) -> Dict[str, object]:
    return {
        "checked_files": checked_files,
        "semantic": semantic,
        "scenario_fixtures": scenario_count,
        "findings_count": len(findings),
        "findings": [
            {
                "path": item.path,
                "check": item.check,
                "detail": item.detail,
            }
            for item in findings
        ],
    }


def render_text(findings: List[Finding], checked_files: int, semantic: bool, scenario_count: int) -> str:
    lines = [
        f"Checked {checked_files} SKILL.md files.",
        f"Semantic checks: {'on' if semantic else 'off'}",
        f"Scenario fixtures: {scenario_count}",
        f"Findings: {len(findings)}",
    ]
    if findings:
        lines.append("")
        lines.append("Top findings:")
        for item in findings[:20]:
            lines.append(f"- {item.path} [{item.check}] {item.detail}")
        if len(findings) > 20:
            lines.append(f"- ... and {len(findings) - 20} more")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    base = Path(args.project_path).resolve()
    skill_files = collect_skills(base)
    findings: List[Finding] = []
    for path in skill_files:
        if not path.exists():
            findings.append(
                Finding(
                    path.relative_to(base).as_posix(),
                    "missing-skill",
                    "Expected runtime skill file is missing",
                )
            )
            continue
        findings.extend(check_skill_file(path, base))
    if args.semantic:
        findings.extend(collect_semantic_findings(base, skill_files))
        findings.extend(collect_tool_profile_findings(base, skill_files, ALL_V3_SKILLS))
        findings.extend(collect_optional_alias_findings(base))
        scenario_findings, scenario_count = collect_scenario_findings(
            base,
            ALL_V3_SKILLS,
            Path(args.scenario_fixtures),
        )
        findings.extend(scenario_findings)
    else:
        scenario_count = 0

    payload = report_payload(
        findings,
        checked_files=len(skill_files),
        semantic=args.semantic,
        scenario_count=scenario_count,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print(render_text(findings, checked_files=len(skill_files), semantic=args.semantic, scenario_count=scenario_count))

    if args.strict and findings:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
