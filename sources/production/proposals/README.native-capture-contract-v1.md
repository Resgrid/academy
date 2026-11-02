# Native capture evidence proposal v1

This is an independent, unadopted proposal. `native_capture_contract_v1.py` reads files only and always returns `proposal_only: true`, `publishable: false`, and `pixel_authenticity_proven: false`. It is not connected to the existing browser evidence validator, renderer, exporter, catalog or site. No native application or simulator has been created, installed, launched or controlled for this proposal.

The first supported scope is literal, fully visible Unit/Responder application text and application-owned native alerts on **our own new dedicated iOS simulator**. The user's already booted simulator and app sessions are excluded. Native icon names, system permission/photo picker surfaces, physical devices, real location and hardware/provider claims remain outside v1.

## Evidence shape

The module docstring describes the contract; the test factory is a complete **synthetic** shape example. It creates temporary parser fixtures only, never genuine application evidence. The CLI accepts a document and five explicit read roots:

```text
python native_capture_contract_v1.py actual-capture.json \
  --assets PUBLIC_RAW_CAPTURE_DIRECTORY \
  --app INSTALLED_SIMULATOR_APP_BUNDLE \
  --source EXACT_MANAGED_APP_SOURCE \
  --dependencies EXACT_MODULE_SOURCE_ROOT \
  --runtime PRIVATE_EXECUTED_JAVASCRIPT_EVIDENCE_DIRECTORY
```

All file references use `{file, sha256}` relative to their specified root. The installed application and runtime JavaScript roots must be outside public screenshot assets. A development JS bundle can contain execution configuration and secrets; retain it privately for hashing, never in the learner source/public screenshot folder.

| Field | Required binding |
| --- | --- |
| `schema`, `app`, `kind` | Exact proposal version; Unit or Responder; `application_screenshot` |
| `session` | New session and simulator UUIDs, device type, matching runtime/OS, creation time, dedicated training ownership, no reused user session; hash-bound real `simctl create` receipt |
| `build` | Actual installed Mach-O and Info.plist bytes/bundle ID, app package and native dependency lock, mapped screen source hashes, module source hashes, exact executed JS bytes; separately reviewed binary/source/runtime correspondence digest |
| `ui_ledger` | Hashed JSON containing same session/device/bundle, ordered timestamped normal UI actions and last actual screen observation; explicit no hidden writes, attestation bypass, state/keychain reset, automatic permission grant, launch hook or hardware claim |
| `capture` | `method: ios_simulator_screenshot`, unchanged raw PNG/hash/full dimensions, started/captured/finished timestamps, exact explicit-device `simctl io UUID screenshot --type=png file` invocation and exit/result hash, recent foreground app/app-alert observation, literal labels, required labels, mapped source paths |
| `review` | Named actual reviewer/time and canonical metadata digest; passed full-image, unmodified, literal-label, unobscured-control, normal-UI and identity reviews; no blocking error |

The final UI ledger action must be `observe_screen`, within thirty seconds of the capture; the foreground observation must be within five seconds. Screenshot invocation timestamps must contain the capture time and span at most fifteen seconds. Timezones are mandatory; future/reordered observations are rejected. These bounds describe evidence freshness, not invented cue times.

Capture labels must come from actual pixels. UI ledger targets are actual control labels, not typed data. Credential entry can be recorded only as `sensitive_typing_redacted` with no typed value; no credential values belong in screenshots or logs. `capture_review`-style assertions do not authenticate pixels, execution or a claimed result: a responsible actual review is still required. A stored result must be freshly read through ordinary UI; a successful command or a prepared form is insufficient.

`review_digest(document)` and `build_digest(build)` only calculate identity digests. They never create a passed review. Changing source/binary/runtime, labels, device, timestamps or action ledger invalidates existing review identity. The validator never executes commands or calls an API. Browser URLs/DOM/`browser_screenshot`, illustrated substitutes, injected-state/API action kinds, missing assets, path escapes and stale metadata fail closed. A legitimate `Draft` label is allowed.

## Ordinary native UI control path, researched only

1. Start with human interaction in a new dedicated Simulator session, or a separately approved XCTest UI runner targeting that simulator. Apple's [XCUIApplication](https://developer.apple.com/documentation/xcuiautomation/xcuiapplication) exposes app interaction/state and [XCUIScreenshot](https://developer.apple.com/documentation/xcuiautomation/xcuiscreenshot) exposes UI screenshot data. No Unit UI-test target exists today, so a runner would be a separate setup task. A new simulator and any install/launch require an intentional later action.
2. Appium is an alternative when a separate UI driver is approved. Its [official installation guide](https://github.com/appium/appium-xcuitest-driver/blob/master/docs/getting-started/installation.md) uses `appium driver install xcuitest`; the [current requirements](https://github.com/appium/appium-xcuitest-driver/blob/master/docs/getting-started/system-requirements.md) map driver/WDA support to Xcode/iOS. Select and retain reviewed versions rather than assuming any latest build works. Installing the driver also introduces WebDriverAgent setup; nothing has been installed here.
3. For a local Appium session, target the **explicit dedicated UDID**, native XCUITest and expected app bundle. Require `noReset: true`, `fullReset: false`, `autoLaunch: false`, `forceAppLaunch: false`, `shouldTerminateApp: false`, `autoAcceptAlerts: false`, `autoDismissAlerts: false`, `isHeadless: false`, and no permission preset, launch-argument injection, SSL override, shell feature, location override or page-source-on-failure logging. Driver setup can still install/launch WDA and must be reviewed separately. Use ordinary accessibility element interactions; retain the normal UI ledger. These options are documented in the [XCUITest capabilities reference](https://appium.github.io/appium-xcuitest-driver/latest/reference/capabilities/).
4. Maestro is another option, but its [CLI installation](https://docs.maestro.dev/maestro-cli/how-to-install-maestro-cli) requires Java17+ and documents a Homebrew route. No installation is performed. Its [device selection](https://docs.maestro.dev/maestro-flows/flow-control-and-logic/specify-and-start-devices) supports an explicit `--device UUID` before `test`; never rely on default device selection. Its [launchApp defaults](https://docs.maestro.dev/reference/commands-available/launchapp) stop the app and allow permissions, while optional `clearKeychain` clears the iOS keychain. Stock quickstart flows are unsuitable here. Begin with the dedicated app already opened normally; omit launch/reset/permission commands entirely. A future flow needs separate inspection before execution.

No driver command in this document has been run. Do not use native UI as an account/MFA/access workaround. Actual device permissions, signatures, safety attestations and provider operations retain their original restrictions.

## Validation and adoption boundary

Run the independent synthetic tests, without browser, simulator, ffmpeg, Pillow, network or Git:

```text
python -B -m unittest discover -s sources/production/proposals/tests -p test_native_capture_contract_v1.py -v
```

Before adoption, review the contract and capture a genuine new dedicated-session sample; independently review raw pixels/normal UI/identity and exercise failure cases. Any adapter into lesson rendering must preserve native provenance rather than manufacture a URL or DOM. The existing full-speech, exact cue/screen/control mapping, raw source hashing, rendered-frame review and actual browser video-playback gates remain separate. This proposal changes none of them and qualifies no video.
