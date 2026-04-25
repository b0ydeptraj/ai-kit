from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from relay_kit_v3 import contract_export, contract_import


ROOT = Path(__file__).resolve().parents[1]


def write_file(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return path


def write_contract_file(root: Path, payload: dict) -> Path:
    path = root / "relay-contract.json"
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return path


def sample_payload() -> dict:
    return {
        "schema_version": contract_export.SCHEMA_VERSION,
        "requirements": ["Imported requirement."],
        "acceptance_criteria": ["Imported acceptance."],
        "verification": {
            "steps": ["Run imported verification."],
            "evidence": ["Imported evidence passed."],
        },
        "files": ["relay_kit_v3/contract_import.py"],
        "risks": ["Imported risk."],
    }


def test_contract_import_dry_run_does_not_write_contracts(tmp_path: Path) -> None:
    prd_path = write_file(
        tmp_path / ".relay-kit" / "contracts" / "PRD.md",
        """
        # prd

        ## Functional requirements
        No evidence recorded yet.
        """,
    )
    contract_file = write_contract_file(tmp_path, sample_payload())

    report = contract_import.import_contracts(tmp_path, contract_file=contract_file, apply=False)

    assert report["status"] == "pass"
    assert any(action["status"] == "would-write" for action in report["actions"])
    assert "Imported requirement." not in prd_path.read_text(encoding="utf-8")


def test_contract_import_apply_writes_mapped_contract_sections(tmp_path: Path) -> None:
    contract_file = write_contract_file(tmp_path, sample_payload())

    report = contract_import.import_contracts(tmp_path, contract_file=contract_file, apply=True)

    assert report["status"] == "pass"
    assert any(action["status"] == "written" for action in report["actions"])
    contracts = tmp_path / ".relay-kit" / "contracts"
    assert "- Imported requirement." in (contracts / "PRD.md").read_text(encoding="utf-8")
    assert "- Imported acceptance." in (contracts / "stories" / "story-001.md").read_text(encoding="utf-8")
    assert "- Run imported verification." in (contracts / "tech-spec.md").read_text(encoding="utf-8")
    assert "- Imported evidence passed." in (contracts / "qa-report.md").read_text(encoding="utf-8")


def test_contract_import_preserves_existing_concrete_sections_without_force(tmp_path: Path) -> None:
    prd_path = write_file(
        tmp_path / ".relay-kit" / "contracts" / "PRD.md",
        """
        # prd

        ## Acceptance criteria
        - Existing acceptance.
        """,
    )
    contract_file = write_contract_file(tmp_path, sample_payload())

    report = contract_import.import_contracts(tmp_path, contract_file=contract_file, apply=True)

    assert report["status"] == "hold"
    assert any(action["status"] == "skipped-existing" for action in report["actions"])
    content = prd_path.read_text(encoding="utf-8")
    assert "Existing acceptance." in content
    assert "Imported acceptance." not in content


def test_contract_import_force_overwrites_existing_concrete_sections(tmp_path: Path) -> None:
    prd_path = write_file(
        tmp_path / ".relay-kit" / "contracts" / "PRD.md",
        """
        # prd

        ## Acceptance criteria
        - Existing acceptance.
        """,
    )
    contract_file = write_contract_file(tmp_path, sample_payload())

    report = contract_import.import_contracts(tmp_path, contract_file=contract_file, apply=True, force=True)

    assert report["status"] == "pass"
    content = prd_path.read_text(encoding="utf-8")
    assert "Imported acceptance." in content
    assert "Existing acceptance." not in content


def test_contract_import_rejects_unknown_schema_version(tmp_path: Path) -> None:
    contract_file = write_contract_file(tmp_path, {**sample_payload(), "schema_version": "wrong.schema"})

    report = contract_import.import_contracts(tmp_path, contract_file=contract_file, apply=False)

    assert report["status"] == "fail"
    assert "Unsupported contract schema_version" in report["findings"][0]


def test_public_cli_contract_import_applies_contracts(tmp_path: Path) -> None:
    contract_file = write_contract_file(
        tmp_path,
        {
            **sample_payload(),
            "acceptance_criteria": ["CLI acceptance."],
        },
    )

    result = subprocess.run(
        [
            sys.executable,
            "relay_kit_public_cli.py",
            "contract",
            "import",
            str(tmp_path),
            "--contract-file",
            str(contract_file),
            "--apply",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert "- CLI acceptance." in (
        tmp_path / ".relay-kit" / "contracts" / "stories" / "story-001.md"
    ).read_text(encoding="utf-8")
