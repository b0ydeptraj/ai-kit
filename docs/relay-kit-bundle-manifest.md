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

The manifest includes:

- schema version
- generated timestamp
- package name and version
- bundle names and skill lists
- SHA-256 hash for each rendered skill contract
- full manifest hash

This is a checksum gate, not cryptographic signing. Signing can be layered on top once release keys and distribution policy exist.
