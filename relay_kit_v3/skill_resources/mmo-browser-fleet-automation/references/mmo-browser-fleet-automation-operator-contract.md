# mmo-browser-fleet-automation Operator Contract

Required contract:

- Profile isolation and profile-to-proxy affinity.
- Session lease table with owner, browser state, last run, next allowed run.
- Stable selector contract and explicit waits.
- Retry and backoff for transient UI/network failures.
- Live debug evidence: screenshots, console logs, network errors, DOM snapshot.
- Human takeover and stop control.

Use official APIs when available and avoid prohibited scraping or stealth-evasion patterns.
