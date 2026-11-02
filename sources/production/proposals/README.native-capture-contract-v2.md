# Native capture contract v2 proposal

This is an independent proposal. It is not imported by the Academy evidence validator, renderer, exporter, catalog or build. Every result retains `proposal_only: true`, `publishable: false` and `pixel_authenticity_proven: false`. No real native capture has been validated by this proposal. The native owner's landscape startup PNG remains diagnostic because it shows an application error.

V1 remains unchanged. V2 retains its dedicated simulator, normal UI ledger, explicit-device `simctl` PNG command, raw PNG/hash/CRC/dimensions, foreground observation, Mach-O/Info.plist, source/module/package/Pod-lock identity, literal label and actual review bindings. It adds an explicit base source revision, installed SDK identity, streamed runtime measurements and native point geometry. Only the declared `development_metro` build branch is proposed; release/embedded or unknown builds fail.

## Runtime bytes without retaining the bundle

`stream_hash(chunks)` incrementally measures caller-supplied byte chunks. It performs no network request or file write and returns only SHA256, byte count, completion and nonretention metadata. Empty, interrupted, nonbyte or oversized streams do not return a successful measurement. It does not collect URLs, queries, headers, bundle bodies or bundle paths, and never establishes that an app loaded or executed the bytes.

Each hash-bound `build.runtime_js.stream_receipts` JSON records a completed decoded-response-body stream, its actual JavaScript-source or Hermes-bytecode format, response status, times, request UUID, target digest and bounded resource category. Session/device fields identify the intended observation scope. `transport_client_identity: not_authenticated_by_transport` and `executed_or_loaded_identity_proven: false` are mandatory. They must not be promoted to execution proof by matching a filename or merely observing a successful HTTP response. No retained bundle file is required or accepted in this branch.

The separate `load_observation` receipt must describe an actual native/runtime and Metro review of the complete observed entry/chunk set for the dedicated app, current binary/source identity and capture window. Every observed request ID must have a measured receipt. Lazy entry-only coverage fails, even if someone changes the metadata review digest. Actual current binary/source/module/load correspondence review remains mandatory. This is deliberately a bounded observed-load-set claim, not a claim that all possible application code or future chunks were executed. Metadata assertions cannot authenticate execution or detect dishonest reviewers.

The native owner's current relay receipts are truthful response measurements, not automatically this proposal's complete load observation. Any future schema bridge must retain their original nonauthentication/nonexecution limits and exact hashes. The proposal requests no relay, application, permission, authentication or runtime changes.

## Native points, DPR and landscape fit

`capture.display` records actual native orientation, DPR, full screen dimensions in logical points, the app window rectangle in points, method/time and a hashed native geometry receipt. Both axes must satisfy `screen_points × DPR = unchanged PNG pixels`; the app viewport must be inside the full screen. A browser DPR, guessed device-catalog dimensions or an unknown orientation cannot substitute for that measurement. A valid portrait trace may remain truthful, but the landscape fit rejects it rather than rotating or inventing a capture.

`propose_landscape_fit(document, roots)` first checks traceability and returns a geometry recipe only. It never modifies the PNG, creates a rendered frame or approves pixels. The proposed canvas is 1920×1080 with a 48px heading and 120px caption band. The complete PNG fits in the remaining rectangle without cropping or overlays.

The two scales have different units:

- `raw_pixel_scale` is output pixels per source PNG pixel.
- `output_pixels_per_logical_point` is `raw_pixel_scale × measured DPR`.

For a **synthetic geometry example** of 2732×2048 pixels, 1366×1024 logical points and DPR2, a full fit uses raw-pixel scale 0.4453125 and logical-point scale 0.890625. The proposal does not pretend that the raw-pixel scale is at least 0.75. It requires an app viewport of at least 960×540 logical points, logical-point scale between 0.75 and 2, and a fitted app area at least 1100×650 output pixels. These floors only screen out clearly unsuitable geometry. Actual text/control legibility still requires source and rendered-frame review.

The fit recipe binds the exact unchanged raw PNG, complete native metadata, pixel review, geometry receipt, build/source identity and literal/required label digests. A future rendered-frame record must additionally bind the exact recipe digest, real video and extracted-frame hashes, captions, literal control observations and actual full-frame review. No such frame is created or approved here. Existing full narration/listening, exact cue/control mapping, raw-source, rendered-frame and advancing beginning/middle/end playback gates remain separate and unchanged.

## API and checks

```text
validate(document, roots, now=None)
propose_landscape_fit(document, roots, now=None)
stream_hash(byte_chunks)
review_digest(document)
build_digest(build)
source_identity_digest(build)
```

The four explicit read roots are `assets`, `app`, `source` and `dependencies`. Installed binary/source/module roots must remain outside screenshot assets. The tests contain complete **synthetic parser fixtures**, never genuine app evidence.

```text
python -B -m unittest discover -s sources/production/proposals/tests -p 'test_native_capture_contract_v*.py' -v

python sources/production/proposals/native_capture_contract_v2.py capture.json \
  --assets RAW_PNG_AND_NONSECRET_RECEIPTS --app INSTALLED_APP \
  --source EXACT_MANAGED_SOURCE --dependencies MODULE_SOURCE --propose-fit
```

Adoption requires root review of the proposal and a genuine error-free native sample with real geometry, source/build/load identity and ordinary UI/pixel review. This document authorizes no integration or publication.
