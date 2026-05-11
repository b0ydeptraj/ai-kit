from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3.command_registry import (
    command_ids,
    lifecycle_commands,
    render_command_surface,
)
from relay_kit_v3.generator import emit_core_skills


def write_command_project(root: Path) -> None:
    emit_core_skills(root, "all", "enterprise")


def test_command_registry_has_thirteen_commands() -> None:
    commands = lifecycle_commands()

    assert len(commands) == 13
    assert len(command_ids()) == 13
    assert command_ids()[0] == "relay-start"
    assert command_ids()[-1] == "relay-token-audit"
    assert commands[-1].route_target == "token-economy"


def test_command_surface_renderer_is_deterministic() -> None:
    command = lifecycle_commands()[0]

    first = render_command_surface(command, adapter="codex")
    second = render_command_surface(command, adapter="codex")

    assert first == second
    assert "# /relay-start" in first
    assert "- route-target: `workflow-router`" in first


def test_generation_emits_commands_for_all_adapters(tmp_path: Path) -> None:
    write_command_project(tmp_path)
    expected = {f"{name}.md" for name in command_ids()}

    for root in (".claude/commands", ".codex/commands", ".agent/commands"):
        command_root = tmp_path / root
        assert command_root.exists()
        names = {path.name for path in command_root.glob("*.md")}
        assert names == expected


def test_public_cli_command_list_outputs_contract(tmp_path: Path, capsys) -> None:
    exit_code = relay_kit_public_cli.main(["command", "list", str(tmp_path), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["schema_version"] == "relay-kit.command-registry.v1"
    assert payload["summary"]["command_count"] == 13
    assert payload["commands"][0]["id"] == "relay-start"
    assert payload["commands"][-1]["id"] == "relay-token-audit"
    assert payload["commands"][-1]["route_target"] == "token-economy"


def test_public_cli_command_diagnose_strict_passes_generated_surface(tmp_path: Path, capsys) -> None:
    write_command_project(tmp_path)

    exit_code = relay_kit_public_cli.main(
        ["command", "diagnose", str(tmp_path), "--adapter", "all", "--strict", "--json"]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "pass"
    assert payload["summary"]["missing_commands"] == 0
    assert payload["summary"]["unexpected_commands"] == 0


def test_public_cli_command_diagnose_strict_fails_on_missing_or_extra(tmp_path: Path, capsys) -> None:
    write_command_project(tmp_path)
    (tmp_path / ".agent" / "commands" / "relay-plan.md").unlink()
    (tmp_path / ".agent" / "commands" / "relay-extra.md").write_text("# /relay-extra\n", encoding="utf-8")

    exit_code = relay_kit_public_cli.main(
        ["command", "diagnose", str(tmp_path), "--adapter", "agent", "--strict", "--json"]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["status"] == "hold"
    assert payload["summary"]["missing_commands"] == 1
    assert payload["summary"]["unexpected_commands"] == 1
