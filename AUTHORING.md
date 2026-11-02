# Updating Resgrid Academy

Academy is the editable production repository. `sources/` holds the course inputs;
`site/` is the generated GitHub Pages website. Run these commands from the repository root.
The Pages action builds from the checked-in sources and uploads only `site/`.

## Where to edit

| Material | Source |
| --- | --- |
| Primer titles, on-screen text, narration and chapters | `sources/course.json` |
| 173 feature recording briefs and five-sector examples | `sources/course.json` and `sources/scripts/feature-*.txt` |
| Department settings reference content | `sources/course.json` (`settings`), with `sources/settings.csv` retained for authoring |
| 30 detailed configuration plans | `sources/deep-dive/course.json` |
| Seven captured lesson scripts, screen order and results | `sources/deep-dive/lessons/*.json` |
| App and configuration walkthrough narration, audience and practice | `sources/expansion/lessons/*.json` |
| Actual-screen assembly plans, narration checks and reviewed masters | `sources/expansion/plans/`, `audio/`, and `rendered/`; see [the production guide](sources/expansion/README.md) |
| Current app source snapshots and recording support | `sources/evidence/expansion/` and [the reproduction guide](sources/demo/README.expansion.md) |
| Recreate the demonstrated card, workflows, turnout and crew | [Configuration fixture and UI replay](sources/demo/scenarios/README.core-configuration.md) |
| Original screenshots and capture evidence | `sources/captures/firehouse51/`, `sources/captures/deep-dive/`, and `sources/captures/expansion/` |
| Intro narration and guided-cut screen timeline | `sources/captures/firehouse51/narration-script.json`, `storyboard.json`, and `firehouse51-walkthrough.chapters.json` |
| Illustrated slides and narration direction | `sources/production/descript/slides/`, `voice-direction.json`, and the edit briefs |
| Primer narration and raw speech timing | `sources/production/descript/natural/audio/` and `natural/captions/` |
| Detailed narration and raw speech timing | `sources/deep-dive/audio/` and `sources/deep-dive/*-raw.srt` |
| Current finished videos, captions and posters | `sources/media/`, `sources/deep-dive/media/`, `sources/expansion/rendered/`, and the intro capture folder |
| Application source cited by the lessons | `sources/evidence/resgrid/`, with hashes in `sources/evidence/source-manifest.json` |
| Fictional department fixtures and stack recipes | `sources/demo/` |
| Public website layouts and content selection | `scripts/public_site.py` and `scripts/export_site.py` |
| Internal review pages and video assembly | `sources/production/library.py`, `deep_dive.py`, and the rendering tools |

The application evidence is a snapshot of cited files, including changes in the original
working tree. A complete runnable Resgrid checkout is obtained separately by the demo
setup command; it records the upstream revision. Private Descript editor projects remain
in Descript. Their exported audio, timing, scripts, illustrations and finished media are
stored here, so installed lessons can be assembled without cloud authentication.

## Build text and website changes

Python 3.10+ is enough for the standard website build. No Descript, Resgrid stack,
FFmpeg or additional Python packages are needed for this step.

```sh
python3 scripts/build.py --local-preview
python3 scripts/test_academy.py
python3 scripts/audit_public_repo.py
python3 scripts/serve.py
```

Build regenerates primer scripts and edit briefs from `sources/course.json`, refreshes
internal review pages, indexes the stored application evidence, and builds the learner-facing
website through `scripts/public_site.py`. Voice names, editorial state and recording QA
stay in the authoring sources. Public transcripts and feature guides are generated from
the course content. Operational terms such as draft records and planned feature availability
remain part of the lessons. Changes
to spoken text also require a new narration export and a video render. Build preserves
existing video bytes; it does not generate speech. Keep a feature's standalone recording
brief in sync when editing its description in the manifest.

Preview at `http://127.0.0.1:8769/` or `http://127.0.0.1:8769/academy/`.
After reviewing the diff, commit and push yourself. The workflow builds and validates on
pull requests and deploys default-branch updates. Existing custom-domain settings remain
in GitHub Pages settings.

## Refresh narration and video

For video assembly, install FFmpeg and the Python packages listed in
`sources/production/requirements.txt` in your local environment. Arial or DejaVu Sans
must be available for rendering new frames. `ACADEMY_FONT_REGULAR` and
`ACADEMY_FONT_BOLD` can select specific font files. Keep a conversational, clear voice;
listen to the result and verify “Resgrid” and technical terminology before publishing.

1. Edit the canonical lesson scenes and run `python3 scripts/sync_course.py`.
2. Generate whole-paragraph narration in your private Descript project, wait for all
   speech to finish rendering, and export audio plus SRT locally.
3. Import those local exports and assemble the selected lesson:

```sh
python3 scripts/import_narration.py --kind primer --lesson 00-start \
  --audio /path/to/export.m4a --captions /path/to/export.srt --ffmpeg /path/to/ffmpeg
python3 scripts/render_slides.py --lesson 00-start
python3 sources/production/descript/render_natural.py \
  --ffmpeg /path/to/ffmpeg --lesson 00-start
python3 scripts/render_public_media.py --ffmpeg /path/to/ffmpeg --lesson 00-start
```

