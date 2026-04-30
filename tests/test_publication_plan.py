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
    if with_dist:
        dist = root / "dist"
        dist.mkdir()
        (dist / f"relay_kit-{version}-py3-none-any.whl").write_text("wheel\n", encoding="utf-8")
        (dist / f"relay_kit-{version}.tar.gz").write_text("sdist\n", encoding="utf-8")


def write_publication_execution_evidence(root: Path) -> tuple[Path, Path]:
    evidence_dir = root / ".tmp" / "publication"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    twine_check = evidence_dir / "twine-check.txt"
    upload_log = evidence_dir / "upload-log.txt"
    twine_check.write_text("Checking dist/relay_kit-3.3.0.tar.gz: PASSED\n", encoding="utf-8")
    upload_log.write_text("Uploading relay-kit 3.3.0 to PyPI: uploaded\n", encoding="utf-8")
    return twine_check, upload_log


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


def test_publication_evidence_published_when_execution_evidence_exists(tmp_path: Path) -> None:
    write_publication_project(tmp_path)
    twine_check, upload_log = write_publication_execution_evidence(tmp_path)

    report = publication.build_publication_evidence(
        tmp_path,
        channel="pypi",
        ci_url="https://github.com/b0ydeptraj/Relay-kit/actions/runs/1",
        release_url="https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.3.0",
        package_url="https://pypi.org/project/relay-kit/3.3.0/",
        twine_check_file=twine_check,
        upload_log_file=upload_log,
    )

    assert report["schema_version"] == "relay-kit.publication-evidence.v1"
    assert report["status"] == "published"
    assert report["findings"] == []
    artifacts = report["distribution"]["artifacts"]
    assert {artifact["kind"] for artifact in artifacts} == {"wheel", "sdist"}
    assert all(len(artifact["sha256"]) == 64 for artifact in artifacts)
    assert report["checks_by_id"]["twine-check"]["status"] == "pass"
    assert report["checks_by_id"]["upload-log"]["status"] == "pass"


def test_publication_evidence_holds_without_upload_log_or_package_url(tmp_path: Path) -> None:
    write_publication_project(tmp_path)
    twine_check, _upload_log = write_publication_execution_evidence(tmp_path)

    report = publication.build_publication_evidence(
        tmp_path,
        channel="pypi",
        ci_url="https://github.com/b0ydeptraj/Relay-kit/actions/runs/1",
        release_url="https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.3.0",
        twine_check_file=twine_check,
    )

    assert report["status"] == "hold"
    assert {finding["gate"] for finding in report["findings"]} >= {"external-evidence", "upload-log"}


def test_public_cli_publish_evidence_writes_default_artifact(tmp_path: Path, capsys) -> None:
    write_publication_project(tmp_path)
    twine_check, upload_log = write_publication_execution_evidence(tmp_path)

    exit_code = relay_kit_public_cli.main(
        [
            "publish",
            "evidence",
            str(tmp_path),
            "--channel",
            "pypi",
            "--ci-url",
            "https://github.com/b0ydeptraj/Relay-kit/actions/runs/1",
            "--release-url",
            "https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.3.0",
            "--package-url",
            "https://pypi.org/project/relay-kit/3.3.0/",
            "--twine-check-file",
            str(twine_check),
            "--upload-log-file",
            str(upload_log),
            "--strict",
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    output_path = tmp_path / ".relay-kit" / "release" / "publication-evidence.json"

    assert exit_code == 0
    assert payload["output_file"] == str(output_path)
    assert output_path.exists()
    assert payload["evidence"]["schema_version"] == "relay-kit.publication-evidence.v1"
    assert payload["evidence"]["status"] == "published"


def test_publication_trail_builds_capture_commands(tmp_path: Path) -> None:
    write_publication_project(tmp_path, with_dist=False)

    report = publication.build_publication_trail(
        tmp_path,
        channel="pypi",
        ci_url="https://github.com/b0ydeptraj/Relay-kit/actions/runs/1",
        release_url="https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.3.0",
        package_url="https://pypi.org/project/relay-kit/3.3.0/",
        shell="powershell",
    )

    assert report["schema_version"] == "relay-kit.publication-trail.v1"
    assert report["status"] == "ready"
    expected_twine_path = str(Path(".tmp") / "relay-publication" / "3.3.0" / "twine-check.txt")
    assert report["evidence_paths"]["twine_check_file"].endswith(expected_twine_path)
    command_text = "\n".join(step["command"] for step in report["steps"])
    assert "Tee-Object" in command_text
    assert "python -m twine check" in command_text
    assert "python -m twine upload dist/*" in command_text
    assert "relay-kit publish evidence" in command_text


def test_publication_trail_holds_when_external_evidence_urls_are_missing(tmp_path: Path) -> None:
    write_publication_project(tmp_path, with_dist=False)

    report = publication.build_publication_trail(tmp_path, channel="pypi")

    assert report["status"] == "hold"
    assert any(finding["gate"] == "external-evidence" for finding in report["findings"])


def test_public_cli_publish_trail_writes_json_and_markdown(tmp_path: Path, capsys) -> None:
    write_publication_project(tmp_path, with_dist=False)

    exit_code = relay_kit_public_cli.main(
        [
            "publish",
            "trail",
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
    json_path = tmp_path / ".relay-kit" / "release" / "publication-trail.json"
    markdown_path = tmp_path / ".relay-kit" / "release" / "publication-trail.md"

    assert exit_code == 0
    assert payload["output_file"] == str(json_path)
    assert payload["markdown_file"] == str(markdown_path)
    assert json_path.exists()
    assert markdown_path.exists()
    assert payload["trail"]["schema_version"] == "relay-kit.publication-trail.v1"
    assert "relay-kit publish evidence" in markdown_path.read_text(encoding="utf-8")
