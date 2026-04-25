from __future__ import annotations

from pathlib import Path

from relay_kit_v3.registry.skills import ALL_V3_SKILLS, render_skill


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_SKILL_ROOTS = [".codex/skills", ".claude/skills", ".agent/skills"]


def test_completion_canonical_skills_have_non_overlapping_boundaries() -> None:
    qa_governor = render_skill(ALL_V3_SKILLS["qa-governor"])
    evidence_before_completion = render_skill(ALL_V3_SKILLS["evidence-before-completion"])

    assert "readiness verdict" in qa_governor
    assert "go or no-go" in qa_governor
    assert "not a one-claim proof pass" in qa_governor

    assert "claim-to-evidence" in evidence_before_completion
    assert "proof output" in evidence_before_completion
    assert "not a readiness verdict" in evidence_before_completion
    assert "does not own `qa-report.md`" in evidence_before_completion


def test_prove_it_public_alias_delegates_without_becoming_readiness_gate() -> None:
    for root in ADAPTER_SKILL_ROOTS:
        content = (ROOT / root / "prove-it" / "SKILL.md").read_text(encoding="utf-8")

        assert "canonical skill: `evidence-before-completion`" in content, root
        assert "claim-to-evidence" in content, root
        assert "not a readiness verdict" in content, root
        assert "does not write `qa-report.md`" in content, root
