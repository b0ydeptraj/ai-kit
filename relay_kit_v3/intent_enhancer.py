from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from relay_kit_v3.context_index import context_hits_for_prompt
from relay_kit_v3.registry.skills import ALL_V3_SKILLS
from relay_kit_v3.repo_profile import build_repo_profile
from relay_kit_v3.route_scoring import rank_prompt_routes


SCHEMA_VERSION = "relay-kit.prompt-enhance.v1"


@dataclass(frozen=True)
class IntentHint:
    id: str
    target_skill: str
    markers: tuple[str, ...]
    routing_text: str
    read_first: tuple[str, ...]
    evidence: tuple[str, ...]


INTENT_HINTS: tuple[IntentHint, ...] = (
    IntentHint(
        id="continue-active-work",
        target_skill="cook",
        markers=("tiep tuc", "lam tiep", "build tiep", "continue"),
        routing_text="Use cook for one active request with existing routing and state. Drive the next solid handoff.",
        read_first=(
            ".relay-kit/state/workflow-state.md",
            ".relay-kit/state/handoff-log.md",
            "recent git diff and latest test output",
        ),
        evidence=(
            "active lane and exact next step",
            "latest completed evidence",
            "next command or file change to execute",
        ),
    ),
    IntentHint(
        id="ci-or-failure-debug",
        target_skill="debug-hub",
        markers=("fix ci", "ci fail", "failing ci", "loi ci", "crash", "bug", "loi", "sua"),
        routing_text=(
            "Use debug-hub for a failure or regression. Collect reproduction, logs, affected files, root cause, "
            "and route to fix-hub or developer after the issue is understood."
        ),
        read_first=(
            "failing test, CI log, or reproduction output",
            "related source files found by rg",
            ".relay-kit/state/workflow-state.md",
        ),
        evidence=(
            "fresh reproduction or failing command",
            "root-cause note tied to files",
            "passing verification after the fix",
        ),
    ),
    IntentHint(
        id="review-ai-smell",
        target_skill="review-hub",
        markers=("mui ai", "overclaim", "co on khong", "on khong", "danh gia", "review"),
        routing_text=(
            "Use review-hub for analysis or review. Check artifacts against repo reality, name risks, missing "
            "evidence, overclaims, and route to debug, fix, or plan only when needed."
        ),
        read_first=(
            "files or artifacts named by the user",
            "README and public docs when claims are being reviewed",
            "tests or evidence reports backing the claim",
        ),
        evidence=(
            "file-specific findings",
            "verified facts versus unverified claims",
            "residual risk and recommended next action",
        ),
    ),
    IntentHint(
        id="api-surface-analysis",
        target_skill="api-integration",
        markers=("fastapi", "api client", "http client", "endpoint", "webhook", "request response", "request/response", "transport"),
        routing_text=(
            "Use api-integration when the request is about endpoints, clients, transports, webhooks, or "
            "request/response contracts. Name contract boundaries and related tests before edits."
        ),
        read_first=(
            "API client, endpoint, or transport files",
            "contract tests and request/response fixtures",
            "external service docs or local integration notes",
        ),
        evidence=(
            "request/response contract",
            "error and retry behavior",
            "integration or contract test anchor",
        ),
    ),
    IntentHint(
        id="data-persistence-analysis",
        target_skill="data-persistence",
        markers=("sqlalchemy", "database", "transaction", "schema", "migration", "engine connection"),
        routing_text=(
            "Use data-persistence when schemas, transactions, repositories, caches, query behavior, or engine "
            "boundaries are central. Tie conclusions to storage files and tests."
        ),
        read_first=(
            "schema/model/repository/engine files",
            "migration or transaction tests",
            "cache and persistence configuration",
        ),
        evidence=(
            "transaction or persistence boundary",
            "schema/query evidence",
            "related test anchor",
        ),
    ),
    IntentHint(
        id="policy-security-analysis",
        target_skill="policy-guard",
        markers=("gitleaks", "secret", "security policy", "policy", "permission scope"),
        routing_text=(
            "Use policy-guard when security policy, secret handling, permissions, or high-risk operations are "
            "being reviewed. Treat missing evidence as a blocker."
        ),
        read_first=(
            "policy/config/rule files",
            "security tests or static checks",
            "docs that define allowed and blocked behavior",
        ),
        evidence=(
            "policy rule or permission scope",
            "blocked-risk evidence",
            "test or audit command anchor",
        ),
    ),
    IntentHint(
        id="automation-ops-analysis",
        target_skill="automation-ops",
        markers=("workflow template", "ci workflow", "package jobs", "scheduler", "automation"),
        routing_text=(
            "Use automation-ops when workflow templates, scheduled jobs, queues, webhooks, or operational "
            "runbooks are central. Require dry-run or rollback evidence before enabling automation."
        ),
        read_first=(
            "workflow/job/runbook files",
            "scheduler or queue configuration",
            "dry-run, rollback, and execution-history evidence",
        ),
        evidence=(
            "idempotency and retry behavior",
            "dry-run or rollback evidence",
            "operator-visible execution history",
        ),
    ),
    IntentHint(
        id="architecture-shape-analysis",
        target_skill="project-architecture",
        markers=("class generation", "module boundary", "dependency direction", "architecture map"),
        routing_text=(
            "Use project-architecture when the request is to map current module shape, class generation, "
            "dependency direction, or architectural drift before planning or coding."
        ),
        read_first=(
            "entrypoint and module boundary files",
            "related tests and configuration",
            "architecture or project-context docs if present",
        ),
        evidence=(
            "entrypoint and ownership map",
            "dependency direction",
            "architecture drift or residual risk",
        ),
    ),
    IntentHint(
        id="repo-or-file-analysis",
        target_skill="scout-hub",
        markers=(
            "doc repo",
            "doc thu muc",
            "phan tich file",
            "phan tich repo",
            "read repo",
            "analyze file",
            "without running code",
            "without installing",
            "read-only",
            "test anchors",
            "map architecture",
            "map command",
        ),
        routing_text=(
            "Use scout-hub for unfamiliar repo or file analysis. Inspect entrypoints, structure, ownership, and "
            "route to repo-map, review-hub, or plan-hub with evidence."
        ),
        read_first=(
            "explicit file path or active editor selection",
            "repo tree slice and nearest README/config",
            ".relay-kit/contracts/project-context.md when present",
        ),
        evidence=(
            "entrypoints and ownership map",
            "file references or concrete artifacts inspected",
            "next skill recommendation",
        ),
    ),
    IntentHint(
        id="implementation-request",
        target_skill="developer",
        markers=("implement", "code", "build", "lam di", "sua code"),
        routing_text=(
            "Use developer when the work is implementation-ready. Read relevant files, make a controlled edit, "
            "and collect test evidence before completion."
        ),
        read_first=(
            "active story, tech spec, or current request",
            "files returned by rg for the affected feature",
            "related tests",
        ),
        evidence=(
            "changed files",
            "test command or focused verification",
            "edge case and rollback note",
        ),
    ),
)


