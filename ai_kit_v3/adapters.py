from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List

from relay_kit_compat import GENERIC_CANONICAL_DIR


ADAPTER_TARGETS: Dict[str, List[str]] = {
    "claude": [".claude/skills"],
    "antigravity": [".agent/skills"],
    "codex": [".codex/skills"],
    "all": [".claude/skills", ".agent/skills", ".codex/skills"],
    "generic": [GENERIC_CANONICAL_DIR],
}


def targets_for(ai: str) -> List[Path]:
    if ai not in ADAPTER_TARGETS:
        raise KeyError(f"Unknown AI adapter: {ai}")
    return [Path(path) for path in ADAPTER_TARGETS[ai]]


def ensure_dirs(base: Path, relative_dirs: Iterable[Path]) -> None:
    for rel in relative_dirs:
        (base / rel).mkdir(parents=True, exist_ok=True)
