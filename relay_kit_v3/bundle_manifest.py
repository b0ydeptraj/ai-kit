"""Checksummed bundle manifest for Relay-kit registry releases."""

from __future__ import annotations

import hashlib
import json
import tomllib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from relay_kit_v3.generator import BUNDLES
from relay_kit_v3.registry.skills import ALL_V3_SKILLS, render_skill


SCHEMA_VERSION = "relay-kit.bundle-manifest.v1"
TRUST_SCHEMA_VERSION = "relay-kit.bundle-trust.v1"
DEFAULT_OUTPUT = Path(".relay-kit") / "manifest" / "bundles.json"
DEFAULT_TRUST_OUTPUT = Path(".relay-kit") / "manifest" / "trust.json"


@dataclass(frozen=True)
class VerifyResult:
    ok: bool
    findings: list[str]


def create_manifest(*, generated_at: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at or _utc_timestamp(),
        "package": _package_metadata(),
        "skill_count": len(ALL_V3_SKILLS),
        "bundles": {},
    }
    for bundle_name, skill_names in sorted(BUNDLES.items()):
        payload["bundles"][bundle_name] = {
            "skills": list(skill_names),
            "skill_hashes": {name: _skill_hash(name) for name in skill_names},
        }
    payload["manifest_hash"] = manifest_hash(payload)
    return payload


