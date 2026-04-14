#!/usr/bin/env python3
"""Context continuity utility for checkpoint, rehydrate, handoff, and diff flows."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


WATCH_FILES = [
    ".relay-kit/state/current-state.md",
    ".relay-kit/state/decision-register.md",
    ".relay-kit/state/open-loops.md",
    ".relay-kit/state/evidence-index.md",
    ".relay-kit/state/workflow-state.md",
    ".relay-kit/state/team-board.md",
    ".relay-kit/state/lane-registry.md",
    ".relay-kit/state/handoff-log.md",
    ".relay-kit/contracts/tech-spec.md",
    ".relay-kit/contracts/investigation-notes.md",
    ".relay-kit/contracts/qa-report.md",
    ".relay-kit/contracts/stories/story-001.md",
]

STATE_TEMPLATES = {
    ".relay-kit/state/current-state.md": "# current-state\n\n## Current objective\nTBD\n\n## Active lane\nTBD\n\n## Current blocker\nTBD\n\n## Exact next step\nTBD\n",
    ".relay-kit/state/decision-register.md": "# decision-register\n\n## Decisions\n- date:\n- decision:\n- reason:\n- rejected options:\n\n",
    ".relay-kit/state/open-loops.md": "# open-loops\n\n## Open items\n- item:\n- owner:\n- unblock condition:\n\n",
    ".relay-kit/state/evidence-index.md": "# evidence-index\n\n## Evidence pointers\n- command:\n- output:\n- related files:\n\n",
    ".relay-kit/state/session-ledger.jsonl": "",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preserve and restore Relay-kit continuity across long chats and session boundaries.",
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    checkpoint = subparsers.add_parser("checkpoint", help="Capture continuity snapshot")
    add_common_mode_args(checkpoint)
    checkpoint.add_argument("--objective", help="Current objective summary")
    checkpoint.add_argument("--lane", default="primary", help="Active lane id")
    checkpoint.add_argument("--blocker", default="none", help="Current blocker")
    checkpoint.add_argument("--next-step", help="Exact next step for the next session")
    checkpoint.add_argument("--note", default="", help="Optional checkpoint note")

    rehydrate = subparsers.add_parser("rehydrate", help="Rehydrate context from last checkpoint")
    add_common_mode_args(rehydrate)

    handoff = subparsers.add_parser("handoff", help="Create handoff pack from latest manifest")
    add_common_mode_args(handoff)
    handoff.add_argument("--reason", default="session-handoff", help="Reason for handoff file naming")
    handoff.add_argument("--receiver", default="next-session", help="Intended receiver")

    diff_cmd = subparsers.add_parser("diff-since-last", help="Diff tracked continuity files since last checkpoint")
    add_common_mode_args(diff_cmd)

    return parser.parse_args()


def add_common_mode_args(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("project_path", nargs="?", default=".", help="Target project root")
    subparser.add_argument("--json", action="store_true", help="Emit JSON output")


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_structure(base: Path) -> None:
    for rel_path, template in STATE_TEMPLATES.items():
        target = base / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_text(template, encoding="utf-8")
    (base / ".relay-kit" / "handoffs").mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def collect_snapshot(base: Path) -> Dict[str, Dict[str, object]]:
    snapshot: Dict[str, Dict[str, object]] = {}
    for rel_path in WATCH_FILES:
        target = base / rel_path
        if not target.exists():
            continue
        stat = target.stat()
        snapshot[rel_path] = {
            "sha256": sha256_file(target),
            "bytes": stat.st_size,
            "mtime_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
        }
    return snapshot


def manifest_path(base: Path) -> Path:
    return base / ".relay-kit" / "state" / "context-manifest.json"


def load_manifest(base: Path) -> Dict[str, object]:
    path = manifest_path(base)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_manifest(base: Path, payload: Dict[str, object]) -> None:
    path = manifest_path(base)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def append_ledger(base: Path, entry: Dict[str, object]) -> None:
    ledger = base / ".relay-kit" / "state" / "session-ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=True) + "\n")


def append_current_state_checkpoint(base: Path, payload: Dict[str, object]) -> None:
    path = base / ".relay-kit" / "state" / "current-state.md"
    lines = [
        "",
        f"## checkpoint {payload['updated_at']}",
        f"- objective: {payload['objective']}",
        f"- lane: {payload['lane']}",
        f"- blocker: {payload['blocker']}",
        f"- next_step: {payload['next_step']}",
        f"- note: {payload['note'] or '-'}",
    ]
    with path.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def run_checkpoint(args: argparse.Namespace) -> int:
    base = Path(args.project_path).resolve()
    ensure_structure(base)
    previous = load_manifest(base)
    snapshot = collect_snapshot(base)
    updated_at = now_utc_iso()

    payload: Dict[str, object] = {
        "version": 1,
        "updated_at": updated_at,
        "objective": args.objective or previous.get("objective", "TBD"),
        "lane": args.lane or previous.get("lane", "primary"),
        "blocker": args.blocker or previous.get("blocker", "none"),
        "next_step": args.next_step or previous.get("next_step", "TBD"),
        "note": args.note,
        "tracked_files": snapshot,
    }
    write_manifest(base, payload)
    append_current_state_checkpoint(base, payload)
    append_ledger(
        base,
        {
            "timestamp": updated_at,
            "mode": "checkpoint",
            "objective": payload["objective"],
            "lane": payload["lane"],
            "next_step": payload["next_step"],
            "tracked_count": len(snapshot),
        },
    )

    if args.json:
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print(f"Checkpoint saved at {updated_at}")
        print(f"Tracked files: {len(snapshot)}")
        print(f"Next step: {payload['next_step']}")
    return 0


def run_rehydrate(args: argparse.Namespace) -> int:
    base = Path(args.project_path).resolve()
    ensure_structure(base)
    manifest = load_manifest(base)
    if not manifest:
        print("No context-manifest found. Run checkpoint first.")
        return 1

    summary = {
        "updated_at": manifest.get("updated_at"),
        "objective": manifest.get("objective", "TBD"),
        "lane": manifest.get("lane", "primary"),
        "blocker": manifest.get("blocker", "none"),
        "next_step": manifest.get("next_step", "TBD"),
        "tracked_count": len(manifest.get("tracked_files", {})),
        "open_loops_file": ".relay-kit/state/open-loops.md",
    }
    append_ledger(
        base,
        {
            "timestamp": now_utc_iso(),
            "mode": "rehydrate",
            "source_manifest": manifest.get("updated_at"),
            "lane": summary["lane"],
        },
    )

    if args.json:
        print(json.dumps(summary, ensure_ascii=True, indent=2))
    else:
        print("Rehydrate brief")
        print(f"- updated_at: {summary['updated_at']}")
        print(f"- objective: {summary['objective']}")
        print(f"- lane: {summary['lane']}")
        print(f"- blocker: {summary['blocker']}")
        print(f"- next_step: {summary['next_step']}")
        print(f"- tracked_files: {summary['tracked_count']}")
        print(f"- open_loops: {summary['open_loops_file']}")
    return 0


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "handoff"


def run_handoff(args: argparse.Namespace) -> int:
    base = Path(args.project_path).resolve()
    ensure_structure(base)
    manifest = load_manifest(base)
    if not manifest:
        print("No context-manifest found. Run checkpoint first.")
        return 1

    timestamp = now_utc_iso()
    file_stamp = timestamp.replace(":", "-")
    handoff_name = f"{file_stamp}-{safe_slug(args.reason)}.md"
    handoff_path = base / ".relay-kit" / "handoffs" / handoff_name
    content = [
        "# context-handoff",
        "",
        f"- timestamp: {timestamp}",
        f"- reason: {args.reason}",
        f"- receiver: {args.receiver}",
        "",
        "## Current lane state",
        f"- objective: {manifest.get('objective', 'TBD')}",
        f"- lane: {manifest.get('lane', 'primary')}",
        f"- blocker: {manifest.get('blocker', 'none')}",
        f"- next_step: {manifest.get('next_step', 'TBD')}",
        "",
        "## Evidence pointers",
        "- .relay-kit/state/context-manifest.json",
        "- .relay-kit/state/session-ledger.jsonl",
        "- .relay-kit/state/open-loops.md",
        "- .relay-kit/state/evidence-index.md",
        "",
    ]
    handoff_path.write_text("\n".join(content), encoding="utf-8")
    append_ledger(
        base,
        {
            "timestamp": timestamp,
            "mode": "handoff",
            "reason": args.reason,
            "receiver": args.receiver,
            "path": str(handoff_path.relative_to(base).as_posix()),
        },
    )
    if args.json:
        print(
            json.dumps(
                {
                    "timestamp": timestamp,
                    "handoff_path": handoff_path.relative_to(base).as_posix(),
                    "receiver": args.receiver,
                },
                ensure_ascii=True,
                indent=2,
            )
        )
    else:
        print(f"Handoff pack written: {handoff_path}")
    return 0


def run_diff(args: argparse.Namespace) -> int:
    base = Path(args.project_path).resolve()
    ensure_structure(base)
    manifest = load_manifest(base)
    previous = manifest.get("tracked_files", {})
    if not isinstance(previous, dict) or not previous:
        print("No tracked file snapshot found. Run checkpoint first.")
        return 1

    current = collect_snapshot(base)
    changed: List[str] = []
    removed: List[str] = []
    added: List[str] = []

    for rel_path, prev_meta in previous.items():
        if rel_path not in current:
            removed.append(rel_path)
            continue
        prev_hash = ""
        if isinstance(prev_meta, dict):
            prev_hash = str(prev_meta.get("sha256", ""))
        curr_hash = str(current[rel_path].get("sha256", ""))
        if prev_hash != curr_hash:
            changed.append(rel_path)

    for rel_path in current:
        if rel_path not in previous:
            added.append(rel_path)

    result = {
        "baseline_manifest": manifest.get("updated_at"),
        "changed": sorted(changed),
        "removed": sorted(removed),
        "added": sorted(added),
    }
    append_ledger(
        base,
        {
            "timestamp": now_utc_iso(),
            "mode": "diff-since-last",
            "changed": len(changed),
            "removed": len(removed),
            "added": len(added),
        },
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        print("Diff since last checkpoint")
        print(f"- baseline_manifest: {result['baseline_manifest']}")
        print(f"- changed: {len(changed)}")
        print(f"- removed: {len(removed)}")
        print(f"- added: {len(added)}")
        if changed:
            print("  changed files:")
            for rel in result["changed"]:
                print(f"  - {rel}")
        if removed:
            print("  removed files:")
            for rel in result["removed"]:
                print(f"  - {rel}")
        if added:
            print("  added files:")
            for rel in result["added"]:
                print(f"  - {rel}")
    return 0


def main() -> int:
    args = parse_args()
    if args.mode == "checkpoint":
        return run_checkpoint(args)
    if args.mode == "rehydrate":
        return run_rehydrate(args)
    if args.mode == "handoff":
        return run_handoff(args)
    if args.mode == "diff-since-last":
        return run_diff(args)
    raise ValueError(f"Unsupported mode: {args.mode}")


if __name__ == "__main__":
    raise SystemExit(main())

