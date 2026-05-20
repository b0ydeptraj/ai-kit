from __future__ import annotations

from pathlib import Path

from relay_kit_v3.registry.skills import ALL_V3_SKILLS


ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = ROOT / "docs" / "site"
REQUIRED_PAGES = {
    "index.md",
    "skill-catalog.md",
    "context-graph.md",
    "prompt-enhance.md",
    "install.md",
    "readiness.md",
    "battle-benchmark.md",
}
FORBIDDEN_OVERCLAIMS = {
    "replaces augment",
    "full context engine",
    "guaranteed expert",
    "expert guarantee engine",
    "commercial proof",
    "field-tested proof",
}


def test_docs_site_pages_exist() -> None:
    for name in REQUIRED_PAGES:
        assert (SITE_ROOT / name).exists(), name


def test_skill_catalog_lists_every_canonical_skill() -> None:
    catalog = (SITE_ROOT / "skill-catalog.md").read_text(encoding="utf-8")

    for skill_name in ALL_V3_SKILLS:
        assert f"`{skill_name}`" in catalog
    assert catalog.count("| `") == len(ALL_V3_SKILLS)
    assert "| `workflow-router` | routing-kernel | layer-1-orchestrators | core-showcase |" in catalog
    assert "| `repo-map` | utility-provider | layer-3-utility-providers | core-showcase |" in catalog
    assert "| `mmo-http-api-automation` | mmo-api-automation | layer-4-specialists-and-standalones | specialized-extension |" in catalog
    assert "public-ready" not in catalog
    assert "specialized-extension" in catalog
    assert "competency-covered" in catalog
    assert "archetype-tested" in catalog
    assert "battle-max-on-suite" in catalog
    assert "domain-pack-tested:" not in catalog


def test_docs_site_avoids_market_or_context_overclaim() -> None:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in SITE_ROOT.glob("*.md"))

    for phrase in FORBIDDEN_OVERCLAIMS:
        assert phrase not in text
    assert "no cloud embeddings" in text
    assert "not a semantic codebase engine" in text
    assert "not proof of external commercial adoption" in text
    assert "public-repo benchmark evidence" in text
    assert "competency-covered" in text
    assert "archetype-tested" in text


def test_readme_points_to_docs_site() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "docs/site/index.md" in readme


def test_public_readme_uses_core_showcase_not_extension_pack_dump() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_vi = (ROOT / "README.vi.md").read_text(encoding="utf-8")

    for text in (readme, readme_vi):
        assert "docs/site/assets/relay-kit-hero.svg" in text
        assert "Core Skill System" in text or "Hệ thống skill cốt lõi" in text
        assert "mmo-" not in text.casefold()


def test_docs_site_has_brand_asset() -> None:
    asset = SITE_ROOT / "assets" / "relay-kit-hero.svg"
    assert asset.exists()
    text = (SITE_ROOT / "index.md").read_text(encoding="utf-8")
    assert "assets/relay-kit-hero.svg" in text
