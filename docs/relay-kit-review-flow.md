# Relay-kit review flow

Relay-kit uses three nearby public names for three different review jobs.

## Quick map

| If you need to... | Use this | Behind the scenes | Main outcome |
|---|---|---|---|
| review a branch or PR before merge or sign-off | `review-pr` | `review-hub` | bounce-back decision plus specific next action |
| decide whether current work is actually ready or shippable | `ready-check` | `review-hub` + `qa-governor` | go / no-go readiness verdict |
| force one last proof pass when the claim still feels too optimistic | `prove-it` | `evidence-before-completion` | claim-to-evidence check |

## Use `review-pr` when

- code already exists and you want a deliberate review pass
- you are reviewing a branch, PR, or handoff before merge
- the important question is what should bounce back, not just whether the work feels close

Typical outputs:

- concrete findings
- missing evidence or regression risk
- exact next owner or next skill

Common next step:

- `build-it` when implementation must change
- `debug-systematically` when the review exposes a real mismatch
- `ready-check` when the code looks complete and now needs a formal readiness verdict

## Use `ready-check` when

- you already have code and evidence
- you need a real go / no-go decision
- the question is readiness, shipability, or whether the lane can be called done

Typical outputs:

- `qa-report.md`
- a readiness verdict
- a bounce-back path if confidence is still weak

## Use `prove-it` when

- someone is about to say the work is done
- the claim sounds stronger than the evidence
- you want one last proof pass before accepting the verdict

Typical outputs:

- a list of explicit claims
- fresh proof for each claim
- rejection of any claim that is still weak

## Practical sequences

### Review a branch or PR

1. `review-pr`
2. `build-it` or `debug-systematically` if the review finds real issues
3. `ready-check` before merge or sign-off

### Check whether a finished lane is really ready

1. `ready-check`
2. `prove-it` if the completion claim still feels too soft

### Pressure-test a strong completion claim

1. `prove-it`
2. `ready-check`
