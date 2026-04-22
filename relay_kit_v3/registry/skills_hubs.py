from __future__ import annotations

from textwrap import dedent
from typing import Dict

from .skill_models import SkillSpec

WORKFLOW_HUB_SKILLS: Dict[str, SkillSpec] = {
    "brainstorm-hub": SkillSpec(
        name="brainstorm-hub",
        description="Use when the request is still an idea, an opportunity, or a loosely described improvement. Guide early ideation and rough problem framing before formal planning exists.",
        role="ideation-hub",
        layer="layer-2-workflow-hubs",
        inputs=["user idea or opportunity", ".relay-kit/state/workflow-state.md", "any existing brief or context"],
        outputs=[".relay-kit/contracts/product-brief.md or a decision not to proceed"],
        references=[
            "Use analyst for structured discovery and pm only once the shape is coherent enough to plan.",
            "Prefer narrowing the problem over generating a giant feature wish list.",
        ],
        next_steps=["analyst", "pm", "research", "ux-structure", "aesthetic", "frontend-design", "ui-styling", "plan-hub", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Turn fuzzy idea energy into something the planning flow can actually use.

            ## What this hub does
            - Facilitate a short option scan.
            - Expose assumptions, success signals, and obvious constraints.
            - Decide whether to write or refresh `product-brief.md`.

            ## Exit conditions
            End with one of only three outcomes:
            1. a brief is ready for planning,
            2. the idea is too weak and should stop, or
            3. one specific question must be answered before planning continues.

            ## Decision hygiene
            - Name the trade-off that was chosen and one option explicitly rejected.
            - Flag assumptions that still need evidence and route them to research or analyst.
            - If UI quality is part of the goal, route through aesthetic/frontend-design/ui-styling before implementation.

            ## Ideation quality checks
            - Problem statement is specific enough to test.
            - Success signal is measurable, not aspirational.
            - At least one non-goal is explicit to constrain scope.
            - One risky assumption is called out for validation.
            - Next planning owner is explicit before handoff.
            """
        ).strip(),
    ),
    "scout-hub": SkillSpec(
        name="scout-hub",
        description="Use when the repo area is unfamiliar, stale, or likely to drift from existing assumptions. Reconnoiter the codebase and refresh living references before planning, debugging, or review work continues.",
        role="recon-hub",
        layer="layer-2-workflow-hubs",
        inputs=["repo tree and relevant files", ".relay-kit/contracts/project-context.md", ".relay-kit/state/workflow-state.md"],
        outputs=[".relay-kit/contracts/project-context.md", ".relay-kit/references/*.md as needed", ".relay-kit/contracts/investigation-notes.md when the work starts from a failure"],
        references=[
            "Use project-architecture, dependency-management, api-integration, data-persistence, and testing-patterns as living references.",
            "Prefer concrete file paths, commands, and entrypoints over summaries.",
            "When the problem starts from a failure, capture findings in investigation-notes.",
            "Run a freshness pass first: stale assumptions or stale artifacts should be called out explicitly before planning.",
        ],
        next_steps=["project-architecture", "dependency-management", "api-integration", "data-persistence", "testing-patterns", "doc-pointers", "repo-map", "memory-search", "impact-radar", "runtime-doctor", "handoff-context", "plan-hub", "debug-hub", "review-hub", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Gather the minimum reliable context the next lane needs so nobody plans or fixes from a false mental model.

            ## Mandatory behavior
            1. Refresh `project-context.md` when architecture, tooling, or domain constraints are unclear.
            2. Refresh only the reference files actually relevant to the active lane.
            3. Add file paths, commands, or modules whenever possible.
            4. Record freshness signals (last-updated clues, stale docs, stale notes) before recommending a path.
            5. If a failure is being investigated, start `investigation-notes.md` with reproduction steps and evidence.

            ## Output contract
            Name exactly what became clearer, what is still unknown, which sources might be stale, and which hub or specialist should use the refreshed context next.

            ## Recon guardrails
            - Prioritize support skills that match the active subsystem rather than scanning everything.
            - Record one concrete risk and one safe next step before leaving scout-hub.
            - If findings show architectural drift, route to plan-hub with dependency and boundary notes.

            ## Recon checklist
            - Entry points and key modules are named with file paths.
            - Dependency direction is captured for touched subsystems.
            - Data/API boundaries are listed when relevant.
            - Stale docs are flagged with recommended refresh owner.
            - The next hub is selected with a clear reason.
            """
        ).strip(),
    ),
    "plan-hub": SkillSpec(
        name="plan-hub",
        description="Use when work is larger than quick-flow or when existing planning artifacts are stale or incomplete. Run the planning chain from SRS-first or brief to PRD to architecture to stories without losing context between roles.",
        role="planning-hub",
        layer="layer-2-workflow-hubs",
        inputs=["workflow-state", "existing srs-spec, brief, PRD, architecture, or epics if present", "project-context", ".relay-kit/state/srs-policy.json when present"],
        outputs=["srs-spec when policy requires it", "product-brief, PRD, architecture, epics, and stories or tech-spec depending track"],
        references=[
            "Call only the roles needed to close the current planning gap.",
            "Use scout-hub first if the current codebase context is too weak to plan safely.",
            "Route to review-hub if artifacts disagree with one another.",
            "Use `.relay-kit/docs/planning-discipline.md` to keep plans artifact-first, bite-sized, and verification-aware.",
            "Lock key UX, API, and behavior assumptions before story slicing so implementation does not drift.",
            "When SRS-first is enabled, call `srs-clarifier` before PM readiness if actors/use cases/pre-post/exception flows are incomplete.",
        ],
        next_steps=["analyst", "research", "pm", "architect", "mermaid-diagrams", "srs-clarifier", "scrum-master", "developer", "review-hub"],
        body=dedent(
            """\
            # Mission
            Sequence the planning roles so the lane produces buildable artifacts instead of disconnected documents.

            ## Mandatory order
            - if SRS-first policy is enabled for this track, use `srs-clarifier` first to create or repair `srs-spec.md`
            - use `analyst` if the brief is missing or stale
            - use `pm` if requirements, acceptance criteria, or slice order are missing
            - use `architect` if technical boundaries or readiness are unclear
            - use `scrum-master` when work must be cut into stories or a quick spec

            ## Planning gate
            Stop and route to `review-hub` when product, architecture, and story artifacts disagree.
            If SRS-first is enabled, block planning readiness until `srs-spec.md` contains actors, UC-IDs, preconditions, postconditions, and exception flows.
            Route to `developer` only when the active story or tech-spec is ready for implementation.

            ## Planning discipline
            - Prefer small, verifiable slices over broad task bundles.
            - Every story or quick spec should name what will prove it is done.
            - If the work spans unrelated subsystems, split the plan before implementation starts.
            - Include dependency metadata (`depends_on`, parallel-safe yes/no, first verification command) so execution can run in controlled waves.
            - If slicing yields zero executable stories, block and escalate instead of declaring planning complete.
            """
        ).strip(),
    ),
    "debug-hub": SkillSpec(
        name="debug-hub",
        description="Use when work starts from a regression, flaky behavior, or an unexplained mismatch between expected and actual behavior. Triage failures, collect evidence, and decide whether the issue is a bug, a test problem, or a planning problem.",
        role="debug-hub",
        layer="layer-2-workflow-hubs",
        inputs=["failing behavior", "logs, traces, or test output", "workflow-state", "relevant references"],
        outputs=[".relay-kit/contracts/investigation-notes.md", ".relay-kit/contracts/tech-spec.md when a fix path is clear"],
        references=[
            "When discipline utilities are installed, use `root-cause-debugging` before touching code.",
            "Use testing-patterns and problem-solving to turn evidence into a fix path.",
            "Root cause beats guess-and-patch.",
            "Escalate to plan-hub if the 'bug' is actually an unclear requirement or architectural mismatch.",
        ],
        next_steps=["root-cause-debugging", "sequential-thinking", "problem-solving", "browser-inspector", "multimodal-evidence", "memory-search", "runtime-doctor", "fix-hub", "test-hub", "plan-hub", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Turn a symptom into evidence and a decision, not into random edits.

            ## Mandatory behavior
            1. Reproduce the issue or explain why reproduction is not yet reliable.
            2. Write `investigation-notes.md` with evidence, likely root cause, and non-causes ruled out.
            3. If available, run the `root-cause-debugging` discipline before proposing a fix.
            4. Decide whether the next move is:
               - `fix-hub` for a real fix,
               - `test-hub` for missing or weak evidence,
               - `plan-hub` when the issue is upstream ambiguity.

            ## Failure decision rules
            - If no evidence changed after two loops, escalate to scout-hub for context refresh.
            - If root cause crosses subsystem boundaries, route to workflow-router for lane reclassification.
            - Capture the exact command or artifact that disproved each rejected hypothesis.

            ## Evidence quality bar
            - Reproduction signal is stable across at least one rerun.
            - Notes include what changed between attempts.
            - Proposed fix path names impacted files and boundary risks.
            - Missing evidence is explicit, not implied.
            - Next hub is chosen from evidence, not preference.
            """
        ).strip(),
    ),
    "fix-hub": SkillSpec(
        name="fix-hub",
        description="Use when debug-hub has validated findings or when a change request is already sharply bounded. Turn those findings into a minimal implementation path and hand off to the developer loop.",
        role="fix-hub",
        layer="layer-2-workflow-hubs",
        inputs=["tech-spec or story", "investigation-notes when debugging", "architecture and project-context when relevant"],
        outputs=["refined tech-spec or story", "implementation handoff to developer", "updated workflow-state"],
        references=[
            "Keep the fix surface as small as possible.",
            "Use developer plus execution-loop for execution, not as a replacement for scoping.",
            "If the fix expands the contract or architecture, route back through workflow-router or plan-hub.",
        ],
        next_steps=["project-architecture", "dependency-management", "api-integration", "data-persistence", "developer", "execution-loop", "test-first-development", "accessibility-review", "handoff-context", "test-hub", "review-hub", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Convert a known problem into a bounded implementation path that can be executed safely.

            ## Mandatory behavior
            1. Update the active story or tech-spec with the real files, boundaries, and verification steps.
            2. Name what must not change while fixing the issue.
            3. Hand off to `developer` for execution.
            4. Route to `test-hub` immediately after implementation evidence exists.

            ## Fix guardrails
            - Keep API and persistence changes explicit by listing affected contracts and tables.
            - Use support skills before coding when boundary risk is high.
            - If the fix adds new behavior, require a test-first note before implementation handoff.

            ## Implementation handoff checklist
            - Files to edit are listed with scope boundaries.
            - Non-goals are explicit to prevent scope creep.
            - Verification commands are ready before coding starts.
            - Migration or compatibility risks are named when present.
            - Rollback hint is recorded for high-impact changes.
            - Reviewer owner for the fix path is identified.
            - Expected blast radius is summarized in one sentence.
            - Required post-fix monitoring signal is named.
            """
        ).strip(),
    ),
    "test-hub": SkillSpec(
        name="test-hub",
        description="Use when implementation exists, after a risky refactor, or whenever confidence is lower than the change impact. Coordinate verification, evidence collection, and residual-risk review before work is called done.",
        role="verification-hub",
        layer="layer-2-workflow-hubs",
        inputs=["story or tech-spec", "implementation evidence", "testing-patterns reference", "workflow-state"],
        outputs=[".relay-kit/contracts/qa-report.md", "updated workflow-state with pass, fail, or blocked verdict"],
        references=[
            "Use qa-governor for the actual readiness gate.",
            "Prefer evidence tied to acceptance criteria and regression surface.",
            "Route back to debug-hub when verification fails unexpectedly.",
            "When discipline utilities are installed, use `evidence-before-completion` before calling the lane ready.",
            "For edit requests, run `prompt-fidelity-check` and reject completion if drift verdict is not pass.",
        ],
        next_steps=["qa-governor", "testing-patterns", "evidence-before-completion", "prompt-fidelity-check", "release-readiness", "skill-gauntlet", "impact-radar", "runtime-doctor", "migration-guard", "accessibility-review", "media-tooling", "ui-styling", "review-hub", "debug-hub", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Turn raw test execution into a real readiness decision.

            ## Mandatory behavior
            1. Decide the smallest useful evidence matrix for the change.
            2. Collect results and compare them to acceptance criteria.
            3. Use `evidence-before-completion` if available to validate every completion claim against fresh command output.
            4. For edit requests, run `prompt-fidelity-check` and write asked-versus-delivered plus drift verdict.
            5. Write or refresh `qa-report.md`.
            6. If evidence is weak or failing, route to `debug-hub` rather than guessing.

            ## Evidence discipline
            - Map every acceptance claim to a concrete command output, log, or artifact delta.
            - Run migration-guard and skill-gauntlet when runtime surfaces or skill files changed.
            - When UI changes are involved, include accessibility and styling checks before readiness.

            ## Verification exit checklist
            - QA report links evidence to acceptance criteria.
            - Regression surface is stated explicitly.
            - Edit lanes include Asked vs Delivered and Drift verdict sections.
            - Remaining risk is categorized as acceptable or blocking.
            - Failed checks route to debug-hub with concrete failure evidence.
            - Completion claim is rejected when evidence is stale.
            - Gate outcome (go/hold) is written to workflow-state before handoff.
            - Any waived check is documented with owner and expiry.
            """
        ).strip(),
    ),
    "review-hub": SkillSpec(
        name="review-hub",
        description="Use when artifacts disagree or before final completion claims. Check alignment across requirements, architecture, implementation, and quality evidence, then decide whether to accept, re-slice, debug, or re-plan.",
        role="review-hub",
        layer="layer-2-workflow-hubs",
        inputs=["active artifacts", "qa-report if present", "workflow-state"],
        outputs=["updated workflow-state", "go/no-go review verdict", "specific bounce-back path when misalignment exists"],
        references=[
            "Review-hub is the mesh junction: it may send work back to plan, debug, fix, or test.",
            "Do not hide disagreement between artifacts; name it and route accordingly.",
            "Use `.relay-kit/docs/review-loop.md` and `.relay-kit/docs/branch-completion.md` for review handling and end-of-branch discipline.",
            "If work crosses sessions, require context-continuity artifacts before accepting final completion claims.",
            "For edit requests, require prompt-fidelity-check with drift verdict pass before go-forward verdict.",
        ],
        next_steps=["plan-hub", "debug-hub", "fix-hub", "test-hub", "prompt-fidelity-check", "context-continuity", "release-readiness", "skill-gauntlet", "impact-radar", "migration-guard", "doc-pointers", "memory-search", "repo-map", "research", "mermaid-diagrams", "aesthetic", "frontend-design", "ui-styling", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Make completion a deliberate alignment check, not just a feeling that enough has happened.

            ## Mandatory checks
            - Do requirements, architecture, and implementation still describe the same change?
            - Does quality evidence actually cover the promised behavior and regression surface?
            - Is the active lane done, or is it merely unblocked enough to continue elsewhere?
            - For edit lanes, does Asked vs Delivered show zero forbidden drift with a pass verdict?

            ## Output contract
            End with one explicit verdict:
            - go forward,
            - bounce to planning,
            - bounce to debugging,
            - bounce to implementation,
            - or hold for missing evidence.

            ## Review handling discipline
            - Verify external review feedback against the codebase before accepting it.
            - Prefer one review item at a time when feedback changes code or requirements.
            - If the lane is complete, route through branch-completion discipline before treating it as finished.
            """
        ).strip(),
    ),
}
