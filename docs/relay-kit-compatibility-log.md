# Relay-kit compatibility cycle log

- Cycle start commit: `8cc21b6`
- Technical rename commit: `d5928c9`
- Cycle start date: `2026-03-17`
- Cycle target length: `14 days`
- Current status: `active`
- Removal decision: `not ready`

## Summary template

`python scripts/summarize_compat_cycle.py --write-summary` refreshes this block.

<!-- compat-cycle-summary:start -->
- Last summary update: `2026-04-14 16:05:29 SE Asia Standard Time`
- Source filter: `interactive`
- Total logged events considered: `39`
- Total real runs: `33`
- `relay_kit.py` runs: `18`
- `python_kit.py` runs: `2`
- `relay_kit_legacy.py` runs: `1`
- `python_kit_legacy.py` runs: `1`
- Generic dual-write runs: `5`
- Distinct target projects: `14`
- Failed runs in filtered set: `0`
- Last validation result: `pass`
- Last observed event: `2026-04-14T16:03:12+07:00`
<!-- compat-cycle-summary:end -->

Manual gate:

- Cycle end date: `TBD`
- Blocking issues: `0`
- Open medium+ issues: `0`
- Removal decision: `not ready`

## Minimum evidence required

- `10` real runs total
- `6` runs via `relay_kit.py`
- `2` runs via `python_kit.py`
- `1` run via `relay_kit_legacy.py`
- `1` run via `python_kit_legacy.py`
- `2` generic runs that verify both:
  - `.relay-kit-prompts`
  - `.python-kit-prompts`
- At least `2` target projects or target workspaces

## Run template

Copy this block for each real run.

```md
## Run YYYY-MM-DD HH:MM ICT

- Entry point: `relay_kit.py`
- Flow: `v3 bundle`
- Command:
  - `python relay_kit.py . --bundle baseline --ai codex --emit-contracts --emit-docs --emit-reference-templates`
- Target project:
  - `C:\...`
- Expected outputs:
  - `.codex/skills`
  - `.ai-kit/contracts`
  - `.ai-kit/docs`
- Generic output involved:
  - `no`
- Result:
  - `pass`
- Notes:
  - none
```

## Generic run template

Use this version when the run uses `--ai generic`.

```md
## Run YYYY-MM-DD HH:MM ICT

- Entry point: `relay_kit.py`
- Flow: `v3 bundle`
- Command:
  - `python relay_kit.py C:\path\to\target --bundle baseline --ai generic`
- Target project:
  - `C:\path\to\target`
- Generic output involved:
  - `yes`
- Canonical path created:
  - `.relay-kit-prompts`
- Compatibility mirror created:
  - `.python-kit-prompts`
- Mirror equivalent:
  - `yes`
- Result:
  - `pass`
- Notes:
  - none
```

## Failure run template

Use this when a run fails or needs fallback behavior.

```md
## Run YYYY-MM-DD HH:MM ICT

- Entry point: `python_kit.py`
- Flow: `legacy kit`
- Command:
  - `python python_kit.py C:\path\to\target --legacy-kit python --ai claude`
- Target project:
  - `C:\path\to\target`
- Generic output involved:
  - `no`
- Result:
  - `fail`
- Failure:
  - short description
- Root cause:
  - known / unknown
- Workaround used:
  - yes / no
- Severity:
  - blocking | high | medium | low
- Notes:
  - extra evidence
```

## Periodic checkpoint template

Use every 3 days or before pushing compatibility-related changes.

```md
## Checkpoint YYYY-MM-DD

- Validation command:
  - `python scripts/validate_runtime.py`
- Result:
  - `pass`
- Notes:
  - none
```

## Commands

```bash
python scripts/summarize_compat_cycle.py
python scripts/summarize_compat_cycle.py --write-summary
python scripts/summarize_compat_cycle.py --checkpoint
```

Windows one-click helpers:

```bat
run-relay-kit-summary.cmd
run-relay-kit-checkpoint.cmd
```


## Checkpoint 2026-03-17 09:42 SE Asia Standard Time

- Source filter:
  - `interactive`
- Total logged events considered:
  - `1`
- Total real runs:
  - `0`
- `relay_kit.py` runs:
  - `0`
- `python_kit.py` runs:
  - `0`
- `relay_kit_legacy.py` runs:
  - `0`
- `python_kit_legacy.py` runs:
  - `0`
