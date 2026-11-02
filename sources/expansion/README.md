# App and configuration walkthrough production

The generated `site/site-manifest.json` and each canonical lesson's current qualification
establish the ready catalog. As of November 2, 2026, the complete local build has **69
qualified actual-screen videos**, including the introduction and original detailed lessons.
The most recent addition is the final inventory return and balance reconciliation walkthrough. The earlier Calls Summary lesson covers: active and priority counts, display limits,
recent-call visibility, font size, restoration and saved readback. Readiness summaries
and unit timer/acknowledgement/mute lessons are also complete.

All three complete narrations have genuine User listening approvals. Their actual encoded
screen intervals and every caption cue passed review, plus advancing browser playback at
the beginning, middle and end. Recipes, raw captures, complete correspondence, audio,
captions and qualified masters are retained here.

The website's deployment package now serves the unchanged masters through this repository's
GitHub Release assets. The custom hostname remains `academy.resgrid.com`. Local preview
retains self-contained videos. See [Release delivery](../../docs/release-video-delivery.md).

The latest [remaining-work audit](audits/academy-remaining-work-qualified69-20261102.json)
records work still needed across administration and the four apps. The full requested
series is not complete. The following production notes retain historical checkpoints;
their older counts, pending states and broad plans do not override current qualification.
Maintainer status and capture notes stay here rather than appearing on learner pages.

The completed Reporting foundations video contains the full 7:12 natural narration,
27 actual screen intervals and 115 caption cues. It passed the user's listening
review, encoded-frame checks, advancing browser playback at the beginning, middle
and end, and the installed learner-page playback check. Its source and finished
master are in `plans/core-reporting-fundamentals-capture-freeze-20261029/` and
`rendered/core-reporting-fundamentals-take-01/`.

Dispatch map references, Records lifecycle, Billing take 02, IC access/session
settings, Shifts take 02, Responder call context, Training administration and
record-definition administration now have qualified videos in the catalog.
Their complete user listening approvals, full audio checks, encoded-screen reviews
and browser-playback evidence are retained with their individual production takes.

The completed native Unit call-lifecycle video retains 23 unchanged app images,
59 sentence-to-screen mappings, the reviewed 835-word script and 88 speech cues.
Its downloaded narration and actual-screen video passed the user listening,
technical and browser checks. The portable checker
is `../production/check_unit_call_lifecycle_native_archive_20261030.py`; it verifies
the copied archive without requiring earlier host-specific capture folders.

Use the v2 authoring recipes for Dispatch map references, IC settings, Responder
call context, Billing and Shifts. They bind instruction digests using the same
actual SRT parsing as the renderer. Full guarded authors are also available for
Records lifecycle and Training administration. Each requires the genuine listening
review before creating final renderer inputs; no pending narration is marked ready.

Dispatch, IC and a separate Unit Records recording copy now have reproducible
Records contract support under `../demo/client-support/`. Their focused Records
suites pass 73, 77 and 87 tests respectively. The actual UI save/readback retest
remains required for those three copies; the completed Responder save/finalize
retest is separate. Historical continuation audits preserve the state observed at
their recorded time; the current catalog and each lesson's qualified evidence
establish what is complete.

The isolated Responder recording copy has a reproducible, tested Records contract
patch in `../demo/client-support/responder-records-contract-20261030/`. Actual UI
recording established a new server draft and a saved note edit. The completed
`app-responder-record-draft-finalize` lesson now shows saving an existing draft,
fresh readback, attestation, finalization and reopening its read-only result.
Its 3:03 narration has genuine user listening approval; all 54 captions and twelve
encoded screen intervals passed review. Attachment upload remains unverified.
The original application checkout and Core source are unchanged.

The completed `app-ic-tactical-map-lane-link` lesson shows creating a named map,
inspecting its saved expiry, attaching it to Staging and reopening that saved
association. Its 2:56 narration has genuine user listening approval; all fifty
captions and twelve encoded screen intervals passed review. This lesson does not
claim drawing, offline operation or a verified expiry duration. Both new videos
passed advancing browser playback at the beginning, middle and end, plus playback
from their installed Academy learner pages.

The completed Responder shift-schedules source is in
`plans/app-responder-shift-schedules-rosters-source-proposal-20261031/`. It retains
ten reviewed narration paragraphs and fourteen actual screens for Today, search,
day details, My Shifts, calendar filters and role needs, On Duty, Trades and
Approvals. The October 27 practice day is historical. No assignment or trade is
submitted in this lesson. Its complete 5:13 narration passed the user's listening
review. Seventeen encoded screen intervals, all 92 captions and advancing browser
playback at the beginning, middle and end passed review. The additional caption
segment uses Descript's actual stored word boundary at 165.290 seconds; no word
timing was estimated. The qualified master is in
`rendered/app-responder-shift-schedules-rosters-take-01/`.

