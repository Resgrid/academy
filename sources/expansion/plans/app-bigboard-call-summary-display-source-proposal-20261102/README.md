# Calls Summary recording source

This candidate contains eight narration paragraphs, 13 personally reviewed original
Resgrid screens and 63 actual Descript speech cues. `actual-cue-screen-proposal.json`
maps the cues to 17 proposed screen intervals using exported endpoints only.
No downloaded-audio, human hearing, encoded-frame or playback approval is inferred.
The learner catalog remains at 67 qualified videos until this candidate passes those gates.

Run `python3 sources/production/check_bigboard_call_summary_source_20261102.py`
from the Academy root to verify the frozen script, controls, images and DOM sidecars.
Edit a new version when changing words or captures; do not renew historical reviews.

Recreate the scenario in the isolated demo stack using the repository's demo setup
and seed sources. In Big Board, add Calls Summary. Configure its width4/height3,
Show Recent Call and Show Priority Counts, Max Priorities to Show and font size.
The script records all-priority counts4/3/1/0, a one-row limit with Active still4,
recent-card hiding, priority-count hiding, restoration and fresh saved readback.
Calls remain fictional and unchanged throughout this recording.

The generic accessibility setValue call did not commit the first priority-slider
attempt. Normal keyboard Arrow keys committed both priority limit and font size;
subsequent saved-result/readback images establish that behavior. Earlier raw005/006
are retained as excluded attempts. Raw009 contains switch animation and raw015 a
React development notification; neither enters the reviewed manifest. The notification
was closed with its visible close control before clean captures016/017. Screenshot
pixels were never edited. Raw018 is an additional saved-limit readback.

The map widget's controls were inspected before selecting this next lesson; no map
settings were changed or claimed to work in this candidate.

## Completed recording

The candidate was subsequently qualified after the complete User listening review,
final1080p render, all63 encoded captions and22 screen intervals, full audio decoding,
source-image comparison and advancing browser playback. The canonical lesson is
`sources/expansion/lessons/app-bigboard-call-summary-display.json`. Earlier pending
statements above describe this source-freeze checkpoint and do not override that
qualification. Run the portable checker
`python3 sources/production/check_bigboard_calls_summary_qualified_archive_20261102.py`.

To render a new take from the retained inputs, use `scripts/render_walkthrough.py`
with this source candidate, the `*-take-01-final-inputs-20261102/plan.json`, asset root
`sources`, a fresh output directory and your FFmpeg path. New output starts unqualified
and needs actual encoded-screen/caption and playback review. Do not reuse old frame
approvals for changed screenshots, speech or timing.
