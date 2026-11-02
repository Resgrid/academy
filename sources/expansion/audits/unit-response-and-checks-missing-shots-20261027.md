# Unit02 actual-screen capture gaps

**Not frozen or ready.** This offline snapshot covers the original40 Unit captures and all21 held response captures. The separate reviewed response subset accepts19 and excludes2. Eight of36 planned groups now have bounded read-only evidence;28 groups still need operations/screens. Parent’s newer action folder is outside this snapshot.

Canonical Unit02 and ready Unit01/location lessons/media remain unchanged. No browser, DB/API request, voice generation or app-source mutation was performed by this audit.

Current recorded baseline001 shows Engine51 Released,1of1 Roles,NoActiveCall after parent’s ordinary Truck81→Engine51 selection. The earlier51009 response and Available cleanup are valid historical evidence;51009 is closed.

## Critical source findings

- Selecting the current unit exits early and closes the sheet; it does not call setActiveUnit/getUnitStatus. Calls focus/RefreshControl fetches calls/priorities, not the active-unit status. The same-unit selection does not refresh status. Parent subsequently used ordinary Truck81→Engine51 selection and fresh001 now shows Released; older Available remains historical.
- 51009/FD51-2026-0001 is now closed by the actual Responder workflow.020–025 remain valid historical Unit response evidence, with their original hashes/capture times. Do not query it as a current active call, reopen it, fabricate a matching result, or use another app’s close/check-in as Unit action proof.
- Rendered Files modal offers read/download/share; it has no file upload form despite unused translated add/upload strings. Images has its own actual picker/upload path. The unfrozen scene09 wording must change before voice; retain file-viewing coverage and an honest native/web limitation.
- 015/040 show a disabled Save because pendingAssignments is empty. No actual Unit crew Save or reassignment has been captured. Current only seat is Officer / Team Lead, not Driver. Narration/practice cannot claim a relief replacement from a preserved readonly crew shot.

## Reviewed response subset

`captures/expansion/unit-response-20261027/reviewed-unit-response-subset.json` binds each endorsed JPEG/DOM hash and narrow actual visible labels.015 is excluded because its Site Info explanation is clipped;017 supplies the complete empty state.021 is excluded as a failed full-screen map operation, despite its Chicago address. Raw images/DOM/manifest are unchanged.

010 selected Dispatched and008 Note iframe text received narrow image/DOM-backed literal corrections; no global recorder, privacy or gate rule changed. Modal background observations are excluded from014/018/019/020 endorsed labels.019 Close and003/004 Clear search use actual reviewed DOM control names.

## Read-only context refresh

1. Keep the currently authenticated Unit tab and close only app sheets normally; no browser reload, sign-out or credential entry is needed for this plan.
2. Calls →Clear search and ordinary navigation/refocus refreshes calls; if a pull-to-refresh control is actually supported on that browser, use it once. Sidebar Call-selection sheet also fetchesCalls(true) on open and has a real Retry only on failure. Neither path guarantees active-unit status refresh.
3. Settings →Active Unit: record Current Unit Engine51. Selecting the same Engine only closes the chooser; do not call that a refresh.
4. When parent authorizes a read-only selection-context refresh, choose another already accessible unit, wait for its actual loaded identity, reopen Active Unit and select Engine51. setActiveUnit reads UnitStatus/GetUnitStatus. Do not submit a status or role assignment on either unit.
5. Reopen1of1 Roles to refetch actual Engine51 assignments; capture Herrmann and fresh final header. If either read fails or permission dialog appears, stop and retain the blocker; do not force session/storage state.

Parent has now performed the selection-only refresh and001 is qualified in the separate reviewed subset; no status/crew save occurred.

## Per-scene actions and evidence

### 01-find-the-correct-call — Find the correct call

Prior evidence: 018-number-search-no-match; 024-engine51-response-saved; 025-engine51-response-header.
New read-only evidence: 002-active-calls-list; 003-search-by-internal-id; 004-search-by-incident-nature; 005-search-cleared-original-calls.

- **U02-S01-A — captured_and_qualified_for_bounded_readonly_scope** Calls → Clear search; wait until the actual wider list renders. Capture the field empty and original active calls with legible identifying details. Proof required: Unfiltered list after the actual Clear search action; do not use the blank transitional019 image.
- **U02-S01-B — captured_and_qualified_for_bounded_readonly_scope** For a fresh exercise, enter its returned internal ID or a distinctive Nature fragment. Capture the rendered match, then clear it. Proof required: Actual returned call number/title/address and matching query; no assumed counter or display-number/name filtering.
  Scope of existing proof: Internal51003 and Nature search are genuinely shown on original existingDEMO-0003. A later fresh call need not masquerade as51009; unfrozen narration still needs the correct historical/current example wording.
