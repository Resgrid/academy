# Responder source audit and remaining capture work

Audited source: `0760a098e78871a6ce193a328f28926fad123e3b`. Lessons02 and04 remain unfrozen. Orientation01 and communications03 hashes are preserved. This is maintainer context, not learner-site production status.

## Critical boundaries

- New Call and Clear search are accessible icon controls, not guaranteed literal labels. New Call needs canUserCreateCalls; Clear search appears only after text entry. Capture DOM control boxes and review the actual image. Source: `Responder/src/app/(app)/home/calls.tsx:169`.
- Address, geolocation, what3words, Plus Code and recipient/schedule fields follow the loaded department field policy. A location field existing in source does not prove the active policy offers it. Source: `Responder/src/app/call/new/index.tsx:941`.
- Set as Active Call selects this call locally. This action does not send personal responding status. Home has a separate View Call Details and Clear Active Call. Source: `Responder/src/app/call/[id]/index.tsx:179`.
- Route to Destination is conditional on a destination with coordinates. Routing invokes an external mapping application; do not open it in this fixture or claim navigation or physical travel. Source: `Responder/src/app/call/[id]/index.tsx:328`.
- Call Files lists and downloads/shares existing attachments. It contains no file upload control. Call Images separately offers photo/library selection and upload; camera and native sharing are unexercised. Source: `Responder/src/components/calls/call-files-modal.tsx:106`.
- The Check-In tab only renders on a timer-enabled call. Current CheckInTabPanel offers eligible checks and history; ToggleCallTimers is API-only, not a rendered timer-management screen. Source: `Responder/src/app/call/[id]/index.tsx:513`.
- Personnel/unit/PAR/hazmat/rotation/rehab choices depend on resolved eligible targets and current unit type. Do not force a target by changing crew or role assignments. Source: `Responder/src/components/check-in/check-in-tab-panel.tsx:91`.
- Contextual New Record is hidden unless Records.Field is enabled and the server catalog offers a definition for the current verified context. Source: `Responder/src/components/records/records-quick-create.tsx:38`.
- Prefill only runs for a definition advertising SupportsPrefill. Keep on this device remains rendered but disabled when offline authoring is unavailable; source presence does not prove durable browser storage. Source: `Responder/src/app/records/new.tsx:71`.
- Draft/Returned records with supported schema render Save, Submit for review, attestation and Finalize. Finalize remains disabled until attestation; the server enforces authority. DraftReference is a legitimate draft identifier; it is not a failed final number. Source: `Responder/src/app/records/[id].tsx:87`.
- Attachments are record-specific after a server record exists, editable only in Draft/Returned and hidden when AllowAttachments is false. Amend, void and approve remain web-first, with no action here. Source: `Responder/src/app/records/[id].tsx:232`.
- Read feed now is readiness-gated and can contact an external system. View existing status only; credentials, reconciliation decisions and provider reads are outside this capture scope. Source: `Responder/src/app/records/connectors/[id].tsx:146`.
- Trade Accept/Decline require incoming + Open + MyState Open; outgoing offer selection, cancellation and supervisory review have distinct gates. These are real rendered actions but remain unexercised in the captured unsent form. Source: `Responder/src/components/shifts/shift-trade-card.tsx:113`.
- Work-order Steps are read-only Text rows, not interactive completion checkboxes. Assignment acceptance requires CanWrite and CanAccept; transition inputs follow the server transitions/requirements. Source: `Responder/src/app/(app)/work-orders/[id].tsx:148`.
- Cancel Attendance uses native Alert with no browser confirmation fallback in this source. The saved signup is real; the cancel button was viewed without a demonstrated cancellation. Source: `Responder/src/components/calendar/calendar-item-details-sheet.tsx:139`.
- Native checklist storage uses encrypted envelopes and device-only SecureStore keys; the browser uses memory only. Same-session resume does not prove reload/crash/offline persistence. Source: `Responder/src/lib/checklists/vault.ts:9`.
- Responder supports time approval only when access.CanApprove and a submitted report exist. Unit disables approval in its app capabilities. This captured report is unsigned Draft, so no approval is demonstrated. Source: `Responder/src/app/(app)/operations/[id].tsx:85`.
- F-42 panel drafts from deployment time reports and validates through the API. The displayed Not ready for the portal is a real validation failure, not successful portal submission. Submission remains a separate audited manual web handoff. Source: `Responder/src/components/operations/mars-panel.tsx:19`.

