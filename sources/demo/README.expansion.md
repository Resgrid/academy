# Reproduce the expansion source profile

Run these commands from a separate, disposable Academy repository checkout. The
expansion source set records the source used for the 25 expansion lesson drafts:

| Repository | Pinned HEAD |
| --- | --- |
| Core | `6f83872110b0382f2911d099e95d6a4ef7da8315` |
| Dispatch | `044b1d88b2ce7fc851a7d0b60b94db072f51ebc9` |
| Responder | `0760a098e78871a6ce193a328f28926fad123e3b` |
| Unit | `0753b6baafbaec74617a412cd9c87fa9de899d47` |
| IC | `39e2b7ecebc2829967a68b8111271d673bebdd70` |

[source-profiles.json](source-profiles.json) pins the expansion evidence manifest,
support scripts, patch files, package manifests and Yarn locks by SHA256.
[source-manifest.json](../evidence/expansion/source-manifest.json) retains 453 cited
source files and both original and snapshot hashes. Three credential-shaped example
literals in one source snapshot are redacted; original-file hashes remain recorded.
These selected files are evidence. Building requires the full pinned repositories.
The public recipes acquire those repositories from their recorded GitHub origins.

The Core workflow settings fix is an additional retained working-tree change. Review
[its patch and application instructions](core-support/README.workflow-edit-validation.md)
before setup. The profile verifies both affected file hashes. It applies the patch
automatically only in its managed isolated Core checkout. Unknown or mixed changes
stop setup. A supplied `--core` checkout must already contain the exact reviewed fix;
setup does not patch an original development checkout.

## Inspect and start the stack

Install Python 3.10+, Git, OpenSSL, the .NET 9 SDK and Docker with Compose 2.33.1+.
The current recipe builds net9 applications and uses net9 application containers.
Host tests require a compatible .NET runtime. On the recording machine only .NET 10
was installed; the workflow tests ran with host runtime roll-forward. Actual workflow
enable/save was separately exercised in the net9 web container. The profile does not
change global SDK selection or runtime settings.

```sh
python3 scripts/setup_demo.py --source-profile expansion --plan
python3 scripts/setup_demo.py --source-profile expansion
python3 sources/demo/manage.py plan
python3 sources/demo/manage.py health
```

A fresh expansion profile uses `resgrid-academy-expansion` and web port `18967`.
Its direct API/eventing ports are `18968`/`18969`, Mailpit is `18126`, and RabbitMQ
management is `15774`. All listeners are loopback-only. Use a different profile name
and `--web-port` together when those ports are occupied. Existing `private/stack.json`
always wins unless matching explicit values are supplied; setup refuses a conflict.

The managed Core checkout is `sources/demo/checkout-expansion/Core/`. Setup records
its selected source set in ignored `private/source-profile.json`, separately from
the unchanged stack schema. Rerunning reuses the selected profile. A later request
for a different source profile or a changed profile definition stops and preserves
existing state; use another disposable Academy checkout for that source set.

The default without a saved selection is still `legacy`, using the original
`sources/evidence/source-manifest.json`, profile `resgrid-academy-capture` and port
`18867`. The existing 24-primer evidence and source manifest are unchanged. No
existing installation is automatically converted to expansion.

Credentials and private certificates are generated locally. Sign in as **boden**
with `demo_password` from `sources/demo/private/credentials.json`. Do not put that
file or environment values into captures, public documentation or source control.
Setup preserves existing databases, department 51, operational history and counters;
the fictional baseline is seeded only when department 51 is absent.

## Prepare and launch the four clients

Install a Node.js version compatible with these pinned Expo apps, plus Corepack or
Yarn **1.22.22**, `rsync` and the `patch` utility. The retained package and lock
hashes are verified before preparation. Dependency installation uses a frozen Yarn
lock and is allowed only in the managed isolated app clones. It requires package
registry access; the repository does not bundle `node_modules` or Node itself.

```sh
python3 scripts/prepare_apps.py --source-profile expansion --plan
python3 scripts/prepare_apps.py --source-profile expansion --install-deps
python3 scripts/launch_app.py --source-profile expansion --app Dispatch --plan
python3 scripts/launch_app.py --source-profile expansion --app Dispatch
```

Run each desired app in its own terminal, using `--app Responder`, `--app Unit` or
`--app IC`. Default web ports are Dispatch `19101`, Responder `19102`, Unit `19103`
and IC `19104`; override with `--port` if needed. The launcher reads the saved Core
web port, or defaults to `18967` for a fresh expansion profile. `--web-port` can
explicitly select another local recording stack.

Before an actual launch, provide the app's public Mapbox variable in your local
environment: `DISPATCH_MAPBOX_PUBKEY`, `RESPOND_MAPBOX_PUBKEY`, `UNIT_MAPBOX_PUBKEY`
or `IC_MAPBOX_PUBKEY`. The launcher inherits the value without printing or saving it.
Plans do not inspect these values and need no credentials. Environment-file loading,
analytics and Sentry are disabled for these launches; the API points to local
`/api/v4`. Expo runs in normal development mode with a cleared Metro cache and
does not open a browser. A Metro development launch with `--no-dev --minify` omitted
the apps' NativeWind stylesheet during actual recording, so these recipes preserve
the normal development CSS loader. Installed Expo modules still require a supported
browser and any appropriate human browser permissions.

