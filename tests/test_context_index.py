from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3.context_index import (
    build_context_index,
    build_context_related,
    build_context_search,
    write_context_index,
)


def write_fixture(project: Path) -> None:
    auth_dir = project / "src" / "auth"
    auth_dir.mkdir(parents=True)
    (auth_dir / "LoginForm.tsx").write_text(
        "import { login } from './authService';\n"
        "export function LoginForm() {\n"
        "  return <button onClick={() => login('user')}>Login</button>;\n"
        "}\n",
        encoding="utf-8",
    )
    (auth_dir / "authService.ts").write_text(
        "export async function login(username: string) {\n"
        "  return fetch('/api/login', { method: 'POST', body: username });\n"
        "}\n",
        encoding="utf-8",
    )
    (auth_dir / "login.test.ts").write_text(
        "import { login } from './authService';\n"
        "test('login posts credentials', async () => {\n"
        "  await login('demo');\n"
        "});\n",
        encoding="utf-8",
    )
    (project / "README.md").write_text("# Fixture\n\nLogin flow docs.\n", encoding="utf-8")


def test_context_index_search_and_related_use_real_files(tmp_path: Path) -> None:
    write_fixture(tmp_path)

    index = build_context_index(tmp_path)
    output_path = write_context_index(tmp_path, index)
    search = build_context_search(tmp_path, query="login")
    related = build_context_related(tmp_path, path="src/auth/LoginForm.tsx")

    assert index["schema_version"] == "relay-kit.context-index.v1"
    assert output_path == tmp_path / ".relay-kit" / "context" / "index.json"
    assert search["schema_version"] == "relay-kit.context-search.v1"
    assert search["index_status"] == "available"
    result_paths = {result["path"] for result in search["results"]}
    assert "src/auth/LoginForm.tsx" in result_paths
    assert "src/auth/authService.ts" in result_paths
    assert "src/auth/login.test.ts" in result_paths
    assert related["schema_version"] == "relay-kit.context-related.v1"
    assert "src/auth/login.test.ts" in {result["path"] for result in related["results"]}


def test_context_search_missing_index_is_empty_not_failure(tmp_path: Path) -> None:
    search = build_context_search(tmp_path, query="login")

    assert search["status"] == "empty"
    assert search["index_status"] == "missing"
    assert search["summary"]["reason"] == "missing-index"


def test_public_cli_context_commands(capsys, tmp_path: Path) -> None:
    write_fixture(tmp_path)

    index_code = relay_kit_public_cli.main(["context", "index", str(tmp_path), "--json"])
    index_payload = json.loads(capsys.readouterr().out)
    search_code = relay_kit_public_cli.main(["context", "search", str(tmp_path), "--query", "login", "--json"])
    search_payload = json.loads(capsys.readouterr().out)
    related_code = relay_kit_public_cli.main(
        ["context", "related", str(tmp_path), "--path", "src/auth/LoginForm.tsx", "--json"]
    )
    related_payload = json.loads(capsys.readouterr().out)

    assert index_code == 0
    assert search_code == 0
    assert related_code == 0
    assert index_payload["schema_version"] == "relay-kit.context-index.v1"
    assert search_payload["results"]
    assert related_payload["source"]["path"] == "src/auth/LoginForm.tsx"
