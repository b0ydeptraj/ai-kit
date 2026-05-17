# browser-inspector Operator Contract

Use this contract when `browser-inspector` is selected for Use when the active hub needs console, network, DOM, or performance observations from a web flow. Browser evidence utility.

Required contract:

- Role: utility-provider.
- Layer: layer-3-utility-providers.
- Start from these inputs: active hub or orchestrator request, current authoritative artifact, only the evidence relevant to this pass.
- Produce or update these outputs: browser-side evidence appended to investigation-notes or qa-report.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: debug-hub, test-hub, review-hub.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
