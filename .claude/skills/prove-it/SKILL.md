---
name: prove-it
description: Use when a completion claim needs one last evidence pass before work is called done, fixed, or ready. Public Relay-kit entrypoint for final proof.
---

# Prove It

Public alias for `evidence-before-completion`.

Use this when:
- someone is about to say the work is done
- the claim sounds stronger than the proof
- you want one final claim-to-evidence check
- you need to map each claim to fresh proof output

What this alias should do:
1. list the exact claims being made
2. tie each claim to fresh proof output
3. send weak claims back for more testing or debugging

Behind the scenes:
- canonical skill: `evidence-before-completion`
- this is not a readiness verdict
- this alias does not write `qa-report.md`
- common outputs: evidence added to `workflow-state.md` or the active artifact

Typical handoff:
- `ready-check`
- `debug-systematically`
