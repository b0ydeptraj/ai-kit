from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERIC_MARKERS = (
    "focused AI SDK Expert implementation",
    "touches AI SDK Expert behavior or tooling",
)


def test_template_policy_hides_placeholder_and_generic_expert_shells() -> None:
    policy_path = ROOT / "docs" / "relay-kit-template-policy.json"
    payload = json.loads(policy_path.read_text(encoding="utf-8"))
    templates = payload["templates"]

    assert templates["template-skill"]["status"] == "internal-scaffold"
    assert templates["ai-sdk-expert"]["status"] in {"starter-only", "deferred-scrub"}
    assert templates["ai-sdk-expert"]["public_ready"] is False


def test_public_ready_templates_do_not_contain_generic_expert_markers() -> None:
    policy_path = ROOT / "docs" / "relay-kit-template-policy.json"
    payload = json.loads(policy_path.read_text(encoding="utf-8"))

    offenders: dict[str, list[str]] = {}
    for template_name, entry in payload["templates"].items():
        if not entry.get("public_ready"):
            continue
        skill_path = ROOT / "templates" / "skills" / template_name / "SKILL.md"
        if not skill_path.exists():
            continue
        text = skill_path.read_text(encoding="utf-8")
        markers = [marker for marker in GENERIC_MARKERS if marker in text]
        if markers:
            offenders[template_name] = markers

    assert offenders == {}
