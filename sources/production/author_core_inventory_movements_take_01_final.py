"""Author Inventory take01 only from exact approved audio/QA/listening inputs.

The peer's source scaffold remains immutable. No caption word/time is changed:
all16 source cuts are genuine boundaries in the original93-cue export. This
recipe creates a NEW renderer plan; it cannot publish or mark a lesson ready.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
SOURCES=ROOT/'sources'
NAME='core-inventory-movements'
PEER=SOURCES/'production/author_core_inventory_movements_take_01.py'
PEER_SHA='8c4be2d2116d033857b8f9f0d263d22fbc8122659429f75073bb2d7cc1b036c0'
sys.path.insert(0,str(ROOT/'scripts'))
from render_walkthrough import load_cues,validate_inputs,words
from verify_capture_evidence import _Validator,_normalized,instruction_scene_digest

REFERENCES={
1:{'Inventory':'Inventory'},3:{'On hand':'On hand','Items':'Items','Location':'Location','Unit':'Unit','Person':'Person'},
9:{'Items':'Items','Tracking mode':'Tracking mode','Status':'Status'},10:{'New item':'New item'},
11:{'How it is tracked':'How it is tracked','By quantity':'By quantity','Track lots':'Track lots'},12:{'Expiration required':'Expiration required'},
13:{'Controlled substance':'Controlled substance','Kit item':'Kit item'},18:{'Review':'Review'},
19:{'packs':'packs','Code':'code','Description':'description'},20:{'Minimum stock':'minimum stock','Reorder point':'reorder point','Unit cost':'unit cost'},21:{'Save':'Save'},
25:{'Lots':'Lots'},26:{'ACADEMY-LOT-A':'ACADEMY lot A','Academy training batteries':'Academy training batteries'},27:{'Expires':'expiry'},28:{'New lot':'New lot'},
33:{'Adjust stock':'Adjust stock','Review':'Review','Receive':'Receive'},34:{'Station':'Station','Amount':'Amount'},36:{'Record movement':'Record movement'},
38:{'On hand':'On hand','Station':'Station','20.000000':'twenty packs'},
41:{'New transfer':'New transfer','Station':'Station','Source location':'Source location','Unit':'Unit'},42:{'Destination location':'Destination location','Amount':'Amount'},43:{'Record movement':'Record movement'},
45:{'Transfers':'Transfers','Station':'Station-to-Unit','Unit':'Station-to-Unit'},
48:{'History':'History','Receive':'Receive','Transfer':'Transfer','20.000000':'twenty','5.000000':'five'},50:{'Station':'Station','Unit':'Unit'},
52:{'Items':'item','Location':'location','Filter':'filters'},53:{'Attest as witness':'Attest as witness','Rebuild stock balances':'Rebuild stock balances'},
55:{'Issue equipment':'Issue equipment','Station':'Station','Matthew Casey':'Matthew'},56:{'Matthew Casey':'Casey','Expected return date':'expected return date'},57:{'Issue':'Issue'},
58:{'Issuances':'Issuances','Personnel':'Personnel','Outstanding':'outstanding','Return':'Return'},
62:{'Issuances':'Issuances','Partially returned':'Partially returned'},63:{'Outstanding':'outstanding','1.000000':'one pack'},65:{'Return':'Return','Outstanding':'outstanding'},
70:{'Station':'Station','14.000000':'fourteen packs'},71:{'Unit':'Unit','5.000000':'five','Personnel':'Personnel','1.000000':'one'},
76:{'Counts, alerts and reports':'Counts, alerts and reports','Inventory alerts':'Inventory alerts'},77:{'Low stock':'Low stock'},78:{'Resolved':'Resolved','All locations':'All locations'},81:{'Refresh alerts':'Refresh alerts'},
84:{'Inventory reports':'Inventory reports','Choose a report':'Choose a report','Inventory on hand':'Inventory on hand'},85:{'Continue':'Continue','Narrow it down':'Narrow it down'},
}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
def asset(ref):
    assert isinstance(ref,dict) and re.fullmatch('[0-9a-f]{64}',ref.get('sha256','')),'Require exact asset hash.'
    rel=Path(ref['file']);path=(SOURCES/rel).resolve()
    assert not rel.is_absolute() and SOURCES in path.parents and path.is_file(),'Asset must remain within public sources.'
    assert sha(path)==ref['sha256'],'Changed reviewed asset: '+str(rel)
    return path

def build(input_path,input_sha):
    assert sha(PEER)==PEER_SHA,'Preserve the retained peer scaffold.'
    assert re.fullmatch('[0-9a-f]{64}',input_sha or '') and sha(input_path)==input_sha,'Supply exact approved-input hash.'
    supplied=json.loads(Path(input_path).read_text());assert supplied['lesson_id']==NAME
    spec=importlib.util.spec_from_file_location('inventory_source_scaffold_v1',PEER);peer=importlib.util.module_from_spec(spec);spec.loader.exec_module(peer)
    source=peer.prepare();assert supplied['lesson_sha256']==source['frozen_lesson_sha256']
    paths={key:asset(supplied[key]) for key in ['audio','captions','qa','listening_review']}
    qa=json.loads(paths['qa'].read_text());heard=json.loads(paths['listening_review'].read_text())
    assert qa['passed'] is True and not qa['issues'] and not qa['possible_speech_gaps']
    assert qa['lesson']['sha256']==source['frozen_lesson_sha256'] and qa['lesson']['scenes']==12
    assert qa['audio']['sha256']==supplied['audio']['sha256'] and qa['audio']['full_decode']=='passed'
    assert qa['raw_captions']['sha256']==peer.PINS['expansion/audio/'+NAME+'-generated-20261028.raw.srt']
    assert qa['corrected_captions']['sha256']==supplied['captions']['sha256']
    assert qa['raw_captions']['cues']==qa['corrected_captions']['cues']==93
    assert qa['silent_raw_cues']==qa['silent_corrected_cues']==0
    assert heard['complete_natural_narration'] is True and heard['audio_sha256']==supplied['audio']['sha256'] and heard['lesson_sha256']==source['frozen_lesson_sha256']
    assert heard['reviewer'] and heard['evidence'] and datetime.fromisoformat(heard['reviewed_at'].replace('Z','+00:00'))<=datetime.now(timezone.utc)
    lesson_path=SOURCES/peer.FREEZE/(NAME+'.narrated-source.json');lesson=json.loads(lesson_path.read_text())
    captures=json.loads((SOURCES/peer.FREEZE/'captures.reviewed.json').read_text());shots={s['id']:s for s in captures['screenshots']}
    cues=load_cues(paths['captions']);raw=load_cues(SOURCES/'expansion/audio'/ (NAME+'-generated-20261028.raw.srt'))
    assert len(cues)==93 and words(' '.join(c['text'] for c in cues))==words(' '.join(s['narration'] for s in lesson['scenes']))
    for a,b in zip(cues,raw):assert (a['start'],a['end'],words(a['text']))==(b['start'],b['end'],words(b['text']))
    duration=qa['audio']['duration_seconds'];assert isinstance(duration,(int,float)) and duration>=cues[-1]['end']
    correspondence={}
    for span in source['source_spans']:
        for number in range(span['first_actual_cue'],span['last_actual_cue']+1):correspondence[number]=span['capture_ref']
    assert len(correspondence)==93
    expanded=[]
    for number,cue in enumerate(cues,1):
        shot=shots[correspondence[number]];refs=REFERENCES.get(number,{})
        assert set(refs)<=set(shot['visible_labels']),(number,set(refs)-set(shot['visible_labels']))
        check=_Validator(SOURCES);check.spoken_references(dict(cue,spoken_references=refs),{_normalized(x) for x in refs},str(number),True);assert not check.issues,check.issues
        expanded.append(dict(cue,cue=number,screenshot_id=shot['id'],required_labels=list(refs),spoken_references=refs,instructional=bool(refs)))
    now=datetime.now(timezone.utc).isoformat();planned=[];reviewed_spans=[]
    for index,scene in enumerate(lesson['scenes']):
        spans=[span for span in source['source_spans'] if span['scene_id']==scene['id']];assert spans
        first,last=spans[0]['first_actual_cue'],spans[-1]['last_actual_cue']
        start=0 if index==0 else cues[first-1]['start']
        end=duration if index==len(lesson['scenes'])-1 else cues[last]['start']
        screens=[]
        for offset,span in enumerate(spans):
            opening=start if offset==0 else cues[span['first_actual_cue']-1]['start']
            closing=end if offset==len(spans)-1 else cues[spans[offset+1]['first_actual_cue']-1]['start']
            screens.append({'screenshot_id':span['capture_ref'],'start':opening,'end':closing})
            reviewed_spans.append(dict(span,final_screen_start=opening,final_screen_hold_end=closing))
        entries=expanded[first-1:last]
        full={'id':scene['id'],'title':scene['title'],'kind':'operational','start':start,'end':end,'visual_required_labels':scene['required_labels'],'screens':screens,'captions':entries}
        review={'passed':True,'reviewer':'Codex independent actual source/control/cue correspondence inspection','reviewed_at':now,
            'mapping_sha256':instruction_scene_digest(full,shots),'correspondence_reviewed':True,'no_unseen_controls':True,
            'method':'All16 original1434x773JPEGs personally inspected. All93 exact frozen speech cues match pictured foreground controls/results in causal order.16 source cuts use unchanged genuine raw SRT boundaries; no word splits or interpolation. Missing return dialog, later usage and report outputs are explicitly excluded.'}
        planned.append({'id':scene['id'],'start':start,'end':end,'screens':screens,'captions':[{k:entry[k] for k in ['cue','screenshot_id','required_labels','spoken_references','instructional']} for entry in entries],'instruction_review':review})
    plan={'schema_version':1,'lesson_id':NAME,'duration_seconds':duration,'instruction_mapping':'reviewed_scene_coverage','display_context':'TRAINING ONLY · fictional department',
        'narration':dict(supplied['audio'],kind='approved_natural_narration',approval={'reviewer':heard['reviewer'],'reviewed_at':heard['reviewed_at'],'sha256':supplied['audio']['sha256'],'complete_natural_narration':True,'evidence':heard['evidence'],'qa_file':supplied['qa']['file'],'qa_sha256':supplied['qa']['sha256'],'listening_review_file':supplied['listening_review']['file'],'listening_review_sha256':supplied['listening_review']['sha256']}),
        'captions':dict(supplied['captions'],kind='speech_timed_srt',approval={'reviewer':'Codex exact frozen words/actual93cue correspondence','reviewed_at':now,'sha256':supplied['captions']['sha256'],'audio_sha256':supplied['audio']['sha256'],'speech_timing_reviewed':True,'method':'Original93 actual raw/corrected cue boundaries and words unchanged. All16 source transitions are existing cue starts; no guessed time or derived split.'}),
        'capture_manifests':[{'file':str(peer.FREEZE/'captures.reviewed.json'),'sha256':peer.PINS[str(peer.FREEZE/'captures.reviewed.json')]}],
        'screenshot_reviews':{key:{'reviewer':'Codex independent original-size Inventory source inspection','reviewed_at':now,'sha256':shot['sha256'],'application_visible':True,'labels_legible':True,'no_errors':True} for key,shot in shots.items()},
        'scenes':planned,'publishable':False,'approved_input_sha256':input_sha,'source_scaffold_helper_sha256':PEER_SHA,
        'limitations':source['scope_limits']+['Actual user full listening approval is retained; encoded-frame/native-playback review remains required after rendering.']}
    return lesson_path,plan,{'kind':'inventory_actual93cue_final_source_correspondence','approved_input_sha256':input_sha,'source_frozen_sha256':source['frozen_lesson_sha256'],'source_spans':reviewed_spans,'captions':expanded,'scenes':12,'source_spans_count':16,'actual_cues':93,'timing_precision':source['timing_precision'],'publication_approved':False}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--approved-inputs',type=Path,required=True);p.add_argument('--approved-inputs-sha256',required=True);p.add_argument('--output',type=Path)
    args=p.parse_args();lesson,plan,correspondence=build(args.approved_inputs,args.approved_inputs_sha256)
    if args.output:
        path=args.output.resolve();assert SOURCES/'expansion/plans' in path.parents and not path.exists(),'Use a NEW staged renderer plan path.'
        mapping=path.with_name('correspondence.reviewed.json');assert not mapping.exists()
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(encoded(plan));mapping.write_bytes(encoded(correspondence))
        recipe=validate_inputs(lesson,path,SOURCES)
        print(json.dumps({'passed':True,'scenes':len(recipe['scenes']),'cues':len(recipe['cues']),'duration':recipe['duration'],'screens':sum(len(scene['screens']) for scene in recipe['scenes']),'rendered':False,'publication_approved':False}))
    else:print(json.dumps({'passed_preflight':True,'scenes':12,'cues':93,'screens':16,'rendered':False,'publication_approved':False}))

if __name__=='__main__':main()
