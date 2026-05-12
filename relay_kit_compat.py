from __future__ import annotations

from pathlib import Path
from typing import List, Sequence


CANONICAL_ENTRYPOINT = "relay_kit.py"

CANONICAL_ARTIFACT_ROOT = ".relay-kit"
GENERIC_CANONICAL_DIR = ".relay-kit-prompts"
GENERIC_OUTPUT_DIRS: Sequence[str] = (GENERIC_CANONICAL_DIR,)


def generic_prompt_dirs(project_path: str | Path) -> List[Path]:
    base = Path(project_path)
    return [base / relative for relative in GENERIC_OUTPUT_DIRS]


def mirrored_generic_paths(project_path: str | Path, relative_path: str | Path) -> List[Path]:
    rel = Path(relative_path)
    return [root / rel for root in generic_prompt_dirs(project_path)]
