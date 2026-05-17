# mmo-mobile-app-automation Operator Contract

Required contract:

- Emulator or device matrix, provider, hub, and startup method.
- Device inventory fields: device id, OS, app version, provider, health, lease owner, battery, network, last run.
- App-state preconditions and teardown.
- Selector strategy, waits, and retries.
- Failure triage for crash, ANR, timeout, and environment drift.
- Run artifacts: logcat, screenshots, video or trace pointers, crash markers.

Do not design rooted, tampered, or policy-evasion mobile automation paths.
