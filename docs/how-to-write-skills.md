# How to write Relay-kit skills

This guide exists to keep new skills consistent with the current Relay-kit
runtime instead of adding more drift.

Use it before adding or rewriting any skill under:

- `.claude/skills/`
- `.agent/skills/`
- `.codex/skills/`

## Start with the smallest correct move

Before writing a new skill, decide which one of these cases you are in:

1. the capability already exists and only needs a better public name
2. the capability exists but the content is too weak or too vague
3. the capability is truly missing and needs a new skill

Default rule:

- prefer improving an existing skill or adding a public alias first
- add a brand-new skill only when the current runtime really cannot cover the job

## Write the description as a trigger, not as a summary

The first line or short description should tell the agent **when to use the
skill**, not summarize the whole workflow.

Good:

- `Use when a request arrives and you need to choose the right path.`
- `Use when implementation is approved and code must change with evidence.`

Bad:

- `Routes requests, updates state, coordinates handoffs, and manages context.`
- `Builds features with planning, testing, review, and documentation.`

Why this rule matters:

- trigger-style wording makes activation clearer
- summary-style wording invites shortcut behavior
- Relay-kit works better when the agent reads the full skill body instead of
  improvising from one sentence

## Keep the public surface small

Relay-kit already has a public first-contact layer:

- `start-here`
- `brainstorm`
- `write-steps`
- `build-it`
- `debug-systematically`
- `ready-check`
- `prove-it`

If a new user-facing name is needed:

- map it to an existing canonical skill if possible
- keep the number of public names low
- avoid creating overlapping names that increase routing confusion

## Respect the current runtime shape

Relay-kit is skill-centric and artifact-centric.

Do not write skills that assume a different runtime model such as:

- plugin-only hooks as the main control surface
- marketplace-only install behavior
- hidden automation that bypasses artifacts and state

Work with the current structure:

- runtime skills live in adapter folders
- shared contracts, state, references, and docs live under `.relay-kit/`
- public aliases should not rewrite canonical runtime names unless there is a
  deliberate migration plan

## Put the skill in the right layer

Before finalizing a skill, decide what it is:

- orchestrator
- workflow hub
- utility provider
- specialist
- standalone/public alias

Use the existing docs if you are unsure:

- `.relay-kit/docs/layer-model.md`
- `.relay-kit/docs/utility-provider-model.md`
- `.relay-kit/docs/folder-structure.md`

## Make the output and stop condition explicit

Every skill should say:

- what artifact or outcome it should produce
- what evidence is enough to stop
- what it should hand off to next

Examples:

- update `workflow-state.md`
- append investigation notes
- write or refresh a QA report
- hand off to `developer`, `review-hub`, or `qa-governor`

If the skill is stateless, say that clearly.

## Define skills by workflow, not persona

Do not define a Relay-kit skill as:

- "become an expert in X"
- "act as a senior Y"
- "you are now a specialist Z"

That wording invites roleplay and overconfident improvisation.

Define the skill by:

- trigger condition
- workflow steps
- artifact inputs and outputs
- stop condition
- next handoff

Better pattern:

- "Use when this kind of request arrives."
- "Read these artifacts."
- "Produce this output."
- "Stop when this evidence exists."
- "Hand off to this next skill."

Relay-kit works better when skills behave like bounded operating procedures, not personas.

## Avoid giant umbrella skills

Do not create broad skills that try to do everything at once.

Warning signs:

- the skill can plan, build, debug, review, and document in one pass
- the handoff target is unclear
- the output changes wildly depending on the model mood

Prefer bounded behavior with a clean next handoff.

## Keep SKILL.md lean; move depth into references and scripts

Do not solve skill quality by making `SKILL.md` huge.

Default rule:

- keep `SKILL.md` focused on trigger, workflow, output, stop condition, and handoff
- move deep procedures, examples, schemas, or domain detail into `references/`
- move deterministic or repetitive behavior into `scripts/`

Why this matters:

- long skills are harder to trigger correctly
- long skills are easier for the model to skim poorly
- smaller cores plus progressive disclosure fit Relay-kit better

If a skill is drifting toward 500 lines, it is usually hiding a structure problem.

## Pressure-test the skill before you keep it

Minimum check before merging:

1. normal scenario
   - the skill activates for the task it was written for
2. edge scenario
   - the skill still behaves sensibly when context is partial
3. loophole scenario
   - the skill does not claim success without evidence

For workflow-heavy skills, also check:

- does it update the right artifact
- does it route to the right next skill
- does it avoid doing work owned by another layer

## Do not let a skill certify itself

The path that creates a skill should not be the only path that approves it.

Default rule:

- a new or heavily rewritten skill must be reviewed by a different path than the one that created it

Examples:

- another reviewer skill
- `review-hub`
- `oracle`
- a gauntlet run
- a separate prompt path focused on failure cases

Why this matters:

- self-review misses blind spots
- the same path that created the skill tends to justify its own structure
- Relay-kit quality improves when authoring and review are separated

## Bundle and baseline discipline

When adding a skill, decide:

- which bundle it belongs to
- whether it should stay optional
- why it should or should not enter `baseline`

Default rule:

- do not add new skills to `baseline` casually
- optional or experimental skills should stay outside the active baseline until
  they prove useful and stable

Read:

- `.relay-kit/docs/bundle-gating.md`

## Contributor checklist

Before opening a PR:

- [ ] The description uses `Use when...` style trigger wording.
- [ ] The skill fits an existing Relay-kit layer.
- [ ] The skill has a clear output, stop condition, and next handoff.
- [ ] The change does not expand the public surface without a good reason.
- [ ] Bundle placement is intentional.
- [ ] `python scripts/validate_runtime.py` still passes.

If the skill changes public behavior, also update:

- `README.md`
- `docs/relay-kit-start-flow.md`
- any compatibility or migration doc affected by the change
