"""Guarded Billing/Shifts take02 final-input authoring; default read-only.

--assemble writes one NEW final-input package only after an operator supplies
an exact genuine, URL-free User listening-receipt SHA256. This code does not
render, publish, adopt lessons, build a site, operate apps or perform Git work.
"""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
S=ROOT/'sources'
HELPER=Path('production/prepare_core_billing_shifts_take_02_20261030.py')
HELPER_SHA='35ee2481bf1ce17e8276a8eb346c7fec270e700dc096127c73fe5fffd82274b9'
PARENT=Path('expansion/plans/root-billing-shifts-timing-review-20261030.json')
PARENT_SHA='c373d1a5d150205076837d03258572591e0227470e9814b27752313b5c4a75b5'
PINNED_CODE={'scripts/render_walkthrough.py': '89f19e92b3005c0e0be9fb5b1babc4e5d780f1529d31ca278eb14c3ca1abc881', 'scripts/verify_capture_evidence.py': '40f41d12497d273feb950d5db1a04a6880466b229ee2d6756a929f87f70c04fa'}
CONFIG={'billing': {'proposal': 'expansion/plans/core-customer-billing-review-take-02-proposed-20261030', 'pins': {'correspondence.proposed.json': '3b91251550e0813cc332576ea72bef2a8891422037398cda53d28bcb72917925', 'captions.proposed.srt': 'c95cd0b871fc016a719330b12685fbe7ce4ef4b9c011e584dc1be6d66b851186', 'captions.proposed.checked.srt': '32a7381e3817f62223dfe702a2b4fde3147cb3671dc18786935dd10cc0e29d2e', 'derived-captions.actual.qa.json': 'eb24f6e0d2bf75cbe2656078b76fef01e3fb58d210f75786123926065a93a6fc', 'actual-derived-QA-followup.json': '3dabb18a81d1bd1801b10baf916e62291158c4cd60ce148de87e6255ba2a8437', 'caption-derivation.json': '0f785272731e1aa1d455f7e2bc82ed5473e11e8acce1ee7199a49741cbfaec41', 'ordered-screens.compact.txt': 'b5ca8d092f832a0a4da61b9fcf421c5d0306a69dd0108230c593106a531690e4', 'cue-screen.compact.txt': '3804817e76594f3f6b958aae40debfad91ef1634af5483ba2325bcea36cc7289', 'input-pins.json': '27f85bfc15ab9bb9b737f991322af843476c3fcf0e9aa71984f2404b1619b69c', 'readiness.proposed.json': 'd46307689ff9455a22bc56e0980265a6c980a6c6cefe90b87059ee977e56b1e6'}, 'holds': 19, 'images': 15, 'cues': 101, 'final': 'expansion/plans/core-customer-billing-review-take-02-final-inputs-20261030', 'listening': 'expansion/audio/core-customer-billing-review-take-02.listening-review.json'}, 'shifts': {'proposal': 'expansion/plans/core-shifts-administration-take-02-proposed-20261030', 'pins': {'correspondence.proposed.json': '32368cf459b495a12c441adcda8970404a46c5c6807cd27cf52ed716be49cbdf', 'captions.proposed.srt': '93ca1f08e1e692eb69030defaa32a7f785f073281ba50cd50d2b42120d791fbe', 'captions.proposed.checked.srt': 'c49aa118b02d31491f5199885ce87dbb34288c66833d983d2191b9d997ea7b9b', 'derived-captions.actual.qa.json': 'e6cbf52d483e5b4d9c7c4d474c368f70162edb148f890c86288f5598bf261886', 'actual-derived-QA-followup.json': '984c27ce9dc277c68fa24a1c697ac3e87207fc857b1b999e72ee589486a7e0c2', 'caption-derivation.json': 'e4a67ab029bf8872beb30d4d4d89bceeb1f9b04f51e135a6198d7c4912b7a606', 'ordered-screens.compact.txt': '6c1c43e88711c743f5d8890d1f4365a3a6a032337b52a3dac02a5dd171d81b87', 'cue-screen.compact.txt': '7e05bb4310571aea0ce288c17a91997a39cd557fb840844e3bb88c04f80cfb51', 'input-pins.json': '92d0a95c1d62b8d91ef367cd4e24e0845d94f4fbb13c415ceb65e6a177e5bff7', 'readiness.proposed.json': '932e238734f90e50aeb7624acaa2c38ef139ea84639a04d0c0c544ffbba3e4b5'}, 'holds': 29, 'images': 24, 'cues': 121, 'final': 'expansion/plans/core-shifts-administration-take-02-final-inputs-20261030', 'listening': 'expansion/audio/core-shifts-administration-take-02.listening-review.json'}}
# Exact natural references in the Root-accepted unchanged source/speech spans.
# The whole UI label still must exist in the actual mapped screenshot.
ALIASES={
 'billing':{
  'subscription':{'Subscription & Billing':['Subscription and Billing'],'Subscription Plan & Billing':['Subscription Plan and Billing']},
  'sector-examples':{'Accounts receivable aging':['outstanding-balance categories']},
 },
 'shifts':{},
}


