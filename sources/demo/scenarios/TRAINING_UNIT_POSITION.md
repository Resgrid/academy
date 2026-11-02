# Reserve apparatus marker fixture

`refresh_training_unit_position.py` is narrowly scoped fixture preparation for the
isolated Academy department. It supports only department 51, Reserve Engine 51
(unit 51006, Engine, station group 51001), at its already seeded fictional station
point **41.8721, -87.6523**. It does not collect GPS or operate a device/provider.

The ordinary Core status action creates a new status without copying location.
The map's latest-status fallback consequently cannot show a locationless status.
The helper appends one new status row with the declared simulated point. It copies
every other current status column, including destination, note and actor fields;
the new identity and UTC/local timestamps are also declared changes. All prior
rows remain. It refuses protected values, crew assignments, changed coordinates,
future status timestamps, unexpected status triggers/rules, or a changed fixture
identity. Repeating the same guarded request at the same point is a no-op.

Help, the default invocation and `--plan` are offline. They do not import stack
management, open private configuration, contact Docker/SQL or save a report:

```sh
python3 sources/demo/scenarios/refresh_training_unit_position.py --plan
```

The operator must review the helper before executing a write. The exact current
Available note supplied for this demonstration can be used as follows, from the
Academy repository root:

```sh
python3 sources/demo/scenarios/refresh_training_unit_position.py \
  --write-training-fix --expected-state Available \
  --expected-note 'TRAINING ONLY - Reserve Engine 51 marker demonstration; simulated Available, no destination or GPS.'
```

The explicit path checks a local Unix-socket Docker endpoint, the named Academy
stack's internal training network and PostgreSQL container project, then executes
one locked transaction only in `resgrid_academy`. The latest row must exactly
match the operator's selected status and supplied single-line Reserve Engine 51
TRAINING ONLY note. A concurrent or unexpected change causes refusal.

After the real map is inspected, restore **only Reserve Engine 51** to
**Out of Service / None** through the ordinary Core UI, with a clear training
restoration note. Read that exact note back before saving. The same helper may
then restore the fictional station fallback using `--expected-state OutOfService`
and that exact note. The note must begin `TRAINING ONLY - Reserve Engine 51 `.
This restores the intended state and fixture point while retaining the honest
demonstration history; it does not roll back history or impersonate the old row.

A successful explicit write/no-op saves only whitelisted public fixture metadata
to `sources/demo/scenario-reports/fresh-training-unit-position.json`. No note,
actor identifier, credentials, connection values or raw SQL errors are exported.
The helper does not call application services, emit events/notifications, modify
live-location documents, change calls or promise that a map/provider accepted it.
Marker visibility and selected artwork require separate normal UI observation.

Offline tests:

```sh
python3 -m unittest scripts.tests.test_training_unit_position scripts.tests.test_training_positions -v
```

The nine new tests cover offline paths, argument refusals, exact-note SQL
encoding, fixed transaction guards and append-only field preservation, sanitized
success/no-op results, failure reporting, inconsistent results, remote/unisolated
Docker rejection and the fixed local database target. Four existing officer
helper tests also pass. These are offline tests and static SQL guard checks;
database execution, transaction integration and application appearance remain
pending until the operator explicitly performs and verifies them.

Source correspondence (paths relative to the separately retained Core source):

- Academy `sources/demo/seed.py:74–75`: apparatus identity and original point.
- `Web/Resgrid.Web/Areas/User/Controllers/UnitsController.cs:781–811`:
  normal status creation sets state, time, optional destination and note, without
  inheriting coordinates.
- `Core/Resgrid.Model/UnitState.cs:188–195`: status location requires nonzero
  typed latitude/longitude.
- `Core/Resgrid.Model/MappingMarkerSource.cs:14–25`: latest source selection.
- `Web/Resgrid.Web.Services/Controllers/v4/MappingController.cs:523–557`:
  unit marker uses selected live/status coordinates, with no station inheritance.
- `Web/Resgrid.Web/Areas/User/Controllers/MappingController.cs:1044–1070`:
  the legacy map also requires coordinates on the latest status row.
