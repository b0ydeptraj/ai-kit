# release-readiness

## Pre-deploy gate

- [ ] `build_passed` - Build and packaging checks passed
- [ ] `tests_passed` - Required test suite passed
- [ ] `migration_plan_checked` - Migration and compatibility impact reviewed
- [ ] `rollback_plan_ready` - Rollback plan and trigger thresholds documented

## Post-deploy smoke gate

- [ ] `healthcheck_ok` - Service health checks are green
- [ ] `critical_user_flow_ok` - Critical user flow smoke tests passed
- [ ] `error_rate_within_budget` - Error rate and latency stay within budget
- [ ] `rollback_signals_clear` - No rollback triggers fired

## Signal evaluation

- pre: PASS
- post: PASS
