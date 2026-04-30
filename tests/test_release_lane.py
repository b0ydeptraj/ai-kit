from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3 import release_lane


def write_release_lane_project(root: Path) -> None:
    (root / "pyproject.toml").write_text(
        """
[project]
name = "relay-kit"
version = "3.3.0"

[project.scripts]
relay-kit = "relay_kit_public_cli:main"

[tool.setuptools.packages.find]
include = ["relay_kit_v3*", "scripts*"]
        """.strip()
        + "\n",
        encoding="utf-8",
    )
    workflow = root / ".github" / "workflows"
    workflow.mkdir(parents=True, exist_ok=True)
    (workflow / "validate-runtime.yml").write_text(
        "\n".join(
            [
                "python scripts/validate_runtime.py",
                "python scripts/runtime_doctor.py . --strict",
                "python scripts/runtime_doctor.py . --strict --state-mode live",
                "python scripts/migration_guard.py . --strict",
                "python scripts/policy_guard.py . --strict",
                "python scripts/skill_gauntlet.py . --strict --semantic",
                "python scripts/eval_workflows.py . --strict",
                "python relay_kit_public_cli.py doctor . --skip-tests --policy-pack enterprise",
                "python -m pip wheel . --no-deps -w .tmp/wheelhouse",
                "python scripts/package_smoke.py .",
                "python -m pytest tests -q",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    for rel in release_lane.REQUIRED_RELEASE_DOCS:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {path.stem}\n", encoding="utf-8")
    manifest = root / ".relay-kit" / "manifest"
    manifest.mkdir(parents=True, exist_ok=True)
    (manifest / "bundles.json").write_text("{}\n", encoding="utf-8")
    (manifest / "trust.json").write_text("{}\n", encoding="utf-8")
    (root / ".relay-kit" / "version.json").write_text("{}\n", encoding="utf-8")
    support = root / ".relay-kit" / "support"
    support.mkdir(parents=True, exist_ok=True)
    (support / ".gitignore").write_text("support-bundle.json\nsupport-request.json\n", encoding="utf-8")
    signals = root / ".relay-kit" / "signals"
    signals.mkdir(parents=True, exist_ok=True)
    (signals / ".gitignore").write_text(
        "relay-signals.json\nrelay-signals.jsonl\nrelay-signals-otlp.json\n",
        encoding="utf-8",
    )
    release = root / ".relay-kit" / "release"
    release.mkdir(parents=True, exist_ok=True)
    (release / ".gitignore").write_text(
        "publication-evidence.json\npublication-trail.json\npublication-trail.md\n",
        encoding="utf-8",
    )


def test_release_lane_report_passes_complete_project(tmp_path: Path) -> None:
    write_release_lane_project(tmp_path)

    report = release_lane.build_release_lane_report(tmp_path)

    assert report["schema_version"] == "relay-kit.release-lane.v1"
    assert report["status"] == "pass"
    assert report["findings"] == []
    assert {check["id"] for check in report["checks"]} >= {
        "package-metadata",
        "ci-runtime-gates",
        "commercial-docs",
        "release-artifacts",
        "artifact-ignore-policy",
    }


def test_release_lane_report_fails_missing_ci_gate(tmp_path: Path) -> None:
    write_release_lane_project(tmp_path)
    (tmp_path / ".github" / "workflows" / "validate-runtime.yml").write_text(
        "python -m pytest tests -q\n",
        encoding="utf-8",
    )

    report = release_lane.build_release_lane_report(tmp_path)

    assert report["status"] == "fail"
    assert any(finding["gate"] == "ci-runtime-gates" for finding in report["findings"])


def test_release_lane_report_fails_missing_package_smoke(tmp_path: Path) -> None:
    write_release_lane_project(tmp_path)
    workflow = tmp_path / ".github" / "workflows" / "validate-runtime.yml"
    workflow.write_text(
        workflow.read_text(encoding="utf-8").replace("python -m pip wheel . --no-deps -w .tmp/wheelhouse\n", ""),
        encoding="utf-8",
    )

    report = release_lane.build_release_lane_report(tmp_path)

    assert report["status"] == "fail"
    ci_check = next(check for check in report["checks"] if check["id"] == "ci-runtime-gates")
    assert "python -m pip wheel . --no-deps -w .tmp/wheelhouse" in ci_check["details"]["missing"]


def test_release_lane_report_fails_missing_package_install_smoke(tmp_path: Path) -> None:
    write_release_lane_project(tmp_path)
    workflow = tmp_path / ".github" / "workflows" / "validate-runtime.yml"
    workflow.write_text(
        workflow.read_text(encoding="utf-8").replace("python scripts/package_smoke.py .\n", ""),
        encoding="utf-8",
    )

    report = release_lane.build_release_lane_report(tmp_path)

    assert report["status"] == "fail"
    ci_check = next(check for check in report["checks"] if check["id"] == "ci-runtime-gates")
    assert "python scripts/package_smoke.py ." in ci_check["details"]["missing"]


def test_public_cli_release_verify_json(tmp_path: Path, capsys) -> None:
    write_release_lane_project(tmp_path)

    exit_code = relay_kit_public_cli.main(["release", "verify", str(tmp_path), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["schema_version"] == "relay-kit.release-lane.v1"
    assert payload["status"] == "pass"
