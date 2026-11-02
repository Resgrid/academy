#!/usr/bin/env python3
"""Read-only real source validation, plus an isolated public-assets-only replay.

Uses the ordinary unmodified proposal validator. No SDK/private binary/npm/JS
roots are copied to the isolated replay. This supplies source evidence only;
it does not render, review frames, approve playback or publish a lesson.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
S = ROOT / 'sources'
sys.path.insert(0, str(HERE / 'proposed/scripts'))
import native_capture_public as n
from prepare_reviewed_packages import OUT, plan


def validation():
    expected, index = plan()
    for name, body in expected.items():
        n.need((OUT / name).read_bytes() == body, 'reviewed source differs from named-review builder: ' + name)
    check = n.PublicCheck(S)
    sources, results, dependencies = [], [], {}
    for entry in index['created_packages']:
        p = check.asset(entry['reviewed_package'], 'actual reviewed source package')
        c = p['capture']
        row = {'id': entry['id'], 'app': 'Unit', 'kind': 'application_screenshot',
               'file': c['image']['file'], 'sha256': c['image']['sha256'],
               'width': c['width'], 'height': c['height'],
               'provenance': {'method': c['method'], 'captured_at': c['captured_at']},
               **p['observations'], 'native_review_package': entry['reviewed_package']}
        report = n.validate_native_source(row, S, 'Unit')
        n.need(report['source_review_validated'] is True and report['publishable'] is False and
               report['pixel_authenticity_proven'] is False and report['executed_identity_proven'] is False,
               'source-only validation must retain actual trust limits')
        for path in report['dependencies']:
            relative = path.relative_to(S.resolve()).as_posix()
            dependencies[relative] = {'file': relative, 'sha256': n.sha(path)}
        sources.append(row)
        results.append({'id': entry['id'], 'reviewed_package': entry['reviewed_package'],
                        'source_review_validated': True, 'publishable': False,
                        'raw_png': c['image'], 'layout': report['layout'],
                        'native_binding': report['native_binding'],
                        'dependency_files': len(report['dependencies']),
                        'pixel_authenticity_proven': False, 'executed_identity_proven': False})
    # Replay with only exact public assets and the standard-library public
    # module, under isolated Python. The private helper is not copied/imported.
    with tempfile.TemporaryDirectory(prefix='academy-native-public-only-') as temp:
        base = Path(temp)
        assets, modules = base / 'assets', base / 'modules'
        modules.mkdir()
        shutil.copyfile(HERE / 'proposed/scripts/native_capture_public.py', modules / 'native_capture_public.py')
        for name in dependencies:
            target = assets / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(S / name, target)
        (base / 'sources.json').write_text(json.dumps(sources))
        program = '''import json,sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import native_capture_public as n
root=Path(sys.argv[2]);rows=json.loads(Path(sys.argv[3]).read_text());out=[]
for row in rows:
 report=n.validate_native_source(row,root,'Unit')
 out.append({'id':row['id'],'source_review_validated':report['source_review_validated'],
             'publishable':report['publishable'],'native_binding':report['native_binding']})
print(json.dumps(out))
'''
        proc = subprocess.run([sys.executable, '-I', '-B', '-c', program, str(modules), str(assets),
                               str(base / 'sources.json')], capture_output=True, text=True, check=False)
        n.need(proc.returncode == 0, 'public-assets-only replay rejected; inspect local failure without exposing private roots')
        offline = n.unique_json(proc.stdout)
        n.need(len(offline) == len(results) and
               all(o['id'] == r['id'] and o['source_review_validated'] is True and o['publishable'] is False and
                   o['native_binding'] == r['native_binding'] for o, r in zip(offline, results)),
               'public-only replay differs from exact reviewed source bindings')
        # A source row cannot approve itself, fabricate a browser URL, invent a
        # printed label or conceal a missing retained source asset.
        negatives = []
        for field, value in [('publishable', True), ('url', 'http://localhost.invalid/native')]:
            changed = dict(sources[0], **{field: value})
            try:
                n.validate_native_source(changed, assets, 'Unit')
            except ValueError:
                negatives.append({'case': field, 'rejected': True})
            else:
                raise ValueError('Native public source incorrectly accepted: ' + field)
        changed = dict(sources[0], visible_labels=sources[0]['visible_labels'] + ['Invented fixture label'])
        try:
            n.validate_native_source(changed, assets, 'Unit')
        except ValueError:
            negatives.append({'case': 'invented literal label', 'rejected': True})
        else:
            raise ValueError('Native public source incorrectly accepted an invented label.')
        css = next(name for name in dependencies if name.endswith('/theme-tokens.css'))
        (assets / css).unlink()
        try:
            n.validate_native_source(sources[0], assets, 'Unit')
        except ValueError:
            negatives.append({'case': 'missing retained CSS body', 'rejected': True})
        else:
            raise ValueError('Native public source incorrectly accepted missing retained source.')
    return {'kind': 'actual_reviewed_native_source_public_offline_validation_not_video_approval',
            'observed_at': datetime.now(timezone.utc).isoformat(), 'proposal_only': True, 'publishable': False,
            'production_gate_adopted': False, 'video_or_publication_approved': False,
            'source_review_attribution': 'Exact named parent context/binding review and existing owner/root displays; no new original-size manual inspection is claimed.',
            'reviewed_source_index': {'file': (OUT / 'reviewed-source-index.json').relative_to(S).as_posix(),
                                      'sha256': n.sha(OUT / 'reviewed-source-index.json')},
            'parent_context_review': index['parent_review'],
            'public_validator': {'file': (HERE / 'proposed/scripts/native_capture_public.py').relative_to(S).as_posix(),
                                 'sha256': n.sha(HERE / 'proposed/scripts/native_capture_public.py')},
            'source_packages_validated': len(results), 'public_only_replay_validated': len(offline),
            'public_only_replay': {'isolated_python': True, 'copied_public_dependency_files': len(dependencies),
                'private_helper_imported': False, 'sdk_or_npm_or_private_binary_or_js_roots_required': False,
                'all_bindings_equal': True},
            'negative_public_guards': negatives, 'sources': sources, 'results': results,
            'public_dependencies': sorted(dependencies.values(), key=lambda r: r['file']),
            'limits': index['limits']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = validation()
    if args.output:
        target = args.output.resolve()
        n.need(target.is_relative_to(HERE) and not target.exists(), 'write only a NEW proposal-local report')
        target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({k:report[k] for k in ['proposal_only','publishable','source_packages_validated',
        'public_only_replay_validated','public_only_replay','negative_public_guards']}, indent=2))


if __name__ == '__main__':
    main()
