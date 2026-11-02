"""Retain the explicitly reviewed Dispatch allocation take01 correspondence.

Historical authoring recipe. Re-running verifies exact retained input hashes
and reproduces this plan; it does not perform a new visual or speech review.
No private editor/export metadata is consumed or made public by this recipe.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from render_walkthrough import load_cues, words
from render_public_media import stamp
from verify_capture_evidence import instruction_scene_digest

NAME = 'app-dispatch-allocation'
FROZEN = 'a9f03e25388af4aa7387685368ba5db686239416a9daf4836165cbf62244b2f7'
FREEZE = '5404213c949d28750d653a37ae4342de6c3fd64020be36e73e7f060f381c0323'
SEQUENCE = 'eed82cb9263b6bdaae8d460b684c197fbe16c57b19426f121641d8979d1fef15'
AUDIO = 'c9ff69a8e77ba2deb6c22e20b1a0e41d4891679823a6e420e4f3720d527b9ce4'
CORRECTED = '48f28f1d7c501b95fa10dd7a92192ced85a8e691ca6ad414f3fb3b1b1e9735af'
TRANSCRIPT = '468951bd31000e0ce19c479e2ea4d93d5533c15b3139f483fa9e4d3357a0e673'
REVIEWED_AT = '2026-10-27T20:19:57Z'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def retain(path, value):
    body = value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
    if path.exists() and path.read_text() != body:
        raise ValueError('Refusing to overwrite different retained output: ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)


def build(root):
    s = root / 'sources'
    canonical = s / f'expansion/lessons/{NAME}.json'
    base = s / 'expansion/plans/app-dispatch-allocation-capture-freeze-20261027'
    freeze_path = base / 'freeze.json'
    sequence_path = base / 'untimed-screen-sequence.json'
    assert digest(canonical) == FROZEN
    assert digest(freeze_path) == FREEZE and digest(sequence_path) == SEQUENCE
    lesson = json.loads(canonical.read_text())
    freeze = json.loads(freeze_path.read_text())
    sequence = json.loads(sequence_path.read_text())
    assert len(lesson['scenes']) == 8 and sum(len(x['narration'].split()) for x in lesson['scenes']) == 812
    voice = s / f'expansion/plans/{NAME}.narrated-source.json'
    if voice.exists():
        assert digest(voice) == FROZEN
    else:
        voice.write_bytes(canonical.read_bytes())
    manifest_path = s / freeze['capture_manifest']
    assert digest(manifest_path) == freeze['capture_manifest_sha256'] == sequence['capture_manifest_sha256']
    manifest = json.loads(manifest_path.read_text())
    records = {}
    for shot in manifest['screenshots']:
        if shot['id'] not in freeze['source_hashes']:
            continue
        row = copy.deepcopy(shot)
        assert digest(s / row['file']) == row['sha256'] == freeze['source_hashes'][row['id']]
        row['visible_labels'] = list(dict.fromkeys(row['visible_labels']))
        row['viewport_review'] = {
            'reviewer': 'Codex', 'reviewed_at': REVIEWED_AT, 'sha256': row['sha256'],
            'method': 'All 22 complete frozen images independently inspected in six four-image sheets; source12 unit/group/crew, source22 pinned decision and source25 closing form additionally inspected at full resolution. Foreground controls and actual counts retained, with no occluded modal background counted as instructional controls.'}
        records[row['id']] = row
    assert len(records) == 22
    def screen(number):
        return next(ident for ident in records if ident.startswith(f'dispatch-{number:02}-'))
    audio = s / f'expansion/audio/{NAME}.m4a'
    qa_path = s / f'expansion/audio/{NAME}.qa.json'
    corrected = s / f'expansion/audio/{NAME}.corrected.srt'
    transcript = s / f'expansion/audio/{NAME}.one-second.txt'
    qa = json.loads(qa_path.read_text())
    assert digest(audio) == AUDIO and digest(corrected) == CORRECTED and digest(transcript) == TRANSCRIPT
    assert qa['passed'] and qa['silent_raw_cues'] == qa['silent_corrected_cues'] == 0
    assert qa['lesson']['sha256'] == FROZEN and qa['audio']['sha256'] == AUDIO
    raw = load_cues(corrected)
    assert len(raw) == 91
    ranges = [
        (1,5,3),(6,10,16),(11,15,5),(16,20,6),
        (21,23,17),(24,27,7),(28,29,8),(30,33,9),
        (34,36,10),(37,39,11),(40,41,9),(42,52,12),(53,53,8),
        (54,58,13),(59,60,14),(61,62,13),(63,63,15),(64,65,13),(66,66,16),
        (67,72,21),(73,76,22),(77,78,21),(79,79,22),(80,84,23),
        (85,86,25),(87,88,26),(89,89,28),(90,91,18),
    ]
    mapping = {}
    for first,last,number in ranges:
        for cue in range(first,last+1):
            assert cue not in mapping
            mapping[cue] = screen(number)
    assert set(mapping) == set(range(1,92))
    refs = {
        1:{'New Call':'New Call'}, 2:{'Name':'Name','Nature':'Nature','Priority':'Priority','Type':'Type'},
        3:{'Urgent':'Urgent','Structure Fire':'Structure Fire'}, 6:{'Latitude':'Latitude','Longitude':'Longitude'},
        11:{'Dispatch To':'Dispatch To','Decision':'Decision'},12:{'Engine within eight minutes':'within eight minutes'},
        13:{'Yes':'Yes','Engine 51':'Engine 51'}, 15:{'Ideal configuration not available':'Ideal configuration not'},
        16:{'Incident officer: 0 of 1 — locations too old':'positions are too old'},17:{'How this was decided':'explanation'},
        19:{'How this was decided':'advice'},
        24:{'Engine 51':'Engine 51','Recommended units (1)':'Recommended units'},
        25:{'Recommended personnel (1)':'Recommended personnel'},
        26:{'Fills: Engine':'Fills labels','Fills: Incident officer':'Fills labels'},27:{'Apply recommendation':'Apply recommendation'},
        28:{'2 selected':'two selected'},30:{'Select Dispatch Recipients':'selection'},
        31:{'Select Dispatch Recipients':'Select Dispatch Recipients','Closest':'Closest','Name':'Name','Available only':'Available only'},
        32:{'Closest':'Closest'},33:{'Nearest #1':'Nearest number one','Run card':'Run card'},
        34:{'Name':'Name','Blake Gallo':'Blake Gallo','Unavailable':'Unavailable','No location':'No location'},
        35:{'No location':'absence of a location'},37:{'Available only':'Available only','Users (12)':'twelve'},
        38:{'2 selected':'selected'},40:{'Everyone':'Everyone'},41:{'Everyone':'Leave it clear'},
        42:{'Engine':'Engine'},43:{'Groups (1)':'Groups entry','Engine 51':'Engine 51'},
        45:{'Groups (1)':'group','Units (1)':'unit'},
        46:{'Available':'Available','Crew: Christopher Herrmann (Officer / Team Lead)':'Herrmann’s crew assignment'},
        47:{'At station':'At station'},48:{'Nearest #3':'Nearest number three'},52:{'Confirm':'Confirm'},
        56:{'Engine within eight minutes':'eight-minute condition'},57:{'Outcome: Review alternatives':'Review alternatives'},58:{'Advice':'advice-only'},
        59:{'101.2 km · ~198 min':'one hundred and one kilometres'},
        61:{'1 × Engine within 8:00 (slowest needed: Engine 51, 199:22)':'response estimate'},
        64:{'2 selected':'two selected recipients'},66:{'Latitude':'coordinates','Longitude':'coordinates'},
        67:{'TRAINING ONLY - Dispatch allocation recording':'TRAINING ONLY, Dispatch'},
        70:{'Dispatched':'Dispatched','Christopher Herrmann':'Herrmann'},71:{'Engine 51':'Engine 51'},
        72:{'Dispatch additional resources':'Dispatch additional resources'},
        73:{"Decision pinned from the dispatcher's preview (Oct 27 12:47)":'decision was pinned from the dispatcher’s preview'},
        74:{"1 of 1 'Engine' already on the call.":'engine',"1 of 1 'Incident officer' already on the call.":'officer'},
        75:{'0 unit(s), 0 responder(s) recommended':'Zero additional recommendations'},
        77:{'Strike alarm 2':'Strike alarm two'},79:{'Re-evaluate':'Re-evaluate'},
        80:{'No':'No','Outcome: Review alternatives':'Review alternatives'},84:{'Cancel':'Cancel'},
        85:{'Close Call':'Close Call','Closed':'Closed','Close Type':'Closed','Close Note':'training note'},
        86:{'Notify everyone on the call':'Notify everyone on the call'},
        88:{'Active Calls':'active','3':'three'},89:{'Activity':'Activity','Responding':'Responding','Released':'Released'},
        90:{'Awaiting Resources':'Awaiting Resources'},91:{'No calls awaiting resources':'queue is empty'},
    }
    # Integer-second cuts are genuine Descript TXT measurements. The exact
    # phrase starts at the recorded anchor; no within-second interpolation.
    splits = {
        15:(59.0,'available and Could not fill',6,{'Could not fill':'Could not fill'},'[00:00:59] available and Could'),
        60:(222.0,'ninety-eight minutes for both Herrmann and Engine 51.',15,{'101.2 km · ~198 min':'ninety-eight minutes','Engine 51':'Engine 51'},'[00:03:42] ninety-eight minutes for both'),
        66:(242.0,'both the new decision and your selection.',17,{'Decision':'decision'},'[00:04:02] both the new'),
        88:(319.0,'calls, and Activity',28,{'Activity':'Activity'},'[00:05:19] calls, and Activity'),
    }
    txt = transcript.read_text()
    expanded, provenance = [], []
    for n,cue in enumerate(raw,1):
        item = dict(cue, screenshot_id=mapping[n], required_labels=list(refs.get(n,{})),
                    spoken_references=refs.get(n,{}), instructional=bool(refs.get(n)), original_cues=[n])
        if n not in splits:
            expanded.append(item)
            continue
        when,phrase,number,new_refs,anchor = splits[n]
        assert anchor in txt, anchor
        before,sep,after = cue['text'].partition(phrase)
        assert sep and before.strip() and cue['start'] < when < cue['end']
        expanded.append(dict(item,end=when,text=before.strip()))
        expanded.append(dict(item,start=when,text=sep+after,screenshot_id=screen(number),
                             required_labels=list(new_refs),spoken_references=new_refs,instructional=bool(new_refs)))
        provenance.append({'original_cue':n,'cut_seconds':when,'before_exact_phrase':phrase,'genuine_export_anchor':anchor,
                           'measurement':'Actual Descript one-second TXT export, integer-second granularity; no interpolated word timing.'})
    # Avoid a 0.96s three-word Activity flash. Its last actual subcue and the
    # next original cue are exactly contiguous; join them with unchanged outer
    # boundaries, speech and screen. The genuine 319s screen cut remains.
    j = next(i for i,x in enumerate(expanded) if x['original_cues']==[88] and x['start']==319.0)
    left,right = expanded[j:j+2]
    assert right['original_cues']==[89] and left['end']==right['start']
    assert left['screenshot_id']==right['screenshot_id']==screen(28)
    joined_refs={'Activity':'Activity','Responding':'Responding','Released':'Released'}
    expanded[j:j+2]=[dict(left,end=right['end'],text=left['text']+' '+right['text'],original_cues=[88,89],
                          required_labels=list(joined_refs),spoken_references=joined_refs,instructional=True)]
    assert len(expanded)==94
    assert words(' '.join(c['text'] for c in expanded))==words(' '.join(x['narration'] for x in lesson['scenes']))
    used={c['screenshot_id'] for c in expanded};assert len(used)==21
    records={ident:row for ident,row in records.items() if ident in used}
    capture_path=s/f'expansion/plans/{NAME}-take-01.captures.json'
    retain(capture_path,{'app':'Dispatch','screenshots':list(records.values()),'source_manifest':freeze['capture_manifest'],
                        'source_manifest_sha256':freeze['capture_manifest_sha256'],
                        'scope':'21 unchanged images used from the frozen 22-image subset. Dispatch20 created-console remains supplemental historical evidence; it is not added as filler. Full source manifest and excluded red LogBox image remain unchanged.'})
    caption_path=s/f'expansion/audio/{NAME}-take-01-screen-cuts.srt'
    retain(caption_path,''.join(f"{i}\n{stamp(c['start'],True)} --> {stamp(c['end'],True)}\n{c['text']}\n\n" for i,c in enumerate(expanded,1)))
    retain(s/f'expansion/audio/{NAME}-take-01-screen-cuts-provenance.json',{
        'lesson_sha256':FROZEN,'audio_sha256':AUDIO,'source_corrected_srt_sha256':CORRECTED,'genuine_one_second_txt_sha256':TRANSCRIPT,
        'raw_cues':91,'derived_cues':94,'splits':provenance,
        'contiguous_join':{'original_cues':[88,89],'start':319.0,'removed_contiguous_boundary':319.96,'end':323.559,
                           'reason':'Join the 0.96-second calls/Activity fragment with the immediately contiguous following actual speech cue, retaining exact words and existing outer boundaries.'},
        'exact_words_order_and_all_other_original_bounds_unchanged':True})
    readability=[{'cue':i,'duration_seconds':round(c['end']-c['start'],3),'words':len(c['text'].split()),'text':c['text']}
                 for i,c in enumerate(expanded,1) if c['end']-c['start']<1.5]
    assert all(c['end']-c['start']>=1.0 for c in expanded), readability
    retain(s/f'expansion/audio/{NAME}-take-01-caption-readability.json',{
        'audio_sha256':AUDIO,'captions_sha256':digest(caption_path),'derived_cues':94,
        'minimum_cue_seconds':min(c['end']-c['start'] for c in expanded),'cues_under_1_5_seconds':readability,
        'review':'No subsecond cue. Four genuine-anchor splits plus one contiguous join retain exact812words; encoded-caption visual review still required.'})
    groups=[];position=0
    for scene in lesson['scenes']:
        expected=words(scene['narration']);actual=[];entries=[]
        while len(actual)<len(expected):
            c=expanded[position];position+=1;actual+=words(c['text']);entries.append(dict(c,cue=position))
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
        built={'id':authored['id'],'title':authored['title'],'kind':'operational','start':start,'end':end,
               'visual_required_labels':authored['required_labels'],'screens':screens,'captions':entries}
        review={'passed':True,'reviewer':'Codex','reviewed_at':REVIEWED_AT,'correspondence_reviewed':True,'no_unseen_controls':True,
                'mapping_sha256':instruction_scene_digest(built,records),
                'method':'All frozen sources actually inspected. Exact94cue/21image correspondence uses four genuine integer-second cuts. Full actual near/far rows, stale-position explanation, saved/pinned/re-evaluated/closed states are distinguished. The far unit and199:22 card estimate recur exactly where spoken; no new application action or unseen control is inferred.'}
        scenes.append({'id':authored['id'],'start':start,'end':end,'screens':screens,
                       'captions':[{key:c[key] for key in ['cue','screenshot_id','required_labels','spoken_references','instructional']} for c in entries],
                       'instruction_review':review})
    plan={'schema_version':1,'lesson_id':NAME,'duration_seconds':duration,'instruction_mapping':'reviewed_scene_coverage',
          'display_context':'TRAINING ONLY · fictional department',
          'narration':{'file':audio.relative_to(s).as_posix(),'sha256':AUDIO,'kind':'approved_natural_narration',
            'approval':{'reviewer':'Codex','reviewed_at':REVIEWED_AT,'sha256':AUDIO,'complete_natural_narration':True,
                'method':'Actual eight generated paragraphs fully decoded, exact812-word frozen script aligned; all91source speech cues measured non-silent. Parent read-only speaker audit reported all eight paragraphs enabled for the established natural stock narrator. No per-paragraph provider-ID readback or human intelligibility review is claimed.',
                'qa_file':qa_path.relative_to(s).as_posix(),'qa_sha256':digest(qa_path)}},
          'captions':{'file':caption_path.relative_to(s).as_posix(),'sha256':digest(caption_path),'kind':'speech_timed_srt',
            'approval':{'reviewer':'Codex','reviewed_at':REVIEWED_AT,'sha256':digest(caption_path),'audio_sha256':AUDIO,'speech_timing_reviewed':True,
                'method':'Actual91source cue boundaries plus four documented genuine integer-second subdivisions; one exactly contiguous Activity fragment joined to the next original cue. Exact words/order unchanged. No estimated word timing.',
                'timing_provenance':f'expansion/audio/{NAME}-take-01-screen-cuts-provenance.json'}},
          'capture_manifests':[{'file':capture_path.relative_to(s).as_posix(),'sha256':digest(capture_path)}],
          'screenshot_reviews':{ident:{'reviewer':'Codex','reviewed_at':REVIEWED_AT,'sha256':row['sha256'],'application_visible':True,'labels_legible':True,'no_errors':True,'method':row['viewport_review']['method']} for ident,row in records.items()},
          'scenes':scenes,'source_freeze':{'lesson_sha256':FROZEN,'spoken_words':812,'voice_source':voice.relative_to(s).as_posix(),
              'capture_freeze_sha256':FREEZE,'untimed_sequence_sha256':SEQUENCE,'source_images_frozen':22,'source_images_used':21},
          'limitations':['All frozen812spokenwords, eight scenes and original source images unchanged. Full media/frame and native playback gates still required.',
              'Near/far, stale/fresh and historical saved-call states are separately recorded observations; no current status, device GPS or real-provider alert delivery is inferred.',
              'Apply recommendation and Confirm prepare recipients. Only the separate own training call was created and later closed with notifications off; the original three active calls remain preserved.',
              'Strike alarm2 is visible but not exercised; only one level is configured. The empty Awaiting Resources queue demonstrates no fulfilment or dismissal.',
              'The read-only voice audit can establish the shared speaker and enabled state, not per-paragraph external provider IDs. No editor or signed export URL is published.']}
    path=s/f'expansion/plans/{NAME}-take-01.plan.json';retain(path,plan)
    print(json.dumps({'plan':path.relative_to(root).as_posix(),'sha256':digest(path),'scenes':8,'selected_images':21,
                      'screen_intervals':sum(len(x['screens']) for x in scenes),'raw_cues':91,'derived_cues':94,'duration_seconds':duration},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    build(parser.parse_args().root.resolve())
