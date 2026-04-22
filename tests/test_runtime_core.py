from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from relay_kit_v3.generator import BUNDLES, generate_relay_bundle
from relay_kit_v3.registry.skills import ALL_V3_SKILLS
from relay_kit_v3.registry.workflows import render_workflow_state


RUNTIME_DIRS = (".claude/skills", ".agent/skills", ".codex/skills")
RUNTIME_ALIAS_SKILLS = {
    "brainstorm",
    "build-it",
    "debug-systematically",
    "prove-it",
    "ready-check",
    "review-pr",
    "start-here",
    "write-steps",
}
ACTIVE_BUNDLE_KEYS = ("round4", "discipline-utilities", "srs-first", "baseline")


def _adapter_skill_sets() -> dict[str, set[str]]:
    skill_sets: dict[str, set[str]] = {}
    for relative in RUNTIME_DIRS:
        root = REPO_ROOT / relative
        skill_sets[relative] = {entry.name for entry in root.iterdir() if entry.is_dir()}
    return skill_sets


def test_reachability_graph_has_no_orphans() -> None:
    inbound = {name: 0 for name in ALL_V3_SKILLS}
    for spec in ALL_V3_SKILLS.values():
        for next_step in spec.next_steps:
            if next_step in inbound:
                inbound[next_step] += 1

    orphans = sorted(name for name, count in inbound.items() if count == 0)
    assert orphans == []


def test_runtime_adapter_parity_uses_exact_equality() -> None:
    adapter_sets = _adapter_skill_sets()
    expected = set(ALL_V3_SKILLS) | RUNTIME_ALIAS_SKILLS

    for relative, current in adapter_sets.items():
        assert current == expected, f"{relative} mismatch"


def test_active_bundle_signatures_are_unique() -> None:
    seen: dict[tuple[str, ...], str] = {}
    for bundle in ACTIVE_BUNDLE_KEYS:
        signature = tuple(sorted(BUNDLES[bundle]))
        other = seen.get(signature)
        assert other is None, f"bundle identity collision: {other} and {bundle}"
        seen[signature] = bundle


def test_generator_uses_relay_naming_surface() -> None:
    assert callable(generate_relay_bundle)

    import relay_kit_v3.generator as generator_module

    assert not hasattr(generator_module, "create_bmad_upgrade")


def test_cli_list_skills_hides_removed_baseline_next() -> None:
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "relay_kit.py"), "--list-skills"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "baseline-next" not in result.stdout


def test_workflow_state_template_has_intent_fidelity_lock_fields() -> None:
    template = render_workflow_state()
    assert "- Request class: unknown" in template
    assert "- Media involved: unknown" in template
    assert "- Intent-lock required: no" in template
    assert "- Entity-lock required: no" in template
    assert "- Prompt-fidelity-check status: not-run" in template
