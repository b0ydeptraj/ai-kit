from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3 import publication, release_lane


def write_publication_project(root: Path, *, version: str = "3.3.0", with_dist: bool = True) -> None:
    (root / "pyproject.toml").write_text(
        f"""
[project]
name = "relay-kit"
version = "{version}"

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
        "\n".join(release_lane.REQUIRED_CI_PATTERNS) + "\n",
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
    (support / ".gitignore").write_text("support-bundle.json\n", encoding="utf-8")
    signals = root / ".relay-kit" / "signals"
    signals.mkdir(parents=True, exist_ok=True)
    (signals / ".gitignore").write_text(
        "relay-signals.json\nrelay-signals.jsonl\nrelay-signals-otlp.json\n",
        encoding="utf-8",
    )
    if with_dist:
        dist = root / "dist"
        dist.mkdir()
        (dist / f"relay_kit-{version}-py3-none-any.whl").write_text("wheel\n", encoding="utf-8")
        (dist / f"relay_kit-{version}.tar.gz").write_text("sdist\n", encoding="utf-8")


def test_publication_plan_ready_when_release_dist_and_external_evidence_exist(tmp_path: Path) -> None:
    write_publication_project(tmp_path)

    report = publication.build_publication_plan(
        tmp_path,
        channel="pypi",
        ci_url="https://github.com/b0ydeptraj/Relay-kit/actions/runs/1",
        release_url="https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.3.0",
        package_url="https://pypi.org/project/relay-kit/3.3.0/",
    )

    assert report["schema_version"] == "relay-kit.publication-plan.v1"
    assert report["status"] == "ready"
    assert report["version"] == "3.3.0"
    assert report["findings"] == []
    assert {check["id"] for check in report["checks"]} >= {
        "package-metadata",
        "version-channel",
        "release-lane",
        "distribution-artifacts",
        "external-evidence",
    }


def test_publication_plan_holds_dev_version_on_pypi_without_override(tmp_path: Path) -> None:
    write_publication_project(tmp_path, version="3.4.0.dev0")

    report = publication.build_publication_plan(
        tmp_path,
        channel="pypi",
        ci_url="https://github.com/b0ydeptraj/Relay-kit/actions/runs/1",
        release_url="https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.4.0",
        package_url="https://pypi.org/project/relay-kit/3.4.0/",
    )

    assert report["status"] == "hold"
    assert any(finding["gate"] == "version-channel" for finding in report["findings"])


def test_publication_plan_holds_without_distribution_artifacts(tmp_path: Path) -> None:
    write_publication_project(tmp_path, with_dist=False)

    report = publication.build_publication_plan(
        tmp_path,
        channel="pypi",
        ci_url="https://github.com/b0ydeptraj/Relay-kit/actions/runs/1",
        release_url="https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.3.0",
        package_url="https://pypi.org/project/relay-kit/3.3.0/",
    )

    assert report["status"] == "hold"
    dist_check = next(check for check in report["checks"] if check["id"] == "distribution-artifacts")
    assert dist_check["status"] == "hold"
    assert "wheel" in dist_check["details"]["missing"]
    assert "sdist" in dist_check["details"]["missing"]


def test_public_cli_publish_plan_json_and_strict(tmp_path: Path, capsys) -> None:
    write_publication_project(tmp_path, with_dist=False)

    exit_code = relay_kit_public_cli.main(
        [
            "publish",
            "plan",
            str(tmp_path),
            "--channel",
            "pypi",
            "--ci-url",
            "https://github.com/b0ydeptraj/Relay-kit/actions/runs/1",
            "--release-url",
            "https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.3.0",
            "--package-url",
            "https://pypi.org/project/relay-kit/3.3.0/",
            "--strict",
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert payload["schema_version"] == "relay-kit.publication-plan.v1"
    assert payload["status"] == "hold"
