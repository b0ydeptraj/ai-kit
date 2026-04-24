from pathlib import Path

from relay_kit_v3.registry.skills import ROLE_SKILLS


ROOT = Path(__file__).resolve().parents[1]
GENERATED_DEVELOPER_SKILLS = [
    ROOT / ".claude" / "skills" / "developer" / "SKILL.md",
    ROOT / ".agent" / "skills" / "developer" / "SKILL.md",
    ROOT / ".codex" / "skills" / "developer" / "SKILL.md",
]

FORBIDDEN_HARD_DEPENDENCY = "Default to `test-first-development` whenever"
CONDITIONAL_CONTRACT = "Use `test-first-development` when it is installed, selected, or provided by the active bundle"


def developer_registry_text() -> str:
    spec = ROLE_SKILLS["developer"]
    return "\n".join([spec.body, *spec.references])


def test_developer_registry_uses_conditional_test_first_contract() -> None:
    text = developer_registry_text()

    assert FORBIDDEN_HARD_DEPENDENCY not in text
    assert CONDITIONAL_CONTRACT in text


def test_generated_developer_skills_use_conditional_test_first_contract() -> None:
    for skill_path in GENERATED_DEVELOPER_SKILLS:
        text = skill_path.read_text(encoding="utf-8")

        assert FORBIDDEN_HARD_DEPENDENCY not in text, skill_path
        assert CONDITIONAL_CONTRACT in text, skill_path
