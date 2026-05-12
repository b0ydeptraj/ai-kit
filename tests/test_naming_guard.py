from __future__ import annotations

import importlib
from pathlib import Path

from scripts import naming_guard


ROOT = Path(__file__).resolve().parents[1]


def test_relay_kit_v3_registry_is_primary_package() -> None:
    skills = importlib.import_module("relay_kit_v3.registry.skills")

    assert "developer" in skills.ALL_V3_SKILLS


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


def test_naming_guard_blocks_retired_package_token(tmp_path: Path) -> None:
    token = "ai_" "kit_v3"
    target = tmp_path / "example.py"
    target.write_text(f"from {token}.generator import BUNDLES\n", encoding="utf-8")

    findings = naming_guard.collect_findings(
        tmp_path,
        naming_guard.DEFAULT_TOKENS,
    )

    assert [(finding.path, finding.line, finding.token) for finding in findings] == [
        ("example.py", 1, token)
    ]


def test_naming_guard_ignores_generated_runtime_artifacts(tmp_path: Path) -> None:
    context_file = tmp_path / ".relay-kit" / "context" / "context-budget.json"
    token_file = tmp_path / ".relay-kit" / "token" / "token-audit.json"
    pulse_file = tmp_path / ".relay-kit" / "pulse" / "pulse-report.json"
    signal_file = tmp_path / ".relay-kit" / "signals" / "latest.json"
    context_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.parent.mkdir(parents=True, exist_ok=True)
    pulse_file.parent.mkdir(parents=True, exist_ok=True)
    signal_file.parent.mkdir(parents=True, exist_ok=True)
    context_token = ".ai" "-kit"
    legacy_namespace_token = "ai_" "kit_v3"
    context_file.write_text(f'{{"snippet": "legacy token {context_token}"}}\n', encoding="utf-8")
    token_file.write_text(
        f'{{"snippet": "legacy token {legacy_namespace_token}"}}\n',
        encoding="utf-8",
    )
    pulse_file.write_text(f'{{"snippet": "legacy token {context_token}"}}\n', encoding="utf-8")
    signal_file.write_text(f'{{"snippet": "legacy token {legacy_namespace_token}"}}\n', encoding="utf-8")

    findings = naming_guard.collect_findings(
        tmp_path,
        naming_guard.DEFAULT_TOKENS,
    )

    assert findings == []


def test_naming_guard_ignores_schema_word_collisions(tmp_path: Path) -> None:
    schema = tmp_path / "templates" / "skills" / "docx" / "ooxml" / "schemas" / "sample.xsd"
    schema.parent.mkdir(parents=True, exist_ok=True)
    schema.write_text(f"<enum value='{('round' + '2' + 'SameRect')}'/>\n", encoding="utf-8")

    findings = naming_guard.collect_findings(
        tmp_path,
        naming_guard.DEFAULT_TOKENS,
    )

    assert findings == []
