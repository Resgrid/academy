"""Add only the two BigBoard loopback origins to an existing isolated training config.

Default is read-only. --apply preserves every other value and retains a private
before-copy. --stage-runtime also updates only that field in the named training
config volume. Restart the local API and eventing services after staging.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess

DEMO = Path(__file__).resolve().parents[2]
ORIGINS = ['http://localhost:19105', 'http://127.0.0.1:19105']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--stage-runtime', action='store_true')
    args = parser.parse_args()
    result = dict(private_files=[], original_config_mutations=0, applied=False)
    for filename in ('ResgridConfig.json', 'EventingConfig.json'):
        file = DEMO / 'private' / filename
        original = file.read_bytes()
        config = json.loads(original)
        assert 'Database=resgrid_academy;' in config.get('DataConfig.ConnectionString', '')
        assert config.get('SystemBehaviorConfig.ResgridBaseUrl') == 'http://127.0.0.1:18967'
        assert str(config.get('SystemBehaviorConfig.DoNotBroadcast')).lower() == 'true'
        before = config.get('ApiConfig.CorsAllowedOrigins', '').split(',')
        additions = [origin for origin in ORIGINS if origin not in before]
        result['private_files'].append(dict(file=filename, added_loopback_origins=additions))
        if args.apply and additions:
            backup = file.with_name(file.stem + '.before-bigboard-20261101.private.json')
            assert not backup.exists(), 'Preserve the earlier private before-copy.'
            with backup.open('xb') as stream:
                os.fchmod(stream.fileno(), 0o600)
                stream.write(original)
            updated = dict(config)
            updated['ApiConfig.CorsAllowedOrigins'] = ','.join([*before, *additions])
            assert {k: v for k, v in updated.items() if k != 'ApiConfig.CorsAllowedOrigins'} == {k: v for k, v in config.items() if k != 'ApiConfig.CorsAllowedOrigins'}
            assert file.read_bytes() == original, 'The config changed after it was read.'
            with file.open('r+') as stream:
                stream.seek(0)
                stream.write(json.dumps(updated, indent=2) + '\n')
                stream.truncate()
                stream.flush()
                os.fsync(stream.fileno())
            assert json.loads(file.read_text()) == updated
            result.update(applied=True, original_config_mutations=result['original_config_mutations'] + 1,
                          only_field_changed='ApiConfig.CorsAllowedOrigins')
    if args.stage_runtime:
        assert args.apply, 'Runtime staging needs the explicit --apply switch.'
        stack = json.loads((DEMO / 'private/stack.json').read_text())['name']
        assert stack.startswith('resgrid-academy-') and all(c.isalnum() or c == '-' for c in stack)
        volume = stack + '_config'
        actual = subprocess.check_output(['docker', 'volume', 'inspect', '--format', '{{.Name}}', volume], text=True).strip()
        assert actual == volume, 'The named local training volume must already exist.'
        # The stack uses a named config volume, not the source private file.
        # Update its allowlist in place; do not restage binaries or other fields.
        program = """import json,os
from pathlib import Path
results=[]
for filename in ['ResgridConfig.json','EventingConfig.json']:
 p=Path('/config')/filename;raw=p.read_bytes();before=json.loads(raw)
 assert 'Database=resgrid_academy;' in before.get('DataConfig.ConnectionString','')
 assert before.get('SystemBehaviorConfig.ResgridBaseUrl')=='http://127.0.0.1:18967'
 assert str(before.get('SystemBehaviorConfig.DoNotBroadcast')).lower()=='true'
 origins=before.get('ApiConfig.CorsAllowedOrigins','').split(',')
 added=[v for v in ['http://localhost:19105','http://127.0.0.1:19105'] if v not in origins]
 after=dict(before);after['ApiConfig.CorsAllowedOrigins']=','.join([*origins,*added])
 assert p.read_bytes()==raw
 if added:
  with p.open('r+') as f:
   f.seek(0);f.write(json.dumps(after,indent=2)+'\\n');f.truncate();f.flush();os.fsync(f.fileno())
 assert json.loads(p.read_text())==after
 results.append({'file':filename,'runtime_loopback_origins_added':added,'other_runtime_values_changed':0})
print(json.dumps(results))
"""
        completed = subprocess.run(['docker', 'run', '--rm', '--network', 'none', '--mount',
                                    'type=volume,source=' + volume + ',target=/config',
                                    'python:3.13-alpine', 'python', '-c', program],
                                   check=True, text=True, capture_output=True)
        result['runtime'] = json.loads(completed.stdout)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
