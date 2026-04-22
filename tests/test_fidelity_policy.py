from __future__ import annotations

import json
from pathlib import Path

from relay_kit_v3.fidelity_policy import (
    default_fidelity_policy,
    ensure_fidelity_policy,
    load_fidelity_policy,
    policy_file,
    should_enforce_fidelity,
    write_fidelity_policy,
)


def _write_workflow_state(project: Path, request_class: str, media_involved: str = "no", intent_required: str = "yes") -> None:
    state_path = project / ".relay-kit" / "state" / "workflow-state.md"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        "\n".join(
            [
                "# workflow-state",
                "## Intent fidelity lock",
                f"- Request class: {request_class}",
                f"- Media involved: {media_involved}",
                f"- Intent-lock required: {intent_required}",
                "- Intent-lock status: pass",
                "- Entity-lock required: no",
                "- Entity-lock status: pass",
                "- Prompt-fidelity-check status: pass",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_default_fidelity_policy_is_hard_all_edits_enabled() -> None:
    policy = default_fidelity_policy()
    assert policy["enabled"] is True
    assert policy["gate"] == "hard"
    assert policy["scope"] == "all-edits"


def test_load_and_write_fidelity_policy_round_trip(tmp_path: Path) -> None:
    project = tmp_path / "policy-project"
    project.mkdir()

    created = ensure_fidelity_policy(project)
    assert created == policy_file(project)
    loaded = load_fidelity_policy(project)
    assert loaded["enabled"] is True
    assert loaded["gate"] == "hard"
    assert loaded["scope"] == "all-edits"

    updated = write_fidelity_policy(project, enabled=False, gate="warn", scope="media-ui")
    assert updated["enabled"] is False
    assert updated["gate"] == "warn"
    assert updated["scope"] == "media-ui"

    reloaded = json.loads(policy_file(project).read_text(encoding="utf-8"))
    assert reloaded["enabled"] is False
    assert reloaded["gate"] == "warn"
    assert reloaded["scope"] == "media-ui"


def test_should_enforce_fidelity_depends_on_scope_and_workflow_markers(tmp_path: Path) -> None:
    project = tmp_path / "enforce-project"
    project.mkdir()
    ensure_fidelity_policy(project)

    _write_workflow_state(project, request_class="read-only", media_involved="no", intent_required="no")
    policy = load_fidelity_policy(project)
    assert should_enforce_fidelity(policy, project) is False

    _write_workflow_state(project, request_class="edit", media_involved="no", intent_required="yes")
    assert should_enforce_fidelity(policy, project) is True

    write_fidelity_policy(project, scope="media-only")
    media_only = load_fidelity_policy(project)
    _write_workflow_state(project, request_class="edit", media_involved="no", intent_required="no")
    assert should_enforce_fidelity(media_only, project) is False
    _write_workflow_state(project, request_class="edit", media_involved="yes", intent_required="no")
    assert should_enforce_fidelity(media_only, project) is True
