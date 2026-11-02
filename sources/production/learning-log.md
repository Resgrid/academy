# Academy production learning log

Production observations live beside the editable Academy sources so another
maintainer can reuse them without the original chat or a private editor link.

## 2026-10-29 | External Service | Fresh stock-voice text generated speech when regeneration did not

The Billing composition retained ten speech files after its final paragraph hit
the credit limit. Once credits were available, stock-voice regeneration returned
“Cannot regenerate for stock voices”; replacing identical paragraph text did not
materialize the missing speech. A new audio composition containing the complete
unchanged script generated eleven new WAV assets while preserving the old take.
Fresh Dispatch, IC and Records compositions also generated their complete sets.

The later Shifts retry also materialized the twelve pending paragraphs in its
earlier composition while generating the new twelve-paragraph take. Both exported
texts still matched the frozen script, but the old estimated duration changed to
an actual speech duration. Retain before/after inventories and identify the chosen
composition explicitly; preserving its text does not imply an unchanged media
inventory when a shared speaker finishes generating speech in the background.

**Files:** `expansion/plans/core-customer-billing-review-descript-take-02-20261029/`,
`expansion/plans/app-ic-access-session-settings-narration-brief-20261029/`.

**Resolution:** A bounded fresh whole-script take was a working alternative in
this account. Keep the prior take, use the exact approved paragraphs and requested
stock voice, and inspect the actual result. This observation does not imply that
generation will work without credits or that publishing is authorized.

## 2026-10-29 | External Service | Editor-agent summaries did not establish audio completeness

Agent Underlord repeatedly described scratch text or an empty media-library
query even when the official `get_project` response listed generated WAV files.
It also reported estimated durations that differed from the actual composition.
The complete Billing take has eleven new files and a 349.12-second composition;
the Records take has twelve files and a 392.96-second composition.

**Files:** `expansion/audio/*-generated-20261029.txt`,
`expansion/audio/*-generated-20261029.raw.srt`, `scripts/qa_narration.py`.

**Resolution:** Compare the actual composition and generated-asset inventory with
the prior inventory, then compare the entire exported transcript and every SRT
cue with the frozen script. Asset presence and script correspondence precede
approved audio export, full decoding, cue-energy checks and listening review;
they do not replace those checks. Keep editor and signed download URLs private.

## 2026-10-29 | Gotcha | Initial capture themes could hide otherwise present labels

The recovered IC and Responder browser copies initially had low-contrast labels.
Ordinary app preferences restored readable views: IC briefly selected Light and
then restored System; Responder selected Dark from System. No application source,
page CSS, security setting or device permission changed during those actions.
The original poor-contrast captures remain diagnostic history and were excluded
from the reviewed lesson subsets.

**Files:** `expansion/plans/app-ic-access-session-settings-capture-freeze-20261029/`,
`captures/expansion/responder-calls-readonly-20261029-235/action-ledger.json`.

**Resolution:** Record the actual preference choice and review fresh screenshot
pixels. A label in the accessibility tree alone did not establish that learners
could read it. This was observed in the recorded development copies, rather than
established as a general production-app defect.

## 2026-10-30 | Gotcha | Historical review timestamps need a genuine current review

The Training administration source contained review timestamps without a time
zone. Strict final-input validation rejected that manifest. The original source
and failed input checkpoint were preserved. A new personal review of all 21
original images produced a separate manifest with actual timezone-aware review
times; the approved narration and caption words stayed unchanged.

**Resolution:** Preserve the historical evidence and perform the missing review.
Do not add a guessed time zone or weaken the validator to make old evidence pass.

## 2026-10-30 | External Service | Timed script text can exist without generated speech

The new onboarding import composition reported approximately seven minutes of
timed text, while the official project inventory contained zero media files.
The complete 13-paragraph script remained available for generation in the editor.
No audio export or complete-listening claim was made from the estimated duration.

**Resolution:** Check actual generated speech assets before requesting an export.
Keep technical decoding, exact script correspondence, actual listening and final
video playback as separate observations. A successful text-edit job does not
establish that speech generation completed.

## 2026-10-30 | Integration | Verify authoring from the installed repository

The native Unit author passed in the capture workspace but failed in Academy:
the copy filter had omitted two historical Call Details source snapshots bound
to the reviewed native images. All other 239 files in the minimal author graph
were present with matching hashes. An exact two-file allowlist restored the
original snapshots without changing the validator, source packages or reviews.

**Resolution:** Run the actual author from the destination repository. The
installed author and a relocated 241-file copy now pass. The relocation guard
also rejects either missing snapshot and an altered snapshot. Preserve both
historical source identities; copying a current app file into their place would
break the recorded evidence.

## 2026-10-30 | Demo operations | Own the training-account sign-ins

The Academy training accounts were created by the recording agent. The user did
not have those credentials. The existing ignored local training credential file
was sufficient to complete normal Core, Dispatch, Responder, Unit and IC sign-ins.
Credential values were kept out of tool output, public source and screenshots;
the temporary in-memory password binding was cleared after the sign-ins.

**Resolution:** Recover and use agent-created demo credentials through normal
authentication before asking the user to sign in. Preserve required MFA and
context checks. A user-managed production account is a different case.

## 2026-10-30 | CI portability | Exercise the installed standalone repository

The complete tests passed in the recording workspace but ten production-test
errors appeared in Academy. Historical tests located cited Core files through
parent-directory assumptions and genuine playback observations under an ignored
reports directory. Separate exact historical fixtures now retain all 63 cited
source-file entries and both original proof JSON files. Only the tests select
those portable locations; production authors, expected hashes and strict
validators remain unchanged.

**Resolution:** Run the workflow from the actual destination repository. Its
404 script tests pass with two existing skips, all 230 production tests pass,
and the complete 43-video site build validates 80 HTML pages with zero issues.
Historical test states are isolated so legitimate later catalog additions do
not make a read-only or new-only guard test depend on an absent real output.

## 2026-10-30 | App behavior | Responder Quick Entry supports direct finalization

The existing fictional community-software Quick Entry draft D-0C0X8 accepted a
normal Save, and the changed notes persisted across a fresh document navigation.
Submit for review was visible but Core rejected Draft to ReadyForReview for
this definition. Normal attestation and Finalize then succeeded, assigned
TRNADM-2026-0002 and disabled the editable fields. The failed submission is
retained as an excluded diagnostic, not successful-operation evidence.

A direct cold detail URL temporarily displayed the stored definition slug;
returning through the normal Records list restored its friendly heading.

**Resolution:** Demonstrate the actual configured lifecycle. A visible action
is not evidence that a definition permits its transition. Preserve the saved
result and read it back; do not imply that every form needs a review step.


## 2026-10-30 | IC map references and deferred operations

Normal IC UI created a named tactical map, attached it to the Staging lane and retained the selection after a fresh document load. The prepared expiry and saved card displayed different clock times. Retain both views and explain the discrepancy without claiming an unverified expiry duration.

The web recording adapter exposes no MapView onPress prop, while the incident-map screen passes one; two ordinary map clicks left the drawing point count at zero. The offered System Run record opened without schema fields. Neither operation is represented as successful learner evidence; source snapshots and diagnostics remain available for a later application fix. No recording-app or backend patch was applied.

## 2026-10-30 | Descript speech assets can finish after the edit job

The IC narration edit job stopped while the project inventory contained five of eight speech files. A later ordinary project read showed all eight, and re-exporting SRT replaced the last paragraph’s estimated endpoints with generated speech timings. Check actual media inventory and fresh exported captions before asking for an audio export. An edit-job completion or estimated composition duration alone does not establish complete generated speech.
