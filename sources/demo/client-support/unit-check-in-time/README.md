# Unit check-in UTC presentation

The service writes `CheckInRecord.Timestamp = DateTime.UtcNow`; timer/history DTOs
pass that instant through. PostgreSQL timestamp rows can arrive without a zone.
The original card passed the raw string to date-fns, and history used `new Date`
directly. Los Angeles therefore interpreted naive UTC as local time. The direct
installed-SDK probe gives -415 minutes for an instant actually five minutes old.

The two presentation components now reuse existing `parseApiUtcDate` from
`@/lib/utils`. UTC-naive strings become UTC; explicit Z and signed offsets remain
intact. Missing/invalid values show the existing translated Unknown, not a fake
recent check-in or Invalid Date. Genuinely future timestamps are not clamped.
No server timestamps, timer rules, clocks, stored records or other date fields
were changed. The existing map/image fixes remain byte-identical.

`verification.json` pins the three original files, four resulting files, parser,
dependency manifests and source contract. `before/`, `after/` and the exact unified
patch are reproducibility inputs; original source was changed only through the
approved filesystem operation. This bundle does not apply or launch anything.
The earlier Unit recording helper/version/proofs are preserved unchanged.

Run the actual installed regression in separate timezone processes, using the
existing installed dependencies (no install, Git or native provider operation):

```bash
export ACADEMY_UNIT_ROOT=/path/to/Unit
TZ=UTC node "$ACADEMY_UNIT_ROOT/node_modules/jest/bin/jest.js" --config sources/demo/client-support/unit-check-in-time/jest-check-in.config.cjs --runInBand --coverage=false --no-cache
TZ=America/Los_Angeles node "$ACADEMY_UNIT_ROOT/node_modules/jest/bin/jest.js" --config sources/demo/client-support/unit-check-in-time/jest-check-in.config.cjs --runInBand --coverage=false --no-cache
```

Each process passed20 tests across two suites. The new component regression
covers naive UTC, explicit Z, positive/negative offsets, compact offset, absent
and invalid input, and a genuinely future instant. The optional
`jest-original-check-in.config.cjs` redirects only the two component imports to
the preserved originals: its Los Angeles regression intentionally fails5of11
cases, including naive UTC. Those failures are baseline proof, not current failures.
Fixtures never access credentials, browser stores, services or actual GPS.

Production components passed targeted ESLint; all four edited files passed
Prettier. Repository ESLint ignores tests, so no test-file lint pass is claimed.
Proof summaries retain test names/statuses without noisy failure render dumps.

Actual browser verification remains with the parent. CI disables Metro watching:
source changes need an explicit restart of the known local Unit server with
`--clear` and the same inherited environment. Do not blank, print or save Mapbox
keys, kill another listener, change authentication, or alter timer/call state to
make a screenshot look correct. This source/test bundle alone qualifies no video.
