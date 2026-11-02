#!/usr/bin/env python3
"""Plan public configuration replay; optionally prepare ignored local SMTP fields.

Never writes application data, invokes a provider, creates an event, enables a
workflow, or fabricates execution history. Normal UI replay handles persistence.
"""
import argparse
import json
import os
from pathlib import Path
import secrets
import sys

DEMO = Path(__file__).resolve().parents[1]
FIXTURE = Path(__file__).with_name('core-configuration.json')


def load_fixture(path=FIXTURE):
    data = json.loads(Path(path).read_text())
    if data.get('schema_version') != 1 or data.get('id') != 'core-configuration-training':
        raise ValueError('Unknown training fixture.')
    guard = data['guard']
    if guard['database'] != 'resgrid_academy' or guard['department_id'] != 51 or guard['department_name'] != 'Firehouse 51 — Training Department':
        raise ValueError('Only the seeded fictional Academy department is supported.')
    fields = data['credential']['fields']
    if fields['SmtpHost'] != 'mail' or fields['SmtpPort'] != 1025 or fields['SmtpUsername'] or fields['SmtpUseSsl']:
        raise ValueError('SMTP replay is restricted to the unauthenticated internal Mailpit sink.')
    if any(workflow['enabled'] for workflow in data['workflows']):
        raise ValueError('Replay workflows must remain disabled.')
    if any(card['auto_dispatch_override'] != 'PrepopulateOnly' for card in data['run_cards']):
        raise ValueError('Replay cards must remain prepopulate-only.')
    if data['dispatch_settings']['automatically_dispatch_recommended_resources'] or data['dispatch_settings']['dispatch_freed_units_to_waiting_calls']:
        raise ValueError('Automatic dispatch must remain off.')
    forbidden = {'password', 'smtppassword', 'encrypteddata', 'credentialid', 'workflowcredentialid',
                 'passwordhash', 'securitystamp', 'privatekey', 'publicjwks', 'access_token', 'refresh_token'}
    def inspect(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key.lower().replace('_', '') in {item.replace('_', '') for item in forbidden}:
                    raise ValueError('Public fixtures cannot store credential or authentication fields.')
                inspect(child)
        elif isinstance(value, list):
            for child in value:
                inspect(child)
    inspect(data)
    return data


def verify_identity(identity, fixture):
    guard = fixture['guard']
    if identity.get('database') != guard['database'] or identity.get('department_id') != guard['department_id'] or identity.get('department_name') != guard['department_name']:
        raise ValueError('The database is not the isolated seeded fictional Academy department; nothing was changed.')
    if len(identity.get('unit_names', [])) != len(guard['required_units']) or set(identity.get('unit_names', [])) != set(guard['required_units']):
        raise ValueError('The six seeded fictional units are required; preserve other data and use the intended training stack.')
    if not identity.get('catalogs_match'):
        raise ValueError('Required fictional baseline catalogs are missing; no local settings were written.')


def read_identity(demo=DEMO):
    sys.path.insert(0, str(demo))
    from manage import sql, STACK
    if not STACK.startswith('resgrid-academy-'):
        raise ValueError('A separately named Academy recording stack is required.')
    # An explicit allowlist; never select credential, identity-secret or history tables.
    query = """SELECT json_build_object(
      'database',current_database(),
      'department_id',(SELECT departmentid FROM departments WHERE departmentid=51),
      'department_name',(SELECT name FROM departments WHERE departmentid=51),
      'unit_names',(SELECT json_agg(name ORDER BY name) FROM units WHERE departmentid=51),
      'catalogs_match',EXISTS(SELECT 1 FROM unittypes WHERE departmentid=51 AND type='Engine')
       AND EXISTS(SELECT 1 FROM personnelroles WHERE departmentid=51 AND name='Officer')
       AND EXISTS(SELECT 1 FROM calltypes WHERE departmentid=51 AND type='Structure Fire')
       AND EXISTS(SELECT 1 FROM departmentcallpriorities WHERE departmentid=51 AND name='Urgent'));"""
    return json.loads(sql(query))


def write_local_settings(fixture, identity, demo=DEMO):
    verify_identity(identity, fixture)
    demo = Path(demo).resolve()
    private = demo / 'private'
    folder = private / 'scenarios'
    target = folder / 'core-workflow-smtp.json'
    if private.is_symlink() or folder.is_symlink() or target.is_symlink():
        raise ValueError('Local settings paths cannot be symlinks.')
    fields = fixture['credential']['fields']
    if target.exists():
        existing = json.loads(target.read_text())
        stored = existing.get('fields', {})
        if existing.get('department_id') != 51 or any(stored.get(key) != value for key, value in fields.items()) or not stored.get('SmtpPassword'):
            raise ValueError('Existing local SMTP settings differ; preserve them and review manually.')
        return {'status': 'reused', 'file': str(target)}
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    folder.chmod(0o700)
    generated = dict(fields, SmtpPassword=secrets.token_urlsafe(32))
    payload = {'schema_version': 1, 'department_id': 51, 'fields': generated,
               'purpose': 'Manual local Mailpit credential form only; not an execution or provider connection test.'}
    # Exclusive creation prevents a concurrent run from replacing another local value.
    with open(target, 'x', encoding='utf-8', opener=lambda path, flags: os.open(path, flags, 0o600)) as handle:
        handle.write(json.dumps(payload, indent=2) + '\n')
    return {'status': 'created', 'file': str(target)}


def plan(fixture):
    return {'fixture': str(FIXTURE), 'mode': 'manual UI replay', 'steps': fixture['replay_order'],
            'state_changes': 'none', 'credential_values': 'not generated or printed',
            'guide': str(FIXTURE.with_name('README.core-configuration.md'))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--plan', action='store_true', help='Read the public fixture without Docker or writes (default).')
    modes.add_argument('--write-local-settings', action='store_true', help='Verify fictional baseline read-only and create/reuse ignored SMTP form values; never print them.')
    args = parser.parse_args()
    fixture = load_fixture()
    if args.write_local_settings:
        result = write_local_settings(fixture, read_identity())
    else:
        result = plan(fixture)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError) as error:
        raise SystemExit(str(error)) from error
