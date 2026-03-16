#!/usr/bin/env python3
"""Validate adapter parity and bundle gating for the active Relay-kit v3 runtime."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ai_kit_v3.adapters import ADAPTER_TARGETS
from ai_kit_v3.generator import BUNDLES
from ai_kit_v3.registry.skills import ALL_V3_SKILLS

ALL_TARGETS = [".claude/skills", ".agent/skills", ".codex/skills"]
EXPECTED_RUNTIME_SKILLS = set(ALL_V3_SKILLS.keys())
ROUND4_DISCIPLINE_SKILLS = {
    "root-cause-debugging",
    "evidence-before-completion",
    "test-first-development",
}
BASELINE_NEXT_APPROVED = {
    "root-cause-debugging",
    "evidence-before-completion",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def run_python_kit(*args: str) -> str:
    command = [sys.executable, str(REPO_ROOT / "python_kit.py"), *args]
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        fail(
            "python_kit.py failed:\n"
            f"command: {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result.stdout


def skill_dirs(base: Path, relative_dir: str) -> set[str]:
    target = base / Path(relative_dir)
    if not target.exists():
        fail(f"Missing runtime folder: {target}")
    return {entry.name for entry in target.iterdir() if entry.is_dir()}


def assert_set(name: str, actual: set[str], expected: set[str]) -> None:
    if actual == expected:
        return
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    fail(f"{name} mismatch. Missing: {missing or '-'} Extra: {extra or '-'}")


def assert_contains(path: Path, required_tokens: list[str]) -> None:
    content = path.read_text(encoding="utf-8")
    missing = [token for token in required_tokens if token not in content]
    if missing:
        fail(f"{path} is missing expected tokens: {missing}")


def validate_checked_in_runtime() -> None:
    adapter_sets = {target: skill_dirs(REPO_ROOT, target) & EXPECTED_RUNTIME_SKILLS for target in ALL_TARGETS}
    reference_target, reference_set = next(iter(adapter_sets.items()))
    for target, current_set in adapter_sets.items():
        assert_set(f"checked-in runtime parity vs {reference_target} for {target}", current_set, reference_set)


def validate_adapter_targets() -> None:
    expected = ALL_TARGETS
    actual = ADAPTER_TARGETS["all"]
    if actual != expected:
        fail(f"ADAPTER_TARGETS['all'] drifted. Expected {expected}, got {actual}")


def validate_list_output() -> None:
    output = run_python_kit("--list-skills")
    for bundle in ("round4", "discipline-utilities", "baseline", "baseline-next"):
        if bundle not in output:
            fail(f"--list-skills output is missing bundle: {bundle}")


def validate_checked_in_docs() -> None:
    assert_contains(
        REPO_ROOT / "README.md",
        ["`--ai all`", ".claude/skills", ".agent/skills", ".codex/skills", "baseline", "baseline-next"],
    )
    assert_contains(
        REPO_ROOT / "skills.manifest.yaml",
        [".claude/skills", ".agent/skills", ".codex/skills", "discipline-utilities", "baseline", "baseline-next"],
    )
    assert_contains(
        REPO_ROOT / ".ai-kit" / "docs" / "bundle-gating.md",
        ["discipline-utilities", "baseline", "baseline-next"],
    )


def validate_generated_bundle(bundle: str) -> None:
    expected_skills = set(BUNDLES[bundle])
    temp_dir = Path(tempfile.mkdtemp(prefix=f"relay-kit-{bundle}-"))
    try:
        run_python_kit(
            str(temp_dir),
            "--bundle",
            bundle,
            "--ai",
            "all",
            "--emit-contracts",
            "--emit-docs",
            "--emit-reference-templates",
        )

        generated_sets = {target: skill_dirs(temp_dir, target) for target in ALL_TARGETS}
        for target, current_set in generated_sets.items():
            assert_set(f"{bundle} generated skills for {target}", current_set, expected_skills)

        if bundle == "round4":
            leaked = generated_sets[ALL_TARGETS[0]] & ROUND4_DISCIPLINE_SKILLS
            if leaked:
                fail(f"round4 leaked discipline skills: {sorted(leaked)}")

        if bundle in {"baseline", "baseline-next"}:
            current = generated_sets[ALL_TARGETS[0]]
            missing = BASELINE_NEXT_APPROVED - current
            unexpected = current & {"test-first-development"}
            if missing or unexpected:
                fail(
                    f"{bundle} discipline mismatch. "
                    f"Missing approved: {sorted(missing) or '-'} "
                    f"Unexpected: {sorted(unexpected) or '-'}"
                )

        if bundle == "discipline-utilities":
            current = generated_sets[ALL_TARGETS[0]]
            assert_set(
                "discipline-utilities bundle",
                current,
                {
                    "root-cause-debugging",
                    "test-first-development",
                    "evidence-before-completion",
                },
            )

        bundle_gating_doc = temp_dir / ".ai-kit" / "docs" / "bundle-gating.md"
        if bundle_gating_doc.exists():
            assert_contains(bundle_gating_doc, ["discipline-utilities", "baseline", "baseline-next"])
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main() -> int:
    validate_adapter_targets()
    validate_list_output()
    validate_checked_in_runtime()
    validate_checked_in_docs()
    for bundle in ("round4", "discipline-utilities", "baseline", "baseline-next"):
        validate_generated_bundle(bundle)
    print("Runtime validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