Dispatch and Unit run directly from their clean managed isolated clones. Responder
and IC prepare fresh copies under `sources/demo/capture-apps/`, apply their retained
web recording compatibility patches and link to verified source dependencies. The
preparers exclude environment files, Git metadata, private folders, keys, builds and
caches. They verify original source hashes after applying patches to the copies.
Repeated preparation verifies an existing copy; it never overwrites unknown edits.
`private/client-paths.json` records only local paths and source profile hashes.

Unit’s optional web Camera and Call Images repairs have a separate [opt-in recording recipe](client-support/README.unit-recording.md). Its exact-hash preparer uses a fresh versioned copy of the clean pinned managed source; the independent launcher preserves the generic defaults, global profile definition and private pins. CI mode requires an explicit server restart with `--clear` after reviewed source changes. These source checks do not replace actual browser verification.

For new check-in recordings, use [Unit recording support v2](client-support/README.unit-recording-v2.md). It adds the UTC timestamp presentation correction to the two web repairs, uses a fresh destination, and preserves the original recipe and proof files. The card and history were checked through the normal Unit interface after a fresh bundle; the fictional personnel check-in and its note were also verified in Core. Runtime logs and editor links remain private.

Responder's patch covers web HTML rendering, the call-menu web event, Metro linked
dependencies, the Calendar detail query expected by the pinned Core API, the existing
logout confirmation dialog on web, and forwarding source-defined map load/camera
events and department camera defaults. The seven modified files and eight read-only
SDK source files are pinned separately. Preparation and launch verification check
those SDK hashes; the web verifier also runs `responder-verify-map.cjs`.
The map adapter preserves the actual Mapbox component, markers and styles. Its
offline checks and Metro compilation passed; browser cartography remains unverified.
IC's
patch covers web Text DOM props, source-defined camera defaults and Metro linked
dependencies. These are recording support changes, not evidence of native camera,
background GPS, push, PTT, real-time negotiation or external provider success.
The client baseline JSON files pin each original and modified file separately.
If an agent or a person updates a support patch, deliberately review and refresh its
baseline and `source-profiles.json` hashes in a separate reproduction checkout.

For an existing read-only dependency installation, prepare a single supported app
copy with `--app Responder --source /absolute/path/to/Responder` (or IC), without
`--install-deps`. Its source HEAD and cited files must exactly match the pinned set.
The launch destination must be isolated. An original development checkout is never
a valid expansion launch destination.

## Optional scenario actions

The [public Core configuration fixture and replay guide](scenarios/README.core-configuration.md)
retain the current conditional run card, response package, both disabled workflow
definitions and 120-second station turnout. All nonsecret authored values are in
one JSON bundle. Its opt-in helper generates ignored local SMTP form values only;
definitions are replayed through the normal UI, without execution history or sends.

The source profile reproduces application code and the clean fictional baseline.
Later operational states still require the documented UI actions in the expansion
lesson drafts and capture provenance. Setup does not silently replay operations,
send messages, grant provider access, close calls, reset sequences or refresh positions.

For the contact-administration recording, the
[retained contact fixture](../expansion/plans/core-contacts-administration-candidate-20261028/scenario.json)
contains the fictional category, person, organization, reserved contact channels,
coordinates, address and exact phone update. Search existing names before creating
anything; resolve returned IDs through the UI and preserve baseline contacts.

The [Unit deployment-review fixture](scenarios/unit-deployment-draft-review.json)
records the exact note-only exercise and its replay guards. It reuses an existing
editable training draft, preserves all hours, and reopens the saved note. Recorded
dates and report numbers are historical observations, not values to force into a
new database. Neither fixture silently submits reports, signs work or sends messages.

If overnight fixture positions have become stale and the nearest-person lesson
specifically needs fresh simulated station fixes, review and explicitly run:

```sh
python3 sources/demo/scenarios/refresh_training_positions.py
```

This optional script requires the isolated `resgrid_academy` database, the fictional
Firehouse 51 training department and all three seeded officers. It checks their latest
coordinate and note, preserves their status types and history, and appends simulated
position logs only when the previous fix is older than two minutes. A changed officer
state stops the action. It emits no event or notification and never reads device GPS.
It is not part of setup, seeding, client preparation or launch.

## Verification and current limits

```sh
python3 -m unittest discover -s scripts/tests -p test_demo_setup.py -v
python3 -m unittest discover -s scripts/tests -p test_source_profiles.py -v
```

The offline tests cover legacy defaults, all retained snapshot hashes, support-file
tampering, source-profile conflicts, no-write/no-process plans, protection of unknown
edits, isolation of patching and dependency installs, and planning without Docker.
The actual recording stack already exercised the current Core workflow fix. A new
full clone/build/install/start cycle for these integrated profile commands has not
been run. It needs network access and the tools above. Browser captures remain a
separate step; browser permission failures must be resolved by the human operator.
No source profile enables production provider credentials or proves remote delivery.

Read-only verification of the recording machine's existing Responder and IC capture
copies passed against every cited file and declared compatibility override. Their
original repositories were clean. The original Core development checkout contains
an unrelated pre-existing tracked `MEMORY.md` edit, so it correctly fails the clean
source guard. The integrated recipes did not modify or discard that edit; use the
managed expansion clone.