def write_manifest(project_root: Path | str, output_file: Path | str | None = None) -> Path:
    root = Path(project_root).resolve()
    output_path = Path(output_file) if output_file is not None else root / DEFAULT_OUTPUT
    if not output_path.is_absolute():
        output_path = root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(create_manifest(), ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return output_path


def write_trust_stamp(
    project_root: Path | str,
    *,
    manifest_file: Path | str | None = None,
    trust_file: Path | str | None = None,
    issuer: str = "local",
    channel: str = "local",
) -> Path:
    root = Path(project_root).resolve()
    manifest_path = resolve_manifest_path(root, manifest_file)
    try:
        manifest_payload = read_json_object(manifest_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"Cannot read manifest: {exc}") from exc
    manifest_result = verify_manifest_payload(manifest_payload)
    if not manifest_result.ok:
        raise ValueError(f"Cannot stamp invalid manifest: {', '.join(manifest_result.findings)}")

    output_path = Path(trust_file) if trust_file is not None else root / DEFAULT_TRUST_OUTPUT
    if not output_path.is_absolute():
        output_path = root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(create_trust_stamp(manifest_payload, issuer=issuer, channel=channel), ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path


def verify_manifest_file(path: Path | str) -> VerifyResult:
    manifest_path = Path(path)
    try:
        payload = read_json_object(manifest_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return VerifyResult(False, [f"manifest read failed: {exc}"])
    return verify_manifest_payload(payload)


def verify_trusted_manifest_file(
    manifest_file: Path | str,
    trust_file: Path | str | None = None,
) -> VerifyResult:
    manifest_path = Path(manifest_file)
    findings: list[str] = []
    try:
        manifest_payload = read_json_object(manifest_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return VerifyResult(False, [f"manifest read failed: {exc}"])

    findings.extend(verify_manifest_payload(manifest_payload).findings)

    trust_path = Path(trust_file) if trust_file is not None else manifest_path.parent / DEFAULT_TRUST_OUTPUT.name
    if not trust_path.exists():
        findings.append(f"missing trust metadata: {trust_path}")
        return VerifyResult(False, findings)

    try:
        trust_payload = read_json_object(trust_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return VerifyResult(False, findings + [f"trust metadata read failed: {exc}"])

    findings.extend(verify_trust_payload(manifest_payload, trust_payload).findings)
    return VerifyResult(not findings, findings)


def verify_manifest_payload(payload: dict[str, Any]) -> VerifyResult:
    findings: list[str] = []
    if payload.get("schema_version") != SCHEMA_VERSION:
        findings.append(f"schema_version mismatch: {payload.get('schema_version')!r}")

    expected_hash = manifest_hash(payload)
    if payload.get("manifest_hash") != expected_hash:
        findings.append("manifest_hash mismatch")

    bundles = payload.get("bundles")
    if not isinstance(bundles, dict):
        findings.append("bundles must be an object")
        return VerifyResult(False, findings)

    for bundle_name, skill_names in sorted(BUNDLES.items()):
        bundle = bundles.get(bundle_name)
        if not isinstance(bundle, dict):
            findings.append(f"missing bundle: {bundle_name}")
            continue
        if bundle.get("skills") != skill_names:
            findings.append(f"bundle skill list mismatch: {bundle_name}")
        skill_hashes = bundle.get("skill_hashes")
        if not isinstance(skill_hashes, dict):
            findings.append(f"missing skill_hashes for bundle: {bundle_name}")
            continue
        for skill_name in skill_names:
            expected_skill_hash = _skill_hash(skill_name)
            if skill_hashes.get(skill_name) != expected_skill_hash:
                findings.append(f"skill hash mismatch: {bundle_name}/{skill_name}")

    return VerifyResult(not findings, findings)


def create_trust_stamp(
    manifest_payload: dict[str, Any],
    *,
    issuer: str = "local",
    channel: str = "local",
    stamped_at: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": TRUST_SCHEMA_VERSION,
        "trust_model": "deterministic-stamp-not-cryptographic-signature",
        "stamped_at": stamped_at or _utc_timestamp(),
        "issuer": issuer,
        "channel": channel,
        "package": dict(manifest_payload.get("package", {})),
        "manifest_schema_version": manifest_payload.get("schema_version"),
        "manifest_hash": manifest_payload.get("manifest_hash"),
    }
    payload["trust_hash"] = trust_hash(payload)
    return payload


def verify_trust_payload(manifest_payload: dict[str, Any], trust_payload: dict[str, Any]) -> VerifyResult:
    findings: list[str] = []
    if trust_payload.get("schema_version") != TRUST_SCHEMA_VERSION:
        findings.append(f"trust schema_version mismatch: {trust_payload.get('schema_version')!r}")
    if trust_payload.get("trust_model") != "deterministic-stamp-not-cryptographic-signature":
        findings.append("trust_model mismatch")
    if trust_payload.get("trust_hash") != trust_hash(trust_payload):
        findings.append("trust_hash mismatch")
    if trust_payload.get("manifest_schema_version") != manifest_payload.get("schema_version"):
        findings.append("trust manifest_schema_version mismatch")
    if trust_payload.get("manifest_hash") != manifest_payload.get("manifest_hash"):
        findings.append("trust manifest_hash mismatch")
    if trust_payload.get("package") != manifest_payload.get("package"):
        findings.append("trust package metadata mismatch")
    if not str(trust_payload.get("issuer", "")).strip():
        findings.append("trust issuer is required")
    if not str(trust_payload.get("channel", "")).strip():
        findings.append("trust channel is required")
    return VerifyResult(not findings, findings)


def manifest_hash(payload: dict[str, Any]) -> str:
    unsigned = {key: value for key, value in payload.items() if key != "manifest_hash"}
    return hashlib.sha256(_canonical_json(unsigned).encode("utf-8")).hexdigest()


def trust_hash(payload: dict[str, Any]) -> str:
    unsigned = {key: value for key, value in payload.items() if key != "trust_hash"}
    return hashlib.sha256(_canonical_json(unsigned).encode("utf-8")).hexdigest()


def read_json_object(path: Path | str) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("JSON root must be an object")
    return payload


def resolve_manifest_path(project_root: Path, manifest_file: Path | str | None = None) -> Path:
    path = Path(manifest_file) if manifest_file is not None else project_root / DEFAULT_OUTPUT
    if not path.is_absolute():
        path = project_root / path
    return path


def _skill_hash(skill_name: str) -> str:
    return hashlib.sha256(render_skill(ALL_V3_SKILLS[skill_name]).encode("utf-8")).hexdigest()


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _package_metadata() -> dict[str, str]:
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    if not pyproject.exists():
        return {"name": "relay-kit", "version": "unknown"}
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    project = data.get("project", {}) if isinstance(data, dict) else {}
    return {
        "name": str(project.get("name", "relay-kit")),
        "version": str(project.get("version", "unknown")),
    }
