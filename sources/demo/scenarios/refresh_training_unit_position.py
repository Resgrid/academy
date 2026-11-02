#!/usr/bin/env python3
"""Append one declared fictional station location to Reserve Engine 51's status.

Default, --plan and --help are offline. The explicit write option requires the
operator's exact expected status and TRAINING note. This is isolated fixture
preparation, not an application action or physical GPS observation. No events,
notifications or live-location document writes occur. Existing history remains.
"""
import argparse
import base64
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
STATES = {'Available': 0, 'OutOfService': 4}
POSITION = {'latitude': 41.8721, 'longitude': -87.6523}
SOURCE = 'SIMULATED Academy station status location; no device GPS or provider'


def validate_note(note):
    if (not isinstance(note, str) or not note.startswith('TRAINING ONLY - Reserve Engine 51 ')
            or len(note) > 500 or not note.isprintable()):
        raise ValueError('Expected note must be the exact single-line Reserve Engine 51 TRAINING ONLY note (maximum 500 characters).')
    return note


def build_query(expected_state, expected_note):
    if expected_state not in STATES:
        raise ValueError('Only explicitly expected Available or OutOfService is supported.')
    # Base64 keeps caller text out of SQL/dollar-quote syntax, including quotes
    # and dollar delimiters. The note is compared exactly, never modified.
    encoded = base64.b64encode(validate_note(expected_note).encode('utf-8')).decode('ascii')
    return QUERY.replace('__EXPECTED_STATE__', str(STATES[expected_state])).replace('__EXPECTED_NOTE_BASE64__', encoded)


