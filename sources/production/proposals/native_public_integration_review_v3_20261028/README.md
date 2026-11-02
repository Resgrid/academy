# Native capture integration: revised two-stage proposal

This package is an **unadopted proposal**. Existing production renderer, evidence validator and exporter have not changed. No real native package has been qualified by this code. Tests use explicitly synthetic images, media identities, source files and review records. V1, V2 and the earlier private-root integration patch remain historical and unchanged.

The proposed trust boundary follows the existing browser evidence model: a named reviewer inspects actual application pixels, ordinary UI actions and current source/build correspondence. Hashes bind the reviewed artifacts. They do not authenticate pixels, a person, a transport client, loaded code or executed JavaScript. There is no new signing system or user approval workflow.

## Capture review and public rebuild are separate

1. The private capture stage keeps the real installed app and managed source/dependency roots outside public assets. `native_capture_review.inspect_private_context(...)` reads the actual Mach-O, Info.plist, declared source/lock/module files and retained served-response metadata. It compares them with the declared digests and public snapshots. It enumerates and stream-hashes every installed thin/fat Mach-O file, including the debug dylib and embedded frameworks, then rejects any added, removed or changed code entry. The executable stub alone is insufficient. It neither records a passed pixel review nor operates the app. Its result remains `publishable:false`, `review_still_required:true`. It can inspect an unreviewed draft before the reviewer authors a final receipt.
2. The responsible reviewer inspects the unchanged simctl PNG, normal UI ledger, native geometry, foreground identity and installed/source correspondence. The reviewer authors specific findings and a binding receipt. `validate_private_context(...)` can then recheck the final review package against the actual private bytes. The baseline revision and build/source correspondence must be checked against the retained source-preparation/build records; this helper does not infer a Git revision from an isolated checkout or reconstruct a complete build graph.
3. The retained public package contains only the unchanged PNG, measured native geometry, redacted ordinary-UI ledger, nonsecret source/lock snapshots, complete app-relative installed Mach-O digest/size inventory plus plist **digest**, served-byte metadata and named review receipts. No installed binary, SDK, node_modules tree, private key, bundle body or runtime JS root is copied into it.
4. Public rebuilds run `native_capture_public.validate_native_source(...)` against those retained files. It has no private-root parameter and imports only standard-library code. It rereads and rehashes the files, checks the review and identity bindings, and derives the fit. The offline positive tests delete every synthetic private app/source/dependency root before running the public source validator, whole evidence validator, exporter preflight and site export.

The private-stage findings are review evidence, not a cached boolean accepted in place of public verification. `passed`, `publishable`, `native_roots`, `native_approved` and similar source-row self-approval fields cannot enable the native branch. Source validation always returns `publishable:false`; publication still needs the ordinary frozen narration/audio/listening, exact cue-to-screen, source image, actual encoded-frame and advancing beginning/middle/end playback gates.

## Public source package

The schema identifier is `academy.reviewed-native-public-package.proposal.v3`. `validate_public_package(package, asset_root)` checks the following groups:

- `session`: explicit new dedicated simulator ID/UDID, device/runtime description, creation time and matching retained creation receipt.
- `build`: the supported Unit development bundle and `development_metro` branch, base source revision, actual SDK name, complete sorted installed Mach-O file/digest/size inventory (including the debug dylib and embedded frameworks), actual plist digest, source snapshot manifest and named installed-correspondence review. Package, actual native Pod lock and relevant screen source snapshots are mandatory. Legitimate CSS source is allowed under the same unchanged key/body checks; this is not an exception for private material. Declared source/module/patch snapshots must match private bytes during capture review; source scope remains explicit rather than a claim that the whole JS graph was executed.
- `capture`: original PNG file/hash and actual dimensions/time, exact `ios_simulator_screenshot` provenance, explicit-device simctl method, same session/UDID and Unit foreground identity. No browser URL or DOM sidecar is invented.
- `normal_ui`: the retained redacted original ledger plus ordered, source-entry-bound reviewed actions and geometry/device events. Hidden API/state writes, launch hooks and automatic permission grants are unsupported. The final ordinary UI guard must be within the explicit 60 second bound of the screenshot; its actual age remains recorded. It supplies session context, not instantaneous AX control values.
- `runtime`: the complete retained safe served-stream ledger, selected immutable entry digests and a named review receipt. Selections associate observations with the reviewed capture context only; they do not authenticate the simulator client. The original ledger remains available, including failed/asset/transport observations and known host probes. No selection is relabeled as an exhaustive load set.
- `observations`: actual literal visible and required labels, bound to the source review. This proposal does not promote native accessibility names or icon metadata into literal printed labels.
- `review`: reviewer name, actual review time/method, exact canonical package digest, specific full-viewport/UI/source/privacy checks and concrete findings. A bare `passed:true` is insufficient. Changes to labels, source, geometry, ledger or runtime review stale the binding.