The separately approved local trade exercise was sent once to fictional Blake
Gallo and cancelled, with saved Open/No reply yet and cancellation readback
captured. The original standby day had ended, so Core's normal calendar UI added
November 1 while preserving all seven earlier selected days. A fresh Responder
reload retained the empty trade queue and restored Request trade with Boden still
on the Scheduled roster. This is not an acceptance, replacement or supervisor
approval. Its actual screens are in
`../captures/expansion/responder-shift-trade-approved-20261101/`, and its retained
results are in `audits/responder-approved-trade-cancellation-20261101.json`.

The separate trade-request/cancellation source is now frozen in
`plans/app-responder-shift-trade-request-cancel-source-proposal-20261101/`:
eleven narration paragraphs, ten reviewed actual screenshots and the complete
727-word script. Chrome's ordinary Descript Play control generated all eleven
speech clips; the exact complete script matches all 84 exported speech cues.
The named private audio export is approved and downloaded. The full 287.207625-second
track and every speech cue pass decoding, exact-script and non-silent audio checks.
One cue now splits at Descript's genuine stored word start, 28.790 seconds, producing
85 caption segments without changing speech or original cue endpoints. Its complete
Root correspondence review covers fifteen actual-screen holds. The user approved
the complete natural narration. All fifteen encoded screen holds, all 85 captions,
the encoded audio and actual advancing beginning/middle/end playback passed review.
The qualified master is in `rendered/app-responder-shift-trade-request-cancel-take-01/`
and is included in the 52-video catalog.

The additional Records analytics source is in
`plans/core-records-analytics-summary-workload-source-proposal-20261101/`.
Its thirteen chapters and eleven reviewed actual screens show Executive summary,
definition/group filters, refreshed readback, restored scope and Workload
breakdowns. The 965-word script distinguishes finalized-record counts from the
recorded administrator's department transition and current-queue measures.
`audits/core-records-analytics-filter-observations-20261101.json` retains the actual
4/2/0-record results and their verified scope. Narration generation and all final
media checks were pending at source freeze. All thirteen speech clips are now
generated, and its complete script matches all 111 exported caption cues. The named
private export is approved and downloaded. Full decoding and all 111 non-silent cue
checks pass for the complete 401.682-second track. Root reviewed all thirteen mapped
screen holds, practices and sector examples. The user approved the complete natural
narration. All thirteen encoded holds, all 111 captions, encoded audio and actual
advancing beginning/middle/end playback passed review. Its qualified master is in
`rendered/core-records-analytics-summary-workload-take-01/` and is in the ready catalog.

`../production/prepare_paragraph_screen_timing_20261101.py` checks the exact source,
image and caption hashes for both new lessons. It maps each complete narration
paragraph to its actual exported cue range without estimating word timing. The
retained `*-actual-cue-proposal-20261101.json` files are proposals, not final media
reviews or qualified renderer inputs.

The fuller correspondence proposals and genuine Root reviews are in each lesson's
`*-complete-correspondence-20261101/` directory. Use
`../production/prepare_trade_analytics_correspondence_20261101.py` to verify them.
`../production/assemble_trade_analytics_take_01_20261101.py` requires an actual User
listening receipt bound to the exact downloaded audio before writing final inputs;
generation confirmation and export permission do not satisfy that review.

Local review previews can be rendered with
`../production/render_local_review_previews_20261101.py trade --render` or the
`analytics` selection, after installing the production dependencies. They use the
verified complete audio and genuine Root correspondence reviews, and write only
to ignored `_reports/review-previews/` folders. These previews contain the actual
screens, full narration and captions for listening/context review. Both passed
complete audio/video decoding and numerical source-pixel checks for every hold;
Root personally inspected all 28 encoded hold frames. They do not create a hearing
approval, final renderer plan or publication qualification. The final pipeline's
genuine-listening and encoded-caption/browser checks remain in place.

