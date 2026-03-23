# Rule: add new skills without breaking Relay-kit topology

Drafted: 2026-03-23
Status: active engineering rule

## Core rule

Every new skill or capability added to Relay-kit must extend the existing topology, not replace it.

In practice:
- do not create a parallel workflow system
- do not bypass existing hubs and artifacts
- do not add public surface area unless it reduces friction without diluting the main flow

## What must stay intact

These are not optional:
- current layer topology
- orchestrator and hub ownership
- `.ai-kit` artifact model
- bundle gating
- adapter parity
- compatibility-safe evolution

Any proposal that weakens one of these is a rejection candidate by default.

## Allowed types of additions

Prefer additions in this order:

1. support reference
2. utility provider
3. discipline utility
4. specialist skill
5. public alias

Only add a new orchestrator, workflow hub, or public install surface when the existing structure cannot safely absorb the need.

## Ownership rule

A new skill must not steal ownership from an existing hub or orchestrator unless the old ownership model is clearly broken.

Examples:
- `context-continuity` may support `handoff-context`, `workflow-router`, `cook`, `team`, and `bootstrap`
- it must not become a second hidden router
- `release-readiness` may extend `test-hub` or `qa-governor`
- it must not become a separate completion system with its own incompatible state model

## Artifact rule

New skills must plug into existing artifacts and state before introducing new standalone storage.

Prefer:
- updating `.ai-kit/state/*`
- updating `.ai-kit/contracts/*`
- adding references under `.ai-kit/references/*`
- adding docs under `.ai-kit/docs/*`

Avoid:
- creating hidden side-state not visible to the Relay-kit workflow
- creating a new memory model that ignores existing artifacts

## Public surface rule

New public names must make Relay-kit easier to use, not harder to remember.

Rules:
- keep the primary public flow compact
- do not expand public names just to match large skill catalogs elsewhere
- use aliases when the capability already exists
- only add a new public entry when it exposes a real workflow users cannot discover cleanly today

## Interoperability rule

New capabilities must compose with existing skills.

Ask:
- which current hub invokes this?
- which artifact does it read?
- which artifact does it update?
- what is the next valid handoff after it runs?

If those answers are vague, the skill is not ready.

## Verification rule

Do not add a new skill based only on intuition or market pressure.

Before adding it, state:
- what gap exists now
- why current skills are insufficient
- where it fits in the topology
- what evidence or workflow it improves
- what it must not replace

## Anti-patterns

Reject or redesign proposals that:
- create a second router
- create a second planning system
- create a second memory system disconnected from `.ai-kit`
- add many public names just for marketing breadth
- clone another kit's persona swarm into Relay-kit
- introduce plugin or command systems that bypass the current runtime model

## Safe implementation sequence

When adding a meaningful new capability:

1. write a design note
2. identify exact topology slot
3. define artifact inputs and outputs
4. implement the new skill
5. patch existing active skills that should invoke it
6. validate that the main flow still feels simpler, not more fragmented

## Final test

A new skill is acceptable only if all of these remain true:
- Relay-kit still feels like one linked system
- the main public flow stays understandable
- artifacts remain the source of truth
- routing remains explicit
- the new capability reduces drift instead of adding a parallel process