The retained public-media authoring tool refreshes primer graphics and posters with Academy branding. It
copies the existing narration audio and removes complete editorial closing cues about
future recording plans, updating captions and chapter times together. Original narration
exports remain available in the authoring folders. The natural-narration renderer
also prepares those original exports by omitting the known editorial closing cues
when they are absent from the current lesson script, keeping script alignment valid. Run without `--lesson` to refresh all
primers. These illustrated outputs stay in the authoring sources; the website exports
their text as topic guides and does not publish their player, MP4, captions or chapter
media. The regular Pages build does not encode video.

For a detailed lesson, edit `sources/deep-dive/lessons/01-setup-wizard.json`, replace its
captures as needed, and use:

```sh
python3 scripts/import_narration.py --kind detailed --lesson 01-setup-wizard \
  --audio /path/to/export.m4a --captions /path/to/export.srt --ffmpeg /path/to/ffmpeg
python3 sources/production/deep_dive.py --render 01-setup-wizard --ffmpeg /path/to/ffmpeg
```

Refresh the intro with `python3 sources/production/render_captured.py --ffmpeg
/path/to/ffmpeg` after updating its narration, raw SRT, storyboard and chapter times.
The tools check speech timing, audible cues and encoded formats. Watch the beginning,
middle, end and chapter seeks, check actual Resgrid screens, and listen for natural speech.
Then run `python3 scripts/build.py --local-preview` to update `site/`.

The original `prepare.py`, `supplement.py`, `finish.py` and general `render.py` retain
prototype history. The current edition uses the natural narrator and captured-screen
renderers above. Do not run prototype generators to update the current course.

## Capture new Resgrid screens

See [the recording-stack instructions](sources/demo/README.md). The setup command creates
fresh local credentials, applies migrations, seeds the fictional department, and checks
services. The fixture baseline includes 14 personnel, six units, calls, training, shifts,
inventory, certifications, contacts, checklists and work orders.

The captured lessons show subsequent application actions. Use the detailed lesson JSON,
observed results, capture manifests and Firehouse 51 workflow evidence to replay those
actions before a matching capture. The seed is a clean baseline, rather than a raw dump
of the existing demo's evolving workflow history. Records activation, stock import,
saved deployments, chat messages and custom statuses shown later in a walkthrough are
created through the application as described in those sources.

Store new screenshots and capture evidence under `sources/captures/`, update the lesson's
capture filenames, and verify the saved state in Resgrid. The current detailed videos
use guided cuts between authentic screens; continuous pointer recordings can be added
as new source media. Do not include credentials in a capture or export.

For an expansion lesson, the explicit take plan in `sources/expansion/plans/`
retains screenshot choices and speech boundaries. Raw narration, Descript timing,
corrected captions and any measured screen-cut provenance are retained in
`sources/expansion/audio/`. Render a new take with `scripts/render_walkthrough.py`;
the [expansion production guide](sources/expansion/README.md) describes the complete
frame and playback review required before export.

The numbering lesson's `core-document-numbering.active-source.json` identifies its
approved 875-word narration snapshot. Its older generic `narrated-source.json` is
historical and must not be used to generate new speech. The Call & Dispatch lesson
also retains `sources/production/author_call_dispatch_take_01.py`, a hash-bound
recipe for its existing manually reviewed correspondence. Repeating that recipe
preserves the original review timestamp; changed images, words or timing require
new review rather than an automatically renewed approval.

## Production state

The generated `site/site-manifest.json` is the current published-video inventory.
Only qualified actual-screen videos enter the learner catalog. The latest dated
`sources/expansion/audits/academy-remaining-work-qualified*.json` records the bounded
remaining scope; overlapping outlines and historical plans are not a remaining-video count.
The 24 legacy illustrated primers are retained separately. Their original
illustrated media, scripts and replacement-gap records remain retained and unchanged;
the public export contains only their readable topic guides, six-sector examples and
transcript downloads. Public course data and the site manifest keep
topic guides separate from the actual-screen video inventory. Fire/EMS guide examples
reuse each original practice task; the five original companion-sector examples are
preserved. Two exact Relay/self-hosting recorder notes become equivalent learner
instructions only in the public projection.
The local preview keeps all videos available without remote uploads. The Pages workflow
packages qualified video bytes into SHA256-named GitHub Release assets and deploys the
smaller website only after verifying those assets. See [Release video delivery](docs/release-video-delivery.md).
`scripts/test_academy.py` runs current guards against current tools and runs the byte-pinned
historical recipes in an isolated copy with their exact retained tools. It does not renew
reviews or change historical hashes.
The [expansion production status](sources/expansion/README.md) and its capture-gap
plans distinguish verified videos from editable plans. Warm Lulu
sources exist for 23 primers; the Records primer retains its original 33 audio segments
under `sources/production/original-records/audio/`. Its natural-voice refresh and human
voice review remain pending. `sources/source-inventory.json` records these boundaries.
