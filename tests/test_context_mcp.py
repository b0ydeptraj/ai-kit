from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3.context_index import (
    build_context_index,
    build_context_mcp_tool_result,
    context_mcp_manifest,
    write_active_context,
    write_context_index,
)


def write_fixture(project: Path) -> None:
    src = project / "src"
    src.mkdir()
    (src / "service.py").write_text(
        "class Service:\n"
        "    pass\n\n"
        "def retry_request():\n"
        "    return 'retry cache evidence'\n",
        encoding="utf-8",
    )
    (project / "tests").mkdir()
    (project / "tests" / "test_service.py").write_text(
        "from src.service import retry_request\n\n"
        "def test_retry_request():\n"
        "    assert retry_request()\n",
        encoding="utf-8",
    )


def test_context_mcp_tools_run_locally(tmp_path: Path) -> None:
    write_fixture(tmp_path)
    write_context_index(tmp_path, build_context_index(tmp_path))
    write_active_context(tmp_path, file_path="src/service.py", selection="retry_request")

    manifest = context_mcp_manifest(tmp_path)
    search = build_context_mcp_tool_result(tmp_path, "context.search", {"query": "retry cache", "limit": 5})
    related = build_context_mcp_tool_result(tmp_path, "context.related", {"path": "src/service.py", "limit": 5})
    explain = build_context_mcp_tool_result(tmp_path, "context.explain_symbol", {"symbol": "retry_request"})
    active = build_context_mcp_tool_result(tmp_path, "context.active", {})

    assert manifest["schema_version"] == "relay-kit.context-mcp.v1"
    assert {tool["name"] for tool in manifest["tools"]} >= {
        "context.search",
        "context.related",
        "context.explain_symbol",
        "context.active",
    }
    assert search["status"] == "pass"
    assert related["status"] == "pass"
    assert explain["status"] == "pass"
    assert active["active_file"] == "src/service.py"


def test_public_cli_context_mcp_json(capsys, tmp_path: Path) -> None:
    write_fixture(tmp_path)
    relay_kit_public_cli.main(["context", "index", str(tmp_path), "--json"])
    capsys.readouterr()

    code = relay_kit_public_cli.main(["context", "mcp", str(tmp_path), "--tool", "context.search", "--query", "retry", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["schema_version"] == "relay-kit.context-search.v1"
    assert payload["results"]