def require(condition,message):
    if not condition:raise ValueError(message)


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb')as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
def norm(value):return ' '.join(value.split())


def retained_helper():
    require(__debug__,'Use ordinary Python; optimized execution disables retained assertions.')
    require(sha(S/HELPER)==HELPER_SHA,'Changed retained proposal author; obtain a new explicit review.')
    for name,digest in PINNED_CODE.items():require(sha(ROOT/name)==digest,'Changed pinned renderer/validator code; preserve this recipe and obtain a new review.')
    sp=importlib.util.spec_from_file_location('billing_shifts_retained_source_author',S/HELPER);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m


def verify_parent(parent,proposal,alias,cfg):
    require(parent.get('reviewer')=='Root'and parent.get('human_listening_claim')is False,'Parent timing review must not be substituted for User listening.')
    rows=[x for x in parent.get('lessons',[])if x.get('lesson_id')==proposal['lesson_id']]
    require(len(rows)==1,'Missing or duplicate actual parent lesson review.');row=rows[0]
    require(row.get('proposal_file')==str(Path(cfg['proposal'])/'correspondence.proposed.json')and row.get('proposal_sha256')==cfg['pins']['correspondence.proposed.json'],'Root reviewed a different proposal.')
    require(row.get('compact_cues_sha256')==cfg['pins']['cue-screen.compact.txt'],'Root reviewed a different cue/image correspondence.')
    require(row.get('source_spans')==cfg['holds']and row.get('accepted_genuine_service_cuts')==proposal['genuine_service_cuts']and row.get('accepted_adjacent_same_image_caption_merges')==proposal['adjacent_same_image_caption_merges'],'Root cut/merge acceptance differs.')
    require(isinstance(row.get('review'),str)and len(row['review'])>40,'Missing genuine parent correspondence account.')
    return row


def verify_audio_qa(qa,raw,checked,frozen_sha,audio_sha,raw_sha,checked_sha,expected):
    require(qa.get('passed')is True and qa.get('issues')==[]and qa.get('possible_speech_gaps')==[],'Actual audio QA has unresolved failures or gaps.')
    require(qa['lesson']['sha256']==frozen_sha,'Wrong frozen source in actual QA.')
    a=qa['audio'];require(a['sha256']==audio_sha and a['full_decode']=='passed','Wrong or undecoded actual audio.')
    duration=a['duration_seconds'];require(type(duration)in(int,float)and duration>raw[-1]['end'],'Audio duration does not close final speech.')
    require(abs(a['decoded_samples']/a['sample_rate']-duration)<1e-6,'Duration is not actual full decoded PCM.')
    require(qa['alignment']['match_ratio']==1.0 and qa['alignment']['text_changes']==[]and qa['alignment']['cues']==expected,'Wrong or changed actual transcript.')
    require(len(raw)==len(checked)==expected and qa['silent_raw_cues']==qa['silent_corrected_cues']==0,'Wrong count or silent cue.')
    require(qa['raw_captions']['sha256']==raw_sha and qa['corrected_captions']['sha256']==checked_sha and qa['corrected_captions']['exact_script']is True,'QA caption identity changed.')
    for key,cues in [('raw_captions',raw),('corrected_captions',checked)]:
        measured=qa[key]['energy'];require(len(measured)==expected,'Incomplete per-cue PCM measurements.')
        for i,(c,e)in enumerate(zip(cues,measured),1):
            require(e['cue']==i and e['samples']>0 and e['below_threshold']is False and e['rms']>=qa['signal_threshold_rms'],'Unmeasured or silent PCM cue.')
            require(abs(c['start']-e['start'])<1e-6 and abs(c['end']-e['end'])<1e-6,'PCM cue boundaries changed.')
    require(raw==checked,'Checked captions changed exact cue text or timing beyond line wrapping.')
    return duration


