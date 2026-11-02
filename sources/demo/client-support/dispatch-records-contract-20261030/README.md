# Dispatch Records contract recording support — 2026-10-30

This opt-in layer fixes only the isolated Dispatch recording copy. New creates use the existing expo-crypto randomUUID(), Standard/Restricted/Protected classifications match Core 0/1/2, and record details consume Core's nested Values.Sections[].Rows[].Cells[]. The mapper preserves literal raw values, row identities, references, units, currency and zero offsets, and excludes withheld cells/keys without substituting Display or ciphertext.

Four production files and two synthetic regression files are retained as exact before/after snapshots and a unified patch. Original app and Core files, dependencies, source-profile history, auth, context, catalog, store/API and offline/ADP policy are unchanged. Existing terminology behavior and app-specific origin codes are preserved.

## Check and apply

Run from this support directory, with explicit existing isolated and original paths:

```sh
python3 -B prepare.py --target /path/to/isolated/Dispatch --original /path/to/original/Dispatch --core-source /path/to/Core
```

The default reads only. Add `--apply` to install the exact snapshots after review; every baseline is verified before any write. It refuses original-checkout targets, unknown edits, partial production patches, changed contracts/dependency hashes, unexpected regression files and changed prior recording compatibility. Expected pre-staged synthetic tests are allowed. A completely patched copy is verified without rewriting it. An optional `--report proofs/NEW-NAME.json` writes a new observation when invoked from this support directory; old reports are never replaced.

The current Dispatch recording copy was created from the unchanged original source using the existing filtered rsync convention: exclude .git, .env*, node_modules, .expo, dist, build, logs, *.log, private, .private, .aws, .ssh, .codex, .claude, .npmrc, coverage, Pods, DerivedData, .gradle, .cxx, .DS_Store, *.p12, *.p8, *.pem, *.key, *.keystore and *.mobileprovision. Use a new empty destination, rsync -a --safe-links, and link node_modules to the existing original installation. This package does not copy a tree, install dependencies or overwrite global source profiles. No matching credential/secret/Google-service/environment/private-key file names were found in the new copy. The original Metro config remains pinned; linked dependency resolution requires separate runtime verification.

## Verification

Both literal Core wire values and the actual app screen/store boundary are exercised. Against unchanged production, nine new regressions produced eight expected contract failures and one resumed-ID pass, without setup errors. Separately patched temporary source copies pass all nine. The actual isolated copy passes 10 focused Records suites / 73 tests. All six changed files pass explicit ESLint and the app's .prettierrc.js Prettier check. Eleven preparer guard tests pass, and a fresh temporary unified-patch replay reproduces all six retained outputs byte for byte. See verification.json and proofs/.

```sh
node node_modules/jest/bin/jest.js --runInBand --coverage=false --reporters=default src/lib/records src/stores/records src/components/records src/app/records/__tests__
node node_modules/eslint/bin/eslint.js --no-ignore 'src/app/records/new.tsx' 'src/app/records/[id].tsx' src/models/v4/records/index.ts src/lib/records/schema.ts src/lib/records/__tests__/wire-contract.test.ts src/app/records/__tests__/contract.test.tsx
node node_modules/prettier/bin/prettier.cjs --check --config .prettierrc.js 'src/app/records/new.tsx' 'src/app/records/[id].tsx' src/models/v4/records/index.ts src/lib/records/schema.ts src/lib/records/__tests__/wire-contract.test.ts src/app/records/__tests__/contract.test.tsx
```

From this support directory, run `python3 -B -m unittest discover -s tests -p test_prepare.py`. These are focused checks, not a whole-project build or native cryptography/provider test. No browser action, authentication, server launch/restart, API/DB mutation, old draft replay or successful UI save/readback is claimed. Root must deliberately launch or restart its owned app with --clear, preserving existing app-specific Mapbox environment values without logging or copying them, then capture actual normal-UI results.
