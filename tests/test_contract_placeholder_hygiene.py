from pathlib import Path

from relay_kit_v3.registry.artifacts import ARTIFACT_CONTRACTS, render_artifact
from scripts.runtime_doctor import check_contract_placeholders


ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER = "TBD"


def test_rendered_artifact_contracts_have_no_tbd_markers() -> None:
    for contract in ARTIFACT_CONTRACTS.values():
        text = render_artifact(contract)

        assert PLACEHOLDER not in text, contract.path


def test_checked_in_artifact_contracts_have_no_tbd_markers() -> None:
    for contract_path in (ROOT / ".relay-kit" / "contracts").glob("*.md"):
        text = contract_path.read_text(encoding="utf-8")

        assert PLACEHOLDER not in text, contract_path


def test_runtime_doctor_flags_contract_placeholders_in_live_mode(tmp_path: Path) -> None:
    contract_dir = tmp_path / ".relay-kit" / "contracts"
    contract_dir.mkdir(parents=True)
    (contract_dir / "qa-report.md").write_text("# QA\n\nTBD\n", encoding="utf-8")

    findings: list[str] = []
    check_contract_placeholders(tmp_path, findings, "live")

    assert findings == ["Live contract artifact still contains TBD markers: .relay-kit/contracts/qa-report.md"]


def test_runtime_doctor_allows_contract_placeholders_in_template_mode(tmp_path: Path) -> None:
    contract_dir = tmp_path / ".relay-kit" / "contracts"
    contract_dir.mkdir(parents=True)
    (contract_dir / "qa-report.md").write_text("# QA\n\nTBD\n", encoding="utf-8")

    findings: list[str] = []
    check_contract_placeholders(tmp_path, findings, "template")

    assert findings == []
