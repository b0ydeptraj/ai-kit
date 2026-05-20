from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3.repo_profile import build_repo_profile


def archetypes(report: dict[str, object]) -> set[str]:
    return {str(item["archetype"]) for item in report.get("archetypes", []) if isinstance(item, dict)}


def test_repo_profile_detects_backend_api(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text(
        "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/login')\ndef login(): return {'ok': True}\n",
        encoding="utf-8",
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_app.py").write_text("def test_login(): assert True\n", encoding="utf-8")

    report = build_repo_profile(tmp_path)

    assert report["schema_version"] == "relay-kit.repo-profile.v1"
    assert "backend-api" in archetypes(report)
    assert report["domain_coverage"] == "known-archetype"
    assert report["unknown_domain_mode"] is False


def test_repo_profile_detects_frontend_cli_database_and_automation(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"scripts":{"dev":"vite"}}\n', encoding="utf-8")
    (tmp_path / "vite.config.ts").write_text("export default {}\n", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "App.tsx").write_text("export function App(){ return <button /> }\n", encoding="utf-8")
    (tmp_path / "cli.py").write_text("import argparse\nargparse.ArgumentParser()\n", encoding="utf-8")
    (tmp_path / "models.py").write_text("class User: pass\n# migration transaction repository\n", encoding="utf-8")
    workflow = tmp_path / ".github" / "workflows"
    workflow.mkdir(parents=True)
    (workflow / "ci.yml").write_text("name: ci\non: push\njobs: {}\n", encoding="utf-8")

    report = build_repo_profile(tmp_path)
    found = archetypes(report)

    assert {"frontend-app", "cli-tool", "database-heavy", "automation-worker"} <= found


def test_repo_profile_unknown_empty_repo(tmp_path: Path) -> None:
    report = build_repo_profile(tmp_path)

    assert report["dominant_archetype"] == "unknown"
    assert report["domain_coverage"] == "unknown"
    assert report["unknown_domain_mode"] is True


def test_public_cli_repo_profile_json(capsys, tmp_path: Path) -> None:
    (tmp_path / "cli.py").write_text("import click\n@click.command()\ndef main(): pass\n", encoding="utf-8")

    code = relay_kit_public_cli.main(["eval", "repo-profile", str(tmp_path), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["schema_version"] == "relay-kit.repo-profile.v1"
    assert "cli-tool" in {item["archetype"] for item in payload["archetypes"]}