DEICTIC_MARKERS = ("cai nay", "file nay", "cho nay", "do", "nay")


def build_prompt_enhancement(
    project_root: Path | str,
    *,
    prompt: str,
    top_limit: int = 5,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    original_prompt = prompt.strip()
    normalized = normalize_text(original_prompt)
    hints = matched_hints(normalized)
    routing_prompt = build_routing_prompt(original_prompt, hints)
    ranked = rank_prompt_routes(routing_prompt, ALL_V3_SKILLS)
    preferred_skill = next((hint.target_skill for hint in hints if hint.target_skill in ALL_V3_SKILLS), "")
    if preferred_skill:
        ranked = promote_route(ranked, preferred_skill)
    top_routes = [
        {"skill": name, "score": score}
        for score, name in ranked[: max(top_limit, 1)]
    ]
    recommended_skill = top_routes[0]["skill"] if top_routes else ""
    top_score = int(top_routes[0]["score"]) if top_routes else 0
    second_score = int(top_routes[1]["score"]) if len(top_routes) > 1 else 0
    route_margin = max(top_score - second_score, 0)
    spec = ALL_V3_SKILLS.get(str(recommended_skill))

    explicit_paths = extract_file_mentions(original_prompt)
    context_index_status, context_hits = context_hits_for_prompt(root, original_prompt, limit=5)
    context_hit_paths = [
        str(item.get("path"))
        for item in context_hits
        if item.get("path")
    ]
    repo_profile = build_repo_profile(root)
    read_first = context_to_read(root, spec, hints, explicit_paths, normalized, context_hit_paths)
    evidence = evidence_required(spec, hints)
    ask_or_act = decide_ask_or_act(
        normalized=normalized,
        explicit_paths=explicit_paths,
        hints=hints,
        top_score=top_score,
        route_margin=route_margin,
        recommended_skill=str(recommended_skill),
    )
    if repo_profile.get("unknown_domain_mode") and ask_or_act == "act":
        ask_or_act = "scout_first"
    missing_context_question = missing_question(ask_or_act, normalized)

    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "project_path": str(root),
        "original_prompt": original_prompt,
        "routing_prompt": routing_prompt,
        "recommended_skill": recommended_skill,
        "top_routes": top_routes,
        "route_margin": route_margin,
        "ask_or_act": ask_or_act,
        "context_index_status": context_index_status,
        "context_hits": context_hits,
        "repo_profile": {
            "dominant_archetype": repo_profile.get("dominant_archetype"),
            "domain_coverage": repo_profile.get("domain_coverage"),
            "unknown_domain_mode": repo_profile.get("unknown_domain_mode"),
            "suggested_competencies": repo_profile.get("suggested_competencies", []),
        },
        "domain_coverage": repo_profile.get("domain_coverage"),
        "unknown_domain_mode": repo_profile.get("unknown_domain_mode"),
        "why": why_lines(hints, str(recommended_skill), top_score, route_margin),
        "read_first": read_first,
        "evidence_required": evidence,
        "enhanced_prompt": render_enhanced_prompt(
            original_prompt=original_prompt,
            recommended_skill=str(recommended_skill),
            ask_or_act=ask_or_act,
            domain_coverage=str(repo_profile.get("domain_coverage")),
            suggested_competencies=repo_profile.get("suggested_competencies", []),
            read_first=read_first,
            evidence_required=evidence,
            missing_context_question=missing_context_question,
        ),
    }
    if missing_context_question:
        report["missing_context_question"] = missing_context_question
    return report


