from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import relay_kit_public_cli
from relay_kit_v3 import commercial_dossier


def ready_readiness(root: Path, profile: str, skip_tests: bool) -> dict[str, Any]:
    return {
        "schema_version": "relay-kit.readiness-report.v1",
        "status": "pass",
        "verdict": "commercial-ready-candidate",
        "profile": profile,
        "project_path": str(root),
        "findings": [],
    }


def complete_publication(root: Path, trail_file: str | None) -> dict[str, Any]:
    return {
        "schema_version": "relay-kit.publication-trail-status.v1",
        "status": "complete",
        "project_path": str(root),
        "trail_file": str(trail_file or root / ".relay-kit" / "release" / "publication-trail.json"),
        "summary": {"complete": 7, "pending": 0, "not_observable": 0, "failed": 0, "total": 7},
        "findings": [],
    }


def published_package_index(root: Path, channel: str, package_url: str | None) -> dict[str, Any]:
    return {
        "schema_version": "relay-kit.package-index-check.v1",
        "status": "published",
        "project_path": str(root),
        "channel": channel,
        "package_url": package_url,
        "target_version": "3.3.0",
        "latest_version": "3.3.0",
        "target_file_count": 2,
        "findings": [],
    }


def ready_triage(root: Path, request_file: str | None, bundle_file: str | None) -> dict[str, Any]:
    return {
        "schema_version": "relay-kit.support-triage.v1",
        "status": "ready",
        "project_path": str(root),
        "severity": "P1",
        "request_file": str(request_file or root / ".relay-kit" / "support" / "support-request.json"),
        "bundle_file": str(bundle_file or root / ".relay-kit" / "support" / "support-bundle.json"),
        "findings": [],
    }


def passing_soak(root: Path, bundle_file: str | None) -> dict[str, Any]:
    return {
        "schema_version": "relay-kit.support-soak.v1",
        "status": "pass",
        "project_path": str(root),
        "bundle_file": str(bundle_file or root / ".relay-kit" / "support" / "support-bundle.json"),
        "case_count": 3,
        "findings": [],
    }


def test_commercial_dossier_ready_with_external_and_local_proof(tmp_path: Path) -> None:
    report = commercial_dossier.build_commercial_dossier(
        tmp_path,
        channel="pypi",
        ci_url="https://github.com/b0ydeptraj/Relay-kit/actions/runs/1",
        release_url="https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.3.0",
        package_url="https://pypi.org/project/relay-kit/3.3.0/",
        sla_url="https://example.com/relay-kit/support-sla",
        support_url="https://example.com/relay-kit/support-intake",
        legal_owner="ops@example.com",
        support_owner="support@example.com",
        readiness_builder=ready_readiness,
        publication_status_builder=complete_publication,
        package_index_builder=published_package_index,
        support_triage_builder=ready_triage,
        support_soak_builder=passing_soak,
    )

    assert report["schema_version"] == "relay-kit.commercial-dossier.v1"
    assert report["status"] == "ready"
    assert report["channel"] == "pypi"
    assert report["findings"] == []
    assert report["checks_by_id"]["readiness"]["status"] == "pass"
    assert report["checks_by_id"]["publication-status"]["status"] == "pass"
    assert report["checks_by_id"]["package-index"]["status"] == "pass"
    assert report["checks_by_id"]["support-triage"]["status"] == "pass"
    assert report["checks_by_id"]["support-soak"]["status"] == "pass"
    assert report["external_proof"]["legal_owner"] == "ops@example.com"


def test_commercial_dossier_holds_when_external_proof_is_missing(tmp_path: Path) -> None:
    report = commercial_dossier.build_commercial_dossier(
        tmp_path,
        channel="pypi",
        readiness_builder=ready_readiness,
        publication_status_builder=complete_publication,
        package_index_builder=published_package_index,
        support_triage_builder=ready_triage,
        support_soak_builder=passing_soak,
    )

    assert report["status"] == "hold"
    finding_gates = {finding["gate"] for finding in report["findings"]}
    assert {"external-ci", "release-url", "package-url", "sla-url", "support-url", "legal-owner", "support-owner"} <= finding_gates
    assert any("Attach green remote CI URL" in action for action in report["next_actions"])


