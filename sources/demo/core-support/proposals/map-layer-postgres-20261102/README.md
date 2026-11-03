# Map-layer PostgreSQL recording investigation

This proposal is not applied to the running recording stack or the original Core checkout. No map-layer video is qualified from it.

The first actual New Layer POST stored a metadata document without geometry coordinates, then reported failure because the MVC controller checked the Mongo ID for a PostgreSQL document. The Layers list tried to materialize the JSON column directly into a MapLayer and raised a Dapper conversion exception.

The proposed repository codec preserves a full GeoJSON feature collection and reads SQL IDs separately. The controller and list proposal use the existing GetId method. Eight real rectangle/marker storage round-trip checks passed against the recording stack dependencies. A separate polygon-hole test fails in the older published Model.Hydrate implementation; that failure is retained, not counted as a pass.

An isolated web build cannot currently use the newer Core source with the older recording binaries: it exposes missing newer incident-back-office and localization contracts. No such mixed build was deployed. The failed newly created demo row was privately backed up and precisely removed to restore the previously empty Layers list; no existing layer was removed. Resume with a consistent source/binary set, resolve the Model geometry defect, repeat the full build and tests, and verify normal UI create/save/reopen/edit/map visibility before authoring narration.

Before/after files and the patch are proposals only. Source identities retain their hashes. Credentials, database backup and complete runtime/build logs remain ignored and local.
