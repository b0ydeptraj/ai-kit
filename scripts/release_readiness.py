#!/usr/bin/env python3
"""Release readiness and deploy-smoke gate utility for Relay-kit."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


PRE_DEPLOY_CHECKS: List[Tuple[str, str]] = [
    ("build_passed", "Build and packaging checks passed"),
    ("tests_passed", "Required test suite passed"),
    ("migration_plan_checked", "Migration and compatibility impact reviewed"),
    ("rollback_plan_ready", "Rollback plan and trigger thresholds documented"),
]

POST_DEPLOY_CHECKS: List[Tuple[str, str]] = [
    ("healthcheck_ok", "Service health checks are green"),
    ("critical_user_flow_ok", "Critical user flow smoke tests passed"),
    ("error_rate_within_budget", "Error rate and latency stay within budget"),
    ("rollback_signals_clear", "No rollback triggers fired"),
]


@dataclass(frozen=True)
class GateResult:
    phase: str
    passed: bool
    failures: List[str]
    missing: List[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate release readiness checklists and evaluate deploy signals.",
    )
    parser.add_argument("project_path", nargs="?", default=".", help="Target project root")
    parser.add_argument(
        "--phase",
        choices=["pre", "post", "both"],
        default="both",
        help="Gate phase to evaluate (default: both)",
    )
    parser.add_argument(
        "--signals-file",
        help="Optional JSON file with boolean release signals",
    )
    parser.add_argument(
        "--output-file",
        help="Optional file path to write the generated checklist report",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail when no machine-checkable signals file is supplied",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON result")
    return parser.parse_args()


def selected_phases(phase: str) -> List[str]:
    if phase == "both":
        return ["pre", "post"]
    return [phase]


def checks_for_phase(phase: str) -> List[Tuple[str, str]]:
    if phase == "pre":
        return PRE_DEPLOY_CHECKS
    return POST_DEPLOY_CHECKS


def evaluate_phase(signals: Dict[str, object], phase: str) -> GateResult:
    failures: List[str] = []
    missing: List[str] = []
    for key, _label in checks_for_phase(phase):
        if key not in signals:
            missing.append(key)
            continue
        if bool(signals[key]) is False:
            failures.append(key)
    return GateResult(
        phase=phase,
        passed=not failures and not missing,
        failures=failures,
        missing=missing,
    )


def checklist_markdown(phase: str) -> str:
    title = "Pre-deploy gate" if phase == "pre" else "Post-deploy smoke gate"
    lines = [f"## {title}", ""]
    for key, label in checks_for_phase(phase):
        lines.append(f"- [ ] `{key}` - {label}")
    return "\n".join(lines)


def render_markdown(phases: List[str], results: List[GateResult] | None) -> str:
    lines = ["# release-readiness", ""]
    for phase in phases:
        lines.append(checklist_markdown(phase))
        lines.append("")
    if results is None:
        lines.append("No signal file provided. Checklist generated only.")
        return "\n".join(lines).strip() + "\n"

    lines.append("## Signal evaluation")
    lines.append("")
    for result in results:
        verdict = "PASS" if result.passed else "HOLD"
        lines.append(f"- {result.phase}: {verdict}")
        if result.failures:
            lines.append(f"  - failing signals: {', '.join(result.failures)}")
        if result.missing:
            lines.append(f"  - missing signals: {', '.join(result.missing)}")
    return "\n".join(lines).strip() + "\n"


def render_json(phases: List[str], results: List[GateResult] | None) -> str:
    payload = {
        "phases": phases,
        "checks": {phase: [key for key, _ in checks_for_phase(phase)] for phase in phases},
        "results": [
            {
                "phase": item.phase,
                "passed": item.passed,
                "failures": item.failures,
                "missing": item.missing,
            }
            for item in (results or [])
        ],
    }
    return json.dumps(payload, ensure_ascii=True, indent=2)


def load_signals(path: Path) -> Dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("signals file must contain a JSON object")
    return data


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_path).resolve()
    phases = selected_phases(args.phase)

    if args.strict and not args.signals_file:
        print("strict mode requires --signals-file", file=sys.stderr)
        return 2

    results: List[GateResult] | None = None
    if args.signals_file:
        signal_path = Path(args.signals_file)
        if not signal_path.is_absolute():
            signal_path = project_root / signal_path
        signals = load_signals(signal_path)
        results = [evaluate_phase(signals, phase) for phase in phases]

    if args.json:
        content = render_json(phases, results)
    else:
        content = render_markdown(phases, results)

    if args.output_file:
        output_path = Path(args.output_file)
        if not output_path.is_absolute():
            output_path = project_root / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        print(f"Wrote {output_path}")
    else:
        print(content, end="")

    if results is None:
        return 0
    return 0 if all(item.passed for item in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
