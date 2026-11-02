# Unit Records staffing integration proposal

This package is a **proposed source change only**. It does not apply a patch, rebuild a server, alter a session, change department data, or modify the Unit recording application. The running server has not been demonstrated with this proposal. No authentication values or credentials were inspected.

## Why the current catalog can refuse a genuinely staffed member

The isolated Unit Records client sends its selected `UnitId` and optional `CallId` in `Context`, and sends `OriginClient = Unit`, in the normal Records request body. Core's controller accepts those fields and computes the caller and department from the authenticated request. There is no separate Unit-staffing header missing from this path.

`FieldRecordsService.VerifyContextAsync` verifies a same-department unit and then requires the caller in the latest saved `UnitState.Roles`. `RecordWorkAssignmentsService.IsStaffedOnUnitAsync` uses the same saved-state authority. But `UnitsService.GetLastUnitStateByUnitIdAsync` currently returns the repository result without loading its `Roles` collection. The actual Dapper projection maps only `UnitState` and `Unit`; both SQL dialects select only `us.*, u.*`. Existing catalog tests mock a preloaded collection, so they do not exercise this integration gap.

Selecting an apparatus in Settings is not crew staffing. The parent recording task reports Ambulance 61 with zero of one seats filled. That is separate from this integration issue. This source review did not inspect live session state or database rows.

## Proposed behavior

1. `UnitsService.GetLastUnitStateByUnitIdAsync` loads the crew rows for **only the exact returned persisted `UnitStateId`**, using the existing `IUnitStateRoleRepository.GetRolesForUnitStatesAsync`. It discards null rows and rows for another state. A missing state, missing crew collection, or failed read never provides positive staffing evidence.
2. The Unit-origin Records catalog refuses soft-deleted apparatus. Other clients' existing historical unit-reference behavior is preserved.
3. Records assignment staffing refuses soft-deleted apparatus too.

The proposal preserves the documented latest-saved-state staffing contract and all existing membership, unit ownership, call access, origin, flag, permission, version, definition-surface and capability gates. It does not create a caller, seat, status, record, claim, or grant. It adds no service dependency or registration.

Do **not** substitute `GetCurrentRolesForUnitAsync` for the exact lookup. Its SQL returns roles from every unit status in the previous two days, so an older seat could authorize someone who left the crew. `GetActiveRolesForUnitAsync` is the current editable crew assignment, but switching Records to that authority would be a separate contract change. This proposal does not do so.

## Legitimate recording sequence after review and a separate deployment

Use the normal Unit interface to assign the signed-in fictional member to an eligible apparatus seat and save it. The normal controller checks unit ownership, current department membership and required qualifications. Preserve other crew assignments. Refresh the crew display and confirm the actual saved member.

Then submit a deliberate normal training status containing that crew. The Unit status sheet sends the saved role assignments and Core persists them as `UnitStateRole` rows tied to the newly saved status. A crew-picker save alone writes `UnitActiveRoles`; it does not create the saved-state evidence required by the current Records contract. Consider the department's personnel-status propagation, call attribution and close-call settings before this normal operational action. Do not change unrelated selections or create a status merely by a direct database/API workaround.

Refresh Records through its normal interface. Verify the actual catalog, definition and create result before recording a successful walkthrough. A stale or unauthorized active call can independently fail context verification and must be resolved through normal app controls.

For a custom Unit definition, the published client surface must enable **Unit** and include launch context **unit**. `FieldRecordContext.Kind` gives `UnitId` precedence over `CallId`, so this remains `unit` even when the selected apparatus also has an active call.

IC has a different empty-catalog case: its locked Run starter accepts `call` or `command`, while its Records home without incident context is `none`. A Responder-only published custom definition is not eligible for IC. A legitimate IC walkthrough needs an actual eligible incident context or a separately reviewed and normally published IC-enabled definition with the matching launch context. This package does not alter definitions.

## Review and verification

`before/` contains exact original source snapshots; `after/` contains the three proposed production files and one new regression test file. `unit-records-staffing.proposed.patch` includes all four changes. `proposal-source-identities.json` pins the snapshots and patch. Compare the intended disposable checkout to those exact before hashes before considering application. Original source and old native Unit profiles must remain unchanged.

The isolated harness compiled the **full** three proposed service files against existing built model/dependency assemblies, with no project references and no server rebuild. All fourteen NUnit test methods and assertions passed. Running the same tests with the unchanged three before files produced five expected regression failures. The actual small test invoker is retained as `proofs/actual-harness-program.cs.txt`; it creates a fresh fixture for each actual NUnit test and awaits its result. See `proofs/proposed-results.json`, `proofs/unchanged-before-results.json` and `proofs/verification.json` for exact evidence and limits. These are repository-boundary tests, not a database, HTTP, authorization-login or browser success claim.

The new tests can be reviewed and used in a compatible disposable full Core checkout through the existing test project:

```sh
dotnet test Tests/Resgrid.Tests/Resgrid.Tests.csproj --filter FullyQualifiedName~FieldRecordUnitStaffingIntegrationTests
```

This was not run against the original full solution; the isolated harness kept all original projects and server outputs untouched. The shared `UnitsService` lookup would perform one extra exact-state crew query for **every caller that finds a saved status**, including callers outside Records. That is a broader read-cost impact than a narrow Records-only lookup or a new explicit service method. Root must compare those alternatives and review the affected consumers before any application or deployment. This package does not expand the proposal to those alternatives. No broad recent-history fallback or cached staffing grant is introduced.

Passing tests do not convert the currently reported zero-of-one-seat demo into an authorized crew. Even after a correct implementation is separately reviewed and deployed, that member must have legitimate latest-saved-state staffing evidence. The positive test supplies a matching persisted seat; the unassigned and active-picker-only tests continue to refuse access.

Root owns any subsequent review, application in the isolated recording Core checkout, full-stack verification and normal UI exercise. No application, deployment or successful live catalog is asserted here.
