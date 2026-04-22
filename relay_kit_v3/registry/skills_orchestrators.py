from __future__ import annotations

from textwrap import dedent
from typing import Dict

from .skill_models import SkillSpec

ORCHESTRATOR_SKILLS: Dict[str, SkillSpec] = {
    "workflow-router": SkillSpec(
        name="workflow-router",
        description="Use when a request arrives, the user asks what to do next, or scope or complexity is unclear. Route a request through the right delivery track, enforce intent-fidelity locks for edit work, choose the active orchestrator or hub, keep workflow-state current, and enforce SRS-first policy when it is enabled.",
        role="routing-kernel",
        layer="layer-1-orchestrators",
        inputs=["user request", ".relay-kit/contracts/project-context.md (if present)", ".relay-kit/state/workflow-state.md (if present)", ".relay-kit/state/team-board.md (if present)"],
        outputs=[".relay-kit/state/workflow-state.md", ".relay-kit/contracts/intent-contract.md when edit work is in scope", ".relay-kit/contracts/entity-map.md when media or UI edits are in scope", ".relay-kit/contracts/srs-spec.md when SRS-first applies", ".relay-kit/contracts/tech-spec.md or product-brief.md kickoff", ".relay-kit/state/team-board.md when parallel lanes are needed"],
        references=[
            "Prefer existing project-context over assumptions.",
            "Escalate from quick-flow to product-flow whenever hidden complexity appears.",
            "Hand off to bootstrap when base artifacts are missing, to cook for a single request, and to team when multiple lanes must move in parallel.",
            "If session continuity is weak, run context-continuity checkpoint or rehydrate before routing deeper work.",
            "For existing codebases, prefer scout-hub plus repo-map before planning when dependency boundaries are still unclear.",
            "For edit requests, run `intent-lock` before implementation handoff and mark lock status in workflow-state.",
            "For media or UI edits with multiple similar targets, require `entity-lock` before allowing transformations.",
            "If `.relay-kit/state/srs-policy.json` enables SRS-first, require `srs-spec.md` before declaring product-flow or enterprise-flow planning-ready.",
        ],
        next_steps=["bootstrap", "cook", "team", "context-continuity", "intent-lock", "entity-lock", "scout-hub", "plan-hub", "debug-hub"],
        body=dedent(
            """\
            # Mission
            Act as the routing kernel for the whole system: choose the track, choose the active lane, and make the next move explicit.

            ## Mandatory routing procedure
            1. Read `.relay-kit/contracts/project-context.md` and `.relay-kit/state/workflow-state.md` if they exist.
            2. Restate the request in one sentence and classify request class in workflow-state (`edit`, `read-only`, or `unknown`).
            3. If request class is `edit`, run `intent-lock` before implementation hub handoff; if media/UI entities are involved, run `entity-lock` too.
            4. Score the request on five axes: ambiguity, breadth of change, architecture risk, operational risk, and coordination cost.
            5. Classify complexity:
               - `L0`: single bug or tiny refactor
               - `L1`: small feature or bug cluster
               - `L2`: multi-component feature slice
               - `L3`: product or platform change with design trade-offs
               - `L4`: enterprise, compliance, or scale-sensitive work
            6. Choose track:
               - `L0-L1` -> quick-flow
               - `L2-L3` -> product-flow
               - `L4` -> enterprise-flow
            7. Choose the layer-1 entrypoint:
               - use `bootstrap` if state, context, or artifacts are missing
               - use `cook` for one active request in one lane
               - use `team` if more than one lane, owner, or branch of work must be coordinated
            8. Choose the first layer-2 hub:
               - `scout-hub` when the codebase area is unclear
               - `plan-hub` when planning artifacts are missing or stale
               - `debug-hub` when the request starts from a failure or regression
            9. Mark the lane mode explicitly as one of: discovery, planning, implementation, or verification.
            10. Update `.relay-kit/state/workflow-state.md` with track choice, next skill, blockers, and intent/entity lock status.

            ## SRS-first gate
            - Read `.relay-kit/state/srs-policy.json` when present.
            - If policy is enabled and scope includes the active track, require `.relay-kit/contracts/srs-spec.md` before calling planning ready.
            - Route to `plan-hub` + `srs-clarifier` when SRS sections or UC-ID traceability are missing.

            ## Escalation rules
            Escalate immediately when:
            - a small fix changes contracts, schemas, APIs, or infrastructure
            - acceptance criteria are unclear or disputed
            - multiple bounded contexts are touched
            - rollout, migration, security, or compliance risk appears

            ## Output contract
            Never end with vague advice. Always name the next skill, the artifact it should create or update, and what evidence is still missing.
            """
        ).strip(),
    ),
    "bootstrap": SkillSpec(
        name="bootstrap",
        description="Use when starting a repo lane, after major structure changes, or whenever workflow-state or project-context is missing or stale. Initialize or refresh the shared Relay-kit runtime before a new lane begins.",
        role="session-bootstrap",
        layer="layer-1-orchestrators",
        inputs=["repo root", ".relay-kit/ runtime folders if present", "current request"],
        outputs=[".relay-kit/state/workflow-state.md", ".relay-kit/contracts/project-context.md", ".relay-kit/state/team-board.md when parallel work is expected"],
        references=[
            "Prefer lightweight initialization over speculative planning.",
            "If the codebase is unfamiliar, route immediately to scout-hub after bootstrapping.",
            "Do not invent project-context facts; mark unknowns and hand off to scout-hub.",
            "Use context-continuity rehydrate when resuming across thread or session boundaries.",
        ],
        next_steps=["workflow-router", "scout-hub", "cook", "team", "context-continuity"],
        body=dedent(
            """\
            # Mission
            Prepare the runtime so later steps have an authoritative baseline instead of relying on chat memory.

            ## Mandatory setup
            1. Ensure `.relay-kit/state/workflow-state.md` exists and records the current request.
            2. Ensure `.relay-kit/contracts/project-context.md` exists. If facts are missing, create a skeletal version with explicit unknowns.
            3. If the request is likely to branch into more than one lane, create or refresh `.relay-kit/state/team-board.md`.
            4. Record which artifacts already exist and which ones must be refreshed.
            5. If the repo area is not well understood, route next to `scout-hub`.

            ## Guardrails
            - Bootstrap does not do deep planning.
            - Bootstrap does not declare work ready; it only makes later work safer.
            - When in doubt, prefer creating the minimal state needed to hand off cleanly.
            - Record the exact artifact owner for the next lane before handing off.
            - If bootstrap detects stale assumptions, force scout-hub before planning.
            - If continuity artifacts conflict with repo reality, route to workflow-router for reclassification.

            ## Ready-to-handoff checklist
            - Workflow-state points to one explicit next skill.
            - Project-context has known unknowns clearly marked.
            - Team-board ownership is set when multiple lanes exist.
            - Required contracts for the next lane are present.
            - Bootstrap output includes one blocking risk and one mitigation step.
            """
        ).strip(),
    ),
    "team": SkillSpec(
        name="team",
        description="Use when work must proceed in parallel, when planning and implementation overlap, or when one lane is blocked and another can move. Coordinate multi-lane or multi-session work without letting agents step on each other.",
        role="meta-orchestrator",
        layer="layer-1-orchestrators",
        inputs=[".relay-kit/state/workflow-state.md", ".relay-kit/state/team-board.md", "active artifacts and blockers"],
        outputs=[".relay-kit/state/team-board.md", ".relay-kit/state/workflow-state.md"],
        references=[
            "Shared artifacts beat chat summaries; update the artifact before handing off.",
            "Assign one owner skill per lane and name merge order explicitly.",
            "Use cook inside a lane, not as a replacement for team.",
            "Use `.relay-kit/docs/parallel-execution.md` to decide when work is independent enough to split safely.",
            "Require context-continuity handoff packs when ownership shifts across sessions or AIs.",
            "Prefer wave-based execution: parallel inside a wave, strict dependency gate between waves.",
        ],
        next_steps=["cook", "plan-hub", "scout-hub", "debug-hub", "review-hub", "context-continuity"],
        body=dedent(
            """\
            # Mission
            Coordinate parallel work while preserving one authoritative source of truth for each artifact.

            ## Mandatory behavior
            1. Maintain `.relay-kit/state/team-board.md` with lanes, owners, active artifacts, blockers, and merge order.
            2. Split work only when lanes are independent enough to avoid editing the same artifact section at the same time.
            3. Use `cook` to drive each active lane, but keep final merge and priority decisions here.
            4. If one lane uncovers architecture or scope drift, update workflow-state and notify all affected lanes.
            5. Park lanes that are blocked instead of letting them thrash.
            6. Record lock scope and handoff status whenever a lane changes ownership or pauses.
            7. For each lane, record `depends_on` and `wave_id`, then only advance to the next wave after current-wave verification gates pass.

            ## Do not do this
            - Do not let two lanes silently diverge on the same acceptance criteria.
            - Do not keep lane state only in memory.
            - Do not parallelize before a quick scout when the codebase area is unfamiliar.
            - Do not close a lane as done when no artifact delta or verification evidence exists.
            """
        ).strip(),
    ),
    "cook": SkillSpec(
        name="cook",
        description="Use when one active request already has routing and state, and needs the next solid handoff. Drive that request forward with the right hub or specialist.",
        role="lane-conductor",
        layer="layer-1-orchestrators",
        inputs=[".relay-kit/state/workflow-state.md", "current request or lane objective", "available artifacts"],
        outputs=["updated workflow-state", "a named next hub or specialist", "refreshed artifacts produced by the chosen lane"],
        references=[
            "Cook does not replace hubs; it chooses and sequences them.",
            "Keep each pass small: one hub, one artifact decision, one clear next handoff.",
            "If completion is claimed, force test-hub or review-hub before accepting it.",
            "If the lane is pausing or switching owners, trigger context-continuity checkpoint before handoff.",
        ],
        next_steps=["brainstorm-hub", "scout-hub", "plan-hub", "debug-hub", "fix-hub", "intent-lock", "entity-lock", "test-hub", "review-hub", "context-continuity"],
        body=dedent(
            """\
            # Mission
            Run the day-to-day loop for one request without letting it skip gates or get stuck in vague next steps.

            ## Mandatory loop
            1. Read workflow-state and identify the lane's current objective.
            2. Choose exactly one hub that should move the work forward now.
            3. Name the artifact that hub must create, update, or validate.
            4. After the hub finishes, update workflow-state with what changed and which hub or specialist comes next.
            5. Stop as soon as the next handoff is explicit.

            ## Safety rules
            - Never jump straight from vague intent to implementation.
            - If request class is `edit` and intent-lock is not pass, run `intent-lock` before implementation.
            - If media/UI edit targets are ambiguous, run `entity-lock` and hold until IDs are stable.
            - When evidence is weak, prefer scout-hub, debug-hub, or test-hub over optimistic implementation.
            - When scope shifts, send the lane back through workflow-router.
            - When implementation starts, route through plan-hub or fix-hub with an explicit artifact target.
            - Before claiming completion, force test-hub and review-hub evidence checkpoints.
            - If the next handoff is ambiguous, pause and rewrite workflow-state before proceeding.

            ## Lane execution checks
            - Current objective and acceptance signal are both visible in workflow-state.
            - The selected hub has a concrete artifact target.
            - Evidence gaps are named before coding decisions.
            - Handoff includes blockers, assumptions, and validation plan.
            - Lane closes only after review-hub verdict is explicit.
            """
        ).strip(),
    ),
}
