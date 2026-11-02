Dispatch and IC source-bound recording runtime — 2026-10-30

The existing isolated artifact copies passed their exact Records contract and prior compatibility baselines against the original app revisions and Core. New source profiles bind all1170Dispatch and1054IC source/config files. No production/Metro/native/dependency edit was needed: both real Metro web bundles compile and returnHTTP200.

Run from the existing staging repository root:
python3 -B sources/demo/client-support/app-runtime-recovery-20261030/launch-recording.py --app dispatch
python3 -B sources/demo/client-support/app-runtime-recovery-20261030/launch-recording.py --app ic

These defaults read source only. To start an absent owned server, add --launch --foreground and keep that persistent execution session open. Ports are fixed localhost19101/19104, API127.0.0.1:18967, with --clear, dotenv absent/disabled, browser launching disabled, CLI networking and analytics disabled. Existing DISPATCH_MAPBOX_PUBKEY or IC_MAPBOX_PUBKEY must be inherited; its value is never written or printed. Source drift or a busy port is refused. The helper is bound to the existing Core/artifacts/academy-expansion-20261025 layout and original app checkouts; relocation requires an explicitly reviewed path/profile update. It does not copy trees, install packages, load credentials, sign in, or operate app data.

Check actual local HTML and JS without executing browser code:
python3 -B sources/demo/client-support/app-runtime-recovery-20261030/verify-served.py --app dispatch --write-observation
python3 -B sources/demo/client-support/app-runtime-recovery-20261030/verify-served.py --app ic --write-observation

The response bodies are never saved. Only status, byte counts, hashes, module counts and sanitized compilation errors may enter ignored _reports/recording-runtime-recovery-20261030/. This is HTTP bundle readiness, not authenticated UI, map/provider, Records save/readback, native or offline success.

The local filesystem/network sandbox disallowed even Core HTTP reads; authorized persistent exec sessions were used for the actual successful launches and local HTTP checks. Initial detached sandbox launch attempts did not remain alive and are preserved as unsuccessful observations. No old helper/source profile was overwritten. Original repositories, source-control state, Academy canonical/site/target and database remain untouched.
