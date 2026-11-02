# Responder and separate Unit Records recording servers

This source-bound launcher uses the existing artifact-level copies:

- `artifacts/academy-expansion-20261025/capture-apps/Responder`
- `artifacts/academy-expansion-20261025/capture-apps/Unit-records`

Earlier `sources/demo/capture-apps` plan paths do not identify these copies. The
historical profiles and native Unit recording tree remain unchanged.

From the Academy repository root, these commands check without launching:

```sh
python3 -B sources/demo/client-support/records-web-runtime-20261030/launch.py --app responder
python3 -B sources/demo/client-support/records-web-runtime-20261030/launch.py --app unit-records
```

The launcher checks the retained Records preparer, original/Core contracts,
existing Responder compatibility and dependency pins, dependency symlink, and
all executable source differences. Later original test/coverage artifacts are
excluded from the runtime identity; the retained Records tests remain checked
by their exact preparer. Unknown runtime source changes fail before launch.

Add `--launch` to start the selected fixed loopback port. The helper refuses an
existing IPv4 or IPv6 listener and never stops a process. It inherits the
corresponding `RESPOND_MAPBOX_PUBKEY` or `UNIT_MAPBOX_PUBKEY` in memory, sets the
API to `http://127.0.0.1:18967`, disables dotenv/telemetry/browser opening, and
uses normal Expo development mode with `--clear`. It does not install packages,
touch a native profile, sign in, change a policy or operate app data.

Expo can bind `localhost` to `::1`; use `http://localhost:19102` for Responder and
`http://localhost:19103` for the separate Unit Records app. IPv4 refusal alone
does not prove these loopback servers are stopped. The initial recovery's
IPv4-only probe is retained in `history/`; the current helper checks both.

To check real HTML and complete JavaScript delivery without browser execution:

```sh
python3 -B sources/demo/client-support/records-web-runtime-20261030/probe.py --app both --retain-report
```

Runtime source receipts, sanitized output and HTTP response hashes go under the
ignored `_reports/recording-runtime-recovery-20261030/` directory. The probe
streams successful JavaScript to hashes only; it does not save response bodies
or print environment values. Successful delivery does not establish a signed-in
screen, map rendering, saved record, backend operation or completed lesson.