## app-responder-02-calls-and-records

Current script SHA256: `44c35ed25f7f492dd6c28623fb0237db30b558733a459f5786990b0811a7386b`. 943 words.

### 01-find-the-incident-you-mean

Route: `/home/calls`. Existing actual refs: 016-calls-styled.

- After human clears Chrome, authenticate Boden normally with no credential screenshot; confirm the Calls view.
- Type the fictional medical call name; capture its card and the Only Calls I'm On toggle, then Clear search before reviewing the complete list.
- Capture New Call/Clear search accessible names and fully visible DOM boxes; bind an image-reviewed visible_controls attestation rather than inventing painted labels.
- Limit: Browser remains explicitly blocked until human extension dismissal.
- Limit: New Call needs create permission; search reset only exists when search text is nonempty.
### 02-read-the-detail-tabs-before-acting

Route: `/call/[id]`. Existing actual refs: 032-call-info-repaired, 034-call-protocols-empty, 035-call-dispatched, 036-call-activity.

- Reopen call 51002 without closing it; capture clean Contact, full Info rich text, and active tab contents.
- Reuse only reviewed 032/034/035/036 captures if they still match the lesson; empty Protocols must retain its actual no-protocols message.
- Limit: Contact033 has an obscuring development notice and is excluded.
- Limit: This incident currently has no attached protocol; do not narrate an attached protocol as present.
### 03-create-only-the-call-you-intend

Route: `/call/new`. Existing actual refs: none.

- Open New Call after coordinator confirms a disposable training-call window; capture actual loaded field-policy fields and any harmless validation message.
- Prepare a clearly TRAINING ONLY industrial alarm without saving, dispatching or altering the reserved calls.
- Limit: No Create action until the Core numbering/run-card coordinator authorizes a disposable scenario.
- Limit: Existing call 51002 stays open; parent-reserved 51006 is untouched.
### 04-resolve-and-confirm-the-location

Route: `/call/new`. Existing actual refs: 045-call-location-controls.

- Show Address/GPS Coordinates/what3words/Plus Code only when the current policy offers them; record the actual route as Edit Call for existing screenshot045.
- If safely supported, demonstrate a non-provider invalid coordinate message. Do not request/accept actual GPS, open an automatic-location picker, or invoke external geocoding.
- After map adapter verification is authorized and browser unblocks, accept a map image only when actual cartography and the app-supplied incident point appear.
- Limit: Map adapter is source/compile verified; standalone cartography is still pending actual browser validation.
- Limit: Provider searches and physical-device location are not authorized evidence.
### 05-choose-recipients-and-scheduling

Route: `/call/new`. Existing actual refs: 046-call-dispatch-recipients, 047-dispatch-recipients-clean.

- Capture allowed Groups/Units and scroll actual Users/Roles if offered; preserve existing assignments and recipients.
- Capture permitted schedule input and its actual validation without sending a notification or creating a scheduled incident.
- Limit: Current screenshots046/047 are Edit Call; they are not evidence of Create New Call or a dispatched schedule.
- Limit: Everyone and hidden policy fields are not universally available.
### 06-correct-details-without-losing-context

Route: `/call/[id]/edit`. Existing actual refs: 042-call-menu-repaired, 044-edit-call-form, 045-call-location-controls, 047-dispatch-recipients-clean.

- Show menu Edit Call, current values and Save. If a coordinator-approved independent incident exists, change one fictional description only and verify it after reopening.
- Until a saved before/after is captured, narrate the form and verification procedure rather than claiming a saved correction.
- Limit: Do not modify parent-reserved 51006, global dispatch policies or unit staffing.
### 07-make-the-call-active-and-navigate

Route: `/call/[id] -> /home`. Existing actual refs: 042-call-menu-repaired.

- Capture Home active Call, View Call Details and Clear Active Call with call 51002 context; distinguish selection from a personal status submission.
- Capture Route and Route to Destination only if the call has a destination with coordinates. Stop before external navigation.
- Limit: No external maps navigation, real GPS or turn-by-turn driving proof.
- Limit: Destination action is conditional; do not require it on the current standby if absent.
### 08-add-useful-notes-and-supporting-evidence