def normalize_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    ascii_text = decomposed.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_text.lower()).strip()


def matched_hints(normalized_prompt: str) -> list[IntentHint]:
    hints = [
        hint
        for hint in INTENT_HINTS
        if any(marker in normalized_prompt for marker in hint.markers)
        and not (hint.target_skill == "developer" and implementation_marker_is_negated(normalized_prompt))
    ]
    if not hints and normalized_prompt:
        hints.append(INTENT_HINTS[3])
    return hints


def implementation_marker_is_negated(normalized_prompt: str) -> bool:
    return any(
        marker in normalized_prompt
        for marker in (
            "without running code",
            "without code",
            "no code",
            "read-only",
            "khong chay code",
            "khong code",
        )
    )


def build_routing_prompt(original_prompt: str, hints: Sequence[IntentHint]) -> str:
    hint_text = "\n".join(hint.routing_text for hint in hints)
    return "\n".join(part for part in [original_prompt, hint_text] if part).strip()


def promote_route(ranked: Sequence[tuple[int, str]], preferred_skill: str) -> list[tuple[int, str]]:
    if not ranked:
        return [(1, preferred_skill)]
    top_score = ranked[0][0]
    promoted = [(max(top_score + 5, score), name) for score, name in ranked if name == preferred_skill]
    rest = [(score, name) for score, name in ranked if name != preferred_skill]
    return [*(promoted or [(top_score + 5, preferred_skill)]), *rest]


def extract_file_mentions(prompt: str) -> list[str]:
    patterns = [
        r"[A-Za-z]:[\\/][^\s:]+",
        r"(?:[\w.-]+[\\/])+[\w.-]+",
        r"[\w.-]+\.(?:py|ts|tsx|js|jsx|go|rs|md|json|yml|yaml|toml|css|html)",
    ]
    mentions: list[str] = []
    for pattern in patterns:
        for match in re.findall(pattern, prompt):
            if match not in mentions:
                mentions.append(match)
    return mentions


def context_to_read(
    root: Path,
    spec: object | None,
    hints: Sequence[IntentHint],
    explicit_paths: Sequence[str],
    normalized_prompt: str,
    context_hit_paths: Sequence[str] = (),
) -> list[str]:
    items: list[str] = []
    for path in explicit_paths:
        items.append(path)
    for path in context_hit_paths:
        items.append(path)
    for hint in hints:
        items.extend(hint.read_first)
    if spec is not None:
        items.extend(str(item) for item in getattr(spec, "inputs", [])[:4])
    if any(marker in normalized_prompt for marker in DEICTIC_MARKERS) and not explicit_paths:
        items.insert(0, "the active file, selected text, PR, or artifact the user means by 'this'")
    if (root / ".relay-kit" / "state" / "workflow-state.md").exists():
        items.append(".relay-kit/state/workflow-state.md")
    return unique(items)[:8]