- Before freeze: Replace present-tense “51009 finds the disposable training call” with explicitly historical wording if using024/025, or use the real returned ID of a fresh exercise.51009 is now closed and normally absent from active calls.

### 02-read-the-incident-before-responding — Read the incident before responding

Prior evidence: 020-practice-call-info.
New read-only evidence: 006-incident-details-info; 007-incident-contact-empty-fields; 008-incident-info-complete-fields; 009-incident-protocols-empty; 010-dispatched-personnel-and-units; 011-incident-activity-inferred-training-rows.

- **U02-S02-A — captured_and_qualified_for_bounded_readonly_scope** Open an authorized existing incident → Info; scroll below Priority. Proof required: Nature, Type, Address, Note, Timestamp and any actual Destination shown in readable viewport(s), with selected call identity.
  Scope of existing proof: Complete current Info shown; this call has no offered Destination. Populated destination/map routing remains an independent gap under03/07.
- **U02-S02-B — captured_and_qualified_for_bounded_readonly_scope** Select Contact, then Protocols; capture each actual body. Proof required: Contact Name/Contact Info and linked IDs, then actual protocol text or “No protocols attached to this call”. Protocol bodies render inline; no invented separate Open action.
  Scope of existing proof: Contact fields and protocols are genuinely loaded empty; no attached protocol contents/open success demonstrated.
- **U02-S02-C — captured_and_qualified_for_bounded_readonly_scope** Select Dispatched, then Activity; scroll actual contents. Proof required: Actual dispatched resource rows and actual status/event/note/time rows, or honest loaded empty states. A tab title alone is insufficient.
  Scope of existing proof: Dispatched nine rows are separate from seated crew. Activity rows are INFERRED simulated personnel positions; do not narrate direct Unit response/physical GPS from them.

### 03-set-the-active-incident-and-check-routing — Set the active incident and check routing

Prior evidence: 020-practice-call-info; 021-set-active-status-selection.
New read-only evidence: none.

- **U02-S03-A — attempted_actual_operation_failed; still_missing_correct_fullscreen_map** On Call Details, activate the actual map-preview control; capture the full-screen incident map and normal close. Proof required: Readable actual cartography/incident marker/address; real DOM semantics of “View on map” if present. Do not invent literal text or mark a text-containing map as icon-only.
- **U02-S03-B — not_captured_for_this_Unit_operation** When an actual destination POI exists, select the destination map target and compare it with Call Location. Inspect the offered destination-route control without opening an external map service. Proof required: Real call-versus-destination toggles/markers/address and the offered Route / destination-route controls.
- Before freeze: Keep explicit unexercised external Route/provider limitation. “Unit has its own web map and HTML implementations” is implementation detail: replace with learner-facing browser/native scope before voice.

### 04-update-unit-status-with-a-destination — Update unit status with a destination

Prior evidence: 016-available-destination-options; 017-status-note-before-submit; 021-set-active-status-selection; 022-responding-own-call-destination; 023-responding-note-submit; 024-engine51-response-saved; 025-engine51-response-header; 035-available-no-destination-step; 038-available-correction-exact-readback; 039-engine51-available-header-crew.
New read-only evidence: 001-refreshed-engine-context.

- **U02-S04-A — captured_and_qualified_for_bounded_readonly_scope** First refresh the selected-unit context through the safe read-only sequence below and capture the actual Engine51 header/status. Proof required: Fresh actual sidebar state compared with current Core report; historical039 Available must not represent today’s parent-reported Released.
- **U02-S04-B — not_captured_for_this_Unit_operation** If retaining the spoken Hold-to-submit branch, capture a genuinely enabled, coordinator-approved hold-mode configuration/control and deliberate hold submission. Otherwise leave that branch explicitly unresolved. Proof required: Actual configured hold control and result, not an ordinary Submit image relabeled Hold.
- **U02-S04-C — not_captured_for_this_Unit_operation** If demonstrating queue/replay, use an explicitly approved bounded connectivity exercise and capture queued, later sent, and final server-backed state. Proof required: Genuine queued message plus later synchronization; existing sent captures prove neither offline queuing nor replay.
- Before freeze: A sent software status proves a saved status, not physical mobilization or provider delivery. Statuses requiring a live GPS fix remain outside this no-device-permission exercise.

### 05-keep-the-seated-crew-accurate — Keep the seated crew accurate

