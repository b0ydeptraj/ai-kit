#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from relay_kit_cycle_log import (
    SUMMARY_END,
    SUMMARY_START,
    is_real_run,
    load_cycle_events,
    replace_summary_block,
)


DOC_PATH = REPO_ROOT / "docs" / "relay-kit-compatibility-log.md"
ENTRYPOINTS_NEW = {"relay_kit.py", "relay_kit_legacy.py"}
ENTRYPOINTS_OLD = {"python_kit.py", "python_kit_legacy.py"}
ENTRYPOINT_ORDER = (
    "relay_kit.py",
    "python_kit.py",
    "relay_kit_legacy.py",
    "python_kit_legacy.py",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize the Relay-kit compatibility-cycle event log and optionally write a checkpoint."
    )
    parser.add_argument(
        "--source",
        default="interactive",
        help="Source filter for summary counts (default: interactive). Use 'all' to include every source.",
    )
    parser.add_argument(
        "--write-summary",
        action="store_true",
        help="Update the auto-managed summary block in docs/relay-kit-compatibility-log.md",
    )
    parser.add_argument(
        "--checkpoint",
        action="store_true",
        help="Append a checkpoint block to docs/relay-kit-compatibility-log.md and refresh the summary block.",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Do not run scripts/validate_runtime.py when creating a checkpoint.",
    )
    return parser.parse_args()


def filtered_events(source: str) -> list[dict]:
    events = load_cycle_events(REPO_ROOT)
    if source == "all":
        return events
    return [event for event in events if event.get("source") == source]


def summarize(events: list[dict]) -> dict[str, object]:
    real_runs = [event for event in events if is_real_run(event)]
    entrypoint_counts = {
        name: sum(1 for event in real_runs if event.get("entrypoint") == name)
        for name in ENTRYPOINT_ORDER
    }
    targets = sorted({str(event.get("project_path")) for event in real_runs if event.get("project_path")})
    last_event = events[-1]["timestamp"] if events else "none"
    return {
        "total_logged_events": len(events),
        "real_runs": len(real_runs),
        "new_entrypoint_runs": sum(entrypoint_counts[name] for name in ENTRYPOINTS_NEW),
        "old_entrypoint_runs": sum(entrypoint_counts[name] for name in ENTRYPOINTS_OLD),
        "generic_dual_write_runs": sum(1 for event in real_runs if event.get("generic_output")),
        "distinct_target_projects": len(targets),
        "failed_runs": sum(1 for event in real_runs if not event.get("success")),
        "entrypoint_counts": entrypoint_counts,
        "last_event": last_event,
    }


def render_summary_lines(summary: dict[str, object], source: str, validation_result: str) -> str:
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    counts = summary["entrypoint_counts"]
    lines = [
        f"- Last summary update: `{timestamp}`",
        f"- Source filter: `{source}`",
        f"- Total logged events considered: `{summary['total_logged_events']}`",
        f"- Total real runs: `{summary['real_runs']}`",
        f"- `relay_kit.py` runs: `{counts['relay_kit.py']}`",
        f"- `python_kit.py` runs: `{counts['python_kit.py']}`",
        f"- `relay_kit_legacy.py` runs: `{counts['relay_kit_legacy.py']}`",
        f"- `python_kit_legacy.py` runs: `{counts['python_kit_legacy.py']}`",
        f"- Generic dual-write runs: `{summary['generic_dual_write_runs']}`",
        f"- Distinct target projects: `{summary['distinct_target_projects']}`",
        f"- Failed runs in filtered set: `{summary['failed_runs']}`",
        f"- Last validation result: `{validation_result}`",
        f"- Last observed event: `{summary['last_event']}`",
    ]
    return "\n".join(lines)


def print_summary(summary: dict[str, object], source: str, validation_result: str) -> None:
    counts = summary["entrypoint_counts"]
    print("Relay-kit compatibility-cycle summary")
    print(f"- Source filter: {source}")
    print(f"- Total logged events considered: {summary['total_logged_events']}")
    print(f"- Total real runs: {summary['real_runs']}")
    print(f"- relay_kit.py runs: {counts['relay_kit.py']}")
    print(f"- python_kit.py runs: {counts['python_kit.py']}")
    print(f"- relay_kit_legacy.py runs: {counts['relay_kit_legacy.py']}")
    print(f"- python_kit_legacy.py runs: {counts['python_kit_legacy.py']}")
    print(f"- Generic dual-write runs: {summary['generic_dual_write_runs']}")
    print(f"- Distinct target projects: {summary['distinct_target_projects']}")
    print(f"- Failed runs in filtered set: {summary['failed_runs']}")
    print(f"- Last validation result: {validation_result}")
    print(f"- Last observed event: {summary['last_event']}")


def write_summary_block(summary: dict[str, object], source: str, validation_result: str) -> None:
    content = DOC_PATH.read_text(encoding="utf-8")
    replacement = render_summary_lines(summary, source, validation_result)
    updated = replace_summary_block(content, replacement)
    DOC_PATH.write_text(updated, encoding="utf-8")


def append_checkpoint(summary: dict[str, object], source: str, validation_result: str) -> None:
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    counts = summary["entrypoint_counts"]
    block = f"""

## Checkpoint {timestamp}

- Source filter:
  - `{source}`
- Total logged events considered:
  - `{summary['total_logged_events']}`
- Total real runs:
  - `{summary['real_runs']}`
- `relay_kit.py` runs:
  - `{counts['relay_kit.py']}`
- `python_kit.py` runs:
  - `{counts['python_kit.py']}`
- `relay_kit_legacy.py` runs:
  - `{counts['relay_kit_legacy.py']}`
- `python_kit_legacy.py` runs:
  - `{counts['python_kit_legacy.py']}`
- Generic dual-write runs:
  - `{summary['generic_dual_write_runs']}`
- Distinct target projects:
  - `{summary['distinct_target_projects']}`
- Failed runs in filtered set:
  - `{summary['failed_runs']}`
- Validation command:
  - `python scripts/validate_runtime.py`
- Result:
  - `{validation_result}`
- Notes:
  - auto-generated checkpoint
"""
    with DOC_PATH.open("a", encoding="utf-8") as handle:
        handle.write(block.rstrip() + "\n")


def run_validation() -> str:
    env = dict(os.environ)
    env["RELAY_KIT_CYCLE_SOURCE"] = "checkpoint"
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "validate_runtime.py")],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    return "pass" if result.returncode == 0 else "fail"


def main() -> int:
    args = parse_args()
    events = filtered_events(args.source)
    validation_result = "not-run"
    if args.checkpoint and not args.skip_validation:
        validation_result = run_validation()
    summary = summarize(events)
    print_summary(summary, args.source, validation_result)

    if args.write_summary or args.checkpoint:
        write_summary_block(summary, args.source, validation_result)
    if args.checkpoint:
        append_checkpoint(summary, args.source, validation_result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