def evidence_required(spec: object | None, hints: Sequence[IntentHint]) -> list[str]:
    items: list[str] = []
    for hint in hints:
        items.extend(hint.evidence)
    if spec is not None:
        items.extend(str(item) for item in getattr(spec, "outputs", [])[:3])
    items.append("clear note of what was verified and what remains unverified")
    return unique(items)[:8]


def decide_ask_or_act(
    *,
    normalized: str,
    explicit_paths: Sequence[str],
    hints: Sequence[IntentHint],
    top_score: int,
    route_margin: int,
    recommended_skill: str,
) -> str:
    if not normalized or len(normalized.split()) <= 1:
        return "ask_one_question"
    if any(marker in normalized for marker in DEICTIC_MARKERS) and not explicit_paths:
        return "ask_one_question"
    if top_score <= 0 or (route_margin <= 1 and not hints):
        return "ask_one_question"
    if recommended_skill in {"scout-hub", "repo-map"}:
        return "scout_first"
    if any(hint.id == "ci-or-failure-debug" for hint in hints) and not explicit_paths:
        return "scout_first"
    return "act"


def missing_question(ask_or_act: str, normalized: str) -> str | None:
    if ask_or_act != "ask_one_question":
        return None
    if "file" in normalized:
        return "Which file or selected code should be analyzed?"
    if any(marker in normalized for marker in ("cai nay", "cho nay", "do", "nay")):
        return "Which file, PR, screen, or artifact does 'this' refer to?"
    return "What exact file, error, or workflow should Relay-kit use as the anchor?"


def why_lines(hints: Sequence[IntentHint], recommended_skill: str, top_score: int, route_margin: int) -> list[str]:
    lines = [f"Route scorer selected {recommended_skill} with score {top_score} and margin {route_margin}."]
    lines.extend(f"Matched prompt shape: {hint.id}." for hint in hints)
    lines.append("This is prompt enhancement over existing skill contracts, not a semantic context engine or expert guarantee.")
    return lines


def render_enhanced_prompt(
    *,
    original_prompt: str,
    recommended_skill: str,
    ask_or_act: str,
    domain_coverage: str,
    suggested_competencies: Sequence[str],
    read_first: Sequence[str],
    evidence_required: Sequence[str],
    missing_context_question: str | None,
) -> str:
    lines = [
        f"User request: {original_prompt}",
        f"Recommended skill: {recommended_skill}",
        f"Decision: {ask_or_act}",
        f"Domain coverage: {domain_coverage}",
        "",
        "Use the skill to turn the short request into a file-aware workflow based on competency evidence.",
    ]
    if suggested_competencies:
        lines.extend(["Competency hints:", *[f"- {item}" for item in suggested_competencies[:6]], ""])
    lines.extend(
        [
            "Read first:",
            *[f"- {item}" for item in read_first],
            "",
            "Evidence required before answering or claiming done:",
            *[f"- {item}" for item in evidence_required],
        ]
    )
    if missing_context_question:
        lines.extend(["", f"Ask this one clarification first: {missing_context_question}"])
    return "\n".join(lines).strip()


def render_prompt_enhancement(report: Mapping[str, Any]) -> str:
    lines = [
        "Relay-kit prompt enhance",
        f"- Recommended skill: {report.get('recommended_skill')}",
        f"- Ask or act: {report.get('ask_or_act')}",
        f"- Context index: {report.get('context_index_status')}",
        f"- Domain coverage: {report.get('domain_coverage')}",
        f"- Route margin: {report.get('route_margin')}",
        "- Why:",
    ]
    lines.extend(f"  - {item}" for item in report.get("why", []))
    if report.get("context_hits"):
        lines.append("- Context graph hits:")
        for hit in report.get("context_hits", [])[:5]:
            lines.append(f"  - {hit.get('path')} [{hit.get('kind')} score={hit.get('score')}]")
    lines.append("- Enhanced prompt:")
    lines.extend(f"  {line}" if line else "" for line in str(report.get("enhanced_prompt", "")).splitlines())
    lines.append("- Read first:")
    lines.extend(f"  - {item}" for item in report.get("read_first", []))
    lines.append("- Evidence required:")
    lines.extend(f"  - {item}" for item in report.get("evidence_required", []))
    return "\n".join(lines)


def write_prompt_enhancement(
    project_root: Path | str,
    report: Mapping[str, Any],
    output_file: Path | str,
) -> Path:
    root = Path(project_root).resolve()
    target = Path(output_file)
    if not target.is_absolute():
        target = root / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return target


def unique(items: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        value = str(item).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
