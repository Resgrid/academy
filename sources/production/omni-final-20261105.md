# Omni Dispatch and IC follow-up walkthroughs

These three review videos use screenshots from the fictional Firehouse 51 department. The editable scripts, shot order, audio and captions are in the matching `sources/expansion/plans/omni-*-source-20261105/` folders. Capture hashes are in `sources/captures/expansion/omni-final-20261105/manifest.json`. Each plan records a full decode check and a comparison between every rendered shot and its original capture.

The English narration uses Kokoro v1.0, voice `af_heart` at 0.96 speed. The retained lossless audio is enough to rebuild without the voice model or a hosted service.

```sh
python3 -m pip install imageio-ffmpeg numpy Pillow
python3 sources/production/render_omni_final_review_20261105.py
python3 sources/production/serve_playback.py sources/expansion/rendered/omni-final-review-20261105 --port 19121
```

Use the isolated training stack documented under `sources/demo/`. Enter the historical call from Core and verify the same call number, original timestamp and closure timestamp in Dispatch. Open the saved call in Omni Dispatch and create a Callback from its Records tab. Save, revise, finalize and check the linked result. Standalone Dispatch can read the same finalized Callback through the same Core API.

For chat, open the same direct conversation as two different fictional operators. The local gateway must route API authentication and Eventing consistently. In the training API and Eventing config, turn on `SystemBehaviorConfig.CacheEnabled` with the training Redis service available; secured chat channels need Redis access versions. Keep broadcast suppression enabled. Record the recipient before and after delivery without reloading, then verify the saved acknowledgment. A device push alert needs a separately configured test provider and device.

The clips are retained for local review and are outside the published lesson catalog.