Route: `/call/[id]`. Existing actual refs: 032-call-info-repaired, 048-call-note-compose.

- After fresh canonical-issuer login, submit one fictional Call Note and reopen Notes to verify the persisted text; otherwise retain it as prepared/failed only.
- Open Images and existing Files, recording actual empty states; file upload is not available in this Call Files screen.
- If a permitted synthetic source image is later uploaded through actual Images UI, inspect the server-returned item separately; no camera access or unrelated private files.
- Limit: Capture049 is an authentication failure and excluded; it does not prove the note saved.
- Limit: Call Files download/share depends on native file-system/sharing behavior and remains unexercised.
### 09-use-site-history-and-incident-coordination

Route: `/call/[id]`. Existing actual refs: 037-call-site-info, 038-call-location-history, 039-call-command, 040-call-video.

- Show No site information, No related calls, No incident command and No video feeds as actual dataset states.
- Only expand to populated preplan/history/command after an independently guarded fictional fixture is available; never open external feeds or paint replacements.
- Limit: The current four screenshots contain no warehouse preplan, active command operation or video stream.
### 10-check-in-against-the-correct-target

Route: `/call/[id]`. Existing actual refs: none.

- Use a separate coordinator-approved timer-enabled training call and eligible personnel target; do not change current role/unit assignments.
- Capture Check-In, eligible timer target, note/Confirm check-in and server history only if actually offered. Distinguish a saved check-in from an offline-queued outcome.
- Capture the no-tab/no-timers case honestly when timer setup is unavailable; do not add an imaginary timer-management control.
- Limit: No timer-enabled call or eligible-target screen is captured yet.
- Limit: A check-in is a software record, not GPS arrival, push delivery or a safety assurance.
### 11-start-a-call-linked-field-record

Route: `/call/[id] -> /records/new`. Existing actual refs: none.

- Open call-context New Record only if server catalog offers it; show definition/version and actual form labels.
- Use a fictional incident record draft: distinguish SupportsPrefill context, ordinary required fields and finalize-only requirements.
- Use Save and send only through normal UI, then capture returned Draft/DraftReference. Show Keep on this device enabled or disabled according to the definition without claiming durable browser offline behavior.
- Limit: Records.Field/catalog/access/schema/definition compatibility must be verified in actual browser first.
- Limit: An incident record legitimately remains Draft; never fabricate final number or finalization.
### 12-review-drafts-attachments-and-final-states

Route: `/records -> /records/[id]`. Existing actual refs: none.

- Open a genuinely server-saved fictional Draft record, capture Drafts/Returned to you list and actual detail identifier/state.
- Show Save, allowed attachment controls and conditional Submit for review/Finalize with unchecked attestation. Do not attest, finalize or claim a review outcome.
- If an actual permitted upload is performed later, verify attachment server state and metadata; do not infer it from a picker or progress label.
- Limit: Draft/Returned plus supported schema render editing controls; final states are read-only.
- Limit: Attachment policy and server authority govern each action; approval/amend/void remain web workflows.
### 13-distinguish-external-orders-and-feeds

Route: `/records/deployments -> /records/connectors`. Existing actual refs: none.

- Open Records Deployments and External connectors read-only, capture actual empty/readiness/authority/run-history messages.
- If a fictional order exists, inspect its fills/reconciliation values only; do not press Read feed now or change credentials/reconciliation.
- Limit: No external feed read, provider dispatch or write authority is claimed.
- Limit: Operational time-report deployments are a separate data model and route.
### 14-close-the-incident-deliberately

Route: `/call/[id]`. Existing actual refs: 042-call-menu-repaired, 043-close-call-preparation.

- Reuse reviewed close preparation043 with exact Close Note (Optional): label; show Close Type, notification explanation and Cancel.
- Keep51002 open and51006 untouched. Capture a closed result only on a separately coordinated disposable fictional call if later authorized.
- Limit: No actual call close occurred in this Responder sequence.
- Limit: Closing a call, clearing active selection and finalizing a record are independent operations.

## app-responder-04-readiness-and-operations

