# mermaid-diagrams Operator Contract

Use this contract when `mermaid-diagrams` is selected for Use when architecture, flow, or sequencing should be expressed as a quick mermaid diagram inside an artifact. Diagramming utility.

Required contract:

- Role: utility-provider.
- Layer: layer-3-utility-providers.
- Start from these inputs: active hub or orchestrator request, current authoritative artifact, only the evidence relevant to this pass.
- Produce or update these outputs: mermaid snippets inserted into architecture, project-context, or docs.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: plan-hub, architect, review-hub.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
