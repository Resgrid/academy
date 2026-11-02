# IC v3 maintainer handoff

Use this version through the expansion source profile. V2 and its proofs remain unchanged. Source revision and every patched hash are pinned in ic-source-baseline.json; the Unit projection reference is also pinned there.

Prepare a fresh empty copy from the repository root:

```sh
python3 sources/demo/client-support/ic-camera-ready-20261027-v3/ic-prepare-recording.py --source /path/to/IC --destination /path/to/isolated-IC
node sources/demo/client-support/ic-camera-ready-20261027-v3/ic-verify-text.cjs /path/to/isolated-IC
node sources/demo/client-support/ic-camera-ready-20261027-v3/ic-verify-camera.cjs /path/to/isolated-IC
```

The guarded preparer installs nothing and links existing source dependencies. The launcher retains normal development mode, --clear, inherited map credentials, fictional loopback API and disabled analytics. Native source is unchanged.

Checks passed: the initial-retry regression fails against v2 and passes v3; later defaultSettings cannot overwrite a newer source request; actual MapView constructor/style-load tests select Mercator; finite actual center/zoom callbacks, Text DOM and all prior camera checks pass. Full TypeScript no-emit reports zero diagnostics. Fresh preparation reproduces all six hashes. See regression-before-after.json and verification.json.

Actual UI was verified on 2026-10-27 after restarting only the isolated IC Metro listener with --clear. The Incident Map showed genuine Chicago cartography and Squad 3. A normal pointer pan, Save View, return through Command Board / Open incident map, and full browser reload retained the same panned framing. Existing board assignments, 50% objective, 1/2 partial need, internal note and command log also remained visible. The eight exact reviewed JPEGs and hashes are linked from runtime-validation-20261027.json. This source capture review does not approve any full lesson or video.

The prior Metro process ran in CI mode with reloads disabled. Source file edits plus browser reload did not prove which compatibility version it served. Earlier unacceptable framing cannot be assigned to v2/v3 from file hashes alone. After changing this isolated source, verify the listener/cwd and restart Metro with --clear before testing; preserve inherited credentials and never print them. The actual browser result and the mocked source regression are distinct evidence.

No separate Recenter button, native GPS/provider behavior, multi-user synchronization or annotation success was exercised. Annotation onPress remains an existing separate web limit. Line, Area and Text toolbar visibility does not establish shape creation or persistence. Preserve warehouse call51001 and the original three active incidents. No call was created or closed in this checkpoint.
