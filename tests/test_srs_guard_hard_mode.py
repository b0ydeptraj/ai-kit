from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


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


def _write_srs_hard_policy(project: Path) -> None:
    policy_path = project / ".relay-kit" / "state" / "srs-policy.json"
    policy_path.parent.mkdir(parents=True, exist_ok=True)
    policy_path.write_text(
        json.dumps(
            {
                "enabled": True,
                "scope": "all",
                "gate": "hard",
                "risk_profile": "high",
                "updated_at": "2026-04-18T00:00:00Z",
            },
            ensure_ascii=True,
            indent=2,
        ),
        encoding="utf-8",
    )


def _write_minimal_traceable_srs_contracts(project: Path) -> None:
    contracts = project / ".relay-kit" / "contracts"
    stories = contracts / "stories"
    stories.mkdir(parents=True, exist_ok=True)

    (contracts / "srs-spec.md").write_text(
        """
## Goal
Define checkout behavior.

## Actors
- Customer

## Use Cases
- UC-CHECKOUT-01: Customer places order.

## Preconditions
- Cart has at least one item.

## Main Flows
1. Submit order.

## Postconditions
- Order status becomes PAID.

## Exception Flows
- Payment gateway timeout.

## Business Rules
- Minimum order amount is 1.

## Acceptance Examples
- UC-CHECKOUT-01 succeeds with valid card.

## Open Questions
- None.
""".strip()
        + "\n",
        encoding="utf-8",
    )

    (contracts / "PRD.md").write_text(
        """
## SRS Traceability
- UC-CHECKOUT-01 -> story-001 -> qa-report coverage row
""".strip()
        + "\n",
        encoding="utf-8",
    )

    (stories / "story-001.md").write_text(
        """
# story-001
Implements UC-CHECKOUT-01 checkout path.
""".strip()
        + "\n",
        encoding="utf-8",
    )

    (contracts / "qa-report.md").write_text(
        """
## SRS coverage table
| UC-ID | Status |
|---|---|
| UC-CHECKOUT-01 | pass |
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_srs_guard_hard_mode_sandbox_negative_then_positive(tmp_path: Path) -> None:
    project = tmp_path / "srs-hard-sandbox"
    project.mkdir(parents=True, exist_ok=True)

    _run(
        str(REPO_ROOT / "relay_kit.py"),
        str(project),
        "--bundle",
        "srs-first",
        "--ai",
        "codex",
        "--emit-contracts",
        "--emit-docs",
        "--emit-reference-templates",
    )
    _write_srs_hard_policy(project)

    negative = _run(str(REPO_ROOT / "scripts" / "srs_guard.py"), str(project), "--json", expect=2)
    negative_payload = json.loads(negative.stdout)
    assert negative_payload["status"] == "failed"
    assert negative_payload["findings_count"] > 0

    _write_minimal_traceable_srs_contracts(project)

    positive = _run(str(REPO_ROOT / "scripts" / "srs_guard.py"), str(project), "--json", expect=0)
    positive_payload = json.loads(positive.stdout)
    assert positive_payload["status"] == "ok"
    assert positive_payload["findings_count"] == 0
