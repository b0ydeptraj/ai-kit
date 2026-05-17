from __future__ import annotations

import re
from typing import Mapping


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "before",
    "by",
    "for",
    "from",
    "has",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "this",
    "to",
    "with",
}


def tokenize(text: str) -> set[str]:
    tokens = {
        token.lower()
        for token in re.findall(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", text)
        if len(token) > 2
    }
    expanded: set[str] = set()
    for token in tokens:
        expanded.add(token)
        if "-" in token:
            expanded.update(part for part in token.split("-") if len(part) > 2)
    return {token for token in expanded if token not in STOPWORDS}


def skill_search_text(spec: object) -> str:
    return "\n".join(
        [
            spec.name.replace("-", " "),
            spec.description,
            spec.role,
            spec.layer,
            *spec.inputs,
            *spec.outputs,
            *spec.references,
            *spec.next_steps,
            spec.body,
        ]
    )


def skill_route_text(spec: object) -> str:
    return "\n".join(
        [
            spec.name.replace("-", " "),
            spec.description,
            spec.role,
            spec.layer,
            *spec.inputs,
            *spec.outputs,
            *spec.next_steps,
        ]
    )


def score_prompt_against_skill(prompt: str, spec: object) -> int:
    prompt_tokens = tokenize(prompt)
    if not prompt_tokens:
        return 0
    spec_tokens = tokenize(skill_route_text(spec))
    score = len(prompt_tokens & spec_tokens)

    prompt_lower = prompt.lower()
    for phrase_source, bonus in ((spec.name, 25), (spec.role, 20), (spec.layer, 10)):
        phrase = str(phrase_source).replace("-", " ").lower()
        if str(phrase_source).lower() in prompt_lower or phrase in prompt_lower:
            score += bonus

    description_tokens = tokenize(spec.description)
    score += len(prompt_tokens & description_tokens) * 2
    return score


def rank_prompt_routes(prompt: str, registry: Mapping[str, object]) -> list[tuple[int, str]]:
    ranked = [(score_prompt_against_skill(prompt, spec), name) for name, spec in registry.items()]
    return sorted(ranked, key=lambda item: (-item[0], item[1]))
