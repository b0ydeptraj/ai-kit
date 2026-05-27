from __future__ import annotations


PUBLIC_ENTRYPOINT_SHIMS: frozenset[str] = frozenset(
    {
        "start-here",
        "brainstorm",
        "write-steps",
        "build-it",
        "debug-systematically",
        "prove-it",
        "ready-check",
        "review-pr",
    }
)


PUBLIC_ENTRYPOINT_ROUTES: dict[str, str] = {
    "start-here": "workflow-router",
    "brainstorm": "brainstorm-hub",
    "write-steps": "scrum-master",
    "build-it": "developer",
    "debug-systematically": "debug-hub",
    "prove-it": "evidence-before-completion",
    "ready-check": "qa-governor",
    "review-pr": "review-hub",
}