The new amendment source is in
`plans/core-records-amendment-and-revisions-source-proposal-20261101/`: fourteen
chapters, thirteen reviewed images and the complete 905-word script. It combines the
earlier actual fictional course-code correction with new read-only captures of the
History comparison/View controls, their actual comparison output and both saved
revisions. The former clipped-launcher gap is resolved by ordinary keyboard focus
in Chrome's normal viewport; the application and record data were not modified.
The actual recheck is retained in
`audits/core-records-revision-control-gap-resolved-20261101.json`. Narration and all
final media checks were pending at source freeze. All fourteen speech clips are
now generated and their complete script exactly matches all 102 exported cues.
The user approved the named private audio export, which is downloaded. The complete
374.816521-second narration and all 102 speech cues pass full decoding, exact-script
and non-silent audio checks. Root reviewed the complete correspondence, fourteen
practice prompts, six sector examples and seventeen actual-screen holds, including
the final paragraph's return to the reason/attestation, saved result and comparison.
The guarded author is `../production/assemble_records_amendment_take_01_20261101.py`.
An unqualified local review preview is available through the `amendment` selection
of `../production/render_local_review_previews_20261101.py`; it passed full decoding
and numerical source comparisons, and Root viewed all seventeen encoded holds.
Genuine listening review and complete final encoded-caption/browser checks remain
required. Source review or speech generation alone does not qualify this video.

The new Responder signup/withdrawal source is in
`plans/app-responder-shift-signup-withdraw-source-proposal-20261101/`. Its seven
chapters and 496-word script cover the actual open day, team confirmation, saved
personal roster entry, withdrawal confirmation and returned empty-day detail.
Root personally reopened all five capture states; the original and returned empty
views have the same image hash, so the freeze records four distinct images rather
than inventing a fifth distinct visual state. The historical October 27 date is
disclosed in the narration. No new roster or notification action was performed.
All seven natural-stock-voice speech files are generated and the complete script
matches all 55 exported caption cues. The named private audio export is awaiting
approval, followed by downloaded audio checks, genuine listening review and final
screen/caption/playback qualification. The source-freeze checker is
`../production/freeze_responder_signup_source_20261101.py`; it defaults to checking
the retained raw inputs and refuses to overwrite existing source files when run
with `--freeze`.

The contact-administration walkthrough retains 22 reviewed application screens,
10 chapters and the complete 338.802-second narration. It shows category creation,
person and organization details, coordinates and addresses, filtering, a phone
update, and saved readback. The original 95 speech cues are preserved; four genuine
one-second transcript markers produce 99 aligned screen/caption segments without
estimated word timing. Its source is in
`plans/core-contacts-administration-capture-freeze-20261028/`, with the recipe in
`../production/author_core_contacts_administration_take_01.py` and the qualified
master in `rendered/core-contacts-administration-take-01/`. The learner text explains
the recorded Category and mailing-address display limitations using the actual
List, View and Edit screens.

The Unit deployment-review walkthrough retains 13 reviewed application screens,
11 chapters, 74 actual speech cues and the complete 263.059-second narration. It
shows an existing deployment, a note-only edit, Save entries, unresolved warnings,
and reopening the saved Draft. It also compares personal and deployment scopes
and reviews the displayed expense, usage and F-42 controls. It does not submit,
sign, approve or claim payment for the report. The frozen source is in
`plans/app-unit-deployment-draft-review-capture-freeze-20261028/`, the recipe is
`../production/author_unit_deployment_draft_review_take_01.py`, and the qualified
master is in `rendered/app-unit-deployment-draft-review-take-01/`.

For both lessons, the user approved the complete natural-voice narration, every
encoded screen interval was reviewed, and three genuine advancing browser checks
verified beginning, middle and end playback. Original captures, raw captions,
technical checks and separate user listening reviews remain retained.

The Dispatch pending-call walkthrough retains 20 reviewed application screens,
8 chapters, 25 screen intervals and the complete 234.405-second narration. It
shows Save pending call, the saved pending record, an explicit one-person
dispatch selection, the active Dispatched result, and closing that exercise
with notifications off. The original 69 speech cues remain intact; two genuine
one-second transcript markers produce 71 caption segments. Its source is in
`plans/app-dispatch-pending-call-to-dispatch-capture-freeze-20261028-v2/`, its
recipe is `../production/author_dispatch_pending_call_take_01.py`, and its qualified
master is in `rendered/app-dispatch-pending-call-to-dispatch-take-01/`. The exercise
does not demonstrate location-based selection or external message delivery.

The Core inventory-movements walkthrough retains 16 reviewed application screens,
12 chapters, 93 speech cues and the complete 337.850-second narration. It reviews
the item and lot, then follows a receipt, transfer, issuance, stored partial return,
ledger and dated stock balances. Its final report chooser establishes where to
choose a report; it does not claim a downloaded PDF. The source is in
`plans/core-inventory-movements-capture-freeze-20261028/`, and the qualified master
is in `rendered/core-inventory-movements-take-01/`. Later return and stock-count
captures are separate exercises with their own current balances.

