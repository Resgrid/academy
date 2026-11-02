# Unit checklist authoring scaffold

This opt-in helper preserves candidate v2, both earlier candidates, canonical
lessons, raw screenshots and history. Its default command performs source and
caption preflight only; it does not write a plan or create media:

```bash
python3 -B sources/production/author_unit_readiness_checklists_take_01.py
python3 -B -m unittest discover -s sources/production/tests -p test_unit_readiness_authoring_scaffold.py
```

The approved source has eight scenes,497 spoken words,17 untimed spans and eight
reviewed full application images. Fresh genuine SRT has54 cues ending190.469s.
The source image for cue42 retains **Submit checklist**; cue43 begins145.289s and
switches to the submitted view. No word-level interpolation or new cue split is
needed. Statements about removed buttons use the resulting submitted image.

The user confirmed all eight generated paragraphs were audible; the parent
read back eight generated assets totaling190.64s. These describe the editor
source composition, not a decoded local export or an exact-file human listen.
Complete local audio was unavailable when this scaffold was prepared. Existing
source confirmation requires no new user approval; actual media gates remain.

Once the parent retains the approved complete audio export, run the existing
`scripts/qa_narration.py` with the frozen candidate, actual audio and `.fresh.srt`.
The expected frozen lesson SHA256 is
`822c1c42f26c43a0ed0a20e1562c9d42dd1417e80287cbaf25ddcc68fe8446a2`.
Keep corrected captions and the QA report as new files. Require complete decode,
all54 raw/corrected measured energies, exact497 words and zero unresolved issues.

Only after that work, supply independently reviewed hashes to the helper:

```bash
python3 -B sources/production/author_unit_readiness_checklists_take_01.py \
  --audio sources/expansion/audio/app-unit-readiness-checklists.m4a \
  --audio-sha <actual-audio-sha256> \
  --corrected sources/expansion/audio/app-unit-readiness-checklists.actual.corrected.srt \
  --corrected-sha <actual-corrected-srt-sha256> \
  --qa-path sources/expansion/audio/app-unit-readiness-checklists.actual.qa.json \
  --qa-sha <actual-completed-qa-sha256> \
  --ffmpeg <local-ffmpeg-executable> \
  --write-plan sources/expansion/plans/app-unit-readiness-checklists-take-01.plan.json
```

The helper checks expected hashes and completed QA, then repeats a full decode
and every measured cue before constructing any plan. Missing/partial audio,
changed script, captions or source pixels, illustrated substitutes, unseen
controls and guessed cue bounds fail closed. Existing outputs are refused.
The tests' invalid media and silent PCM are temporary rejection fixtures, never
approved narration or tutorial assets.

A future plan still needs unchanged renderer input validation, full-frame image
and caption/layout inspection, actual rendered-frame QA and beginning/middle/end
browser playback proof. The helper contains no render/export/publish command and
does not mark the lesson ready. Do not infer physical readiness, an inspection,
offline or restart durability, device location, witness/signature/photo completion
or other Unit lesson coverage from this bounded software checklist exercise.

Take 01 is complete. Its downloaded narration, corrected captions and measured
QA are in `sources/expansion/audio/`; the 1080p master, chapters, extracted frames,
cue comparisons, three actual native-player proofs and final qualification are in
`sources/expansion/rendered/app-unit-readiness-checklists-take-01/`.
The canonical lesson is `sources/expansion/lessons/app-unit-readiness-checklists.json`.
The frozen candidate, raw media/transcripts and pending worksheets remain retained.

Use a Python environment with Pillow and NumPy, plus an installed FFmpeg executable,
for rendering and numerical frame checks. The new review helper accepts an explicit
binary path and does not depend on the recording machine's temporary runtime path:

```bash
python3 sources/production/review_unit_readiness_take_01_assets.py --ffmpeg /path/to/ffmpeg
```

Numerical comparisons do not approve changed footage. New recordings or narration
require a new take, actual visual review and fresh browser playback checks before
qualifying or replacing the learner video. Rebuilding the existing website needs
only `python3 scripts/build.py`; it does not need Descript or these media tools.
