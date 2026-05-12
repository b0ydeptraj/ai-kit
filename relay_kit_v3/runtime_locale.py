from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from relay_kit_compat import CANONICAL_ARTIFACT_ROOT


SCHEMA_VERSION = "relay-kit.runtime-locale.v1"
REPORT_SCHEMA_VERSION = "relay-kit.runtime-locale-report.v1"
RUNTIME_LOCALE_RELATIVE_PATH = Path(CANONICAL_ARTIFACT_ROOT) / "state" / "runtime-locale.json"

DEFAULT_LOCALE = "en"
SUPPORTED_RUNTIME_LOCALES = {"en", "vi"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def runtime_locale_file(project_root: Path) -> Path:
    return project_root / RUNTIME_LOCALE_RELATIVE_PATH


def default_runtime_locale() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "locale_profile": DEFAULT_LOCALE,
        "fallback_locale": DEFAULT_LOCALE,
        "enforce_output_language": True,
        "updated_at": utc_now(),
    }


def normalize_locale_code(value: str | None) -> str:
    if value is None:
        return DEFAULT_LOCALE
    candidate = str(value).strip().lower()
    if not candidate:
        return DEFAULT_LOCALE
    return candidate


def is_valid_locale_code(value: str | None) -> bool:
    if value is None:
        return False
    return normalize_locale_code(value) in SUPPORTED_RUNTIME_LOCALES


def normalize_runtime_locale(raw: Mapping[str, Any] | None) -> dict[str, Any]:
    base = default_runtime_locale()
    if raw is None:
        return base

    locale_value = raw.get("locale_profile", raw.get("locale"))
    fallback_value = raw.get("fallback_locale", raw.get("fallback"))
    enforce_value = raw.get("enforce_output_language")
    updated_at = raw.get("updated_at")

    locale_profile = normalize_locale_code(str(locale_value) if locale_value is not None else None)
    fallback_locale = normalize_locale_code(str(fallback_value) if fallback_value is not None else None)

    if is_valid_locale_code(locale_profile):
        base["locale_profile"] = locale_profile
    if is_valid_locale_code(fallback_locale):
        base["fallback_locale"] = fallback_locale
    if isinstance(enforce_value, bool):
        base["enforce_output_language"] = enforce_value
    if isinstance(updated_at, str) and updated_at.strip():
        base["updated_at"] = updated_at.strip()

    return base


def load_runtime_locale(project_root: Path) -> dict[str, Any]:
    path = runtime_locale_file(project_root)
    if not path.exists():
        return default_runtime_locale()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default_runtime_locale()
    if not isinstance(payload, Mapping):
        return default_runtime_locale()
    return normalize_runtime_locale(payload)


def ensure_runtime_locale(project_root: Path) -> Path:
    path = runtime_locale_file(project_root)
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(default_runtime_locale(), ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return path


def write_runtime_locale(
    project_root: Path,
    *,
    locale: str | None = None,
    fallback_locale: str | None = None,
    enforce_output_language: bool | None = None,
) -> dict[str, Any]:
    current = load_runtime_locale(project_root)

    if locale is not None:
        normalized_locale = normalize_locale_code(locale)
        if not is_valid_locale_code(normalized_locale):
            raise ValueError(f"Invalid locale value: {locale!r}")
        current["locale_profile"] = normalized_locale
    if fallback_locale is not None:
        normalized_fallback = normalize_locale_code(fallback_locale)
        if not is_valid_locale_code(normalized_fallback):
            raise ValueError(f"Invalid fallback locale value: {fallback_locale!r}")
        current["fallback_locale"] = normalized_fallback
    if enforce_output_language is not None:
        current["enforce_output_language"] = bool(enforce_output_language)
    current["updated_at"] = utc_now()
    current["schema_version"] = SCHEMA_VERSION

    path = runtime_locale_file(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(current, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return current


def inspect_runtime_locale(project_root: Path | str) -> dict[str, Any]:
    root = Path(project_root).resolve()
    path = runtime_locale_file(root)
    findings: list[dict[str, str]] = []

    if not path.exists():
        findings.append(
            {
                "id": "missing-runtime-locale",
                "path": str(RUNTIME_LOCALE_RELATIVE_PATH).replace("\\", "/"),
                "summary": "missing runtime locale policy file",
            }
        )
        normalized = default_runtime_locale()
        return {
            "schema_version": REPORT_SCHEMA_VERSION,
            "status": "hold",
            "project_path": str(root),
            "file": str(path),
            "summary": {
                "file_exists": False,
                "locale_profile": normalized["locale_profile"],
                "fallback_locale": normalized["fallback_locale"],
                "enforce_output_language": normalized["enforce_output_language"],
                "findings": len(findings),
            },
            "findings": findings,
            "runtime_locale": normalized,
        }

    payload: Mapping[str, Any] | None = None
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(parsed, Mapping):
            payload = parsed
        else:
            findings.append(
                {
                    "id": "invalid-runtime-locale",
                    "path": str(RUNTIME_LOCALE_RELATIVE_PATH).replace("\\", "/"),
                    "summary": "runtime locale file must contain a JSON object",
                }
            )
    except json.JSONDecodeError as exc:
        findings.append(
            {
                "id": "invalid-runtime-locale-json",
                "path": str(RUNTIME_LOCALE_RELATIVE_PATH).replace("\\", "/"),
                "summary": f"runtime locale JSON parse failed: {exc.msg}",
            }
        )

    if payload is None:
        normalized = default_runtime_locale()
    else:
        schema = payload.get("schema_version")
        if schema != SCHEMA_VERSION:
            findings.append(
                {
                    "id": "runtime-locale-schema-drift",
                    "path": str(RUNTIME_LOCALE_RELATIVE_PATH).replace("\\", "/"),
                    "summary": f"runtime locale schema drift: expected {SCHEMA_VERSION}, found {schema!r}",
                }
            )
        raw_locale = payload.get("locale_profile", payload.get("locale"))
        raw_fallback = payload.get("fallback_locale", payload.get("fallback"))
        if not isinstance(raw_locale, str) or not is_valid_locale_code(raw_locale):
            findings.append(
                {
                    "id": "invalid-locale-profile",
                    "path": str(RUNTIME_LOCALE_RELATIVE_PATH).replace("\\", "/"),
                    "summary": "locale_profile must be one of: en, vi",
                }
            )
        if not isinstance(raw_fallback, str) or not is_valid_locale_code(raw_fallback):
            findings.append(
                {
                    "id": "invalid-fallback-locale",
                    "path": str(RUNTIME_LOCALE_RELATIVE_PATH).replace("\\", "/"),
                    "summary": "fallback_locale must be one of: en, vi",
                }
            )
        normalized = normalize_runtime_locale(payload)

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "status": "hold" if findings else "pass",
        "project_path": str(root),
        "file": str(path),
        "summary": {
            "file_exists": True,
            "locale_profile": normalized["locale_profile"],
            "fallback_locale": normalized["fallback_locale"],
            "enforce_output_language": normalized["enforce_output_language"],
            "findings": len(findings),
        },
        "findings": findings,
        "runtime_locale": normalized,
    }
