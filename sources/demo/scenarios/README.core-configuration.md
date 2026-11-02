# Replay the Core training configuration

[core-configuration.json](core-configuration.json) is the single public data bundle
for the saved Academy run card, response package, two workflow definitions and
nearest-response settings beyond the baseline seed. It contains fictional labels,
templates, conditions and numeric settings. It contains no authentication values,
credential ciphertext, credential identifiers or authentication hashes. Credential
contents were not read when retaining it.

The observed card and package IDs were both `1`. Those are reference information,
not IDs to impose on another installation. Resolve exact names within department 51
and let Core assign IDs and graph keys. Both workflows were disabled when retained;
the card was enabled with **Pre-populate for dispatcher review** and automatic
dispatch off. No historical calls, dispatches, executions, messages, retries or audit
rows are part of this replay.

## Prerequisites and safety boundary

Use a separate Academy recording stack created with the expansion source profile.
Its application database must be `resgrid_academy`, department 51 must be exactly
**Firehouse 51 — Training Department**, and the six seeded units and baseline Engine,
Officer, Structure Fire and Urgent catalog entries must exist. Sign in through Core
with an authorized department administrator using the locally generated baseline
credentials. Keep the application network internal and Mailpit local. No production
SMTP provider, payment connection, mobile device permission or real location is needed.

```sh
python3 sources/demo/scenarios/core_configuration.py --plan
```

The plan is offline and read-only. This scenario intentionally uses normal UI replay
instead of direct database inserts. Core owns credential encryption, graph validation,
IDs, audit metadata, tenant checks and cache invalidation. A database upsert cannot
faithfully provide those guarantees or safely decide whether an existing authored
definition is the same scenario. The helper never writes application tables or makes
an application/provider request.

Before creating anything, inspect existing definitions by exact name. If one matching
definition exists, compare its fields with the JSON and reuse it. If duplicate names
or different content exist, stop and preserve them; use a fresh isolated stack rather
than overwriting configuration or history. Normal UI creation may produce its ordinary
configuration audit entries; this bundle never manufactures operational history.

## Prepare a fresh local SMTP form

```sh
python3 sources/demo/scenarios/core_configuration.py --write-local-settings
```

This opt-in command performs only a read-only fictional-baseline check, then creates
or reuses `sources/demo/private/scenarios/core-workflow-smtp.json`. Its directory is
private and the file is mode 0600. It prints the path and status only. It generates a
fresh local value for the required **Password** field instead of extracting any saved
credential or reusing the application sign-in password. Do not capture, publish or
log that value. Existing different local settings are preserved and rejected.

Open `/User/Workflows/Credentials`, then **New Credential** (the form route is
`/User/Workflows/CredentialNew`). Use the public fields in the fixture and the generated
local Password:

| Control | Value |
| --- | --- |
| Name | Academy local captured mail |
| Type | SMTP (Email) |
| Host | mail |
| Port | 1025 |
| From Address | training@firehouse51.example |
| Username | Leave blank |
| Password | Read the generated ignored local file privately |
| Use SSL/TLS | Off |

Save through Core. This local replay profile is constructed for Compose's internal
Mailpit service. The sender matches the retained receiver evidence; saved credential
contents were never copied. The SMTP executor authenticates only when Username is
nonempty, so the generated value satisfies this form's required validation and is
not used for SMTP authentication. Saving the credential does not test a connection or
send a message. Editing an existing credential intentionally does not expose its
stored values; do not expect the edit screen's placeholders to describe saved settings.

## Response package and conditional card

1. Open `/User/RunCards/Packages`, choose **New response package**, and name it
   **Academy Initial Response**. Use the fixture description; leave Retired off.
2. Add two rows in this order. The first has a blank Label, Engine as its only target,
   **Pick** one and **Any available** status. The second is **Incident officer**, Officer
   as its only target, **Pick** one and **Any available**. Leave response codes,
   substitute packages and **Keep outstanding until sent** unset/off for both. Save,
   reopen via the package list and compare the rows.
3. Open `/User/RunCards`, choose **New Run Card**, and name it **Academy Training Alarm**.
   Keep Disabled on while assembling it. Use the fixture description, **Closest Unit
   Response**, and **Pre-populate for dispatcher review**. Leave Home station and
   minimum staffing override at department/default, Relax unfilled rows off and
   waiting-call automatic dispatch at department/default.
4. On **Triggers**, add the combined **Urgent** + **Structure Fire** trigger. Leave its
   start/end dates empty. A combined trigger requires both values; separate triggers
   would be alternatives and would not reproduce this card.