Both videos retain the user's complete narration review, an actual encoded-frame
review for every static screen interval and caption, and three advancing browser
playback proofs. Training, shifts, certification administration, native Unit stock
counts and final inventory returns have further source work underway; their
preparation files do not make them completed videos.

The Core check-in configuration video has 14 reviewed application screens.
Its corrected narration is retained under `plans/core-checkin-configuration-capture-freeze-20261028-v2/`.
Descript generated the corrected paragraph after the workspace plan was verified.
The approved private export is retained as `audio/core-checkin-configuration.m4a`.
Its full 348.578-second decode and all 97 speech cues passed the signal, script and
caption checks. All 14 actual screen images and the complete cue correspondence
were reviewed; `../production/author_core_checkin_configuration_take_01.py` retains
the hash-bound recipe. The user completed the full listening review. All 14 encoded
screen intervals and beginning/middle/end advancing browser playback passed review.
The finished master and qualification evidence are retained under
`rendered/core-checkin-configuration-take-01/`. The earlier
audio has an incorrect warning explanation and is preserved as superseded material
in `audio/history/`. The new generation transcript is retained as
`audio/core-checkin-configuration-generation-20261028-053409.raw.srt`; it must be
paired with the fresh corrected audio export, never the superseded recording.
See `audits/core-checkin-warning-source-reconciliation-20261028.json` for the source
comparison. The learner page explicitly notes the recorded difference between the
Core countdown and server thresholds; warning/overdue transitions are not demonstrated.

The recorded default and override inputs are retained in
[`checkin-timer-configurations.json`](../demo/scenarios/checkin-timer-configurations.json).
That fixture distinguishes reusable configuration from observed historical call IDs,
timestamps, and check-in results; replay creates its own practice call.

Unit call-response preparation is retained in
`plans/app-unit-response-candidate-20261028/`. It maps 26 reviewed historical
screens to proposed narration and explicitly prohibits speech generation while
entry-action footage is incomplete. A separate fresh exercise,
`../captures/expansion/unit-response-recapture-20261028/`, captures creation,
Set Active, response destinations, notes, saved activity and closure for
FD51-2026-0006. Its review accepts 16 images for the specified visible content
and excludes one image from unit/status identity proof because its header is
scrolled out of view. Do not mix the fresh exercise with historical
FD51-2026-0003 as if they were one incident.

The fresh Unit sequence still needs a readable Activity entry and an actual screenshot
of its native Deselect confirmation. The settled unit readback and explicit
Available / No Destination / note / Submit cleanup are captured separately under
`../captures/expansion/unit-response-final-readback-20261028/`. A fresh sign-in
showed No Active Call while Engine 51 still had On Scene as its saved status;
the separate Available submission completed the software cleanup. Do not teach
call closure or selection clearing as automatically resetting the unit status.
The browser tool observed the real confirmation text but explicitly cannot capture
its pixels; that AX record is supporting text, not video footage. No confirmation
image has been fabricated. The initial `unit-workflow-entry-20261028/` session also
retains a low-contrast blank form, which is excluded from lesson preparation.
Neither candidate is a new published video.

The focused Responder certification lesson retains six reviewed screens and a
414-word frozen script under
`plans/app-responder-certification-renewal-capture-freeze-20261028/`. It shows a saved
education entry, a renewal date, and the resulting Awaiting verification state.
The connector's initial text-only attempt produced no audio assets, and its
estimated timing remains rejected. The ordinary editor generation step has now
produced six real audio assets and a 185.12-second composition. The fresh 49-cue
speech transcript is retained under `audio/`. The user explicitly approved its
private audio export, and the full 185.133-second download passed decode, signal,
script and caption checks for all 49 cues. The six original source images and
their complete cue correspondence passed review; the hash-bound recipe is
`../production/author_responder_certification_renewal_take_01.py`. The user completed
the full natural-voice listening review. The six encoded screen intervals and
advancing beginning/middle/end browser playback also passed review. The finished
1080p video, chapters, captions and qualification evidence are retained under
`rendered/app-responder-certification-renewal-take-01/`. No new-record save,
photo attachment or department approval is inferred, and the broader readiness
lesson remains unfinished.
The [manual replay fixture](../demo/scenarios/responder-certification-renewal.json)
retains the exact fictional inputs and distinguishes historical results from a
fresh seed's relative dates. Replay checks existing entries before adding hours
and leaves department verification to the normal review procedure.

