Native Unit call candidate: installed-archive verification

Run from the Academy repository:

  python3 -B sources/production/check_unit_call_lifecycle_native_archive_20261030.py

To check a separate installed sources folder:

  python3 -B sources/production/check_unit_call_lifecycle_native_archive_20261030.py --sources-root /path/to/academy/sources

This new checker needs only the retained candidate folder
expansion/plans/app-unit-call-lifecycle-native-candidate-20261030/ and the existing
Root source-review JSON alongside it. It checks the exact pinned source freeze,
55 copied assets, 23 original PNG hashes and dimensions, 23 copied native metadata
files, exact 15-paragraph / 59-sentence / 835-word continuity, visible-label/control
bindings and the existing Root review receipt. It refuses missing/tampered files,
path escapes, symlinks and undeclared archive files. It reads no old host paths,
excluded public projections, original recordings or historical recipe modules.

The original candidate, source-freeze.json and preparation recipe are preserved
unchanged. Historical regeneration through prepare_unit_call_lifecycle_native_20261030.py
--build still requires the original source archive/projection and a new destination.
Its old default verify path is also historically coupled to those inputs; use the
new archive checker for the portable installed package.

This is source-integrity validation, not a new pixel review, natural-voice listening
review, native public qualification, timed plan, rendered video or publication.
Original native profile transitions and independent Core corroboration remain
provenance; Core images are never relabeled native footage.

Guard checks:

  python3 -B -m unittest discover -s scripts/tests -p test_unit_call_lifecycle_native_archive.py
