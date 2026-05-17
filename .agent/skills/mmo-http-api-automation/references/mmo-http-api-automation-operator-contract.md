# mmo-http-api-automation Operator Contract

Required contract:

- Endpoint catalog grouped by risk and side-effect level.
- Auth scope and token lifecycle.
- Request ledger fields: request id, endpoint, method, status code, duration, retry count, origin, cost, idempotency key.
- Rate-limit parsing and reset-aware retry backoff.
- Redacted raw request/response samples.
- Replay-safety policy for write operations.
- Contract drift check against schema or official docs.
