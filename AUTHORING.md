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
| Original screenshots and capture evidence | `sources/captures/firehouse51/` and `sources/captures/deep-dive/` |
| Intro narration and guided-cut screen timeline | `sources/captures/firehouse51/narration-script.json`, `storyboard.json`, and `firehouse51-walkthrough.chapters.json` |
| Illustrated slides and narration direction | `sources/production/descript/slides/`, `voice-direction.json`, and the edit briefs |
| Primer narration and raw speech timing | `sources/production/descript/natural/audio/` and `natural/captions/` |
| Detailed narration and raw speech timing | `sources/deep-dive/audio/` and `sources/deep-dive/*-raw.srt` |
| Current finished videos, captions and posters | `sources/media/`, `sources/deep-dive/media/`, and the intro capture folder |
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
python3 scripts/build.py
python3 -m unittest discover -s scripts/tests -v
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

The public-media step refreshes primer graphics and posters with Academy branding. It
copies the existing narration audio and removes complete editorial closing cues about
future recording plans, updating captions and chapter times together. Original narration
exports remain available in the authoring folders. The natural-narration renderer
also prepares those original exports by omitting the known editorial closing cues
when they are absent from the current lesson script, keeping script alignment valid. Run without `--lesson` to refresh all
primers. The regular Pages build does not encode video.

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
Then run `python3 scripts/build.py` to update `site/`.

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

## Production state

There are 24 illustrated primers, seven detailed captured videos and an introductory
walkthrough. Twenty-three detailed workflows remain to capture and narrate. Warm Lulu
sources exist for 23 primers; the Records primer retains its original 33 audio segments
under `sources/production/original-records/audio/`. Its natural-voice refresh and human
voice review remain pending. `sources/source-inventory.json` records these boundaries.