Current script SHA256: `585cfb74356f574869383f2d0164a68cf77c68839eb621a0c5e1e9fe59469f98`. 956 words.

### 01-understand-the-shift-views

Route: `/shifts`. Existing actual refs: 093-shifts-today-overview, 097-my-shifts-overview, 105-shift-on-duty-roster.

- Review existing Today/My Shifts/On Duty screenshots and the visible tabs; no new roster mutation is needed.
- Limit: Giant browser tab layout is a known source limitation; never substitute an illustrated roster.
### 02-sign-up-and-review-the-roster

Route: `/shifts`. Existing actual refs: 099-signup-practice-open-day, 100-signup-team-confirmation, 101-signup-result, 102-signup-withdraw-confirmation, 103-signup-withdrawn-result, 106-shift-supervisor-approvals.

- Reuse actual independent day51003/51108 signup, capacity 2-to1 and withdrawal-to2 proof; keep the final unenrolled state.
- Use existing supervisory approval screenshot view-only; do not approve/deny another member.
- Limit: Existing signup/withdraw results are real; Add person and supervisory actions remain permission-gated and unperformed.
### 03-trade-a-shift-with-a-clear-agreement

Route: `/shifts`. Existing actual refs: 094-shift-day-roster, 096-shift-trade-prepared, 104-shift-trades-empty.

- After human clears Chrome, sign in as Boden normally and use only independent future practice shift 51003/day 51108.
- Inspect actual candidate eligibility. If Casey is not offered/eligible for the Chief day, capture the refusal or unavailable choice; never change roles or qualifications.
- For an eligible training-only request, capture sending, separate Casey response if offered, outgoing offer selection/confirmation and actual resulting status. Preserve seeded staffing, trades and approvals.
- Limit: Current screenshot096 is prepared/unsent and104 has no trades.
- Limit: Accept/Decline require incoming Open and MyState Open; give/swap, cancel and supervisor review have separate source gates.
- Limit: No completed trade or approval has been captured.
### 04-attend-an-event-and-connect-the-learning

Route: `/calendar`. Existing actual refs: 107-event-calendar-today, 111-calendar-signup-result-repaired, 113-event-attendance-visible-controls.

- Reuse actual briefing signup Signed Up/attendee proof and the Cancel Attendance button.
- Leave cancellation unclaimed unless an authorized retained compatibility change or a genuine native capture supplies the missing confirmation and result.
- Limit: Current native Alert cancellation has no browser confirmation; do not retry the same no-op or claim canceled attendance.
### 05-maintain-a-certification-record

Route: `/certifications -> /certifications/edit`. Existing actual refs: 114-certification-list, 117-certification-add-input-labels.

- Reuse actual My certifications/Add form fields without Save, photographs or qualification changes.
- Limit: Photo and credential verification controls are view-only; no actual card/camera or new qualification.
### 06-renew-and-document-continuing-education

Route: `/certifications/[id]`. Existing actual refs: 118-certification-renewal-ce-controls, 119-certification-ce-prepared, 120-certification-ce-result, 122-certification-renewal-prepared, 123-certification-renewal-result.

- Reuse actual quarter-hour software-practice CE result and renewal Awaiting verification.
- Show supporting-photo control only; do not turn a software practice entry into accredited credit or approved professional renewal.
- Limit: Department verification remains outstanding.
### 07-prepare-due-checks-before-leaving-coverage

Route: `/checklists`. Existing actual refs: 124-checklists-start-overview, 125-checklist-required-critical-item, 127-checklist-local-draft-list, 128-checklist-resumed-draft, 140-checklist-submitted-score, 170-checklist-history-visible.

- Reuse selected checklist/target/version, actual simulated failure, draft/resume, Submitted · Score: 66.67 and History.
- Retain exact literal Required question and combined Submitted/Score label; confirm the source image is legible at rendered size.
- Limit: The score is a fictional software exercise, not equipment certification; no new physical inspection.
### 08-answer-the-checklist-with-evidence

Route: `/checklists`. Existing actual refs: 126-checklist-simulated-failure-note, 159-checklist-not-applicable, 160-checklist-yes-no, 161-checklist-checkbox, 162-checklist-numeric, 163-checklist-quantity, 164-checklist-free-text, 165-checklist-select-list, 166-checklist-date, 167-checklist-photo-controls, 168-checklist-signature-pad.

