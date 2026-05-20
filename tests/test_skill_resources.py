from __future__ import annotations

import json
from pathlib import Path

from relay_kit_v3.generator import emit_core_skills
from relay_kit_v3.registry.skills import ALL_V3_SKILLS, EDIT_AND_TEST_TOOLS, READ_ANALYZE_TOOLS


ROOT = Path(__file__).resolve().parents[1]
DOMAIN_RESOURCE_SKILLS = [
    "automation-ops",
    "market-research",
    "growth-marketing",
    "next-product-frontend",
    "mmo-reup-automation",
    "mmo-account-operations",
    "mmo-browser-fleet-automation",
    "mmo-social-marketing-automation",
    "mmo-lowcode-automation",
    "mmo-mobile-app-automation",
    "mmo-cloud-operations-automation",
    "mmo-http-api-automation",
]
RESOURCE_SKILLS = sorted(ALL_V3_SKILLS)
READ_ONLY_RESOURCE_SKILLS = {"market-research", "growth-marketing"}
GENERIC_RESOURCE_PHRASES = {
    "Good response shape",
    "Bad response shape",
    "Handle a compact",
    "context-anchored-output",
    "handoff-and-risk-control",
    "Use this contract when",
    "Use this reference when",
}


def test_domain_skill_resources_exist_and_have_eval_cases() -> None:
    for skill_name in RESOURCE_SKILLS:
        skill_root = ROOT / "relay_kit_v3" / "skill_resources" / skill_name

        assert (skill_root / "references" / f"{skill_name}-operator-contract.md").exists(), skill_name
        assert (skill_root / "examples" / f"{skill_name}-good-output.md").exists(), skill_name
        assert (skill_root / "examples" / f"{skill_name}-bad-output.md").exists(), skill_name
        competency_path = skill_root / "competencies" / f"{skill_name}-competencies.json"
        competencies = json.loads(competency_path.read_text(encoding="utf-8"))
        assert competencies["schema_version"] == "relay-kit.skill-competency.v1"
        assert len(competencies["core_competencies"]) >= 5
        assert len(competencies["failure_traps"]) >= 2
        cases_path = skill_root / "evals" / f"{skill_name}-cases.json"
        cases = json.loads(cases_path.read_text(encoding="utf-8"))

        assert isinstance(cases, list), skill_name
        assert len(cases) >= 3, skill_name
        for case in cases:
            assert case["skill"] == skill_name
            assert case["repo_profile"]
            assert case["task"]
            assert case["expected_files"]
            assert case["expected_symbols"]
            assert case["expected_tests"]
            assert case["expected_evidence_terms"]
            assert case["bad_answer_traps"]
            assert len(case["expected_evidence_terms"]) >= 3


def test_skill_resources_are_not_generic_skeletons() -> None:
    for skill_name in RESOURCE_SKILLS:
        skill_root = ROOT / "relay_kit_v3" / "skill_resources" / skill_name
        for path in [
            skill_root / "references" / f"{skill_name}-operator-contract.md",
            skill_root / "examples" / f"{skill_name}-good-output.md",
            skill_root / "examples" / f"{skill_name}-bad-output.md",
        ]:
            text = path.read_text(encoding="utf-8")
            for phrase in GENERIC_RESOURCE_PHRASES:
                assert phrase not in text, f"{skill_name}: {phrase}"


def test_domain_skill_resources_copy_to_all_adapters(tmp_path: Path) -> None:
    emit_core_skills(tmp_path, "all", "enterprise")

    for adapter in (".codex", ".claude", ".agent"):
        for skill_name in RESOURCE_SKILLS:
            skill_root = tmp_path / adapter / "skills" / skill_name

            assert (skill_root / "references" / f"{skill_name}-operator-contract.md").exists()
            assert (skill_root / "examples" / f"{skill_name}-good-output.md").exists()
            assert (skill_root / "examples" / f"{skill_name}-bad-output.md").exists()
            assert (skill_root / "evals" / f"{skill_name}-cases.json").exists()
            assert (skill_root / "competencies" / f"{skill_name}-competencies.json").exists()
            source_profile = json.loads(
                (ROOT / "relay_kit_v3" / "skill_resources" / skill_name / "competencies" / f"{skill_name}-competencies.json").read_text(
                    encoding="utf-8"
                )
            )
            copied_profile = json.loads(
                (skill_root / "competencies" / f"{skill_name}-competencies.json").read_text(encoding="utf-8")
            )
            assert copied_profile["category"] == source_profile["category"]
            assert {item["id"] for item in copied_profile["core_competencies"]} == {
                item["id"] for item in source_profile["core_competencies"]
            }


def test_all_skills_reference_their_resource_pack() -> None:
    for skill_name in RESOURCE_SKILLS:
        spec = ALL_V3_SKILLS[skill_name]
        assert f"references/{skill_name}-operator-contract.md" in "\n".join(spec.references)
        assert f"evals/{skill_name}-cases.json" in "\n".join(spec.references)
        assert f"competencies/{skill_name}-competencies.json" in "\n".join(spec.references)


def test_hardened_domain_skills_keep_explicit_tool_stance() -> None:
    for skill_name in DOMAIN_RESOURCE_SKILLS:
        spec = ALL_V3_SKILLS[skill_name]
        expected_tools = READ_ANALYZE_TOOLS if skill_name in READ_ONLY_RESOURCE_SKILLS else EDIT_AND_TEST_TOOLS

        assert spec.allowed_tools == expected_tools, skill_name
