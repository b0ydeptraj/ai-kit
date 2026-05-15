from __future__ import annotations

from relay_kit_v3.registry.skills import ALL_V3_SKILLS, render_skill


BACKEND_REALISM_SKILLS = {
    "go-service-engineering": [
        "handler boundary",
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


def test_backend_relevant_skills_use_concrete_operator_language() -> None:
    missing_by_skill: dict[str, list[str]] = {}
    for skill_name, required_terms in BACKEND_REALISM_SKILLS.items():
        rendered = render_skill(ALL_V3_SKILLS[skill_name]).lower()
        missing = [term for term in required_terms if term.lower() not in rendered]
        if missing:
            missing_by_skill[skill_name] = missing

    assert missing_by_skill == {}


def test_backend_relevant_skills_avoid_generic_ai_smell_phrases() -> None:
    offenders: dict[str, list[str]] = {}
    for skill_name in BACKEND_REALISM_SKILLS:
        rendered = render_skill(ALL_V3_SKILLS[skill_name]).lower()
        phrases = [phrase for phrase in FORBIDDEN_BACKEND_SMELL_PHRASES if phrase in rendered]
        if phrases:
            offenders[skill_name] = phrases

    assert offenders == {}
