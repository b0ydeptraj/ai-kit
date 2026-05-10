from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "relay-kit.lane-audit.v1"

STATE_DIR = ".relay-kit/state"
TEAM_BOARD = f"{STATE_DIR}/team-board.md"
LANE_REGISTRY = f"{STATE_DIR}/lane-registry.md"
HANDOFF_LOG = f"{STATE_DIR}/handoff-log.md"

ACTIVE_STATUSES = {"active", "running", "in-progress", "in progress", "queued"}
PARKED_STATUSES = {"parked", "paused", "blocked"}
PLACEHOLDER_VALUES = {"", "-", "none", "n/a", "na", "unassigned", "empty lane", "not set"}
BROAD_LOCK_SCOPES = {"repo", "whole repo", "whole-repo", "entire repo", "all", "*", "everything", "root"}


@dataclass(frozen=True)
class MarkdownTable:
    path: str
    headers: list[str]
    rows: list[dict[str, str]]


def normalize_header(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")


def normalize_value(value: str) -> str:
    return value.strip().strip("`").strip()


def is_placeholder(value: str) -> bool:
    return normalize_value(value).casefold() in PLACEHOLDER_VALUES


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator(cells: Iterable[str]) -> bool:
    return all(set(cell.strip()) <= {"-", ":"} and "-" in cell for cell in cells)


def parse_markdown_tables(path: Path, relative_path: str) -> list[MarkdownTable]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    tables: list[MarkdownTable] = []
    index = 0
    while index < len(lines) - 1:
        line = lines[index].strip()
        next_line = lines[index + 1].strip()
        if not (line.startswith("|") and next_line.startswith("|")):
            index += 1
            continue
        headers = split_markdown_row(line)
        separator = split_markdown_row(next_line)
        if not is_separator(separator):
            index += 1
            continue
        normalized_headers = [normalize_header(header) for header in headers]
        rows: list[dict[str, str]] = []
        index += 2
        while index < len(lines) and lines[index].strip().startswith("|"):
            cells = split_markdown_row(lines[index])
            row = {
                header: normalize_value(cells[position]) if position < len(cells) else ""
                for position, header in enumerate(normalized_headers)
            }
            rows.append(row)
            index += 1
        tables.append(MarkdownTable(path=relative_path, headers=normalized_headers, rows=rows))
    return tables


def find_lane_table(tables: list[MarkdownTable]) -> MarkdownTable | None:
    for table in tables:
        headers = set(table.headers)
        if {"lane", "status", "lock_scope"} <= headers:
            return table
    return None


def find_handoff_table(tables: list[MarkdownTable]) -> MarkdownTable | None:
    for table in tables:
        headers = set(table.headers)
        if {"from", "to", "lane", "expected_return_condition"} <= headers:
            return table
    return None


def required_column_findings(table: MarkdownTable | None, path: str, required: set[str]) -> list[dict[str, Any]]:
    if table is None:
        return [
            {
                "id": "missing-lane-table",
                "status": "hold",
                "path": path,
                "summary": f"required lane table is missing from {path}",
            }
        ]
    missing = sorted(required - set(table.headers))
    return [
        {
            "id": "missing-lane-column",
            "status": "hold",
            "path": path,
            "summary": f"lane table is missing required columns: {', '.join(missing)}",
        }
    ] if missing else []


def lane_rows(table: MarkdownTable | None) -> list[dict[str, str]]:
    if table is None:
        return []
    return [row for row in table.rows if not is_placeholder(row.get("lane", ""))]


def lane_status(row: dict[str, str]) -> str:
    return row.get("status", "").casefold()


def is_active_lane(row: dict[str, str]) -> bool:
    return lane_status(row) in ACTIVE_STATUSES


def is_parked_lane(row: dict[str, str]) -> bool:
    return lane_status(row) in PARKED_STATUSES


def lock_scope(row: dict[str, str]) -> str:
    return normalize_value(row.get("lock_scope", ""))


def lock_is_broad(scope: str) -> bool:
    normalized = scope.casefold()
    return normalized in BROAD_LOCK_SCOPES or "whole repo" in normalized or "entire repo" in normalized


def lock_parts(scope: str) -> set[str]:
    if is_placeholder(scope):
        return set()
    separators = [",", ";", "\n"]
    parts = [scope]
    for separator in separators:
        parts = [piece for part in parts for piece in part.split(separator)]
    return {normalize_value(part).casefold().replace("\\", "/") for part in parts if not is_placeholder(part)}


def scopes_overlap(left: str, right: str) -> bool:
    left_parts = lock_parts(left)
    right_parts = lock_parts(right)
    for left_part in left_parts:
        for right_part in right_parts:
            if left_part == right_part:
                return True
            if left_part and right_part and (left_part.startswith(f"{right_part}/") or right_part.startswith(f"{left_part}/")):
                return True
    return False


def build_lane_audit(root: Path | str) -> dict[str, Any]:
    project = Path(root).resolve()
    team_tables = parse_markdown_tables(project / TEAM_BOARD, TEAM_BOARD)
    registry_tables = parse_markdown_tables(project / LANE_REGISTRY, LANE_REGISTRY)
    handoff_tables = parse_markdown_tables(project / HANDOFF_LOG, HANDOFF_LOG)
    team_table = find_lane_table(team_tables)
    registry_table = find_lane_table(registry_tables)
    handoff_table = find_handoff_table(handoff_tables)
    findings: list[dict[str, Any]] = []

    required_lane_columns = {"lane", "status", "lock_scope", "depends_on", "wave_id", "resume_condition"}
    findings.extend(required_column_findings(team_table, TEAM_BOARD, required_lane_columns))
    findings.extend(required_column_findings(registry_table, LANE_REGISTRY, required_lane_columns))
    if handoff_table is None:
        findings.append(
            {
                "id": "missing-handoff-table",
                "status": "hold",
                "path": HANDOFF_LOG,
                "summary": "handoff-log is missing a handoff table with expected return conditions",
            }
        )

    registry_rows = lane_rows(registry_table)
    team_rows = lane_rows(team_table)
    audit_rows = registry_rows or team_rows
    active_rows = [row for row in audit_rows if is_active_lane(row)]
    parked_rows = [row for row in audit_rows if is_parked_lane(row)]

    for row in audit_rows:
        lane = row.get("lane", "unknown")
        scope = lock_scope(row)
        if not is_placeholder(scope) and lock_is_broad(scope):
            findings.append(
                {
                    "id": "broad-lock-scope",
                    "status": "hold",
                    "path": LANE_REGISTRY if registry_rows else TEAM_BOARD,
                    "lane": lane,
                    "summary": f"lane {lane} uses overly broad lock scope: {scope}",
                }
            )
        if is_active_lane(row):
            if is_placeholder(row.get("wave_id", "")):
                findings.append(
                    {
                        "id": "missing-wave-id",
                        "status": "hold",
                        "path": LANE_REGISTRY if registry_rows else TEAM_BOARD,
                        "lane": lane,
                        "summary": f"active lane {lane} is missing wave_id",
                    }
                )
        if is_parked_lane(row) and is_placeholder(row.get("resume_condition", "")):
            findings.append(
                {
                    "id": "missing-resume-condition",
                    "status": "hold",
                    "path": LANE_REGISTRY if registry_rows else TEAM_BOARD,
                    "lane": lane,
                    "summary": f"parked lane {lane} is missing resume_condition",
                }
            )

    for index, left in enumerate(active_rows):
        for right in active_rows[index + 1 :]:
            if scopes_overlap(lock_scope(left), lock_scope(right)):
                findings.append(
                    {
                        "id": "lane-lock-conflict",
                        "status": "hold",
                        "path": LANE_REGISTRY if registry_rows else TEAM_BOARD,
                        "lanes": [left.get("lane", "unknown"), right.get("lane", "unknown")],
                        "summary": (
                            f"active lanes {left.get('lane', 'unknown')} and {right.get('lane', 'unknown')} "
                            "touch overlapping lock scopes"
                        ),
                    }
                )

    if handoff_table is not None:
        for row in handoff_table.rows:
            if is_placeholder(row.get("from", "")) and is_placeholder(row.get("to", "")):
                continue
            if is_placeholder(row.get("expected_return_condition", "")):
                findings.append(
                    {
                        "id": "missing-handoff-return-condition",
                        "status": "hold",
                        "path": HANDOFF_LOG,
                        "lane": row.get("lane", "unknown"),
                        "summary": "handoff row is missing expected return condition",
                    }
                )

    status = "hold" if findings else "pass"
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "project_path": str(project),
        "summary": {
            "active_lanes": len(active_rows),
            "parked_lanes": len(parked_rows),
            "findings": len(findings),
            "conflicts": sum(1 for finding in findings if finding["id"] == "lane-lock-conflict"),
            "broad_locks": sum(1 for finding in findings if finding["id"] == "broad-lock-scope"),
            "missing_resume_conditions": sum(1 for finding in findings if finding["id"] == "missing-resume-condition"),
            "incomplete_handoffs": sum(1 for finding in findings if finding["id"] == "missing-handoff-return-condition"),
        },
        "findings": findings,
    }


def render_lane_audit(report: dict[str, Any]) -> str:
    lines = [
        "Relay-kit lane audit",
        f"- status: {report['status']}",
        f"- active lanes: {report['summary']['active_lanes']}",
        f"- parked lanes: {report['summary']['parked_lanes']}",
        f"- findings: {report['summary']['findings']}",
    ]
    for finding in report.get("findings", []):
        lines.append(f"  - {finding.get('summary', finding.get('id', 'finding'))}")
    return "\n".join(lines)


def write_lane_audit(root: Path | str, report: dict[str, Any], output_file: Path | str | None = None) -> Path:
    project = Path(root).resolve()
    target = Path(output_file) if output_file else project / ".relay-kit" / "lanes" / "lane-audit.json"
    if not target.is_absolute():
        target = project / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return target
