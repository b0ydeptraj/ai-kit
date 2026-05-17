# mmo-cloud-operations-automation Operator Contract

Required contract:

- Scheduler, producer, worker pool, and queue boundaries.
- Queue dashboard fields: waiting, active, delayed, failed, completed, stalled, throughput, failure rate, average duration.
- Dead-letter policy and poison-message handling.
- Retry policy, jitter, and max attempts.
- Idempotency keys and dedupe strategy.
- Cost ceiling, quota guard, pause, resume, retry, drain, replay, and safe scale-down controls.
