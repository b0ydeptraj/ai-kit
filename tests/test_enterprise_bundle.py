from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from relay_kit_v3 import bundle_manifest
from relay_kit_v3.generator import BUNDLES
from relay_kit_v3.registry import BUNDLE_DOC_NAMES, REFERENCE_NAMES_FOR_BUNDLE, SUPPORT_REFERENCES, contract_names_for_bundle


ROOT = Path(__file__).resolve().parents[1]


def test_enterprise_bundle_extends_baseline_with_full_discipline_utilities() -> None:
    enterprise = BUNDLES["enterprise"]

    assert set(BUNDLES["baseline"]).issubset(enterprise)
    assert "test-first-development" in enterprise
    assert "policy-guard" in enterprise
    assert "release-readiness" in enterprise
    assert len(enterprise) == len(set(enterprise))


def test_enterprise_bundle_emits_governance_docs_and_all_references() -> None:
    docs = set(BUNDLE_DOC_NAMES["enterprise"])

    assert set(contract_names_for_bundle("baseline")) == set(contract_names_for_bundle("enterprise"))
    assert set(REFERENCE_NAMES_FOR_BUNDLE["enterprise"]) == set(SUPPORT_REFERENCES)
    assert {
        "bundle-gating",
        "planning-discipline",
        "parallel-execution",
        "workspace-isolation",
        "branch-completion",
        "review-loop",
        "enterprise-bundle",
    }.issubset(docs)


def test_bundle_manifest_includes_enterprise_bundle() -> None:
    manifest = bundle_manifest.create_manifest()

    assert "enterprise" in manifest["bundles"]
    assert "test-first-development" in manifest["bundles"]["enterprise"]["skills"]
    assert bundle_manifest.verify_manifest_payload(manifest).ok is True


def test_public_cli_generates_enterprise_bundle(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "relay_kit_public_cli.py",
            "init",
            str(tmp_path),
            "--codex",
            "--bundle",
            "enterprise",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / ".codex" / "skills" / "test-first-development" / "SKILL.md").exists()
    assert (tmp_path / ".relay-kit" / "docs" / "enterprise-bundle.md").exists()
    assert (tmp_path / ".relay-kit" / "references" / "security-patterns.md").exists()


def test_list_skills_shows_enterprise_bundle() -> None:
    result = subprocess.run(
        [sys.executable, "relay_kit_public_cli.py", "--list-skills"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "enterprise" in result.stdout
