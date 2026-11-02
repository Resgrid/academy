"""Map Contacts' actual export cues to the unchanged reviewed application frames.

Default/--source-preflight is read-only and does not approve narration or rendering.
--write-correspondence retains a source-only scaffold. An assembly plan additionally
requires exact downloaded-audio, passed QA and full-listening-review hashes supplied
in --approved-inputs, plus genuine word anchors for the four mixed-screen cues.
No canonical lesson, publication evidence, readiness, website or app is changed.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
NAME = 'core-contacts-administration'
BASE = Path('expansion/plans/core-contacts-administration-capture-freeze-20261028')
ASSEMBLY = Path('expansion/plans/core-contacts-administration-take-01-source-correspondence-20261028')
FROZEN = 'f497c0b12cc770b0dde6c555329a1905eabe170013beb3a4f70ab073d0daf67e'
MANIFEST = '326872b591a6802e3cc81aa154abeb232ccefc56e4ca3b58e9c3f19f7fb3245e'
SEQUENCE = '5f90fae8716cb8c4fa6ff6e2dbdddd25b58828b7aad3e0cddb231d35bf031853'
RAW_FILE = Path('expansion/audio/core-contacts-administration-generated-20261028.raw.srt')
RAW = 'bccb5cbb58a05c3cce5d8cfe2450ee70e722d978e06fcaf353519ff416e698dc'
TEXT_FILE = Path('expansion/audio/core-contacts-administration-generated-20261028.raw.txt')
TEXT = '2509dd3ce071eaca3cee73454d20e96120315d4b4aa8a9cb136ddbdf3cbd7980'
REVIEWED_AT = '2026-10-28T21:14:43+00:00'
RANGES = [(1,10),(11,20),(21,29),(30,37),(38,46),(47,56),(57,64),(65,75),(76,84),(85,95)]
# These are existing export cue boundaries. No word split is assumed here.
SCREEN_STARTS = {1:1,11:2,18:3,21:4,26:5,30:6,33:8,36:6,37:7,38:9,
                 42:10,47:11,51:12,57:13,59:14,65:14,66:16,68:17,
                 69:14,71:18,72:20,75:17,76:19,78:21,79:23,85:24,88:13}
# A single genuine raw cue mentions separately captured controls/results. A plan
# must use a real word-anchor cut, never a duration proportion or interpolation.
MIXED = {
  17: {'before':2,'after':3,'reason':'Show Save on the prepared category before its returned saved row.'},
  32: {'before':6,'after':7,'reason':'Show the list View control before saved person name/channels.'},
  41: {'before':9,'after':10,'reason':'Organization email and Office Phone are in separate viewports.'},
  71: {'before':18,'after':20,'reason':'Named category and copied mailing fields are separate viewports.'},
}
REFERENCES = {
  6:{'Categories':'Categories'},7:{'Name':'name','Description':'description','Color':'color','Contacts In Category':'contact count'},
  11:{'Add Category':'Add Category'},12:{'Academy Partner Directory':'Academy Partner Directory','Name':'Name'},
  14:{'#0080ff':'blue color'},15:{'Display On Map':'Display On Map','Map Icon':'Map Icon','Default':'Default'},
  17:{'Save':'Save'},18:{'Academy Partner Directory':'name','#0080ff':'blue color'},19:{'Contacts In Category':'Contacts In Category','0':'zero'},
  21:{'Add Contact':'Add Contact','Person':'Person','Academy Partner Directory':'Academy Partner Directory'},
  22:{'Sylvie':'Sylvie','Brett':'Brett','First Name':'first','Last Name':'last name'},
  23:{'Company\\Location Name':'organization field'},25:{'Email Address':'Email Address','Cell Phone':'Cell Phone'},
  26:{'Description':'Description'},27:{'TRAINING ONLY - Fictional community partner liaison. Verify current contact details before operational use.':'fictional community partner liaison'},
  30:{'Search:':'Search','Brett':'Brett'},31:{'Sylvie Brett':'Sylvie Brett','Person':'Person','Academy Partner Directory':'named category'},
  32:{'View':'View'},33:{'Description':'Description'},36:{'Academy Partner Directory':'named category'},37:{'Additional Info':'Additional Info','Category:':'category value','0':'numeric'},
  38:{'Location or Company':'Location or Company'},39:{'Category':'category','First Name':'person name fields','Last Name':'person name fields'},
  40:{'Academy Logistics Desk (fictional)':'Academy Logistics Desk, marked fictional','Company\\Location Name':'Company Location Name'},
  41:{'Email Address':'email'},42:{'+13125550143':'zero one four three'},43:{'Description':'Description'},
  47:{'Location Info':'Location Info','GPS Location':'GPS Location'},48:{'41.8722':'Chicago pair','-87.6524':'Chicago pair'},
  49:{'Entrance GPS Location':'Entrance GPS Location','Exit GPS Location':'Exit GPS Location'},
  51:{'Physical Address':'Physical Address','1000 Training Avenue (fictional)':'fictional Training Avenue street'},52:{'Chicago':'Chicago','IL':'Illinois','Postal Code':'postal code'},
  53:{'Same as Physical?':'Same as Physical','Mailing Address':'Mailing Address','Save':'Save'},
  57:{'Academy Partner Directory':'Academy Partner Directory'},58:{'Sylvie Brett':'person','Academy Logistics Desk (fictional)':'logistics organization'},
  59:{'Search:':'Search','Logistics':'Logistics'},61:{'Showing 1 to 1 of 1 entries (filtered from 2 total entries)':'one result is filtered from two entries'},62:{'View':'View','Edit':'Edit'},
  65:{'View':'Open'},66:{'Contact Details':'Contact Details','Location Info':'Location Info'},67:{'41.8722,-87.6524':'stored coordinate pair'},
  68:{'Physical Address':'physical address','Description':'Description'},70:{'Edit':'Edit'},71:{'Academy Partner Directory':'category is selected by name'},
  72:{'1000 Training Avenue (fictional)':'street','City':'city','State':'state','Postal Code':'postal code'},73:{'Same as Physical?':'Same as Physical'},
  75:{'Mailing Address':'View proves that nothing was saved'},77:{'Office Phone':'Office Phone','+13125550143':'zero one four three'},
  78:{'+13125550144':'four'},80:{'+13125550144':'zero one four four'},82:{'Description':'Description'},
  85:{'Categories':'Categories'},86:{'Academy Partner Directory':'Academy Partner Directory','2':'two contacts'},
}

sys.path.insert(0,str(ROOT/'scripts'))
from render_walkthrough import load_cues, validate_inputs, words
from verify_capture_evidence import _Validator, _normalized, _image_dimensions, instruction_scene_digest

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encoded(value): return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
def safe_asset(ref):
    assert isinstance(ref,dict) and re.fullmatch(r'[0-9a-f]{64}',ref.get('sha256',''))
    name=Path(ref['file']);path=(SOURCES/name).resolve()
    assert not name.is_absolute() and SOURCES in path.parents and path.is_file()
    assert sha(path)==ref['sha256'], 'Re-review changed input: '+str(name)
    return path

def prepare():
    lesson_path=SOURCES/BASE/(NAME+'.narrated-source.json')
    manifest_path=SOURCES/BASE/(NAME+'.captures.reviewed.json')
    assert sha(lesson_path)==FROZEN and sha(manifest_path)==MANIFEST
    assert sha(SOURCES/BASE/(NAME+'.screen-sequence.json'))==SEQUENCE
    assert sha(SOURCES/RAW_FILE)==RAW and sha(SOURCES/TEXT_FILE)==TEXT
    lesson=json.loads(lesson_path.read_text());manifest=copy.deepcopy(json.loads(manifest_path.read_text()))
    cues=load_cues(SOURCES/RAW_FILE);assert len(cues)==95 and len(lesson['scenes'])==10
    assert words((SOURCES/TEXT_FILE).read_text())==words(' '.join(s['narration'] for s in lesson['scenes']))
    records=manifest['screenshots'];assert len(records)==22
    by_number={int(r['id'][:3]):r for r in records}
    for row in records:
        assert row['eligible_for_lesson'] and row['capture_review']['passed']
        assert sha(SOURCES/row['file'])==row['sha256'] and sha(SOURCES/row['dom_file'])==row['dom_sha256']
        assert _image_dimensions(SOURCES/row['file'])==(row['width'],row['height'])
    person=by_number[7]
    for label in ['Additional Info','Category:','0']:
        if label not in person['visible_labels']:person['visible_labels'].append(label)
    person['assembly_observation_review']={'reviewer':'Codex independent original-size image inspection',
      'reviewed_at':REVIEWED_AT,'sha256':person['sha256'],'added_visible_labels':['Additional Info','Category:','0'],
      'method':'All three literals are fully readable in original007 pixels; this assembly copy leaves frozen manifest/image/DOM untouched.'}
    address=by_number[17]
    if 'Mailing Address' not in address['visible_labels']:address['visible_labels'].append('Mailing Address')
    address['assembly_observation_review']={'reviewer':'Codex independent original-size image inspection',
      'reviewed_at':REVIEWED_AT,'sha256':address['sha256'],'added_visible_labels':['Mailing Address'],
      'method':'Original017 plainly shows the Mailing Address heading and empty displayed values alongside saved Physical Address/Description; no copied mailing fields are inferred from View.'}
    mapping=[];selected=None
    for number,cue in enumerate(cues,1):
        if number in SCREEN_STARTS:selected=SCREEN_STARTS[number]
        shot=by_number[selected];refs=REFERENCES.get(number,{})
        assert set(refs)<=set(shot['visible_labels']),(number,refs)
        validator=_Validator(SOURCES);validator.spoken_references(dict(cue,spoken_references=refs),{_normalized(x) for x in refs},str(number),True)
        assert not validator.issues,validator.issues
        mapping.append(dict(cue,cue=number,screenshot_id=shot['id'],required_labels=list(refs),spoken_references=refs,
            pending_word_anchor=MIXED.get(number)))
    for (first,last),scene in zip(RANGES,lesson['scenes']):
        assert words(' '.join(c['text'] for c in cues[first-1:last]))==words(scene['narration'])
    manifest.update(kind='reviewed_actual_contacts_assembly_subset',source_frozen_manifest=(BASE/(NAME+'.captures.reviewed.json')).as_posix(),source_frozen_manifest_sha256=MANIFEST)
    source={'schema_version':1,'id':NAME,'status':'source-only actual-cue correspondence scaffold; NOT renderer/canonical ready',
      'renderer_ready':False,'narration_approved':False,'canonical_ready':False,'source_frozen_sha256':FROZEN,
      'raw_captions':{'file':RAW_FILE.as_posix(),'sha256':RAW,'cues':95},'exact_text':{'file':TEXT_FILE.as_posix(),'sha256':TEXT},
      'scene_ranges':[{'scene_id':s['id'],'first_cue':a,'last_cue':b} for (a,b),s in zip(RANGES,lesson['scenes'])],
      'cues':mapping,'pending_dependencies':['Downloaded actual audio and exact SHA-256','Passed full-decode/script/per-cue energy QA with exact SHA-256','Genuine full natural-listening review bound to this frozen lesson and audio, with exact review-file SHA-256','Actual one-second word anchors for mixed cues17,32,41,71'],
      'limits':['No within-cue time has been guessed or speech word split yet.','Raw004 person Save is offscreen; saved006 begins after saving without pretending to show that control.','Prepared021 phone Save is offscreen;023 is independent reopen proof, not a picture of Save.','Original015 fade and022 failed richtext replacement stay excluded.','Assembly-only007 adds three actually legible labels and017 adds its readable Mailing Address heading; all frozen inputs remain byte-identical.']}
    return lesson_path,lesson,manifest,source

def word_anchors(path):
    text=path.read_text();parts=re.split(r'\[(\d{2}):(\d{2}):(\d{2})\]',text)
    assert len(parts)>4 and not words(parts[0])
    offset=0;result=[]
    for n in range(1,len(parts),4):
        time=int(parts[n])*3600+int(parts[n+1])*60+int(parts[n+2]);segment=parts[n+3]
        result.append((time,offset));offset+=len(words(segment))
    return result,words(re.sub(r'\[\d{2}:\d{2}:\d{2}\]','',text))

def build(approved,approved_sha,source_review_only=False):
    assert re.fullmatch(r'[0-9a-f]{64}',approved_sha or '') and sha(approved)==approved_sha, 'Supply exact reviewed approval-input SHA-256.'
    inputs=json.loads(Path(approved).read_text());assert inputs['lesson_id']==NAME and inputs['lesson_sha256']==FROZEN
    keys=['audio','captions','qa','word_timing']+([] if source_review_only else ['listening_review'])
    paths={key:safe_asset(inputs[key]) for key in keys}
    lesson_path,lesson,manifest,source=prepare();qa=json.loads(paths['qa'].read_text())
    assert qa['passed'] is True and not qa['issues'] and not qa['possible_speech_gaps']
    assert qa['audio']['sha256']==inputs['audio']['sha256'] and qa['audio']['full_decode']=='passed'
    assert qa['lesson']['sha256']==FROZEN and qa['raw_captions']['sha256']==RAW
    assert qa['corrected_captions']['sha256']==inputs['captions']['sha256']
    assert qa['silent_raw_cues']==qa['silent_corrected_cues']==0
    assert qa['raw_captions']['cues']==qa['corrected_captions']['cues']==95
    if not source_review_only:
        heard=json.loads(paths['listening_review'].read_text())
        assert heard['complete_natural_narration'] is True and heard['audio_sha256']==inputs['audio']['sha256'] and heard['lesson_sha256']==FROZEN
        assert heard['reviewer'] and heard['evidence'] and datetime.fromisoformat(heard['reviewed_at'].replace('Z','+00:00'))<=datetime.now(timezone.utc)
    cues=load_cues(paths['captions']);assert len(cues)==95
    for corrected,raw in zip(cues,source['cues']):
        assert (corrected['start'],corrected['end'])==(raw['start'],raw['end']) and words(corrected['text'])==words(raw['text'])
    anchors,transcript_words=word_anchors(paths['word_timing']);assert transcript_words==words(' '.join(s['narration'] for s in lesson['scenes']))
    splits={s['cue']:s for s in inputs['splits']};assert set(splits)==set(MIXED)
    expanded=[];global_offset=0;by_id={r['id']:r for r in manifest['screenshots']};by_number={int(r['id'][:3]):r for r in manifest['screenshots']}
    for number,(cue,original) in enumerate(zip(cues,source['cues']),1):
        segments=[dict(cue,screenshot_id=original['screenshot_id'],required_labels=original['required_labels'],spoken_references=original['spoken_references'])]
        if number in splits:
            split=splits[number];at=float(split['at_seconds']);before,after=split['before_text'],split['after_text']
            assert words(before)+words(after)==words(cue['text']) and words(before) and words(after)
            assert (at,global_offset+len(words(before))) in anchors,'Use a genuine transcript marker at this exact word boundary.'
            assert at-cue['start']>=0.7 and cue['end']-at>=0.7,'Avoid unreadable microcues; obtain an earlier genuine word anchor.'
            segments=[]
            for text,start,end,side in [(before,cue['start'],at,'before'),(after,at,cue['end'],'after')]:
                shot=by_number[MIXED[number][side]];refs=split[side+'_references']
                assert refs and set(refs)<=set(shot['visible_labels'])
                validator=_Validator(SOURCES);validator.spoken_references({'text':text,'spoken_references':refs},{_normalized(x) for x in refs},str(number),True);assert not validator.issues,validator.issues
                segments.append({'start':start,'end':end,'text':text,'screenshot_id':shot['id'],'required_labels':list(refs),'spoken_references':refs})
        for segment in segments:segment.update(raw_cue=number,cue=len(expanded)+1,instructional=bool(segment['required_labels']));expanded.append(segment)
        global_offset+=len(words(cue['text']))
    duration=qa['audio']['duration_seconds'];assert duration>=expanded[-1]['end']
    assert words(' '.join(e['text'] for e in expanded))==words(' '.join(s['narration'] for s in lesson['scenes']))
    now=datetime.now(timezone.utc).isoformat();scenes=[]
    for index,((first,last),scene) in enumerate(zip(RANGES,lesson['scenes'])):
        start=0 if index==0 else cues[first-1]['start'];end=duration if index==9 else cues[RANGES[index+1][0]-1]['start']
        entries=[e for e in expanded if first<=e['raw_cue']<=last];screens=[];selected=entries[0]['screenshot_id'];screen_start=start
        for entry in entries:
            if entry['screenshot_id']!=selected:
                screens.append({'screenshot_id':selected,'start':screen_start,'end':entry['start']});selected=entry['screenshot_id'];screen_start=entry['start']
        screens.append({'screenshot_id':selected,'start':screen_start,'end':end})
        built={'id':scene['id'],'title':scene['title'],'kind':'operational','start':start,'end':end,'visual_required_labels':scene['required_labels'],'screens':screens,'captions':entries}
        union={label for screen in screens for label in by_id[screen['screenshot_id']]['visible_labels']};assert set(scene['required_labels'])<=union
        review={'passed':True,'reviewer':'Codex actual export/source-image correspondence review','reviewed_at':now,'correspondence_reviewed':True,'no_unseen_controls':True,
          'mapping_sha256':instruction_scene_digest(built,by_id),'method':'All95 genuine export cues matched to frozen words and22 reviewed actual Core images. Four derived word splits use exact cumulative-word positions at genuine one-second transcript markers. No interpolation, synthetic click, unseen Save, failed edit or map result is inferred.'}
        scenes.append({'id':scene['id'],'start':start,'end':end,'screens':screens,'captions':[{k:e[k] for k in ['cue','screenshot_id','required_labels','spoken_references','instructional']} for e in entries],'instruction_review':review})
    def stamp(seconds):
        ms=round(seconds*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
    captions='\n\n'.join(f"{e['cue']}\n{stamp(e['start'])} --> {stamp(e['end'])}\n{e['text']}" for e in expanded)+'\n'
    if source_review_only:
        return lesson_path,{'kind':'reviewed_actual_contacts_source_cue_correspondence','lesson_id':NAME,
          'status':'source correspondence reviewed; full listening approval pending; NOT an assembly plan',
          'renderer_ready':False,'narration_approved':False,'canonical_ready':False,'rendered':False,
          'frozen_lesson_sha256':FROZEN,'media_input_sha256':approved_sha,'media_inputs':inputs,
          'duration_seconds':duration,'raw_cues':95,'derived_cues':len(expanded),'scenes':scenes,
          'cue_correspondence':expanded,'reviewed_manifest_sha256':hashlib.sha256(encoded(manifest)).hexdigest(),
          'limitations':source['limits'][1:]+['Four added cue boundaries use actual service whole-second markers, not millisecond word precision or interpolation.','Full human listening review remains required before assembly authoring or rendering.']},None,manifest
    cap_path=ASSEMBLY/(NAME+'.derived.srt');capture_path=ASSEMBLY/'captures.reviewed.json'
    plan={'schema_version':1,'lesson_id':NAME,'duration_seconds':duration,'instruction_mapping':'reviewed_scene_coverage','display_context':'TRAINING ONLY · fictional department',
      'narration':dict(inputs['audio'],kind='approved_natural_narration',approval={'reviewer':heard['reviewer'],'reviewed_at':heard['reviewed_at'],'sha256':inputs['audio']['sha256'],'complete_natural_narration':True,'evidence':heard['evidence'],'qa_file':inputs['qa']['file'],'qa_sha256':inputs['qa']['sha256'],'listening_review_file':inputs['listening_review']['file'],'listening_review_sha256':inputs['listening_review']['sha256']}),
      'captions':{'file':cap_path.as_posix(),'sha256':hashlib.sha256(captions.encode()).hexdigest(),'kind':'speech_timed_srt','approval':{'reviewer':'Codex exact frozen words/export/word-anchor correspondence','reviewed_at':now,'sha256':hashlib.sha256(captions.encode()).hexdigest(),'audio_sha256':inputs['audio']['sha256'],'speech_timing_reviewed':True,'method':'Original95 cue starts/ends retained; four added boundaries are actual transcript word markers, recorded in input approval.','word_timing_file':inputs['word_timing']['file'],'word_timing_sha256':inputs['word_timing']['sha256']}},
      'capture_manifests':[{'file':capture_path.as_posix(),'sha256':hashlib.sha256(encoded(manifest)).hexdigest()}],
      'screenshot_reviews':{r['id']:{'reviewer':'Codex original-size Core image inspection','reviewed_at':REVIEWED_AT,'sha256':r['sha256'],'application_visible':True,'labels_legible':True,'no_errors':True} for r in manifest['screenshots']},
      'scenes':scenes,'publishable':False,
      'limitations':source['limits'][1:]+['Four derived cuts use genuine service whole-second word markers; no interpolation or millisecond word precision is claimed.'],
      'approved_input_sha256':approved_sha}
    return lesson_path,plan,captions,manifest

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source-preflight',action='store_true');parser.add_argument('--write-correspondence',action='store_true')
    parser.add_argument('--approved-inputs',type=Path);parser.add_argument('--approved-inputs-sha256');parser.add_argument('--output',type=Path)
    parser.add_argument('--media-inputs',type=Path);parser.add_argument('--media-inputs-sha256');parser.add_argument('--write-media-correspondence',action='store_true')
    args=parser.parse_args();lesson_path,lesson,manifest,source=prepare()
    if args.media_inputs or args.write_media_correspondence:
        assert not(args.output or args.approved_inputs or args.approved_inputs_sha256),'Do not combine source correspondence with approved assembly authoring.'
        if not(args.media_inputs and args.media_inputs_sha256):parser.error('Require exact actual media-input file and hash; no listening approval is implied.')
        _,review,_,manifest=build(args.media_inputs,args.media_inputs_sha256,source_review_only=True)
        if args.write_media_correspondence:
            target=SOURCES/ASSEMBLY/'correspondence.reviewed-pending-listening.json';payload=encoded(review)
            assert not target.exists(),'Preserve the retained source review; choose a new version in the recipe.'
            target.write_bytes(payload)
        print(json.dumps({'passed_source_correspondence':True,'scenes':10,'raw_cues':95,'derived_cues':review['derived_cues'],'duration':review['duration_seconds'],'narration_approved':False,'renderer_ready':False,'rendered':False,'canonical_ready':False}))
    elif args.output or args.approved_inputs:
        if not(args.output and args.approved_inputs and args.approved_inputs_sha256):parser.error('Require output plus exact approved-input file and hash after actual download, QA and full listening review.')
        lesson_path,plan,captions,manifest=build(args.approved_inputs,args.approved_inputs_sha256)
        path=args.output.resolve();canonical=(SOURCES/'expansion/lessons').resolve()
        assert SOURCES/'expansion/plans' in path.parents and canonical not in path.parents and not path.exists(),'Use a new staged plan output.'
        outputs={SOURCES/ASSEMBLY/'captures.reviewed.json':encoded(manifest),SOURCES/ASSEMBLY/(NAME+'.derived.srt'):captions.encode(),path:encoded(plan)}
        for target,payload in outputs.items():assert not target.exists() or target.read_bytes()==payload,'Preserve prior authored version.'
        for target,payload in outputs.items():target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
        recipe=validate_inputs(lesson_path,path,SOURCES)
        print(json.dumps({'passed':True,'scenes':len(recipe['scenes']),'cues':len(recipe['cues']),'duration':recipe['duration'],'rendered':False,'canonical_ready':False}))
    else:
        if args.write_correspondence:
            outputs={SOURCES/ASSEMBLY/'captures.reviewed.json':encoded(manifest),SOURCES/ASSEMBLY/'correspondence.scaffold.json':encoded(source)}
            for target,payload in outputs.items():assert not target.exists() or target.read_bytes()==payload,'Preserve historical correspondence.'
            for target,payload in outputs.items():target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
        print(json.dumps({'passed_source_preflight':True,'scenes':10,'cues':95,'reviewed_sources':22,'pending_mixed_cues':list(MIXED),'renderer_ready':False,'narration_approved':False,'rendered':False,'canonical_ready':False}))

if __name__=='__main__':main()
