"""Prepare a read-only-first, exact native Unit actual-cue source proposal.

--write creates NEW source-only files. No natural-voice listening, context
qualification, authoring approval, rendering or publication is inferred.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
B = Path('expansion/plans/app-unit-call-lifecycle-native-candidate-20261030')
OUT = Path('expansion/plans/app-unit-call-lifecycle-native-take-01-proposed-20261030')
PINS = {
    B / 'lesson.candidate.json': 'a98a596197aa748981d9ed30b65f3a76e2bf64166ffa697e1eb8b134f97d759c',
    B / 'sentence-screen-map.untimed.json': 'acaaa31c29be68e882d53f3ce137efe3cb389a0cd8866d6e48fc21f9fd366894',
    Path('expansion/audio/app-unit-call-lifecycle-native.m4a'): 'e95e8fed105ed21c44334898e4b5476767bc29ca5b9152ec478cb2808c37986d',
    Path('expansion/audio/app-unit-call-lifecycle-native.actual.qa.json'): '77d0fbe0dbcfd93c006008ea4b5159084194381ec8485a15c139de018d46f1e5',
    Path('expansion/audio/app-unit-call-lifecycle-native.actual.corrected.srt'): '6c8880bcca673beac948c4a67d963c727d151aa97fd2b83a1e5b2a492da085ee',
}


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def words(s): return re.findall(r'\w+', s.casefold())
def encoded(d): return (json.dumps(d, ensure_ascii=False, indent=2) + '\n').encode()


def proposal():
    assert __debug__
    for p, digest in PINS.items():
        assert sha(S / p) == digest, 'Changed exact Unit source/audio: ' + str(p)
    sys.path.insert(0, str(ROOT / 'scripts'))
    from render_walkthrough import load_cues
    sentences = json.loads((S / B / 'sentence-screen-map.untimed.json').read_text())['sentences']
    cues = load_cues(S / 'expansion/audio/app-unit-call-lifecycle-native.actual.corrected.srt')
    qa = json.loads((S / 'expansion/audio/app-unit-call-lifecycle-native.actual.qa.json').read_text())
    assert qa['passed'] and not qa['issues'] and not qa['possible_speech_gaps']
    assert qa['alignment']['match_ratio'] == 1 and qa['alignment']['text_changes'] == []
    assert qa['silent_raw_cues'] == qa['silent_corrected_cues'] == 0
    assert len(cues) == qa['alignment']['cues'] == 88 and len(sentences) == 59
    assert words(' '.join(s['text'] for s in sentences)) == words(' '.join(c['text'] for c in cues))
    ranges = []
    offset = 0
    for sentence in sentences:
        end = offset + len(words(sentence['text']))
        ranges.append((offset, end, sentence))
        offset = end
    offset = 0
    rows = []
    for n, cue in enumerate(cues, 1):
        end = offset + len(words(cue['text']))
        matched = [s for a, b, s in ranges if a < end and b > offset]
        ids = list(dict.fromkeys(s['capture_id'] for s in matched))
        scenes = list(dict.fromkeys(s['scene_id'] for s in matched))
        assert len(ids) == len(scenes) == 1, 'Actual cue crosses a source/scene boundary.'
        rows.append({'cue': n, 'start': cue['start'], 'end': cue['end'], 'text': cue['text'],
            'sentence_ids': [s['sentence_id'] for s in matched], 'scene_ids': scenes,
            'source_ids_in_exact_spoken_order': ids, 'image_sha256': matched[0]['image_sha256'],
            'within_cue_screen_cut_unresolved': False,
            'labels_to_check_in_actual_source': list(dict.fromkeys(x for s in matched for x in s['required_labels'])),
            'native_controls_to_check': list(dict.fromkeys(s['native_control'] for s in matched if s['native_control']))})
        offset = end
    duration = qa['audio']['duration_seconds']
    spans = []
    for row in rows:
        key = (row['scene_ids'][0], row['source_ids_in_exact_spoken_order'][0])
        if not spans or (spans[-1]['scene_id'], spans[-1]['screenshot_id']) != key:
            if spans: spans[-1]['end'] = row['start']
            spans.append({'scene_id': key[0], 'screenshot_id': key[1], 'image_sha256': row['image_sha256'],
                'start': 0 if not spans else row['start'], 'end': duration, 'actual_cues': []})
        spans[-1]['actual_cues'].append(row['cue'])
    continuous = 0
    previous = None
    for span in spans:
        if span['screenshot_id'] != previous: continuous += 1
        previous = span['screenshot_id']
    result = {'kind': 'Exact actual 88-cue native Unit source proposal; no estimated word cuts',
        'lesson_id': 'app-unit-call-lifecycle-native', 'duration_seconds': duration,
        'actual_cues': rows, 'scene_bounded_source_spans': spans,
        'continuous_image_holds': continuous, 'source_images': len({s['screenshot_id'] for s in spans}),
        'source_profiles': {'017_through_051': 'Retained pre-spinner source Call Details e6f88c2b1468959840f7fe81b32b2637ee1982f35be4f9aefc5cfd8e4596d605',
            '062_through_081': 'Retained post-spinner source Call Details 30afe9ef7fbb2372b77c69d61c2079a5c60ce55c54c58a703bd021f933bebac1'},
        'input_hashes': {p.as_posix(): d for p, d in PINS.items()},
        'all_original_cue_words_and_endpoints_retained': True, 'word_timing_interpolation': False,
        'parent_proposed_correspondence_review': 'pending', 'native_context_qualification': 'pending',
        'actual_User_full_listening_review': 'pending', 'rendered': False, 'publishable': False,
        'limits': ['Labels and icon references are review targets, not automatic cue-specific observations.',
            'Literal aliases and instructional cue labels require authoring review.',
            'Actual native source package and its independent named context review are required before final authoring.']}
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write', action='store_true')
    a = p.parse_args()
    document = proposal()
    path = S / OUT / 'actual-cue-source-proposal.json'
    if a.write:
        assert not (S / OUT).exists(), 'Preserve immutable proposal history.'
        path.parent.mkdir(parents=True)
        with path.open('xb') as stream: stream.write(encoded(document))
    elif path.exists():
        assert path.read_bytes() == encoded(document), 'Existing proposal changed.'
    print(json.dumps({'proposal_ready': True, 'written': a.write, 'cues': 88,
        'source_spans': len(document['scene_bounded_source_spans']),
        'continuous_holds': document['continuous_image_holds'], 'images': document['source_images'],
        'proposal_sha256': hashlib.sha256(encoded(document)).hexdigest(), 'hearing_assumed': False}))


if __name__ == '__main__': main()
