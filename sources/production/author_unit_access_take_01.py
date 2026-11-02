"""Retain the manually reviewed Unit access/crew take01 source correspondence.

Historical recipe only. Re-running verifies fixed input hashes and reproduces
this exact reviewed plan; it does not perform a new visual or speech review.
Changed source, words, cue exports or pixels require a new reviewed take.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from render_walkthrough import load_cues, words
from render_public_media import stamp
from verify_capture_evidence import instruction_scene_digest

NAME = 'app-unit-01-access-and-crew'
FROZEN = 'b4d19c33b8a1631e5f9c8849870eb9bca0af941e3e5b7808e7302b0c61be4b07'
FREEZE = '6986db9125aa7beca1af36021661ce9fba2f8fe12409584c03eb3a6daa814d34'
AUDIO = '83ca192daeadbd162f42d5a69a8b2f1cdff8732101a0d3d99df236467ae348e3'
REVIEWED_AT = '2026-10-27T19:19:46Z'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def retain(p, value):
    body = value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
    if p.exists() and p.read_text() != body:
        raise ValueError('Refusing to overwrite a different retained output: ' + str(p))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body)

def build(root):
    s = root / 'sources'
    voice = s / f'expansion/plans/{NAME}.narrated-source.json'
    freeze_path = s / 'captures/expansion/unit/access-and-crew-freeze.json'
    assert digest(voice) == FROZEN and digest(freeze_path) == FREEZE
    lesson = json.loads(voice.read_text())
    canonical = json.loads((s / f'expansion/lessons/{NAME}.json').read_text())
    assert canonical['scenes'] == lesson['scenes']
    freeze = json.loads(freeze_path.read_text())
    assert len(freeze['screenshots']) == 24 and len(lesson['scenes']) == 10
    audio = s / f'expansion/audio/{NAME}.m4a'
    qa_path = s / f'expansion/audio/{NAME}-qa.json'
    qa = json.loads(qa_path.read_text())
    assert digest(audio) == AUDIO and qa['passed'] and qa['silent_raw_cues'] == 0
    assert qa['lesson']['sha256'] == FROZEN
    corrected = s / f'expansion/audio/{NAME}-corrected.srt'
    raw = load_cues(corrected)
    assert len(raw) == 76
    transcript = s / f'expansion/audio/{NAME}-one-second.txt'
    txt = transcript.read_text()
    records = {}
    for entry in freeze['screenshots']:
        row = copy.deepcopy(entry)
        assert digest(s / row['file']) == row['sha256']
        # Keep original source text untouched in the immutable freeze. The
        # public derivative needs no loopback URL values or duplicate labels.
        row['visible_labels'] = list(dict.fromkeys(x for x in row['visible_labels'] if not x.startswith(('http://','https://'))))
        row['viewport_review'] = {
            'reviewer': 'Codex', 'reviewed_at': REVIEWED_AT, 'sha256': row['sha256'],
            'method': 'All 24 complete genuine source images visually inspected in six four-image sheets; the response header and unchanged role assignment also inspected individually at full resolution. Actual icon shapes and retained DOM rectangles reviewed. Empty credential fields remain empty; no operator identity inferred from crew.'}
        records[row['id']] = row
    def screen(prefix):
        return next(k for k in records if k.startswith(prefix + '-'))
    ranges = [
        (1,3,'027'), (4,5,'028'), (6,8,'039'),
        (9,9,'001'), (10,10,'004'), (11,12,'005'), (13,13,'002'), (14,14,'003'), (15,16,'005'),
        (17,19,'004'), (20,20,'027'), (21,21,'004'), (22,22,'039'),
        (23,25,'006'), (26,29,'007'),
        (30,30,'006'), (31,32,'026'), (33,33,'039'), (34,37,'026'),
        (38,38,'028'), (39,39,'029'), (40,43,'031'), (44,45,'039'),
        (46,53,'040'),
        (54,55,'039'), (56,56,'020'), (57,58,'038'), (59,59,'035'), (60,61,'039'),
        (62,65,'025'), (66,66,'020'), (67,67,'022'), (68,68,'025'),
        (69,69,'039'), (70,73,'032'), (74,74,'039'), (75,76,'039'),
    ]
    refs = {
        5:{'Settings':'Settings'},
        9:{'Next':'Next','Skip':'Skip'}, 10:{'Server URL':'Server URL'}, 11:{'Server':'server','Custom':'custom address'},
        17:{'Username':'Username','Password':'Password','Sign In':'Sign In'}, 18:{'Sign in with SSO':'Sign in with SSO'},
        23:{'Shared device':'Shared device'}, 24:{'This is a shared device':'This is a shared device','Device label (optional)':'Device label (optional)'}, 25:{'Save':'Save'},
        30:{'Shared device':'Shared device'}, 31:{'Sign In':'Sign In'}, 33:{'Active Unit':'Active Unit'},
        38:{'Settings':'Settings','Active Unit':'Active Unit'}, 39:{'Select Unit':'Select Unit'}, 40:{'Current Unit':'Current Unit'},
        46:{'Unit Role Assignments':'Unit Role Assignments'}, 47:{'Officer / Team Lead':'Officer / Team Lead','Christopher Herrmann':'Christopher Herrmann'}, 48:{'Save':'Save'},
        54:{'Available':'state'}, 57:{'Submit':'Submit'}, 60:{'Available':'saved unit state'},
        62:{'TRAINING ONLY — Responder call and check-in practice':'call card'},
        63:{'View Call Details':'View Call Details'}, 64:{'Directions':'Directions'}, 65:{'Deselect':'Deselect'},
        66:{'Set Active':'Set Active','Select Status':'Select Status'}, 67:{'Submit':'status submission'},
        69:{'Sign-in and security':'Sign-in and security','Authenticator app':'Authenticator app','Passkeys for this app':'Passkeys for'},
        70:{'Recent verifications':'Recent verifications'}, 71:{'No passkeys for this app yet.':'no passkeys are registered'},
        74:{'Login Info':'Login Info','Username':'Username','Password':'Password','Cancel':'Cancel'},
        76:{'Logout':'Logout','Confirm Logout':'Confirm Logout','Cancel':'Cancel'},
    }
    mapping = {}
    for first,last,prefix in ranges:
        for n in range(first,last+1):
            assert n not in mapping
            mapping[n] = screen(prefix)
    assert set(mapping) == set(range(1,77))
    # Every cut is an integer-second boundary genuinely present in Descript's
    # one-second export. Phrase strings are exact frozen speech, never timing
    # interpolation within a cue. The export has one-second granularity.
    splits = {
        9:[(32.0,'Language','004',{'en':'Language'},'[00:00:32] Language and Server')],
        46:[(158.0,'inspect Unit Role Assignments.','040',{'Unit Role Assignments':'Unit Role Assignments'},'[00:02:38] inspect Unit Role')],
        55:[(187.0,'opens','035',{},'[00:03:07] opens that'), (189.0,'note steps;','038',{'Add Note':'note steps'},'[00:03:09] note steps;')],
        56:[(192.0,'Select Status.','021',{'Select Status':'Select Status'},'[00:03:12] Select Status.')],
        59:[(202.0,'destinations and note','038',{'Note (optional):':'note'},'[00:03:22] destinations and note before')],
        63:[(214.0,'Details opens','020',{'Call Details':'Details'},'[00:03:34] Details opens its full')],
        66:[(227.0,'opened Select Status.','021',{'Select Status':'Select Status'},'[00:03:47] opened Select')],
        67:[(231.0,'status submission,','023',{'Submit':'status submission'},'[00:03:51] status submission,')],
        69:[(240.0,'Authenticator app,','032',{'Authenticator app':'Authenticator app','Passkeys for this app':'Passkeys for'},'[00:04:00] Authenticator app,')],
        74:[(258.0,'Info opens','033',{'Username':'Username','Password':'Password','Cancel':'Cancel'},'[00:04:18] Info opens empty')],
        76:[(264.0,'opens Confirm Logout;','034',{'Confirm Logout':'Confirm Logout','Cancel':'Cancel'},'[00:04:24] opens Confirm'), (267.0,'the current session.','039',{},'[00:04:27] the current session.')],
    }
    first_refs = {
        9:{'Next':'Next','Skip':'Skip'}, 46:{'1 of 1 Roles':'roles card'}, 55:{'Available':'quick status button'},
        56:{'Set Active':'Set Active'}, 59:{}, 63:{'View Call Details':'View Call'},
        66:{'Set Active':'Set Active'}, 67:{}, 69:{'Sign-in and security':'Sign-in and security'},
        74:{'Login Info':'Login'}, 76:{'Logout':'Logout'},
    }
    expanded = []
    provenance = []
    for n,cue in enumerate(raw,1):
        parts = [];text = cue['text'];at = cue['start'];ident = mapping[n]
        references = first_refs.get(n,refs.get(n,{}))
        if n == 46:
            ident = screen('039')
        for when,phrase,prefix,new_refs,anchor in splits.get(n,[]):
            assert anchor in txt, anchor
            before,sep,after = text.partition(phrase)
            assert sep and at < when < cue['end'] and before.strip()
            parts.append((at,when,before.strip(),ident,references))
            provenance.append({'original_cue':n,'cut_seconds':when,'before_exact_phrase':phrase,'genuine_export_anchor':anchor,'measurement':'Actual Descript one-second TXT export; one-second granularity, no interpolated word timing.'})
            at=when;text=sep+after;ident=screen(prefix);references=new_refs
        parts.append((at,cue['end'],text,ident,references))
        for start,end,text,ident,references in parts:
            expanded.append({'start':start,'end':end,'text':text,'screenshot_id':ident,'required_labels':list(references),'spoken_references':references,'instructional':bool(references),'original_cue':n})
    assert len(expanded) == 89
    assert words(' '.join(c['text'] for c in expanded)) == words(' '.join(c['narration'] for c in lesson['scenes']))
    used = {c['screenshot_id'] for c in expanded}
    assert used == set(records), sorted(set(records)-used)
    capture_path = s / f'expansion/plans/{NAME}-take-01.captures.json'
    retain(capture_path, {'app':'Unit','screenshots':list(records.values()),'source_manifest':freeze_path.relative_to(s).as_posix(),'source_manifest_sha256':FREEZE,'scope':'Immutable 24-source freeze, unchanged pixels; public label subsets omit only unused URL values and duplicate text. Exact named-control timing is separately authored and reviewed.'})
    srt=''.join(f"{i}\n{stamp(c['start'],True)} --> {stamp(c['end'],True)}\n{c['text']}\n\n" for i,c in enumerate(expanded,1))
    caption_path = s / f'expansion/audio/{NAME}-screen-cuts.srt'
    retain(caption_path,srt)
    retain(s / f'expansion/audio/{NAME}-screen-cuts-provenance.json', {'lesson_sha256':FROZEN,'source_corrected_srt_sha256':digest(corrected),'genuine_one_second_txt_sha256':digest(transcript),'raw_cues':76,'derived_cues':89,'splits':provenance,'audio_sha256':AUDIO,'no_speech_words_or_original_outer_cue_bounds_changed':True,'scope':'These integer-second cuts are measured transcript anchors. No narrower word timing or newly performed application action is claimed.'})
    groups=[];position=0
    for scene in lesson['scenes']:
        expected=words(scene['narration']);actual=[];entries=[]
        while len(actual)<len(expected):
            cue=expanded[position];position+=1;actual+=words(cue['text']);entries.append(dict(cue,cue=position))
        assert actual==expected,scene['id']
        groups.append((scene,entries))
    duration=qa['audio']['duration_seconds'];scenes=[]
    for i,(authored,entries) in enumerate(groups):
        start=0 if i==0 else entries[0]['start'];end=duration if i==len(groups)-1 else groups[i+1][1][0]['start'];screens=[]
        for j,c in enumerate(entries):
            at=start if j==0 else c['start']
            if not screens or screens[-1]['screenshot_id']!=c['screenshot_id']:
                if screens:screens[-1]['end']=at
                screens.append({'screenshot_id':c['screenshot_id'],'start':at,'end':end})
        built={'id':authored['id'],'title':authored['title'],'kind':'operational','start':start,'end':end,'visual_required_labels':authored['required_labels'],'screens':screens,'captions':entries}
        review={'passed':True,'reviewer':'Codex','reviewed_at':REVIEWED_AT,'correspondence_reviewed':True,'no_unseen_controls':True,'mapping_sha256':instruction_scene_digest(built,records),'method':'All24 actual complete source images independently inspected. Explicit exact-cue/screenshot correspondence; 13 cuts use genuine integer-second Descript anchors. Language maps to painted en in its real language selector. The three call actions are actual icon-only controls bound to their captured DOM names and rectangles, not invented literal labels. Conditional/unverified branches and historical response versus later cleanup remain distinct.'}
        scenes.append({'id':authored['id'],'start':start,'end':end,'screens':screens,'captions':[{k:c[k] for k in ('cue','screenshot_id','required_labels','spoken_references','instructional')} for c in entries],'instruction_review':review})
    plan={'schema_version':1,'lesson_id':NAME,'duration_seconds':duration,'instruction_mapping':'reviewed_scene_coverage','display_context':'TRAINING ONLY · fictional department',
        'narration':{'file':audio.relative_to(s).as_posix(),'sha256':AUDIO,'kind':'approved_natural_narration','approval':{'reviewer':'Codex','reviewed_at':REVIEWED_AT,'sha256':AUDIO,'complete_natural_narration':True,'method':'Established natural stock voice; all10 actual generated paragraphs fully decoded and exact618word frozen script aligned. All76 source cues measured non-silent. No human listening or pronunciation review claimed.','qa_file':qa_path.relative_to(s).as_posix(),'qa_sha256':digest(qa_path)}},
        'captions':{'file':caption_path.relative_to(s).as_posix(),'sha256':digest(caption_path),'kind':'speech_timed_srt','approval':{'reviewer':'Codex','reviewed_at':REVIEWED_AT,'sha256':digest(caption_path),'audio_sha256':AUDIO,'speech_timing_reviewed':True,'method':'Actual76 exported cue boundaries retained except13 documented genuine integer-second splits into89 cues. Exact frozen words and order retained. Derived signal/layout QA and encoded-frame review required before publication.','timing_provenance':f'expansion/audio/{NAME}-screen-cuts-provenance.json'}},
        'capture_manifests':[{'file':capture_path.relative_to(s).as_posix(),'sha256':digest(capture_path)}],
        'screenshot_reviews':{ident:{'reviewer':'Codex','reviewed_at':REVIEWED_AT,'sha256':row['sha256'],'application_visible':True,'labels_legible':True,'no_errors':True,'method':row['viewport_review']['method']} for ident,row in records.items()},
        'scenes':scenes,'source_freeze':{'lesson_sha256':FROZEN,'spoken_words':618,'voice_source':voice.relative_to(s).as_posix(),'actual24_photo_freeze_sha256':FREEZE,'source_plan_sha256':digest(s/'expansion/plans/app-unit-01-access-capture-plan.json')},
        'limitations':freeze['follow_up_app_coverage']+['Normal reload reached the empty Sign In page; no lock/unlock/end-shift/operator-switch success or provider/MFA enrollment is claimed.','Source025 and its response flow are earlier actual training observations for call51009. Later039 is Available/No Active Call cleanup. Neither an assigned crew name nor an apparatus name identifies the signed-in operator.','Role assignments preserve Herrmann in one configured seat; Save is disabled, not an executed crew change.','Source004 paints en in the actual language selector. No literal Language label is invented.','The89 derived speech cues require all actual encoded-frame review and three independent native playback proofs before publication.']}
    p=s/f'expansion/plans/{NAME}-take-01.plan.json';retain(p,plan)
    print(json.dumps({'plan':p.relative_to(root).as_posix(),'sha256':digest(p),'scenes':10,'selected_images':len(records),'screen_intervals':sum(len(x['screens']) for x in scenes),'raw_cues':76,'derived_cues':len(expanded),'duration_seconds':duration},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);build(p.parse_args().root.resolve())
