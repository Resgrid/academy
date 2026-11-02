# Opt-in Unit recording helpers

These independent helpers prepare the reviewed Unit Camera and Call Images repairs without changing normal `prepare_apps.py`, source profiles, installation pins, original checkouts, or existing capture copies.

First prepare the managed Unit checkout and its pinned dependencies:

```sh
python3 scripts/prepare_apps.py --source-profile expansion --app Unit --install-deps
```

This provides `sources/demo/checkout-expansion/Unit` at clean pinned HEAD `0753b6baafbaec74617a412cd9c87fa9de899d47`. The recording helpers reuse that checkout without cloning or installing anything. A working checkout with local edits is not an eligible input.

From the Academy repository, inspect a plan before execution:

```sh
python3 sources/demo/client-support/unit-recording-prepare.py --plan
python3 sources/demo/client-support/unit-recording-prepare.py
python3 sources/demo/client-support/unit-recording-launch.py --plan
python3 sources/demo/client-support/unit-recording-launch.py --port 19103 --api-origin http://127.0.0.1:18967
```

`--plan` is offline and read-only: no Git/process execution, source copy, credential requirement, environment-value output, or profile write. The default fresh destination is `sources/demo/capture-apps/Unit-recording-20261027`. To retain another take, pass the same `--destination sources/demo/capture-apps/Unit-recording-<version>` to both helpers. Existing destinations are always preserved; even an empty existing directory is refused by preparation.

Execution checks the exact baseline, two formatted patch hashes, three original file hashes, absence of the new Camera test, package/lock hashes, and ten installed SDK source hashes. It copies only clean Git-tracked regular application files, excluding environment/private data, Git metadata, caches and dependencies. Both patches must apply at their exact line/context positions and yield all four approved output hashes. The copy links only the verified managed dependencies. Complete source/support/dependency provenance is required before launch; unknown edits, extra files, altered links, SDK changes and incomplete preparation are rejected.

The launcher requires the already inherited `UNIT_MAPBOX_PUBKEY`; never put its value in a command, document or environment file. The value is passed only in memory and never printed or saved. The API origin must be explicit HTTP loopback with a nonprivileged port. Analytics and Expo environment-file loading are disabled, normal app validation/auth remains, and the launcher starts normal Expo web development with `--localhost --clear`. It never kills a listener, opens a browser, changes auth/GPS permissions, or reseeds a database. Choose an unused port or explicitly stop only the intended existing local Unit server first.

**CI mode disables Metro watch/reload.** After any reviewed source/support revision, prepare a fresh version and explicitly stop/restart only the intended local Unit server. A browser navigation alone does not rebuild cached modules. The helpers retain CI and never silently change other running apps.

Guard tests:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/tests -p test_unit_recording_support.py -v
```

Tests use temporary fixtures and mocked read-only Git metadata; they never initialize or commit a repository, execute a Git command, copy a live app, start Expo, or access a browser. They additionally apply the actual retained patches to retained baseline files in a temporary fixture and verify every approved output hash.

Source preparation and offline tests do not prove an isolated Expo boot, correct rendered cartography, image persistence, native hardware, provider delivery, or a publishable lesson. Verify the required operations through the normal app interface before using the resulting captures in a lesson. Historical failures and the previous 45-file source/proof checkpoint remain unchanged.