The focused Dispatch console lesson retains 19 reviewed application screens and
a 967-word script under
`plans/app-dispatch-console-status-and-staffing-capture-freeze-20261028/`.
It covers call context versus panel searches, Available only, selecting the correct
unit, status and destination choices, submitting a practice unit update, reading
back the saved note, and separately submitting and verifying personnel staffing.
`../production/prepare_dispatch_console_status_and_staffing.py` retains its
reproducible source freeze. The user completed ordinary editor speech generation,
approved the private audio export, and approved the full 6:48 listening review.
The full download and all 118 actual caption cues passed technical checks; the
earlier 386.8-second text estimate remains rejected. The reviewed video has 22
screen intervals, showing Clear Filter and the resource cards before their result
views. All encoded intervals and advancing beginning/middle/end browser playback
passed review. The master, captions, chapters and qualification evidence are in
`rendered/app-dispatch-console-status-and-staffing-take-01/`, with the hash-bound
recipe in `../production/author_dispatch_console_status_and_staffing_take_01.py`.
The existing broader Dispatch lessons are preserved.

The focused Core mapping source retains 16 reviewed screens and an 870-word script
under `plans/core-mapping-points-and-filters-capture-freeze-20261028-v2/`. It shows the
actual text/category/label controls, a saved destination category and point,
List/Edit readback, the operating-map marker and popup, and a hide/restore result.
Its 26 original captures remain unchanged under
`../captures/expansion/core-mapping-20261028/`; the reviewed subset is separate.
The [manual replay fixture](../demo/scenarios/mapping-points-and-filters.json)
preserves the fictional values and checks existing names before creating records.
The separate layer attempt failed in the local PostgreSQL save/read path; only its
exact failed insert was backed up and removed to restore the map. That failure is
documented in `audits/core-mapping-coverage-20261028.json` and is excluded from
successful setup narration. The approved private audio export passed full decode
and all 99 speech-cue checks, and the user approved the full 5:47 listening review.
The finished video has 20 reviewed screen intervals: Manage POIs is shown before
the category list, and the saved List and Edit views appear when discussed. The
hash-bound recipe is `../production/author_core_mapping_points_and_filters_take_01.py`;
the supplemental control review preserves the original manifest and all JPEGs.
Practice tasks and six-sector examples are retained separately in
`plans/core-mapping-points-and-filters-learner-text-20261028.json`, without changing
the spoken script. All encoded intervals and advancing beginning/middle/end
browser playback passed. The finished master and qualification evidence are in
`rendered/core-mapping-points-and-filters-take-01/`. The broader mapping lesson
still has additional coverage work.

Three additional reviewed source batches are retained with their original JPEGs,
DOM observations and separate review scopes:

- `../captures/expansion/dispatch-workspace-20261028/`: 22 screens covering call
  filters, actual unit status submission and saved note readback, and separate
  personnel staffing submission/readback. The
  [Dispatch replay fixture](../demo/scenarios/dispatch-console-status-and-staffing.json)
  preserves the exact fictional notes and unchanged crew/call requirements.
- `../captures/expansion/core-planned-routes-20261028/`: 14 screens covering actual
  route settings, explicit endpoints and two staged map-picked stops. The normal
  Create Route attempt returned the form and the list remained empty. The
  [form-practice fixture](../demo/scenarios/planned-route-form-practice.json)
  records that incomplete result; no saved route or execution is claimed.
- `../captures/expansion/core-import-review-20261028/`: 18 read-only screens covering
  the existing additive workspace, glossary/import limits, templates, mappings,
  issues, unaccepted settings, preview, approval boundary, history and zero-person
  activation state. The import remains unapplied as requested. Clipped selector
  labels and the blank preview diagram are explicitly excluded from exact-label
  or diagram teaching.

These batches are reviewed production sources, not new finished videos. Their
`review/` manifests deliberately keep lesson eligibility and publication pending.

## Editable inputs

| Material | Location |
| --- | --- |
| Narration, lesson text, audience, prerequisites, practice and sector examples | `lessons/<lesson-id>.json` |
| Raw Descript audio, raw timing, corrected captions and signal checks | `audio/` |
| Explicit screen/cue timing and immutable capture snapshots | `plans/` |
| Finished takes, frames, caption files, posters and review evidence | `rendered/` |
| Original browser screenshots, observations and provenance | `../captures/expansion/` |
| Cited app/Core source files and hashes | `../evidence/expansion/` |
| Source limitations and exact remaining app capture operations | `audits/` |

