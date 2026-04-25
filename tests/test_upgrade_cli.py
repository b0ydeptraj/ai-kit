from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3 import bundle_manifest, upgrade


def test_upgrade_report_flags_untracked_project(tmp_path: Path) -> None:
    report = upgrade.build_upgrade_report(tmp_path)

    assert report["status"] == "action-required"
    assert report["upgrade_status"] == "untracked"
    assert report["target_version"] == bundle_manifest.create_manifest()["package"]["version"]
    assert any("relay-kit upgrade mark-current" in action for action in report["actions"])


def test_upgrade_mark_current_with_manifest_passes_check(tmp_path: Path) -> None:
    manifest_path = bundle_manifest.write_manifest(tmp_path)
    marker_path = upgrade.write_version_marker(
        tmp_path,
        bundle="baseline",
        adapters=["codex"],
        manifest_file=manifest_path,
    )

    report = upgrade.build_upgrade_report(tmp_path)

    assert marker_path == tmp_path / ".relay-kit" / "version.json"
    assert report["status"] == "pass"
    assert report["upgrade_status"] == "current"
    assert report["manifest_status"] == "valid"
    assert report["installed_version"] == report["target_version"]
    assert report["runtime"]["bundle"] == "baseline"
    assert report["runtime"]["adapters"] == ["codex"]
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    assert marker["manifest"]["path"] == ".relay-kit/manifest/bundles.json"


def test_upgrade_report_detects_old_version(tmp_path: Path) -> None:
    manifest_path = bundle_manifest.write_manifest(tmp_path)
    upgrade.write_version_marker(
        tmp_path,
        bundle="baseline",
        adapters=["codex"],
        manifest_file=manifest_path,
    )
    marker_path = tmp_path / ".relay-kit" / "version.json"
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    marker["package"]["version"] = "0.1.0"
    marker_path.write_text(json.dumps(marker, ensure_ascii=True, indent=2), encoding="utf-8")

    report = upgrade.build_upgrade_report(tmp_path)

    assert report["status"] == "action-required"
    assert report["upgrade_status"] == "upgrade-available"
    assert any("relay-kit init" in action for action in report["actions"])
    assert any("relay-kit doctor" in action for action in report["actions"])


def test_public_cli_upgrade_check_and_mark_current(capsys, tmp_path: Path) -> None:
    bundle_manifest.write_manifest(tmp_path)

    mark_exit = relay_kit_public_cli.main(["upgrade", "mark-current", str(tmp_path), "--adapter", "codex"])
    check_exit = relay_kit_public_cli.main(["upgrade", "check", str(tmp_path), "--strict", "--json"])

    output = capsys.readouterr().out
    payload = json.loads(output[output.index("{") :])

    assert mark_exit == 0
    assert check_exit == 0
    assert "Wrote" in output
    assert payload["status"] == "pass"
    assert payload["upgrade_status"] == "current"
