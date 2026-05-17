from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli


def test_public_cli_prompt_enhance_json(capsys, tmp_path: Path) -> None:
    exit_code = relay_kit_public_cli.main(["prompt", "enhance", str(tmp_path), "--prompt", "sửa login", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["schema_version"] == "relay-kit.prompt-enhance.v1"
    assert payload["recommended_skill"] == "debug-hub"
    assert payload["ask_or_act"] == "scout_first"
    assert payload["top_routes"]
    assert "Enhanced prompt" not in payload
    assert "Recommended skill: debug-hub" in payload["enhanced_prompt"]


def test_public_cli_prompt_enhance_text(capsys, tmp_path: Path) -> None:
    exit_code = relay_kit_public_cli.main(["prompt", "enhance", str(tmp_path), "--prompt", "fix CI"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Relay-kit prompt enhance" in output
    assert "Recommended skill: debug-hub" in output
    assert "Evidence required" in output


def test_public_cli_prompt_enhance_writes_output_file(capsys, tmp_path: Path) -> None:
    output_file = tmp_path / "prompt-enhance.json"

    exit_code = relay_kit_public_cli.main(
        [
            "prompt",
            "enhance",
            str(tmp_path),
            "--prompt",
            "tiếp tục build đi",
            "--output-file",
            str(output_file),
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    written = json.loads(output_file.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert output_file.exists()
    assert payload["output_file"] == str(output_file)
    assert written["schema_version"] == "relay-kit.prompt-enhance.v1"
    assert written["recommended_skill"] == "cook"
