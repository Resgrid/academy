# Unit source audit and remaining capture work

Audited source: `0753b6baafbaec74617a412cd9c87fa9de899d47`. All four Unit lesson JSONs await actual captures. No audio, export, browser capture, or completed-video claim was produced by this audit.

## Critical boundaries

- Holding for two seconds and Hold to submit depend on department configuration. Normal mode uses ordinary submission; Current on quick buttons is accessibility text/ring, not guaranteed literal paint. Source: `src/components/sidebar/sidebar-content.tsx:40`.
- Set Active saves incident selection then opens status selection with call preselected; unit status has not yet been submitted. Source: `src/app/call/[id].tsx:169`.
- Manual route check-in substitutes0,0 without device fix; software state change is not physical-arrival proof. Source: `src/app/routes/stop/[id].tsx:125`.
- Pause/resume/cancel/acknowledge functions exist in API/store but are not invoked by current rendered route controls. Cancelled history text and Acknowledge badge are state displays. Source: `src/stores/routes/store.ts:171`.
- Acknowledge is conditional badge text only, with no onPress action in DeviationCard. Source: `src/app/routes/history/instance/[id].tsx:458`.
- End Route confirmation uses native Alert; browser confirmation/completion requires actual verification or separately authorized retained compatibility fix. Source: `src/app/routes/active.tsx:217`.
- Complete and Cancel count use native Alert. Do not treat a web button click as posted adjustments. Controlled-item witness remains a separate web workflow. Source: `src/app/(app)/inventory/count/[id].tsx:57`.
- Zone action routes with zoneName/zoneId. New-call source does not consume these params; no coordinate or recipient prefill can be claimed. Source: `src/app/maps/indoor/[id].tsx:74`.
- Unit already has a real web map event/camera adapter and HtmlRenderer.web; Responder installed-SDK/WebView failures do not establish Unit failures. Source: `src/components/maps/map-view.web.tsx:309`.
- Lock/unlock are icon accessible names. Need actual DOM control boxes plus separate screenshot review; never append semantic names to literal visible_labels. Source: `src/components/sidebar/unit-sidebar.tsx:85`.
- Audio Settings and Disconnect belong to connected view; empty picker does not support claiming those controls or hardware/provider success. Source: `src/components/livekit/livekit-bottom-sheet.tsx:224`.
- Unit writes crew/individual time and usage/expenses and can draft F42; it intentionally does not offer supervisor time approval. Source: `src/lib/operations/capabilities.ts:15`.
- Checklist web vault is memory-only; native uses device-only keys/envelopes. Other feature offline behavior must be inspected separately. Source: `src/lib/checklists/vault.ts:9`.
- Add passkey is conditional and credential changes are outside this recording authorization. Source: `src/app/(app)/account-security.tsx:194`.

## Current crew fixture to preserve

- Preserve Engine51 unit role51001 Officer/TeamLead = Christopher Herrmann only. The other five units remain unassigned; do not change member status, shift assignments or qualifications for this crew example.
- Parent retained the guarded normal-UI assignment and reopened proof separately; source audit does not claim to have captured Unit role UI itself.

## Capture order and scenarios

- Authenticate fictional Boden on dedicated Unit tab only; selectEngine51 and verify both member+unit.
- Orientation/roles/status/call-context views, using existing permitted calls and preserving parent run-card resources.
- Route fixture with assigned Engine51, actual pending→InProgress→Completed/Skipped stop states and genuine history; observe native-alert boundary for End Route.
- Independent compartment/whole-unit counts with serialized+bulk examples, server-save proof and actual completion/cancellation/witness boundary.
- Unit04 map/layers/indoor/weather/references/chat/voice availability/records/deployment/settings views; use each real source component and state.

Use fictional Fire/EMS coordination, community-care rounds, SAR transport or trail checks, security patrol visits, wildland staging, and industrial inspection scenarios through actual fields. Every Unit lesson includes a relevant spoken example beyond Fire/EMS; companions retain all six sectors.

## app-unit-01-access-and-crew

638 spoken words. Source SHA256: `294324f3934a6ebec9eeccde7e506d5ce15aa7e967dc6c58dc1a1be0b84bbedc`.