- Reuse all ten actual answer type views and N/A reason; show blank Photo and Signature tools without opening a camera or signing.
- Limit: Capture controls are not photographic evidence or an attestation; optional items were not invented as completed.
### 09-handle-witnesses-and-offline-conflicts

Route: `/checklists`. Existing actual refs: 172-checklist-persisted-awaiting-witness, 176-witness-account-context, 177-casey-independent-witness-form, 173-checklist-queued-recovery.

- Reuse distinct Casey identity and the actual independent witness form, with blank statement and disabled Attest and complete.
- Reuse genuine queue recovery controls; no server-version replacement or induced outage occurred.
- Limit: Casey authorization is view-only for witness; do not submit attestation.
- Limit: Browser vault is memory-only and native Alert replacement is not demonstrated; native persistence/recovery requires separate device evidence.
### 10-report-a-maintenance-problem-clearly

Route: `/work-orders -> /work-orders/new`. Existing actual refs: 142-work-orders-assigned, 143-work-order-report-prepared, 144-work-order-report-heading, 145-work-order-created.

- Reuse the saved fictional facility report with no apparatus/safety-critical designation and its actual Requested number.
- Limit: Do not reclassify the practice request as an apparatus defect or change unit availability.
### 11-work-an-assigned-order-with-a-useful-trail

Route: `/work-orders/[id]`. Existing actual refs: 145-work-order-created, 146-work-order-saved-activity, 147-work-order-accepted.

- After human clears Chrome, open independent assigned-order e6158298-a817-4d92-b075-a7d7ed331b5e as Boden.
- Show Accept assignment only if server CanWrite/CanAccept; capture a permitted acceptance result without altering any other order.
- Inspect Steps as read-only text. Select only a safe offered transition to expose required reason/resolution/cause/verification/duplicate/all-steps fields; do not certify physical work or complete steps via nonexistent buttons.
- Retain the already saved Requested-to-Accepted,0.1 h practice labor and comment trail from the separate original report.
- Limit: Assigned fixture acceptance and transition-specific input screenshots are still missing.
- Limit: Steps are read-only content, not interactive completion checkboxes; server transitions/revision govern every mutation.
### 12-use-maps-and-settings-for-field-awareness

Route: `/map -> /weather-alerts -> /settings`. Existing actual refs: 157-map-poi-list, 158-weather-alerts-filters, 057-settings-native-capability-controls.

- Reuse actual zero-POI and empty-weather severity views and native settings, retaining their limitations.
- After human clears Chrome, verify the declared web Mapbox adapter with real cartography/app-supplied coordinates. Only a visible valid map may replace the excluded gray156; no provider bypass, painted map, mock or actual GPS request.
- Limit: Support source/compile checks passed, but the new adapter has no actual successful browser cartography capture.
- Limit: POI search overlaps on this browser; native permissions/background/Keep Alive cannot be validated from switches.
### 13-record-daily-deployment-time-accurately

Route: `/operations -> /operations/[id]`. Existing actual refs: 148-deployment-list, 149-deployment-scope, 150-time-report-entry-fields, 151-time-report-save-submit-signature.

- Reuse actual unsigned daily crew report, default sample subjects/hours, saved entries and break warnings.
- Inspect submit/signature controls without signing, claiming worked hours or approval.
- A later approval demonstration would need a separate authorized submitted practice report and CanApprove reviewer; it is not current evidence.
- Limit: Actual report remains Draft/unsigned. Approval is supported by Responder but absent without Submitted+CanApprove; no signature/attestation/payment operation is performed.
### 14-keep-costs-usage-and-recovery-distinct

Route: `/operations/[id]`. Existing actual refs: 152-deployment-expense-form, 153-deployment-usage-form, 154-deployment-f42-boundary, 155-deployment-f42-validation.

- Reuse expense/usage forms view-only and the actual F-42 Not ready validation with missing prerequisites.
- Do not treat the work-item summary counts as a ready result or request any government/financial/provider submission.
- Limit: No expense or usage reading was saved. F-42 validation failure is intentional actual evidence; portal handoff remains manual web.