def caption_annotations(alias,proposal,manifest):
    """Pure source annotation: exact source literals and actual cue phrases."""
    rows={x['id']:x for x in manifest['screenshots']};result=[]
    for original in proposal['cue_correspondence']:
        c=deepcopy(original);row=rows[c['screenshot_id']];refs={}
        for literal in row['visible_labels']:
            if re.search(r'(?<!\w)'+re.escape(literal)+r'(?!\w)',c['text'],flags=re.I):refs[literal]=literal
        for literal,phrases in ALIASES.get(alias,{}).get(c['scene_id'],{}).items():
            if literal not in row['visible_labels']:continue
            for phrase in phrases:
                if norm(phrase).casefold()in norm(c['text']).casefold():refs[literal]=phrase;break
        for literal,phrase in refs.items():
            require(literal in row['visible_labels']and norm(phrase).casefold()in norm(c['text']).casefold(),'Unseen control or absent unchanged spoken reference.')
        c.update(required_labels=list(refs),spoken_references=refs,instructional=bool(refs));result.append(c)
    return result


def instruction_mappings(lesson,proposal,manifest,entries,reviewed_at):
    sys.path.insert(0,str(ROOT/'scripts'))
    from verify_capture_evidence import instruction_scene_digest,_Validator,_normalized
    rows={x['id']:x for x in manifest['screenshots']};out=[]
    for authored in lesson['scenes']:
        spans=[x for x in proposal['source_spans']if x['scene_id']==authored['id']];caps=[x for x in entries if x['scene_id']==authored['id']]
        require(norm(' '.join(x['text']for x in caps))==norm(authored['narration']),'Mapped scene words changed.')
        screens=[{'screenshot_id':x['capture_id'],'start':x['start']['seconds'],'end':x['end']['seconds']}for x in spans]
        require(all(s['end']>s['start']for s in screens),'Unresolved or nonpositive screen interval.')
        require(any(x['required_labels']for x in caps),'Operational scene lacks an actual speech-to-visible-control reference.')
        for c in caps:
            require(any(x['screenshot_id']==c['screenshot_id']and x['start']<=c['start']and x['end']>=c['end']for x in screens),'Actual caption crosses its mapped screen; do not adjust genuine timing.')
        full={'id':authored['id'],'title':authored['title'],'kind':'operational','start':screens[0]['start'],'end':screens[-1]['end'],'visual_required_labels':authored['required_labels'],'screens':screens,'captions':caps}
        review={'passed':True,'reviewer':'Root retained complete source/cue map; Codex literal-reference checks','reviewed_at':reviewed_at,'correspondence_reviewed':True,'no_unseen_controls':True,'mapping_sha256':instruction_scene_digest(full,rows),'parent_timing_review_file':PARENT.as_posix(),'parent_timing_review_sha256':PARENT_SHA,'method':'Frozen original image/DOM reviews, exact accepted screen/cue map and real caption/PCM identities are retained. Caption references use only exact source literals and actual unchanged speech phrases. Root accepted the complete map and explicit coarse-service cuts/merges. No new original-pixel, encoded-frame, browser-playback or human-listening review is claimed.'}
        full['instruction_review']=review
        # The evidence validator checks source annotations only; this is not
        # renderer execution, image decoding or construction of a final plan.
        v=_Validator(S)
        for c in caps:v.spoken_references(c,{_normalized(x)for x in c['required_labels']},'source caption',True)
        v.instruction_review(full,rows,{sid:{_normalized(x)for x in row['visible_labels']}for sid,row in rows.items()},'source scene',lesson['app'])
        require(not v.issues,'Source instruction mapping failed: '+json.dumps(v.issues))
        out.append(full)
    return out