5. On **Alarm Levels**, create level 1 **Initial Response**. The current saved level has
   no fixed package, fixed unit requirements or fixed role requirements. Its decision
   graph provides the response. Create these nodes:

   | Node | Configuration |
   | --- | --- |
   | Engine within eight minutes | Condition, **Available within**, Engine subject, **Any available**, count 1, threshold 480 seconds; mark **Start** |
   | Engine available | Outcome, **Academy Initial Response**, advice `Send the initial response after review.` |
   | Review alternatives | Outcome, no package, advice `Review alternatives or mutual aid. Training exercise only.` |

   Connect the condition's **If yes** to Engine available and **If no** to Review
   alternatives. Use the names to connect Core's newly generated graph keys; do not
   paste the observed database IDs. Save and reopen to verify both branches.
6. On **Dispatchable Statuses**, leave the current default availability behavior:
   there are no stored explicit selection rows. Empty stored selections mean Core's
   default availability matrix applies, not that nobody is dispatchable. The package
   and condition status filters remain **Any available**.
7. Compare the entire saved card against the fixture, then clear Disabled and save.
   The card still only pre-populates selections for dispatcher review. Do not create
   or dispatch a call as part of this configuration replay. Its retained description
   mentions rescue capability; the actual current package asks for Engine and Officer.

The edit routes are `/User/RunCards/EditPackage?responsePackageId=<new-id>` and
`/User/RunCards/Edit?runCardId=<new-id>`. UI changes must be committed through the
control's change/blur behavior before Save; reopen to verify retained values.

## Nearest-response settings

Open `/User/Department/DispatchSettings`. Compare only the values listed under
`dispatch_settings` in the JSON and preserve every unlisted setting. Current values:

| Control | Value |
| --- | --- |
| Automatic resource selection mode | Closest Unit Response |
| Automatically dispatch recommended resources | Off |
| Scope Dispatch to Group Areas | Off; no department-wide dispatch roles selected |
| Maximum unit / personnel location age (seconds) | 1800 / 1800 |
| Maximum response radius (meters) | 0 |
| Include stale locations / Order by driving ETA | Off / Off |
| ETA shortlist size | 5 |
| In-quarters turnout (seconds) | **120** |
| Mobile / Personnel turnout (seconds) | 0 / 0 |
| Rest period / Minimum unit staffing | 0 / Off |
| Enable move-up / backfill recommendations | Off |
| Dispatch freed units to calls awaiting them | Off |
| Automatic dispatch limit (seconds, 0 = none) | 0 |

Save and reopen. No unit/person status, crew assignment or location is changed by
these settings. Turnout can affect recommendations using a station origin; station
origin is also used when a unit lacks usable GPS. A displayed station source does
not establish its physical whereabouts. The optional
`refresh_training_positions.py` is a separate explicit simulated-position scenario;
this replay never calls it.

That script defaults to an offline plan; `--help` and invalid arguments also never
contact Docker, load private configuration or write data. Run it separately only
when refreshing the three unchanged seeded officers' fictional station positions:

```bash
python3 sources/demo/scenarios/refresh_training_positions.py --plan
python3 sources/demo/scenarios/refresh_training_positions.py --write-training-fixes
```

The write requires the isolated `resgrid_academy` database and Firehouse 51 training
department, all three officers' existing training statuses, and unchanged simulated
coordinates and approved notes. It appends history using each current status type,
leaves fixes newer than two minutes untouched, and stops if a walkthrough changed
those positions or notes. It emits no application event or notification and does
not establish anyone's physical location. The actual result is retained in
`sources/demo/scenario-reports/fresh-training-positions.json`.

## One configured Engine 51 seat

The baseline defines one **Officer / Team Lead** seat for Engine 51. Its observed
control was `Role_51001`; resolve the existing seat by unit and name instead of
forcing that identifier. The seat has no required Personnel Role and Required is
false. Preserve that definition; its name alone does not enforce an Officer
qualification.

1. Open `/User/Units/UnitStaffing`. Confirm Engine 51's seat is unoccupied or already
   assigned to Christopher Herrmann. If another person occupies it, stop rather than
   replace their assignment.
2. Select **Christopher Herrmann** in that seat's personnel selector. Save. Do not
   change the other five units' seats or any status/location.
3. Reopen Unit Staffing. Engine 51 should show Herrmann and **Fully Staffed**. That
   badge means all configured seats are occupied: **one of one** here. It is not an
   assertion about a real engine's crew minimum. The other five seats were empty in
   the recording fixture; never clear unrelated assignments to manufacture that view.
4. On an unsaved New Call with a training point, inspect **Shift Coverage** and
   **Role Mix**. The observed result showed 1/1 crew on shift, **A Shift — Firehouse
   51**, Christopher Herrmann and **Officer ×1**. That role comes from Herrmann's
   personnel role, separately from the seat's unrestricted required-role setting.

