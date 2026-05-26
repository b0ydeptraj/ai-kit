# Relay-kit Signal Calibration

`signal-calibration` is Relay-kit's claim-strength guard. It turns scattered proof surfaces into one verdict before an agent calls work done, production-ready, commercial-ready, field-tested, realistic, or proven.

This is not a user workflow command to memorize. Generated adapters include the `signal-calibration` skill so agents can route to it automatically when a claim risks sounding stronger than the evidence.

## What It Calibrates

- completion and fixed claims that need file, command, or artifact proof
- skill quality claims, including weak, strong, validated, and field-tested labels
- production-ready, commercial-ready, and release-ready wording
- backend realism, UI realism, MMO/API realism, benchmark, and research claims
- any confident statement that has no concrete file, log, test, source, or field evidence

## Proof Levels

The report schema is `relay-kit.signal-calibration.v1`.

Proof levels are intentionally strict:

- `none`: no concrete evidence was attached.
- `synthetic-validated`: internal or synthetic checks exist, but no production-shaped fixture.
- `real-world-fixture`: Relay-kit real-world fixtures validate the contract, but this is still not field evidence.
- `runtime-validated`: a local runtime gate or artifact supports the claim.
- `field-tested`: external field evidence exists under Relay-kit evidence artifacts.

`field-tested`, `real-world proven`, `production-ready`, and `commercial-ready` claims are blocked when the only proof is fixture, test, or local readiness output. Local readiness can support a release lane; it does not prove external support operation or user field validation by itself.

## CLI

The CLI exists for CI, release proof, and debugging:

```bash
relay-kit calibrate claims /path/to/project --claim "This skill is field-tested" --strict --json
relay-kit calibrate skill /path/to/project --skill all --strict --json
relay-kit calibrate readiness /path/to/project --strict --json
```

Default output, when `--output-file` is omitted:

```text
.relay-kit/eval/signal-calibration.json
```

## Enterprise Gate

Enterprise readiness includes a required `signal-calibration` gate. Strict mode fails when a strong claim has only weak or missing evidence.

The gate orchestrates existing Relay-kit proof surfaces:

- `relay-kit proof audit`
- `relay-kit eval real-world`
- `relay-kit eval battle-audit`

Those lower-level commands remain available. `signal-calibration` combines them into one claim-level verdict.

## Pulse And Signals

Pulse includes a `signal_calibration` report and a `calibration_health` summary by default. Signal export emits:

- `relay.calibration.unsupported_claims`
- `relay.calibration.overclaim_flags`
- `relay.calibration.proven_claims`
- `relay.calibration.field_tested_claims`
- `relay.calibration.blocked_claims`

Use these metrics to detect when an agent is drifting from evidence into confident wording.