def preflight(alias):
    require(alias in CONFIG,'Choose one retained lesson.');cfg=CONFIG[alias];m=retained_helper()
    require(sha(S/PARENT)==PARENT_SHA,'Changed actual Root timing receipt.')
    for name,digest in cfg['pins'].items():require(sha(S/cfg['proposal']/name)==digest,'Changed accepted proposal asset: '+name)
    proposal,deps=m.propose(alias);require(encoded(proposal)==(S/cfg['proposal']/'correspondence.proposed.json').read_bytes(),'Proposal no longer reproduces exactly.')
    parent=json.loads((S/PARENT).read_text());verify_parent(parent,proposal,alias,cfg)
    c=m.CONFIG[alias];frozen=Path(c['base'])/(c['name']+'.narrated-source.json');lesson=json.loads((S/frozen).read_text());manifest=json.loads((S/c['base']/(c['name']+'.captures.reviewed.json')).read_text())
    raw=m.cues(S/cfg['proposal']/'captions.proposed.srt');checked=m.cues(S/cfg['proposal']/'captions.proposed.checked.srt');qa=json.loads((S/cfg['proposal']/'derived-captions.actual.qa.json').read_text())
    duration=verify_audio_qa(qa,raw,checked,c['pins'][frozen.as_posix()],c['pins'][c['audio']],cfg['pins']['captions.proposed.srt'],cfg['pins']['captions.proposed.checked.srt'],cfg['cues'])
    require(len(proposal['source_spans'])==cfg['holds']and len(manifest['screenshots'])==cfg['images'],'Accepted source scope changed.')
    require(proposal['missing_anchors']==[]and not any(x['needs_review']for x in proposal['caption_layout']),'Source/readability gap remains.')
    require(proposal['source_spans'][-1]['end']['seconds']==duration,'Last source hold is not actual PCM duration.')
    entries=caption_annotations(alias,proposal,manifest)
    require([(x['start'],x['end'],x['text'])for x in entries]==[(x['start'],x['end'],x['text'])for x in checked],'Annotation changed actual caption text or timing.')
    scenes=instruction_mappings(lesson,proposal,manifest,entries,parent['recorded_at'])
    return {'config':cfg,'retained_config':c,'lesson':lesson,'frozen':frozen,'manifest':manifest,'proposal':proposal,'entries':entries,'scenes':scenes,'qa':qa,'parent':parent,'duration':duration,'frozen_sha':c['pins'][frozen.as_posix()],'audio_sha':c['pins'][c['audio']]}


def validate_listening_record(record,source_sha,audio_sha,qa_checked_at,now=None):
    require(isinstance(record,dict),'Listening receipt must be an object.')
    require(not re.search(r'(?i)(?:://|www\.|\blocalhost\b|\b127\.0\.0\.1\b)',json.dumps(record)),'Listening receipt must be URL-free, including optional fields.')
    require(record.get('reviewer')=='User','Require the actual User listening review, not agent QA or Root timing acceptance.')
    require(record.get('complete_natural_narration')is True,'Complete natural narration is not approved.')
    require(record.get('lesson_sha256')==source_sha and record.get('audio_sha256')==audio_sha,'Listening receipt source/audio identity differs.')
    evidence=record.get('evidence');require(isinstance(evidence,str)and re.search(r'(?i)\b(?:complete|full)\b',evidence)and re.search(r'(?i)\bnatural\b',evidence),'Retain actual full-listening request and natural/complete response.')
    checked=datetime.fromisoformat(record['reviewed_at'].replace('Z','+00:00'));earliest=datetime.fromisoformat(qa_checked_at.replace('Z','+00:00'))
    require(checked.tzinfo is not None and earliest.tzinfo is not None,'Listening chronology requires timezone-aware dates.')
    require(earliest<=checked<=(now or datetime.now(timezone.utc)),'Listening chronology must follow actual original-audio QA and cannot be future-dated.')
    return record


