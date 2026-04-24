# Relay-kit accessibility-review gate (v1)

`accessibility-review` makes accessibility a real gate instead of optional polish.

## What it checks (critical)

- keyboard navigation
- visible focus states
- semantic heading and landmark structure
- form labels and accessible names
- color contrast

If any critical check fails or is missing, verdict must be `HOLD`.

## Generate checklist template

```bash
python scripts/accessibility_review.py /path/to/project --surface "checkout-flow"
```

Checklist-only output is non-strict and must not be used as an accessibility pass verdict.

## Evaluate from a report file

Markdown report format:

```markdown
- [x] keyboard_navigation
- [x] focus_visible
- [x] semantic_structure
- [ ] form_labels
- [x] color_contrast
```

Run gate:

```bash
python scripts/accessibility_review.py /path/to/project --report-file a11y-report.md --strict
```

Exit code:

- `0`: pass
- `2`: hold (critical failure or missing evidence)
- `2`: strict mode was requested without `--report-file`
