"""Freeze the demonstrated local record-number setting change; never qualify a video."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

S = Path(__file__).resolve().parents[1]
NAME = 'core-record-numbering-settings'
BASE = Path('expansion/plans') / (NAME + '-source-proposal-20261101-v2')


def scene(number, title, narration, practice, labels, capture):
    return {'id': f'{number:02}', 'title': title, 'narration': narration, 'practice': practice, 'required_labels': labels, 'capture_refs': [capture]}


LESSON = {
    'id': NAME,
    'app': 'Core',
    'title': 'Configure record numbering and verify saved changes',
    'summary': 'Understand patterns, padding, year starts and prefixes; save a custom pattern, verify its sequence previews, then restore the original format.',
    'audience': ['Department administrators', 'Records administrators', 'Migration coordinators'],
    'prerequisites': ['An authorized department administrator session with Records Settings available.', 'A separate training department for practice and an agreed numbering policy before changing operational settings.'],
    'scenes': [
        scene(1, 'Start in the department Records Settings',
              'Record numbers help people find and distinguish documents during a handover or a data migration. This walkthrough starts on Records Settings in the fictional Firehouse fifty-one training department. We will inspect the numbering controls, save one change, verify what persisted and restore the original pattern. The department name and settings page should match the department you intend to administer.',
              'Verify the intended department and Records Settings page before editing.',
              ['Records Settings'], '001-records-settings-lifecycle'),
        scene(2, 'Read the number pattern and its tokens',
              'Scroll to Record numbering. Number pattern currently contains the prefix token, a hyphen, the four-digit year token, another hyphen and the sequence token. The help below explains what each token writes. Prefix uses the record type prefix, year includes the numbering year, and sequence supplies the counter. Changing this pattern does not renumber records that already have numbers. Read that impact before applying a new format.',
              'Read the existing pattern and the explanation that existing record numbers are retained.',
              ['Record numbering', 'Number pattern', '{PREFIX}-{YYYY}-{SEQ}'], '006-pattern-tokens-padding-readable'),
        scene(3, 'Distinguish padding from the next sequence',
              'Sequence digits is four in this department. The help shows that four digits writes a zero-padded value such as zero one eight four. This control accepts three through eight digits. Changing the width keeps each sequence\'s next number; it is not the same as choosing a different next counter. Definitions that have their own numbering keep their own width. In this exercise, we leave the four-digit setting as it is.',
              'Find Sequence digits and distinguish zero padding from a counter change.',
              ['Sequence digits', '4'], '006-pattern-tokens-padding-readable'),
        scene(4, 'Review the numbering year start',
              'Numbering year starts has a month and day. January first is selected here. The displayed help explains how a fiscal-year start affects sequences that include the year. This setting is separate from call numbering, which has its own year start on Call Settings. Review the policy your department actually follows before changing either. This demonstration keeps the existing January-first value.',
              'Identify the actual month and day controls and read their scope before changing a year start.',
              ['Numbering year starts', 'January', '1'], '005-year-start-readable'),
        scene(5, 'Understand type prefixes and shared sequences',
              'Record type prefixes lists each type, its default and a Number prefix box. The visible defaults include Run, R U N; Training, T R N; Work, W R K; and Meeting, M T G. Leave a box blank to keep its default. The help explains that a new prefix starts its own sequence, and types given the same prefix share one sequence. Prefixes take effect when the number pattern includes the prefix token. Choose them deliberately rather than using a cosmetic change that accidentally joins two counters.',
              'Compare the visible type, default and prefix columns and read the sharing rule.',
              ['Record type prefixes', 'Record type', 'Default', 'Number prefix', 'Run', 'RUN', 'Training', 'TRN', 'Work', 'WRK', 'Meeting', 'MTG'], '008-prefix-heading-and-table'),
        scene(6, 'Prepare a custom pattern in the training department',
              'For this local exercise, replace the two hyphens in Number pattern with underscores. Keep the same prefix, four-digit year and sequence tokens. The example beside the field now uses underscores too. This is still an unsaved form value. The format of the example is useful feedback, but it does not prove the department has saved the change or issued a new record number.',
              'Compare the prepared underscore pattern and example without treating the preview as a saved result.',
              ['Record numbering', 'Number pattern', '{PREFIX}_{YYYY}_{SEQ}', 'INC_2026_0153'], '001-prepared-custom-pattern'),
        scene(7, 'Use the actual Save action',
              'Scroll to the bottom of Records Settings, where Save and Cancel are visible. Review your intended edit before choosing Save. This demonstration changes the number pattern only; it does not submit a record, raise a counter or request delivery to an external service. Use Save once, then verify the returned settings page instead of assuming that typing in the field completed the configuration.',
              'Find the real Save control at the bottom of the settings form.',
              ['Save', 'Cancel'], '002-save-control'),
        scene(8, 'Verify the returned success message',
              'The returned page displays Records settings saved. This confirms that the settings form was accepted. We still need to verify the particular value we intended to change. A general success notice is useful, but reading the saved field and its effect gives an administrator a more complete check.',
              'Read the success notice, then continue to inspect the specific saved field.',
              ['Records Settings', 'Records settings saved.'], '003-settings-saved'),
        scene(9, 'Reopen settings and confirm persistence',
              'Reopening Records Settings shows the underscore-separated pattern in Number pattern, with the matching example alongside it. This is a fresh page load after saving. Compare the full pattern, including each token and separator, with your intended format. The result confirms persistence of this local setting; the example is still an example rather than a newly issued record.',
              'Verify the complete saved pattern after reopening the page.',
              ['Record numbering', '{PREFIX}_{YYYY}_{SEQ}', 'INC_2026_0153'], '006-pattern-after-reopen'),
        scene(10, 'Inspect the effect on next-number previews',
              'The saved pattern changes Next numbers for twenty twenty-six. The Run and Training previews now have underscores and end in zero zero zero one. The text around the sequence token changed, so this format has its own sequence. Raise next to is a separate control for carrying on from previously issued numbers. Leave it alone when you do not intend to raise a counter. Viewing this table does not issue the previewed numbers.',
              'Read the new pattern previews and distinguish them from a request to raise a counter.',
              ['Next numbers for 2026', 'RUN_2026_0001', 'TRN_2026_0001', 'Raise next to'], '005-new-pattern-next-numbers'),
        scene(11, 'Restore the original pattern for the exercise',
              'After the exercise, the original hyphen-separated pattern was restored. Record numbering now shows the original prefix, year and sequence arrangement. Restore a practice change only when that is your intended configuration. Changing separators back is a format decision; it is not a way to erase previously issued numbers or reset a counter.',
              'Compare the restored pattern with the original baseline.',
              ['Record numbering', '{PREFIX}-{YYYY}-{SEQ}', 'INC-2026-0153'], '007-original-pattern-restored'),
        scene(12, 'Verify the original sequence resumes',
              'The original format now shows Training ending in zero zero zero three, the same next-number preview it had before the demonstration. Run ends in zero zero zero one. Restoring the earlier format resumed its existing sequence rather than restarting Training at one. No new records were issued during this exercise. When importing from another system, review Raise next to against the numbers already issued before applying a higher starting point.',
              'Verify the resumed original Training sequence without entering or saving a counter increase.',
              ['Next numbers for 2026', 'TRN-2026-0003', 'RUN-2026-0001', 'Raise next to'], '008-original-sequence-resumed'),
        scene(13, 'Distinguish other record-number settings',
              'Other record numbers has separate rows for Records requests, Occupancies, Inspections, Permits and Investigations. Each visible row has a Number pattern, Sequence digits and a next-number area. The help explains that blank patterns keep the built-in numbers and that these types follow the record-numbering year start above. Review the particular row you intend to administer. This recording inspects those controls without saving a custom pattern for these other record types.',
              'Identify the correct row before editing another record-number pattern.',
              ['Other record numbers', 'Records requests', 'Occupancies', 'Inspections', 'Permits', 'Investigations', 'Number pattern', 'Sequence digits', 'Next number'], '010-other-record-number-patterns'),
        scene(14, 'Apply a clear numbering policy across departments',
              'A consistent numbering policy helps security teams find post reports, wildland contractors distinguish crew-support work, and industrial teams coordinate equipment records. Community paramedicine and mental health teams can organize appropriate service documentation, while search-and-rescue teams can distinguish training and support records. Fire and E M S departments can use the same pattern review. Agree on the format, inspect the correct controls, save deliberately and verify both persistence and the next-number preview.',
              'Apply the demonstrated format, persistence and sequence checks to a fictional policy for your department.',
              ['Next numbers for 2026', 'TRN-2026-0003', 'Raise next to'], '008-original-sequence-resumed'),
    ],
    'sector_examples': [{'sector': sector, 'scenario': scenario} for sector, scenario in [
        ('Fire / EMS', 'Agree on distinguishable training and incident record identifiers.'),
        ('Community response', 'Keep appropriate outreach documentation identifiable under the department policy.'),
        ('Search and rescue', 'Distinguish training and mission-support records.'),
        ('Security', 'Use a consistent identifier format for authorized post-support documentation.'),
        ('Wildland', 'Distinguish crew-support records and preserve previously issued identifiers.'),
        ('Industrial', 'Coordinate equipment-support records using understood prefixes and counters.'),
    ]],
    'scope_limits': [
        'Demonstrates normal settings UI in the fictional local department: an underscore pattern is saved, verified after a fresh GET, then the original hyphen pattern is saved again. No records or numbers are issued.',
        'Width, fiscal-year start, type prefixes, counter-raising and other record-type patterns are inspected without changing those settings. No counter raise, shared-prefix transition or fiscal-year rollover is demonstrated.',
        'The running screen has month/day controls but no year-label selector. Only visible controls and their displayed help are taught.',
        'Source candidate only; natural narration, actual timing and complete encoded/browser reviews remain required.',
    ],
    'export_ready': False,
    'publication_mode': 'source_candidate_only',
}


def freeze(write=False):
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    encode = lambda data: (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode()
    manifests = [S / 'captures/expansion/core-records-numbering-settings-20261101/captures.reviewed.json', S / 'captures/expansion/core-record-number-change-20261101/captures.reviewed.json']
    by_id = {}
    for manifest in manifests:
        for row in json.loads(manifest.read_text())['screenshots']:
            assert row['id'] not in by_id
            by_id[row['id']] = (row, manifest)
    files = {BASE / 'lesson.candidate.json': encode(LESSON)}
    rows = []
    for capture_id in dict.fromkeys(ref for item in LESSON['scenes'] for ref in item['capture_refs']):
        original, manifest = by_id[capture_id]
        row = deepcopy(original)
        labels = list(dict.fromkeys(label for item in LESSON['scenes'] if capture_id in item['capture_refs'] for label in item['required_labels']))
        assert set(labels) <= set(row['visible_labels']), (capture_id, labels)
        assert row['capture_review']['passed'] and row['capture_review']['reviewer'] == 'Codex /root'
        assert sha(S / row['file']) == row['sha256'] and sha(S / row['dom_file']) == row['dom_sha256']
        image = BASE / 'images' / (capture_id + '.jpg')
        dom = BASE / 'dom' / (capture_id + '.dom.txt')
        files[image] = (S / row['file']).read_bytes()
        files[dom] = (S / row['dom_file']).read_bytes()
        row['raw_source'] = {'manifest_file': str(manifest.relative_to(S)), 'manifest_sha256': sha(manifest), 'image_file': row['file'], 'image_sha256': row['sha256'], 'dom_file': row['dom_file'], 'dom_sha256': row['dom_sha256']}
        row.update(file=str(image), dom_file=str(dom), visible_labels=labels, required_labels=labels, visible_controls=[], visible_field_text=[])
        row['capture_review'].pop('controls_sha256', None)
        rows.append(row)
    text = '\n\n'.join(item['narration'] for item in LESSON['scenes']) + '\n'
    files[BASE / 'narration.txt'] = text.encode()
    files[BASE / 'captures.reviewed.json'] = encode({'app': 'Core', 'screenshots': rows})
    files[BASE / 'source-provenance.json'] = encode({'created_at': datetime.now(timezone.utc).isoformat(), 'lesson_sha256': hashlib.sha256(files[BASE / 'lesson.candidate.json']).hexdigest(), 'script_words': len(text.split()), 'scenes': len(LESSON['scenes']), 'reviewed_source_images': len(rows), 'source_review_inherited_from_exact_reviewed_manifest_bytes': True, 'source_manifests': [{'file': str(path.relative_to(S)), 'sha256': sha(path)} for path in manifests], 'actual_video_or_listening_approval_inferred': False})
    if write:
        assert all(not (S / path).exists() for path in files)
        for path, data in files.items():
            destination = S / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open('xb') as stream:
                stream.write(data)
    return {'lesson_id': NAME, 'words': len(text.split()), 'scenes': len(LESSON['scenes']), 'actual_source_images': len(rows), 'source_sha256': hashlib.sha256(files[BASE / 'lesson.candidate.json']).hexdigest(), 'written': write, 'qualified_video': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', action='store_true')
    arguments = parser.parse_args()
    print(json.dumps(freeze(arguments.freeze), indent=2))