def receipt_path(cfg,override=None):
    relative=override or cfg['listening'];require(isinstance(relative,str)and relative and '\\'not in relative and not re.search(r'(?i)(?:://|www\.)',relative),'Use a public source-relative receipt path.')
    path=Path(relative);require(not path.is_absolute()and not any(x in {'.','..','private','.git','node_modules'}or x.startswith('.env')for x in path.parts),'Unsafe listening receipt path.')
    target=S/path;require(target.resolve().is_relative_to(S.resolve()),'Listening receipt escapes source root.')
    require(not any(x.is_symlink()for x in [target,*target.parents]if x!=S and x.is_relative_to(S)),'Symlinked listening receipt is not allowed.')
    return target,path


def listening(data,expected_sha,override=None):
    require(isinstance(expected_sha,str)and re.fullmatch('[a-f0-9]{64}',expected_sha),'Supply the exact genuine User listening receipt SHA256.')
    path,relative=receipt_path(data['config'],override);require(path.is_file(),'Actual User full-listening receipt has not arrived; assembly is blocked.')
    require(sha(path)==expected_sha,'Changed or unreviewed listening receipt.')
    original_qa=json.loads((S/data['retained_config']['qa']).read_text())
    record=validate_listening_record(json.loads(path.read_text()),data['frozen_sha'],data['audio_sha'],original_qa['checked_at'])
    return record,relative


def build(alias,expected_sha,override=None):
    data=preflight(alias);heard,receipt=listening(data,expected_sha,override);cfg=data['config'];final=Path(cfg['final']);c=data['retained_config'];now=datetime.now(timezone.utc).isoformat()
    scenes=[{'id':x['id'],'start':x['start'],'end':x['end'],'screens':x['screens'],'captions':[{k:c[k]for k in ['cue','screenshot_id','required_labels','spoken_references','instructional']}for c in x['captions']],'instruction_review':x['instruction_review']}for x in data['scenes']]
    caption_name=c['name']+f'.derived{cfg["cues"]}.srt';caption_sha=cfg['pins']['captions.proposed.checked.srt'];qa_path=Path(cfg['proposal'])/'derived-captions.actual.qa.json'
    plan={'schema_version':1,'lesson_id':c['name'],'duration_seconds':data['duration'],'instruction_mapping':'reviewed_scene_coverage','display_context':'TRAINING ONLY · fictional department','narration':{'file':c['audio'],'sha256':data['audio_sha'],'kind':'approved_natural_narration','approval':{'reviewer':heard['reviewer'],'reviewed_at':heard['reviewed_at'],'sha256':data['audio_sha'],'complete_natural_narration':True,'evidence':heard['evidence'],'qa_file':qa_path.as_posix(),'qa_sha256':cfg['pins']['derived-captions.actual.qa.json'],'listening_review_file':receipt.as_posix(),'listening_review_sha256':expected_sha}},'captions':{'file':(final/caption_name).as_posix(),'sha256':caption_sha,'kind':'speech_timed_srt','approval':{'reviewer':'Codex retained exact-source/service-anchor/full-PCM reviewer','reviewed_at':now,'sha256':caption_sha,'audio_sha256':data['audio_sha'],'speech_timing_reviewed':True,'method':'Original actual SRT boundaries and explicitly accepted genuine whole-second service word-group cuts only. Exact frozen words and adjacent same-image merges retain genuine endpoints. Full derived-cue PCM QA passed. No interpolated/millisecond word precision or human listening inferred from signal.'}},'capture_manifests':[{'file':(final/'captures.reviewed.json').as_posix(),'sha256':hashlib.sha256(encoded(data['manifest'])).hexdigest()}],'screenshot_reviews':{row['id']:{'reviewer':row['capture_review']['reviewer'],'reviewed_at':row['capture_review']['reviewed_at'],'sha256':row['sha256'],'application_visible':True,'labels_legible':True,'no_errors':True}for row in data['manifest']['screenshots']},'scenes':scenes,'parent_timing_review':{'file':PARENT.as_posix(),'sha256':PARENT_SHA},'actual_caption_derivation':{'file':str(Path(cfg['proposal'])/'caption-derivation.json'),'sha256':cfg['pins']['caption-derivation.json']},'publishable':False,'limitations':data['proposal']['limits_and_editorial_choices']+['Actual rendered-frame/caption/pixel checks and genuine browser beginning/middle/end playback remain required after a separate render.']}
    return data,plan,(S/cfg['proposal']/'captions.proposed.checked.srt').read_bytes(),caption_name


