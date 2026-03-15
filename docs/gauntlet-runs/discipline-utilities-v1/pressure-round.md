# discipline-utilities-v1 pressure round

## Scope

Pressure round re-ran 9 representative cases:

- 3 cases for `root-cause-debugging + debug-hub`
- 3 cases for `test-first-development + developer + test-hub`
- 3 cases for `evidence-before-completion + qa-governor + review-hub`

The goal was not to add more repo coverage. The goal was to see whether each skill still helps once it is embedded in a real workflow path instead of being evaluated in isolation.

## Track A ? `root-cause-debugging + debug-hub`

### A2-D ? `pallets/itsdangerous`
- commands re-run:
  - `Serializer vs TimedSerializer positional-salt repro via uv run python`
- fresh output:
  - `serializer value`
  - `BadSignature ... does not match`
- workflow verdict:
  - `debug-hub` would keep the lane in investigation mode, not bounce straight to a fix, because the failure comes from positional-argument drift rather than random token corruption.
- pressure result:
  - strong pass

### B2-D ? `encode/httpx`
- commands re-run:
  - `_resolve_qop(b"auth-int")` repro via `uv run --with-requirements requirements.txt python -`
- fresh output:
  - `NotImplementedError Digest auth-int support is not yet implemented`
- workflow verdict:
  - `debug-hub` would classify this as an explicit unsupported branch, not as a flaky auth bug.
- pressure result:
  - strong pass

### C3-D ? `sindresorhus/p-limit`
- commands re-run:
  - `rejectOnClear AbortError repro via node --input-type=module`
- fresh output:
  - `pendingBefore=1`
  - `AbortError This operation was aborted`
  - `pendingAfter=0`
- workflow verdict:
  - `debug-hub` would bounce this away from library-fix work and toward runtime-boundary classification.
- pressure result:
  - strong pass

## Track B ? `test-first-development + developer + test-hub`

### A2-T ? `pallets/itsdangerous`
- commands re-run:
  - `uv run --group tests pytest tests/test_itsdangerous/test_timed.py -q -k legacy_positional_salt_compatibility`
- fresh output:
  - targeted test stays red with `BadTimeSignature`
- workflow verdict:
  - `developer` gets a concrete red target, and `test-hub` correctly refuses to accept any implementation without turning this specific signal green.
- pressure result:
  - strong pass

### B3-T ? `pallets/flask`
- commands re-run:
  - `uv run --group tests pytest tests/test_async_optional.py -q`
- fresh output:
  - `1 passed`
- workflow verdict:
  - `developer` can protect an optional-dependency edge path with a very small targeted test, and `test-hub` gets proof without dragging in the whole async suite.
- pressure result:
  - pass

### C2-T ? `axios/axios`
- commands re-run:
  - `npx vitest run tests/unit/composeSignals.test.js`
- fresh output:
  - `4 passed`
- workflow verdict:
  - `developer` can lock a narrow helper behavior before any broader adapter work, and `test-hub` gets a stable regression check with low ceremony.
- pressure result:
  - pass

## Track C ? `evidence-before-completion + qa-governor + review-hub`

### A2-E ? `pallets/itsdangerous`
- commands re-run:
  - `uv run --group tests pytest tests/test_itsdangerous/test_timed.py -q`
- fresh output:
  - suite now fails because the compatibility test is intentionally red
- workflow verdict:
  - `qa-governor` blocks completion immediately and `review-hub` keeps the lane open until the compatibility claim is either fixed or explicitly narrowed.
- pressure result:
  - strong pass

### B4-E ? `fastapi/fastapi`
- commands re-run:
  - `uv run --group tests pytest tests/test_deprecated_openapi_prefix.py tests/test_openapi_cache_root_path.py -q`
- fresh output:
  - `6 passed`
- workflow verdict:
  - `qa-governor` still blocks any broad deprecation-cleanup claim because the proof covers only the exercised root_path/openapi_prefix surfaces.
- pressure result:
  - pass

### C4-E ? `date-fns/date-fns`
- commands re-run:
  - `corepack pnpm vitest run src/closestIndexTo/test.ts src/endOfDecade/test.ts`
- fresh output:
  - `16 passed`
- workflow verdict:
  - `review-hub` still refuses to treat green tests as proof that semantics may change safely, because this area is compatibility-sensitive by design.
- pressure result:
  - pass

## Pressure-round conclusion

- `root-cause-debugging` stayed useful under workflow pressure in all 3 representative cases.
- `test-first-development` stayed useful, but the itsdangerous case showed the real value comes when there is a meaningful red target rather than a general preference for more tests.
- `evidence-before-completion` was the most stable under pressure because it made both kinds of decisions correctly:
  - block when proof is missing or scope is too wide
  - approve only when the claim is genuinely narrow and supported

## Pressure-round recommendation

- `root-cause-debugging`: pressure signal supports promotion.
- `test-first-development`: pressure signal is positive but still not enough to erase baseline-noise concerns.
- `evidence-before-completion`: pressure signal strongly supports promotion.
