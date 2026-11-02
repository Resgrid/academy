"""Propose Groups/Units actual-source caption timing; never assemble or render.

Default is read-only. --write-proposed requires a NEW directory and real FFmpeg
to decode the complete approved audio and measure every derived cue. Only the
genuine service whole-second markers below may split words. The original123
service cues, audio, frozen learner words and reviewed source pairs are retained.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import textwrap

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
NAME = 'core-groups-units-administration'
BASE = Path('expansion/plans') / (NAME + '-capture-freeze-20261028')
DIRECTORY = SOURCES / 'expansion/plans/core-groups-units-administration-take-01-proposed-derived-20261028'
AUDIO = Path('expansion/audio') / (NAME + '.m4a')
RAW = Path('expansion/audio') / (NAME + '-generated-20261028.raw.srt')
CORRECTED = Path('expansion/audio') / (NAME + '.srt')
TEXT = Path('expansion/audio') / (NAME + '-generated-20261028.raw.txt')
ANCHORS = Path('expansion/audio') / (NAME + '-generated-20261028.one-second.txt')
ORIGINAL_QA = Path('expansion/audio') / (NAME + '.actual.qa.json')
LISTENING = Path('expansion/audio') / (NAME + '.listening-review.json')
FROZEN = '56b13d11be889d0825950a2cb33c0453c51302872939788ee03c6d1fd7bfee5c'
PINS = {
    BASE / (NAME + '.narrated-source.json'): FROZEN,
    BASE / (NAME + '.captures.reviewed.json'): '655294154349fd715cb5396315d27448cbd481502e52e777f9e82622628a1e3f',
    BASE / (NAME + '.screen-sequence.json'): 'b114b67af040b34efffcde0eb5d0e510ecb2d897f15851c2ba3de4a620302844',
    BASE / 'source-hashes.json': 'd3e96e37b349ce44284b0d341539d393bc93449db1d2fdc6c82dcd2f0549726c',
    BASE / 'source-evidence.json': 'd95a46bb7e6d79d0bdae1d545eefe2b0bc3bbdc055adad35bcb4a8dee6994713',
    RAW: '16d78a6d0fadca34e3ef1ad3ef97868d9458857da025ffc2625c72298d6351f9',
    TEXT: 'e689b4b5e06c7cf415a16c0b4b6147ecbb299c29bda56a37f0c245064c88c867',
    ANCHORS: 'e0a6f3e85a34fa97b9756ddc9270c9d47256d539fdefd8a1cd5f3c7ae3e4e205',
    CORRECTED: '717d9aef7991cbd448ea5431a44ffe81e5a1f65f9a7ed58645c9e429f6eb7a56',
    AUDIO: 'a969e646a19151e47f51e5f96a08db3cdcf5cfd7cf0328d0eb650b7bf8a611ae',
    ORIGINAL_QA: 'ddc5c9947ef23373c884c2e0d18c3df0df7ec55a251676844beff90d59b98549',
    LISTENING: '7b2ff52ceeecc526669a9e707cba49af87fe304d2d3b152c472d63359fec0e56',
}
UTILITY = SOURCES / 'production/qa_core_certification_proposed_captions_20261028.py'
UTILITY_SHA = '6c24c31946717f27f06a6829e32846dbb2420fc894f5d980b245d3a8b9441594'
SCREEN_STARTS = {1:1,2:2,9:2,10:3,11:4,18:4,19:6,25:2,26:7,27:8,
    33:9,35:10,42:11,45:11,46:13,50:14,51:15,56:15,57:17,58:18,
    64:19,67:19,68:20,69:20,70:21,72:14,73:22,82:22,83:23,88:25,
    91:25,92:26,93:26,94:27,95:28,97:26,99:26,100:29,102:30,104:32,
    107:26,108:33,110:34,115:34,118:11}
SPLITS = [
    {'raw_cue':9,'at_seconds':27,'before_text':'Choose Add New Group and','after_text':'keep Organizational Group selected.',
     'before':2,'after':3,'before_references':{'Add New Group':'Add New Group'},'after_references':{'Organizational Group':'Organizational Group'},
     'reason':'Actual Add New Group launcher precedes the blank Organizational form.'},
    {'raw_cue':25,'at_seconds':80,'before_text':'Create another group and','after_text':'select Station Group.',
     'before':2,'after':7,'before_references':{'Add New Group':'Create another group'},'after_references':{'Station Group':'Station Group'},
     'reason':'Actual group launcher precedes Station Group selection and physical-location fields.'},
    {'raw_cue':45,'at_seconds':149,'before_text':'Use the station’s Edit control to check','after_text':'its full name and relationship again.',
     'before':11,'after':12,'before_references':{'Edit':'Edit'},'after_references':{'Group Name':'full name','Parent Group':'relationship'},
     'reason':'The catalog Edit control is pictured before fresh saved Station name/parent readback.'},
    {'raw_cue':56,'at_seconds':192,'before_text':'From the Unit Types section,','after_text':'choose New Unit Type.',
     'before':15,'after':16,'before_references':{},'after_references':{'New Unit Type':'New Unit Type'},
     'reason':'The preceding actual New Unit type link remains until the Unit Types catalog and New Unit Type launcher are named. The link screen does not display a Unit Types heading.'},
    {'raw_cue':67,'at_seconds':229,'before_text':'Save, then','after_text':'read the new type row in the catalog.',
     'before':19,'after':20,'before_references':{'Save':'Save'},'after_references':{'TRAINING ONLY - Community response vehicle':'new type row'},
     'reason':'Keep the actual Save button on screen before the returned Unit Types row.'},
    {'raw_cue':69,'at_seconds':237,'before_text':'Open Edit to verify','after_text':'Support, Standard Actions, and the Van choice again.',
     'before':20,'after':21,'before_references':{'Edit':'Edit'},'after_references':{'Support':'Support','Standard Actions':'Standard Actions','Van':'Van'},
     'reason':'Show the Unit Types Edit launcher before the fresh stored type options.'},
    {'raw_cue':72,'at_seconds':247,'before_text':'Return to New','after_text':'Unit and name the vehicle Training Only, Community',
     'before':14,'after':15,'before_references':{'New Unit':'New'},'after_references':{'Name':'name the vehicle'},
     'reason':'A genuine marker within the two-word New Unit label retains its actual launcher first, followed by the Name control. No subsecond word position is inferred.'},
    {'raw_cue':93,'at_seconds':312,'before_text':'Open Edit and check','after_text':'that both positions and their Required choices remain.',
     'before':26,'after':27,'before_references':{'Edit':'Edit'},'after_references':{'Required?':'Required','Coordination seat':'positions'},
     'reason':'Keep the saved unit’s Edit launcher before its two retained seat definitions.'},
    {'raw_cue':94,'at_seconds':317,'before_text':'Open the Station dropdown to','after_text':'read the complete selected Community Base',
     'before':27,'after':28,'before_references':{'Station':'Station'},'after_references':{'TRAINING ONLY - Community base 20261028':'Community Base'},
     'reason':'Show the closed Station control before the actual open dropdown reveals the complete selected station name.'},
]
ORG = 'TRAINING ONLY - Community coordination 20261028'
STATION = 'TRAINING ONLY - Community base 20261028'
UNIT = 'TRAINING ONLY - Community van 20261028'
TYPE = 'TRAINING ONLY - Community response vehicle'
ROLE = 'TRAINING ONLY - Community response navigator'
REFS = {
 1:{'Stations & Groups':'Stations and Groups'},2:{'Type':'type','Parent':'parent','Members':'member count'},
 10:{'Group Name':'Enter Training Only'},11:{ORG:'exercise date'},12:{'Parent Group':'Parent Group','None':'None'},
 13:{'Group Admins':'Group Admins','Group Users':'Group Users'},18:{'Save Group':'Save Group'},
 19:{'Edit Group':'Edit Group','Group Name':'full name','None':'None'},20:{'Organizational Group':'Organizational'},
 21:{'Group Admins':'membership','Group Users':'selectors'},
 22:{"Users can only be in one group at a time. If you don't see your user in the list they are already in a group.":'only one group at a time'},
 26:{'Group Name':'Name it'},27:{ORG:'new coordination group','Parent Group':'parent'},29:{'Station Address':'address fields','Gps Coordinates':'coordinate pair'},
 33:{'Gps Coordinates':'Gps Coordinates','41.8500':'forty-one point eight five'},34:{'-87.6500':'minus eighty-seven point six five'},
 35:{'41.8500':'both values','-87.6500':'together'},36:{'what3words Address':'what3words'},
 39:{'Group Users':'member','Group Admins':'administrator'},40:{'Select Printer':'printing'},41:{'Save Group':'Save Group'},
 42:{'Members':'zero members','0':'zero'},43:{'Parent':'parent','Organizational':'organizational'},
 46:{'Gps Coordinates':'coordinate pair','what3words Address':'what3words'},47:{'Print Calls to Printer':'Print Calls to Printer'},
 50:{'Units':'Units','New Unit':'New Unit'},51:{'Name':'Name','Type':'Type','Station':'Station','Roles':'role positions'},
 52:{'No Station':'No Station'},53:{'Roles':'role position'},54:{'here':'type link'},
 57:{'Unit Type Name':'Enter Training Only'},58:{'Class':'Class','Support':'Support'},
 60:{'Standard Actions':'Standard Actions','Map Icon':'Map Icon','Van':'Van'},61:{'No file chosen':'file remains empty'},
 64:{'Preview':'preview','Van':'Van','Light map':'light'},65:{'Dark map':'dark','In a list':'list'},
 68:{TYPE:'full name','Default Unit Actions':'Default Unit Actions','Van':'Van'},
 73:{UNIT:'Van'},74:{'Type':'type','Station':'station'},75:{'Add Role':'Add two positions'},
 76:{'Coordination seat':'Coordination Seat',ROLE:'Community Response Navigator'},77:{'Required?':'Required'},
 78:{'Optional support seat':'Optional Support Seat','-- None --':'no personnel-role restriction'},79:{'Required?':'Required'},
 82:{'Browse Templates':'Browse Templates'},83:{'Security Companies':'Security Companies'},
 84:{'Security Patrol':'Patrol','Alarm Response Team':'Alarm Response Team'},85:{'Use these roles':'Use These Roles'},87:{'Close':'Close'},
 88:{'Coordination seat':'two prepared positions','Optional support seat':'positions'},
 91:{'Save':'Save'},92:{UNIT:'full name',TYPE:'training vehicle type'},96:{'Update':'Update'},97:{'Available':'Available'},
 99:{'Unit Staffing':'Unit Staffing'},100:{'Engine 51':'Engine fifty-one','Christopher Herrmann':'Herrmann'},
 101:{'Not Staffed':'Not Staffed','Not Occupied':'Not Occupied'},102:{'Not Occupied':'person selector'},
 104:{'Not Occupied':'without selecting anyone'},105:{'Save':'Save'},107:{'Units':'Units'},
 108:{ORG:'Community Coordination parent'},109:{STATION:'Community Base station',UNIT:'vehicle'},
 110:{STATION:'station',UNIT:'unit'},115:{ORG:'coordination structure',STATION:'station',UNIT:'vehicles'},
 118:{ORG:'coordination groups',STATION:'staging bases'},
}

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encoded(value): return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()

def utility():
    assert sha(UTILITY)==UTILITY_SHA,'Retain exact timing/reference utility; no silent rule changes.'
    spec=importlib.util.spec_from_file_location('retained_groups_timing_utility',UTILITY)
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    return helper

def prepare():
    helper=utility()
    from render_walkthrough import load_cues,words
    from verify_capture_evidence import _image_dimensions
    for path,digest in PINS.items(): assert sha(SOURCES/path)==digest,'Changed retained input: '+str(path)
    lesson=json.loads((SOURCES/BASE/(NAME+'.narrated-source.json')).read_text())
    manifest=json.loads((SOURCES/BASE/(NAME+'.captures.reviewed.json')).read_text())
    sequence=json.loads((SOURCES/BASE/(NAME+'.screen-sequence.json')).read_text())
    evidence=json.loads((SOURCES/BASE/'source-evidence.json').read_text())
    assert len(evidence['files'])==37
    for row in evidence['files']:
        assert row['repo']=='Core' and sha(ROOT.parents[2]/row['path'])==row['sha256'],'Changed cited Core source: '+row['path']
    raw=load_cues(SOURCES/RAW);corrected=load_cues(SOURCES/CORRECTED)
    assert len(raw)==len(corrected)==123 and len(lesson['scenes'])==15
    for a,b in zip(raw,corrected): assert (a['start'],a['end'],words(a['text']))==(b['start'],b['end'],words(b['text']))
    all_words=words(' '.join(s['narration'] for s in lesson['scenes']))
    anchors,anchor_words=helper.service_anchors((SOURCES/ANCHORS).read_text())
    assert len(all_words)==1050
    assert all_words==words((SOURCES/TEXT).read_text())==words(' '.join(c['text'] for c in raw))==anchor_words
    qa=json.loads((SOURCES/ORIGINAL_QA).read_text());heard=json.loads((SOURCES/LISTENING).read_text())
    assert qa['passed'] and not qa['issues'] and not qa['possible_speech_gaps']
    assert qa['audio']['sha256']==PINS[AUDIO] and qa['audio']['full_decode']=='passed'
    assert qa['lesson']['sha256']==FROZEN and qa['silent_raw_cues']==qa['silent_corrected_cues']==0
    assert heard['complete_natural_narration'] is True and heard['lesson_sha256']==FROZEN and heard['audio_sha256']==PINS[AUDIO]
    assert heard['reviewer'] and heard['evidence']
    assert datetime.fromisoformat(heard['reviewed_at'].replace('Z','+00:00'))<=datetime.now(timezone.utc)
    rows={int(r['id'][:3]):r for r in manifest['screenshots']}
    assert len(rows)==31 and not {5,24,31}&set(rows)
    for row in rows.values():
        assert row['eligible_for_lesson'] and row['capture_review']['passed']
        assert sha(SOURCES/row['file'])==row['sha256'] and sha(SOURCES/row['dom_file'])==row['dom_sha256']
        assert _image_dimensions(SOURCES/row['file'])==(1434,773)
    source_map=[];current=None;split_numbers={s['raw_cue'] for s in SPLITS}
    for number,cue in enumerate(raw,1):
        current=SCREEN_STARTS.get(number,current);assert current in rows
        refs=REFS.get(number,{})
        if number not in split_numbers: helper.references(cue['text'],refs,rows[current])
        source_map.append(dict(cue,raw_cue=number,screenshot_id=rows[current]['id'],required_labels=list(refs),spoken_references=refs))
    operations=[helper.check_anchor(s,raw,anchors) for s in SPLITS]
    splits={s['raw_cue']:s for s in SPLITS};expanded=[]
    for number,cue in enumerate(source_map,1):
        if number in splits:
            split=splits[number]
            for side in ['before','after']:
                text=split[side+'_text'];refs=split[side+'_references'];row=rows[split[side]]
                helper.references(text,refs,row)
                expanded.append({'start':cue['start'] if side=='before' else float(split['at_seconds']),
                    'end':float(split['at_seconds']) if side=='before' else cue['end'],
                    'text':text,'screenshot_id':row['id'],'required_labels':list(refs),'spoken_references':refs,'raw_cues':[number]})
        else:
            out={k:cue[k] for k in ['start','end','text','screenshot_id','required_labels','spoken_references']}
            out['raw_cues']=[number];expanded.append(out)
    assert len(expanded)==132 and words(' '.join(c['text'] for c in expanded))==all_words
    for index,cue in enumerate(expanded,1): cue.update(cue=index,instructional=bool(cue['required_labels']))
    scenes=[];raw_position=0
    for index,(scene,frozen_scene) in enumerate(zip(lesson['scenes'],sequence['scenes'])):
        assert scene['id']==frozen_scene['scene_id'] and words(scene['narration'])==words(frozen_scene['narration'])
        count=len(words(scene['narration']));start=raw_position;cursor=0
        while raw_position<len(raw) and cursor<count:cursor+=len(words(raw[raw_position]['text']));raw_position+=1
        assert cursor==count
        entries=[c for c in expanded if start+1<=c['raw_cues'][0]<=raw_position]
        allowed=[s['capture_id'] for s in frozen_scene['screens']]
        selected=list(dict.fromkeys(c['screenshot_id'] for c in entries))
        assert selected==allowed,(scene['id'],selected,allowed)
        union={label for r in rows.values() if r['id'] in selected for label in r['visible_labels']}
        assert set(scene['required_labels'])<=union,(scene['id'],set(scene['required_labels'])-union)
        assert any(c['instructional'] for c in entries),'Operational scene requires actual spoken field correspondence.'
        begin=0.0 if index==0 else entries[0]['start']
        end=qa['audio']['duration_seconds'] if index==14 else raw[raw_position]['start']
        spans=[];active=entries[0]['screenshot_id'];opening=begin
        for c in entries:
            if c['screenshot_id']!=active:
                spans.append({'capture_ref':active,'actual_start':opening,'actual_end':c['start']});active=c['screenshot_id'];opening=c['start']
        spans.append({'capture_ref':active,'actual_start':opening,'actual_end':end})
        scenes.append({'scene_id':scene['id'],'first_raw_cue':start+1,'last_raw_cue':raw_position,
                       'derived_cues':[c['cue'] for c in entries],'required_labels':scene['required_labels'],
                       'source_spans':spans,'source_limits':scene['source_limits']})
    assert raw_position==123
    blocks=[];readability=[]
    for c in expanded:
        lines=textwrap.wrap(c['text'],width=42,break_on_hyphens=False,break_long_words=False)
        if len(lines)>2:lines=textwrap.wrap(c['text'],width=48,break_on_hyphens=False,break_long_words=False)
        assert len(lines)<=2,'Read actual text; do not invent a caption split.'
        duration=c['end']-c['start'];cps=len(c['text'])/duration
        assert duration>=1.0 and cps<=22.0,(c['cue'],duration,cps)
        readability.append({'cue':c['cue'],'raw_cues':c['raw_cues'],'duration_seconds':round(duration,3),'characters_per_second':round(cps,3),'lines':len(lines)})
        blocks.append(f"{c['cue']}\n{helper.stamp(c['start'])} --> {helper.stamp(c['end'])}\n"+'\n'.join(lines))
    out={'schema_version':1,'lesson_id':NAME,'status':'PROPOSED actual-audio source/caption plan for parent timing review; no final assembly or render',
         'source_frozen_sha256':FROZEN,'renderer_normalized_words':1050,'space_delimited_source_words':1041,
         'original_raw_cues':123,'proposed_derived_cues':132,'reviewed_actual_sources':31,
         'screen_intervals':sum(len(s['source_spans']) for s in scenes),'actual_audio_seconds':qa['audio']['duration_seconds'],
         'genuine_service_anchor_cuts':operations,'coalescence':None,'scenes':scenes,
         'raw_cue_correspondence':source_map,'cue_correspondence':expanded,'readability':readability,
         'timing_method':'Original service cue boundaries plus nine exact exported whole-second word markers27/80/149/192/229/237/247/312/317 only. Whole-second markers are not millisecond word timing. Actual images hold through original cue gaps until the next observed boundary, without speech-time interpolation.',
         'listening_approved':True,'listening_review_file':LISTENING.as_posix(),'listening_review_sha256':PINS[LISTENING],
         'parent_timing_review_pending':True,'renderer_plan_created':False,'video_rendered':False,'publication_approved':False,
         'explicit_timing_choices':[
             'Raw72 is split at genuine247 between New and Unit so the actual New Unit launcher precedes its Name field; no finer inferred boundary is used.',
             'Unit-read returns from the open Station dropdown028 to the already reviewed saved Units list026 at real raw97 start325.199 for the Available statement; first appearances retain the frozen source order.',
             'Raw56 begins over the preceding actual type link015, then switches at192 to the catalog016 containing New Unit Type. No Unit Types heading is claimed on015.',
             'Raw29 describes the form’s location options over its visible address/Gps fields008; the what3words field is explicitly pictured in the following coordinates scene009/010, where its blank state is discussed.'],
         'coverage_limits':[
             '005 clipped catalog row,024 transient modal backdrop and031 stale unsuccessful Casey search stay excluded; all34 raw pairs remain immutable.',
             'Closed Type/Station values truncate on unit forms; use the full saved type catalog and open Station dropdown028 for exact identity.',
             'Template cards are preview only; no Use these roles application or template qualification claim.',
             'Staffing picker030 is an ordinary people list, not proof of eligibility; no member selection or department staffing Save occurred.',
             'Available is a display readback, not a new stored status event, crew-readiness proof, map position or timestamp attestation.',
             'Typed station coordinates are illustrative references, not a device position or physical arrival. No provider delivery, printing configuration or administrator assignment demonstrated.',
             'Source34-original review was performed during curation; timing-specific cut images are separately re-inspected. No encoded frames or browser playback are claimed by this proposal.']}
    return out,'\n\n'.join(blocks)+'\n',qa

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write-proposed',action='store_true');p.add_argument('--ffmpeg',type=Path);a=p.parse_args()
    proposed,text,original=prepare()
    if a.write_proposed:
        assert a.ffmpeg and a.ffmpeg.is_file() and not DIRECTORY.exists(),'Use actual FFmpeg and a NEW output directory.'
        DIRECTORY.mkdir(parents=True)
        derived=DIRECTORY/(NAME+'.derived132.srt');corrected=DIRECTORY/(NAME+'.derived132.corrected.srt');report=DIRECTORY/(NAME+'.derived132.actual.qa.json')
        derived.write_text(text)
        sys.path.insert(0,str(SOURCES/'production'))
        from qa_narration import audit
        result=audit(SOURCES/BASE/(NAME+'.narrated-source.json'),SOURCES/AUDIO,derived,corrected,report,str(a.ffmpeg),FROZEN)
        assert result['passed'] and not result['alignment']['text_changes'] and result['silent_raw_cues']==result['silent_corrected_cues']==0
        assert result['audio']['decoded_samples']==original['audio']['decoded_samples'] and result['audio']['duration_seconds']==original['audio']['duration_seconds']
        from render_walkthrough import load_cues
        assert len(load_cues(corrected))==132
        result['derived_caption_provenance']={'original_service_raw_cues':123,'original_service_raw_file':RAW.as_posix(),'original_service_raw_sha256':PINS[RAW],
            'original_actual_qa_sha256':PINS[ORIGINAL_QA],'raw_captions_field_denotes':'Separate proposed derived132input, not the original123service export.',
            'whole_second_cuts':proposed['genuine_service_anchor_cuts'],'coalescence':None,'all_originals_preserved':True,
            'human_listening_review_file':LISTENING.as_posix(),'human_listening_review_sha256':PINS[LISTENING]}
        report.write_bytes(encoded(result))
        proposed['derived_audio_qa']={'file':str(report.relative_to(SOURCES)),'sha256':sha(report),'passed':True,'silent_cues':0,'minimum_cue_rms':result['minimum_raw_cue_rms']}
        proposed['derived_captions']={'file':str(corrected.relative_to(SOURCES)),'sha256':sha(corrected)}
        mapping=DIRECTORY/'correspondence.proposed.json';mapping.write_bytes(encoded(proposed))
        compact=DIRECTORY/'cue-screen-correspondence.txt'
        compact.write_text('\n'.join(f"{c['cue']:03} raw{c['raw_cues'][0]:03} {c['start']:.3f}–{c['end']:.3f} {c['screenshot_id']} | {c['text']}" for c in proposed['cue_correspondence'])+'\n')
        provenance={'schema_version':1,'kind':'source_only_groups_units_actual_audio_proposed132_derivation','created_at':datetime.now(timezone.utc).isoformat(),
            'source_frozen_sha256':FROZEN,'inputs':[{'file':p.as_posix(),'sha256':h} for p,h in PINS.items()],
            'recipe':{'file':str(Path(__file__).relative_to(SOURCES)),'sha256':sha(__file__)},
            'utility':{'file':str(UTILITY.relative_to(SOURCES)),'sha256':UTILITY_SHA},
            'outputs':[{'file':str(p.relative_to(SOURCES)),'sha256':sha(p)} for p in [derived,corrected,report,mapping,compact]],
            'complete_audio_decode':True,'derived_cues':132,'silent_cues':0,'speech_energy_is_not_listening_review':True,
            'listening_approved':True,'parent_timing_review_pending':True,'renderer_plan_created':False,'video_rendered':False,'canonical_or_ready_changed':False}
        (DIRECTORY/'provenance.json').write_bytes(encoded(provenance))
    print(json.dumps({'source_preflight':True,'scenes':15,'raw_cues':123,'proposed_cues':132,'sources':31,
        'intervals':proposed['screen_intervals'],'minimum_caption_seconds':min(r['duration_seconds'] for r in proposed['readability']),
        'maximum_caption_cps':max(r['characters_per_second'] for r in proposed['readability']),
        'files_written':a.write_proposed,'listening_approved':True,'timing_review_pending':True,'rendered':False,'canonical_ready':False}))

if __name__=='__main__':main()
