# Unit indoor rendering compatibility

This pack belongs to the isolated `capture-apps/Unit-records` recording copy. The
primary Unit checkout is unchanged. Apply it after the earlier Unit mapping-contract
pack; every before/after file and SHA-256 identity is retained here.

The API adapter requests the existing authorized `SignMapResourceUrls` contract for
floor images. It does not remove bearer checks or make an image public. Missing
permission fails closed. The viewer clears an old image on floor changes, ignores a
late response for a previous floor, and reports a failed image request. The search
field keeps readable contrast. An absent floor list is not displayed as a false zero
floor count on the map card. Signed URL
values are generated at runtime and must stay out of source, logs and screenshots.

For older floor-editor rooms whose API GeoJSON is empty, the adapter can read the
actual stored coordinate ring from `PixelGeometry`. It accepts only geographic
coordinates near the room's stored geographic centre, closes the original ring and
retains the saved name and colour. Ordinary image-pixel coordinates, malformed rings
and missing centres are rejected. No new coordinates, live positions or permission
flags are invented. Existing nonempty GeoJSON is preserved exactly. The viewer uses
a fallback display colour for imported regions that have no saved colour.

```sh
python3 sources/demo/client-support/unit-indoor-render-compatibility-20261103/apply_verified.py \
  --recording-copy /path/to/capture-apps/Unit-records
node sources/demo/client-support/unit-indoor-render-compatibility-20261103/check-contract.mjs \
  /path/to/capture-apps/Unit-records
```

The first command is read-only; add `--apply` to copy the three replacements after all
hashes pass. It does not restart applications, build, use Git or write a database.
Restart only the owned recording-copy Metro listener and check the actual UI before
capturing. Contract checks pass against the actual transpiled adapter. Full Unit
TypeScript checking still reports the pre-existing Records `SchemaVersion` test
error; no new diagnostic was reported for these changes.

A successful contract test is not proof of a visible image or polygon. Actual browser
rendering and all tutorial production gates remain separate. This pack adds no live
indoor tracking, sensor feed, floor/room identity to personnel locations or occupancy
overlay. A saved room reference is not evidence that a person is inside it.

The final normal-UI render was personally verified on 2026-11-03: actual floor image,
room overlays/details, readable search/filter/clear, imported KML/KMZ regions and
map reopening are retained in `browser-verification.json` and the frozen lesson
sources it identifies. These are stored references; no live occupancy is demonstrated.