def test_commercial_dossier_holds_when_local_gate_is_not_ready(tmp_path: Path) -> None:
    def limited_readiness(root: Path, profile: str, skip_tests: bool) -> dict[str, Any]:
        payload = ready_readiness(root, profile, skip_tests)
        payload["verdict"] = "limited-beta"
        return payload

    report = commercial_dossier.build_commercial_dossier(
        tmp_path,
        channel="pypi",
        ci_url="https://github.com/b0ydeptraj/Relay-kit/actions/runs/1",
        release_url="https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.3.0",
        package_url="https://pypi.org/project/relay-kit/3.3.0/",
        sla_url="https://example.com/relay-kit/support-sla",
        support_url="https://example.com/relay-kit/support-intake",
        legal_owner="ops@example.com",
        support_owner="support@example.com",
        readiness_builder=limited_readiness,
        publication_status_builder=complete_publication,
        package_index_builder=published_package_index,
        support_triage_builder=ready_triage,
        support_soak_builder=passing_soak,
    )

    assert report["status"] == "hold"
    assert report["checks_by_id"]["readiness"]["status"] == "hold"
    assert any(finding["gate"] == "readiness" for finding in report["findings"])


def test_commercial_dossier_holds_when_package_index_is_not_published(tmp_path: Path) -> None:
    def missing_package_index(root: Path, channel: str, package_url: str | None) -> dict[str, Any]:
        payload = published_package_index(root, channel, package_url)
        payload["status"] = "hold"
        payload["findings"] = [{"gate": "package-index-version", "status": "hold", "summary": "target missing"}]
        return payload

    report = commercial_dossier.build_commercial_dossier(
        tmp_path,
        channel="pypi",
        ci_url="https://github.com/b0ydeptraj/Relay-kit/actions/runs/1",
        release_url="https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.3.0",
        package_url="https://pypi.org/project/relay-kit/3.3.0/",
        sla_url="https://example.com/relay-kit/support-sla",
        support_url="https://example.com/relay-kit/support-intake",
        legal_owner="ops@example.com",
        support_owner="support@example.com",
        readiness_builder=ready_readiness,
        publication_status_builder=complete_publication,
        package_index_builder=missing_package_index,
        support_triage_builder=ready_triage,
        support_soak_builder=passing_soak,
    )

    assert report["status"] == "hold"
    assert report["checks_by_id"]["package-index"]["status"] == "hold"
    assert any(finding["gate"] == "package-index" for finding in report["findings"])


def test_write_commercial_dossier_uses_default_artifact_path(tmp_path: Path) -> None:
    report = commercial_dossier.build_commercial_dossier(
        tmp_path,
        channel="internal",
        ci_url="https://example.com/ci",
        package_url="https://example.com/packages/relay-kit",
        sla_url="https://example.com/sla",
        support_url="https://example.com/support",
        legal_owner="ops@example.com",
        support_owner="support@example.com",
        readiness_builder=ready_readiness,
        publication_status_builder=complete_publication,
        support_triage_builder=ready_triage,
        support_soak_builder=passing_soak,
    )

    output = commercial_dossier.write_commercial_dossier(tmp_path, report)
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert output == tmp_path / ".relay-kit" / "commercial" / "commercial-dossier.json"
    assert payload["schema_version"] == "relay-kit.commercial-dossier.v1"
    assert payload["status"] == "ready"


def test_public_cli_commercial_dossier_json_and_strict(monkeypatch, tmp_path: Path, capsys) -> None:
    def fake_build(project_path: str, **kwargs: Any) -> dict[str, Any]:
        assert Path(project_path) == tmp_path
        assert kwargs["channel"] == "pypi"
        assert kwargs["ci_url"] == "https://example.com/ci"
        return {
            "schema_version": "relay-kit.commercial-dossier.v1",
            "status": "hold",
            "project_path": str(tmp_path),
            "findings": [{"gate": "package-url", "status": "hold", "summary": "missing package URL"}],
        }

    def fake_write(project_path: str, report: dict[str, Any], *, output_file: str | None = None) -> Path:
        return tmp_path / ".relay-kit" / "commercial" / "commercial-dossier.json"

    monkeypatch.setattr(relay_kit_public_cli, "build_commercial_dossier", fake_build)
    monkeypatch.setattr(relay_kit_public_cli, "write_commercial_dossier", fake_write)

    exit_code = relay_kit_public_cli.main(
        [
            "commercial",
            "dossier",
            str(tmp_path),
            "--channel",
            "pypi",
            "--ci-url",
            "https://example.com/ci",
            "--strict",
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert payload["output_file"].endswith("commercial-dossier.json")
    assert payload["dossier"]["schema_version"] == "relay-kit.commercial-dossier.v1"
    assert payload["dossier"]["status"] == "hold"
