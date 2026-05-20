from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3.competency_battle import build_competency_battle
from relay_kit_v3.competency_catalog import (
    PROFILE_SCHEMA_VERSION,
    build_competency_catalog,
    category_for_skill,
    competency_profile_path,
)
from relay_kit_v3.registry.skills import ALL_V3_SKILLS


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_HIGH_RISK_CATEGORIES = {
    "architect": "implementation",
    "browser-inspector": "browser-inspector",
    "bootstrap": "context-continuity",
    "cook": "context-continuity",
    "debug-hub": "debugging",
    "dependency-management": "dependency-management",
    "fix-hub": "implementation",
    "go-service-engineering": "go-service-engineering",
    "mmo-account-operations": "mmo-safe-ops",
    "mmo-browser-fleet-automation": "mmo-safe-ops",
    "mmo-cloud-operations-automation": "mmo-safe-ops",
    "mmo-http-api-automation": "mmo-safe-ops",
    "mmo-lowcode-automation": "mmo-safe-ops",
    "mmo-mobile-app-automation": "mmo-safe-ops",
    "mmo-reup-automation": "mmo-safe-ops",
    "mmo-social-marketing-automation": "mmo-safe-ops",
    "plan-hub": "research-product",
    "repo-map": "repo-map",
    "review-hub": "debugging",
    "scout-hub": "implementation",
    "team": "routing-orchestration",
    "test-hub": "debugging",
    "testing-patterns": "testing-patterns",
    "workflow-router": "routing-orchestration",
}
REQUIRED_DEDICATED_COMPETENCIES = {
    "dependency-management": {
        "dependency-management.dependency-drift",
        "dependency-management.source-of-truth",
        "dependency-management.upgrade-risk",
        "dependency-management.supply-chain-boundary",
        "dependency-management.rollback-pin-strategy",
    },
    "go-service-engineering": {
        "go-service-engineering.handler-service-boundary",
        "go-service-engineering.context-cancellation",
        "go-service-engineering.middleware-job-ownership",
        "go-service-engineering.transaction-cache-boundary",
        "go-service-engineering.httptest-integration-evidence",
    },
    "testing-patterns": {
        "testing-patterns.fixture-factory-strategy",
        "testing-patterns.mock-integration-boundary",
        "testing-patterns.regression-anchor",
        "testing-patterns.flake-control",
        "testing-patterns.risk-coverage-map",
    },
    "repo-map": {
        "repo-map.entrypoint-map",
        "repo-map.ownership-boundary",
        "repo-map.dependency-direction",
        "repo-map.test-doc-adjacency",
        "repo-map.scout-handoff",
    },
    "browser-inspector": {
        "browser-inspector.console-network-evidence",
        "browser-inspector.dom-state-trace",
        "browser-inspector.screenshot-video-artifact",
        "browser-inspector.browser-state-isolation",
        "browser-inspector.runtime-handoff",
    },
}


def test_competency_catalog_has_profiles_for_all_skills() -> None:
    catalog = build_competency_catalog()

    assert catalog["schema_version"] == "relay-kit.competency-catalog.v1"
    assert catalog["status"] == "pass"
    assert catalog["skill_count"] == len(ALL_V3_SKILLS)
    for skill_name in ALL_V3_SKILLS:
        path = competency_profile_path(skill_name)
        assert path.exists(), skill_name
        profile = json.loads(path.read_text(encoding="utf-8"))
        assert profile["schema_version"] == PROFILE_SCHEMA_VERSION
        assert len(profile["core_competencies"]) >= 5
        assert len(profile["failure_traps"]) >= 2
        assert profile["unknown_domain_policy"] == "scout_first_without_expert_claim"


def test_competency_battle_core_scores_skill() -> None:
    report = build_competency_battle(ROOT, skill="api-integration", suite="core")
    skill = report["skills"][0]

    assert report["schema_version"] == "relay-kit.competency-battle.v1"
    assert report["status"] == "pass"
    assert skill["skill"] == "api-integration"
    assert skill["claim_status"] == "competency-covered"
    assert skill["coverage_score"] == 1.0
    assert "api-integration.client-endpoint-contract" in skill["covered_competencies"]


def test_high_risk_skills_keep_expected_competency_category() -> None:
    wrong_categories: dict[str, dict[str, str]] = {}
    for skill_name, expected_category in EXPECTED_HIGH_RISK_CATEGORIES.items():
        path = competency_profile_path(skill_name)
        profile = json.loads(path.read_text(encoding="utf-8"))
        actual_category = category_for_skill(skill_name)
        profile_category = str(profile["category"])
        if actual_category != expected_category or profile_category != expected_category:
            wrong_categories[skill_name] = {
                "expected": expected_category,
                "actual": actual_category,
                "profile": profile_category,
            }

    assert wrong_categories == {}


def test_dedicated_competency_skills_have_required_competency_ids() -> None:
    missing_by_skill: dict[str, list[str]] = {}
    for skill_name, required_ids in REQUIRED_DEDICATED_COMPETENCIES.items():
        profile = json.loads(competency_profile_path(skill_name).read_text(encoding="utf-8"))
        actual_ids = {str(item["id"]) for item in profile["core_competencies"]}
        missing = sorted(required_ids - actual_ids)
        if missing:
            missing_by_skill[skill_name] = missing

    assert missing_by_skill == {}


def test_public_cli_competency_battle_json(capsys, tmp_path: Path) -> None:
    code = relay_kit_public_cli.main(
        ["eval", "competency-battle", str(tmp_path), "--skill", "api-integration", "--suite", "core", "--json"]
    )
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["schema_version"] == "relay-kit.competency-battle.v1"
    assert payload["summary"]["competency_covered"] == 1


def test_public_cli_domain_pack_list_json(capsys, tmp_path: Path) -> None:
    code = relay_kit_public_cli.main(["eval", "domain-pack", "list", str(tmp_path), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["schema_version"] == "relay-kit.domain-pack.v1"
    assert {pack["name"] for pack in payload["packs"]} == {"commerce-api", "mmo-safe-ops"}