The screenshot row uses `native_review_package:{file,sha256}`. It must match the package's exact PNG identity, dimensions, captured time and literal labels. The package and every dependent asset must be confined beneath the current public asset root; symlink escapes, unreadable assets, wrong hashes, raw bundle/binary paths and common key-bearing payload patterns fail. The privacy checks cannot detect every possible secret or authenticate pixels: actual source/image privacy review and the repository privacy audit remain necessary.

## Served bytes and execution limits

The native owner's currently retained entry measurements are completed HTTP `multipart/mixed` response streams. They are not proven isolated Hermes payloads or a complete executed-JavaScript graph. The new proposal validates the actual content-type/stage, positive byte count, completion, stream/target/original-receipt hashes and unchanged public ledger entry. It does not invent request UUIDs, decode an unretained payload or call its response hash an executed-script identity.

Every public package explicitly retains these limitations:

- transport client identity is not authenticated;
- loaded/executed identity and the complete lazy-execution graph are unresolved;
- review is not cryptographic pixel authentication;
- no real hardware or GPS success is claimed.

Entry-only served observations may truthfully accompany an actual reviewed app screen. They never become a `complete_loaded_set` claim. This differs from historical V2's unadopted requirement and reflects the parent-confirmed review boundary. A new schema bridge must preserve the original safe ledger and reviewer association scope; it may not invent observation times, control outcomes or execution facts.

## Native points and full-image fit

Native geometry is measured through the native screen/window APIs and retained in a hashed receipt. Both dimensions must satisfy `logical screen points × measured DPR = raw PNG pixels`. This proposal accepts only a complete foreground app viewport covering the measured landscape screen. A portrait screenshot is rejected rather than rotated or cropped.

The new explicit geometry and final normal-UI guard observation bound is **60 seconds**, approved for the same dedicated device and fixed full-screen geometry. Both actual ages are retained in the fit/binding. There must be no intervening rotate, resize, window change or device-switch event in the retained ledger. An older measurement is rejected. Geometry establishes dimensions; actual screenshot/pixel review establishes the visible controls. A stale AX label alone cannot prove control visibility. Historical V2's five-second rule is unchanged.

The selected 14 held native sources have measured 2732×2048 pixels, 1366×1024 logical points and DPR2. Their actual AX-to-simctl gaps are 19.672333–50.249733 seconds. This observation is not a qualification of those packages by this code.

## Reviewed recording-session correspondence

V3 retains the prior-observation option: a real installed-code comparison must precede the image by at most 600 seconds. It also supports an explicitly reviewed recording session lasting at most one hour. For that option, the actual binary comparison and every image must lie inside the original capture manifest's exact first/last bounds. A named context review must bind the same dedicated device, Unit bundle, base source, complete Mach-O inventory, original full normal-UI ledger and retained source/event receipts. Actual binary observations and signed offsets remain unchanged.

The current actual recording session is 22:25:15.340836–22:58:50.814309 UTC on 2026-10-28, lasting 2015.473473 seconds. Its initial binary comparison is really 22:32:38.074934, with a separate fresh 25-file comparison at 23:54:24.360875. Two images precede the initial comparison; those times are not rewritten or replaced by foreground guard times. The named review must occur after the completed session and retained source/event/binary confirmations.

The actual retained event receipt declares XCTest builds 09/10 and test-driver runs 07/08 during the recording session, plus build 11 afterward. These are instrumentation changes. Xcode may have reinstalled the identical Unit target during test startup; no uninterrupted-installation assertion is made. Supported instrumentation events must retain their actual command categories, times, command-receipt hashes and sanitized-log hashes. Unknown or changed product code/source and undeclared product-changing events are rejected. The original full UI ledger is retained, not replaced by a favorable action subset.

The managed-source comparison covers 1480 files with only the previously reviewed Android-only `app.config.ts` removal. Both genuine installed-code comparisons match all 25 product Mach-O files. Historical driver 09/10 source snapshots and test-bundle digests were not retained; they are not reconstructed. The actual latest postcapture build-11 driver source is retained with its honest scope. This is named observed-app/source context review, like the browser model. It is not proof of continuous installation, authenticated execution or a complete lazy-JavaScript graph. The parent explicitly accepted those declared limits; a missing historical driver hash is not relabeled as an available measurement.

The proposed 1920×1080 output reserves 48 pixels for a heading and 120 for captions. The entire raw PNG is fitted in the remaining 1920×912 area. The geometry above yields raw-pixel scale 0.4453125 and output-pixels-per-logical-point 0.890625. The proposal does **not** label the raw-pixel scale as at least 0.75. It requires at least 960×540 native logical UI points, logical scale 0.75–2, and fitted UI area at least 1100×650 output pixels. Those floors do not establish actual text/control legibility; source and encoded-frame review still do that.

## Proposed production changes

`native-public-integration-review.patch` contains only these proposed changes:

| File/function | Proposed behavior |
|---|---|
| `scripts/native_capture_public.py` (new) | Read-only self-contained public source/fit validation and separately authored native frame-review binding validation. |
| `scripts/native_capture_review.py` (new, private stage only) | Actual private Mach-O/plist/source/lock/stream-reference comparisons. Never imported by public rebuilds. |
| `render_walkthrough.validate_inputs` | Branch on genuine native method before the existing browser-only layout check; use DPR-aware full-PNG fit and include all retained public dependencies in render-time hash guards. Browser branch stays otherwise unchanged. |
| `render_walkthrough.render` | Copy native source/geometry/review binding into extracted-frame worksheets, set `native_frame_review:null`, retain explicit Unit primary identity. Never author a passed frame review. |
| `verify_capture_evidence.verify_document` | Validate native source packages without private roots and require a separate actual encoded-native-frame review binding to current frame/master/source/layout/labels/caption. Existing caption/control and playback checks continue. |
| `expansion_site._screenshots` | Accept the verified native provenance branch without requiring a fabricated browser URL. Existing canonical learner-content digest, strict video evidence, privacy and relative-asset export remain in force. |
| `scripts/tests/test_native_public_package.py` (new) | Synthetic offline/private-stage/geometry/identity/privacy/frame/publication guard cases. |

`expansion_site` needs the narrow provenance branch because it currently independently rejects every source that lacks browser provenance before calling the whole video gate. No public readiness API gains native root arguments. There is no change to normal export/build callers or browser playback requirements.

## Running and reviewing the proposal

From the staged Academy root:

```sh
python3 -B -m unittest discover \
  -s sources/production/proposals/native_public_integration_review_v3_20261028/proposed/scripts/tests \
  -p 'test_*.py' -v
python3 sources/production/proposals/native_public_integration_review_v3_20261028/prepare_patch.py --check
```

The final suite has 65 native proposal guards plus 131 copied legacy browser tests (196 total; 194 pass and 2 optional skips). The copied legacy browser tests run against the proposed copies. Two optional real FFmpeg/Pillow legacy fixtures remain skipped unless explicitly enabled; no native video was rendered by these synthetic tests. Guards cover changed/missing/added debug or framework code, JSON-serializable full inventories, stale/wrong-device sessions, changed product source, undeclared build/install events, out-of-bounds comparisons, DPR/dimension tampering, missing stream hashes, body retention, source privacy and source/frame/review/playback bindings.

Before adoption, root must inspect the real native candidate, literal label/control correspondence, private context comparison and self-contained reviewed package. Its bridge from the retained 26 actual PNG/sidecar records must be explicit and preserve actual timestamps, method, geometry, controls, outcomes and runtime limits. No genuine native source is claimed valid merely because a synthetic fixture passes.

## Revision and actual bridge findings

This new version preserves the prior proposal directory and patches. Hashing uses the existing chunked SHA256 pattern, compatible with Python 3.10; it does not use the Python 3.11-only `hashlib.file_digest` API. Private tests cover a changed debug dylib while the launcher/plist stay unchanged, added/missing embedded code and a bound complete public inventory. No Mach-O bytes are retained in the public package.

`actual_bridge_preflight.py` preserves the earlier read-only chronology research. Its prior-600-second findings are historical; they do not describe the newly supported reviewed-session option. It never authored passed reviews or altered actual timestamps.

The separate native-owner addendum now retains the three actual safe CSS bodies, own-device-only creation receipt, two genuine installed-code observations, explicit driver event/source context and fresh managed-source comparison. The immutable 421693… source freeze and original owner/root pixel reviews remain unchanged. No other-device inventory, binary, private key or development-bundle body is copied.

`prepare_actual_drafts.py` defaults to a read-only plan; `--write` creates a new proposal-local directory and refuses to overwrite an existing one. Its retained `actual-drafts/` contains 14 **unreviewed** packages, exact native image/sidecar references, original full ledgers and source snapshots. Every new reviewer/method/time/finding/check is null. In particular, the product-source attestation remains null pending the named context reviewer. Existing source-only reviews retain their actual authors, scope and times; the builder does not manufacture a fresh review from them.

`assess_actual_drafts.py` independently rehashes the public dependency graph, reconstructs all 85 draft files from held original inputs, checks actual geometry, chronology, sidecar and source-review correspondence, and verifies that the ordinary public validator rejects all 14 missing-review packages. This assessment is not a schema-validation bypass or a qualification. It also binds the owner's genuine read-only private comparison report at 2026-10-29 00:18:38.965195 UTC: all 25 installed Mach-O files, plist and 16 source/lock snapshots matched. That report supplies byte comparisons, not pixel approval or historical execution proof.

```sh
python3 sources/production/proposals/native_public_integration_review_v3_20261028/prepare_actual_drafts.py
python3 sources/production/proposals/native_public_integration_review_v3_20261028/assess_actual_drafts.py
```

`actual-drafts.unreviewed-fact-assessment.json` records the exact remaining review requests. The installed context and served metadata each share one factual binding across all 14 packages. The current PNG/literal labels must still be bound individually to the genuine existing source observations. The real reviewer must supply their name, actual review time, method and concrete findings, including the explicit instrumentation/reinstall/historical-driver limits. Any resulting reviewed packages must be new files, with updated dependent hashes and the ordinary strict gate rerun. The drafts remain held, `publishable:false`, and unqualified. Production adoption, narration/media, encoded-frame review and real beginning/middle/end playback are separate later steps.
