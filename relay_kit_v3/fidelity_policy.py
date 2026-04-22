from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from relay_kit_compat import CANONICAL_ARTIFACT_ROOT


FIDELITY_POLICY_RELATIVE_PATH = Path(CANONICAL_ARTIFACT_ROOT) / "state" / "fidelity-policy.json"
WORKFLOW_STATE_RELATIVE_PATH = Path(CANONICAL_ARTIFACT_ROOT) / "state" / "workflow-state.md"

VALID_GATES = {"off", "warn", "hard"}
VALID_SCOPES = {"all-edits", "media-ui", "media-only"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_fidelity_policy() -> dict[str, Any]:
    return {
        "enabled": True,
        "gate": "hard",
        "scope": "all-edits",
        "updated_at": _utc_now(),
    }


def policy_file(project_root: Path) -> Path:
    return project_root / FIDELITY_POLICY_RELATIVE_PATH


def workflow_state_file(project_root: Path) -> Path:
    return project_root / WORKFLOW_STATE_RELATIVE_PATH


def normalize_fidelity_policy(raw: Mapping[str, Any] | None) -> dict[str, Any]:
    base = default_fidelity_policy()
    if raw is None:
        return base

    enabled = raw.get("enabled")
    gate = raw.get("gate")
    scope = raw.get("scope")
    updated_at = raw.get("updated_at")

    if isinstance(enabled, bool):
        base["enabled"] = enabled
    if isinstance(gate, str) and gate in VALID_GATES:
        base["gate"] = gate
    if isinstance(scope, str) and scope in VALID_SCOPES:
        base["scope"] = scope
    if isinstance(updated_at, str) and updated_at.strip():
        base["updated_at"] = updated_at.strip()

    return base


def load_fidelity_policy(project_root: Path) -> dict[str, Any]:
    path = policy_file(project_root)
    if not path.exists():
        return default_fidelity_policy()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default_fidelity_policy()
    if not isinstance(payload, Mapping):
        return default_fidelity_policy()
    return normalize_fidelity_policy(payload)


def ensure_fidelity_policy(project_root: Path) -> Path:
    path = policy_file(project_root)
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(default_fidelity_policy(), ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def write_fidelity_policy(
    project_root: Path,
    *,
    enabled: bool | None = None,
    gate: str | None = None,
    scope: str | None = None,
) -> dict[str, Any]:
    current = load_fidelity_policy(project_root)
    if enabled is not None:
        current["enabled"] = enabled
    if gate is not None and gate in VALID_GATES:
        current["gate"] = gate
    if scope is not None and scope in VALID_SCOPES:
        current["scope"] = scope
    current["updated_at"] = _utc_now()

    path = policy_file(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(current, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return current


def workflow_marker(project_root: Path, label: str) -> str | None:
    path = workflow_state_file(project_root)
    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(rf"^- {re.escape(label)}:\s*([^\n\r]+)$", content, re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip().lower()


def should_enforce_fidelity(policy: Mapping[str, Any], project_root: Path) -> bool:
    enabled = bool(policy.get("enabled", True))
    gate = str(policy.get("gate", "hard"))
    scope = str(policy.get("scope", "all-edits"))

    if not enabled or gate == "off":
        return False

    request_class = workflow_marker(project_root, "Request class")
    media_involved = workflow_marker(project_root, "Media involved")
    intent_required = workflow_marker(project_root, "Intent-lock required")

    if intent_required in {"yes", "true"}:
        return True

    if scope == "all-edits":
        return request_class == "edit"
    if scope == "media-ui":
        return request_class in {"media-ui", "edit-media"} or media_involved in {"yes", "true"}
    if scope == "media-only":
        return media_involved in {"yes", "true"}
    return False
