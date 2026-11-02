# Dedicated Unit native recording

This is a local, source-only XCTest recorder for the Academy iPad session. It is
not connected to the Academy publication gates. Native PNGs are not browser
screenshots, accessibility observations are not DOM, and observed packager
responses do not prove which JavaScript bytes executed. No video is qualified
by running these helpers.

The concrete owned artifact directory is
`/Users/shawn/Documents/dev/Core/artifacts/academy-expansion-20261025/native-unit-20261028`.
The original Unit checkout, existing simulators, their data/keychains, port 8081,
the web Unit session and global source profiles are outside this recorder's
mutation scope. A different recording session requires a reviewed new session
binding and fresh destination; these helpers refuse to reuse the prior source
destination or a device present before creation.

## Source and build

`prepare_native_unit.py` reads Git objects at Unit revision
`0753b6baafbaec74617a412cd9c87fa9de899d47`, verifies the retained Unit recording-v2
patches, all eight outputs, dependency locks and selected installed SDK sources,
and prepares a fresh source tree. It excludes Git, environment and private
files. Its dependency link points to the installed local SDK source; it does
not clone, install packages, build, launch, stop servers or authenticate.

Run its read-only plan first, then the explicit prepare operation only for a
new owned destination:

```sh
python3 sources/production/native-unit/prepare_native_unit.py
python3 sources/production/native-unit/prepare_native_unit.py --prepare
python3 sources/production/native-unit/apply_ios_recording_config.py
```

The iOS-only recording configuration patch removes the unused Android
`googleServicesFile` reference from the isolated copy. No private Android file
is copied. Apply it before a future fresh native build. This session's first
installed binary preceded that patch: installed and rebuilt MachO files match,
but the embedded configuration differs only at `android.googleServicesFile`.
The explicit configuration-delta report preserves that distinction.

Build commands run through `native_build_command.py NAME -- COMMAND...` from
the owned source. It uses inherited Mapbox configuration without printing its
value, disables analytics/uploads, disables dotenv, targets the loopback
training services, scrubs command output, rejects sensitive argv and preserves
each uniquely named log/receipt. It never implicitly installs or launches an
app. The actual recorded build commands are retained in the source checkpoint.

Expo iOS prebuild used `--no-install`; CocoaPods resolution ran only in the owned
project. Its original cache lock was stale relative to the pinned package
graph. The reviewed native graph added only `react-native-passkey 3.6.2`; existing
pod versions stayed unchanged. Do not describe the two locks as identical.
No package/yarn lock or original Unit source was changed by native preparation.
Future preparation must review its native dependency delta before recording.

`add_xctest_target.rb` adds only the public-API UI test target to that generated
owned Xcode project. It uses the already installed CocoaPods Ruby/xcodeproj.
Build for the exact dedicated simulator with code signing disabled and package
updates/resolution disabled. XCTest configuration must bind the exact owned
UDID, disable parallel test destinations and set **both** attachment lifetimes
to `keepNever`. Raw `.xcresult`, build products and generated app configuration
remain private artifact/cache material; never copy them into public sources.

## Normal native interaction

`AcademyUnitDriver.swift` uses public `XCUIApplication`/`XCUIElement` interfaces.
`native_ui.py` communicates only through this independently installed test
runner's inbox. It never reads Unit app data/stores/keychain or writes backend
APIs. The host can read private fictional credentials into a transient `0600`
runner file; they never enter argv, capture metadata or public action receipts.
The runner deletes that file. Populated credential forms block screenshots and
tree inspection. No automatic screenshots or permission grants are enabled.

The native Server URL sheet must visibly target the verified training origin
before sign-in. Source `sources/demo/nginx.conf` routes the Core-origin
`/api/v4/`, `/connect/` and `/.well-known/` paths to the API with its canonical
local issuer and verified upstream TLS. The direct API port is a separate
endpoint. The session retained a read-only origin/config verification before
saving the exact loopback value through the real form.

Only the own-app location alert's **Don't Allow** action is supported; no GPS
permission, physical location, notification registration, camera, provider
delivery or attestation result is implied. The observed notification keychain
warning and initial dev-tool render error remain diagnostic history. Their
normal overlay dismissal is not a repair of notification registration.

The native inventory confirmation has a separate explicit action which accepts
only the real `Complete count?` alert with `Everything matches what was
expected.` and its normal Cancel/Complete buttons. A submitted confirmation is
not assumed successful: record actual result, fresh history and normal reopen.
Stop on stale-snapshot/backend failure; do not override, cancel or recreate to
force a successful take. Generic alert interaction and security/permission
grant actions remain denied.

The iPad supports landscape through its actual declared orientation policy.
Measured evidence is 2732×2048 raw pixels, 1366×1024 application points and DPR 2.
Do not relabel it as 1920×1080 or infer landscape from the earlier portrait
diagnostic. Existing renderers/validators need an independently reviewed native
contract and layout before this source can enter a video.

The normal local dev-client opens the owned Metro 19113. This machine's Expo
`--localhost` listener bound IPv6 while native bundle requests used IPv4.
`metro_ipv4_bridge.py` transparently relays that same loopback packager over
HTTP and WebSocket. It retains hashes/counts/timestamps only, never response
bodies, request URLs/queries, headers or frames. It neither forwards app API
writes nor substitutes app screens. A served response hash is explicitly not
authenticated client execution/load identity; lazy-chunk coverage remains a
separate review requirement. CI Metro disables watching, so source changes
require an explicit owned-server restart with `--clear`.

## Evidence and verification

Raw source is under `sources/captures/expansion/unit-native-20261028/`.
Each PNG has its own untouched native sidecar with actual simctl command,
timestamp, SHA256, dimensions and native AX observation. Pixel reviews and
action/source correspondence belong in separate reports. Do not fabricate a
browser URL, DOM, browser screenshot method or browser-playback proof.

The guard tests are synthetic and do not qualify application behavior:

```sh
python3 -m unittest discover -s sources/production/native-unit/tests -p 'test_native_helpers.py'
```

They check own/new device binding, rejection of another device's container,
stale runner binding, pending-command preservation, privacy failure before
screenshot, path/name guards and output/argv redaction. Real product outcomes
must still come from the separately reviewed native PNGs and ordinary UI ledger.
