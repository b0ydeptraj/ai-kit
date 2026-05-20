from __future__ import annotations

from pathlib import Path

from relay_kit_v3.registry.skills import ALL_V3_SKILLS, render_skill


ROOT = Path(__file__).resolve().parents[1]
RESOURCE_ROOT = ROOT / "relay_kit_v3" / "skill_resources"
BACKEND_REALISM_SKILLS = {
    "dependency-management": [
        "dependency drift",
        "lockfile",
        "transitive dependency",
        "rollback pin",
        "supply-chain",
    ],
    "go-service-engineering": [
        "handler boundary",
        "service boundary",
        "transaction boundary",
        "context cancellation",
        "httptest",
        "migration rollback",
    ],
    "api-integration": [
        "request id",
        "timeout budget",
        "429",
        "idempotency",
        "redacted",
    ],
    "data-persistence": [
        "transaction boundary",
        "cache invalidation",
        "backfill",
        "rollback",
        "isolation",
    ],
    "developer": [
        "failing reproduction",
        "smallest diff",
        "rollback",
        "edge case",
        "test evidence",
    ],
    "testing-patterns": [
        "fixture",
        "factory",
        "mock",
        "integration boundary",
        "flake",
    ],
    "repo-map": [
        "entrypoint",
        "dependency direction",
        "nearby test",
        "ownership",
        "handoff",
    ],
    "browser-inspector": [
        "console",
        "network",
        "dom",
        "screenshot",
        "reproduction trace",
    ],
    "project-architecture": [
        "entrypoint",
        "call graph",
        "ownership",
        "boundary table",
        "hotspot",
    ],
    "mmo-http-api-automation": [
        "request id",
        "429",
        "idempotency key",
        "replay",
        "redacted",
    ],
    "mmo-cloud-operations-automation": [
        "queue depth",
        "dead-letter",
        "idempotency key",
        "cost ceiling",
        "scale-down",
    ],
}

FORBIDDEN_BACKEND_SMELL_PHRASES = [
    "production-grade",
    "best practices",
    "robust",
    "scalable",
    "high reliability",
    "measurable quality",
    "quality constraints",
    "full operational traceability",
]


def _combined_skill_text(skill_name: str) -> str:
    root = RESOURCE_ROOT / skill_name
    resource_paths = [
        root / "competencies" / f"{skill_name}-competencies.json",
        root / "references" / f"{skill_name}-operator-contract.md",
        root / "examples" / f"{skill_name}-good-output.md",
        root / "evals" / f"{skill_name}-cases.json",
    ]
    parts = [render_skill(ALL_V3_SKILLS[skill_name])]
    for path in resource_paths:
        if path.exists():
            parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts).lower()


def test_backend_relevant_skills_use_concrete_operator_language() -> None:
    missing_by_skill: dict[str, list[str]] = {}
    for skill_name, required_terms in BACKEND_REALISM_SKILLS.items():
        rendered = _combined_skill_text(skill_name)
        missing = [term for term in required_terms if term.lower() not in rendered]
        if missing:
            missing_by_skill[skill_name] = missing

    assert missing_by_skill == {}


def test_backend_relevant_skills_avoid_generic_ai_smell_phrases() -> None:
    offenders: dict[str, list[str]] = {}
    for skill_name in BACKEND_REALISM_SKILLS:
        rendered = _combined_skill_text(skill_name)
        phrases = [phrase for phrase in FORBIDDEN_BACKEND_SMELL_PHRASES if phrase in rendered]
        if phrases:
            offenders[skill_name] = phrases

    assert offenders == {}
