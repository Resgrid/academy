# Unit Records contract support — 2026-10-30

This opt-in package corrects three client/server mismatches in a **separate Unit Records recording copy**:

- New creates use the existing `expo-crypto.randomUUID()` dependency for Core's GUID/idempotency contract.
- Classification matches Core: Standard `0`, Restricted `1`, Protected `2`; unknown values remain restricted.
- Details read nested `Values.Sections[].Rows[].Cells[]`. The mapper preserves returned values, references, section/row/ordinal identity, currency, units and zero offsets. It excludes `Withheld`, legacy `IsWithheld` and `WithheldFieldKeys`, and never substitutes display/redacted text or ciphertext.

Only four production files and two synthetic regression files change. Unit's context-bound create behavior remains intact: a resumed draft keeps its identity and recorded call/group context. The patch does not alter authentication, authorization, ADP, server catalog eligibility, offline policy, the Records store/API, an existing record or any credential/provider setting.

The original Unit checkout, Core and the historical native Unit recording profile remain unchanged. The native call lesson's build/source identities are preserved. This copy does not claim the older Unit camera/image/check-in compatibility layer; those opt-in versions remain separate.

## Reproduce the isolated source copy

The original Unit source must match the retained content inventory, with its existing lockfile dependencies installed. Run these commands from this support directory. Use explicit paths; the destination must be a fresh `Unit-records` or `Unit-records-*` directory directly under a `capture-apps` folder.

```sh
python3 -B create_copy.py \
  --target /path/to/capture-apps/Unit-records \
  --original /path/to/Unit \
  --core-source /path/to/Core \
  --create

python3 -B prepare.py \
  --target /path/to/capture-apps/Unit-records \
  --original /path/to/Unit \
  --core-source /path/to/Core
```

Without `--create`, the copy helper only reports its opt-in requirement. It copies only the 1,533 pinned regular source files, excluding environment/private/Git/native-output paths, and links the original dependencies. It never clones, installs, launches or reads environment/key values. Existing targets and all historical `native-unit*` trees are refused.

The preparer is read-only by default. It verifies the complete original content inventory, unchanged target files, package/lock, Core contracts, patch and before/after snapshots. Unknown edits, a partial production patch, symlinks, changed contracts or an original/native target fail before application. Exact pre-staged regression files are accepted; unknown same-path files are refused.

After review, apply the exact retained snapshots:

```sh
python3 -B prepare.py \
  --target /path/to/capture-apps/Unit-records \
  --original /path/to/Unit \
  --core-source /path/to/Core \
  --apply
```

A complete current patch is checked without rewriting it. Optional `--report proofs/NEW-NAME.json` writes one new local source observation and refuses an existing report path. Prior metadata/patch/test-harness bytes and the earlier read-only observation remain retained under `history/` and `proofs/`.

## Verification

The unchanged Unit Records baseline passes **9 suites / 78 tests**. The nine new regressions then produce **8 expected failures / 1 pass**, with no setup failures. The corrected isolated copy passes **11 suites / 87 tests**. Fourteen temporary-fixture preparer/copy guards pass, including original/native target rejection, source/Core drift, partial patches, unknown edits, excluded environment files and write rollback. The unified patch also replays to the exact six after-snapshots in a temporary tree.

From the isolated app directory:

```sh
node node_modules/jest/bin/jest.js --runInBand --coverage=false --reporters=default \
  --cacheDirectory=/private/tmp/academy-unit-records-contract-jest \
  src/lib/records src/stores/records src/components/records src/app/records/__tests__

node node_modules/eslint/bin/eslint.js --no-ignore \
  'src/app/records/new.tsx' 'src/app/records/[id].tsx' \
  src/models/v4/records/index.ts src/lib/records/schema.ts \
  src/lib/records/__tests__/wire-contract.test.ts src/app/records/__tests__/contract.test.tsx

node node_modules/prettier/bin/prettier.cjs --check --config .prettierrc.js \
  'src/app/records/new.tsx' 'src/app/records/[id].tsx' \
  src/models/v4/records/index.ts src/lib/records/schema.ts \
  src/lib/records/__tests__/wire-contract.test.ts src/app/records/__tests__/contract.test.tsx
```

From this support directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_prepare.py -v
```

These are synthetic focused checks, not a whole-project/native build or actual server save. The test harness mocks UUID/network/UI boundaries while exercising the real screen handler and Records store request construction. The first test harness produced import-style lint warnings; its bytes are retained in history. The final harness uses Jest's actual-module helper and has no lint warnings.

## Runtime and footage boundary

No Metro/server launch, browser/simulator operation, live store/context injection, API/DB call, sign-in or existing-record mutation was performed for this package. The prepared app is separate from the native call recording. Root must choose and record a new source-bound launch revision and then capture the normal authorized UI before teaching a successful Unit Records action. Inherited `UNIT_MAPBOX_PUBKEY` must be preserved in memory by any future launcher, without printing or saving its value. No key or private URL belongs in this package.

Do not silently rekey or replay an existing non-GUID pending draft. A successfully displayed generic catalog form is not proof of a call-linked launcher/context. Keep failed captures and source history, and verify the actual returned record and retained call/group relationship through the app.
