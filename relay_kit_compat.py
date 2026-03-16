from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Sequence


CANONICAL_ENTRYPOINT = "relay_kit.py"
COMPAT_ENTRYPOINT = "python_kit.py"
CANONICAL_LEGACY_ENTRYPOINT = "relay_kit_legacy.py"
COMPAT_LEGACY_ENTRYPOINT = "python_kit_legacy.py"

GENERIC_CANONICAL_DIR = ".relay-kit-prompts"
GENERIC_COMPAT_DIR = ".python-kit-prompts"
GENERIC_OUTPUT_DIRS: Sequence[str] = (GENERIC_CANONICAL_DIR, GENERIC_COMPAT_DIR)


def generic_prompt_dirs(project_path: str | Path) -> List[Path]:
    base = Path(project_path)
    return [base / relative for relative in GENERIC_OUTPUT_DIRS]


def mirrored_generic_paths(project_path: str | Path, relative_path: str | Path) -> List[Path]:
    rel = Path(relative_path)
    return [root / rel for root in generic_prompt_dirs(project_path)]


def legacy_entrypoint_candidates(repo_root: Path) -> Iterable[Path]:
    return (
        repo_root / CANONICAL_LEGACY_ENTRYPOINT,
        repo_root / COMPAT_LEGACY_ENTRYPOINT,
    )