Prior evidence: 015-engine51-herrmann-preserved; 040-engine51-herrmann-assignment-preserved.
New read-only evidence: none.

- **U02-S05-A — not_captured_for_this_Unit_operation** Open 1 of1 Roles →Unit Role Assignments→Officer / Team Lead; capture the real picker, current choice and offered name/group search. Proof required: Actual “Assign: Officer / Team Lead”, member choices and any real assignment/qualification information; no implied Driver role.
- **U02-S05-B — not_captured_for_this_Unit_operation** Use one of the bounded crew Save options below only when parent authorizes that exact operation. Capture pending choice, enabled Save, real result, and fresh reopen. Proof required: Actual Save result and reopened server-backed assignment, with all unit seats visible. Disabled Save040 does not qualify as mutation proof.
- **U02-S05-C — not_captured_for_this_Unit_operation** If a different relief member was actually saved, immediately restore Christopher Herrmann to the same single seat via the same UI, Save and reopen. Proof required: Restored Herrmann1/1 plus unchanged other unit assignments; no personal status/staffing/qualification changes.
- Before freeze: The practice “replace a relief driver” conflicts with the actual single Officer / Team Lead seat. Correct role wording before freeze. The narration currently instructs choosing people and saving an updated assignment; a read-only disabled Save shot does not cover it.

### 06-create-a-call-with-the-permitted-fields — Create a call with the permitted fields

Prior evidence: none.
New read-only evidence: none.

- **U02-S06-A — not_captured_for_this_Unit_operation** Calls → actual plus FAB → Create New Call; wait for loaded policy. Open Priority and Type choices. Proof required: Real Create New Call, Name, Nature, Priority, Type and actual options/required indicators. The plus FAB has no source-provided “New Call” accessible name; do not fabricate metadata.
- **U02-S06-B — not_captured_for_this_Unit_operation** Before creation, submit one safe intentionally incomplete exercise draft; correct the actual visible validation error. Proof required: Real missing-field message and corrected required field. No duplicate saved call.
- Before freeze: Describe the actual plus control and resulting Create New Call screen, rather than inventing a painted New Call button. Loaded field policy controls optional/required/scheduling behavior.

### 07-resolve-the-call-location-and-destination — Resolve the call location and destination

Prior evidence: none.
New read-only evidence: none.

- **U02-S07-A — not_captured_for_this_Unit_operation** On the unsaved Create New Call form, show permitted Address / GPS Coordinates / what3words / Plus Code inputs and the separate destination selector. Proof required: Actually visible offered input modes, entered clearly simulated coordinates and available/empty destination choices. No provider lookup success implied.
- **U02-S07-B — not_captured_for_this_Unit_operation** Select Location on Map; inspect the supplied simulated point on real cartography; confirm only through actual offered controls. Proof required: Actual map picker/control, real rendered point and returned form coordinates.
- **U02-S07-C — not_captured_for_this_Unit_operation** Select an actual approved fictional destination POI if that branch is narrated, then inspect its returned label/location. Proof required: Saved call/destination distinction using a real POI; an empty selector can only support explaining an empty state.

### 08-dispatch-and-edit-with-a-reviewed-scope — Dispatch and edit with a reviewed scope

Prior evidence: none.
New read-only evidence: none.

- **U02-S08-A — not_captured_for_this_Unit_operation** Create New Call →Dispatch To; clear any broad default and select only coordinator-approved fictional recipients. Inspect the loaded scheduling control if offered. Proof required: Actual selected recipient summary and actual immediate/scheduled time control state.
- **U02-S08-B — not_captured_for_this_Unit_operation** Create exactly one approved clearly TRAINING ONLY Unit exercise. Capture returned actual number/ID and real detail result. Proof required: Successful actual Unit creation result, received number and narrow dispatch scope; no assumed numbering or delivery claim.
- **U02-S08-C — not_captured_for_this_Unit_operation** On that new call, use the real overflow menu →Edit Call. Change one public-safe fictional Contact Info value →Save→fresh reopen Contact. Proof required: Actual menu/form/input/Save and returned stored Contact Info; no cached-only success.

### 09-share-concise-incident-evidence — Share concise incident evidence

Prior evidence: 020-practice-call-info.
New read-only evidence: 016-incident-history-nearby-training-call; 017-site-information-full-empty-state; 018-call-files-empty.

