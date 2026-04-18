# Startup deep checkpoint automation

## What is installed

- Wrapper command: `run-daily-deep-checkpoints.cmd`
- Batch runner: `scripts/startup_deep_checkpoint.py`
- Deep checkpoint engine: `scripts/deep_checkpoint.py`

## Behavior

- Trigger: user logon/startup
- Runs 5 deep checkpoints (`--count 5`) with 10s gap
- Heavy output goes to `D:\relay-kit-checkpoint` and temp to `D:\relay-kit-temp`
- Daily guard file prevents duplicate same-day execution:
  - `D:\relay-kit-checkpoint\state\startup-deep-checkpoint-guard.json`

## Installed startup hook (active)

- Startup file path:
  - `C:\Users\b0ydeptrai\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\relay-kit-deep-checkpoint-startup.cmd`
- It calls:
  - `C:\Users\b0ydeptrai\OneDrive\Documents\relay-kit\run-daily-deep-checkpoints.cmd`

## Optional task scheduler command (reference)

```powershell
schtasks /Create /F /TN "RelayKit-DeepCheckpoint-Startup" /SC ONLOGON /DELAY 0000:30 /TR "\"C:\Users\b0ydeptrai\OneDrive\Documents\relay-kit\run-daily-deep-checkpoints.cmd\""
```

Note: if `schtasks` returns `Access is denied`, keep using the Startup-folder hook above.

## Key outputs

- Batch summary JSON:
  - `D:\relay-kit-checkpoint\logs\startup-deep-checkpoint-batch-*.json`
- Batch summary Markdown:
  - `D:\relay-kit-checkpoint\logs\startup-deep-checkpoint-batch-*.md`
- Each deep run report:
  - `D:\relay-kit-checkpoint\logs\deep-checkpoint-30-*.json`
  - `D:\relay-kit-checkpoint\logs\deep-checkpoint-30-*.md`

## Manual run

```powershell
cd C:\Users\b0ydeptrai\OneDrive\Documents\relay-kit
py -3.12 scripts\startup_deep_checkpoint.py --count 5 --output-root D:\relay-kit-checkpoint --temp-root D:\relay-kit-temp
```