def write_new_directory(path,assets):
    require(not path.exists()and not path.is_symlink(),'New-only final inputs refuse every existing output; preserve history.')
    path.mkdir(parents=True)
    for name,body in assets.items():
        with (path/name).open('xb')as f:f.write(body)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--lesson',choices=['billing','shifts','all'],default='all');p.add_argument('--assemble',action='store_true');p.add_argument('--listening-review-sha256');p.add_argument('--listening-review-file');a=p.parse_args(argv)
    require(not(a.lesson=='all'and(a.assemble or a.listening_review_sha256 or a.listening_review_file)),'Choose one lesson for each exact genuine User listening receipt.')
    if a.assemble:
        require(a.listening_review_sha256,'--assemble requires the exact genuine User listening receipt hash.')
        require(not(S/CONFIG[a.lesson]['final']).exists(),'New-only final inputs refuse an existing package.')
        data,plan,captions,caption_name=build(a.lesson,a.listening_review_sha256,a.listening_review_file);out=S/data['config']['final'];assets={'plan.json':encoded(plan),'captures.reviewed.json':encoded(data['manifest']),caption_name:captions};write_new_directory(out,assets)
        # Renderer input validation is reachable ONLY after genuine listening
        # and explicit assembly, never on default preflight or source tests.
        sys.path.insert(0,str(ROOT/'scripts'));from render_walkthrough import validate_inputs
        checked=validate_inputs(S/data['frozen'],out/'plan.json',S)
        provenance={'kind':'New guarded take02 inputs after actual User full listening','lesson_id':data['lesson']['id'],'recipe_sha256':sha(__file__),'frozen_sha256':data['frozen_sha'],'audio_sha256':data['audio_sha'],'listening_receipt_sha256':a.listening_review_sha256,'parent_timing_receipt_sha256':PARENT_SHA,'source_proposal_sha256':data['config']['pins']['correspondence.proposed.json'],'strict_renderer_inputs_passed':True,'rendered':False,'canonical_site_or_target_changed':False,'outputs':[{'file':name,'sha256':sha(out/name)}for name in assets]}
        with(out/'provenance.json').open('xb')as f:f.write(encoded(provenance))
        print(json.dumps({'assembled_new_inputs':True,'strict_inputs_passed':True,'lesson':data['lesson']['id'],'plan_sha256':sha(out/'plan.json'),'scenes':len(checked['scenes']),'cues':len(checked['cues']),'duration':checked['duration'],'rendered':False,'canonical_or_site_changed':False}));return
    aliases=['billing','shifts']if a.lesson=='all'else[a.lesson];statuses=[]
    for alias in aliases:
        d=preflight(alias)
        if a.listening_review_sha256:listening(d,a.listening_review_sha256,a.listening_review_file)
        statuses.append({'lesson':d['lesson']['id'],'source_preflight':True,'parent_timing_review_valid':True,'frozen_source_sha256':d['frozen_sha'],'audio_sha256':d['audio_sha'],'holds':len(d['proposal']['source_spans']),'cues':len(d['entries']),'actual_User_listening_required':True,'receipt_present':receipt_path(d['config'])[0].is_file(),'final_inputs_written':False,'renderer_executed':False,'canonical_or_site_changed':False})
    print(json.dumps(statuses,indent=2))


if __name__=='__main__':main()
