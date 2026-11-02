#!/usr/bin/env python3
"""Read-only factual assessment of the actual UNREVIEWED bridge drafts.

This is deliberately not a review/gate bypass. It reconstructs exact factual
draft bytes from the original freeze/addenda, rehashes public dependencies and
checks measured geometry/chronology. The ordinary public validator must still
REJECT every draft because its named review fields are null. No review is
invented, no private roots are read and no source package is modified.
"""
import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
S = ROOT / 'sources'
sys.path.insert(0, str(HERE / 'proposed/scripts'))
import native_capture_public as n
from prepare_actual_drafts import OUT, plan, timestamp

PRIVATE_REPORT = 'expansion/audits/unit-native-context-addendum-20261028/proposed-private-context-preflight.json'
PRIVATE_SHA = 'df3700f77db9152047aba9526be748a23c901e2b57374a39cce9ba4bfbfdc1ee'


def assessment():
    expected_files, expected_index = plan()
    for name, body in expected_files.items():
        path = OUT / name
        n.need(path.is_file() and path.read_bytes() == body,
               'actual draft differs from reproducible frozen-source normalization: ' + name)
    checker = n.PublicCheck(S)
    index = checker.asset({'file': (OUT / 'bridge-index.DRAFT.json').relative_to(S).as_posix(),
                           'sha256': n.sha(OUT / 'bridge-index.DRAFT.json')}, 'actual draft index')
    n.need(index == expected_index, 'actual index differs from retained factual normalization')
    seen = set()

    def dependencies(value):
        if isinstance(value, dict):
            if set(value) == {'file', 'sha256'}:
                key = (value['file'], value['sha256'])
                if key in seen:
                    return
                seen.add(key)
                suffix = Path(value['file']).suffix
                kind = 'png' if suffix == '.png' else 'json' if suffix == '.json' else 'source'
                loaded = checker.asset(value, 'actual retained public dependency', kind)
                if kind == 'png':
                    checker.png(loaded)
                elif kind == 'json':
                    dependencies(loaded)
            else:
                for child in value.values():
                    dependencies(child)
        elif isinstance(value, list):
            for child in value:
                dependencies(child)

    # Traverse the proposed public package dependency graph. The immutable
    # authoring freeze is independently rehashed by plan(); its unrelated TXT
    # narration/replay helpers are not native source-snapshot dependencies.
    dependencies([entry['package'] for entry in index['packages']])
    private = checker.asset({'file': PRIVATE_REPORT, 'sha256': PRIVATE_SHA},
                            'actual owner private-byte comparison report')
    pr = private['result']
    n.need(private['normal_ui_interactions'] is False and
           private['writes_to_apps_or_private_roots'] is False and
           pr['private_context_matches_review_candidate'] is True and
           pr['review_still_required'] is True and pr['review_flags_generated'] is False and
           pr['publishable'] is False, 'private comparison must remain read-only and unreviewed')
    parent = checker.asset(index['retained_parent_pixel_review'], 'existing parent source review')
    owner = checker.asset(index['original_owner_pixel_review'], 'existing owner source review')
    parent_hashes = {r['sha256'] for r in parent['source_images']}
    owner_hashes = {r['sha256'] for r in owner['sources']}
    installed_groups, runtime_groups = defaultdict(list), defaultdict(list)
    captures = []
    for entry in index['packages']:
        package = checker.asset(entry['package'], 'actual draft package')
        b, cap, rt = package['build'], package['capture'], package['runtime']
        identity = checker.asset(b['installed_correspondence'], 'pending installed review')
        runtime_review = checker.asset(rt['review_receipt'], 'pending served-context review')
        normal_ui = checker.asset(package['normal_ui'], 'actual normalized UI guard')
        original_ui = checker.asset(normal_ui['source_ledger'], 'original complete UI ledger')
        display = checker.asset(cap['display'], 'actual normalized geometry')
        metadata = checker.asset(entry['source_native_metadata'], 'original native sidecar')
        source_guard = metadata['native_accessibility_observation']
        source_prov = metadata['provenance']
        guard = source_guard['result']
        n.need(package['schema'] == n.SCHEMA and package['app'] == 'Unit' and
               cap['method'] == source_prov['method'] == 'ios_simulator_screenshot' and
               source_prov['exit_code'] == 0, 'actual native capture method differs')
        n.need(source_prov['simulator_udid'] == package['session']['udid'] and
               cap['foreground_bundle_id'] == guard['bundle_id'] == n.BUNDLE and
               guard['state'] == 'running_foreground', 'actual same-device foreground app identity differs')
        command = source_prov['command']
        tokens = command if isinstance(command, list) else command.split()
        n.need(all(t in tokens for t in ['simctl', 'io', 'screenshot', package['session']['udid']]),
               'actual screenshot did not retain explicit own-device simctl method')
        measured, captured = timestamp(source_guard['at']), timestamp(cap['captured_at'])
        age = (captured - measured).total_seconds()
        n.need(0 <= age <= 60 and display['measured_at'] == source_guard['at'],
               'actual geometry/normal-UI guard exceeds agreed60second bound')
        points = guard['app_frame_points']
        n.need(display['app_viewport_points'] == points == {'x': 0, 'y': 0, 'width': 1366, 'height': 1024}
               and display['dpr'] == guard['screen_scale'] == 2 and guard['device_orientation'] == 3
               and (cap['width'], cap['height']) == (2732, 2048), 'actual DPR/fullscreen geometry differs')
        n.need(checker.png(S / cap['image']['file']) == (2732, 2048), 'actual raw PNG dimensions differ')
        original_hashes = {n.digest(row) for row in original_ui['entries']}
        n.need(len(normal_ui['actions']) == 1 and
               normal_ui['actions'][0]['source_entry_sha256'] in original_hashes and
               normal_ui['actions'][0]['at'] == source_guard['at'], 'exact original guard source binding differs')
        for row in original_ui['entries']:
            action = row.get('request', {}).get('action')
            time = row.get('response', {}).get('at')
            if action in {'landscape', 'portrait', 'rotate', 'set_orientation', 'setorientation',
                          'resize', 'switch_device', 'select_device', 'change_window'} and time:
                n.need(not measured < timestamp(time) <= captured, 'actual intervening geometry/device action')
        scope = identity['recording_session']
        start, end = timestamp(scope['started_at']), timestamp(scope['ended_at'])
        binary = timestamp(identity['observation_at'])
        n.need(start <= captured <= end and start <= binary <= end and
               (end-start).total_seconds() == 2015.473473 and
               scope['installation_continuity_claimed'] is False and
               scope['continuous_execution_identity_proven'] is False,
               'actual reviewed-session chronology or honest installation limits differ')
        n.need(scope['product_managed_native_source_unchanged'] is None,
               'source attestation must remain pending named context review')
        inventory = checker.asset(b['installed_mach_o_inventory'], 'actual complete code inventory')
        code = n.validate_mach_o_inventory(inventory, b['bundle_id'])
        snapshots = checker.asset(b['snapshot_manifest'], 'actual public source snapshots')
        n.need(n.build_digest(b) == pr['identity_sha256'] and
               code == pr['installed_mach_o_files'] and len(code) == 25 and
               len(snapshots['snapshots']) == len(pr['source_snapshots']) == 16,
               'private report does not cover this actual shared build/source identity')
        ledger = checker.asset(rt['served_ledger'], 'original served metadata ledger')
        n.need(rt['loaded_or_executed_identity'] == rt['complete_lazy_execution_graph'] == 'unresolved'
               and rt['transport_client_identity'] == 'not_authenticated_by_transport',
               'served metadata was promoted to executed identity')
        for item in rt['selected_streams']:
            stream = ledger['entries'][item['entry_index']]
            n.need(item['entry_sha256'] == n.digest(stream) and
                   stream['status'] == 200 and stream['completed'] is True and
                   stream['body_saved'] is False and stream['body_or_query_logged'] is False and
                   timestamp(stream['finished_at']) <= captured, 'actual selected stream differs')
        labels = package['observations']['visible_labels']
        n.need(len(labels) == len(set(labels)) and labels == package['observations']['required_labels'],
               'actual literal label lists differ or contain duplicates')
        n.need(cap['image']['sha256'] in parent_hashes & owner_hashes,
               'actual PNG is absent from existing independent source reviews')
        for record in [identity, runtime_review, package['review']]:
            n.need(all(record[k] is None for k in ['reviewer', 'reviewed_at', 'method', 'findings']),
                   'draft unexpectedly contains newly authored review approval')
        n.need(all(v is None for v in package['review']['checks'].values()),
               'draft source checks must remain unreviewed')
        n.need(identity['binding_sha256'] == n.installed_review_digest(b, identity) and
               runtime_review['binding_sha256'] == n.digest({k:v for k,v in rt.items() if k != 'review_receipt'}) and
               package['review']['binding_sha256'] == n.review_digest(package),
               'draft pending binding digest differs')
        try:
            n.validate_public_package(package, S)
        except ValueError as error:
            rejection = str(error)
            n.need('installed correspondence.reviewer must contain specific nonempty text' in rejection,
                   'unexpected actual draft gate failure: ' + rejection)
        else:
            raise ValueError('An unreviewed actual draft was unexpectedly accepted.')
        installed_groups[identity['binding_sha256']].append(entry['id'])
        runtime_groups[runtime_review['binding_sha256']].append(entry['id'])
        captures.append({'id': entry['id'], 'package': entry['package'],
                         'raw_png': cap['image'], 'captured_at': cap['captured_at'],
                         'guard_and_geometry_at': source_guard['at'], 'actual_guard_age_seconds': age,
                         'actual_binary_to_capture_seconds': (captured-binary).total_seconds(),
                         'existing_owner_and_parent_png_reviews_rehashed': True,
                         'source_review_still_pending': True, 'ordinary_public_gate_rejection': rejection})
    return {
        'kind': 'actual_native_public_draft_fact_assessment_not_review_or_qualification',
        'observed_at': datetime.now(timezone.utc).isoformat(), 'proposal_only': True, 'publishable': False,
        'new_passed_review_generated': False, 'production_gate_adopted': False,
        'drafts_reconstructed_byte_identically': len(captures), 'draft_files_compared': len(expected_files),
        'retained_public_dependency_files_rehashed': len(seen),
        'source_freeze': index['immutable_source_freeze'],
        'actual_private_comparison': {'file': PRIVATE_REPORT, 'sha256': PRIVATE_SHA},
        'private_comparison_observed_at': private['observed_at'],
        'shared_build_identity_sha256': pr['identity_sha256'], 'complete_mach_o_files': 25,
        'source_and_lock_snapshots': 16, 'recording_session': index['recording_session'],
        'actual_guard_age_seconds': {'minimum': min(x['actual_guard_age_seconds'] for x in captures),
                                     'maximum': max(x['actual_guard_age_seconds'] for x in captures)},
        'fit_facts_not_legibility_approval': {'raw_pixels': [2732,2048], 'logical_points': [1366,1024],
            'dpr': 2, 'raw_pixel_scale': .4453125, 'output_pixels_per_logical_point': .890625,
            'fitted_pixels': [1217,912], 'no_crop': True},
        'pending_installed_review_binding_groups': dict(installed_groups),
        'pending_served_review_binding_groups': dict(runtime_groups),
        'actual_draft_packages_qualified': 0, 'captures': captures,
        'remaining_named_review_findings': [
            'Confirm exact reviewed-session build/source/device bindings and actual initial/fresh25MachO comparisons; retain instrumentation09/10 events, possible identical reinstall and absent historical driver digests as limits. Set product_managed_native_source_unchanged only from the real named context review.',
            'Name reviewer, actual review time, method and findings for the original served-response metadata association. State client/load/lazy execution identity remains unresolved; no full execution or uninterrupted-install assertion.',
            'Rebind each actual PNG and literal label list to existing owner/root source observations with specific foreground/fullscreen/control/privacy/normal-UI findings. No new pixel inspection is claimed by this assessment.',
            'Review receipts must bind final reviewed bytes. Authoring actual reviews changes dependent hashes; regenerate new reviewed packages separately and rerun the ordinary strict gate. These immutable draft packages remain rejected.',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = assessment()
    if args.output:
        path = args.output.resolve()
        n.need(path.is_relative_to(HERE) and not path.exists(), 'write only a NEW proposal-local assessment')
        path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({k: result[k] for k in ['proposal_only','publishable','drafts_reconstructed_byte_identically',
        'retained_public_dependency_files_rehashed','complete_mach_o_files','source_and_lock_snapshots',
        'actual_guard_age_seconds','actual_draft_packages_qualified']}, indent=2))


if __name__ == '__main__':
    main()
