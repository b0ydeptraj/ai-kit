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
DEFAULT_OUTPUT = Path(".relay-kit") / "manifest" / "bundles.json"


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


def verify_manifest_file(path: Path | str) -> VerifyResult:
    manifest_path = Path(path)
    payload = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        return VerifyResult(False, ["manifest root must be a JSON object"])
    return verify_manifest_payload(payload)


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


def manifest_hash(payload: dict[str, Any]) -> str:
    unsigned = {key: value for key, value in payload.items() if key != "manifest_hash"}
    return hashlib.sha256(_canonical_json(unsigned).encode("utf-8")).hexdigest()


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
