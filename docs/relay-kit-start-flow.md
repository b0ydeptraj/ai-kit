# Relay-kit start flow

Relay-kit already has a strong internal workflow. This document exposes the small public surface you should learn first.

## Public names first, internal names second

You do **not** need to memorize the whole Relay-kit taxonomy to use it well.

Start with these public names:

| If you want to... | Use this | Behind the scenes |
|---|---|---|
| figure out where to start | `start-here` | `workflow-router` |
| turn a rough idea into a clear direction | `brainstorm` | `brainstorm-hub` |
| slice approved work into buildable steps | `write-steps` | `scrum-master` |
| implement an approved slice | `build-it` | `developer` |
| review a branch or PR before merge or sign-off | `review-pr` | `review-hub` |
| debug a bug or mismatch properly | `debug-systematically` | `debug-hub` + `root-cause-debugging` |
| decide whether work is actually ready | `ready-check` | `review-hub` + `qa-governor` |
| force one last proof pass | `prove-it` | `evidence-before-completion` |

## Default paths

### New work

1. `start-here`
2. `brainstorm`
3. `write-steps`
4. `build-it`
5. `ready-check`
6. `prove-it` if the completion claim still feels weak

### Bug or regression

1. `start-here`
2. `debug-systematically`
3. `build-it` once the fix path is real
4. `ready-check`

### Branch or PR review

1. `review-pr`
2. `ready-check` when you need a real readiness or shipability verdict
3. `prove-it` when the completion claim still sounds stronger than the proof

### Final confidence check

1. `prove-it`
2. `ready-check`

## Why this exists

Relay-kit has more depth than a tiny skill pack. That depth is useful, but the first contact should still be simple:

- few names
- clear entry points
- clear handoff order
- no need to learn internal layers on day one

The canonical runtime skills stay the same. This page only gives you a cleaner public face for day-to-day use through the repo-local public skill surface.

For the review-specific path, see [`docs/relay-kit-review-flow.md`](relay-kit-review-flow.md).
