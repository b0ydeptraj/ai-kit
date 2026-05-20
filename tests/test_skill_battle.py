from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3.skill_battle import build_skill_battle, build_skill_weakness_report


ROOT = Path(__file__).resolve().parents[1]
RESOURCE_ROOT = ROOT / "relay_kit_v3" / "skill_resources"
PATTERN_CASE_EXPECTATIONS = {
    "dependency-management": ["dependency drift", "lockfile", "transitive dependency", "rollback pin", "latest-only advice"],
    "go-service-engineering": ["handler boundary", "context cancellation", "transaction boundary", "httptest", "handler-only review"],
    "testing-patterns": ["fixture", "factory", "integration boundary", "flake", "mock everything"],
    "repo-map": ["entrypoint", "ownership", "dependency direction", "nearby test", "tree dump"],
    "browser-inspector": ["console", "network", "dom", "screenshot", "screenshot only"],
    "mmo-account-operations": ["account health", "quarantine", "cooldown", "operator ledger"],
    "mmo-browser-fleet-automation": ["session lease", "profile-to-proxy affinity", "console logs", "operator ledger"],
    "mmo-http-api-automation": ["request ledger", "idempotency key", "retry count", "redacted"],
    "mmo-cloud-operations-automation": ["worker queue", "queue depth", "dead-letter", "pause"],
    "mmo-mobile-app-automation": ["device lease", "logcat", "app-state", "operator ledger"],
    "mmo-lowcode-automation": ["node graph", "execution history", "redacted execution", "operator ledger"],
    "mmo-social-marketing-automation": ["approval lane", "quota meter", "reject reason", "operator ledger"],
    "mmo-reup-automation": ["source inventory", "publish queue", "dedupe", "evidence timeline"],
}


def _load_skill_cases(skill_name: str) -> list[dict[str, object]]:
    cases_path = RESOURCE_ROOT / skill_name / "evals" / f"{skill_name}-cases.json"
    return json.loads(cases_path.read_text(encoding="utf-8"))


def test_skill_battle_scores_single_skill_and_cleans_tmp(tmp_path: Path) -> None:
    report = build_skill_battle(tmp_path, skill="api-integration", suite="deep", cleanup=True)

    assert report["schema_version"] == "relay-kit.skill-battle.v1"
    assert report["summary"]["skill_count"] == 1
    assert report["skills"][0]["skill"] == "api-integration"
    assert report["skills"][0]["score"] >= 8
    assert report["skills"][0]["case_count"] == 3
    assert report["skills"][0]["claim_status"] in {"battle-max-on-suite", "battle-strong-needs-more-cases"}
    assert not (tmp_path / ".tmp" / "relay-kit-skill-battle").exists()


def test_skill_battle_all_skills_meet_hardening_threshold() -> None:
    report = build_skill_battle(ROOT, skill="all", suite="deep", cleanup=True)

    assert report["status"] == "pass"
    assert report["summary"]["skill_count"] >= 62
    assert report["summary"]["weakest_score"] >= 8
    assert not report["findings"]


def test_pattern_specific_deep_cases_exist_for_utility_and_mmo_skills() -> None:
    missing_by_skill: dict[str, list[str]] = {}
    malformed_cases: dict[str, list[str]] = {}
    for skill_name, required_terms in PATTERN_CASE_EXPECTATIONS.items():
        cases = _load_skill_cases(skill_name)
        combined = json.dumps(cases, ensure_ascii=True).lower()
        missing = [term for term in required_terms if term.lower() not in combined]
        if missing:
            missing_by_skill[skill_name] = missing
        for case in cases:
            case_id = str(case.get("id", "<missing-id>"))
            missing_fields = [
                field
                for field in [
                    "expected_files",
                    "expected_symbols",
                    "expected_tests",
                    "expected_evidence_terms",
                    "bad_answer_traps",
                ]
                if not case.get(field)
            ]
            if missing_fields:
                malformed_cases.setdefault(skill_name, []).append(f"{case_id}:{','.join(missing_fields)}")

    assert missing_by_skill == {}
    assert malformed_cases == {}


def test_skill_weakness_report_summarizes_battle_output(tmp_path: Path) -> None:
    battle = build_skill_battle(tmp_path, skill="api-integration", suite="deep", cleanup=True)
    report = build_skill_weakness_report(tmp_path, battle_report=battle)

    assert report["schema_version"] == "relay-kit.skill-weakness-report.v1"
    assert report["source_schema_version"] == "relay-kit.skill-battle.v1"
    assert report["summary"]["finding_count"] == 0


def test_public_cli_skill_battle_and_weakness_json(capsys, tmp_path: Path) -> None:
    battle_code = relay_kit_public_cli.main(
        ["eval", "skill-battle", str(tmp_path), "--skill", "api-integration", "--suite", "deep", "--cleanup", "--json"]
    )
    battle_payload = json.loads(capsys.readouterr().out)
    weakness_code = relay_kit_public_cli.main(["eval", "skill-weakness-report", str(tmp_path), "--json"])
    weakness_payload = json.loads(capsys.readouterr().out)

    assert battle_code == 0
    assert battle_payload["schema_version"] == "relay-kit.skill-battle.v1"
    assert battle_payload["skills"][0]["score"] >= 8
    assert weakness_code == 0
    assert weakness_payload["schema_version"] == "relay-kit.skill-weakness-report.v1"
