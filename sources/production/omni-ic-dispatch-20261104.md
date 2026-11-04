# Omni IC and Dispatch walkthrough sources

The nine videos under `sources/expansion/rendered/omni-ic-review-20261104/` use screenshots captured from the actual Resgrid app with the fictional Firehouse 51 department. The player is a local review tool. Academy publication requires the normal lesson evidence and playback review.

Each corresponding `sources/expansion/plans/omni-ic-*-source-20261104/` directory contains the editable script, screenshot sequence, speech-timed captions, lossless mono audio, timing measurements and an encoded-frame check. The screenshot originals and captured viewport evidence are in the `omni-ic-*-20261104` and `omni-dispatch-followups-20261104` directories under `sources/captures/expansion/`.

The local narration was produced with Kokoro v1.0 and the English `af_heart` voice at 0.96 speed. Captions are timed to the actual samples for each sentence. The build can be reproduced from the retained audio without access to the voice service or model.

```sh
python3 -m pip install imageio-ffmpeg numpy Pillow
python3 sources/production/render_omni_ic_dispatch_review_20261104.py
python3 sources/production/serve_playback.py sources/expansion/rendered/omni-ic-review-20261104 --port 19116
```

## Recording scope

- The shared-device lessons cover labels, verification status, manual lock and ending a shift. The fictional account has no enrolled authenticator or passkey.
- IC communications covers viewing a training channel, composing an unsent draft, previewing alert sounds and checking the browser inbox availability. Live delivery requires a configured notification service.
- The offline exercise temporarily stopped only the isolated training API. The note appeared as queued, cleared from the outbox after the API returned and was visible in a separate IC session.
- Dispatch Records uses a department form published for the call context. The built-in Callback and Run forms use a different fixed-field contract.
- Archived Calls covers filtering and reading an existing call. Historical entry in Core is a separate scenario.