- **U02-S09-A — not_captured_for_this_Unit_operation** Notes→enter a clearly TRAINING ONLY access note→actual add/send control→close/reopen. Proof required: Actual newly stored note text, fictional author/time and fresh-read result; retain exact readback before submit.
- **U02-S09-B — not_captured_for_this_Unit_operation** Images→actual gallery/library selection; when the normal authorized chooser is available, select only a public-safe fictional software image→training note→Upload→reopen. Proof required: Real selection preview, Upload and stored image result. A file dialog alone is not storage proof.
- **U02-S09-C — captured_and_qualified_for_bounded_readonly_scope** Open Files, Site Info and History separately; inspect loaded bodies/empty states. Proof required: Actual Files list/download/share offer, matched site information and earlier-call history or their honest empty states. No invented upload control.
  Scope of existing proof: Files/SiteInfo are loaded empty; History shows a Nearby closed exercise. No stored file, native download/share or populated pre-plan demonstrated.
- Before freeze: Correct “Images and Files attach supporting material”: Images has selection/upload; current call-files-modal.tsx only lists/downloads/shares existing files. Translated Add File/Upload strings alone do not create rendered controls. Native file writing/sharing is untested on web.

### 10-use-check-ins-command-and-video-appropriately — Use check-ins, command, and video appropriately

Prior evidence: 020-practice-call-info.
New read-only evidence: 012-incident-command-empty; 013-incident-video-empty.

- **U02-S10-A — not_captured_for_this_Unit_operation** On an approved active call with timers enabled, select Check-In; inspect actual eligible target cards/type choices before acting. Proof required: Actual timer/target/countdown, Check In form and offered Personnel/Unit-type choices.
- **U02-S10-B — not_captured_for_this_Unit_operation** If authorized, record one explicitly fictional software check-in with a clear note, then open History. Proof required: Actual success and newly stored history entry for the selected target. No GPS/physical arrival/remote alert claim.
- **U02-S10-C — captured_and_qualified_for_bounded_readonly_scope** Open Command and Video; capture actual content/loaded empty states. Proof required: Real command resource panel and configured feed list or honest no-feed state.
  Scope of existing proof: Command and Video loaded empty.014 only shows an unsaved feed form; no actual command assignment/feed creation/stream exercised.

### 11-complete-the-crew-s-checklist-deliberately — Complete the crew’s checklist deliberately

Prior evidence: none.
New read-only evidence: none.

- **U02-S11-A — not_captured_for_this_Unit_operation** Sidebar Checklists→Due checks→actual published definition/target or Open check. Proof required: Actual active unit target, checklist name/published version/required items and entry into the editable run.
- **U02-S11-B — not_captured_for_this_Unit_operation** Answer only fictional non-attestation items; inspect an actually allowed Not applicable→Reason branch and actual conditional/required item validation. Proof required: Real entered answer, required indicator, Not applicable and Reason; no invented branch.
- **U02-S11-C — not_captured_for_this_Unit_operation** Save progress→close→Local drafts or server History→reopen the same run. Proof required: Actual resumable stored answer/version and run identity. “Start checklist” is a heading; new runs start with a target-name button, not necessarily a button with that heading.
- **U02-S11-D — not_captured_for_this_Unit_operation** Review the permitted completed training answers→Submit checklist; capture the actual returned state or validation/refusal. Proof required: Real submitted / Awaiting witness / failed validation result, with no Attest and complete action.
- **U02-S11-E — not_captured_for_this_Unit_operation** If photo/evidence is retained in practice, use an authorized public-safe sample through the actual normal chooser and reopen its evidence; otherwise keep the photo branch expressly unresolved. Proof required: Real selected/stored evidence shown in this Unit run, not Responder evidence or an empty photo control.
- Before freeze: Correct “choose an apparatus target and Start checklist” to identify the actual Start checklist heading and target-name button. “Resume ... review a photo” remains an operation gap until actual Unit evidence exists.

### 12-close-deselect-and-reset-deliberately — Close, deselect, and reset deliberately

Prior evidence: 024-engine51-response-saved; 025-engine51-response-header; 035-available-no-destination-step; 038-available-correction-exact-readback; 039-engine51-available-header-crew.
New read-only evidence: none.

- **U02-S12-A — not_captured_for_this_Unit_operation** On only the new owned disposable Unit call, actual overflow→Close Call. Show Close Type choices, clear training Close Note and Notify everyone on the call OFF. Proof required: Actual Unit close form with selected type/note/off notification state immediately before submit.
- **U02-S12-B — not_captured_for_this_Unit_operation** Submit Close Call once; capture success and refreshed active-call list without the new call. Proof required: Actual Unit closure result and disappearance/closed detail state; errors such as active incident command remain real blockers.
- **U02-S12-C — not_captured_for_this_Unit_operation** If active selection remains, use Deselect→real browser confirmation→accept, then capture No Active Call. Proof required: Actual web confirmation and cleared-selection result, separate from closure.
- **U02-S12-D — not_captured_for_this_Unit_operation** Inspect final actual Engine51 status. If parent authorizes a cleanup status, submit the chosen configured no-destination state with a clear training note and fresh-read result; preserve Herrmann1/1. Proof required: Independent final status/NoActiveCall/crew proof. Do not assume Close or Deselect made the unit Available or Released.

