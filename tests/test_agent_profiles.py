from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3.agent_profiles import (
    agent_profile_ids,
    agent_profiles,
    render_agent_surface,
)
from relay_kit_v3.generator import emit_core_skills


def write_agent_project(root: Path) -> None:
    emit_core_skills(root, "all", "enterprise")


def test_agent_registry_has_two_profiles() -> None:
    profiles = agent_profiles()

    assert len(profiles) == 2
    assert len(agent_profile_ids()) == 2
    assert agent_profile_ids() == ["relay-engineer", "relay-growth"]


def test_agent_surface_renderer_is_deterministic() -> None:
    profile = agent_profiles()[0]

    first = render_agent_surface(profile, adapter="codex")
    second = render_agent_surface(profile, adapter="codex")

    assert first == second
    assert "# relay-engineer" in first
    assert "workflow-router -> scout-hub -> plan-hub" in first


def test_generation_emits_canonical_and_adapter_agent_surfaces(tmp_path: Path) -> None:
    write_agent_project(tmp_path)
    expected = {f"{name}.md" for name in agent_profile_ids()}

    canonical_root = tmp_path / ".relay-kit" / "agents"
    assert canonical_root.exists()
    canonical_files = {path.name for path in canonical_root.glob("*.json")}
    assert canonical_files == {"relay-engineer.json", "relay-growth.json"}

    for root in (".claude/agents", ".codex/agents", ".agent/agents"):
        agent_root = tmp_path / root
        assert agent_root.exists()
        names = {path.name for path in agent_root.glob("*.md")}
        assert names == expected


def test_public_cli_agent_list_outputs_contract(tmp_path: Path, capsys) -> None:
    exit_code = relay_kit_public_cli.main(["agent", "list", str(tmp_path), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["schema_version"] == "relay-kit.agent-registry.v1"
    assert payload["summary"]["profile_count"] == 2
    assert payload["profiles"][0]["id"] == "relay-engineer"
    assert payload["profiles"][-1]["id"] == "relay-growth"


def test_public_cli_agent_diagnose_strict_passes_generated_surface(tmp_path: Path, capsys) -> None:
    write_agent_project(tmp_path)

    exit_code = relay_kit_public_cli.main(
        ["agent", "diagnose", str(tmp_path), "--adapter", "all", "--strict", "--json"]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "pass"
    assert payload["summary"]["missing_profiles"] == 0
    assert payload["summary"]["unexpected_profiles"] == 0
    assert payload["summary"]["invalid_profile_contracts"] == 0


def test_public_cli_agent_diagnose_strict_fails_on_missing_or_extra(tmp_path: Path, capsys) -> None:
    write_agent_project(tmp_path)
    (tmp_path / ".codex" / "agents" / "relay-growth.md").unlink()
    (tmp_path / ".codex" / "agents" / "relay-extra.md").write_text("# relay-extra\n", encoding="utf-8")

    exit_code = relay_kit_public_cli.main(
        ["agent", "diagnose", str(tmp_path), "--adapter", "codex", "--strict", "--json"]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["status"] == "hold"
    assert payload["summary"]["missing_profiles"] == 1
    assert payload["summary"]["unexpected_profiles"] == 1
