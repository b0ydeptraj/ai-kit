# automation-ops Good Output

Good output names the trigger, runbook owner, dry-run command, idempotency key, retry policy, rollback path, and evidence artifacts.

Example summary:

- Trigger: hourly scheduler with manual override.
- Safety: dry-run default, write mode requires explicit flag.
- Idempotency: `job_id + target_id + action`.
- Failure: three bounded retries with backoff, then dead-letter.
- Evidence: run id, redacted action log, skipped action reasons, rollback checklist.
