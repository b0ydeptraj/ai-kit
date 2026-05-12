from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3.adapter_diagnostics import build_adapter_diagnostics
from relay_kit_v3.command_registry import lifecycle_command_records
from relay_kit_v3.generator import emit_core_skills
from relay_kit_v3.localized_metadata import (
    localized_skill_description,
    resolve_locale_pack,
)
from relay_kit_v3.runtime_locale import (
    default_runtime_locale,
    ensure_runtime_locale,
    inspect_runtime_locale,
    load_runtime_locale,
    runtime_locale_file,
    write_runtime_locale,
)


def test_runtime_locale_defaults_and_ensure(tmp_path: Path) -> None:
    payload = default_runtime_locale()

    assert payload["schema_version"] == "relay-kit.runtime-locale.v1"
    assert payload["locale_profile"] == "en"
    assert payload["fallback_locale"] == "en"
    assert payload["enforce_output_language"] is True

    path = ensure_runtime_locale(tmp_path)
    assert path == runtime_locale_file(tmp_path)
    assert path.exists()


def test_runtime_locale_write_and_load_normalize(tmp_path: Path) -> None:
    updated = write_runtime_locale(tmp_path, locale="VI", fallback_locale="EN", enforce_output_language=False)
    loaded = load_runtime_locale(tmp_path)

    assert updated["locale_profile"] == "vi"
    assert updated["fallback_locale"] == "en"
    assert updated["enforce_output_language"] is False
    assert loaded == updated


def test_runtime_locale_rejects_unsupported_values(tmp_path: Path) -> None:
    try:
        write_runtime_locale(tmp_path, locale="zz")
    except ValueError as exc:
        assert "Invalid locale value" in str(exc)
    else:
        raise AssertionError("write_runtime_locale should reject unsupported locale")


def test_runtime_locale_inspect_fails_for_invalid_json(tmp_path: Path) -> None:
    target = runtime_locale_file(tmp_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{not json}\n", encoding="utf-8")

    report = inspect_runtime_locale(tmp_path)

    assert report["status"] == "hold"
    assert any(finding["id"] == "invalid-runtime-locale-json" for finding in report["findings"])


def test_public_cli_locale_set_and_show_json(tmp_path: Path, capsys) -> None:
    exit_code = relay_kit_public_cli.main(["locale", "set", str(tmp_path), "--locale", "vi", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["locale_profile"] == "vi"
    assert payload["fallback_locale"] == "en"

    exit_code = relay_kit_public_cli.main(["locale", "show", str(tmp_path), "--json"])
    report = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert report["status"] == "pass"
    assert report["summary"]["locale_profile"] == "vi"


def test_locale_switch_propagates_to_generated_command_and_agent_surfaces(tmp_path: Path) -> None:
    write_runtime_locale(tmp_path, locale="vi", enforce_output_language=True)

    emit_core_skills(tmp_path, "codex", "enterprise")

    command_surface = (tmp_path / ".codex" / "commands" / "relay-start.md").read_text(encoding="utf-8")
    agent_surface = (tmp_path / ".codex" / "agents" / "relay-engineer.md").read_text(encoding="utf-8")

    assert "- locale-profile: `vi`" in command_surface
    assert "- enforce-output-language: `True`" in command_surface
    assert "Bắt đầu một yêu cầu với routing rõ ràng và lane mode cụ thể." in command_surface
    assert "- locale-profile: `vi`" in agent_surface
    assert "Triển khai công việc kỹ thuật với planning, verification và readiness gate chặt chẽ." in agent_surface


def test_locale_resolver_fallback_chain_prefers_supported_pack() -> None:
    assert resolve_locale_pack("zz-zz", "fr") == "en"
    assert resolve_locale_pack("fr-ca", "vi-vn") == "vi"
    assert resolve_locale_pack("fr-ca", "de-de") == "en"


def test_generated_skill_description_localizes_for_vi_and_unsupported_locale(tmp_path: Path) -> None:
    write_runtime_locale(tmp_path, locale="vi", fallback_locale="en")
    emit_core_skills(tmp_path, "codex", "enterprise")
    vi_skill = (tmp_path / ".codex" / "skills" / "developer" / "SKILL.md").read_text(encoding="utf-8")
    assert "description: Dùng khi planning is ready and code must be changed with controlled scope and evidence." in vi_skill

    legacy_policy = runtime_locale_file(tmp_path)
    legacy_policy.parent.mkdir(parents=True, exist_ok=True)
    legacy_policy.write_text(
        json.dumps(
            {
                "schema_version": "relay-kit.runtime-locale.v1",
                "locale_profile": "zz",
                "fallback_locale": "en",
                "enforce_output_language": True,
            },
            ensure_ascii=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    emit_core_skills(tmp_path, "codex", "enterprise")
    fallback_skill = (tmp_path / ".codex" / "skills" / "developer" / "SKILL.md").read_text(encoding="utf-8")
    assert "description: Use when planning is ready and code must be changed with controlled scope and evidence." in fallback_skill


def test_generated_command_and_agent_surfaces_fallback_for_unsupported_locale(tmp_path: Path) -> None:
    legacy_policy = runtime_locale_file(tmp_path)
    legacy_policy.parent.mkdir(parents=True, exist_ok=True)
    legacy_policy.write_text(
        json.dumps(
            {
                "schema_version": "relay-kit.runtime-locale.v1",
                "locale_profile": "zz-zz",
                "fallback_locale": "en",
                "enforce_output_language": True,
            },
            ensure_ascii=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    emit_core_skills(tmp_path, "codex", "enterprise")
    command_surface = (tmp_path / ".codex" / "commands" / "relay-start.md").read_text(encoding="utf-8")
    agent_surface = (tmp_path / ".codex" / "agents" / "relay-engineer.md").read_text(encoding="utf-8")
    assert "Start a request with explicit routing and lane mode." in command_surface
    assert "Deliver implementation work with strict planning, verification, and readiness gates." in agent_surface


def test_adapter_diagnose_strict_passes_localized_runtime(tmp_path: Path) -> None:
    write_runtime_locale(tmp_path, locale="vi", fallback_locale="en")
    emit_core_skills(tmp_path, "all", "enterprise")
    report = build_adapter_diagnostics(tmp_path, adapter="all")
    assert report["status"] == "pass"
    assert report["summary"]["metadata_drift"] == 0


def test_skill_gauntlet_strict_semantic_passes_localized_runtime(tmp_path: Path) -> None:
    write_runtime_locale(tmp_path, locale="vi", fallback_locale="en")
    emit_core_skills(tmp_path, "all", "enterprise")
    result = subprocess.run(
        [sys.executable, "scripts/skill_gauntlet.py", str(tmp_path), "--strict", "--semantic"],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_command_and_agent_list_remain_english_under_non_english_locale(tmp_path: Path, capsys) -> None:
    write_runtime_locale(tmp_path, locale="vi", fallback_locale="en")
    emit_core_skills(tmp_path, "codex", "enterprise")

    exit_code = relay_kit_public_cli.main(["command", "list", str(tmp_path), "--json"])
    command_payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert command_payload["commands"][0]["intent"] == lifecycle_command_records()[0]["intent"]

    exit_code = relay_kit_public_cli.main(["agent", "list", str(tmp_path), "--json"])
    agent_payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert agent_payload["profiles"][0]["display_name"] == "Relay Engineer"


def test_localized_skill_description_falls_back_to_english_for_missing_pack() -> None:
    base = "Use when work starts from a regression."
    assert localized_skill_description("debug-hub", base, locale="fr-fr", fallback_locale="de") == base
