# Omni Dispatch walkthrough sources

The five lesson keys are `access`, `call-lifecycle`, `maps`, `communications`, and `operations`. Each source directory under `sources/expansion/plans/omni-dispatch-<key>-source-20261103/` contains the editable script, captions, scene and screen timing, capture manifest, and assembly plan. The screenshots are captured from the real Omni Dispatch application in the fictional training department.

To reproduce a current master with the included narration, screenshots, and reviewed timings, run from the Academy repository root (replace `access` with the desired key):

```sh
lesson_key=access
plan_dir="sources/expansion/plans/omni-dispatch-${lesson_key}-source-20261103"
python3 scripts/render_walkthrough.py \
  --lesson "$plan_dir/lesson.candidate.json" \
  --plan "$plan_dir/plan.json" \
  --asset-root sources \
  --output-dir "sources/expansion/rendered/app-dispatch-omni-${lesson_key}-take-02"
```

Rendering requires Pillow, FFmpeg, and a system font available to the renderer. Use a new output directory for each take. If you change the script, generate new narration and captions, update the screen and cue mappings, then review and qualify the new output before replacing its lesson evidence. Descript share links and raw export receipts are kept out of the public source; the lossless mono narration used to build the current masters is included.
