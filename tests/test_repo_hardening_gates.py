from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from relay_kit_v3.generator import BUNDLES
from relay_kit_v3.public_entrypoints import PUBLIC_ENTRYPOINT_SHIMS
from relay_kit_v3.registry.skills import ALL_V3_SKILLS


ROOT = Path(__file__).resolve().parents[1]


def test_no_empty_or_retired_bundles_are_active() -> None:
    retired = {
        "round" + "2",
        "round" + "3-core",
        "round" + "3",
        "round" + "4-core",
        "round" + "4",
        "baseline" + "-" + "next",
        "b" + "mad-core",
        "b" + "mad-lite",
        "legacy" + "-native",
    }

    assert retired.isdisjoint(BUNDLES)
    assert {name for name, skills in BUNDLES.items() if not skills} == set()
    assert all(set(skills).issubset(ALL_V3_SKILLS) for skills in BUNDLES.values())


def test_relay_kit_rejects_retired_bundle_with_mapping() -> None:
    result = subprocess.run(
        [sys.executable, "relay_kit.py", ".", "--bundle", "baseline" + "-" + "next"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "Use 'baseline' instead" in result.stdout


def test_registered_skills_have_inbound_routing() -> None:
    inbound = {name: set() for name in ALL_V3_SKILLS}
    broken: list[tuple[str, str]] = []
    for skill_name, spec in ALL_V3_SKILLS.items():
        for next_step in spec.next_steps:
            if next_step not in ALL_V3_SKILLS:
                broken.append((skill_name, next_step))
                continue
            inbound[next_step].add(skill_name)

    assert broken == []
    assert {name for name, sources in inbound.items() if not sources} == set()


def test_public_entrypoint_shims_are_adapter_facades_not_registry_skills() -> None:
    assert PUBLIC_ENTRYPOINT_SHIMS.isdisjoint(ALL_V3_SKILLS)

    for adapter in (".codex", ".claude", ".agent"):
        existing = {
            entry.name
            for entry in (ROOT / adapter / "skills").iterdir()
            if entry.is_dir()
        }
        assert PUBLIC_ENTRYPOINT_SHIMS.issubset(existing)


def test_artifact_hygiene_patterns_are_gitignored() -> None:
    patterns = {
        line.strip()
        for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }

    assert {
        ".kilo/",
        ".kiro/",
        "build/",
        "dist/",
        "*.egg-info/",
        ".eggs/",
    }.issubset(patterns)


def test_migration_guard_wrapper_delegates_to_naming_guard() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/migration_guard.py", ".", "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "findings_count" in result.stdout