- Generic dual-write runs:
  - `0`
- Distinct target projects:
  - `0`
- Failed runs in filtered set:
  - `0`
- Validation command:
  - `python scripts/validate_runtime.py`
- Result:
  - `pass`
- Notes:
  - auto-generated checkpoint


## Checkpoint 2026-03-18 22:48 SE Asia Standard Time

- Source filter:
  - `interactive`
- Total logged events considered:
  - `2`
- Total real runs:
  - `1`
- `relay_kit.py` runs:
  - `1`
- `python_kit.py` runs:
  - `0`
- `relay_kit_legacy.py` runs:
  - `0`
- `python_kit_legacy.py` runs:
  - `0`
- Generic dual-write runs:
  - `0`
- Distinct target projects:
  - `1`
- Failed runs in filtered set:
  - `0`
- Validation command:
  - `python scripts/validate_runtime.py`
- Result:
  - `pass`
- Notes:
  - auto-generated checkpoint


## Checkpoint 2026-03-23 21:07 SE Asia Standard Time

- Source filter:
  - `interactive`
- Total logged events considered:
  - `4`
- Total real runs:
  - `2`
- `relay_kit.py` runs:
  - `2`
- `python_kit.py` runs:
  - `0`
- `relay_kit_legacy.py` runs:
  - `0`
- `python_kit_legacy.py` runs:
  - `0`
- Generic dual-write runs:
  - `0`
- Distinct target projects:
  - `1`
- Failed runs in filtered set:
  - `0`
- Validation command:
  - `python scripts/validate_runtime.py`
- Result:
  - `pass`
- Notes:
  - auto-generated checkpoint


## Checkpoint 2026-04-01 09:39 SE Asia Standard Time

- Source filter:
  - `interactive`
- Total logged events considered:
  - `5`
- Total real runs:
  - `3`
- `relay_kit.py` runs:
  - `3`
- `python_kit.py` runs:
  - `0`
- `relay_kit_legacy.py` runs:
  - `0`
- `python_kit_legacy.py` runs:
  - `0`
- Generic dual-write runs:
  - `0`
- Distinct target projects:
  - `1`
- Failed runs in filtered set:
  - `0`
- Validation command:
  - `python scripts/validate_runtime.py`
- Result:
  - `pass`
- Notes:
  - auto-generated checkpoint


## Checkpoint 2026-04-07 16:06 SE Asia Standard Time

- Source filter:
  - `interactive`
- Total logged events considered:
  - `24`
- Total real runs:
  - `19`
- `relay_kit.py` runs:
  - `9`
- `python_kit.py` runs:
  - `2`
- `relay_kit_legacy.py` runs:
  - `1`
- `python_kit_legacy.py` runs:
  - `1`
- Generic dual-write runs:
  - `2`
- Distinct target projects:
  - `9`
- Failed runs in filtered set:
  - `0`
- Validation command:
  - `python scripts/validate_runtime.py`
- Result:
  - `pass`
- Notes:
  - auto-generated checkpoint


## Checkpoint 2026-04-14 14:01 SE Asia Standard Time

- Source filter:
  - `interactive`
- Total logged events considered:
  - `33`
- Total real runs:
  - `27`
- `relay_kit.py` runs:
  - `17`
- `python_kit.py` runs:
  - `2`
- `relay_kit_legacy.py` runs:
  - `1`
- `python_kit_legacy.py` runs:
  - `1`
- Generic dual-write runs:
  - `4`
- Distinct target projects:
  - `13`
- Failed runs in filtered set:
  - `0`
- Validation command:
  - `python scripts/validate_runtime.py`
- Result:
  - `pass`
- Notes:
  - auto-generated checkpoint


## Checkpoint 2026-04-14 16:05 SE Asia Standard Time

- Source filter:
  - `interactive`
- Total logged events considered:
  - `39`
- Total real runs:
  - `33`
- `relay_kit.py` runs:
  - `18`
- `python_kit.py` runs:
  - `2`
- `relay_kit_legacy.py` runs:
  - `1`
- `python_kit_legacy.py` runs:
  - `1`
- Generic dual-write runs:
  - `5`
- Distinct target projects:
  - `14`
- Failed runs in filtered set:
  - `0`
- Validation command:
  - `python scripts/validate_runtime.py`
- Result:
  - `pass`
- Notes:
  - auto-generated checkpoint
