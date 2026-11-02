Guarded Billing and Shifts take02 authoring

Default reads and verifies retained inputs only:
python3 -B sources/production/author_core_billing_shifts_take_02_20261030.py

Run source-only guard tests:
python3 -B -m unittest discover -s sources/production/tests -p 'test_core_billing_shifts_take_02_authoring_guards.py' -v

After the real User has approved the full matching narration, Root records the
actual URL-free review at the default source-relative receipt file named in
listening-receipt-contracts.json. No approval sample is supplied. The receipt's
SHA256 must be passed explicitly. An alternate public source-relative receipt
can be chosen with --listening-review-file.

Future authorized Billing assembly:
python3 -B sources/production/author_core_billing_shifts_take_02_20261030.py --lesson billing --assemble --listening-review-sha256 <ACTUAL_USER_RECEIPT_SHA256>

Future authorized Shifts assembly:
python3 -B sources/production/author_core_billing_shifts_take_02_20261030.py --lesson shifts --assemble --listening-review-sha256 <ACTUAL_USER_RECEIPT_SHA256>

Each command creates only its absent named take02-final-inputs-20261030 folder,
then runs the pinned strict renderer input validator. It does not encode video.
The code refuses mismatched receipts, absent reviews, modified source/audio/QA,
changed accepted cuts, or an existing output. No default imports a renderer,
Pillow or NumPy; optional media dependencies are needed only for later explicit
assembly validation/rendering. Renderer and evidence-validator hashes are fixed.

No assembly or renderer execution was performed when this guard package was
prepared. All proposed/frozen/canonical source, audio and raw data are preserved.
Actual frames, browser playback, qualification and publication are separate later
steps. User full listening remains required for each actual narration.
