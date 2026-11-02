"""Retain exact native Unit call source/context packages, without app operations.

Default checks existing packages or previews inputs. --write creates a NEW
source-only package directory. This binds separately retained pre/post-spinner
sources to actual earlier binary observations and actual per-capture guards.
It never reads sign-in receipts, env values, credentials, binaries or keychain.
No video, hearing, browser playback, canonical readiness or publication claimed.
"""
import argparse
from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
ARTIFACT = ROOT.parent
NATIVE = ARTIFACT / 'native-unit-20261028'
B = Path('expansion/plans/app-unit-call-lifecycle-native-candidate-20261030')
PROJ = Path('expansion/plans/unit-native-call-public-source-projection-20261029')
OUT = Path('expansion/plans/app-unit-call-lifecycle-native-context-reviewed-20261030')
BASELINE = Path('production/proposals/native_public_integration_review_v3_20261028/actual-reviewed-20261029/packages/unit-native-20261028-007-native-settings.reviewed.json')
SPINNER = Path('production/native-unit-call-set-active-compatibility-20261029')
REVIEWER = 'Codex source-context reviewer /root/remaining_responder_unit'
REVIEWED_AT = '2026-10-30T21:12:28+00:00'
PINS = {
    PROJ / 'native-context.public.json': 'b6647b52957c284f7ccec941317290c502c45662501bdbe282b1191e5ac1c77c',
    PROJ / 'native-captures.public.json': 'bedba95fd5e88993815ae4344a934722e4580ef7ed50706736de6e6260b1d430',
    B / 'source-freeze.json': 'f3b3ffb533e9b73a1508aa3fe3c473aebb63a117c58caec688356e53d8376c15',
    BASELINE: '13366e307be2d01fdff59142b49ebe2c937a8456b50afe53d77e7d1180214b27',
    SPINNER / 'before/src/app/call/[id].tsx': 'e6f88c2b1468959840f7fe81b32b2637ee1982f35be4f9aefc5cfd8e4596d605',
    SPINNER / 'after/src/app/call/[id].tsx': '30afe9ef7fbb2372b77c69d61c2079a5c60ce55c54c58a703bd021f933bebac1',
}
sys.path.insert(0, str(ROOT / 'scripts'))
import native_capture_public as n


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return n.unique_json(p.read_text())
def encoded(d): return (json.dumps(d, ensure_ascii=False, indent=2) + '\n').encode()
def when(s): return datetime.fromisoformat(s.replace('Z', '+00:00'))


