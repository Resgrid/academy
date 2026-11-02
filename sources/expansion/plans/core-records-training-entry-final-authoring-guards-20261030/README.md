# Records lifecycle final-input authoring

This is a completed source-only authoring recipe, not a finished video or an
approval example. It retains the actual downloaded narration, the unchanged
112 raw/corrected SRT cues, twelve frozen chapters, twenty source spans,
seventeen continuous image holds, and sixteen independently reviewed images.
The final hold closes at the actual full-PCM duration, 392.9745208333333 seconds.

The genuine Root complete-map review is retained at
`../core-records-training-entry-take-01-proposed-20261029/parent-proposed-correspondence-review.json`.
Its SHA-256 is `1947d90026a948856abf8ce24e7933eef7325add900c6c9440c64a18cbc59e32`.
It is a source/cue review; it does not stand in for User hearing, encoded-image
inspection or browser playback. The actual User listening review is still pending.

From the repository root, this command reads and validates only:

```sh
python3 -B sources/production/author_core_records_training_entry_take_01_20261030.py
python3 -B -m unittest discover -s scripts/tests -p test_records_lifecycle_final_authoring.py
```

After a real full-listening response, retain that exact response in a URL-free
receipt bound to source SHA `e3df33c2315187e211c0e5c83f8ea0468c22cb549230c0cb752d736853ad9bc5`
and audio SHA `f7f1235fb74e25a008a7c53d34c6309e67feb31f42cdeab46c314d7860babdc6`.
Use the existing `../core-records-training-entry-authoring-recipe-20261030/listening-review.schema.json`.
No filled-in receipt is supplied here. A generated audio file or technical QA
cannot substitute for the actual listening response.

Explicit assembly accepts the actual receipt SHA through
`--listening-review-sha256` and the above actual Root SHA through
`--parent-timing-review-sha256`. Add `--assemble` to create one NEW package at
`../core-records-training-entry-take-01-final-inputs-20261030/`. The default hearing
receipt path is `expansion/audio/core-records-training-entry.listening-review.json`.
An alternate public source-relative receipt path can be supplied with
`--listening-review-file` and its exact hash. Private, remote, escaping and
symlinked receipt paths are rejected.

Assembly writes plan, capture-manifest copy and the unchanged checked SRT,
then runs the existing strict renderer-input validator and writes provenance.
It does not render, publish, update canonical lesson readiness, operate apps,
change target Academy files, or use Git. Existing output folders are never
replaced. Failed/partial packages must remain historical evidence and be
resolved deliberately rather than silently overwritten.

The retained historical sequence ends at the first finalized Training revision.
It must not be joined to the later amendment as if those were the same view or
current database state. Physical training, attendance, unit response and licensed
PDF export are not claimed. Rendered pixel/caption checks, actual advancing
beginning/middle/end browser playback and public evidence qualification remain
required after rendering.
