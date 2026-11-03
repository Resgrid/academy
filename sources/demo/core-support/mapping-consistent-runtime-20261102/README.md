# Mapping recording runtime

This support pack reproduces the actual layer and weather-source operations recorded
against Core revision `c28164f35bd771fbc2a2717610f60a110e8b5a13`. It preserves all five
original and replacement source files, SHA-256 identities and the real storage probe.
The primary Core checkout was not modified. It is separate from the older expansion
source profile; do not rewrite that profile's pins or reuse its historical evidence.

The PostgreSQL map-layer codec retains full GeoJSON coordinates, properties and polygon
holes. The UI uses the PostgreSQL identifier on edit links. The API also returns each real layer identifier, preventing multiple PostgreSQL layers from sharing an empty Mongo identifier and a visibility preference. The Dapper GUID handler
accepts native UUID and legacy citext identifiers and sends parameters so PostgreSQL
can infer the destination type. Invalid identifiers and legacy documents with lost
coordinates fail explicitly. `probe-results-final.txt` contains the 16 passed checks;
temporary probe writes were rolled back.

Use a complete isolated Core checkout at the recorded revision. Review the changes:

```sh
python3 sources/demo/core-support/mapping-consistent-runtime-20261102/apply_verified.py \
  --isolated-checkout /path/to/isolated-Core
```

Add `--apply` to copy the five replacements after all before/after hashes pass. It
refuses unknown source bytes and the Academy checkout's sibling primary Core/Unit
directories. It performs no Git actions, builds, container operations or database writes.
The existing [stack setup](../../README.md) accepts that complete isolated checkout
through `--core`. Use a separate fresh Academy checkout/profile for a different source
selection; existing source pins, counters, credentials and volumes must be preserved.

Build/publish the web and API projects from the same isolated checkout. Do not mix
assemblies from different publish outputs. The recordings used standard web/API
publishes, retaining the earlier route numeric-form support. Reapply the
[route form pack](../routes-new-numeric-stops-20261102/README.md) when required by its
exact before hash. The 32KB `loopback-after.conf` header buffers accommodate the local
training access token; they do not weaken certificate verification or authorization.

## Optional provider access

`../../compose.mapping-providers.yaml` adds an unpublished, non-root CONNECT tunnel.
Only `api.mapbox.com:443` and `api.weather.gov:443` are allowed. Web/API remain on the
internal training network; only the tunnel has egress. It neither terminates TLS nor
logs tunnel payloads or credentials. Worker delivery and test-mail settings stay as
configured by the isolated stack.

Set `MappingConfig.RoutingProvider` to `mapbox` and supply
`MappingConfig.MapboxRoutingAccessToken` in the ignored runtime configuration. The
recording used the inherited `UNIT_MAPBOX_PUBKEY`; no token is included in this pack.
Use the same environment and named profile as setup, adding the override explicitly:

```sh
docker compose --project-name YOUR_TRAINING_PROFILE \
  --env-file sources/demo/.env -f sources/demo/compose.yaml \
  -f sources/demo/compose.mapping-providers.yaml up -d routing-egress web api loopback
```

This is an opt-in recording configuration, not a production deployment recipe. The
recorded source remains inactive/Never Polled, and global weather messaging is off.
Provider access alone is not evidence of a completed weather poll or alert delivery.
The road lesson retains actual provider estimates; it does not claim a physical trip.

See `../../scenarios/mapping-recordings-actual-ui-20261103.json` for new recording
fixtures and the precise normal-UI replay steps. Generated configuration, database
backups, private exports and credentials remain under ignored `private/`.
