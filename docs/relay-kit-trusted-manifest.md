# Relay-kit Trusted Manifest

`relay-kit manifest stamp` adds deterministic trust metadata beside the bundle manifest.

This is not cryptographic signing. It is a local trust stamp that makes enterprise verification stricter without adding crypto dependencies.

## Commands

```bash
relay-kit manifest write /path/to/project
relay-kit manifest stamp /path/to/project --issuer relay-kit --channel enterprise
relay-kit manifest verify /path/to/project --trusted
```

Enterprise doctor uses the same trusted verification gate:

```bash
relay-kit doctor /path/to/project --policy-pack enterprise
```

If `.relay-kit/manifest/trust.json` is missing or stale, enterprise doctor fails.

Custom paths:

```bash
relay-kit manifest stamp /path/to/project \
  --manifest-file /path/to/bundles.json \
  --trust-file /path/to/trust.json \
  --issuer relay-kit \
  --channel enterprise

relay-kit manifest verify /path/to/project \
  --manifest-file /path/to/bundles.json \
  --trust-file /path/to/trust.json \
  --trusted
```

## What Trusted Verify Checks

`--trusted` requires:

- manifest checksum is valid
- each bundle skill list matches the current registry
- each skill hash matches the rendered skill contract
- trust metadata exists
- trust metadata schema is valid
- trust hash is valid
- trust manifest hash matches the manifest
- trust package metadata matches the manifest
- issuer and channel are present

## Failure Cases

These must fail in trusted mode:

- skill hash changed after manifest write
- manifest hash changed or became stale
- trust metadata missing
- trust metadata edited without updating its trust hash
- trust stamp points to a different manifest hash

## Boundary

This is a first trust-readiness slice for enterprise workflows. It does not prove signer identity.

Future cryptographic signing can extend the same shape with:

- public key IDs
- signature algorithm
- signature payload
- key rotation policy
- release-channel policy
