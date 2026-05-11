from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3 import token_economy


def write_token_project(root: Path) -> None:
    (root / ".relay-kit" / "state").mkdir(parents=True, exist_ok=True)
    (root / ".relay-kit" / "contracts").mkdir(parents=True, exist_ok=True)
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / ".relay-kit" / "state" / "workflow-state.md").write_text(
        "\n".join(
            [
                "# workflow-state",
                "Traceback (most recent call last):",
                '  File "runner.py", line 42, in <module>',
                "AssertionError: expected release gate pass",
                "exit code 2",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / ".relay-kit" / "contracts" / "project-context.md").write_text(
        "# project-context\n\nArchitecture and release coordination notes.\n",
        encoding="utf-8",
    )
    (root / "docs" / "release-notes.md").write_text(
        "# release notes\n\nThis is a compact changelog for token economy checks.\n",
        encoding="utf-8",
    )


def test_context_budget_reports_required_contract_and_metrics(tmp_path: Path) -> None:
    write_token_project(tmp_path)

    report = token_economy.build_context_budget(
        tmp_path,
        max_tokens=8000,
        scopes=["state", "contracts", "docs"],
    )

    assert report["schema_version"] == "relay-kit.context-budget.v1"
    assert report["summary"]["source_count"] >= 2
    assert {"estimated_tokens", "compressed_tokens", "signal_retention", "raw_required_blocks", "budget_violations"} <= set(
        report["summary"]
    )
    raw_required = [
        source
        for source in report["selected_sources"]
        if source["classification"] == "raw-required"
    ]
    assert raw_required
    assert raw_required[0]["raw_path"].endswith("workflow-state.md")


def test_context_pack_is_task_scoped_and_can_drop_sources(tmp_path: Path) -> None:
    write_token_project(tmp_path)

    report = token_economy.build_context_pack(
        tmp_path,
        task="traceback assertion failure release gate",
        max_tokens=20,
        scopes=["state", "contracts", "docs"],
    )

    assert report["schema_version"] == "relay-kit.context-pack.v1"
    assert report["task"] == "traceback assertion failure release gate"
    assert report["summary"]["source_count"] >= 1
    assert report["summary"]["selected_source_count"] >= 1
    assert report["summary"]["dropped_source_count"] >= 1
    assert all("authority" in source and "freshness" in source for source in report["selected_sources"])


def test_public_cli_context_budget_and_pack_json(tmp_path: Path, capsys) -> None:
    write_token_project(tmp_path)

    budget_code = relay_kit_public_cli.main(
        ["context", "budget", str(tmp_path), "--max-tokens", "8000", "--strict", "--json"]
    )
    budget_payload = json.loads(capsys.readouterr().out)

    pack_code = relay_kit_public_cli.main(
        [
            "context",
            "pack",
            str(tmp_path),
            "--task",
            "traceback assertion release",
            "--max-tokens",
            "8000",
            "--strict",
            "--json",
        ]
    )
    pack_payload = json.loads(capsys.readouterr().out)

    assert budget_code == 0
    assert budget_payload["schema_version"] == "relay-kit.context-budget.v1"
    assert pack_code == 0
    assert pack_payload["schema_version"] == "relay-kit.context-pack.v1"


def test_public_cli_token_audit_strict_fails_on_budget_violation(tmp_path: Path, capsys) -> None:
    write_token_project(tmp_path)

    exit_code = relay_kit_public_cli.main(
        ["token", "audit", str(tmp_path), "--max-tokens", "1", "--strict", "--json"]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["schema_version"] == "relay-kit.token-audit.v1"
    assert payload["status"] == "hold"
    assert payload["metrics"]["budget_violations"] == 1
