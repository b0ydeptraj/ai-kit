from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli


def test_service_boundary_report_passes_current_repo() -> None:
    from relay_kit_v3.service_boundaries import build_service_boundary_report

    report = build_service_boundary_report(Path.cwd())

    assert report["schema_version"] == "relay-kit.service-boundaries.v1"
    assert report["status"] == "pass"
    assert report["summary"]["boundary_count"] >= 7
    assert report["summary"]["findings"] == 0
    assert any(boundary["id"] == "public-cli" for boundary in report["boundaries"])


def test_service_boundary_report_flags_registry_importing_cli(tmp_path: Path) -> None:
    from relay_kit_v3.service_boundaries import build_service_boundary_report

    registry = tmp_path / "relay_kit_v3" / "registry"
    registry.mkdir(parents=True)
    (registry / "bad.py").write_text("import relay_kit_public_cli\n", encoding="utf-8")

    report = build_service_boundary_report(tmp_path)

    assert report["status"] == "hold"
    assert any(finding["id"] == "registry-imports-cli" for finding in report["findings"])


def test_service_boundary_report_flags_runtime_importing_scripts(tmp_path: Path) -> None:
    from relay_kit_v3.service_boundaries import build_service_boundary_report

    package = tmp_path / "relay_kit_v3"
    package.mkdir(parents=True)
    (package / "bad_runtime.py").write_text("from scripts import runtime_doctor\n", encoding="utf-8")

    report = build_service_boundary_report(tmp_path)

    assert report["status"] == "hold"
    assert any(finding["id"] == "runtime-imports-scripts" for finding in report["findings"])


def test_public_cli_service_boundaries_outputs_json(tmp_path: Path, capsys) -> None:
    (tmp_path / "relay_kit_v3").mkdir()

    exit_code = relay_kit_public_cli.main(["service", "boundaries", str(tmp_path), "--strict", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "pass"
    assert payload["summary"]["findings"] == 0
