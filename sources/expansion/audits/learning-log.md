# Academy production learning log

## 2026-10-28 | Bug Root Cause | A failed layer save can leave a document that breaks the next read
Normal Add Layer on the isolated PostgreSQL stack inserted a document but reported a save failure. The controller checks the Mongo-style `Id.Timestamp` after the PostgreSQL repository sets `PgId`. The subsequent Layers read threw when Dapper tried mapping the whole JSON `data` column to `MapLayerData`. A zero-row list had worked before the exercise. This is source-supported diagnosis, not a completed product fix.
**Files:** `expansion/audits/core-mapping-coverage-20261028.json`, `evidence/expansion/Core/Web/Resgrid.Web/Areas/User/Controllers/MappingController.cs`, `evidence/expansion/Core/Repositories/Resgrid.Repositories.NoSqlRepository/MapLayersDocRepository.cs`
**Resolution:** Backed up and removed only this run's exact failed training insert after checking the isolated database, department, unit count and original active calls. Verified normal Layers loads again. Excluded layer-success claims from narration; the focused POI sequence separately verifies real saved records and main-map results. Resolve and review the product path before rerecording layer success.

## 2026-10-28 | Gotcha | Staged route stops did not establish a saved route
The normal Core form rendered two numbered Chicago waypoint markers with the entered dwell/contact/note fields. Create Route returned the form with Stops 0, and a separate Routes visit still showed an empty list. The exact server validation reason was not established. No saved plan or execution was seeded to replace that missing UI outcome.
**Files:** `captures/expansion/core-planned-routes-20261028/`, `demo/scenarios/planned-route-form-practice.json`
**Resolution:** Preserve the unsaved configuration footage and exact fictional input values, exclude successful save/route/arrival claims, and investigate the normal form path before recording completion.

## 2026-10-28 | Capture Integrity | Accessible labels can exceed the text actually painted in a selector
Core's import mapping selectors contain full Source ID, Belongs to and Longitude options in the DOM while the narrow closed controls clip those strings. A native select popup was not present in the browser screenshot. Collapsed content and underlying modal content can also contain text that is not a readable foreground label.
**Files:** `captures/expansion/core-import-review-20261028/review/reviewed-source-subset-20261028.json`, `captures/expansion/dispatch-workspace-20261028/review/reviewed-source-subset-20261028.json`
**Resolution:** Review the exact saved JPEG, retain only its legible foreground labels in the separate review manifest, and record any clipped/native-only gap. DOM matching alone cannot qualify an option as visibly demonstrated.

## 2026-10-27 | Capture Integrity | Verify entered text before the save action
A Unit note lost characters during accessibility typing. Its incorrect training note was submitted because inspection and submission were batched without checking the read-back. The raw failed take remains excluded. A subsequent ordinary status submission appended a clear correction, entered with the supported fill API and compared exactly with the intended string before Submit; history was preserved.
**Files:** `captures/expansion/unit/036-available-training-note-before-submit.jpg`, `038-available-correction-exact-readback.jpg`, `expansion/audits/unit-access-freeze-20261027.json`
**Resolution:** Keep text entry/read-back verification separate from consequential submission. Use complete-value fill or paste for controlled inputs, inspect the resulting actual value, and stop on any mismatch.

## 2026-10-27 | Capture Integrity | Raw recorder formats differ from reviewed snapshots
Passing a reviewed `{screenshots: [...]}` snapshot to an append recorder caused format errors; the older array recorder wrote an unbound JPEG before failing. Both recorders now reject incompatible manifests before writing image assets, with regression coverage that preserves the original manifest and directory contents. The unbound JPEG was quarantined in ignored diagnostics and all existing review records were preserved.
**Files:** `production/capture_application.mjs`, `production/capture-evidence.mjs`, `scripts/tests/test_capture_manifest_guards.py`
**Resolution:** Start a fresh recording directory. Keep raw array or `{captures: [...]}` manifests separate from hash-bound reviewed snapshots; never convert or append to the latter implicitly.