## Crew Save and restoration

015/040 prove the existing Officer / Team Lead seat is Herrmann with Save disabled. The real picker can reselect Herrmann to create a pending choice; an authorized actual Save plus fresh reopen can demonstrate confirming the same assignment, not a changed crew. The current relief-driver practice must be corrected to the actual seat.

A true relief-replacement example requires parent approval of the exact eligible fictional member, ordinary selection→Save→fresh reopen, then immediate Herrmann restoration through the same controls and fresh reopen. Preserve all other seats/units and personal statuses/staffing/shifts/qualifications. Honor a qualification refusal. Save replaces the active unit’s full seat payload; if restoration fails, report the temporary state before other work.

## Interactive mapping blocker

`unit-response-map-mismatch-diagnosis-20261027.json` retains the original021 failure, exact source/SDK hashes,16-case option probes and real-component10-test regression. Undefined numeric Camera option keys cause NaN in installed MapboxGL; the proposed patch omits undefined zoom/bearing/pitch while retaining valid0. Original source produced5 failed Camera tests; proposed source passed10. The normal Unit Jest setup is separately blocked by missingreact-native-permissions; no install/setup edit. Actual browser cartography retest is still required, and this agent did not apply the patch.

Typing GPS text alone does not set selectedLocation. The real GPS magnifier parses/stores the point even if address lookup warns. Full-screen X discards the picker without Set Location. The inline picker has no dismiss control; leave Confirm Location/map untouched and scroll past it, or Cancel the whole unsaved form. No device GPS permission or actual location claim.

## Capture sequence

1. Read-only refresh/context + Calls clear-search and detail/tab content captures; keep original active calls unchanged. (U02-S01-A, U02-S02-A, U02-S02-B, U02-S02-C, U02-S04-A)
2. Crew picker inspection, then only the exact parent-approved same-assignment or relief+restoration Save example. (U02-S05-A, U02-S05-B, U02-S05-C)
3. Coordinate one new clearly TRAINING ONLY disposable Unit call; capture blank/validation/options/location/destination/recipients and actual returned identity. (U02-S06-A, U02-S06-B, U02-S07-A, U02-S07-B, U02-S07-C, U02-S08-A, U02-S08-B, U02-S01-B)
4. Capture call edits, maps, notes/image/file/site/history contents; Set Active/status only when needed and authorized, preserving clear software-only notes. (U02-S08-C, U02-S03-A, U02-S03-B, U02-S09-A, U02-S09-B, U02-S09-C)
5. While the owned call is still open, coordinate an eligible narrow timer; record only actually offered Unit check-in and stored history; inspect Command/Video loaded states. (U02-S10-A, U02-S10-B, U02-S10-C)
6. Run the separate authorized fictional Unit checklist to save/resume/submit boundary; no witness attestation, signature or device GPS. (U02-S11-A, U02-S11-B, U02-S11-C, U02-S11-D, U02-S11-E)
7. Close only the newly owned call with Notify everyone OFF; capture closure, separate Deselect dialog/result and independent final unit/crew state. (U02-S12-A, U02-S12-B, U02-S12-C, U02-S12-D)
8. Hold/queue branches stay unresolved unless specifically approved and actually exercised; no department setting/network mutation just to fill footage. (U02-S04-B, U02-S04-C)

Read-only resolution statuses above supersede the initial planned capture needs; operations newly recorded in parent’s action folder need their own later pixel/DOM review.

## Platform limits

- No actual GPS, camera, microphone, native background location/alert, external navigation/feed or provider receipt is exercised or claimed.
- Current source supports required live-fix statuses, signature/location-required checklist fields and protected access. Such branches are not bypassed; stop at their actual boundary.
- File download/share uses device filesystem/sharing code; a web list/empty state does not demonstrate native download/share success.
- No durable native offline-recovery claim can come from a desktop browser queue/control alone.
- No new call number, destination POI, timer or eligible relief member is assumed to exist; actual coordinator-prepared state and returned identifiers must be recorded.

Exact hashes, all36 group statuses, sources, rejected records and all six sector companions are retained in the adjacent JSON. No cue timing or media master is invented.
