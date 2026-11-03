# Unit mapping response compatibility

These before/after files and `mapping-contract.patch` belong to the isolated
`capture-apps/Unit-records` recording copy. The original Unit repository is unchanged.
The adapter uses Core's path parameters, maps layer `Id`/`LayerSource`, projects the
indoor `Map`/`Floors` envelope and bounds, and wraps actual raw GeoJSON for the store.
It does not generate geometry, suppress API errors or change authorization.

Run the meaningful response-contract check with a complete recording copy:

```sh
node sources/demo/client-support/unit-mapping-contract-20261103/check-contract.mjs \
  /path/to/capture-apps/Unit-records
```

The test reproduces the prior layer/map/GeoJSON mismatches and checks the actual
transpiled adapter against current Core contracts, exact coordinates, route paths and
malformed-data rejection. Results are in `contract-check-results.txt`. The full Unit
typecheck still reports the pre-existing `SchemaVersion` Records test error; no new
mapping diagnostic was reported.

Normal UI now opens Maps and the indoor floor selector. The inspected recording
still lacks the indoor floor image/region overlay, so this is **not** evidence of a
working indoor-viewer or live indoor-tracking video. No blank viewer screen is eligible
for an Academy lesson. Preserve that limitation until an actual successful viewer
render and location scenario have been recorded. The Core indoor-room and KML/KMZ
lessons independently demonstrate their actual saved geometry and call references.

The missing image/region state above is the earlier observation. The later
[indoor rendering pack](../unit-indoor-render-compatibility-20261103/README.md)
now has successful actual browser evidence for floor images and saved region
references. It still adds no live occupancy or tracking feed.
