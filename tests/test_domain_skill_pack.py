from __future__ import annotations

from pathlib import Path

from relay_kit_v3.generator import BUNDLES, emit_core_skills
from relay_kit_v3.registry.skills import ALL_V3_SKILLS, render_skill


DOMAIN_SKILLS = {
    "go-service-engineering",
    "next-product-frontend",
    "growth-marketing",
    "market-research",
    "automation-ops",
    "vietnamese-product-localization",
    "mmo-reup-automation",
    "mmo-account-operations",
    "mmo-browser-fleet-automation",
    "mmo-social-marketing-automation",
    "mmo-lowcode-automation",
    "mmo-mobile-app-automation",
    "mmo-cloud-operations-automation",
    "mmo-http-api-automation",
    "mmo-identity-infrastructure",
    "mmo-proxy-network-ops",
    "mmo-nick-warmup-engine",
    "mmo-ecommerce-multichannel",
    "mmo-content-factory",
    "mmo-crypto-wallet-farming",
    "mmo-data-harvesting",
    "frontend-design",
    "ui-styling",
    "aesthetic",
}


def test_domain_skills_exist_in_registry() -> None:
    missing = sorted(skill for skill in DOMAIN_SKILLS if skill not in ALL_V3_SKILLS)

    assert missing == []


def test_domain_skills_have_layer_role_and_render_contract() -> None:
    for skill_name in sorted(DOMAIN_SKILLS):
        spec = ALL_V3_SKILLS[skill_name]
        rendered = render_skill(spec)

        assert spec.layer == "layer-4-specialists-and-standalones"
        assert spec.role
        assert "## Inputs" in rendered
        assert "## Outputs" in rendered
        assert "## Reference skills and rules" in rendered
        assert "## Likely next step" in rendered


def test_enterprise_bundle_includes_domain_skills() -> None:
    enterprise_bundle = set(BUNDLES["enterprise"])

    assert DOMAIN_SKILLS.issubset(enterprise_bundle)


def test_domain_skills_generate_for_all_adapters(tmp_path: Path) -> None:
    written = emit_core_skills(tmp_path, "all", "enterprise")

    assert written
    for adapter in (".codex", ".claude", ".agent"):
        for skill_name in DOMAIN_SKILLS:
            skill_path = tmp_path / adapter / "skills" / skill_name / "SKILL.md"
            assert skill_path.exists(), str(skill_path)
