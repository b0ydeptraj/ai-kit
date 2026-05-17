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
    assert "| public-ready | complete | 2+ cases |" in catalog


def test_docs_site_avoids_market_or_context_overclaim() -> None:
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in SITE_ROOT.glob("*.md"))

    for phrase in FORBIDDEN_OVERCLAIMS:
        assert phrase not in text
    assert "no cloud embeddings" in text
    assert "not a semantic codebase engine" in text
    assert "not proof of external commercial adoption" in text


def test_readme_points_to_docs_site() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "docs/site/index.md" in readme
