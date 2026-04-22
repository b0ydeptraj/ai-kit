from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_CASE = json.loads(
    (REPO_ROOT / "tests" / "fixtures" / "prompt_fidelity_case_shoes.json").read_text(encoding="utf-8")
)


def _run(*args: str, cwd: Path = REPO_ROOT, expect: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == expect, (
        f"command failed: {args}\n"
        f"expected rc={expect}, got rc={result.returncode}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    return result


def _write_workflow_state_for_edit(project: Path, *, intent_status: str, entity_status: str, fidelity_status: str) -> None:
    state_path = project / ".relay-kit" / "state" / "workflow-state.md"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        "\n".join(
            [
                "# workflow-state",
                "## Intent fidelity lock",
                "- Request class: edit",
                "- Media involved: yes",
                "- Intent-lock required: yes",
                f"- Intent-lock status: {intent_status}",
                "- Entity-lock required: yes",
                f"- Entity-lock status: {entity_status}",
                f"- Prompt-fidelity-check status: {fidelity_status}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_intent_contract(path: Path) -> None:
    allowed = FIXTURE_CASE["allowed"]
    forbidden = FIXTURE_CASE["forbidden"]
    targets = FIXTURE_CASE["target_entities"]
    path.write_text(
        "\n".join(
            [
                "## Primary request",
                f"- {FIXTURE_CASE['asked']}",
                "",
                "## Allowed changes",
                f"- {allowed[0]}",
                f"- {allowed[1]}",
                "",
                "## Forbidden changes",
                f"- {forbidden[0]}",
                f"- {forbidden[1]}",
                f"- {forbidden[2]}",
                f"- {forbidden[3]}",
                "",
                "## Target objects",
                f"- {targets[0]}",
                f"- {targets[1]}",
                "",
                "## Done signal",
                "- Only P2/P7 shoes changed.",
                "",
                "## Ambiguities and holds",
                "- none",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_entity_map(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "## Entity IDs",
                "- P2: left glasses officer",
                "- P7: right bob officer",
                "",
                "## Allowed edit scope",
                "- P2 shoes style only",
                "- P7 shoes style only",
                "",
                "## Forbidden edit scope",
                "- All faces and body positions",
                "",
                "## Ambiguous regions",
                "- none",
                "",
                "## Verification checklist",
                "- No entity count change",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_qa_report(path: Path, verdict: str) -> None:
    path.write_text(
        "\n".join(
            [
                "## Scope checked",
                "- Media edit lane",
                "",
                "## Acceptance coverage",
                "- Covered",
                "",
                "## Risk matrix",
                "- Low",
                "",
                "## Regression surface",
                "- Visual consistency",
                "",
                "## Evidence collected",
                "- Before/after screenshot",
                "",
                "## Asked vs Delivered",
                "| Asked | Delivered |",
                "|---|---|",
                "| Edit P2/P7 shoes only | Matched |",
                "",
                "## Drift verdict (pass/fail + reason)",
                f"- {verdict}: forbidden changes not observed",
                "",
                "## Go / no-go recommendation",
                "- go",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_prompt_fidelity_guard_hard_mode_negative_then_positive(tmp_path: Path) -> None:
    project = tmp_path / "fidelity-hard-sandbox"
    project.mkdir(parents=True, exist_ok=True)

    _run(
        str(REPO_ROOT / "relay_kit.py"),
        str(project),
        "--bundle",
        "baseline",
        "--ai",
        "codex",
        "--emit-contracts",
        "--emit-docs",
        "--emit-reference-templates",
    )

    _write_workflow_state_for_edit(project, intent_status="pass", entity_status="pass", fidelity_status="pass")

    intent_path = project / ".relay-kit" / "contracts" / "intent-contract.md"
    if intent_path.exists():
        intent_path.unlink()

    negative = _run(str(REPO_ROOT / "scripts" / "prompt_fidelity_guard.py"), str(project), "--json", expect=2)
    negative_payload = json.loads(negative.stdout)
    assert negative_payload["status"] == "failed"
    assert negative_payload["findings_count"] > 0

    contracts_dir = project / ".relay-kit" / "contracts"
    _write_intent_contract(contracts_dir / "intent-contract.md")
    _write_entity_map(contracts_dir / "entity-map.md")
    _write_qa_report(contracts_dir / "qa-report.md", verdict="pass")
    _write_workflow_state_for_edit(project, intent_status="pass", entity_status="pass", fidelity_status="pass")

    positive = _run(str(REPO_ROOT / "scripts" / "prompt_fidelity_guard.py"), str(project), "--json", expect=0)
    positive_payload = json.loads(positive.stdout)
    assert positive_payload["status"] == "ok"
    assert positive_payload["findings_count"] == 0
