# Local recording stack

This folder contains the public recipes and fictional Firehouse 51 fixtures used for
Resgrid Academy. It includes the schema metadata, seed generator, Compose services,
local billing fixture, gateway configuration and pinned supplemental assets. Generated
credentials, certificates, seed SQL, application builds and databases stay local.

## Start a recording environment

Install Python 3.10+, Git, the .NET 9 SDK, OpenSSL and Docker with Compose 2.33.1 or
later. The Compose version supports the gateway network priority used here; see the
[Docker service reference](https://docs.docker.com/reference/compose-file/services/#gw_priority).
Start Docker before setup. Commands below run from the Academy repository root.

Review the setup steps without changing anything:

```sh
python3 scripts/setup_demo.py --plan
```

Create the stack using a complete existing Resgrid checkout:

```sh
python3 scripts/setup_demo.py --core ../Core
```

Or run `python3 scripts/setup_demo.py` to acquire the recorded Resgrid/Core revision
under the ignored `sources/demo/checkout/` folder. This requires network access for
Git, NuGet and container downloads. The application snapshot cited by the tutorials
may include additional working-tree changes; pass `--core` with that checkout when
those exact application changes are required.

Setup restores and publishes the web app, API, eventing, worker and migration console.
It generates fresh credentials and local API/OIDC certificates, creates the supporting
databases, runs migrations, inserts the baseline once, reserves custom status IDs above
the built-in range, starts services and checks health.

The default profile is **resgrid-academy-capture**, with these loopback addresses:

| Service | Address |
| --- | --- |
| Resgrid web and proxied API | `http://127.0.0.1:18867/` |
| Direct API gateway | `http://127.0.0.1:18868/` |
| Eventing gateway | `http://127.0.0.1:18869/` |
| Captured test mail | `http://127.0.0.1:18026/` |
| RabbitMQ management | `http://127.0.0.1:15674/` |

Sign in as **boden** using the generated `demo_password` in
`sources/demo/private/credentials.json`. Each installation has a new password.
That file and `.env` are ignored by Git. Do not copy them into public files or captures.

To choose different ports or an additional profile on a separate Academy checkout:
`python3 scripts/setup_demo.py --name resgrid-academy-recording2 --web-port 18967`.
All five ports move together. The original `resgrid-academy` profile is reserved, so
this command does not address the existing 18767 demo.

## Preserve the recording department

Rerunning setup resumes this profile and skips seeding an existing Firehouse 51 department.
The SQL seed also independently rejects any database other than `resgrid_academy` and
refuses to overwrite department 51. Existing Docker storage without its original local
credentials stops setup. Keep `private/` with the local installation so it can reconnect.

```sh
python3 sources/demo/manage.py status
python3 sources/demo/manage.py health
python3 sources/demo/manage.py stop
python3 sources/demo/manage.py start
```

`stop` stops this profile's applications while retaining storage and infrastructure.
Before rebuilding an existing profile, stop its applications; rerun setup to apply the
new application build and resume. The scripts do not delete volumes, reset databases,
change global Docker settings or install certificate trust on the host. Build and
migration logs are in ignored `sources/demo/logs/`. A failed setup can be rerun after
correcting the error; review these logs and `validation.json` first.

The application network is internal; only loopback gateway ports are exposed. Broadcasts
are suppressed, test mail goes to Mailpit, and billing uses the local fixture. The
feature overrides are for tutorial exploration. Provider delivery, mobile OIDC over
local HTTP, AI calls, voice dispatch, financial transactions and regulatory submissions
are not demonstrated as functioning external integrations.

## Fixtures and recording workflow

Edit `fixtures.json` before the first seed to change fictional names, units, calls,
training and supplies. `seed.py` derives related roles, stations, assignments, schedules,
certifications, contacts, checklists and work orders, and checks values against
`schema.json`. Fixture identifiers and dates are for a local training database.

To reproduce later screen states, replay the actions described in
`../deep-dive/lessons/*.json` and `../captures/firehouse51/workflow-evidence.json`.
They include saved status policies, dispatch changes, stock initialization, Records
activation, completed checklists and operational deployments. The seed preserves a clean
starting point, so configuration lessons can show both the initial and saved state.
Capture the normal browser viewport and store the screenshots and associated evidence
in `sources/captures/`; follow [AUTHORING.md](../../AUTHORING.md) to rebuild a lesson.

The setup plan, credential generation, schema-checked seed generation and existing-data
guards are tested offline. A newly created full stack still needs a live setup and browser
sign-in check on the machine used for recording. The original production stack was used
for the existing captures; this new profile is independent.
