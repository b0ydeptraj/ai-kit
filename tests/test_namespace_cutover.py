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


def test_migration_guard_rejects_broad_allowlist_rules(tmp_path: Path) -> None:
    allowlist = tmp_path / "allowlist.txt"
    allowlist.write_text("docs/**/*|*\n", encoding="utf-8")
    target = tmp_path / "docs" / "active.md"
    target.parent.mkdir(parents=True)
    target.write_text("stale marker: .ai-kit\n", encoding="utf-8")

    policy_findings = migration_guard.collect_allowlist_findings(tmp_path, allowlist)
    rules = migration_guard.load_allow_rules(allowlist)
    token_findings = migration_guard.collect_findings(tmp_path, migration_guard.DEFAULT_TOKENS, rules)

    assert any(finding.check == "allowlist-policy" for finding in policy_findings)
    assert [(finding.path, finding.line, finding.token) for finding in token_findings] == [
        ("docs/active.md", 1, ".ai-kit")
    ]


def test_migration_guard_accepts_exact_allowlist_with_metadata(tmp_path: Path) -> None:
    allowlist = tmp_path / "scripts" / "migration_guard_allowlist.txt"
    allowlist.parent.mkdir(parents=True)
    allowlist.write_text(
        "docs/allowed.md|.ai-kit|runtime-migration|2026-04-24|Historical fixture.\n",
        encoding="utf-8",
    )
    allowed_file = tmp_path / "docs" / "allowed.md"
    blocked_file = tmp_path / "docs" / "blocked.md"
    allowed_file.parent.mkdir(parents=True)
    allowed_file.write_text("historical marker: .ai-kit\n", encoding="utf-8")
    blocked_file.write_text("new marker: .ai-kit\n", encoding="utf-8")

    assert migration_guard.collect_allowlist_findings(tmp_path, allowlist) == []
    rules = migration_guard.load_allow_rules(allowlist)
    token_findings = migration_guard.collect_findings(tmp_path, migration_guard.DEFAULT_TOKENS, rules)

    assert [(finding.path, finding.line, finding.token) for finding in token_findings] == [
        ("docs/blocked.md", 1, ".ai-kit")
    ]


def test_migration_guard_ignores_generated_context_and_token_artifacts(tmp_path: Path) -> None:
    context_file = tmp_path / ".relay-kit" / "context" / "context-budget.json"
    token_file = tmp_path / ".relay-kit" / "token" / "token-audit.json"
    context_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.parent.mkdir(parents=True, exist_ok=True)
    context_token = ".ai" "-kit"
    legacy_namespace_token = "ai_" "kit_v3"
    context_file.write_text(f'{{"snippet": "legacy token {context_token}"}}\n', encoding="utf-8")
    token_file.write_text(
        f'{{"snippet": "legacy token {legacy_namespace_token}"}}\n',
        encoding="utf-8",
    )

    findings = migration_guard.collect_findings(
        tmp_path,
        migration_guard.DEFAULT_TOKENS,
        [],
    )

    assert findings == []
