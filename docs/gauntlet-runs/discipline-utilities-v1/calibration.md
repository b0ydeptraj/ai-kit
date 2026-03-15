# Round 1 calibration

## Control checks

## Round 0 summary

- `python python_kit.py --list-skills` passed and listed `discipline-utilities` with exactly 3 skills.
- Clean temp-generation passed for `round2`, `round3`, `round4`, and `discipline-utilities`.
- Overlay gating checks passed:
  - `round2` did not emit `discipline-utilities` skills or docs.
  - `round3` did not emit `discipline-utilities` skills or docs.
  - `round4` kept round4 topology/state/docs but did not leak `discipline-utilities` content.
  - `discipline-utilities` emitted only the 3 overlay skills plus 5 overlay docs.
- Runtime wiring checks passed in the live repo for:
  - `debug-hub -> root-cause-debugging`
  - `developer -> test-first-development`
  - `test-hub -> evidence-before-completion`
  - `qa-governor -> evidence-before-completion`
  - `team -> parallel-execution.md`
  - `plan-hub -> planning-discipline.md`
  - `review-hub -> review-loop.md` and `branch-completion.md`
  - `scrum-master -> planning-discipline.md`
  - `agentic-loop -> root-cause-debugging` and `evidence-before-completion`

## Repo-by-repo calibration


### `pallets/click`

- slot: `Track A`
- workdir: `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\click`
- setup command: `uv run --group tests pytest tests/test_utils.py -q`
- baseline test command: `uv run --group tests pytest tests/test_utils.py -q`
- lint/type command: `not run in calibration`
- baseline status: 76 passed, 67 skipped
- reproduction status: Confirmed A1-D seed: a daemon thread calling `_tempfilepager` with an infinite generator stayed alive after 300ms, which proves eager consumption before pager execution.
- calibration verdict: `ready`
- notes: All three click tasks retained. A1-E stays conditional because there is no candidate fix under review yet.


### `pallets/itsdangerous`

- slot: `Track A`
- workdir: `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\itsdangerous`
- setup command: `uv run --group tests pytest tests/test_itsdangerous/test_timed.py -q`
- baseline test command: `uv run --group tests pytest tests/test_itsdangerous/test_timed.py -q`
- lint/type command: `not run in calibration`
- baseline status: 101 passed
- reproduction status: Confirmed A2-D seed: `Serializer.loads(token, "legacy-salt")` works positionally, while `TimedSerializer.loads(token, "legacy-salt")` fails with `BadTimeSignature`, showing positional compatibility drift.
- calibration verdict: `ready`
- notes: All three tasks retained.


### `pallets-eco/blinker`

- slot: `Track A`
- workdir: `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\blinker`
- setup command: `uv run --group tests pytest tests/test_signals.py -q`
- baseline test command: `uv run --group tests pytest tests/test_signals.py -q`
- lint/type command: `not run in calibration`
- baseline status: 19 passed
- reproduction status: Confirmed A3-D seed: a malformed `receiver_connected` listener raises `TypeError`, and the attempted receiver is disconnected (`receiver_list == []`).
- calibration verdict: `ready`
- notes: Restored a prior pilot-only local test addition before calibration, then kept all three tasks.


### `pallets/markupsafe`

- slot: `Track A`
- workdir: `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\markupsafe`
- setup command: `uv run --group tests pytest tests/test_ext_init.py -q -rs`
- baseline test command: `uv run --group tests pytest tests/test_ext_init.py -q -rs`
- lint/type command: `not run in calibration`
- baseline status: 1 passed, 1 skipped (`speedups not active`)
- reproduction status: Confirmed A4-D/A4-E seed as environment-sensitive rather than immediately buggy: the extension-init test suite skips the no-speedups path when speedups are inactive on this machine.
- calibration verdict: `conditional`
- notes: A4-D and A4-E retained. A4-T stays conditional because the useful branch is packaging/import-path sensitive.


### `httpie/cli`

- slot: `Track B`
- workdir: `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\httpie-cli`
- setup command: `uv run --with-editable ".[test]" pytest tests/test_errors.py -q`
- baseline test command: `uv run --with-editable ".[test]" pytest tests/test_errors.py -q`
- lint/type command: `not run in calibration`
- baseline status: 12 passed
- reproduction status: Concrete code-path evidence confirmed in `httpie/client.py:66-116`: request kwargs and environment-mergeable kwargs are split and later merged, so the seed is real even before a full CLI repro.
- calibration verdict: `conditional`
- notes: B1-D retained. B1-T and B1-E remain conditional until the exact redirect/error branch under review is chosen.


### `encode/httpx`

