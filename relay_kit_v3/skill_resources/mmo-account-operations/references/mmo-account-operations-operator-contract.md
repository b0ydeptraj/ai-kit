# mmo-account-operations Operator Contract

Required contract:

- Authorized account ownership and credential policy.
- Account states: onboarding, active, limited, suspended, retired.
- Inventory fields: owner, folder, tags, proxy binding, session status, health score, last action, cooldown until.
- Per-account and per-platform budgets.
- Bulk action dry-run and approval.
- Quarantine, cooldown, and escalation runbook.

Do not design CAPTCHA bypass, identity spoofing, or policy-circumvention flows.
