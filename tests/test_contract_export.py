from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from relay_kit_v3 import contract_export


ROOT = Path(__file__).resolve().parents[1]


def write_artifact(root: Path, rel_path: str, content: str) -> Path:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return path


def test_contract_export_collects_acceptance_and_verification(tmp_path: Path) -> None:
    write_artifact(
        tmp_path,
        ".relay-kit/contracts/stories/story-001.md",
        """
        # story

        ## Story statement
        As a maintainer, I can export a machine-readable story contract.

        ## Acceptance criteria
        - Export includes acceptance criteria.
        - Export includes verification steps.

        ## Test notes
        - Run `python -m pytest tests/test_contract_export.py -q`.
        """,
    )
    write_artifact(
        tmp_path,
        ".relay-kit/contracts/qa-report.md",
        """
        # qa-report

        ## Acceptance coverage
        - Both criteria covered by unit tests.

        ## Evidence collected
        - `python -m pytest tests/test_contract_export.py -q` passed.
        """,
    )

    payload = contract_export.export_contracts(tmp_path)

    assert payload["schema_version"] == "relay-kit.contract-export.v1"
    assert payload["verification_ready"] is True
    assert payload["acceptance_criteria"] == [
        "Export includes acceptance criteria.",
        "Export includes verification steps.",
    ]
    assert payload["verification"]["evidence"] == [
        "`python -m pytest tests/test_contract_export.py -q` passed."
    ]
    assert payload["source_files"][0]["sha256"]


def test_contract_export_marks_placeholder_contract_not_ready(tmp_path: Path) -> None:
    write_artifact(
        tmp_path,
        ".relay-kit/contracts/stories/story-001.md",
        """
        # story

        ## Acceptance criteria
        TBD
        """,
    )

    payload = contract_export.export_contracts(tmp_path)

    assert payload["verification_ready"] is False
    assert "acceptance_criteria" in payload["missing_fields"]
    assert "verification_evidence" in payload["missing_fields"]


def test_contract_export_ignores_template_instruction_lines(tmp_path: Path) -> None:
    write_artifact(
        tmp_path,
        ".relay-kit/contracts/PRD.md",
        """
        # prd

        ## Functional requirements
        List numbered requirements with user-facing intent.

        ## Acceptance criteria
        Concrete pass/fail conditions tied to scope.
        """,
    )

    payload = contract_export.export_contracts(tmp_path)

    assert payload["requirements"] == []
    assert payload["acceptance_criteria"] == []
    assert "acceptance_criteria" in payload["missing_fields"]


def test_public_cli_contract_export_writes_json(tmp_path: Path) -> None:
    write_artifact(
        tmp_path,
        ".relay-kit/contracts/stories/story-001.md",
        """
        # story

        ## Acceptance criteria
        - Export produces JSON.

        ## Test notes
        - CLI smoke test passed.
        """,
    )
    output = tmp_path / "export.json"

    result = subprocess.run(
        [
            sys.executable,
            "relay_kit_public_cli.py",
            "contract",
            "export",
            str(tmp_path),
            "--output-file",
            str(output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["project_path"] == str(tmp_path.resolve())
    assert payload["acceptance_criteria"] == ["Export produces JSON."]
