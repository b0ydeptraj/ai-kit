from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3.battle_audit import build_battle_audit
from relay_kit_v3.registry.skills import ALL_V3_SKILLS


ROOT = Path(__file__).resolve().parents[1]


def test_battle_audit_rejects_generic_resource_fixture(tmp_path: Path) -> None:
    skill_root = tmp_path / "demo-skill"
    (skill_root / "references").mkdir(parents=True)
    (skill_root / "examples").mkdir()
    (skill_root / "evals").mkdir()
    (skill_root / "references" / "demo-skill-operator-contract.md").write_text(
        "Use this contract when a compact request arrives.\n", encoding="utf-8"
    )
    (skill_root / "examples" / "demo-skill-good-output.md").write_text(
        "Good response shape: read first, evidence, residual risk.\n", encoding="utf-8"
    )
    (skill_root / "examples" / "demo-skill-bad-output.md").write_text(
        "Bad response shape: guess from the name.\n", encoding="utf-8"
    )
    (skill_root / "evals" / "demo-skill-cases.json").write_text(
        json.dumps(
            [
                {
                    "id": "demo",
                    "skill": "demo-skill",
                    "task": "Handle a compact request.",
                    "expected_evidence_terms": ["read first"],
                },
                {
                    "id": "demo-2",
                    "skill": "demo-skill",
                    "task": "Review output.",
                    "expected_evidence_terms": ["risk"],
                },
            ]
        ),
        encoding="utf-8",
    )

    report = build_battle_audit(ROOT, resource_root=tmp_path, skill_names=["demo-skill"])

    assert report["status"] == "fail"
    assert report["summary"]["high_findings"] >= 1
    assert any("generic skeleton" in finding["message"] for finding in report["findings"])


def test_current_skill_pack_is_battle_audited_after_hardening() -> None:
    report = build_battle_audit(ROOT)

    assert report["schema_version"] == "relay-kit.battle-audit.v1"
    assert report["summary"]["skill_count"] == len(ALL_V3_SKILLS)
    assert report["summary"]["resource_complete_count"] == len(ALL_V3_SKILLS)
    assert report["status"] == "pass"
    assert report["summary"]["high_findings"] == 0
    assert report["summary"]["medium_findings"] == 0


def test_public_cli_battle_audit_json(capsys) -> None:
    code = relay_kit_public_cli.main(["eval", "battle-audit", str(ROOT), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["schema_version"] == "relay-kit.battle-audit.v1"
    assert payload["status"] == "pass"
