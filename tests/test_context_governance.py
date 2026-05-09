from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3 import context_governance
from scripts import memory_search, runtime_doctor


def write_context_project(root: Path) -> None:
    state = root / ".relay-kit" / "state"
    contracts = root / ".relay-kit" / "contracts"
    state.mkdir(parents=True)
    contracts.mkdir(parents=True)
    (state / "workflow-state.md").write_text(
        "\n".join(
            [
                "# workflow-state",
                "## Current source of truth",
                "- Current main baseline after PR #82: `abc123`.",
                "- Main CI after PR #82: https://github.com/example/actions/runs/1, conclusion `success`.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (state / "team-board.md").write_text("# team-board\n\n## Lanes\nnone\n", encoding="utf-8")
    (state / "lane-registry.md").write_text("# lane-registry\n\n## Active lanes\nnone\n", encoding="utf-8")
    (state / "handoff-log.md").write_text("# handoff-log\n\n## Handoff entries\nnone\n", encoding="utf-8")
    (contracts / "project-context.md").write_text("# project-context\n\nAuthoritative architecture note.\n", encoding="utf-8")
    (contracts / "qa-report.md").write_text("# qa-report\n\nRecent evidence.\n", encoding="utf-8")


def test_context_audit_classifies_authoritative_recent_and_missing_sources(tmp_path: Path) -> None:
    write_context_project(tmp_path)
    (tmp_path / ".relay-kit" / "contracts" / "qa-report.md").unlink()

    report = context_governance.build_context_audit(tmp_path, stale_days=30)

    assert report["schema_version"] == "relay-kit.context-audit.v1"
    assert report["status"] == "hold"
    assert report["summary"]["missing_sources"] == 1
    sources = {source["path"]: source for source in report["sources"]}
    assert sources[".relay-kit/state/workflow-state.md"]["source_type"] == "authoritative"
    assert sources[".relay-kit/contracts/project-context.md"]["source_type"] == "authoritative"
    assert sources[".relay-kit/contracts/qa-report.md"]["source_type"] == "missing"
    assert sources[".relay-kit/state/team-board.md"]["source_type"] == "recent"


def test_context_audit_marks_stale_sources_by_age(tmp_path: Path) -> None:
    write_context_project(tmp_path)
    old = datetime.now(timezone.utc) - timedelta(days=45)
    old_ts = old.timestamp()
    target = tmp_path / ".relay-kit" / "state" / "team-board.md"
    target.touch()
    import os

    os.utime(target, (old_ts, old_ts))

    report = context_governance.build_context_audit(tmp_path, stale_days=30)
    team_source = next(source for source in report["sources"] if source["path"] == ".relay-kit/state/team-board.md")

    assert team_source["source_type"] == "stale"
    assert team_source["stale"] is True
    assert report["summary"]["stale_sources"] >= 1


def test_public_cli_context_audit_outputs_json_and_strict_status(tmp_path: Path, capsys) -> None:
    write_context_project(tmp_path)

    exit_code = relay_kit_public_cli.main(["context", "audit", str(tmp_path), "--strict", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "pass"
    assert payload["summary"]["authoritative_sources"] >= 2


def test_memory_search_json_includes_confidence_source_type_and_age(tmp_path: Path) -> None:
    write_context_project(tmp_path)
    matches = memory_search.find_matches(
        paths=memory_search.candidate_files(tmp_path, "all", []),
        query="architecture",
        context=0,
        max_results=5,
        base=tmp_path,
        intent="decision",
        sort_mode="relevance",
        stale_days=30,
    )
    payload = json.loads(memory_search.render_json(matches, "architecture"))

    first = payload["matches"][0]
    assert first["source_type"] == "authoritative"
    assert first["confidence"] in {"high", "medium", "low"}
    assert isinstance(first["age_days"], int)
    assert first["stale_warning"] in {"", "stale source"}


def test_context_continuity_checkpoint_records_source_metadata(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/context_continuity.py",
            "checkpoint",
            str(tmp_path),
            "--objective",
            "phase 2 context governance",
            "--next-step",
            "run context audit",
            "--json",
        ],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)

    assert "sources" in payload
    assert payload["sources"]
    assert {"path", "source_type", "confidence", "age_days", "stale"} <= set(payload["sources"][0])


def test_runtime_doctor_detects_stale_main_pointer_when_on_main(tmp_path: Path) -> None:
    write_context_project(tmp_path)
    findings: list[str] = []

    runtime_doctor.check_stale_main_pointer(
        tmp_path,
        findings,
        mode="live",
        current_branch="main",
        head_sha="def456",
    )

    assert any("workflow-state main baseline is stale" in finding for finding in findings)


def test_runtime_doctor_skips_stale_main_pointer_when_ancestor_status_unknown(tmp_path: Path, monkeypatch) -> None:
    write_context_project(tmp_path)
    findings: list[str] = []
    monkeypatch.setattr(runtime_doctor, "current_git_branch", lambda _root: "main")
    monkeypatch.setattr(runtime_doctor, "current_git_head", lambda _root: "def456")
    monkeypatch.setattr(runtime_doctor, "is_ancestor", lambda _root, _ancestor, _head: None)

    runtime_doctor.check_stale_main_pointer(tmp_path, findings, mode="live")

    assert findings == []
