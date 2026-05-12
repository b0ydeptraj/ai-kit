# Relay-kit Locale Policy

Relay-kit uses one project-level locale policy file:

- `.relay-kit/state/runtime-locale.json`

This is a global switch for language preference across generated adapter surfaces.

Current scope is metadata localization only:

- skill frontmatter `description`
- command surface `intent` and `expected evidence`
- agent surface `display_name`, `intent`, and `expected evidence`

Canonical routing contracts remain stable in English (`skill id`, `command id`, `agent id`, route targets, layer contracts).

`relay-kit command list` and `relay-kit agent list` stay English by default so JSON contracts remain stable across locales.

## Default Policy

```json
{
  "schema_version": "relay-kit.runtime-locale.v1",
  "locale_profile": "en",
  "fallback_locale": "en",
  "enforce_output_language": true
}
```

## Public CLI

Show current locale policy:

```bash
relay-kit locale show /path/to/project --json
```

Set locale once:

```bash
relay-kit locale set /path/to/project --locale vi --json
```

Set locale during init/install:

```bash
relay-kit init /path/to/project --codex --locale vi
```

## Guarding Behavior

- `runtime_doctor --state-mode live` reports findings when runtime locale policy is missing or invalid.
- `readiness check --profile enterprise` includes a required `runtime-locale` gate.
- locale-aware validation accepts supported trigger prefixes for localized generated skills while keeping English fallback accepted.
- Locale policy is explicit and project-scoped; it is not forced globally for every repo.

## Locale Packs and Fallback

- v1 locale packs: `en`, `vi`
- runtime policy values are strict: `locale_profile` and `fallback_locale` must be one of `en`, `vi`
- unsupported locale values are flagged by runtime doctor/readiness and rejected by `relay-kit locale set`.
