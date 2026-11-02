# Actual application walkthrough production

The expansion lesson JSONs are editable narration and capture plans. They are not
completed videos. `scripts/render_walkthrough.py` assembles a staged video only
after approved local natural narration, its reviewed speech-timed SRT, and real
application screenshots exist. It never requests speech generation, creates a
voice fallback, estimates cue timing, infers a screen from prose, or publishes a
lesson. If narration credits or a browser blocker prevent obtaining these
inputs, keep the affected lesson pending rather than substituting evidence.

## Inputs and capture review

Use paths relative to `--asset-root`, normally the repository's `sources/`.
Lesson and plan filenames are command arguments. Referenced audio, SRT, capture
manifests, and screenshot assets must exist inside that root with matching
SHA-256 hashes. The screenshot manifest may contain `captures` or `screenshots`.
IDs must be unambiguous across the supplied manifests.

Each selected screenshot needs this evidence from the real capture process:

```json
{
  "id": "incident-draft",
  "app": "Core",
  "kind": "application_screenshot",
  "file": "captures/expansion/core/incident-draft.jpg",
  "sha256": "<SHA-256 of the untouched JPEG>",
  "width": 1434,
  "height": 829,
  "provenance": {
    "method": "browser_screenshot",
    "url": "http://localhost:18966/User/Records/Edit/123",
    "captured_at": "<actual ISO-8601 time with timezone>"
  },
  "visible_labels": ["Incident record", "Save draft", "Draft"]
}
```

This is a schema example, not a claim that this URL or capture exists. Copy actual
capture values. Supported applications are Core, Dispatch, Responder, Unit and
IC; a screenshot's application must match the lesson's `app`. Illustrated
substitutes, excluded/blocked captures, reported missing controls, bad hashes,
missing provenance and mismatched dimensions fail validation. A real record
labeled **Draft** is a valid application state. Do not describe a draft, prepared
form, empty list or error as a saved/finalized/provider-delivered result.

Inspect each screenshot, including control text, development notices, loading
states and private fields. Record a hash-bound review in the explicit plan only
after that inspection. The renderer checks the review's presence and identity;
metadata cannot authenticate pixels or perform OCR. Required labels must be
actual legible viewport labels, not hidden DOM text, off-screen controls, or a
source-code string. If a control is unavailable, obtain the correct authorized
scenario or revise and reapprove the lesson; do not set a review flag to bypass
the gap. Never capture passwords, tokens, credential forms or real private data.

The complete screenshot is fitted without cropping in the main 1920×1080 video
area. A 48-pixel chapter header and 120-pixel caption band sit outside it; no
overlay covers application controls. Landscape captures must be at least
960×540. The fitted view must remain at least 1100×650 and must not shrink below
75% of its original pixel dimensions. Full-page/portrait captures that would
become a tiny UI inset fail. Recapture a suitable landscape viewport with
readable app text. The source JPEG/PNG is never modified; only the rendered
copy is scaled proportionally.

## Explicit speech and screen plan

Save a separate JSON plan for each lesson. The following is a structural
example only. Its placeholder hashes, paths, reviews and times must be replaced
with actual reviewed assets and speech measurements. Do not use example times
as a substitute for alignment.

```json
{
  "schema_version": 1,
  "lesson_id": "core-record-draft",
  "duration_seconds": 2.4,
  "narration": {
    "file": "expansion/audio/core-record-draft.m4a",
    "sha256": "<audio hash>",
    "kind": "approved_natural_narration",
    "approval": {
      "reviewer": "<person who listened to the whole export>",
      "reviewed_at": "<actual ISO-8601 time>",
      "sha256": "<same audio hash>",
      "complete_natural_narration": true
    }
  },
  "captions": {
    "file": "expansion/audio/core-record-draft.srt",
    "sha256": "<SRT hash>",
    "kind": "speech_timed_srt",
    "approval": {
      "reviewer": "<person who checked the speech alignment>",
      "reviewed_at": "<actual ISO-8601 time>",
      "sha256": "<same SRT hash>",
      "audio_sha256": "<same audio hash>",
      "speech_timing_reviewed": true
    }
  },
  "capture_manifests": [
    {"file": "captures/expansion/core/manifest.json", "sha256": "<manifest hash>"}
  ],
  "screenshot_reviews": {
    "incident-draft": {
      "reviewer": "<person who inspected this viewport>",
      "reviewed_at": "<actual ISO-8601 time after capture>",
      "sha256": "<same untouched screenshot hash>",
      "application_visible": true,
      "labels_legible": true,
      "no_errors": true
    }
  },
  "scenes": [
    {
      "id": "save-draft",
      "start": 0,
      "end": 2.4,
      "screens": [
        {"screenshot_id": "incident-draft", "start": 0, "end": 2.4}
      ],
      "captions": [
        {
          "cue": 1,
          "screenshot_id": "incident-draft",
          "required_labels": ["Save draft", "Draft"]
        }
      ]
    }
  ]
}
```

The corresponding authored scene would have `id: "save-draft"`,
`required_labels: ["Save draft", "Draft"]`, and narration such as
“Select Save draft to keep this incident record as a Draft.” The actual SRT cue
contains those spoken words and its measured start/end. The renderer copies
caption timing from the SRT; the plan refers to its one-based cue number.

Rules enforced before assembly:

