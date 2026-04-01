#!/usr/bin/env python3
"""Validate adapter parity and bundle gating for the active Relay-kit v3 runtime."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ai_kit_v3.adapters import ADAPTER_TARGETS
from ai_kit_v3.generator import BUNDLES
from ai_kit_v3.registry.skills import ALL_V3_SKILLS
from relay_kit_compat import (
    CANONICAL_ENTRYPOINT,
    COMPAT_ENTRYPOINT,
    GENERIC_CANONICAL_DIR,
    GENERIC_COMPAT_DIR,
)

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


def run_cli(script_name: str, *args: str) -> str:
    command = [sys.executable, str(REPO_ROOT / script_name), *args]
    env = dict(os.environ)
    env["RELAY_KIT_CYCLE_SOURCE"] = "validate_runtime"
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    if result.returncode != 0:
        fail(
            f"{script_name} failed:\n"
            f"command: {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result.stdout


def run_public_cli(*args: str) -> str:
    command = [sys.executable, str(REPO_ROOT / "relay_kit_public_cli.py"), *args]
    env = dict(os.environ)
    env["RELAY_KIT_CYCLE_SOURCE"] = "validate_runtime"
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    if result.returncode != 0:
        fail(
            "relay_kit_public_cli.py failed:\n"
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


def assert_skill_descriptions_trigger_first() -> None:
    skill_roots = [
        REPO_ROOT / ".claude" / "skills",
        REPO_ROOT / ".agent" / "skills",
        REPO_ROOT / ".codex" / "skills",
    ]
    bad_descriptions: list[str] = []
    for root in skill_roots:
        for skill_file in root.rglob("SKILL.md"):
            content = skill_file.read_text(encoding="utf-8")
            match = re.search(r"^description:\s*(.+)$", content, re.MULTILINE)
            if match is None:
                bad_descriptions.append(f"{skill_file}: missing description")
                continue
            description = match.group(1).strip()
            if not description.startswith("Use when "):
                bad_descriptions.append(f"{skill_file}: {description}")
    if bad_descriptions:
        preview = "\n".join(bad_descriptions[:10])
        fail(
            "Skill descriptions must use trigger-first wording that starts with "
            "`Use when ...`.\n"
            f"Examples of drift:\n{preview}"
        )


def validate_skill_gauntlet() -> None:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "skill_gauntlet.py"),
        str(REPO_ROOT),
        "--strict",
    ]
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        fail(
            "skill_gauntlet validation failed:\n"
            f"command: {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def assert_file_map(name: str, actual: dict[str, str], expected: dict[str, str]) -> None:
    actual_names = set(actual)
    expected_names = set(expected)
    if actual_names != expected_names:
        missing = sorted(expected_names - actual_names)
        extra = sorted(actual_names - expected_names)
        fail(f"{name} mismatch. Missing: {missing or '-'} Extra: {extra or '-'}")
    for key in sorted(expected_names):
        if actual[key] != expected[key]:
            fail(f"{name} content drift for {key}")


def prompt_files(base: Path, relative_dir: str) -> dict[str, str]:
    target = base / relative_dir
    if not target.exists():
        fail(f"Missing prompt folder: {target}")
    return {
        entry.name: entry.read_text(encoding="utf-8")
        for entry in target.iterdir()
        if entry.is_file() and entry.suffix == ".md"
    }


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
    antigravity_expected = [".agent/skills"]
    antigravity_actual = ADAPTER_TARGETS["antigravity"]
    if antigravity_actual != antigravity_expected:
        fail(
            "ADAPTER_TARGETS['antigravity'] drifted. "
            f"Expected {antigravity_expected}, got {antigravity_actual}"
        )
    if "gemini" in ADAPTER_TARGETS:
        fail("Legacy adapter key 'gemini' should not be present in active adapter targets.")
    generic_expected = [GENERIC_CANONICAL_DIR, GENERIC_COMPAT_DIR]
    generic_actual = ADAPTER_TARGETS["generic"]
    if generic_actual != generic_expected:
        fail(f"ADAPTER_TARGETS['generic'] drifted. Expected {generic_expected}, got {generic_actual}")


def validate_list_output() -> None:
    for script_name in (CANONICAL_ENTRYPOINT, COMPAT_ENTRYPOINT):
        output = run_cli(script_name, "--list-skills")
        for bundle in ("round4", "discipline-utilities", "baseline", "baseline-next"):
            if bundle not in output:
                fail(f"{script_name} --list-skills output is missing bundle: {bundle}")


def validate_checked_in_docs() -> None:
    assert_contains(
        REPO_ROOT / "README.md",
        [
            "`--ai all`",
            "`--antigravity`",
            ".claude/skills",
            ".agent/skills",
            ".codex/skills",
            "baseline",
            "baseline-next",
            "relay_kit.py",
            "python_kit.py",
            ".relay-kit-prompts",
            ".python-kit-prompts",
        ],
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
        run_cli(
            CANONICAL_ENTRYPOINT,
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


def validate_generated_generic_bundle(bundle: str) -> None:
    expected_files = {f"{name}.md" for name in BUNDLES[bundle]}
    temp_dir = Path(tempfile.mkdtemp(prefix=f"relay-kit-generic-{bundle}-"))
    try:
        run_cli(
            CANONICAL_ENTRYPOINT,
            str(temp_dir),
            "--bundle",
            bundle,
            "--ai",
            "generic",
        )
        canonical = prompt_files(temp_dir, GENERIC_CANONICAL_DIR)
        compat = prompt_files(temp_dir, GENERIC_COMPAT_DIR)
        assert_file_map(
            f"{bundle} generic prompt parity",
            canonical,
            compat,
        )
        if set(canonical) != expected_files:
            missing = sorted(expected_files - set(canonical))
            extra = sorted(set(canonical) - expected_files)
            fail(f"{bundle} generic prompt set mismatch. Missing: {missing or '-'} Extra: {extra or '-'}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def validate_legacy_generation() -> None:
    for script_name in (CANONICAL_ENTRYPOINT, COMPAT_ENTRYPOINT):
        temp_dir = Path(tempfile.mkdtemp(prefix=f"relay-kit-legacy-{Path(script_name).stem}-"))
        try:
            run_cli(
                script_name,
                str(temp_dir),
                "--legacy-kit",
                "python",
                "--skills",
                "project-architecture",
                "--ai",
                "generic",
            )
            canonical = prompt_files(temp_dir, GENERIC_CANONICAL_DIR)
            compat = prompt_files(temp_dir, GENERIC_COMPAT_DIR)
            expected = {"project-architecture.md"}
            assert_file_map(f"{script_name} legacy generic parity", canonical, compat)
            if set(canonical) != expected:
                fail(f"{script_name} legacy generic output mismatch. Expected {sorted(expected)}, got {sorted(canonical)}")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def validate_public_wrapper_surface() -> None:
    run_public_cli("--list-skills")
    for adapter, target in (
        ("codex", ".codex/skills"),
        ("claude", ".claude/skills"),
        ("antigravity", ".agent/skills"),
    ):
        temp_dir = Path(tempfile.mkdtemp(prefix=f"relay-kit-public-{adapter}-"))
        try:
            run_public_cli(str(temp_dir), f"--{adapter}")
            if not (temp_dir / target).exists():
                fail(f"Public wrapper failed to generate adapter target {target} for --{adapter}")
            if not (temp_dir / ".ai-kit").exists():
                fail(f"Public wrapper failed to emit .ai-kit artifacts for --{adapter}")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def main() -> int:
    validate_adapter_targets()
    validate_list_output()
    validate_checked_in_runtime()
    assert_skill_descriptions_trigger_first()
    validate_skill_gauntlet()
    validate_checked_in_docs()
    for bundle in ("round4", "discipline-utilities", "baseline", "baseline-next"):
        validate_generated_bundle(bundle)
        validate_generated_generic_bundle(bundle)
    validate_legacy_generation()
    validate_public_wrapper_surface()
    print("Runtime validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
