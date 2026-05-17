# automation-ops Bad Output

Bad output says the automation is reliable without proving the operating model.

Red flags:

- No dry-run.
- No idempotency or replay rule.
- No rollback or compensation path.
- No owner for stuck runs.
- Logs include secrets or raw user data.
- Success is defined as "script exits zero" without checking side effects.
