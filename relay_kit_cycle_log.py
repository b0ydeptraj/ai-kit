from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


CYCLE_LOG_DIR = ".relay-kit-cycle"
EVENTS_FILE = "events.jsonl"
SUMMARY_START = "<!-- compat-cycle-summary:start -->"
SUMMARY_END = "<!-- compat-cycle-summary:end -->"


def cycle_log_dir(repo_root: Path) -> Path:
    return repo_root / CYCLE_LOG_DIR


def event_log_path(repo_root: Path) -> Path:
    return cycle_log_dir(repo_root) / EVENTS_FILE


def should_log_cycle_events() -> bool:
    return os.environ.get("RELAY_KIT_CYCLE_DISABLE", "").lower() not in {"1", "true", "yes"}


def current_source() -> str:
    return os.environ.get("RELAY_KIT_CYCLE_SOURCE", "interactive")


def append_cycle_event(repo_root: Path, event: dict[str, Any]) -> None:
    if not should_log_cycle_events():
        return
    log_path = event_log_path(repo_root)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        **event,
    }
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=True) + "\n")


def load_cycle_events(repo_root: Path) -> list[dict[str, Any]]:
    log_path = event_log_path(repo_root)
    if not log_path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        events.append(json.loads(line))
    return events


def is_real_run(event: dict[str, Any]) -> bool:
    return event.get("flow") not in {"list_skills", "help_only", "no_op", "invalid"}


def count_if(events: Iterable[dict[str, Any]], *, source: str | None = None, predicate=None) -> int:
    total = 0
    for event in events:
        if source is not None and event.get("source") != source:
            continue
        if predicate is not None and not predicate(event):
            continue
        total += 1
    return total


def replace_summary_block(content: str, summary_block: str) -> str:
    if SUMMARY_START not in content or SUMMARY_END not in content:
        raise ValueError("Compatibility log is missing summary markers.")
    start = content.index(SUMMARY_START) + len(SUMMARY_START)
    end = content.index(SUMMARY_END)
    return content[:start] + "\n" + summary_block.rstrip() + "\n" + content[end:]
