from __future__ import annotations

import json
import shutil
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3.generator import emit_core_skills


def write_adapter_project(root: Path) -> None:
    emit_core_skills(root, "all", "enterprise")


def test_adapter_diagnostics_passes_generated_enterprise_adapters(tmp_path: Path) -> None:
    from relay_kit_v3.adapter_diagnostics import build_adapter_diagnostics

    write_adapter_project(tmp_path)

    report = build_adapter_diagnostics(tmp_path, adapter="all")

    assert report["schema_version"] == "relay-kit.adapter-diagnostics.v1"
    assert report["status"] == "pass"
    assert report["summary"]["missing_skills"] == 0
    assert report["summary"]["unexpected_skills"] == 0
    assert report["summary"]["metadata_drift"] == 0
    assert report["summary"]["missing_commands"] == 0
    assert report["summary"]["unexpected_commands"] == 0
    agent = next(item for item in report["adapters"] if item["adapter"] == "agent")
    assert agent["metadata_policy"]["allowed-tools"] == "advisory"
    assert agent["missing_command_count"] == 0
    assert agent["unexpected_command_count"] == 0


def test_adapter_diagnostics_flags_missing_and_unexpected_skill(tmp_path: Path) -> None:
    from relay_kit_v3.adapter_diagnostics import build_adapter_diagnostics

    write_adapter_project(tmp_path)
    shutil.rmtree(tmp_path / ".codex" / "skills" / "developer")
    extra = tmp_path / ".codex" / "skills" / "not-allowed" / "SKILL.md"
    extra.parent.mkdir(parents=True)
    extra.write_text("---\nname: not-allowed\ndescription: Use when this should not exist.\n---\n", encoding="utf-8")

    report = build_adapter_diagnostics(tmp_path, adapter="codex")

    assert report["status"] == "hold"
    assert {finding["id"] for finding in report["findings"]} >= {"missing-skill", "unexpected-skill"}


def test_adapter_diagnostics_flags_frontmatter_metadata_drift(tmp_path: Path) -> None:
    from relay_kit_v3.adapter_diagnostics import build_adapter_diagnostics

    write_adapter_project(tmp_path)
    skill = tmp_path / ".claude" / "skills" / "skill-evolution" / "SKILL.md"
    skill.write_text(
        skill.read_text(encoding="utf-8").replace(
            'allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]',
            'allowed-tools: ["Read"]',
        ),
        encoding="utf-8",
    )

    report = build_adapter_diagnostics(tmp_path, adapter="claude")

    assert report["status"] == "hold"
    assert any(
        finding["id"] == "frontmatter-drift" and finding["field"] == "allowed-tools"
        for finding in report["findings"]
    )


def test_adapter_diagnostics_flags_missing_command_surface(tmp_path: Path) -> None:
    from relay_kit_v3.adapter_diagnostics import build_adapter_diagnostics

    write_adapter_project(tmp_path)
    (tmp_path / ".claude" / "commands" / "relay-plan.md").unlink()

    report = build_adapter_diagnostics(tmp_path, adapter="claude")

    assert report["status"] == "hold"
    assert any(
        finding["id"] == "missing-command" and finding.get("command_id") == "relay-plan"
        for finding in report["findings"]
    )


def test_adapter_diagnostics_flags_unexpected_command_surface(tmp_path: Path) -> None:
    from relay_kit_v3.adapter_diagnostics import build_adapter_diagnostics

    write_adapter_project(tmp_path)
    extra = tmp_path / ".codex" / "commands" / "relay-extra.md"
    extra.write_text("# /relay-extra\n", encoding="utf-8")

    report = build_adapter_diagnostics(tmp_path, adapter="codex")

    assert report["status"] == "hold"
    assert any(
        finding["id"] == "unexpected-command" and finding.get("command_id") == "relay-extra"
        for finding in report["findings"]
    )


def test_public_cli_adapter_diagnose_outputs_json(tmp_path: Path, capsys) -> None:
    write_adapter_project(tmp_path)

    exit_code = relay_kit_public_cli.main(["adapter", "diagnose", str(tmp_path), "--adapter", "all", "--strict", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "pass"
    assert payload["summary"]["adapter_count"] == 3
