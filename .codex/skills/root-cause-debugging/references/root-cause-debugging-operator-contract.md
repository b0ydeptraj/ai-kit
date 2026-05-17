# root-cause-debugging Operator Contract

Use this contract when `root-cause-debugging` is selected for Use when a hub needs a disciplined investigation before proposing fixes. Structured root-cause debugging utility.

Required contract:

- Role: utility-provider.
- Layer: layer-3-utility-providers.
- Start from these inputs: active hub or orchestrator request, current authoritative artifact, only the evidence relevant to this pass.
- Produce or update these outputs: root-cause notes and disproven hypotheses appended to investigation-notes or the active artifact.
- Name the concrete files, commands, logs, screenshots, docs, or state artifacts inspected.
- Separate verified evidence from assumptions before giving advice or making changes.
- If the request is vague, ask one anchored clarification or run a scout step before acting.
- Return through one of these next steps when the lane needs handoff: debug-hub, fix-hub, test-hub.

Do not present generic process text as completion evidence. The output must cite task-specific context and the next verifiable action.
