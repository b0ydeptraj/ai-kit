from __future__ import annotations

from relay_kit_v3.registry.skills import ALL_V3_SKILLS, render_skill


THIN_UTILITY_SKILLS = {
    "problem-solving",
    "sequential-thinking",
    "browser-inspector",
    "multimodal-evidence",
}


def test_thin_utilities_have_boundary_and_evidence_contracts() -> None:
    for skill_name in THIN_UTILITY_SKILLS:
        rendered = render_skill(ALL_V3_SKILLS[skill_name])

        assert "## Boundary" in rendered, skill_name
        assert "## Evidence contract" in rendered, skill_name
