# Relay-kit MMO Automation References

This note records external references used to shape the Relay-kit MMO automation skill pack.

## Browser automation reliability

- Playwright best practices:
  [playwright.dev/docs/best-practices](https://playwright.dev/docs/best-practices)
- Selenium waits:
  [selenium.dev/documentation/webdriver/waits](https://www.selenium.dev/documentation/webdriver/waits/)

Used by:
- `mmo-browser-fleet-automation`

## Mobile automation reliability

- Appium quickstart:
  [appium.io/docs/en/latest/quickstart](https://appium.io/docs/en/latest/quickstart/)
- Android UI Automator:
  [developer.android.com/training/testing/other-components/ui-automator](https://developer.android.com/training/testing/other-components/ui-automator)

Used by:
- `mmo-mobile-app-automation`

## No-code and low-code orchestration

- n8n workflow creation:
  [docs.n8n.io/workflows/create](https://docs.n8n.io/workflows/create/)
- Make scenario scheduling:
  [help.make.com/schedule-a-scenario](https://help.make.com/schedule-a-scenario)
- IFTTT Webhooks:
  [help.ifttt.com/.../What-are-Webhooks](https://help.ifttt.com/hc/en-us/articles/34771177340315-What-are-Webhooks)

Used by:
- `mmo-lowcode-automation`
- `mmo-reup-automation`

## Social and marketing API guardrails

- X API rate limits:
  [docs.x.com/x-api/fundamentals/rate-limits](https://docs.x.com/x-api/fundamentals/rate-limits)
- YouTube developer policies:
  [developers.google.com/youtube/terms/developer-policies](https://developers.google.com/youtube/terms/developer-policies)

Used by:
- `mmo-social-marketing-automation`
- `mmo-reup-automation`

## HTTP/API and cloud operation safety

- AWS retry with backoff and jitter:
  [docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/retry-backoff.html](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/retry-backoff.html)
- Stripe idempotent requests:
  [docs.stripe.com/api/idempotent_requests](https://docs.stripe.com/api/idempotent_requests)
- Kubernetes CronJob:
  [kubernetes.io/docs/concepts/workloads/controllers/cron-jobs](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
- Terraform state locking:
  [developer.hashicorp.com/terraform/language/state/locking](https://developer.hashicorp.com/terraform/language/state/locking)

Used by:
- `mmo-http-api-automation`
- `mmo-cloud-operations-automation`
- `mmo-account-operations`

## Safety posture

The MMO skill pack is designed for authorized automation only:

- no CAPTCHA bypass guidance
- no identity spoofing guidance
- no policy-evasion guidance
- no abusive spam orchestration guidance