## 2026-10-27 | Application Finding | Concurrent icon cleanup can orphan the saved key
Three marker form submissions completed within one second. The isolated icon table recorded three inserts and three deletes, leaving the call type pointing at a missing row. The service's independent insert, pointer update and competing-row deletion admit a deterministic interleaving with this result. Exact live SQL ordering was not traced. Closing duplicate forms and performing one ordinary upload restored the image in the reopened form and actual warehouse map.
**Files:** `expansion/audits/core-marker-upload-race-20261027.json`, `core-marker-upload-race.production-fix-recommendation.json`, `core-marker-single-save-recovery-20261027.json`
**Resolution:** Sequential UI recovery repaired only the fictional fixture. A production transaction/serialization fix remains separate; no authentication, route, image response or database workaround was applied for these recordings.

## 2026-10-27 | Fixture Safety | A helper without argument parsing treated --help as a write
The simulated-position helper previously ran its append query whenever executed, including with `--help`. A sandbox-denied Docker connection exposed the issue before any database command ran. The CLI now parses arguments before importing stack management: default/`--plan` are offline, help and invalid options exit without database contact, and only `--write-training-fixes` enters the guarded transaction. Missing latest status records and null coordinates/notes now fail the existing fixture guard as well.
**Files:** `sources/demo/scenarios/refresh_training_positions.py`, `scripts/tests/test_training_positions.py`
**Resolution:** Test harmless CLI paths separately from the explicit mutation path. Preserve current status types and append-only history; simulated fixture positions never establish device GPS or real personnel locations.

## 2026-10-26 | Gotcha | A captured screen subset cannot establish that a control is absent
Numbering scene 04 originally inferred that no year-label selector existed from its selected screenshot/DOM subset. The pinned Core view does render `CallNumberYearLabel` with start/end-year options. Source review caught the unsupported negative before any speech media existed; the script is being revised without changing demonstrated January 1 settings or pretending an unseen control was exercised.
**Files:** `Web/Resgrid.Web/Areas/User/Views/Department/CallSettings.cshtml:129`, `sources/expansion/lessons/core-document-numbering.json`
**Resolution:** Reconcile current source with actual visible controls. Preserve the prior script and record an explicit revision; describe only the observed configuration until additional footage verifies the selector.

## 2026-10-26 | External Service | Successful Descript jobs can contain timed text without speech
Preparing AI narration can produce a plausible composition duration while the project's media-file map is empty. A publish job can also complete with a tiny, nearly empty audio export. Opening the actual editor and completing pending stock speech produced real media and fresh timing for the completed lessons.
**Files:** `scripts/qa_narration.py`, `sources/expansion/audio/`, `sources/expansion/plans/`
**Resolution:** Require actual media, full audio decode, exact-script and per-cue signal checks, then export fresh SRT timing. Preserve rejected exports only in ignored local diagnostics. Signal checks do not establish human listening or pronunciation quality.

## 2026-10-26 | Gotcha | Legacy master timing includes transition pauses
The current hash-pinned location primer MP4 measures 214.97 seconds and its current SRT contains 72 cues ending at 214.729 seconds. An older validation JSON instead reports 218.84 seconds, 73 cues and twelve 0.45-second pauses added to 213.44 seconds of raw audio; it does not describe the current files. Course metadata reports 214.954 seconds. The exact reason for the historical timing discrepancy is unverified. Replacing illustrated scenes must bind the actual current media and caption hashes rather than reuse the older validation or pair final captions with raw narration.
**Files:** `sources/course.json`, `sources/expansion/audits/legacy-*`
**Resolution:** Measure the actual final master and use its real caption timing. Keep unverified scene mappings as proposed captures rather than completed replacements.

## 2026-10-27 | Gotcha | CI-mode Metro can keep serving a pre-edit client bundle
The isolated IC Metro listener reported CI mode and disabled reloads. Editing source files and reloading the browser did not establish that the current compatibility code was served. After verifying the isolated listener and working directory, restarting normal development Metro with --clear produced the rebuilt v3 client; genuine Chicago framing, pointer pan and Save View then survived a full browser reload. Earlier framing failures cannot be attributed to a specific served patch version from the source-file hashes alone.
**Files:** `sources/demo/client-support/ic-camera-ready-20261027-v3/HANDOFF.md`, `sources/demo/client-support/ic-camera-ready-20261027-v3/runtime-validation-20261027.json`
**Resolution:** Treat build/runtime cache provenance separately from source provenance. Rebuild the isolated listener after edits, preserve inherited map credentials, and require actual screen/persistence checks before reporting UI behavior. Annotation tap handling remains unverified and unchanged.
