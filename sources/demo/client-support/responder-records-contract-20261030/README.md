# Responder Records contract support — 2026-10-30

This opt-in layer fixes three client/server contract mismatches in an isolated Responder recording copy:

- New records use the existing `expo-crypto.randomUUID()` instead of a non-GUID draft identifier.
- Field classification matches Core: Standard `0`, Restricted `1`, Protected `2`. Unknown classifications remain restricted.
- Details read Core's nested `Values.Sections[].Rows[].Cells[]`. The mapper preserves flat-array/prefill callers, returned literal values, references, row identity, units, currency and zero offsets. It excludes `Withheld`/legacy `IsWithheld` cells and `WithheldFieldKeys`; it never substitutes `Display`, ciphertext or invented content.

The patch changes four production files and adds two synthetic regression files. It does not change the original Responder checkout, Core, dependencies, API/auth/context/store gates, ADP, catalog eligibility, `AllowOffline`, existing records or other recording compatibility patches.

## Check and apply

Run from this directory. All three paths are explicit; use an existing isolated copy already carrying the retained seven-file Responder web compatibility layer. Its `node_modules` must be the expected symlink to the original installation. This script deliberately does not create or clone a source tree, install packages, launch Metro, refresh historical provenance or alter global source profiles.

```bash
python3 prepare.py \
  --target /path/to/isolated/Responder \
  --original /path/to/original/Responder \
  --core-source /path/to/Core
```

The default is read-only. It checks the pinned metadata, patch and snapshots, original and Core contracts, dependency lock/package files, all seven prior compatibility outputs, unchanged auth/context/store/API gates, and every target file. Unknown edits, partial production patches, symlinked files, changed contracts and an original-checkout target are rejected.

To apply the exact retained outputs after review:

```bash
python3 prepare.py \
  --target /path/to/isolated/Responder \
  --original /path/to/original/Responder \
  --core-source /path/to/Core \
  --apply
```

Every baseline is verified before the first write. Exact pre-staged regression files are allowed after a baseline test run; unknown same-path tests are refused. A complete current patch is verified without rewriting it. The unified patch is retained for inspection and was separately replayed against a fresh temporary baseline tree. The guarded preparer writes the hash-verified snapshots rather than accepting fuzzy patch hunks.

An optional `--report proofs/NEW-NAME.json` records a new source-preparation observation inside this package and refuses existing report paths. Historical reports and support versions remain intact.

## Verification

From the isolated app directory, using its existing dependencies:

```bash
node node_modules/jest/bin/jest.js --runInBand --coverage=false --reporters=default \
  --cacheDirectory=/private/tmp/academy-responder-records-contract-jest \
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

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_prepare.py -v
```

The existing focused baseline passed 7 suites/63 tests. Nine new regression tests then ran against unchanged production code: 8 failed on the expected contract boundaries and the resumed-ID test passed, with no setup failures. Final focused verification passes 10 suites/76 tests, including the existing record-detail suite, plus 11 temporary-fixture preparer guards. Explicit lint and Responder-config formatting checks pass. These are focused checks; no whole-project build or native cryptography/provider execution is claimed. UUID generation and network boundaries are mocked in the synthetic screen regression; the actual production handler/store and valid UUID request contract are exercised.

The first staged formatting used Core's editor settings. That version and its actual apply observation are retained under `history/pre-app-editorconfig-format/` and `proofs/applied-20261030.json`. The final patch uses Responder's own formatting. An initial unstable test translation mock and the later test-lint cleanup are also retained as history; neither changed product behavior.

## Runtime boundary

No app reload, server restart, API/DB action or record retry was performed for this package. Metro running with `CI=1` does not watch source edits; Root must deliberately restart the owned Responder server with its retained environment and `--clear` after reviewing the final pins. No token is copied, blanked, printed or persisted here. Record the new source revision before capturing a fresh normal-UI attempt. The existing failed footage is historical evidence, not a saved record. Previously retained non-GUID pending drafts are not silently rekeyed or replayed.

Do not treat this opt-in layer as the older global profile's complete source identity. The old profile/support files remain unchanged; bind this package's final metadata and verification observation as an additional recording revision. Actual post-reload UI save/readback remains unverified until Root records it.
