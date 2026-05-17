# handoff-context Operator Contract

Use this contract when `handoff-context` is selected for Use when the next skill needs a tighter, more relevant context handoff than the current artifact already provides. Context-pack utility.

Required contract:

- Role: utility-provider.
- Layer: layer-3-utility-providers.
- Start from these inputs: active hub or orchestrator request, current authoritative artifact, only the evidence relevant to this pass.
- Produce or update these outputs: focused context pack notes added to workflow-state, story, or handoff-log, an explicit include/exclude list for the receiving skill.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: workflow-router, team, cook, developer.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
