# automation-ops Operator Contract

Use this reference when an automation request can affect files, users, accounts, schedules, external APIs, or production-like data.

Required contract:

- Trigger model: manual, schedule, webhook, queue, or event stream.
- Idempotency key or replay rule for every side-effecting action.
- Dry-run output that lists planned actions before mutation.
- Retry budget, backoff rule, and terminal failure state.
- Rollback or compensation path with an accountable operator.
- Observability: run id, inputs, outputs, redacted logs, and failure reason.

Do not approve automation that only says "run a script" without naming the runbook, stop condition, and recovery path.