- Every authored scene appears exactly once, in order, with complete scene and
  screenshot coverage from zero through the end of the narration. Gaps and
  overlaps greater than one millisecond fail. Silence between speech cues is
  allowed and still displays a real mapped application screenshot.
- Every SRT cue maps exactly once to a scene and screenshot that is displayed
  for its entire interval. Do not drag cues to fit screen cuts. If a cut falls
  inside a spoken cue, obtain a correctly split speech-timed export or move the
  explicit screen cut without altering the speech.
- Each scene's complete caption transcript matches its authored narration,
  ignoring case, punctuation and typographic quote differences. Missing, extra
  or changed words fail; omitted scenes cannot silently disappear. If an
  approved recording uses different wording or spoken numbers, reconcile the
  editable script and aligned transcript after listening.
- Every authored `required_labels` item is mapped to at least one actual cue
  that names that exact visible control. Labels compare case-insensitively with
  normalized whitespace. A non-instructional cue may explicitly set
  `"instructional": false, "required_labels": []`; it cannot bypass a scene's
  required UI controls. Every displayed screen interval needs a mapped cue for
  extracted-frame review.
- Cue/screen intervals shorter than two frames fail. Caption text uses at most
  three readable lines; an overlong cue fails during layout. Split it using
  actual speech alignment, never estimated timings or smaller application UI.
- Full audio is decoded before assembly. The explicit final interval must
  include all decoded speech and may extend at most one video frame past it.
  No audio is synthesized, accelerated, replaced, shortened or supplied when
  missing. The decoded voice is resampled to 48 kHz mono and encoded as AAC.

## Commands and staged outputs

Use the supplied runtime with Pillow. Supply an existing FFmpeg executable
through `--ffmpeg`; `imageio_ffmpeg.get_ffmpeg_exe()` locates the bundled binary
when run with `PYTHONPATH=/private/tmp/academy-video-runtime`. No app dependency
installation is required. An existing TrueType font can be supplied with
`--font`; otherwise Arial on macOS or DejaVu Sans on Linux is used.

```sh
python3 -B scripts/render_walkthrough.py \
  --lesson sources/expansion/lessons/LESSON.json \
  --plan sources/expansion/plans/LESSON.json \
  --asset-root sources \
  --output-dir sources/expansion/rendered/LESSON-take-01 \
  --ffmpeg /absolute/path/to/ffmpeg \
  --check
```

`--check` validates the contract and decodes the supplied audio, without creating
a video. Omit `--check` to assemble. The output directory must be new and inside
the asset root; existing exports are never replaced. Work happens in a temporary
directory and only a successful assembly is copied to the requested staging
directory. Encoding failures do not replace source assets or an earlier take.

A successful take contains:

- `LESSON.mp4`: 1920×1080, 30 fps, H264/yuv420p and AAC, burned readable captions,
  an embedded subtitle track, embedded chapters and fast-start metadata.
- `LESSON.srt`: the original speech-timed SRT bytes, unchanged;
  `LESSON.vtt`: equivalent cue text and timings in WebVTT format.
- `LESSON.chapters.json`, a full-frame `LESSON.jpg` poster, and extracted real
  video frames under `frames/` for each explicit screen interval.
- `assembly.json`: input hashes, layout coordinates, explicit timeline, output
  hashes, full-decode results, inspected output codecs/dimensions/duration, and
  `publishable: false`.
- `evidence.pending.json`: a worksheet compatible with the separate capture
  evidence validator. Extracted frames have pending visual review, no invented
  visible labels, and `application_visible: null`. Browser playback is empty.

The renderer decodes the entire MP4's video and audio, verifies its actual H264
and AAC streams and 1080p frame dimensions, checks the muxed duration, and checks
that output audio did not truncate the source. It rechecks source hashes after
rendering. These are media checks, not browser playback or proof of native
hardware/provider behavior.

## Publication remains a separate gate

Inspect the actual extracted frames at the recorded times. Verify that the full
application view, named controls and exact caption text are legible. Record
genuine `application_visible`, `visible_labels` and review observations in a
separate reviewed evidence copy; the assembler intentionally does not fill them
from the source manifest.

Serve the exact current MP4 and captions locally, then test actual advancing
browser playback at beginning, middle and end. Record each HTMLMediaElement
state, dimensions, duration, active caption, errors, screenshot and the current
video SHA-256. Old playback evidence must not be reused after reassembly. Follow
the schema in `scripts/verify_capture_evidence.py`, then run:

```sh
python3 -B scripts/verify_capture_evidence.py \
  sources/expansion/rendered/LESSON-take-01/evidence.reviewed.json \
  --asset-root sources
```

Only real, fully reviewed and validated outputs may later enter the public
site. The assembler has no build/export integration and never marks a video
publishable, even when media decoding passes. Keep source manifests, private
audio paths, plans and review worksheets out of public assets unless separately
reviewed for public release. Record native-only/provider/offline limitations in
the lesson instead of using a browser settings view as a success demonstration.

## Tests

`python3 -B -m unittest discover -s scripts/tests -p test_walkthrough_render.py`
runs synthetic fail-closed contracts without Pillow, a browser, a speech service
or FFmpeg. Set `WALKTHROUGH_TEST_FFMPEG` to a local executable and use the Pillow
runtime to additionally render and decode a one-second synthetic fixture. That
fixture remains in a temporary directory, is explicitly not real application or
narration evidence, and confirms that generated pending evidence fails the
publication validator until real review and browser proof are supplied.
