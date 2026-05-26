"""Claim calibration gate for Relay-kit proof surfaces."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from relay_kit_v3.battle_audit import build_battle_audit
from relay_kit_v3.real_world_eval import build_report as build_real_world_eval_report
from relay_kit_v3.skill_proof import build_report as build_skill_proof_report


SCHEMA_VERSION = "relay-kit.signal-calibration.v1"
DEFAULT_OUTPUT = Path(".relay-kit") / "eval" / "signal-calibration.json"
VALID_MODES = {"claims", "skill", "readiness"}

OVERCLAIM_PATTERNS: tuple[tuple[str, str], ...] = (
    ("field-tested", r"\bfield[- ]tested\b|\bthuc chien\b|\bthuc te da chay\b"),
    ("real-world-proven", r"\breal[- ]world proven\b|\bproven in real\b"),
    ("production-ready", r"\bproduction[- ]ready\b|\bprod[- ]ready\b"),
    ("commercial-ready", r"\bcommercial[- ]ready\b|\bpaid[- ]ready\b"),
    ("expert-guarantee", r"\bexpert guarantee\b|\bguaranteed expert\b|\bchac chan\b"),
)

EVIDENCE_HINTS = (
    "pytest",
    "test",
    "runtime_doctor",
    "skill_gauntlet",
    "readiness",
    "proof",
    "artifact",
    "log",
    ".json",
    ".md",
    ".py",
    "file:",
    "http",
)


def build_report(
    project_root: Path | str,
    *,
    mode: str = "readiness",
    claims: Sequence[str] | None = None,
    claim_file: Path | str | None = None,
    skill: str = "all",
    strict: bool = False,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    selected_mode = _normalize_mode(mode)
    proof_report = build_skill_proof_report(root)
    real_world_report = build_real_world_eval_report(root)
    battle_report = build_battle_audit(root)

    claim_rows: list[dict[str, Any]] = []
    if selected_mode == "claims":
        claim_rows.extend(
            _explicit_claims(
                root,
                _claim_inputs(root, claims=claims, claim_file=claim_file),
                proof_report=proof_report,
            )
        )
    elif selected_mode == "skill":
        claim_rows.extend(_skill_claims(proof_report, skill=skill))
    else:
        claim_rows.extend(_readiness_claims(proof_report, real_world_report, battle_report))

    findings = _findings_from_claims(claim_rows)
    summary = _summary(claim_rows, findings)
    status = "fail" if strict and summary["blocked_claims"] else "pass"
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "mode": selected_mode,
        "project_path": str(root),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "claims": claim_rows,
        "findings": findings,
        "source_reports": {
            "skill_proof": {
                "schema_version": proof_report.get("schema_version"),
                "status": proof_report.get("status"),
                "summary": proof_report.get("summary", {}),
            },
            "real_world_skill_eval": {
                "schema_version": real_world_report.get("schema_version"),
                "status": real_world_report.get("status"),
                "case_count": real_world_report.get("case_count", 0),
                "passed": real_world_report.get("passed", 0),
                "failed": real_world_report.get("failed", 0),
            },
            "battle_audit": {
                "schema_version": battle_report.get("schema_version"),
                "status": battle_report.get("status"),
                "summary": battle_report.get("summary", {}),
            },
        },
    }


def write_report(project_root: Path | str, report: Mapping[str, Any], output_file: Path | str | None = None) -> Path:
    root = Path(project_root).resolve()
    target = Path(output_file) if output_file else root / DEFAULT_OUTPUT
    if not target.is_absolute():
        target = root / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return target


def render_report(report: Mapping[str, Any]) -> str:
    summary = _mapping(report.get("summary"))
    lines = [
        "Relay-kit signal calibration",
        f"- status: {report.get('status')}",
        f"- mode: {report.get('mode')}",
        f"- claims: {summary.get('claim_count', 0)}",
        f"- proven: {summary.get('proven_claims', 0)}",
        f"- unsupported: {summary.get('unsupported_claims', 0)}",
        f"- blocked: {summary.get('blocked_claims', 0)}",
        f"- field-tested: {summary.get('field_tested_claims', 0)}",
    ]
    for finding in list(report.get("findings", []))[:12]:
        if isinstance(finding, Mapping):
            lines.append(f"  - {finding.get('check')}: {finding.get('summary')}")
    return "\n".join(lines)


def _normalize_mode(mode: str) -> str:
    value = str(mode).strip().lower()
    if value not in VALID_MODES:
        raise ValueError(f"Unknown signal calibration mode: {mode}")
    return value


def _claim_inputs(
    root: Path,
    *,
    claims: Sequence[str] | None,
    claim_file: Path | str | None,
) -> list[str]:
    values = [str(claim).strip() for claim in claims or [] if str(claim).strip()]
    if claim_file is None:
        return values
    path = Path(claim_file)
    if not path.is_absolute():
        path = root / path
    text = path.read_text(encoding="utf-8")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        values.extend(line.strip("- ").strip() for line in text.splitlines() if line.strip("- ").strip())
        return values
    if isinstance(payload, list):
        values.extend(str(item).strip() for item in payload if str(item).strip())
    elif isinstance(payload, Mapping):
        raw_claims = payload.get("claims", [])
        if isinstance(raw_claims, list):
            values.extend(str(item).strip() for item in raw_claims if str(item).strip())
    return values


def _explicit_claims(root: Path, claims: Sequence[str], *, proof_report: Mapping[str, Any]) -> list[dict[str, Any]]:
    if not claims:
        return [
            _claim(
                claim="No explicit claims supplied for calibration.",
                claim_type="operator_input",
                proof_level="none",
                verdict="inferred",
                confidence="low",
                evidence_sources=[],
                residual_risk="No claim text was provided, so Relay-kit cannot prove or disprove operator wording.",
                next_verification="Pass --claim or --claim-file with the exact wording to calibrate.",
            )
        ]
    return [_classify_explicit_claim(root, claim, proof_report=proof_report) for claim in claims]


def _classify_explicit_claim(root: Path, claim_text: str, *, proof_report: Mapping[str, Any]) -> dict[str, Any]:
    flags = _overclaim_flags(claim_text)
    sources = _evidence_hints(claim_text)
    field_count = int(_mapping(proof_report.get("summary")).get("field_tested", 0) or 0)
    skill_count = int(_mapping(proof_report.get("summary")).get("skill_count", 0) or 0)
    all_field_tested = skill_count > 0 and field_count == skill_count

    if "field-tested" in flags or "real-world-proven" in flags:
        if all_field_tested:
            return _claim(
                claim=claim_text,
                claim_type="field_validation",
                proof_level="field-tested",
                verdict="proven",
                confidence="high",
                evidence_sources=_all_field_sources(proof_report),
                overclaim_flags=flags,
                residual_risk="Field evidence exists for every canonical skill, but current operator context may still need task-specific proof.",
                next_verification="Attach current field evidence ids to the final answer or release artifact.",
            )
        return _claim(
            claim=claim_text,
            claim_type="field_validation",
            proof_level="none",
            verdict="unsupported",
            confidence="blocked",
            evidence_sources=sources,
            overclaim_flags=flags,
            residual_risk="Fixture validation is not field evidence.",
            next_verification="Add .relay-kit/evidence/skill-field-evidence.json entries before using field-tested wording.",
        )

    if "commercial-ready" in flags or "production-ready" in flags:
        return _claim(
            claim=claim_text,
            claim_type="readiness",
            proof_level="runtime-validated" if sources else "none",
            verdict="partially-proven" if sources else "unsupported",
            confidence="blocked",
            evidence_sources=sources,
            overclaim_flags=flags,
            residual_risk="Local runtime evidence does not prove external release, support, or field validation.",
            next_verification="Attach readiness, CI, release, support, package-index, and field evidence before using this claim.",
        )

    if not sources:
        return _claim(
            claim=claim_text,
            claim_type="general",
            proof_level="none",
            verdict="inferred",
            confidence="low",
            evidence_sources=[],
            overclaim_flags=flags,
            residual_risk="The claim does not name a concrete file, command, log, source, or artifact.",
            next_verification="Map this claim to a command output, artifact path, or source citation.",
        )

    return _claim(
        claim=claim_text,
        claim_type="general",
        proof_level="runtime-validated",
        verdict="partially-proven",
        confidence="medium",
        evidence_sources=sources,
        overclaim_flags=flags,
        residual_risk="Evidence hints exist, but the calibration gate did not execute those commands.",
        next_verification="Run the cited checks and attach fresh output before claiming proven.",
    )


def _skill_claims(proof_report: Mapping[str, Any], *, skill: str) -> list[dict[str, Any]]:
    records = [record for record in proof_report.get("skills", []) if isinstance(record, Mapping)]
    selected = records if skill == "all" else [record for record in records if record.get("skill") == skill]
    if not selected and skill != "all":
        return [
            _claim(
                claim=f"Skill `{skill}` exists in the Relay-kit proof report.",
                claim_type="skill_quality",
                proof_level="none",
                verdict="unsupported",
                confidence="blocked",
                evidence_sources=[],
                residual_risk="The requested skill was not found in the proof report.",
                next_verification="Check the canonical registry skill name.",
            )
        ]
    return [_claim_from_skill_record(record) for record in selected]


def _claim_from_skill_record(record: Mapping[str, Any]) -> dict[str, Any]:
    skill_name = str(record.get("skill", ""))
    status = str(record.get("status", "theoretical"))
    sources = [str(item) for item in record.get("proof_sources", []) if str(item)]
    if status == "field-tested":
        proof_level = "field-tested"
        verdict = "proven"
        confidence = "high"
        residual = "Field evidence exists; still attach the exact evidence id when making a task-specific claim."
    elif status == "validated":
        proof_level = "real-world-fixture" if any(source.startswith("real-world-case:") for source in sources) else "synthetic-validated"
        verdict = "proven"
        confidence = "high" if proof_level == "real-world-fixture" else "medium"
        residual = "This proves fixture/runtime validation, not external field use."
    else:
        proof_level = "none"
        verdict = "unsupported"
        confidence = "blocked"
        residual = str(record.get("missing_proof_reason", "No validation evidence found."))
    return _claim(
        claim=f"Skill `{skill_name}` proof level is {proof_level}.",
        claim_type="skill_quality",
        proof_level=proof_level,
        verdict=verdict,
        confidence=confidence,
        evidence_sources=sources,
        residual_risk=residual,
        next_verification="Add field evidence before claiming field-tested." if proof_level != "field-tested" else "Attach field evidence id to the claim.",
    )


def _readiness_claims(
    proof_report: Mapping[str, Any],
    real_world_report: Mapping[str, Any],
    battle_report: Mapping[str, Any],
) -> list[dict[str, Any]]:
    claims = [
        _aggregate_skill_validation_claim(proof_report),
        _real_world_fixture_claim(real_world_report),
    ]
    public_overclaims = _public_overclaim_claims(battle_report)
    if public_overclaims:
        claims.extend(public_overclaims)
    else:
        claims.append(
            _claim(
                claim="Public surfaces avoid blocked overclaim phrases.",
                claim_type="public_claims",
                proof_level="runtime-validated",
                verdict="proven",
                confidence="high",
                evidence_sources=["relay_kit_v3/battle_audit.py#PUBLIC_OVERCLAIM_PATTERNS"],
                residual_risk="This does not prove external adoption or field validation.",
                next_verification="Keep battle-audit in readiness before release.",
            )
        )
    return claims


def _aggregate_skill_validation_claim(proof_report: Mapping[str, Any]) -> dict[str, Any]:
    summary = _mapping(proof_report.get("summary"))
    theoretical = int(summary.get("theoretical", 0) or 0)
    validated = int(summary.get("validated", 0) or 0)
    field_tested = int(summary.get("field_tested", 0) or 0)
    skill_count = int(summary.get("skill_count", 0) or 0)
    sources = ["relay-kit proof audit"] if skill_count else []
    if theoretical:
        return _claim(
            claim="Canonical skills have at least validation coverage.",
            claim_type="skill_quality",
            proof_level="none",
            verdict="unsupported",
            confidence="blocked",
            evidence_sources=sources,
            residual_risk=f"{theoretical} skills have no validation evidence.",
            next_verification="Add workflow and real-world fixtures for theoretical skills.",
        )
    return _claim(
        claim=f"Canonical skills are validated: {validated} validated, {field_tested} field-tested.",
        claim_type="skill_quality",
        proof_level="real-world-fixture" if validated else "field-tested",
        verdict="proven",
        confidence="high",
        evidence_sources=sources,
        residual_risk="Validated does not mean field-tested unless field evidence exists.",
        next_verification="Use field-tested wording only for skills with field evidence.",
    )


def _real_world_fixture_claim(real_world_report: Mapping[str, Any]) -> dict[str, Any]:
    status = str(real_world_report.get("status", "fail"))
    passed = int(real_world_report.get("passed", 0) or 0)
    case_count = int(real_world_report.get("case_count", 0) or 0)
    if status != "pass":
        return _claim(
            claim="Real-world skill contract fixtures cover the canonical registry.",
            claim_type="runtime_safety",
            proof_level="none",
            verdict="unsupported",
            confidence="blocked",
            evidence_sources=["relay-kit eval real-world"],
            residual_risk=f"Real-world eval passed {passed}/{case_count}.",
            next_verification="Fix real-world skill eval findings before claiming validated coverage.",
        )
    return _claim(
        claim=f"Real-world skill contract fixtures pass: {passed}/{case_count}.",
        claim_type="runtime_safety",
        proof_level="real-world-fixture",
        verdict="proven",
        confidence="high",
        evidence_sources=["relay-kit eval real-world"],
        residual_risk="Fixture pass is not field deployment evidence.",
        next_verification="Attach field evidence separately when a claim needs it.",
    )


def _public_overclaim_claims(battle_report: Mapping[str, Any]) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    for finding in battle_report.get("findings", []):
        if not isinstance(finding, Mapping):
            continue
        if str(finding.get("skill", "")) != "public-surface":
            continue
        message = str(finding.get("message", "Public overclaim finding."))
        if "overclaim phrase" not in message.casefold():
            continue
        path = str(finding.get("file", ""))
        flags = _overclaim_flags(message)
        claims.append(
            _claim(
                claim=message,
                claim_type="public_claims",
                proof_level="none",
                verdict="unsupported",
                confidence="blocked",
                evidence_sources=[path] if path else [],
                overclaim_flags=flags,
                residual_risk="Public copy contains wording that can imply proof stronger than local evidence.",
                next_verification="Rewrite the public surface or attach external field evidence.",
                finding_check="public-overclaim",
            )
        )
    return claims


def _claim(
    *,
    claim: str,
    claim_type: str,
    proof_level: str,
    verdict: str,
    confidence: str,
    evidence_sources: Sequence[str],
    residual_risk: str,
    next_verification: str,
    overclaim_flags: Sequence[str] | None = None,
    finding_check: str | None = None,
) -> dict[str, Any]:
    return {
        "claim": claim,
        "claim_type": claim_type,
        "evidence_sources": list(evidence_sources),
        "proof_level": proof_level,
        "verdict": verdict,
        "confidence": confidence,
        "overclaim_flags": list(overclaim_flags or []),
        "residual_risk": residual_risk,
        "next_verification": next_verification,
        "finding_check": finding_check,
    }


def _findings_from_claims(claims: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for index, claim in enumerate(claims, start=1):
        verdict = str(claim.get("verdict", ""))
        confidence = str(claim.get("confidence", ""))
        if verdict not in {"unsupported", "contradicted"} and confidence != "blocked":
            continue
        check = str(claim.get("finding_check") or "claim-calibration")
        findings.append(
            {
                "check": check,
                "claim_index": index,
                "claim_type": str(claim.get("claim_type", "")),
                "verdict": verdict,
                "confidence": confidence,
                "summary": str(claim.get("residual_risk", "")),
                "next_verification": str(claim.get("next_verification", "")),
                "evidence_sources": list(claim.get("evidence_sources", [])),
            }
        )
    return findings


def _summary(claims: Sequence[Mapping[str, Any]], findings: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "claim_count": len(claims),
        "proven_claims": sum(1 for claim in claims if claim.get("verdict") == "proven"),
        "partially_proven_claims": sum(1 for claim in claims if claim.get("verdict") == "partially-proven"),
        "inferred_claims": sum(1 for claim in claims if claim.get("verdict") == "inferred"),
        "unsupported_claims": sum(1 for claim in claims if claim.get("verdict") == "unsupported"),
        "contradicted_claims": sum(1 for claim in claims if claim.get("verdict") == "contradicted"),
        "blocked_claims": sum(1 for claim in claims if claim.get("confidence") == "blocked" or claim.get("verdict") in {"unsupported", "contradicted"}),
        "overclaim_flags": sum(len(_list(claim.get("overclaim_flags"))) for claim in claims),
        "field_tested_claims": sum(1 for claim in claims if claim.get("proof_level") == "field-tested"),
        "findings": len(findings),
    }


def _overclaim_flags(text: str) -> list[str]:
    flags: list[str] = []
    for label, pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            flags.append(label)
    return flags


def _evidence_hints(text: str) -> list[str]:
    hits: list[str] = []
    for hint in EVIDENCE_HINTS:
        if re.search(_evidence_hint_pattern(hint), text, flags=re.IGNORECASE):
            hits.append(hint)
    return hits


def _evidence_hint_pattern(hint: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_]+", hint):
        return rf"(?<![A-Za-z0-9_]){re.escape(hint)}(?![A-Za-z0-9_])"
    return re.escape(hint)


def _all_field_sources(proof_report: Mapping[str, Any]) -> list[str]:
    sources: list[str] = []
    for record in proof_report.get("skills", []):
        if not isinstance(record, Mapping) or record.get("status") != "field-tested":
            continue
        sources.extend(str(item) for item in record.get("proof_sources", []) if str(item))
    return sources


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []
