# Unit web Camera support snapshot

The parent applied and reviewed the retained two-file patch. The source/test snapshots reproduce the resulting actual installed Unit files; this bundle performs no application writes.

`unit-camera-options.patch` applies to the documented original source SHA22e7bf01916d7fabc5b3a44cc8010eb57c3f90ed74484481896dd01ce7359b7a and adds the colocated10-test regression. The patched source SHA is44a844c3afb90a46af5e5e56ab78871277b5c4fb27901f680f06bdf426c711fc. It omits undefined zoom/bearing/pitch from four actual Camera paths while preserving valid0 and defined values.

With existing Unit dependencies, from the Academy source repository:

```sh
node sources/demo/client-support/unit-camera/verify-camera-sdk.cjs --unit-root /path/to/Unit --source /path/to/Unit/src/components/maps/map-view.web.tsx --expect-invalid 0
ACADEMY_UNIT_ROOT=/path/to/Unit ACADEMY_CAMERA_TEST_CACHE=/private/tmp/academy-unit-camera-installed-jest node /path/to/Unit/node_modules/jest/bin/jest.js --config sources/demo/client-support/unit-camera/jest-camera.config.cjs --runInBand
```

The SDK probe and isolated regression were run against the actual installed Unit files:16 finite SDK cases and10 passing real Camera/ReactDOM tests. The normal Unit Jest setup separately references missingreact-native-permissions; no package was installed or setup edited. The focused harness executes only this web module and its installed SDK contract, with cache outside Unit.

These checks do not render cartography, exercise navigation or prove the original Nevada map is fixed. Actual browser retest and new reviewed screenshots remain required; the original failed capture021 stays retained/excluded. No native/geolocation/provider behavior changes are represented.

## CI-mode restart requirement

The recording launcher usesCI mode, which disables Metro watch/reload. A normal browser navigation alone does not rebuild changed modules. After applying an approved source patch, explicitly stop/restart only the local Unit server with `--clear`, preserving the inherited environment. KeepCI unless separately reviewed; never print or save Mapbox values. No server action is performed by these source bundles.

The post-format actual installed Camera test source is refreshed; pre-format proof/snapshots remain byte-identical under history/pre-format-20261027. Actual installed SDK Camera+real Mercator Transform/matrix checks passed20cases without constructing WebGL or a browser.
