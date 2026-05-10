from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli


def write_query_project(root: Path) -> None:
    (root / ".relay-kit" / "contracts").mkdir(parents=True)
    (root / ".relay-kit" / "state").mkdir(parents=True)
    (root / ".relay-kit" / "evidence").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "relay_kit_v3" / "registry").mkdir(parents=True)
    (root / ".relay-kit" / "contracts" / "project-context.md").write_text(
        "# project-context\n\nAdapter diagnostics are the authoritative source for generated skill parity.\n",
        encoding="utf-8",
    )
    (root / ".relay-kit" / "state" / "workflow-state.md").write_text(
        "# workflow-state\n\nNext lane: query search and service boundary map.\n",
        encoding="utf-8",
    )
    (root / "docs" / "relay-kit-adapter-diagnostics.md").write_text(
        "# Adapter diagnostics\n\nUse adapter diagnose for metadata drift.\n",
        encoding="utf-8",
    )
    (root / ".relay-kit" / "evidence" / "events.jsonl").write_text(
        '{"gate":"adapter diagnostics","status":"pass"}\n',
        encoding="utf-8",
    )
    (root / "relay_kit_v3" / "registry" / "skills.py").write_text(
        '"""adapter diagnostics registry terms"""\n',
        encoding="utf-8",
    )


def test_query_search_ranks_authoritative_hits(tmp_path: Path) -> None:
    from relay_kit_v3.query_search import build_query_search

    write_query_project(tmp_path)

    report = build_query_search(tmp_path, query="adapter diagnostics", limit=5)

    assert report["schema_version"] == "relay-kit.query-search.v1"
    assert report["status"] == "pass"
    assert report["summary"]["hit_count"] >= 3
    assert report["results"][0]["source_type"] == "contracts"
    assert report["results"][0]["authority"] > report["results"][-1]["authority"]
    assert report["results"][0]["line"] >= 1


def test_query_search_reports_no_hits(tmp_path: Path) -> None:
    from relay_kit_v3.query_search import build_query_search

    write_query_project(tmp_path)

    report = build_query_search(tmp_path, query="missing phrase", limit=5)

    assert report["status"] == "empty"
    assert report["results"] == []


def test_public_cli_query_search_outputs_json(tmp_path: Path, capsys) -> None:
    write_query_project(tmp_path)

    exit_code = relay_kit_public_cli.main(["query", "search", str(tmp_path), "--query", "adapter diagnostics", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "pass"
    assert payload["summary"]["hit_count"] >= 3
