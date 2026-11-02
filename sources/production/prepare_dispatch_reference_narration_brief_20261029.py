"""Prepare a bounded, exact-text Dispatch narration brief; no provider calls.

Default read-only. --write-brief creates a NEW text/JSON source package only.
Frozen scripts, captures, canonical lessons and media remain unchanged.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
NAME = 'app-dispatch-map-and-site-reference'
BASE = Path('expansion/plans') / (NAME + '-capture-freeze-20261029')
OUT = S / 'expansion/plans' / (NAME + '-narration-brief-20261029')
PINS = {
    BASE / 'source-freeze.json': '647cf025be0a86fb327243f4b95b1b4aecccdda5981f648242ef9b0e71b3aa59',
    BASE / (NAME + '.narrated-source.json'): 'b7753f1893ecc9881af038a7ac3b01380841583318df9dd46e0b906b7744837e',
    BASE / 'narration.frozen.txt': '5e8db2a4fd8fcfa4f168c0c0dace29fcfa41841ab2ffa838400674b06cb62994',
    BASE / 'captures.reviewed.json': '139b424d1e48fe3bb2f72e30eb05e7ffd2e6eb643a0d8a4069387a95be4af94c',
    BASE / 'ordered27span.accepted.json': '95389ab03e80d83cb6475c8bd6e295ae0587bde21f675fa83bf42c49188b9580',
    BASE / 'parent-freeze-acceptance.json': '3012e8dbe9c85e32f134d533e9cfbfbaa9e0112369f369ea974ec60830614860',
    BASE / 'known-values-audit.json': '55dc9503950cfb5cc91d9e9d7c9dcf77e113539168cd20037df4f1e174b90daf',
    BASE / 'original-review/literal-source-review.json': '2d9b84211e51bc3099b2caca63614ee9e9efac9ebde6bf0d27f33a46c276196d',
    Path('production/descript/voice-direction.json'): '9589e8344b6e2f50293b753d56ab433da5a745d05e983fbe9384e9fc915e6aee',
    Path('production/descript/natural/batch-02-04-request.txt'): '8618b1ccd49d706ea5f5f5cc8a2b29b1b3b739dc7cc1d181aa599d141db99b11',
}
SPOT_CHECKS = ['005-map-layers-staging-on', '006-map-layer-staging-hidden-state',
               '009-poi-list-all-types', '011-poi-search-staging', '016-contact-details-fictional-site',
               '020-contact-related-calls-empty', '021-settings-app-info-account', '022-settings-preferences-support-readonly']


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(part)
    return digest.hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def prepare():
    for path, digest in PINS.items():
        assert sha(S / path) == digest, 'Changed approved source: ' + str(path)
    freeze = json.loads((S / BASE / 'source-freeze.json').read_text())
    assert freeze['parent_whole_script_approved'] and not freeze['publication_approved']
    for path, digest in freeze['freeze_files'].items():
        assert sha(S / BASE / path) == digest, 'Changed frozen package asset: ' + path
    lesson = json.loads((S / BASE / (NAME + '.narrated-source.json')).read_text())
    narration = (S / BASE / 'narration.frozen.txt').read_text()
    assert narration == '\n\n'.join(x['narration'] for x in lesson['scenes']) + '\n'
    assert len(lesson['scenes']) == 8 and len(narration.split()) == 634 and len(lesson['sector_examples']) == 6
    manifest = json.loads((S / BASE / 'captures.reviewed.json').read_text())
    rows = {x['id']: x for x in manifest['screenshots']}
    mapping = json.loads((S / BASE / 'ordered27span.accepted.json').read_text())
    assert len(rows) == 21 and len(mapping['untimed_spans']) == 27
    assert ' '.join(x['exact_spoken_segment'] for x in mapping['untimed_spans']) == ' '.join(x['narration'] for x in lesson['scenes'])
    sys.path.insert(0, str(ROOT / 'scripts'))
    from verify_capture_evidence import _image_dimensions
    for row in rows.values():
        assert sha(S / row['file']) == row['sha256'] and sha(S / row['dom_file']) == row['dom_sha256']
        assert row['eligible_for_lesson'] and row['capture_review']['passed'] and row['capture_review']['sha256'] == row['sha256']
        assert _image_dimensions(S / row['file']) == (1434, 773)
    for span in mapping['untimed_spans']:
        row = rows[span['source_id']]
        assert (span['source_file'], span['source_sha256']) == (row['file'], row['sha256'])
        assert set(span['required_pixel_controls_or_context']) <= set(row['visible_labels']), 'Uncovered required control.'
        assert span['timing'] is None
    parent = json.loads((S / BASE / 'parent-freeze-acceptance.json').read_text())
    assert parent['parent_whole_script_approved'] and parent['ordered_source_correspondence_approved'] and parent['literal_glyph_finding_approved']
    paragraphs = [{'scene_id': x['id'], 'title': x['title'], 'exact_text': x['narration'],
                   'text_sha256': hashlib.sha256(x['narration'].encode()).hexdigest(),
                   'ordered_capture_ids': [p['source_id'] for p in mapping['untimed_spans'] if p['scene_id'] == x['id']]}
                  for x in lesson['scenes']]
    voice = {'name': 'Warm Lulu', 'library_voice_id': 'itMkRQx56fOF4CJe1D0C', 'language': 'en-US',
             'kind': 'existing approved stock voice convention; no cloned or imitated person',
             'delivery': 'Warm, relaxed, conversational instruction; clear labels and natural pauses.',
             'pace': 'Use natural unhurried delivery. Do not claim a rate setting or assign estimated duration.',
             'exact_words': True, 'paragraphs_generated_whole': True}
    brief = {'kind': 'exact_Dispatch_audio_generation_brief_only', 'lesson_id': NAME, 'title': lesson['title'],
             'frozen_source': {'file': (BASE / (NAME + '.narrated-source.json')).as_posix(), 'sha256': PINS[BASE / (NAME + '.narrated-source.json')]},
             'exact_script': {'file': (BASE / 'narration.frozen.txt').as_posix(), 'sha256': PINS[BASE / 'narration.frozen.txt']},
             'paragraphs': paragraphs, 'words_whitespace': 634, 'voice': voice,
             'source_coverage': {'actual_images': 21, 'untimed_spans': 27, 'uncovered_claims_or_controls': []},
             'completion_checks': ['Generate actual audible speech for every exact paragraph once; speaker assignment or a150-wpm estimated timeline is not evidence of generated media.',
                                   'Read back the stock voice identity and materialized speech assets; retain exact ordered transcript exports after generation.',
                                   'Obtain fresh SRT and genuine one-second TXT anchors for later control-aligned cuts; do not estimate word timings.',
                                   'Actual media export, full decoded-audio/per-cue QA and real User complete natural-listening approval remain separate later gates.'],
             'provider_mutation_performed_by_this_preparation': False, 'media_created': False,
             'timing_assigned': False, 'publication_approved': False}
    request = (
        'Prepare ONE NEW audio-only composition named "Dispatch: map layers and site references — Natural narration (Warm Lulu)". '
        'Preserve all existing projects and compositions. Generate actual speech for the eight exact paragraphs below, each once in order, using STOCK Warm Lulu, '
        'library voice ID itMkRQx56fOF4CJe1D0C (en-US; warm, relaxed narrative). Do not substitute another Lulu voice or clone a person.\n\n'
        'Use natural conversational delivery, clear screen labels and ordinary pauses between paragraphs. Preserve every word and qualification exactly: '
        'do not paraphrase, add a greeting/outro, insert spoken directions or alter names. Generate whole paragraphs; do not patch isolated words. '
        'No music, stock footage, avatars, visuals, new product claims or screenshot uploads. The real app screenshots will be assembled locally later. '
        'Do not publish, export media, share, change access or edit any existing composition.\n\n'
        'Verify the eight exact paragraphs appear once, with one stock speaker and actual generated speech media covering the full text. '
        'Return the new composition identity, verified voice and actual generated assets/status. If generation is incomplete, say precisely what remains; '
        'do not present estimated timeline duration or assigned scratch text as audible output. Narration contains six-sector examples in the final paragraph; retain them.\n\n'
        'BEGIN EXACT NARRATION (only these paragraphs are spoken)\n\n' + narration + '\nEND EXACT NARRATION\n')
    audit = {'kind': 'Dispatch_narration_source_screen_coverage_preflight', 'frozen_source_sha256': brief['frozen_source']['sha256'],
             'narration_sha256': brief['exact_script']['sha256'], 'freeze_sha256': PINS[BASE / 'source-freeze.json'],
             'exact_frozen_files_rehashed': len(freeze['freeze_files']), 'actual_images': 21, 'image_dimensions': [1434, 773],
             'paragraphs': 8, 'words_whitespace': 634, 'untimed_spans': 27, 'six_sectors_spoken_and_companions': True,
             'uncovered_claims_or_controls': [],
             'existing_pixel_review_basis': {'file': (BASE / 'original-review/literal-source-review.json').as_posix(), 'sha256': PINS[BASE / 'original-review/literal-source-review.json'],
                                            'method': 'Reuse exact-byte earlier actual original-source display reviews and separate parent full-script/27span acceptance. No new assertion that all21 were independently re-inspected today.'},
             'fresh_spot_checks_by_this_agent': {'source_ids': SPOT_CHECKS, 'method': 'Actual frozen JPEGs re-viewed through view_image(detail=original) while preparing this brief. Tool display review; no100-percent manual pixel-inspection claim.'},
             'constraints_for_later_assembly': [
                 'Show003 upper Menu for Map/POIs/Protocols/Contacts;024 lower Menu for Settings. Do not substitute offscreen entries.',
                 '005 is actual layer On;006 is Off and supplies the actual literal✕ plus Show All.007/008 are intact map comparison/restoration. Do not call✕ an invented named Close control.',
                 '009 shows empty Search POIs placeholder and All types/Name(A-Z);010 shows selected type;011 supplies entered Staging and full point card. One point cannot prove sorting changes.',
                 '013 is an actual empty Protocols result. No protocol, route operation or procedure execution is shown or claimed.',
                 '016 physical address and selected Details text are low contrast and excluded. Its name,Company,Contact Information,Email andOffice Phone are readable; no calling/emailing/address-link action is claimed.',
                 'For Notes/Pre-Plan/Files/Calls, preserve the exact27span order: readable unselected next-tab label precedes the result whose selected label has low contrast.020 empty Related calls is scoped to the contact query.',
                 '021 shows AppInfo name/version/environment and a truncated local training server value. No auth identifier, complete server value or server/security/shared/active-unit operation is spoken or linked.022 supplies all Preferences/Support labels.',
                 'No GPS/device arrival, wake lock/native hardware, provider delivery, new dispatch or record mutation is asserted. Existing authorised session is a prerequisite; sign-in is not demonstrated.',
                 'Actual SRT/one-second markers are still needed for future cuts, readable holds and caption alignment. No audio or duration exists in this package.'],
             'prior_known_value_audit': {'file': (BASE / 'known-values-audit.json').as_posix(), 'sha256': PINS[BASE / 'known-values-audit.json'], 'scope': 'Retained root17-known-value/58file audit; no new credential or token file reads.'},
             'browser_or_provider_or_canonical_or_site_operations': False}
    return brief, request, mapping, audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-brief', action='store_true')
    args = parser.parse_args()
    brief, request, mapping, audit = prepare()
    assets = {'narration-generation-brief.json': encoded(brief), 'descript-generation-request.txt': request.encode(),
              'source-screen-map.json': encoded(mapping),
              'source-screen-map.compact.txt': (S / BASE / 'ordered27span.compact.txt').read_bytes(),
              'source-screen-preflight.json': encoded(audit)}
    if args.write_brief:
        assert not OUT.exists(), 'New-only preparation; preserve held sources and prior packages.'
        spec = importlib.util.spec_from_file_location('ordinary_privacy', ROOT / 'scripts/audit_public_repo.py')
        privacy = importlib.util.module_from_spec(spec); spec.loader.exec_module(privacy)
        findings = [{'file': name, 'rule': rule} for name, body in assets.items() for rule in privacy.scan_bytes(body)]
        assert not findings, findings
        provenance = {'kind': 'new_only_narration_brief_preparation', 'helper_sha256': sha(__file__),
                      'input_hashes': {str(path): digest for path, digest in PINS.items()},
                      'ordinary_privacy_rule_findings': [], 'additional_known_private_values_checked': 0,
                      'frozen_script_or_capture_or_readiness_changed': False,
                      'provider_calls_or_media_export_or_publication': False,
                      'files': {name: hashlib.sha256(body).hexdigest() for name, body in assets.items()}}
        assets['provenance.json'] = encoded(provenance)
        OUT.mkdir(parents=True)
        for name, body in assets.items():
            with (OUT / name).open('xb') as stream:
                stream.write(body)
    print(json.dumps({'source_preflight': True, 'words': 634, 'paragraphs': 8, 'actual_sources': 21,
                      'untimed_spans': 27, 'uncovered_claims_or_controls': [], 'files_written': args.write_brief,
                      'stock_voice': 'Warm Lulu', 'provider_called': False, 'timing_assigned': False}))


if __name__ == '__main__':
    main()