- **01-understand-the-person-and-the-apparatus** (/): Show authenticated member identity and active-unit context; open Settings.
- **02-complete-first-launch-and-choose-the-server** (/onboarding -> /login): Capture each actual onboarding page and empty login with Language; open Server URL without displaying credentials.
- **03-sign-in-with-an-available-method** (/login -> /login/sso): Capture empty password/SSO entry; show only verification choices actually offered, without changing methods or exercising a real provider.
- **04-configure-a-shared-installation-deliberately** (/login/shared-device): Open Shared device setup and show toggle/label/Save; if configuration is changed, verify normal next sign-in rather than injecting session state.
- **05-practice-lock-and-shift-handoff** (/): Capture actual shared-session bar if server offers it, then permitted Lock/End shift/Switch operator states; never fabricate idle deadlines or unlock choices.
- **06-select-the-apparatus-you-actually-have** (/settings): Open Active Unit/Select Unit and choose authorized Engine51; verify Current Unit.
- **07-assign-the-actual-crew-roles** (Sidebar Roles): Open Unit Role Assignments for Engine51 and show the existing Officer/TeamLead seat51001 assigned only to Christopher Herrmann; reopen to verify without changing crew, other units, staffing or qualifications.
- **08-read-the-unit-status-before-changing-it** (Sidebar Status): Use an existing training call Set Active to open Select Status; capture current banner and actual configured options; submit only an authorized fictional unit change using the currently offered mode.
- **09-understand-the-sidebar-incident-context** (Sidebar Call): Show Select Active Call and selected call card; inspect details/directions controls; Deselect may use actual browser confirmation, without launching external maps.
- **10-keep-account-security-and-recovery-visible** (/settings -> /account-security): Open account security and no-challenge recovery prerequisite; no passkey/MFA/device credential changes.

## app-unit-02-response-and-checks

763 spoken words. Source SHA256: `4d2a6ad9f9e6c3a737f3ce96439b0cb712c531e3cf6d596fddc8ce32d2caa768`.

- **01-find-the-correct-call** (/calls): Show Calls search, a fictional result, clear control, and actual New Call entry if permitted.
- **02-read-the-incident-before-responding** (/call/[id]): Open existing51002 or another non-reserved training call; scroll Info/Contact/Protocols/Dispatched/Activity and capture real contents or empty states.
- **03-set-the-active-incident-and-check-routing** (/call/[id]): Capture Set Active and resulting Select Status before any unit transition; inspect internal map views; external Route handoffs remain unexercised.
- **04-update-unit-status-with-a-destination** (Sidebar Status): Capture source-offered destination/note steps and actual Submit or hold control; verify saved result, and label genuine queue state only if it occurs.
- **05-keep-the-seated-crew-accurate** (Sidebar Roles): Open Unit Role Assignments for Engine51 and show the existing Officer/TeamLead seat51001 assigned only to Christopher Herrmann; reopen to verify without changing crew, other units, staffing or qualifications.
- **06-create-a-call-with-the-permitted-fields** (/call/new): Open actual creation form and policy-required fields; do not Create until Core coordinator authorizes an independent numbered exercise.
- **07-resolve-the-call-location-and-destination** (/call/new): Show location input modes and permitted fictional coordinate/map selection; never accept real GPS permissions or claim external lookup success.
- **08-dispatch-and-edit-with-a-reviewed-scope** (/call/new -> /call/[id]/edit): Inspect actual dispatch recipients/scheduling; after authorization create or edit a dedicated TRAINING call, verify saved fields without provider-delivery claims.
- **09-share-concise-incident-evidence** (/call/[id]): Create a clearly labelled training note and verify it; inspect Images/Files upload controls and real SiteInfo/History views.
- **10-use-check-ins-command-and-video-appropriately** (/call/[id]): Inspect Check-In target/timer and history; Command/Video need prepared internal incident/feed data, otherwise record honest empty states.
- **11-complete-the-crew-s-checklist-deliberately** (/checklists): Select active-unit checklist; capture required/conditional fields, save/resume/submit only fictional answers, and actual witness boundary without attestation.
- **12-close-deselect-and-reset-deliberately** (/call/[id] -> Sidebar Call): Use a separate approved disposable call for actual closure; keep51002 open and avoid parent-reserved51006. Capture Close form/result, Deselect confirmation/result, and unit status separately.

## app-unit-03-routes-and-inventory

768 spoken words. Source SHA256: `301aceaf5283ee8afdf0fe7a2dff64b24c6f59ab263011961a63d4baf16878bb`.

- **01-browse-the-routes-and-poi-context** (/routes): Capture Routes/My Unit/All Routes and POIs, search/filter/sort using prepared actual data.
- **02-review-the-plan-before-starting** (/routes/start): Open a route assigned to Engine51; show ordered stops, schedule and Start Route; no reassignment to bypass eligibility.
- **03-read-the-active-route-s-progress** (/routes/active): Show actual active instance, progress/next-stop and direction availability; do not claim a provider journey.
- **04-check-in-at-the-intended-stop** (/routes/stop/[id]): Open a pending training stop, capture manual Check In and resulting state; explicitly disclose no location fix and0,0 fallback if applicable.
- **05-keep-stop-notes-and-contacts-useful** (/routes/stop/[id] -> /routes/stop/contact): Open stop contact and save a clearly fictional visit note; verify persisted note.
- **06-check-out-after-the-work-is-complete** (/routes/stop/[id]): Check Out an InProgress fictional stop and verify Completed/progress.
- **07-skip-with-a-reason-instead-of-hiding-a-visit** (/routes/active -> /routes/stop/[id]): Open Skip reason modal on a separate pending stop; submit a clear training reason and verify Skipped.
- **08-review-deviations-before-acknowledging-them** (/routes/history/instance/[id]): Open actual instance Deviations and any already-recorded acknowledgement badge. No acknowledgement/Pause/Resume/Cancel action is rendered.
- **09-end-the-route-and-inspect-its-history** (/routes/active -> /routes/history/[planId] -> /routes/history/instance/[id]): Inspect End Route and its actual confirmation behavior; claim ended only after real result. Open an existing legitimate historical instance for summary/stops/deviations.
- **10-inspect-what-the-selected-apparatus-carries** (/inventory): Open Inventory for Engine51 and populated compartments/serial/bulk items plus Recent counts; distinguish setup/access empty states from physical absence.
- **11-count-actual-quantities-and-save-progress** (/inventory/count/[id]): Start an independent fictional count with Adjust Inventory permission; capture serialized Present/Missing, bulk quantities, difference count and actual Save progress result.
- **12-complete-cancel-or-obtain-the-required-witness** (/inventory/count/[id]): Inspect Complete/Cancel count and real confirmation behavior on separate disposable counts; controlled-item change needs existing approved fixture and actual Awaiting witness, no web witness action claimed.

