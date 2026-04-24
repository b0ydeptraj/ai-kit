from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from relay_kit_v3 import bundle_manifest


ROOT = Path(__file__).resolve().parents[1]


def test_bundle_manifest_verifies_current_registry() -> None:
    manifest = bundle_manifest.create_manifest()
    result = bundle_manifest.verify_manifest_payload(manifest)

    assert result.ok is True
    assert result.findings == []
    assert manifest["schema_version"] == "relay-kit.bundle-manifest.v1"
    assert "baseline" in manifest["bundles"]
    assert manifest["bundles"]["baseline"]["skills"]
    assert manifest["manifest_hash"]


def test_bundle_manifest_detects_skill_hash_drift() -> None:
    manifest = bundle_manifest.create_manifest()
    manifest["bundles"]["baseline"]["skill_hashes"]["workflow-router"] = "0" * 64

    result = bundle_manifest.verify_manifest_payload(manifest)

    assert result.ok is False
    assert any("workflow-router" in finding for finding in result.findings)


def test_public_cli_manifest_write_and_verify(tmp_path: Path) -> None:
    manifest_path = tmp_path / "bundles.json"
    write_result = subprocess.run(
        [
            sys.executable,
            "relay_kit_public_cli.py",
            "manifest",
            "write",
            str(tmp_path),
            "--output-file",
            str(manifest_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert write_result.returncode == 0, write_result.stdout + write_result.stderr
    assert manifest_path.exists()
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["manifest_hash"]

    verify_result = subprocess.run(
        [
            sys.executable,
            "relay_kit_public_cli.py",
            "manifest",
            "verify",
            str(tmp_path),
            "--manifest-file",
            str(manifest_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert verify_result.returncode == 0, verify_result.stdout + verify_result.stderr
    assert "Manifest verification passed." in verify_result.stdout
