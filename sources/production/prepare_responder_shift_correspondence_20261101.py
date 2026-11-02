"""Prepare the complete actual92-cue Responder shift correspondence for review.

Default is read-only. --prepare writes a NEW proposal directory, never approvals,
renderer inputs, media, canonical lessons, site files, target files or Git state.
One original cue is split at a genuine stored Descript word timestamp; speech and
all original endpoints remain unchanged. Actual review and hearing are separate.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
NAME = 'app-responder-shift-schedules-rosters'
BASE = Path('expansion/plans') / (NAME + '-source-proposal-20261031')
OUT = Path('expansion/plans') / (NAME + '-proposed92-correspondence-20261101')
LESSON = BASE / 'lesson.candidate.json'
MANIFEST = BASE / 'captures.reviewed.json'
EXTRA = BASE / 'additional-literal-observations-20261101.json'
AUDIO = Path('expansion/audio') / (NAME + '.m4a')
CAPTIONS = Path('expansion/audio') / (NAME + '.word-aligned-92.corrected.srt')
QA = Path('expansion/audio') / (NAME + '.word-aligned-92.qa.json')
HEARING = Path('expansion/audio') / (NAME + '.listening-review.json')
PINS = {
    LESSON: '43306580f2123226fd171b3c5dd9c3fb5e66a3aa53dfe040e86c58d4fa3d51fa',
    MANIFEST: 'f6f668f8faff69cf4345823e99dd5d990f3067b71ad4e1c0650778f5e341d9d9',
    EXTRA: '4ed577ce0714055bd82fb5eb1a18d576d582559c3329d977659a515311ac62fa',
    AUDIO: '1af3e2355d89d67cb3d73ccec3c5a371124e1306550cff9493731739a7b8f2ee',
    CAPTIONS: 'af702692c4283a3c5c7ceb82e8bf76b30a98ad87818eb91c52732a018376d5f6',
    QA: '00d40e20d7d9f094fda8f9fbedd2ea7bf11ecc10dad043ca1b332d8e78c42c07',
    HEARING: 'e19c2734d005aafe4447839e656a0d75ec888b73ed87db416ab6f4401484e02f',
    Path('expansion/audio') / (NAME + '.word-boundary-provenance.json'): '993394a204412b47ab95bc7a62462b9111a66f9cc78e59279f155a5e8589df5f',
}
# Scene, first/last actual cue, actual source capture prefix. The empty search
# field and Roster heading remain visible until their corresponding speech ends.
SPANS = [('01',1,1,'019-'),('01',2,9,'017-'),
         ('02',10,10,'017-'),('02',11,18,'018-'),
         ('03',19,28,'003-'),('04',29,29,'003-'),('04',30,37,'004-'),
         ('05',38,40,'007-'),('05',41,45,'009-'),
         ('06',46,49,'010-'),('06',50,51,'011-'),('06',52,55,'012-'),
         ('07',56,64,'013-'),('08',65,73,'014-'),
         ('09',74,76,'016-'),('09',77,83,'015-'),('10',84,92,'018-')]
# Explicit literal labels -> exact phrases in each actual speech cue. Unlisted
# cues explain the visible state or scope; they do not introduce hidden actions.
REFERENCES = {
 1:{'Shifts':'Shifts','Today':'Today'},
 2:{'My Shifts':'My Shifts','Calendar':'Calendar','Trades':'Trades','On Duty':'On Duty','Approvals':'Approvals'},
 4:{'A Shift — Firehouse 51':'A Shift at Firehouse 51'},
 6:{'next day':'next day'},7:{'Assigned':'Assigned'},8:{'You are on':'You are on'},
 10:{'Search shifts...':'Search shifts'},
 11:{'Community':'Community','Community standby signup':'Community standby signup'},
 13:{'Sign-up':'Sign-up','Approval required':'Approval required'},14:{'You are on':'You are on'},
 19:{'Community standby signup':'standby card'},
 22:{'Sign-ups and trades on this shift need supervisor approval.':'sign-ups and trades'},
 23:{'Sign-ups and trades on this shift need supervisor approval.':'supervisor approval'},
 25:{'Open needs':'Open needs','Firehouse 51':'Firehouse 51','Filled':'Filled','No role requirements':'No role requirements'},
 27:{'Request trade':'Request trade','Add person':'Add person'},29:{'Roster':'Roster'},
 31:{'Wallace Boden':'Wallace Boden','Command':'Command','Chief':'Chief','Engine 51':'Engine','Squad 3':'Squad'},
 33:{'Scheduled':'Scheduled'},38:{'My Shifts':'My Shifts'},
 39:{'Shifts I am on':'Shifts I am on','A Shift — Firehouse 51':'A Shift'},40:{'Assigned':'Assigned'},
 41:{'Community standby signup':'standby summary'},
 42:{'Manual':'Manual','Sign-up':'Sign-up','Approval required':'Approval required'},43:{'Upcoming days':'Upcoming days'},
 46:{'Calendar':'Calendar'},47:{'October 2026':'month heading'},48:{'All Shifts':'All Shifts'},
 49:{'TRAINING — Academy signup practice':'Training, Academy signup practice'},50:{'27':'twenty-seventh'},
 51:{'My shifts':'My shifts','Open slots':'Open slots','Fully staffed':'Fully staffed'},
 52:{'Tuesday, October 27, 2026':'selected date'},
 53:{'1:00 PM':'one','3:00 PM':'three','Open slots: 2':'two open slots'},
 56:{'TRAINING — Academy signup practice':'practice day'},
 57:{'Open needs':'Open needs','Firehouse 51':'Firehouse 51','Open: 2':'Open, two','Chief':'Chief'},
 58:{'Needed: 2':'Needed, two'},59:{'Roster':'Roster','No one is on this day yet.':'No one is on this day yet.'},
 62:{'Add person':'Add person'},65:{'On Duty':'On Duty'},
 66:{'A Shift — Firehouse 51':'A Shift','On duty: 10':'ten on-duty entries'},
 67:{'Until':'Until'},68:{'Scheduled':'Scheduled'},72:{'Scheduled':'Scheduled'},
 74:{'Trades':'Trades'},75:{'No shift trades':'No shift trades'},77:{'Approvals':'Approvals'},
 78:{'Nothing to approve':'Nothing to approve'},
 84:{'Community standby signup':'intended day'},85:{'Approval required':'approval requirement'},
}

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text())
def need(ok, message):
    if not ok: raise ValueError(message)
def put(path, value):
    with path.open('x') as f: f.write(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

def prepare(write=False):
    for relative, digest in PINS.items():
        need(sha(S/relative)==digest, 'Changed frozen input: '+str(relative))
    sys.path.insert(0,str(ROOT/'scripts'))
    from render_walkthrough import load_cues, words
    from verify_capture_evidence import _Validator, _normalized, instruction_scene_digest
    from expansion_site import lesson_content_digest
    lesson=read(S/LESSON); manifest=deepcopy(read(S/MANIFEST)); extra=read(S/EXTRA)
    rows={x['id']:x for x in manifest['screenshots']}
    for item in extra['observations']:
        row=rows[item['capture_id']]
        need(row['sha256']==item['source_sha256'],'Additional observation uses changed pixels')
        row['visible_labels']=list(dict.fromkeys([*row['visible_labels'],*item['labels']]))
        row['additional_literal_review']={'file':str(EXTRA),'sha256':PINS[EXTRA]}
    observed={}
    for id,row in rows.items():
        need(sha(S/row['file'])==row['sha256'] and sha(S/row['dom_file'])==row['dom_sha256'],'Changed source image/DOM')
        v=_Validator(S); observed[id]=v.observations(row,id);need(not v.issues,json.dumps(v.issues))
    cues=load_cues(S/CAPTIONS);qa=read(S/QA);hearing=read(S/HEARING)
    need(len(cues)==92 and qa['passed'] and qa['issues']==[] and qa['silent_corrected_cues']==0,'Incomplete actual cue QA')
    need(qa['audio']['sha256']==PINS[AUDIO] and qa['corrected_captions']['sha256']==PINS[CAPTIONS],'Different measured media')
    need(hearing['reviewer']=='User' and hearing['complete_natural_narration'] and hearing['audio_sha256']==PINS[AUDIO],'Genuine complete hearing absent')
    need(cues[48]['end']==cues[49]['start']==165.29,'Stored genuine word cut changed')
    duration=qa['audio']['duration_seconds']; entries=[]; holds=[]
    need([n for _,a,b,_ in SPANS for n in range(a,b+1)]==list(range(1,93)),'Incomplete cue ranges')
    for i,(scene,first,last,prefix) in enumerate(SPANS):
        matches=[id for id in rows if id.startswith(prefix)];need(len(matches)==1,'Ambiguous actual source')
        id=matches[0];begin=0.0 if i==0 else cues[first-1]['start'];end=cues[SPANS[i+1][1]-1]['start'] if i+1<len(SPANS) else duration
        holds.append({'scene_id':scene,'screenshot_id':id,'start':begin,'end':end,'first_cue':first,'last_cue':last})
        for n in range(first,last+1):
            cue=cues[n-1];refs=REFERENCES.get(n,{})
            need(cue['start']>=begin and cue['end']<=end,'Actual cue crosses its real source hold')
            need({_normalized(x) for x in refs}<=observed[id],'Reference names an unseen label')
            mapped=dict(cue,cue=n,screenshot_id=id,required_labels=list(refs),spoken_references=refs,instructional=bool(refs),scene_id=scene)
            v=_Validator(S);v.spoken_references(mapped,{_normalized(x) for x in refs},'cue'+str(n),True);need(not v.issues,json.dumps(v.issues))
            entries.append(mapped)
    scenes=[]
    for authored in lesson['scenes']:
        selected=[x for x in holds if x['scene_id']==authored['id']];captions=[{k:v for k,v in c.items() if k!='scene_id'} for c in entries if c['scene_id']==authored['id']]
        need(words(' '.join(c['text'] for c in captions))==words(authored['narration']),'Speech changed in scene '+authored['id'])
        union=set().union(*(observed[h['screenshot_id']] for h in selected));need({_normalized(x) for x in authored['required_labels']}<=union,'Authored label unseen in scene '+authored['id'])
        scene={'id':authored['id'],'title':authored['title'],'kind':'operational','start':selected[0]['start'],'end':selected[-1]['end'],'visual_required_labels':authored['required_labels'],'screens':[{k:h[k] for k in ['screenshot_id','start','end']} for h in selected],'captions':captions}
        scene['proposed_mapping_sha256']=instruction_scene_digest(scene,rows);scenes.append(scene)
    learner=deepcopy(lesson)
    learner['scope_limits']=[x for x in learner['scope_limits'] if 'separate prepared' not in x.lower() and 'Source candidate only' not in x]
    learner['scope_limits'].append('The separate approved future-day trade-and-cancellation exercise is retained independently; this walkthrough inspects recorded schedules and queues.')
    need(lesson_content_digest(lesson)==lesson_content_digest(learner),'Learner words/metadata changed')
    data={'created_at':datetime.now(timezone.utc).isoformat(),'lesson_file':str(LESSON),'lesson_sha256':PINS[LESSON],'audio_file':str(AUDIO),'audio_sha256':PINS[AUDIO],'qa_file':str(QA),'qa_sha256':PINS[QA],'captions_file':str(CAPTIONS),'captions_sha256':PINS[CAPTIONS],'duration_seconds':duration,'scenes':scenes,'holds':holds,'cues':entries,'learner_content_sha256':lesson_content_digest(learner),'cue_count':92,'source_images':14,'holds_count':17,'review_state':'proposal_only_no_approval_inferred'}
    if write:
        destination=S/OUT;need(not destination.exists(),'Preserve existing proposal');destination.mkdir()
        put(destination/'captures.source-relative.json',manifest);put(destination/'correspondence.proposed.json',data);put(destination/'lesson.learner-projection.proposed.json',learner)
        compact='\n\n'.join(f"Cue{c['cue']:03} · scene{c['scene_id']} · {c['start']:.3f}–{c['end']:.3f} · {c['screenshot_id']}\n{c['text']}\nLiteral -> exact speech: {json.dumps(c['spoken_references'],ensure_ascii=False)}" for c in entries)+'\n'
        (destination/'cue-screen-correspondence.txt').open('x').write(compact)
    return {'passed':True,'read_only':not write,'actual_cues':92,'scenes':10,'source_images':14,'holds':17,'full_audio_seconds':duration,'instruction_review':'not inferred','canonical_or_site_changed':False}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepare',action='store_true');args=parser.parse_args()
    print(json.dumps(prepare(args.prepare),indent=2))