Use the [expansion stack and app reproduction guide](../demo/README.expansion.md)
to prepare isolated pinned checkouts. The
[public scenario fixture and guarded UI replay](../demo/scenarios/README.core-configuration.md)
retain the demonstrated card/package graph, disabled workflow definitions, turnout
and one-seat crew assignment. Credentials are generated locally under ignored
`private/`; they are not part of the public fixture. Existing historical results
are observations of real UI operations, not seed records that claim execution.

## Updating a lesson

1. Edit its JSON source and confirm the actual current application controls.
   Every setting or operation described must have corresponding readable screens.
   Record native-only and provider-dependent limits explicitly. Keep examples useful
   to community care, mental health, SAR, security, wildland and industrial teams.
2. Capture the real isolated application using `../production/capture-evidence.mjs`.
   Review the raw images, clipping, literal labels, icon controls and state continuity.
   An illustration or an inaccessible control cannot substitute for the real page.
   Use a fresh directory for a new recording session. `capture-evidence.mjs` records
   a raw array manifest; `capture_application.mjs` records an object with `captures`.
   A reviewed object with `screenshots` is an immutable snapshot, not an append target.
   Both recorders reject incompatible folders before writing new image assets.
3. Freeze the narration and source hashes. Generate whole-paragraph speech with the
   established natural narrator in Descript, then wait for actual audio media to exist.
   Export fresh audio and SRT after generation finishes. Timed text alone is not audio;
   a publish job reporting success is not proof that its export contains speech.
4. Run the complete audio decode, exact-script and per-cue signal checks. Listen to
   assess intelligibility and pronunciation; signal energy alone cannot establish them.
5. Build an explicit timed plan with corresponding screenshots for each spoken cue.
   Keep raw timing and prior takes. Render into a new take directory, then inspect
   every extracted interval/caption frame against its source image.
6. Play the final unchanged file in a browser at its beginning, middle and end.
   Record advancing media time, loaded state, visible matching captions and errors.
   Merge only actual observations into the reviewed evidence. New media bytes require
   new playback proof.
7. Set `export_ready: true` only after the complete evidence gate passes, with
   `publication_mode: "video"`, the reviewed `evidence_file` and current authoring
   digest. The exporter checks these again; changing lesson text invalidates review.

Commands below run from the Academy repository root. FFmpeg and Pillow are needed
for rendering; the regular website build does not need them.

```sh
python3 scripts/qa_narration.py --help
python3 scripts/render_walkthrough.py --help
python3 scripts/verify_capture_evidence.py --help

python3 scripts/verify_capture_evidence.py \
  sources/expansion/rendered/core-workflows-take-01/evidence.reviewed.json \
  --asset-root sources

python3 -m unittest discover -s scripts/tests -v
python3 scripts/build.py
python3 scripts/audit_public_repo.py
python3 scripts/serve.py
```

`scripts/build.py` copies reviewed media rather than generating or revoicing videos.
New walkthrough players use burned captions by default and offer optional native
closed captions plus a VTT download. The public pages contain relative asset links,
so repository subpaths and the custom domain work with the same export.

## Current external steps

The operator's file-URL permission update and normal Unit sign-in were verified.
Unit access, apparatus selection, read-only security, empty Login Info and canceled
Logout are now captured; its first lesson has passed source, narration, screen,
caption and actual browser-playback review. Engine 51 was restored to Available through the
ordinary app flow, preserving Christopher Herrmann's existing configured seat.

Three simultaneous marker saves left a stored key without its image row. One
ordinary upload after duplicate forms were closed restored the saved custom icon in
the editor and actual department map. This recovered the fictional fixture; it did
not fix the separate concurrency defect. See the hash-bound diagnosis and recovery
observations under `audits/`.

The operator completed **Dispatch** sign-in after its extension popup was dismissed;
operational Dispatch recording has resumed. The existing capture plan still requires
its conditional run-card and nearest-resource observations before narration freezes.
No filled credential form is accepted as footage, and a later extension block must
be handed back rather than bypassed through another browser or hidden endpoint.

Onboarding import apply remains intentionally deferred by the operator. No import,
MFA enrollment or approval has been performed. An empty export or blocked page is
never accepted as completed footage. Private project links and signed downloads
belong only in ignored local metadata. The full audio, caption, screen and playback
evidence for completed lessons remains local and reproducible without those links.