The JSON also retains the near/far preview points. Place the pin at
`41.8725, -87.6524`, inspect the station-origin turnout annotation, optionally tick
Engine 51, then compare `42.5, -88.5` and selection retention. These are unsaved
form previews. Do not choose **Create and Dispatch Call**. The retained 2-minute /
195-minute results are recording observations; inspect actual current results
rather than treating them as new evidence or guarantees.

## Two disabled workflows and ordered steps

Open `/User/Workflows`, choose **New Workflow** (`/User/Workflows/New`). Create or verify
each definition below with **Enabled unchecked from the first save**. Each definition
has one event. Creating a second event is a second workflow, not a waiting step in
the first. Bind the saved local credential by its name; do not store its generated
database ID in the public fixture.

| Name | Trigger | Max Retry Count | Retry Backoff Base Seconds |
| --- | --- | --- | --- |
| Academy call opened — captured mail | CallAdded | 3 | 5 |
| Academy call closed — captured mail | CallClosed | 3 | 30 |

Use the exact descriptions in the JSON. In each editor, choose **Add Step** and
**Send Email**, select **Academy local captured mail**, and enter the fixture's
`action_config`, `output_template`, `condition_expression` and `order`. Each step is
enabled; its parent workflow remains disabled.

- The opened workflow has order 1 to `training-supervisor@firehouse51.example`, then
  order 2 to `training-audit@firehouse51.example`. The second condition is exactly
  `{{ call.name | string.contains "TRAINING" }}`. Its subject and template are retained
  verbatim in the JSON; do not substitute prose or preview output.
- The closed workflow has one order-1 email to
  `training-closeout@firehouse51.example`, with no condition. Its template uses
  `call.state_text`.

Save each step, inspect the ordered step cards, save the workflow settings and
reopen both. Verify Disabled on the workflow list. A condition syntax check or
template preview is optional validation only; it is not a send, an execution test
or evidence of a successful run. Do not enable workflows, create/close a call,
manipulate the receiver or enqueue a retry as part of this replay.

## Recorded custom call icon

The versioned image `sources/demo/marker-icons/call-fire-base.png` is a 128 × 128
transparent training PNG (SHA-256
`faf95e82e2970f1362c37091527f4b05160258a761ff0c802d00c5446cdd7ff5`).
Reproduce this narrow configuration through the ordinary UI after verifying the
fictional department identity:

1. Open Department Types, then edit **Structure Fire**. Preserve its name, class
   and built-in Map Icon selection. Custom icon is a separate setting.
2. Choose the PNG under **Custom icon**. Check its light-map, dark-map and list
   previews. The new-icon message describes an unsaved selection at this point.
3. Bring **Update** fully into view and save once. Close only completed duplicate
   training forms before doing this; never issue competing saves from several tabs.
4. Reopen the type. Confirm **Showing the current custom icon** and successfully
   loaded previews. The file input is empty after saving; that does not mean the
   stored icon is missing. The server assigns the opaque image key—do not seed or
   copy a recorded key into a new installation.
5. Open Mapping and inspect the existing **TRAINING — Warehouse alarm**. It is
   already Structure Fire with Urgent priority; leave that call's fields intact.
   Observe the saved icon on the actual map separately from the upload preview.

This sequence recovered one fictional icon after concurrent save cleanup removed
the underlying image row. It is not a production concurrency fix. The observed
facts, inferred ordering and successful single-save recovery are retained in
`sources/expansion/audits/core-marker-*20261027.json`. Unit and personnel icons,
priority/status overrides, legend matrices and removal fallback require their own
captures; this base-icon observation does not establish those outcomes.

## Verification and limits

The data bundle retains **definitions**, not outcomes. Leave all existing completed
and failed runs, step logs, calls and messages untouched. A new reproduction starts
without the recording installation's historical success/failure evidence. Authentic
new runs require separately authorized operational events and observation; never
insert synthetic successful or failed history rows.

The current worker reads global `WorkflowConfig.DefaultMaxRetryCount` and
`RetryBackoffBaseSeconds`, rather than each definition's stored fields. Keep the
closed workflow's saved 30-second value, but do not promise that it produces
30-second execution delays in this source version. No worker configuration changes
are included here.

The expansion source profile pins five application repositories and reviewed support
patches; it is not a complete database snapshot. These manually authored scenario
definitions must be replayed separately after the baseline. External providers,
native device features, timing observations and historical runs are not made
reproducible merely by copying a source profile. The staged recording installation
was inspected read-only; credential data and execution history were excluded.

```sh
python3 -m unittest discover -s scripts/tests -p test_scenario_replay.py -v
```
