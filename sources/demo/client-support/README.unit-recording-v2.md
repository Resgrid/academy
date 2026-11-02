# Unit recording support v2

V2 adds the check-in card/history UTC presentation fix to the retained camera and
web image-read fixes. It deliberately preserves the v1 module, CLIs, baseline,
README and proof checkpoints. The v2 module is a versioned copy of the reviewed
v1 guards with a new baseline, three-patch requirement, v2-only destination,
separate provenance filename and checks of the prior version's immutable files.
Diff the two modules to review that bounded guard revision.

Planning is offline/read-only and requires no credentials or managed checkout:

```bash
python3 -B sources/demo/client-support/unit-recording-prepare-v2.py --plan
python3 -B sources/demo/client-support/unit-recording-launch-v2.py --plan
```

After separately preparing the clean managed Unit checkout at pinned0753 with its
already installed lockfile dependencies, explicitly opt in:

```bash
python3 -B sources/demo/client-support/unit-recording-prepare-v2.py
python3 -B sources/demo/client-support/unit-recording-launch-v2.py
```

Default destination is `sources/demo/capture-apps/Unit-recording-v2-20261027`.
A different destination must be a fresh direct `Unit-recording-v2-*` child of
that capture directory. Existing v1/v2 copies and original source are refused;
there is no in-place upgrade, overwrite, clone or dependency install. Execution
checks clean tracked source, exact seven input hashes, three patch inputs, all
eight outputs, package/lock hashes, fourteen installed SDK source hashes, Expo
CLI identity and eight preserved v1 support/proof files. It copies tracked regular
application files only, excludes environment/private/Git/caches, links the
verified managed dependencies, and records a separate `.academy-unit-recording-v2.json`.
Launch rechecks complete provenance and refuses extra/private files or edits.

Launch inherits `UNIT_MAPBOX_PUBKEY` in memory; never blank, print or save it.
Only explicit local HTTP API origins are accepted. It never stops an existing
server, opens a browser, signs in, changes a policy or requests GPS. CI disables
Metro watching: parent-controlled source changes require an explicit restart of
the known local listener with `--clear`; this helper does not perform a kill.
Generic prepare/launch commands, global profiles and private pins stay unchanged.

```bash
python3 -B -m unittest discover -s scripts/tests -p test_unit_recording_support_v2.py
python3 -B -m unittest discover -s scripts/tests -p test_unit_recording_support.py
```

V2's13 tests use synthetic temporary source files and mocked read-only Git
metadata; no Git process/commit or live app copy is made. They include actual
retained-patch derivation of all eight approved outputs without changing inputs.
All27 existing v1 tests remain green. See [UTC fix proof](unit-check-in-time/README.md)
for the original-failing/patched-passing rendered-component tests in UTC and Los
Angeles. Source/test success does not establish real browser display or qualify
any tutorial; parent must retain fresh actual UI evidence after its normal restart.
