# Record BigBoard against the Academy training stack

This support package prepares a separate copy of the pinned BigBoard source. It does not alter the original checkout. The existing Academy stack supplies the fictional department, calls, personnel, units and notes.

Prerequisites: the Academy demo stack, a local BigBoard checkout matching `source-baseline.json`, its installed dependencies, and `BIGBOARD_MAPBOX_PUBKEY` in the local environment. Environment files from the original app are excluded from the recording copy. Never put keys, credentials, bundles or runtime logs in the public repository.

From this directory:

```sh
python3 prepare.py --source /path/to/BigBoard --destination /path/to/recording/BigBoard --prepare
python3 allow_recording_origin.py --apply --stage-runtime
```

The second command changes only `ApiConfig.CorsAllowedOrigins` in the isolated stack's private API/eventing configuration and named config volume. It adds the two port-19105 loopback origins and preserves private before-copies. Restart only the existing Academy API and eventing services using that stack's Compose configuration; do not recreate the database or reseed an active exercise.

```sh
python3 launch.py --recording-directory /path/to/recording/BigBoard --plan
python3 launch.py --recording-directory /path/to/recording/BigBoard
```

Open `http://localhost:19105` and sign in normally using the local generated fictional training account. The launcher points only to the loopback training API, disables environment-file loading and analytics configuration, and inherits the map key without printing or writing it. Local browser/runtime restrictions may require normal host permission to bind the recording server.

The recorded operational-display exercise adds Calls, Units, Personnel and Time, changes dimensions and column order, moves and removes a temporary Notes widget, and reloads the board. Its source proposal and raw captures retain the exact executed evidence. No database write is needed for that display exercise.

This pinned build also exposes controls whose saved values did not change the corresponding widget during recording: generic font settings, personnel availability filtering and clock format. Those are documented in the production audit and are not represented as successful effects in the lesson. Existing development warnings are dismissed through their normal UI before clean captures; original pixels are never modified.