QUERY = r"""
BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '15s';
SELECT pg_advisory_xact_lock(8151051006);
LOCK TABLE public.unitstates, public.unitstateroles IN SHARE ROW EXCLUSIVE MODE;
DO $academy_unit_fixture$
DECLARE
 previous public.unitstates%ROWTYPE;
 seeded public.unitstates%ROWTYPE;
 previous_json jsonb;
 seeded_json jsonb;
 expected_note text := convert_from(decode('__EXPECTED_NOTE_BASE64__','base64'),'UTF8');
 expected_state integer := __EXPECTED_STATE__;
 changed_fields text[] := ARRAY['unitstateid','timestamp','localtimestamp','latitude','longitude','geolocationdata'];
 before_count bigint;
 column_names text;
 fresh_timestamp timestamp without time zone := timezone('UTC',clock_timestamp());
 appended boolean := false;
 result jsonb;
BEGIN
 IF current_database() <> 'resgrid_academy' THEN
  RAISE EXCEPTION 'Only the isolated Academy database is supported'; END IF;
 IF EXISTS (SELECT 1 FROM pg_trigger WHERE tgrelid='public.unitstates'::regclass
  AND NOT tgisinternal AND tgenabled<>'D') OR EXISTS
  (SELECT 1 FROM pg_rules WHERE schemaname='public' AND tablename='unitstates') THEN
  RAISE EXCEPTION 'Unexpected status trigger or rule refused; no event side effects permitted'; END IF;
 PERFORM 1 FROM public.departments WHERE departmentid=51
  AND name='Firehouse 51 — Training Department' AND code='FH51' FOR SHARE;
 IF NOT FOUND THEN RAISE EXCEPTION 'Exact fictional department identity required'; END IF;
 PERFORM 1 FROM public.departmentgroups WHERE departmentgroupid=51001
  AND departmentid=51 AND name='Firehouse 51' AND type=2
  AND latitude::text='41.8721' AND longitude::text='-87.6523' FOR SHARE;
 IF NOT FOUND THEN RAISE EXCEPTION 'Unchanged fictional station identity and point required'; END IF;
 PERFORM 1 FROM public.units u WHERE unitid=51006 AND departmentid=51
  AND name='Reserve Engine 51' AND type='Engine' AND stationgroupid=51001
  AND vin='DEMO-APPARATUS-6' AND platenumber='TRAINING'
  AND NOT COALESCE((to_jsonb(u)->>'isdeleted')::boolean,false) FOR SHARE;
 IF NOT FOUND THEN RAISE EXCEPTION 'Exact fictional reserve apparatus identity required'; END IF;
 SELECT * INTO previous FROM public.unitstates WHERE unitid=51006
  ORDER BY timestamp DESC,unitstateid DESC LIMIT 1;
 IF NOT FOUND THEN RAISE EXCEPTION 'Existing reserve status required'; END IF;
 IF previous.state IS DISTINCT FROM expected_state OR previous.note::text IS DISTINCT FROM expected_note THEN
  RAISE EXCEPTION 'Latest status or exact training note changed; preserve that state'; END IF;
 previous_json := to_jsonb(previous);
 IF COALESCE((previous_json->>'isprotected')::boolean,false) OR EXISTS
  (SELECT 1 FROM jsonb_each(previous_json) p WHERE p.key LIKE 'protected%'
   AND p.value <> 'null'::jsonb AND p.value <> '""'::jsonb) THEN
  RAISE EXCEPTION 'Protected status values cannot be copied to a new identity'; END IF;
 IF EXISTS (SELECT 1 FROM public.unitstateroles WHERE unitstateid=previous.unitstateid) THEN
  RAISE EXCEPTION 'Reserve crew assignment changed; preserve it through the application'; END IF;
 IF (previous.latitude IS NOT NULL AND previous.latitude <> 41.8721)
  OR (previous.longitude IS NOT NULL AND previous.longitude <> -87.6523)
  OR (previous.geolocationdata IS NOT NULL AND previous.geolocationdata::text NOT IN ('','41.8721,-87.6523')) THEN
  RAISE EXCEPTION 'Changed location refused; only missing or declared fixture coordinates are supported'; END IF;
 IF previous.timestamp > fresh_timestamp THEN
  RAISE EXCEPTION 'Future status timestamp refused'; END IF;
 SELECT count(*) INTO before_count FROM public.unitstates WHERE unitid=51006;
 IF previous.latitude=41.8721 AND previous.longitude=-87.6523
  AND previous.geolocationdata::text='41.8721,-87.6523' THEN
  seeded := previous;
 ELSE
  -- Give the appended row a strictly later timestamp without reinterpreting the
  -- original local/UTC offset. All other present and future columns are copied.
  fresh_timestamp := greatest(fresh_timestamp,previous.timestamp + interval '1 microsecond');
  seeded_json := previous_json || jsonb_build_object(
   'timestamp',fresh_timestamp,
   'localtimestamp',previous.localtimestamp + (fresh_timestamp - previous.timestamp),
   'latitude',41.8721,'longitude',-87.6523,'geolocationdata','41.8721,-87.6523');
  SELECT string_agg(quote_ident(attname),',' ORDER BY attnum) INTO column_names
   FROM pg_attribute WHERE attrelid='public.unitstates'::regclass AND attnum>0
   AND NOT attisdropped AND attname<>'unitstateid' AND attgenerated='';
  IF column_names IS NULL THEN RAISE EXCEPTION 'Status schema unavailable'; END IF;
  EXECUTE format('INSERT INTO public.unitstates (%s) SELECT %s FROM jsonb_populate_record(NULL::public.unitstates,$1) RETURNING *',column_names,column_names)
   INTO seeded USING seeded_json;
  appended := true;
 END IF;
 IF (to_jsonb(seeded) - changed_fields) IS DISTINCT FROM (previous_json - changed_fields) THEN
  RAISE EXCEPTION 'Status, destination, note, actor or other preserved field changed'; END IF;
 IF (SELECT to_jsonb(s) FROM public.unitstates s WHERE unitstateid=previous.unitstateid) IS DISTINCT FROM previous_json THEN
  RAISE EXCEPTION 'Original status history changed'; END IF;
 IF (SELECT count(*) FROM public.unitstates WHERE unitid=51006) <> before_count + appended::integer THEN
  RAISE EXCEPTION 'Unexpected status history count'; END IF;
 IF seeded.latitude IS DISTINCT FROM 41.8721 OR seeded.longitude IS DISTINCT FROM -87.6523
  OR seeded.geolocationdata::text IS DISTINCT FROM '41.8721,-87.6523' THEN
  RAISE EXCEPTION 'Declared fixture location did not persist'; END IF;
 result := jsonb_build_object('scenario','fictional reserve apparatus station status location',
  'unit_id',51006,'department_id',51,'expected_state',expected_state,
  'previous_status_id',previous.unitstateid,'status_id',seeded.unitstateid,
  'appended',appended,'latitude',41.8721,'longitude',-87.6523,
  'status_fields_preserved',true,'note_preserved',true,'prior_history_preserved',true,
  'events_emitted',false,'live_location_written',false,
  'source','SIMULATED Academy station status location; no device GPS or provider');
 PERFORM set_config('academy.unit_fixture_report',result::text,true);
END $academy_unit_fixture$;
SELECT current_setting('academy.unit_fixture_report');
COMMIT;
"""


