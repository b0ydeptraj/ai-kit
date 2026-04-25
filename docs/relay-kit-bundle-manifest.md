# Relay-kit Bundle Manifest

`relay-kit manifest write` creates a checksummed JSON manifest for the current bundle registry.

Write a manifest:

```bash
relay-kit manifest write /path/to/project
```

Write to a custom path:

```bash
relay-kit manifest write /path/to/project --output-file /path/to/bundles.json
```

Verify a manifest:

```bash
relay-kit manifest verify /path/to/project --manifest-file /path/to/bundles.json
```

Write deterministic trust metadata:

```bash
relay-kit manifest stamp /path/to/project --issuer relay-kit --channel enterprise
```

Verify with trust metadata:

```bash
relay-kit manifest verify /path/to/project --trusted
```

The manifest includes:

- schema version
- generated timestamp
- package name and version
- bundle names and skill lists
- SHA-256 hash for each rendered skill contract
- full manifest hash

The trust metadata includes:

- schema version
- trust model
- issuer label
- release channel label
- package metadata
- manifest hash
- trust hash over the trust metadata

This is a checksum and deterministic trust-stamp gate, not cryptographic signing. It proves the manifest and trust metadata stayed internally consistent after stamping. It does not prove identity the way Ed25519, Sigstore, or KMS-backed signing would.
