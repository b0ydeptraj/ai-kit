from __future__ import annotations

import json
from pathlib import Path

from relay_kit_v3.intent_enhancer import SCHEMA_VERSION, build_prompt_enhancement


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "relay_kit_v3" / "eval_fixtures" / "prompt_enhance_scenarios.json"


def combined_text(report: dict[str, object]) -> str:
    return json.dumps(report, ensure_ascii=False).lower()


def write_login_fixture(project: Path) -> None:
    auth_dir = project / "src" / "auth"
    auth_dir.mkdir(parents=True)
    (auth_dir / "LoginForm.tsx").write_text(
        "import { login } from './authService';\nexport function LoginForm() { return login('demo'); }\n",
        encoding="utf-8",
    )
    (auth_dir / "authService.ts").write_text(
        "export async function login(user: string) { return fetch('/login', { body: user }); }\n",
        encoding="utf-8",
    )
    (auth_dir / "login.test.ts").write_text(
        "import { login } from './authService';\ntest('login', () => login('demo'));\n",
        encoding="utf-8",
    )


def test_short_bug_prompt_routes_to_debug_without_overconfidence(tmp_path: Path) -> None:
    report = build_prompt_enhancement(tmp_path, prompt="sửa login")

    assert report["schema_version"] == SCHEMA_VERSION
    assert report["recommended_skill"] == "debug-hub"
    assert report["ask_or_act"] == "scout_first"
    assert report["read_first"]
    assert report["evidence_required"]
    assert report["context_index_status"] == "missing"
    assert report["domain_coverage"] == "unknown"
    assert report["unknown_domain_mode"] is True
    text = combined_text(report)
    assert "reproduction" in text
    assert "root-cause" in text
    assert "not a semantic context engine" in text
    assert "domain coverage" in text


def test_short_bug_prompt_includes_context_graph_hits_when_index_exists(tmp_path: Path) -> None:
    from relay_kit_v3.context_index import build_context_index, write_context_index

    write_login_fixture(tmp_path)
    write_context_index(tmp_path, build_context_index(tmp_path))

    report = build_prompt_enhancement(tmp_path, prompt="sửa login")

    assert report["recommended_skill"] == "debug-hub"
    assert report["context_index_status"] == "available"
    assert report["repo_profile"]["domain_coverage"] == "known-archetype"
    hit_paths = {hit["path"] for hit in report["context_hits"]}
    assert "src/auth/LoginForm.tsx" in hit_paths
    assert "src/auth/authService.ts" in hit_paths
    assert "src/auth/login.test.ts" in hit_paths
    read_first = set(report["read_first"])
    assert "src/auth/LoginForm.tsx" in read_first


def test_vague_deictic_prompt_asks_one_question(tmp_path: Path) -> None:
    report = build_prompt_enhancement(tmp_path, prompt="cái này có ổn không")

    assert report["recommended_skill"] == "review-hub"
    assert report["ask_or_act"] == "ask_one_question"
    assert report["domain_coverage"] == "unknown"
    assert "missing_context_question" in report
    assert "Which file" in str(report["missing_context_question"])


def test_read_only_code_mapping_does_not_route_to_developer(tmp_path: Path) -> None:
    report = build_prompt_enhancement(
        tmp_path,
        prompt="map command parsing architecture and test anchors without running code",
    )

    assert report["recommended_skill"] == "scout-hub"
    assert report["ask_or_act"] == "scout_first"


def test_prompt_enhance_scenarios_cover_short_real_prompts(tmp_path: Path) -> None:
    scenarios = json.loads(SCENARIOS.read_text(encoding="utf-8"))

    assert len(scenarios) >= 6
    for scenario in scenarios:
        report = build_prompt_enhancement(tmp_path, prompt=scenario["prompt"])
        text = combined_text(report)
        assert report["recommended_skill"] == scenario["expected_skill"], scenario["id"]
        assert report["ask_or_act"] == scenario["expected_ask_or_act"], scenario["id"]
        for term in scenario["expected_terms"]:
            assert str(term).lower() in text, f"{scenario['id']} missing {term}"