def execute_query(query):
    # No settings, private files or Docker are loaded on the offline paths.
    sys.path.insert(0, str(ROOT))
    from manage import STACK, docker, sql
    if not re.fullmatch(r'resgrid-academy-[a-z0-9][a-z0-9-]{0,40}', STACK):
        raise ValueError('A named isolated Academy stack is required.')
    if not os.environ.get('DOCKER_HOST', 'unix://local').startswith('unix://'):
        raise ValueError('Only a local Unix-socket Docker endpoint is supported.')
    endpoint = json.loads(docker('context', 'inspect', '--format', '{{json .Endpoints.docker.Host}}', capture_output=True).stdout)
    if not isinstance(endpoint, str) or not endpoint.startswith('unix://'):
        raise ValueError('Only a local Unix-socket Docker context is supported.')
    internal = docker('network', 'inspect', STACK + '_training', '--format', '{{.Internal}}', capture_output=True).stdout.strip()
    project = docker('inspect', STACK + '-postgres-1', '--format', '{{index .Config.Labels "com.docker.compose.project"}}', capture_output=True).stdout.strip()
    if internal != 'true' or project != STACK:
        raise ValueError('The named internal Academy training stack is required.')
    return sql(query, db='resgrid_academy')


def read_report(raw, expected_state):
    # Publish only the known non-secret result shape, never SQL/stderr/headers.
    candidates = [json.loads(line) for line in raw.splitlines() if line.startswith('{')]
    if len(candidates) != 1:
        raise ValueError('Exactly one fixture result is required.')
    result = candidates[0]
    required = {
        'scenario': 'fictional reserve apparatus station status location',
        'unit_id': 51006, 'department_id': 51, 'expected_state': STATES[expected_state],
        **POSITION, 'status_fields_preserved': True, 'note_preserved': True,
        'prior_history_preserved': True, 'events_emitted': False,
        'live_location_written': False, 'source': SOURCE,
    }
    for key, value in required.items():
        if type(result.get(key)) is not type(value) or result[key] != value:
            raise ValueError('Fixture result does not match its declared guards.')
    for key in ('previous_status_id', 'status_id'):
        if type(result.get(key)) is not int or result[key] <= 0:
            raise ValueError('Fixture status identity is missing.')
    if type(result.get('appended')) is not bool:
        raise ValueError('Fixture append result is missing.')
    if result['appended'] == (result['status_id'] == result['previous_status_id']):
        raise ValueError('Fixture append identities disagree.')
    return {**required, **{key: result[key] for key in ('previous_status_id', 'status_id', 'appended')}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--plan', action='store_true', help='Offline description (default); no database inspection.')
    action.add_argument('--write-training-fix', action='store_true', help='Append one guarded simulated status location in the isolated stack.')
    parser.add_argument('--expected-state', choices=tuple(STATES), help='Required exact latest state for a write.')
    parser.add_argument('--expected-note', help='Required exact latest single-line Reserve Engine 51 TRAINING ONLY note for a write.')
    args = parser.parse_args(argv)
    if args.write_training_fix and (args.expected_state is None or args.expected_note is None):
        parser.error('--write-training-fix requires --expected-state and --expected-note.')
    if args.expected_note is not None:
        try:
            validate_note(args.expected_note)
        except ValueError as error:
            parser.error(str(error))
    if not args.write_training_fix:
        print(json.dumps({
            'state_changes': 'none', 'database_contacted': False,
            'unit': {'id': 51006, 'department_id': 51, 'name': 'Reserve Engine 51', 'type': 'Engine', 'station_group_id': 51001},
            'position': POSITION, 'source': SOURCE,
            'write_option': '--write-training-fix --expected-state Available|OutOfService --expected-note EXACT_NOTE',
            'guards': ['local Unix-socket Docker; named internal Academy network', 'resgrid_academy; exact department, station and reserve apparatus identity', 'caller-explicit exact latest status and training note', 'refuse changed coordinates, protected values, future timestamps and crew assignments', 'transaction and table lock; preserve all other status fields and every history row', 'no-op when the same fixture point is already present'],
            'appended_fields': ['new status identity', 'fresh UTC timestamp and corresponding local timestamp', 'declared simulated latitude, longitude and location text'],
            'limits': ['No physical GPS, live-location document, application event, notification or provider operation.', 'Application map visibility and style must be verified separately through normal UI.'],
        }, indent=2))
        return 0
    try:
        result = read_report(execute_query(build_query(args.expected_state, args.expected_note)), args.expected_state)
    except Exception:
        # Docker/SQL errors may contain configuration or caller text. The tool
        # intentionally refuses to echo them into public source reports.
        print('Fixture write failed or was refused. No successful fixture report was written; review the guarded state locally before retrying.', file=sys.stderr)
        return 1
    output = ROOT / 'scenario-reports' / 'fresh-training-unit-position.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
