from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PORTABLE_SKILL_COMMANDS = [
    ("runtime", "doctor"),
    ("skill", "gauntlet"),
    ("impact", "radar"),
    ("accessibility", "review"),
    ("release", "readiness"),
    ("continuity", "checkpoint"),
    ("continuity", "rehydrate"),
    ("continuity", "handoff"),
    ("continuity", "diff-since-last"),
    ("migration", "guard"),
]
EXPECTED_SKILL_COMMAND_TEXT = {
    "runtime-doctor": "relay-kit runtime doctor <project> --strict",
    "skill-gauntlet": "relay-kit skill gauntlet <project> --strict",
    "impact-radar": "relay-kit impact radar <project>",
    "accessibility-review": "relay-kit accessibility review <project>",
    "release-readiness": "relay-kit release readiness <project> --phase pre|post",
    "context-continuity": "relay-kit continuity",
    "migration-guard": "relay-kit migration guard <project> --strict",
    "memory-search": "relay-kit query search <project> --query",
    "policy-guard": "relay-kit policy check <project> --strict",
}


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "relay_kit_public_cli.py", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_public_cli_exposes_script_backed_skill_wrappers() -> None:
    for command in PORTABLE_SKILL_COMMANDS:
        result = run_cli(*command, "--help")

        assert result.returncode == 0, " ".join(command) + "\n" + result.stdout + result.stderr
        assert "usage:" in result.stdout


def test_generated_runtime_skills_use_portable_cli_commands(tmp_path: Path) -> None:
    result = run_cli("init", str(tmp_path), "--all")

    assert result.returncode == 0, result.stdout + result.stderr
    for adapter in (".codex", ".claude", ".agent"):
        skills_root = tmp_path / adapter / "skills"
        for skill_path in skills_root.rglob("SKILL.md"):
            text = skill_path.read_text(encoding="utf-8")

            assert "python scripts/" not in text, str(skill_path)
        for skill_name, expected_text in EXPECTED_SKILL_COMMAND_TEXT.items():
            skill_path = skills_root / skill_name / "SKILL.md"
            text = skill_path.read_text(encoding="utf-8")

            assert expected_text in text, str(skill_path)
