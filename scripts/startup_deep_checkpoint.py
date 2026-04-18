#!/usr/bin/env python3
"""Run deep checkpoints automatically once per day after startup/logon."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = Path(r"D:\relay-kit-checkpoint")
DEFAULT_TEMP_ROOT = Path(r"D:\relay-kit-temp")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deep checkpoint multiple times with daily guard.")
    parser.add_argument("--count", type=int, default=5, help="How many deep checkpoints to run (default: 5).")
    parser.add_argument("--gap-sec", type=int, default=10, help="Sleep between runs in seconds (default: 10).")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT), help="Checkpoint output root.")
    parser.add_argument("--temp-root", default=str(DEFAULT_TEMP_ROOT), help="Temp root.")
    parser.add_argument("--force", action="store_true", help="Ignore daily guard and run immediately.")
    return parser.parse_args()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_guard(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_guard(path: Path, payload: dict[str, object]) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run_one(output_root: Path, temp_root: Path) -> tuple[int, str]:
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "deep_checkpoint.py"),
        "--output-root",
        str(output_root),
        "--temp-root",
        str(temp_root),
        "--allow-no-real-projects",
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    return proc.returncode, output


def main() -> int:
    args = parse_args()
    output_root = Path(args.output_root).resolve()
    temp_root = Path(args.temp_root).resolve()
    ensure_dir(output_root)
    ensure_dir(temp_root)

    logs_dir = output_root / "logs"
    state_dir = output_root / "state"
    ensure_dir(logs_dir)
    ensure_dir(state_dir)

    guard_file = state_dir / "startup-deep-checkpoint-guard.json"
    today = datetime.now().date().isoformat()
    now = datetime.now().strftime("%Y%m%d-%H%M%S")

    guard = read_guard(guard_file)
    if not args.force and guard.get("last_run_date") == today:
        message = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "status": "skipped",
            "reason": "already-ran-today",
            "last_run_date": guard.get("last_run_date"),
        }
        print(json.dumps(message, ensure_ascii=False, indent=2))
        return 0

    batch_results: list[dict[str, object]] = []
    pass_count = 0
    fail_count = 0

    for idx in range(1, args.count + 1):
        started = time.perf_counter()
        code, output = run_one(output_root, temp_root)
        elapsed = round(time.perf_counter() - started, 3)
        ok = code == 0
        if ok:
            pass_count += 1
        else:
            fail_count += 1
        batch_results.append(
            {
                "run": idx,
                "ok": ok,
                "returncode": code,
                "duration_sec": elapsed,
                "output_tail": output[-2000:],
            }
        )
        if idx < args.count and args.gap_sec > 0:
            time.sleep(args.gap_sec)

    summary = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "mode": "startup-daily-batch",
        "count": args.count,
        "pass": pass_count,
        "fail": fail_count,
        "results": batch_results,
    }

    json_path = logs_dir / f"startup-deep-checkpoint-batch-{now}.json"
    md_path = logs_dir / f"startup-deep-checkpoint-batch-{now}.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# Startup deep checkpoint batch ({summary['timestamp']})",
        "",
        f"- Count: {summary['count']}",
        f"- Pass: {summary['pass']}",
        f"- Fail: {summary['fail']}",
        "",
        "## Runs",
    ]
    for item in batch_results:
        lines.append(
            f"- run {item['run']}: {'PASS' if item['ok'] else 'FAIL'} "
            f"(rc={item['returncode']}, {item['duration_sec']}s)"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    write_guard(
        guard_file,
        {
            "last_run_date": today,
            "last_batch_json": str(json_path),
            "last_batch_md": str(md_path),
            "last_status": "pass" if fail_count == 0 else "fail",
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        },
    )

    print(
        json.dumps(
            {
                "timestamp": summary["timestamp"],
                "count": summary["count"],
                "pass": summary["pass"],
                "fail": summary["fail"],
                "batch_json": str(json_path),
                "batch_md": str(md_path),
                "guard_file": str(guard_file),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