def prepare():
    assert __debug__
    for rel, digest in PINS.items(): assert sha(S / rel) == digest, 'Changed native source input: ' + str(rel)
    freeze = read(S / B / 'source-freeze.json')
    for item in freeze['files']:
        assert sha(S / item['file']) == item['sha256'], 'Changed frozen candidate member.'
    root_review_file = S / 'expansion/plans/app-unit-call-lifecycle-native-root-source-review-20261030.json'
    root_review = read(root_review_file)
    assert root_review['reviewer'] == 'Root' and root_review['actual_native_images_viewed'] == 23
    assert root_review['lesson_sha256'] == freeze['lesson_sha256'] and root_review['full_script_approved_for_narration'] is True
    owned = read(S / B / 'captures.native-reviewed.json')['native_sources']
    source_rows = read(S / PROJ / 'native-captures.public.json')['captures']
    originals = {Path(r['metadata']['file']).stem: r for r in source_rows}
    contexts = read(S / PROJ / 'native-context.public.json')['contexts']
    binary_contexts = [r for r in contexts if Path(r['original_file']).name.startswith('call-fresh-session-private-context-')]
    baseline = read(S / BASELINE)
    session = deepcopy(baseline['session'])
    b0 = deepcopy(baseline['build'])
    b0.pop('installed_correspondence')
    inventory = read(S / b0['installed_mach_o_inventory']['file'])
    baseline_manifest = read(S / b0['snapshot_manifest']['file'])
    files = {}
    inputs = {}

    def existing(ref):
        path = S / ref['file']
        assert sha(path) == ref['sha256']
        inputs[ref['file']] = ref['sha256']
        return deepcopy(ref)

    def put(name, document):
        body = document if isinstance(document, bytes) else encoded(document)
        assert not n.SECRET.search(body), 'Possible secret in selected public metadata/source; stop before writing.'
        assert name not in files
        files[name] = body
        return {'file': (OUT / name).as_posix(), 'sha256': hashlib.sha256(body).hexdigest()}

    # These exact public assets carry creation/native-code facts only. No prior
    # inventory pixel, session or runtime review is borrowed for call footage.
    for key in ('creation_receipt', 'creation_source'): existing(session[key])
    existing(b0['installed_mach_o_inventory'])
    for row in baseline_manifest['snapshots']: existing(row['snapshot'])
    revision = next(r['projection'] for r in contexts if Path(r['original_file']).name == 'managed-source-spinner-public-projection-20261029.json')
    assert revision['native_code_or_dependency_change'] is False
    prepared = {r['file']: r['sha256'] for r in revision['current_prepared_source_files']}
    # Only explicitly named nonsecret app screen/store components, never config.
    names = ['src/app/(app)/calls.tsx', 'src/app/call/new/index.tsx',
        'src/components/sidebar/call-sidebar.tsx', 'src/components/calls/call-card.tsx',
        'src/stores/app/core-store.ts', 'src/components/ui/bottom-sheet.tsx',
        'src/components/common/native-modal.tsx', 'src/components/status/status-bottom-sheet.tsx',
        'src/stores/status/store.ts', 'src/stores/calls/store.ts', 'src/stores/calls/detail-store.ts',
        'src/lib/status-flow.ts', 'src/lib/status-destination.ts', 'src/lib/unit-status-set.ts',
        'src/components/ui/spinner/index.tsx']
    common = []
    for name in names:
        p = NATIVE / 'source' / name
        assert sha(p) == prepared[name], 'Changed historically measured call source: ' + name
        common.append({'namespace': 'source', 'original_path': name, 'snapshot': put('snapshots/common/' + name, p.read_bytes())})
    manifests = {}
    for profile in ('pre-spinner', 'post-spinner'):
        before = profile == 'pre-spinner'
        source = SPINNER / ('before' if before else 'after') / 'src/app/call/[id].tsx'
        rows = deepcopy(baseline_manifest['snapshots']) + deepcopy(common)
        rows.append({'namespace': 'source', 'original_path': 'src/app/call/[id].tsx',
            'snapshot': existing({'file': source.as_posix(), 'sha256': PINS[source]})})
        manifests[profile] = put('normalized/' + profile + '.source-snapshots.json',
            {'base_source_revision': b0['base_source_revision'], 'snapshots': rows})

    new_stream_raw = next(r for r in contexts if Path(r['original_file']).name == '24dcf390-2e8d-4a3c-b3aa-17202d69068f.json')
    stream = deepcopy(new_stream_raw['projection'])
    stream['original_receipt_sha256'] = new_stream_raw['original_sha256']
    new_stream_ledger = put('normalized/post-spinner.served-metadata.json',
        {'kind': 'actual_served_packager_stream_receipts_not_execution_proof', 'source_only': True,
        'native_client_authenticated': False, 'loaded_or_executed_identity_proven': False,
        'lazy_load_set_complete': False, 'bodies_urls_queries_headers_frames_retained': False,
        'known_host_manifest_probe_present': False, 'entries': [stream]})
    baseline_ledger_ref = existing(baseline['runtime']['served_ledger'])
    baseline_ledger = read(S / baseline_ledger_ref['file'])
    packages = []
    shots = []
    for row in owned:
        ident = row['id']
        sequence = int(ident[:3])
        source = originals[ident]
        metadata = source['metadata']
        assert row['sha256'] == metadata['sha256'] == sha(S / row['file'])
        assert row['sha256'] in {r['sha256'] for r in root_review['images']}
        original_meta = S / source['original_metadata']['file']
        assert sha(original_meta) == source['original_metadata']['sha256']
        native_meta = read(original_meta)
        assert native_meta['provenance']['simulator_udid'] == session['udid']
        assert native_meta['provenance']['bundle_id'] == b0['bundle_id']
        assert native_meta['provenance']['command'][:3] == ['xcrun', 'simctl', 'io']
        at = row['captured_at']
        prior = [r for r in binary_contexts if when(r['projection']['observed_at']) <= when(at)]
        ctx = max(prior, key=lambda r: when(r['projection']['observed_at']))
        context = ctx['projection']
        result = context['result']
        age = (when(at) - when(context['observed_at'])).total_seconds()
        assert 0 <= age <= 600 and result['private_context_matches_review_candidate'] is True
        assert result['installed_binary_sha256'] == b0['installed_binary_sha256']
        assert result['installed_info_plist_sha256'] == b0['installed_info_plist_sha256']
        assert result['installed_mach_o_files'] == inventory['files']
        assert result['loaded_or_executed_identity_proven'] is False
        observed_static = {(r['namespace'], r['original_path']): r['sha256'] for r in result['source_snapshots']}
        assert all(observed_static[(r['namespace'], r['original_path'])] == r['snapshot']['sha256'] for r in baseline_manifest['snapshots'])
        profile = 'pre-spinner' if sequence <= 51 else 'post-spinner'
        if profile == 'post-spinner':
            assert context['managed_source_revision']['sha256'] == 'f568294fcc26afdc083eba9366b560bd530831206af38fc11656ba39721db936'
            comparisons = {x['file']: x for x in context['call_source_comparisons']}
            assert comparisons['src/app/call/[id].tsx']['managed_sha256'] == PINS[SPINNER / 'after/src/app/call/[id].tsx']
            assert all(x['equal'] is True for x in comparisons.values())
        context_ref = put('observations/' + ident + '.prior-binary-source.json',
            {'kind': 'explicit_public_projection_of_actual_prior_binary_source_observation',
            'original_file': ctx['original_file'], 'original_sha256': ctx['original_sha256'],
            'public_projection_file': (PROJ / 'native-context.public.json').as_posix(),
            'public_projection_sha256': PINS[PROJ / 'native-context.public.json'], 'observation': context,
            'actual_original_capture_metadata_sha256': source['original_metadata']['sha256'],
            'actual_capture_device_matches_dedicated_session': True, 'source_profile': profile})
        ax = metadata['native_accessibility_observation']
        guards = metadata['capture_privacy_guards']
        records = []
        for item in [ax, *guards]:
            rid = item['id']
            if sequence <= 51:
                p = NATIVE / 'call-ui-receipts' / (rid + '.json')
            else:
                matches = [r for r in contexts if Path(r['original_file']).name == rid + '.json' and 'normal-ui-ledger' in r['original_file']]
                assert len(matches) == 1
                p = S / matches[0]['original_file']
                assert sha(p) == matches[0]['original_sha256']
            record = read(p)
            assert record['request']['action'] in {'capture_guard', 'screen', 'snapshot', 'inspect', 'describe', 'dump', 'elements', 'observe', 'inspect_screen', 'screen_context', 'get_screen'}
            assert record['response']['id'] == rid and record['response']['at'] == item['at']
            # Exactly known captured screen/guard receipts, never sign-in input.
            records.append(record)
        records.sort(key=lambda r: when(r['response']['at']))
        ledger_ref = put('observations/' + ident + '.original-capture-guards.json',
            {'kind': 'actual_original_screen_and_capture_guard_receipts_only',
            'scope': 'Exact retained screen/guard receipt window for this PNG; not a full-session action or execution ledger.',
            'entries': records})
        guard = guards[-1]
        g = guard['result']
        assert g['capture_allowed'] is True and g['unit_foreground'] is True and g['device_orientation'] == 3
        assert g['screen_scale'] == 2 and g['app_frame_points'] == {'x': 0, 'y': 0, 'width': 1366, 'height': 1024}
        measured = g['geometry_observed_at']
        assert 0 <= (when(at) - when(measured)).total_seconds() <= 60
        display = put('normalized/' + ident + '.geometry.json',
            {'session_id': session['id'], 'udid': session['udid'], 'measured_at': measured,
            'method': 'xcuitest_frame_and_uiscreen_scale', 'orientation': 'landscape_left', 'dpr': 2,
            'screen_points': {'width': 1366, 'height': 1024}, 'app_viewport_points': g['app_frame_points'],
            'pixel_width': 2732, 'pixel_height': 2048})
        actions = [{'id': r['response']['id'], 'at': r['response']['at'], 'kind': 'observe_screen',
            'control': b0['bundle_id'], 'observation': 'Actual screen/capture guard observation retained; literal labels separately reviewed from the unchanged PNG, without invented accessibility names.',
            'source_entry_sha256': n.digest(r)} for r in records]
        normal = put('normalized/' + ident + '.normal-ui.json',
            {'session_id': session['id'], 'udid': session['udid'], 'bundle_id': b0['bundle_id'],
            'method': 'xcuitest', 'source_ledger': ledger_ref, 'actions': actions, 'geometry_events': []})
        b = deepcopy(b0)
        b['snapshot_manifest'] = manifests[profile]
        identity = {'reviewer': REVIEWER, 'reviewed_at': REVIEWED_AT,
            'method': 'Actual per-capture device/foreground/geometry receipt and independently retained complete Mach-O/plist/static source comparisons, with distinct exact pre/post-spinner call source snapshots. No continuous install, authenticated JS execution or whole lazy graph claim.',
            'binding_sha256': None, 'session_id': session['id'], 'udid': session['udid'],
            'foreground_bundle_id': b['bundle_id'], 'observation_at': context['observed_at'],
            'snapshot_manifest_sha256': b['snapshot_manifest']['sha256'], 'correspondence_scope': 'prior_capture_binary600',
            'recording_session': None, 'additional_binary_confirmations': [context_ref],
            'findings': 'Genuine complete25-Mach-O inventory, main binary, plist and all16 static source/lock snapshots agree at the prior observation. The actual PNG and capture command belong to the dedicated session. Call source profiles are declared separately; observed busy-indicator-only revision is retained exactly. Known adjacent guards preserve landscape/full viewport; absence of unrecorded actions or complete execution identity is not proven.'}
        identity['binding_sha256'] = n.installed_review_digest(b, identity)
        b['installed_correspondence'] = put('reviews/' + ident + '.installed-context.json', identity)
        if profile == 'pre-spinner':
            ledger = baseline_ledger_ref
            selected = [{'entry_index': r['entry_index'], 'entry_sha256': r['entry_sha256'],
                'association_method': 'reviewed_capture_context_only_not_authenticated',
                'build_identity_sha256': n.build_digest(b)} for r in result['stream_references']]
            assert all(n.digest(baseline_ledger['entries'][r['entry_index']]) == r['entry_sha256'] for r in selected)
        else:
            assert when(stream['finished_at']) <= when(at)
            ledger = new_stream_ledger
            selected = [{'entry_index': 0, 'entry_sha256': n.digest(stream),
                'association_method': 'reviewed_capture_context_only_not_authenticated', 'build_identity_sha256': n.build_digest(b)}]
        runtime = {'coverage': 'served_response_metadata_only', 'transport_client_identity': 'not_authenticated_by_transport',
            'loaded_or_executed_identity': 'unresolved', 'complete_lazy_execution_graph': 'unresolved',
            'lazy': True, 'served_ledger': ledger, 'selected_streams': selected}
        runtime['review_receipt'] = put('reviews/' + ident + '.served-context.json',
            {'reviewer': REVIEWER, 'reviewed_at': REVIEWED_AT,
            'method': 'Read the retained actual completed HTTP response metadata and hashes with capture chronology; source-context association only.',
            'binding_sha256': n.digest(runtime), 'session_id': session['id'], 'udid': session['udid'],
            'build_identity_sha256': n.build_digest(b), 'observed_entry_sha256': [r['entry_sha256'] for r in selected],
            'findings': 'Actual200 completed decoded-body stream metadata predates this PNG. No response body, URL/query, headers, credentials or key values retained. This does not authenticate the client, show JS executed or complete the lazy load graph.'})
        package = {'schema': n.SCHEMA, 'app': 'Unit', 'kind': 'application_screenshot', 'session': session, 'build': b,
            'capture': {'image': {'file': row['file'], 'sha256': row['sha256']}, 'width': 2732, 'height': 2048,
                'captured_at': at, 'method': 'ios_simulator_screenshot', 'session_id': session['id'], 'udid': session['udid'],
                'foreground_bundle_id': b['bundle_id'], 'simctl_method': 'xcrun_simctl_io_explicit_udid_screenshot_png', 'display': display},
            'normal_ui': normal, 'runtime': runtime,
            'observations': {'visible_labels': row['manual_visible_labels'], 'required_labels': row['manual_visible_labels']},
            'limitations': deepcopy(n.LIMITS)}
        package['review'] = {'reviewer': REVIEWER, 'reviewed_at': REVIEWED_AT,
            'method': 'Prior personal inspection of all23 unchanged actual PNGs at the tool-displayed1824x1367 size, plus the genuine Root23-image/full-script receipt and this separate exact source/context/guard review. No original-size pixel-authentication claim.',
            'binding_sha256': n.review_digest(package), 'checks': {k: True for k in n.REVIEW_CHECKS},
            'findings': 'Actual Unit application viewport, literal labels and referenced glyph locations were personally read. Same dedicated device, known adjacent full-viewport landscapeDPR2 guards and prior binary/source metadata are retained. No known intervening geometry change or private value was observed in this bounded recorded capture window. No inventory pixel approval borrowed. No hearing, video frame, public qualification or hardware suitability claimed.'}
        ref = put('packages/' + ident + '.reviewed.json', package)
        packages.append({'id': ident, 'package': ref, 'profile': profile, 'prior_binary_age_seconds': age,
            'geometry_age_seconds': (when(at) - when(measured)).total_seconds(),
            'guard_age_seconds': (when(at) - when(actions[-1]['at'])).total_seconds(),
            'actual_context_observation': context_ref, 'root_source_review_sha256': sha(root_review_file)})
        shots.append({'id': ident, 'app': 'Unit', 'kind': 'application_screenshot', 'file': row['file'], 'sha256': row['sha256'],
            'width': 2732, 'height': 2048, 'provenance': {'method': 'ios_simulator_screenshot', 'captured_at': at},
            'visible_labels': row['manual_visible_labels'], 'required_labels': row['manual_visible_labels'], 'native_review_package': ref})
    put('captures.reviewed.json', {'schema_version': 1, 'screenshots': shots})
    index = {'kind': 'Native Unit call source-context review only', 'reviewer': REVIEWER, 'reviewed_at': REVIEWED_AT,
        'parent_actual_pixel_script_review': {'file': root_review_file.relative_to(S).as_posix(), 'sha256': sha(root_review_file)},
        'frozen_candidate_sha256': PINS[B / 'source-freeze.json'], 'packages': packages, 'input_hashes': inputs,
        'source_profiles_retained_separately': True, 'prior_binary_observation_max_seconds': max(x['prior_binary_age_seconds'] for x in packages),
        'actual_known_capture_window_receipts_only': True, 'full_session_action_coverage_claimed': False,
        'inventory_pixel_or_recording_session_review_reused': False, 'device_or_app_operations': False,
        'audio_hearing_or_rendered_frame_review_claimed': False, 'canonical_or_site_changed': False, 'publishable': False}
    put('source-context-review-index.json', index)
    return files, index


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write', action='store_true')
    p.add_argument('--retain-validation', action='store_true', help='Retain NEW current-validator report for exact already prepared files.')
    a = p.parse_args()
    files, index = prepare()
    if a.write:
        assert not (S / OUT).exists(), 'Preserve existing native qualification history.'
        for name, body in files.items():
            path = S / OUT / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as f: f.write(body)
    reports = []
    if (S / OUT).exists():
        for name, body in files.items(): assert (S / OUT / name).read_bytes() == body, 'Changed retained native review member.'
        manifest = read(S / OUT / 'captures.reviewed.json')
        for row in manifest['screenshots']:
            report = n.validate_native_source(row, S, 'Unit')
            assert report['source_review_validated'] is True
            reports.append({'id': row['id'], 'layout': report['layout'], 'native_binding': report['native_binding'],
                'dependencies': [Path(p).relative_to(S).as_posix() for p in report['dependencies']], 'publishable': False})
        result = {'kind': 'Actual current unchanged native source validator result', 'source_packages_validated': len(reports),
            'validator_file': 'scripts/native_capture_public.py', 'validator_sha256': sha(ROOT / 'scripts/native_capture_public.py'),
            'packages': reports, 'publishable': False, 'canonical_or_site_changed': False}
        path = S / OUT / 'current-validator-report-v2.json'
        body = encoded(result)
        if a.write or a.retain_validation:
            with path.open('xb') as f: f.write(body)
        elif path.exists(): assert path.read_bytes() == body
    print(json.dumps({'files': len(files), 'packages': len(index['packages']), 'validated_packages': len(reports),
        'written': a.write, 'max_prior_binary_age_seconds': index['prior_binary_observation_max_seconds'],
        'render_or_hearing_or_publish_claimed': False}))


if __name__ == '__main__': main()