## app-unit-04-field-workspace

924 spoken words. Source SHA256: `a6a23b9bb9823f63adc901c21a9c67f9eff5ba74f45e775606b8bf0112722c38`.

- **01-follow-the-apparatus-and-control-the-map** (/): Capture legible real cartography and current unit; review named lock/unlock icons with DOM bounds and actual image review; show recenter only if genuinely offered.
- **02-inspect-pins-and-useful-map-overlays** (/): Select real incident/resource/POI pins and review actual details; enable only actual supplied route/geofence/layer overlays.
- **03-use-custom-map-layers-for-the-task** (/maps -> /maps/custom/[id]): Use a guarded local custom-map fixture with real source layer/region data; capture catalog, Layer Toggles and rendered layer changes.
- **04-find-a-building-floor-or-zone** (/maps/search -> /maps/indoor/[id]): Use an actual indoor-map/floor/zone fixture; capture floor selection, zone info and Dispatch to this zone opening the real form, explicitly verify absent/unconsumed prefill.
- **05-read-the-weather-alert-itself** (/weather-alerts -> /weather-alert/[id]): Capture Weather Alerts search/severity filters; use clearly fictional prepared alert for detail/polygon/instructions, or disclose No Weather Alerts.
- **06-coordinate-in-chat-and-verify-assistant-advice** (/chat -> /chat/[channelId] -> /chatbot): Capture actual Chat entry, recipients/group/thread/composer/attachment choices; internal fictional sends only. Assistant workspace view only, no AI provider query.
- **07-inspect-voice-streams-and-real-device-settings** (Sidebar Voice Channels -> Audio Streams -> /settings): Open actual Voice Channels and Audio Streams availability; connected-only Audio Settings/Disconnect must not be required when no approved session exists. No device permissions/provider join.
- **08-consult-the-department-s-field-references** (/contacts -> /notes -> /protocols): Open actual contact details/preplan/files/calls and department Note/Protocol HTML through Unit’s existing HtmlRenderer.web. No Responder patch assumed.
- **09-create-a-field-record-in-the-correct-context** (/records -> /records/new): Open Records catalog and contextual training form; create a clearly labelled legitimate server draft and verify actual draft reference and context.
- **10-handle-record-attachments-and-offline-states** (/records/[id]): Inspect record Attachments and supported lifecycle actions; upload only authorized training file if allowed and verify stored result. Actual local/returned/final states require their own source-supported scenario.
- **11-separate-external-orders-from-daily-operations** (/records/deployments -> /records/connectors): Open Records deployments/fills and connector readiness/run/reconciliation views; never invoke Read feed now against a real provider or expose credentials.
- **12-record-the-crew-s-deployment-day** (/operations/[id]): Open independent fictional deployment rostered to Engine51; choose a new date if crew draft already exists. Capture actual crew time form/save result, leaving signatures/approval unexercised.
- **13-capture-expenses-and-readings-without-claiming-submission** (/operations/[id]): Inspect Expenses/Usage forms and permitted fictional saved inputs only if authorized; capture actual F-42 local draft/validation failure without external submission.
- **14-set-reliable-preferences-and-verify-recovery** (/settings): Show actual settings/toggles, shared installation and logout views; no GPS/audio/notification permissions, no native background or durable-storage success claims.

## Media and platform limits

- Unit uses its own mapbox.web and HtmlRenderer.web; do not assume Responder failures or blindly copy its adapters.
- Native Alert is used for End Route and inventory completion/cancellation; actual web failure is not yet observed by this audit.
- Deselect already has a web window.confirm fallback; logout uses the existing Unit confirmation UI.
- Physical GPS/geofence/arrival, microphone/BT/PTT/push/background delivery remain untested and permission prompts must not be accepted.
- Checklist web vault is memory-only; Records offline support is definition-specific; inventory count progress uses server requests.
- Voice Audio Settings/Disconnect require an actual connected provider session, outside current no-provider authorization.

Full JSON includes source hashes, code anchors, per-scene labels and API inventory. Responder01/03 frozen hashes remain unchanged. All eight Responder/Unit lessons total 6451 spoken words.
