from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from relay_kit_compat import CANONICAL_ARTIFACT_ROOT


SRS_POLICY_RELATIVE_PATH = Path(CANONICAL_ARTIFACT_ROOT) / "state" / "srs-policy.json"
WORKFLOW_STATE_RELATIVE_PATH = Path(CANONICAL_ARTIFACT_ROOT) / "state" / "workflow-state.md"

VALID_GATES = {"off", "warn", "hard"}
VALID_SCOPES = {"product-enterprise", "all"}
VALID_RISK_PROFILES = {"normal", "high"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_srs_policy() -> dict[str, Any]:
    return {
        "enabled": False,
        "scope": "product-enterprise",
        "gate": "off",
        "risk_profile": "normal",
        "updated_at": utc_now(),
    }


def policy_file(project_root: Path) -> Path:
    return project_root / SRS_POLICY_RELATIVE_PATH


def workflow_state_file(project_root: Path) -> Path:
    return project_root / WORKFLOW_STATE_RELATIVE_PATH


def normalize_srs_policy(raw: Mapping[str, Any] | None) -> dict[str, Any]:
    base = default_srs_policy()
    if raw is None:
        return base

    enabled = raw.get("enabled")
    scope = raw.get("scope")
    gate = raw.get("gate")
    risk_profile = raw.get("risk_profile")
    updated_at = raw.get("updated_at")

    if isinstance(enabled, bool):
        base["enabled"] = enabled
    if isinstance(scope, str) and scope in VALID_SCOPES:
        base["scope"] = scope
    if isinstance(gate, str) and gate in VALID_GATES:
        base["gate"] = gate
    if isinstance(risk_profile, str) and risk_profile in VALID_RISK_PROFILES:
        base["risk_profile"] = risk_profile
    if isinstance(updated_at, str) and updated_at.strip():
        base["updated_at"] = updated_at.strip()

    return base


def load_srs_policy(project_root: Path) -> dict[str, Any]:
    path = policy_file(project_root)
    if not path.exists():
        return default_srs_policy()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default_srs_policy()
    if not isinstance(payload, Mapping):
        return default_srs_policy()
    return normalize_srs_policy(payload)


def ensure_srs_policy(project_root: Path) -> Path:
    path = policy_file(project_root)
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(default_srs_policy(), ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return path


def write_srs_policy(
    project_root: Path,
    *,
    enabled: bool | None = None,
    scope: str | None = None,
    gate: str | None = None,
    risk_profile: str | None = None,
) -> dict[str, Any]:
    current = load_srs_policy(project_root)
    if enabled is not None:
        current["enabled"] = enabled
    if scope is not None and scope in VALID_SCOPES:
        current["scope"] = scope
    if gate is not None and gate in VALID_GATES:
        current["gate"] = gate
    if risk_profile is not None and risk_profile in VALID_RISK_PROFILES:
        current["risk_profile"] = risk_profile
    current["updated_at"] = utc_now()

    path = policy_file(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(current, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return current


def track_from_workflow_state(project_root: Path) -> str | None:
    path = workflow_state_file(project_root)
    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"^- Track:\s*([^\n\r]+)$", content, re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip()


def should_enforce_srs(policy: Mapping[str, Any], project_root: Path) -> bool:
    enabled = bool(policy.get("enabled", False))
    gate = str(policy.get("gate", "off"))
    scope = str(policy.get("scope", "product-enterprise"))

    if not enabled or gate == "off":
        return False
    if scope == "all":
        return True

    track = track_from_workflow_state(project_root)
    if track in {"product-flow", "enterprise-flow"}:
        return True
    if track == "quick-flow":
        return False

    prd = project_root / CANONICAL_ARTIFACT_ROOT / "contracts" / "PRD.md"
    stories_dir = project_root / CANONICAL_ARTIFACT_ROOT / "contracts" / "stories"
    if prd.exists():
        return True
    if stories_dir.exists() and any(stories_dir.glob("*.md")):
        return True
    return False
