# IC recording adapter handoff

The current expansion source profile selects this versioned package. The previous `client-support/ic-*` files remain unchanged as recording history. Original IC source remains at revision `39e2b7ecebc2829967a68b8111271d673bebdd70` with a clean tracked tree.

This version preserves the prior Text DOM, Camera defaults and Metro dependency visibility changes. It additionally mounts the Camera ref before the web style is ready, retains the latest source-specified imperative camera request, and reports the real map center and zoom through the native callback fields. It does not supply substitute coordinates or change incident data.

## Reproduce

From the Academy repository root, prepare a **new, empty** isolated destination using an independently verified IC checkout at the pinned revision. Existing source dependencies are linked; this command installs nothing and does not start the UI.

```sh
python3 sources/demo/client-support/ic-camera-ready-20261026/ic-prepare-recording.py \
  --source /path/to/IC \
  --destination /path/to/isolated-IC
node sources/demo/client-support/ic-camera-ready-20261026/ic-verify-text.cjs /path/to/isolated-IC
node sources/demo/client-support/ic-camera-ready-20261026/ic-verify-camera.cjs /path/to/isolated-IC
```

The preparer rejects changed source revisions, changed original file hashes and nonempty destinations. The retained baseline lists all six patched file hashes; the patch changes three original tracked files and adds three declared compatibility files. It excludes environment files, private directories, build output and credentials.

When browser use is available, launch the isolated copy through the versioned launcher or the expansion source-profile launcher. For the direct launcher, set `IC_RECORDING_DIR` to the prepared destination and `IC_RECORDING_PORT` to the intended free port. The default recording port is `19104`. Preserve the inherited `IC_MAPBOX_PUBKEY`; never print or embed its value. The launcher uses ordinary development mode with a local Metro cache reset, the fictional API at loopback port `18967`, and disabled analytics. It does not request device location.

## Checks completed

- Fresh isolated preparation applied the patch and reproduced all six active-copy hashes.
- Full IC `tsc --noEmit --pretty false` completed with zero diagnostics.
- Text DOM tests passed style flattening, line clamp, press/keyboard translation, accessibility and server rendering.
- Native default-camera and actual React ref/effect tests passed. They cover pre-load request retention, latest-request precedence, stable Camera mount through readiness, deferred map layers, finite actual center/zoom values, invalid coordinates and zero-valued settings/durations. Map behavior is mocked; no provider or GPS operation occurs. React test renderer emits its deprecation notice.
- All 1,370 unexcluded original tracked files were compared. Only the three declared tracked files differ; no undeclared or missing source files were found. The three new compatibility files match the baseline.
- All 15 source-profile tests and full `verify_client` checks passed against the active isolated copy and retained original dependencies.

See [verification.json](verification.json), [ic-recording-provenance.json](ic-recording-provenance.json), [ic-source-baseline.json](ic-source-baseline.json), and [source-profile-revision.json](source-profile-revision.json). The top-level expansion profile pins both retained and versioned support hashes. No lesson narration, approved video, raw screenshot or browser playback proof was changed by this adapter increment.

## Real UI checks still pending

Chrome is awaiting the human dismissal of an extension panel. No browser use or operational footage was accepted for this adapter version.

After browser access resumes, reopen the existing fictional warehouse training incident without closing it. Confirm that the incident map actually recenters on its Chicago incident or command-post geometry. Check actual map movement and use **Save View** only within the authorized fictional exercise; reopen the view to verify server persistence before claiming it. A static callback or mock test is not persistence evidence.

Annotation taps remain a separate existing web limitation: `MapView.web` does not bridge the source `onPress` handler. This camera repair therefore does not demonstrate tap-created lines, areas, text annotations or command-post placement. Do not claim those actions work on web from this package. Native annotation behavior also remains untested. No UI result, device GPS, native permission, provider delivery or hardware operation is established by these source checks.
