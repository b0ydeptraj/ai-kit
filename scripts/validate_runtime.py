#!/usr/bin/env python3
"""Validate Relay-kit runtime integrity for the post-cutover model."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from relay_kit_v3.adapters import ADAPTER_TARGETS
from relay_kit_v3.generator import BUNDLES
from relay_kit_v3.registry.skills import ALL_V3_SKILLS
from relay_kit_compat import (
    CANONICAL_ARTIFACT_ROOT,
    CANONICAL_ENTRYPOINT,
    CANONICAL_LEGACY_ENTRYPOINT,
    GENERIC_CANONICAL_DIR,
)

ALL_TARGETS = [".claude/skills", ".agent/skills", ".codex/skills"]
EXPECTED_RUNTIME_SKILLS = set(ALL_V3_SKILLS.keys())
ROUND4_DISCIPLINE_SKILLS = {
    "root-cause-debugging",
    "evidence-before-completion",
    "test-first-development",
    "srs-clarifier",
}
RUNTIME_ALIAS_SKILLS = {
    "brainstorm",
    "build-it",
    "debug-systematically",
    "prove-it",
    "ready-check",
    "review-pr",
    "start-here",
    "write-steps",
}
BASELINE_DISCIPLINE_APPROVED = {
    "root-cause-debugging",
    "evidence-before-completion",
}
ACTIVE_VALIDATION_BUNDLES = ("round4", "discipline-utilities", "srs-first", "baseline")


def fail(message: str) -> None:
    raise AssertionError(message)


def run_command(command: list[str], label: str, *, cwd: Path = REPO_ROOT) -> str:
    env = dict(os.environ)
    env["RELAY_KIT_CYCLE_SOURCE"] = "validate_runtime"
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    if result.returncode != 0:
        fail(
            f"{label} failed:\n"
            f"command: {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result.stdout


def run_cli(script_name: str, *args: str) -> str:
    return run_command([sys.executable, str(REPO_ROOT / script_name), *args], script_name)


def run_public_cli(*args: str) -> str:
    return run_command(
        [sys.executable, str(REPO_ROOT / "relay_kit_public_cli.py"), *args],
        "relay_kit_public_cli.py",
    )


def run_helper_script(script_relative_path: str, *args: str) -> str:
    return run_command(
        [sys.executable, str(REPO_ROOT / script_relative_path), *args],
        script_relative_path,
    )


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
    run_command(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "skill_gauntlet.py"),
            str(REPO_ROOT),
            "--strict",
        ],
        "skill_gauntlet",
    )


def validate_migration_guard() -> None:
    run_command(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "migration_guard.py"),
            str(REPO_ROOT),
            "--strict",
        ],
        "migration_guard",
    )


def validate_srs_guard() -> None:
    run_command(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "srs_guard.py"),
            str(REPO_ROOT),
            "--strict",
        ],
        "srs_guard",
    )


def validate_prompt_fidelity_guard() -> None:
    run_command(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "prompt_fidelity_guard.py"),
            str(REPO_ROOT),
            "--strict",
        ],
        "prompt_fidelity_guard",
    )


def validate_context_continuity_utility() -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="relay-kit-continuity-"))
    try:
        run_helper_script(
            "scripts/context_continuity.py",
            "checkpoint",
            str(temp_dir),
            "--objective",
            "runtime validation",
            "--lane",
            "primary",
            "--next-step",
            "run qa gate",
        )
        run_helper_script("scripts/context_continuity.py", "rehydrate", str(temp_dir))
        run_helper_script("scripts/context_continuity.py", "diff-since-last", str(temp_dir))
        run_helper_script(
            "scripts/context_continuity.py",
            "handoff",
            str(temp_dir),
            "--reason",
            "validate-runtime",
            "--receiver",
            "qa",
        )
        manifest = temp_dir / CANONICAL_ARTIFACT_ROOT / "state" / "context-manifest.json"
        ledger = temp_dir / CANONICAL_ARTIFACT_ROOT / "state" / "session-ledger.jsonl"
        handoff_dir = temp_dir / CANONICAL_ARTIFACT_ROOT / "handoffs"
        if not manifest.exists():
            fail("context_continuity checkpoint did not create context-manifest.json")
        if not ledger.exists():
            fail("context_continuity checkpoint did not create session-ledger.jsonl")
        handoffs = list(handoff_dir.glob("*.md"))
        if not handoffs:
            fail("context_continuity handoff did not create a handoff markdown file")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


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
    adapter_sets = {target: skill_dirs(REPO_ROOT, target) for target in ALL_TARGETS}
    reference_target, reference_set = next(iter(adapter_sets.items()))
    for target, current_set in adapter_sets.items():
        assert_set(
            f"checked-in runtime parity vs {reference_target} for {target}",
            current_set,
            reference_set,
        )

    expected_runtime = EXPECTED_RUNTIME_SKILLS | RUNTIME_ALIAS_SKILLS
    for target, current_set in adapter_sets.items():
        assert_set(f"checked-in runtime exact set for {target}", current_set, expected_runtime)


def validate_skill_reachability() -> None:
    inbound = {name: 0 for name in ALL_V3_SKILLS}
    for spec in ALL_V3_SKILLS.values():
        for next_step in spec.next_steps:
            if next_step in inbound:
                inbound[next_step] += 1
    orphans = sorted(name for name, count in inbound.items() if count == 0)
    if orphans:
        fail(f"skill routing orphan detected: {orphans}")


def validate_bundle_identity() -> None:
    signatures: dict[tuple[str, ...], str] = {}
    for bundle in ACTIVE_VALIDATION_BUNDLES:
        signature = tuple(sorted(BUNDLES[bundle]))
        previous = signatures.get(signature)
        if previous is not None:
            fail(f"bundle identity collision: {previous} and {bundle} emit identical skill sets")
        signatures[signature] = bundle


def validate_runtime_core_tests() -> None:
    run_command([sys.executable, "-m", "pytest", "-q", "tests"], "runtime core pytest")


def validate_adapter_targets() -> None:
    if ADAPTER_TARGETS["all"] != ALL_TARGETS:
        fail(f"ADAPTER_TARGETS['all'] drifted: {ADAPTER_TARGETS['all']}")
    if ADAPTER_TARGETS["antigravity"] != [".agent/skills"]:
        fail(f"ADAPTER_TARGETS['antigravity'] drifted: {ADAPTER_TARGETS['antigravity']}")
    if ADAPTER_TARGETS["generic"] != [GENERIC_CANONICAL_DIR]:
        fail(f"ADAPTER_TARGETS['generic'] drifted: {ADAPTER_TARGETS['generic']}")


def validate_list_output() -> None:
    output = run_cli(CANONICAL_ENTRYPOINT, "--list-skills")
    for bundle in ACTIVE_VALIDATION_BUNDLES:
        if bundle not in output:
            fail(f"{CANONICAL_ENTRYPOINT} --list-skills output is missing bundle: {bundle}")


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
            "relay_kit.py",
            ".relay-kit-prompts",
            ".relay-kit/",
        ],
    )
    assert_contains(
        REPO_ROOT / "skills.manifest.yaml",
        [
            ".claude/skills",
            ".agent/skills",
            ".codex/skills",
            "discipline-utilities",
            "baseline",
            ".relay-kit/state/workflow-state.md",
        ],
    )
    assert_contains(
        REPO_ROOT / ".relay-kit" / "docs" / "bundle-gating.md",
        ["discipline-utilities", "baseline"],
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

        if bundle == "baseline":
            current = generated_sets[ALL_TARGETS[0]]
            missing = BASELINE_DISCIPLINE_APPROVED - current
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
                    "srs-clarifier",
                },
            )

        bundle_gating_doc = temp_dir / CANONICAL_ARTIFACT_ROOT / "docs" / "bundle-gating.md"
        if bundle_gating_doc.exists():
            assert_contains(bundle_gating_doc, ["discipline-utilities", "baseline"])
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
        if set(canonical) != expected_files:
            missing = sorted(expected_files - set(canonical))
            extra = sorted(set(canonical) - expected_files)
            fail(f"{bundle} generic prompt set mismatch. Missing: {missing or '-'} Extra: {extra or '-'}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def validate_legacy_generation() -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="relay-kit-legacy-generic-"))
    try:
        run_cli(
            CANONICAL_LEGACY_ENTRYPOINT,
            str(temp_dir),
            "--kit",
            "python",
            "--skills",
            "project-architecture",
            "--ai",
            "generic",
        )
        canonical = prompt_files(temp_dir, GENERIC_CANONICAL_DIR)
        expected = {"project-architecture.md"}
        if set(canonical) != expected:
            fail(
                f"{CANONICAL_LEGACY_ENTRYPOINT} legacy generic output mismatch. "
                f"Expected {sorted(expected)}, got {sorted(canonical)}"
            )
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
            if not (temp_dir / CANONICAL_ARTIFACT_ROOT).exists():
                fail(f"Public wrapper failed to emit {CANONICAL_ARTIFACT_ROOT} artifacts for --{adapter}")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def main() -> int:
    validate_adapter_targets()
    validate_list_output()
    validate_checked_in_runtime()
    validate_skill_reachability()
    validate_bundle_identity()
    assert_skill_descriptions_trigger_first()
    validate_skill_gauntlet()
    validate_context_continuity_utility()
    validate_migration_guard()
    validate_srs_guard()
    validate_prompt_fidelity_guard()
    validate_checked_in_docs()
    for bundle in ACTIVE_VALIDATION_BUNDLES:
        validate_generated_bundle(bundle)
        validate_generated_generic_bundle(bundle)
    validate_legacy_generation()
    validate_public_wrapper_surface()
    validate_runtime_core_tests()
    print("Runtime validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



