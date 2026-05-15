from __future__ import annotations

import json
import math
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence
from uuid import uuid4


RAW_LOG_SCHEMA_VERSION = "relay-kit.shell-raw.v1"
COMPACT_SCHEMA_VERSION = "relay-kit.shell-compact.v1"

RAW_REQUIRED_MARKERS = (
    "fail",
    "failed",
    "failure",
    "error",
    "traceback",
    "assertion",
    "assertionerror",
    "exception",
)
MAX_PREVIEW_LINES = 12
MAX_FAILURE_CONTEXT_LINES = 12


class ShellCompactionError(RuntimeError):
    """Raised when strict shell compaction drops required signal."""


def estimate_tokens(text: str) -> int:
    return int(math.ceil(len(text) / 4)) if text else 0


def run_compacted_command(
    command: Sequence[str],
    *,
    project_root: Path | str,
    cwd: Path | str | None = None,
    strict: bool = False,
    timeout: float | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    run_cwd = Path(cwd).resolve() if cwd is not None else root
    completed = subprocess.run(
        list(command),
        cwd=run_cwd,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    raw_path = _write_raw_log(
        root,
        command=list(command),
        cwd=run_cwd,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
    compact = compact_shell_output(
        stdout=completed.stdout,
        stderr=completed.stderr,
        returncode=completed.returncode,
        raw_path=raw_path,
        command=list(command),
        strict=strict,
    )
    return {
        "schema_version": COMPACT_SCHEMA_VERSION,
        "command": list(command),
        "cwd": str(run_cwd),
        "returncode": completed.returncode,
        "raw_path": str(raw_path),
        **compact,
    }


def compact_shell_output(
    *,
    stdout: str,
    stderr: str,
    returncode: int,
    raw_path: Path | str,
    command: Sequence[str] | None = None,
    strict: bool = False,
    max_raw_required_lines: int | None = None,
) -> dict[str, Any]:
    raw_path_text = str(raw_path)
    raw_text = _raw_text(stdout=stdout, stderr=stderr)
    raw_required_lines = _raw_required_lines(stdout=stdout, stderr=stderr, returncode=returncode)
    kept_required_lines = (
        raw_required_lines
        if max_raw_required_lines is None
        else raw_required_lines[:max_raw_required_lines]
    )
    signal_retention = (
        1.0
        if not raw_required_lines
        else len(kept_required_lines) / len(raw_required_lines)
    )
    if strict and signal_retention < 1.0:
        raise ShellCompactionError(
            f"shell compaction signal_retention {signal_retention:.3f} is below 1.0; raw log: {raw_path_text}"
        )

    compact_output = _render_compact_output(
        returncode=returncode,
        raw_path=raw_path_text,
        command=command,
        kept_required_lines=kept_required_lines,
        stdout=stdout,
        stderr=stderr,
        signal_retention=signal_retention,
    )
    estimated_raw_tokens = estimate_tokens(raw_text)
    estimated_compact_tokens = estimate_tokens(compact_output)
    saved_tokens = max(estimated_raw_tokens - estimated_compact_tokens, 0)
    savings_ratio = 0.0 if estimated_raw_tokens == 0 else saved_tokens / estimated_raw_tokens
    return {
        "compact_output": compact_output,
        "estimated_raw_tokens": estimated_raw_tokens,
        "estimated_compact_tokens": estimated_compact_tokens,
        "saved_tokens": saved_tokens,
        "savings_ratio": savings_ratio,
        "signal_retention": signal_retention,
        "raw_required_line_count": len(raw_required_lines),
        "retained_raw_required_line_count": len(kept_required_lines),
    }


def _write_raw_log(
    root: Path,
    *,
    command: Sequence[str],
    cwd: Path,
    returncode: int,
    stdout: str,
    stderr: str,
) -> Path:
    raw_dir = root / ".relay-kit" / "evidence" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = _command_slug(command)
    raw_path = raw_dir / f"{timestamp}-{slug}-{uuid4().hex[:8]}.json"
    payload = {
        "schema_version": RAW_LOG_SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "command": list(command),
        "cwd": str(cwd),
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr,
    }
    raw_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return raw_path


def _raw_required_lines(*, stdout: str, stderr: str, returncode: int) -> list[str]:
    lines: list[str] = []
    for stream_name, text in (("stdout", stdout), ("stderr", stderr)):
        for line in text.splitlines():
            lowered = line.lower()
            if any(marker in lowered for marker in RAW_REQUIRED_MARKERS):
                lines.append(f"{stream_name}: {line}")
    if returncode != 0 and not lines:
        lines.extend(_failure_tail_context(stdout=stdout, stderr=stderr))
    return lines


def _failure_tail_context(*, stdout: str, stderr: str) -> list[str]:
    combined: list[str] = []
    for stream_name, text in (("stdout", stdout), ("stderr", stderr)):
        combined.extend(f"{stream_name}: {line}" for line in text.splitlines())
    return combined[-MAX_FAILURE_CONTEXT_LINES:]


def _raw_text(*, stdout: str, stderr: str) -> str:
    return f"stdout:\n{stdout}\nstderr:\n{stderr}"


def _render_compact_output(
    *,
    returncode: int,
    raw_path: str,
    command: Sequence[str] | None,
    kept_required_lines: Sequence[str],
    stdout: str,
    stderr: str,
    signal_retention: float,
) -> str:
    lines = [
        "Relay-kit shell compact output",
        f"- returncode: {returncode}",
        f"- raw_path: {raw_path}",
        f"- signal_retention: {signal_retention:.3f}",
    ]
    if command is not None:
        lines.append(f"- command: {_quote_command(command)}")
    if kept_required_lines:
        lines.append("raw-required:")
        lines.extend(f"- {line}" for line in kept_required_lines)
    else:
        preview = _preview_lines(stdout=stdout, stderr=stderr)
        if preview:
            lines.append("preview:")
            lines.extend(f"- {line}" for line in preview)
        else:
            lines.append("preview: <no output>")
    return "\n".join(lines) + "\n"


def _preview_lines(*, stdout: str, stderr: str) -> list[str]:
    preview: list[str] = []
    for stream_name, text in (("stdout", stdout), ("stderr", stderr)):
        for line in text.splitlines():
            if len(preview) >= MAX_PREVIEW_LINES:
                return preview
            preview.append(f"{stream_name}: {line}")
    return preview


def _command_slug(command: Sequence[str]) -> str:
    joined = "-".join(Path(part).name if index == 0 else part for index, part in enumerate(command[:3]))
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", joined).strip("-").lower()
    return slug[:48] or "command"


def _quote_command(command: Sequence[str]) -> str:
    return " ".join(command)
