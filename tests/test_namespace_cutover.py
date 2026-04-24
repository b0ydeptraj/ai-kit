from __future__ import annotations

import importlib
from pathlib import Path

from scripts import migration_guard


ROOT = Path(__file__).resolve().parents[1]


def test_relay_kit_v3_registry_is_primary_package() -> None:
    skills = importlib.import_module("relay_kit_v3.registry.skills")

    assert "developer" in skills.ALL_V3_SKILLS


def test_legacy_namespace_shim_points_to_primary_registry() -> None:
    legacy_skills = importlib.import_module("ai_" "kit_v3.registry.skills")
    primary_skills = importlib.import_module("relay_kit_v3.registry.skills")

    assert legacy_skills.ALL_V3_SKILLS is primary_skills.ALL_V3_SKILLS


def test_active_runtime_imports_use_relay_kit_v3_namespace() -> None:
    checked_paths = {
        ROOT / "relay_kit.py",
        ROOT / "relay_kit_public_cli.py",
        ROOT / "scripts" / "runtime_doctor.py",
        ROOT / "scripts" / "skill_gauntlet.py",
        ROOT / "scripts" / "srs_guard.py",
        ROOT / "scripts" / "validate_runtime.py",
    }
    direct_runtime_import_paths = checked_paths - {ROOT / "relay_kit_public_cli.py"}

    for path in checked_paths:
        text = path.read_text(encoding="utf-8")

        assert "from ai_" "kit_v3" not in text, path
        assert "import ai_" "kit_v3" not in text, path
        if path in direct_runtime_import_paths:
            assert "relay_kit_v3" in text, path


def test_migration_guard_blocks_legacy_package_token_outside_allowlist(tmp_path: Path) -> None:
    token = "ai_" "kit_v3"
    target = tmp_path / "example.py"
    target.write_text(f"from {token}.generator import BUNDLES\n", encoding="utf-8")

    findings = migration_guard.collect_findings(
        tmp_path,
        migration_guard.DEFAULT_TOKENS,
        [],
    )

    assert [(finding.path, finding.line, finding.token) for finding in findings] == [
        ("example.py", 1, token)
    ]
