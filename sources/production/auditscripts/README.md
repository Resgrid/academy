# Reproduce the legacy-primer audit

These tools produce source-only replacement plans. They do not generate speech,
open the browser, render videos, approve publication, import data or change app
features/security. Original narration, audio, captions and screenshots are read only.

From the Academy repository, use an existing Python3 and FFmpeg installation:

```sh
python3 sources/production/auditscripts/legacy_primer_audit.py \
  --root . --source-root /path/to/source-checkouts --ffmpeg /path/to/ffmpeg
python3 sources/production/auditscripts/validate_legacy_primer_audit.py \
  --root . --source-root /path/to/source-checkouts
```

The source-checkout directory contains named Core,Responder,Dispatch,IC and other
cited repositories. The generator reuses the stdlib JPEG/PNG header reader in
`scripts/verify_capture_evidence.py`. If `--ffmpeg` is omitted it uses an existing
FFmpeg on PATH, then the optional imageio_ffmpeg package; it downloads nothing.

`legacy-audit-inputs.json` retains portable source-route/narration research,
previous capture gaps and exact image-hash-bound visual review observations.
Narration/scene/source assumptions must still match before output is regenerated;
Changed scripts,priority source or hash-pinned priority media/cues require an explicit source/capture/cue remap.
Review timestamps are preserved: regeneration never claims a new pixel review.
Prior labels remain source suggestions until actual viewport/image proof exists.

The normalized narration checksum is named `normalised_words_sha256`. It hashes
lowercase normalized narration words, never any authentication material. Raw
narration, scene and cue checksums remain separately pinned.

The validator checks all generated legacy files, these retained sources and the
learning log with the actual unchanged `scripts/audit_public_repo.scan_stream`.
When present, ignored `sources/demo/private/credentials.json` supplies additional
known local values; the ignored SMTP scenario SmtpPassword and inherited actual Mapbox values are also checked in memory. An
alternate local JSON may be passed with `--private-values-json`. No private value
is printed, retained in the report or used as a scanner exemption. The resulting
report records the scanner hash and value/file counts. Pattern checks still run
when no local private values are available.

Generated outputs are only `sources/expansion/plans/legacy-*` and
`sources/expansion/audits/legacy-*`. Every replacement remains blocked until actual
screens, source controls/results, genuine speech anchors, strict frame validation
and separate caption-enabled browser playback qualify. The current location
priority plan documents TTL0 versus narrated60, unsupported weather controls and
the disagreement between current214.97s/72cue media and old218.84s/73cue validation.
