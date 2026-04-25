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


def test_trusted_manifest_stamp_verifies_manifest(tmp_path: Path) -> None:
    manifest_path = bundle_manifest.write_manifest(tmp_path)
    trust_path = bundle_manifest.write_trust_stamp(tmp_path, manifest_file=manifest_path, issuer="relay-kit-test")

    result = bundle_manifest.verify_trusted_manifest_file(manifest_path, trust_path)

    assert result.ok is True
    assert result.findings == []
    trust_payload = json.loads(trust_path.read_text(encoding="utf-8"))
    assert trust_payload["schema_version"] == "relay-kit.bundle-trust.v1"
    assert trust_payload["issuer"] == "relay-kit-test"
    assert trust_payload["manifest_hash"]
    assert trust_payload["trust_hash"]


def test_trusted_manifest_fails_when_skill_hash_is_tampered(tmp_path: Path) -> None:
    manifest_path = bundle_manifest.write_manifest(tmp_path)
    trust_path = bundle_manifest.write_trust_stamp(tmp_path, manifest_file=manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["bundles"]["baseline"]["skill_hashes"]["workflow-router"] = "0" * 64
    manifest["manifest_hash"] = bundle_manifest.manifest_hash(manifest)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=True, indent=2), encoding="utf-8")

    result = bundle_manifest.verify_trusted_manifest_file(manifest_path, trust_path)

    assert result.ok is False
    assert any("skill hash mismatch" in finding for finding in result.findings)
    assert any("trust manifest_hash mismatch" in finding for finding in result.findings)


def test_trusted_manifest_fails_when_manifest_hash_is_tampered(tmp_path: Path) -> None:
    manifest_path = bundle_manifest.write_manifest(tmp_path)
    trust_path = bundle_manifest.write_trust_stamp(tmp_path, manifest_file=manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["manifest_hash"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=True, indent=2), encoding="utf-8")

    result = bundle_manifest.verify_trusted_manifest_file(manifest_path, trust_path)

    assert result.ok is False
    assert any("manifest_hash mismatch" in finding for finding in result.findings)


def test_trusted_manifest_fails_when_trust_metadata_is_missing(tmp_path: Path) -> None:
    manifest_path = bundle_manifest.write_manifest(tmp_path)

    result = bundle_manifest.verify_trusted_manifest_file(manifest_path)

    assert result.ok is False
    assert any("missing trust metadata" in finding for finding in result.findings)


def test_public_cli_manifest_stamp_and_trusted_verify(tmp_path: Path) -> None:
    write_result = subprocess.run(
        [sys.executable, "relay_kit_public_cli.py", "manifest", "write", str(tmp_path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    stamp_result = subprocess.run(
        [sys.executable, "relay_kit_public_cli.py", "manifest", "stamp", str(tmp_path), "--issuer", "relay-kit-test"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    verify_result = subprocess.run(
        [sys.executable, "relay_kit_public_cli.py", "manifest", "verify", str(tmp_path), "--trusted"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert write_result.returncode == 0, write_result.stdout + write_result.stderr
    assert stamp_result.returncode == 0, stamp_result.stdout + stamp_result.stderr
    assert verify_result.returncode == 0, verify_result.stdout + verify_result.stderr
    assert "Trust verification passed." in verify_result.stdout


def test_public_cli_manifest_stamp_missing_file_fails_cleanly(tmp_path: Path) -> None:
    missing_manifest = tmp_path / "missing.json"

    result = subprocess.run(
        [
            sys.executable,
            "relay_kit_public_cli.py",
            "manifest",
            "stamp",
            str(tmp_path),
            "--manifest-file",
            str(missing_manifest),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "Manifest trust stamp failed:" in result.stdout
    assert "Cannot read manifest" in result.stdout
    assert "Traceback" not in result.stderr


def test_public_cli_manifest_verify_missing_file_fails_cleanly(tmp_path: Path) -> None:
    missing_manifest = tmp_path / "missing.json"

    result = subprocess.run(
        [
            sys.executable,
            "relay_kit_public_cli.py",
            "manifest",
            "verify",
            str(tmp_path),
            "--manifest-file",
            str(missing_manifest),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "Manifest verification failed." in result.stdout
    assert "manifest read failed" in result.stdout
    assert "Traceback" not in result.stderr