- slot: `Track B`
- workdir: `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\httpx`
- setup command: `uv run --with-requirements requirements.txt pytest tests/test_auth.py -q`
- baseline test command: `uv run --with-requirements requirements.txt pytest tests/test_auth.py -q`
- lint/type command: `not run in calibration`
- baseline status: 8 passed
- reproduction status: Confirmed B2-D seed: a digest challenge with `qop="auth-int"` raises `NotImplementedError("Digest auth-int support is not yet implemented")` in `httpx._auth.DigestAuth`.
- calibration verdict: `ready`
- notes: All three tasks retained.


### `pallets/flask`

- slot: `Track B`
- workdir: `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\flask`
- setup command: `uv run --group tests pytest tests/test_async.py tests/test_config.py tests/test_reqctx.py -q`
- baseline test command: `uv run --group tests pytest tests/test_async.py tests/test_config.py tests/test_reqctx.py -q`
- lint/type command: `not run in calibration`
- baseline status: 41 passed
- reproduction status: Confirmed optional-dependency path is real: `tests/test_async.py` uses `pytest.importorskip("asgiref")`, and the selected tests pass with the tests group installed.
- calibration verdict: `conditional`
- notes: All three Flask tasks retained but kept conditional because the missing-dependency path is environment dependent.


### `fastapi/fastapi`

- slot: `Track B`
- workdir: `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\fastapi`
- setup command: `uv run --group tests pytest tests/test_jsonable_encoder.py tests/test_deprecated_openapi_prefix.py tests/test_openapi_cache_root_path.py -q`
- baseline test command: `uv run --group tests pytest tests/test_jsonable_encoder.py tests/test_deprecated_openapi_prefix.py tests/test_openapi_cache_root_path.py -q`
- lint/type command: `not run in calibration`
- baseline status: 30 passed
- reproduction status: Confirmed B4 seeds: `jsonable_encoder({"value": Decimal("1.23")})` emits `1.23`, and openapi/root_path coverage already exists in `tests/test_deprecated_openapi_prefix.py` and `tests/test_openapi_cache_root_path.py`.
- calibration verdict: `ready`
- notes: All three tasks retained.


### `sindresorhus/ky`

- slot: `Track C`
- workdir: `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\ky`
- setup command: `npm install`
- baseline test command: `npx ava test/methods.ts`
- lint/type command: `not run in calibration`
- baseline status: 3 passed, 1 known failure
- reproduction status: Confirmed C1-D seed: `npx ava test/methods.ts` reports `[expected fail] custom method remains identical`, which keeps the method-semantics mismatch actionable.
- calibration verdict: `conditional`
- notes: C1-D and C1-T retained. C1-E remains conditional because the `ResponsePromise.json` typing question is review-driven rather than runtime-failing today.


### `axios/axios`

- slot: `Track C`
- workdir: `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\axios`
- setup command: `npm install`
- baseline test command: `npx vitest run tests/unit/composeSignals.test.js tests/unit/axiosHeaders.test.js`
- lint/type command: `not run in calibration`
- baseline status: 40 passed across 2 unit files
- reproduction status: Concrete seed evidence confirmed in both old and new suites: old adapter/regression files still contain skip-based branches, while modern vitest coverage for `composeSignals` and `AxiosHeaders` passes.
- calibration verdict: `conditional`
- notes: C2-T and C2-E retained as ready. C2-D remains conditional because the skip-based seed is split across legacy runner paths.


### `sindresorhus/p-limit`

- slot: `Track C`
- workdir: `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\p-limit`
- setup command: `npm install`
- baseline test command: `npx ava test.js`
- lint/type command: `not run in calibration`
- baseline status: 21 passed
- reproduction status: Current Node 22 does not trigger the Node 20 AVA skip, but the underlying `rejectOnClear` behavior is concrete: a pending task is aborted with `DOMException [AbortError]` after `clearQueue()`.
- calibration verdict: `adjusted`
- notes: Kept the same files and skill family, but reframed C3-D/C3-T around `rejectOnClear` semantics instead of the Node-20-only skip gate.


### `date-fns/date-fns`

- slot: `Track C`
- workdir: `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\date-fns`
- setup command: `git -c url.https://github.com/.insteadOf=git@github.com: submodule update --init --recursive && corepack pnpm install`
- baseline test command: `corepack pnpm vitest run src/closestIndexTo/test.ts src/endOfDecade/test.ts`
- lint/type command: `not run in calibration`
- baseline status: 15 passed across 2 test files
- reproduction status: Repo was initially blocked by uninitialized workspace submodules; after submodule init and pnpm install, targeted tests for `closestIndexTo` and `endOfDecade` passed and the seeds stayed actionable.
- calibration verdict: `ready`
- notes: All three tasks retained.


## Calibration decisions

- `p-limit` stays in the matrix, but the actionable focus shifts from the Node-20-only skip guard to the underlying `rejectOnClear` abort semantics in the same file and task family.
- `date-fns` stays in the matrix after submodule initialization; no repo swap was needed.
- Conditional tasks stay conditional when the seed is real but the exact candidate change is not yet selected.
