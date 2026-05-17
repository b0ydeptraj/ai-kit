# doc-pointers Operator Contract

Use this contract when `doc-pointers` is selected for Use when a hub needs exact docs fragments, file paths, or source references before deciding. Stateless docs retrieval utility.

Required contract:

- Role: utility-provider.
- Layer: layer-3-utility-providers.
- Start from these inputs: active hub or orchestrator request, current authoritative artifact, only the evidence relevant to this pass.
- Produce or update these outputs: doc pointers, file paths, or citations appended to the active artifact, a short conflict note when documentation and implementation disagree.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: scout-hub, review-hub, workflow-router.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
