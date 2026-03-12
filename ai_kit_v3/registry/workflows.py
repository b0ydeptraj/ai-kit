from __future__ import annotations

from textwrap import dedent


TRACKS = {
    "quick-flow": {
        "levels": ["L0", "L1"],
        "use_for": "Small, well-bounded work with tight scope and low coordination overhead.",
        "artifacts": ["tech-spec", "investigation-notes", "qa-report"],
        "flow": ["workflow-router", "cook", "debug-hub", "fix-hub", "test-hub", "qa-governor"],
    },
    "product-flow": {
        "levels": ["L2", "L3"],
        "use_for": "Features, products, or platform work that need requirements, architecture, story slicing, and utility-provider support.",
        "artifacts": ["product-brief", "prd", "architecture", "epics", "story", "qa-report"],
        "flow": ["workflow-router", "cook", "plan-hub", "architect", "scrum-master", "developer", "qa-governor"],
    },
    "enterprise-flow": {
        "levels": ["L4"],
        "use_for": "High-risk, compliance-sensitive, multi-tenant, or multi-team changes that need explicit lane ownership and handoff discipline.",
        "artifacts": ["product-brief", "prd", "architecture", "epics", "story", "qa-report", "team-board", "lane-registry", "handoff-log"],
        "flow": ["bootstrap", "team", "workflow-router", "cook", "plan-hub", "architect", "scrum-master", "developer", "qa-governor"],
    },
}

COMPLEXITY_LADDER = {
    "L0": "Single bug or tiny refactor in a well-understood area. One module, one behavior, low ambiguity.",
    "L1": "Small feature or bug cluster. A few files, straightforward constraints, low architectural risk.",
    "L2": "Feature slice touching multiple components. Requires acceptance criteria and design alignment.",
    "L3": "Product or platform change with meaningful architectural trade-offs and rollout considerations.",
    "L4": "Enterprise-grade work with compliance, scale, security, migration, or cross-team coordination needs.",
}


def render_workflow_state() -> str:
    return dedent(
        """        # workflow-state

        ## Current request
        TBD

        ## Active lane
        - Lane id: primary
        - Mode: serial or parallel TBD
        - Lane owner: TBD

        ## Active orchestration
        - Layer-1 orchestrator: TBD
        - Layer-2 workflow hub: TBD
        - Active specialist: TBD

        ## Active utility providers
        - Primary utility provider: TBD
        - Additional utilities in play: TBD

        ## Active standalone/domain skill
        - Skill: TBD
        - Why selected: TBD

        ## Complexity level
        - Level: TBD
        - Reasoning: TBD

        ## Chosen track
        - Track: TBD
        - Why this track fits: TBD

        ## Completed artifacts
        - [ ] product-brief
        - [ ] PRD
        - [ ] architecture
        - [ ] epics
        - [ ] story
        - [ ] tech-spec
        - [ ] investigation-notes
        - [ ] qa-report
        - [ ] team-board
        - [ ] lane-registry
        - [ ] handoff-log

        ## Ownership locks
        | Artifact | Owner lane | Lock scope | Status |
        |---|---|---|---|
        | TBD | TBD | TBD | TBD |

        ## Next skill
        TBD

        ## Known blockers
        TBD

        ## Escalation triggers noticed
        TBD

        ## Notes
        TBD
        """
    )



def render_team_board() -> str:
    return dedent(
        """        # team-board

        ## Shared objective
        TBD

        ## Active orchestrator
        - team

        ## Lanes
        | Lane | Owner skill | Current hub | Current artifact | Lock scope | Status | Handoff status | Notes |
        |---|---|---|---|---|---|---|---|
        | primary | TBD | TBD | TBD | TBD | queued | none | TBD |
        | lane-2 | TBD | TBD | TBD | TBD | parked | none | TBD |
        | lane-3 | TBD | TBD | TBD | TBD | parked | none | TBD |

        ## Shared artifacts that must stay authoritative
        - `.ai-kit/state/workflow-state.md`
        - `.ai-kit/state/lane-registry.md`
        - `.ai-kit/state/handoff-log.md`
        - `.ai-kit/contracts/project-context.md`
        - `.ai-kit/contracts/PRD.md`
        - `.ai-kit/contracts/architecture.md`

        ## Merge order
        TBD

        ## Merge prerequisites
        TBD

        ## Conflict risks
        TBD

        ## Decision log
        TBD
        """
    )



def render_lane_registry() -> str:
    return dedent(
        """        # lane-registry

        ## Usage rules
        - One lane owns one artifact lock at a time.
        - Record the narrowest useful lock scope, not whole-repo ownership by default.
        - Release or reassign the lock before a different lane edits the same artifact section.

        ## Active lanes
        | Lane | Owner skill | Source orchestrator | Target hub | Primary artifact | Lock scope | Merge prerequisite | Status |
        |---|---|---|---|---|---|---|---|
        | primary | TBD | workflow-router | TBD | TBD | TBD | TBD | active |
        | lane-2 | TBD | team | TBD | TBD | TBD | TBD | parked |
        | lane-3 | TBD | team | TBD | TBD | TBD | TBD | parked |

        ## Released locks
        | Lane | Artifact | Previous scope | Released because |
        |---|---|---|---|
        | TBD | TBD | TBD | TBD |
        """
    )



def render_handoff_log() -> str:
    return dedent(
        """        # handoff-log

        ## Handoff entries
        | From | To | Lane | Trigger | Artifact touched | Evidence linked | Expected return condition |
        |---|---|---|---|---|---|---|
        | workflow-router | cook | primary | route selected | workflow-state | TBD | hub chosen |
        | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

        ## Rules
        - Every non-trivial handoff should update this log before the receiving skill starts work.
        - Link to the authoritative artifact, not only a chat summary.
        - If a handoff changes scope or ownership, update `workflow-state.md` and `lane-registry.md` in the same pass.
        """
    )
