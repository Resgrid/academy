"""Author Unit deployment from immutable actual screenshots and genuine74cue speech.

Default/source-preflight is read-only and does not render. Writing a NEW plan
requires the exact completed user listening review and independently hash-bound
full audio QA. Every source change needs a new version; no estimates, cue splits,
canonical edits, source reapproval, browser playback approval or publication occur.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
NAME = 'app-unit-deployment-draft-review'
BASE = Path('expansion/plans/' + NAME + '-capture-freeze-20261028')
FROZEN = '7c6556f4d2d90dea0cd6666eedd0a8cb4874372487194009c3778f5f3918e297'
MANIFEST = '62d9967648068d525e62579e2bc775f49663bba1e3af8d7225abf2087c0d7b10'
AUDIO = 'abe104aafe5de5df988a72fdf23e1926e9bc1b90a37ea9e189aeaea4a6c251d4'
CAPTIONS = 'ddcce993b4b7d6bef7c476bc53bc463d1acad61bb57801395888c1eb4e047155'
RAW = 'b4cb43e7b102439b6e8b04b388a94f81149c40052518a6efce871f6168b5ead8'
QA = '5b8902ae4fb2318b9be7df7286e0bafc7d3524ac844402c151f61cb2950cc73e'
LISTENING = '2055a9fac7f86bf81109cc202fb66836ed20f9c6ca7619eaaa1aff68fdba802e'
PINS = {
    BASE/(NAME+'.narrated-source.json'): FROZEN,
    BASE/'captures.reviewed.json': MANIFEST,
    BASE/'narration.frozen.txt': '6e1a30c03f60962cf01533d0e2d05c12e09b6fdf58e43672da9b894a3ef04123',
    BASE/'untimed-screen-sequence.json': 'bf0debcb8e5b1298a2a739e48ca9e7e284fa60365fae6007bac91a6ead3bbff9',
    BASE/'source-pins.json': '77b53f59a0e4880b284e0039db1fa08b3a57efa9d9cb7f6e31e8817255b93de8',
    Path('expansion/audio/'+NAME+'.m4a'): AUDIO,
    Path('expansion/audio/'+NAME+'.srt'): CAPTIONS,
    Path('expansion/audio/'+NAME+'-generated-20261028.raw.srt'): RAW,
    Path('expansion/audio/'+NAME+'.actual.qa.json'): QA,
}
SCENE_RANGES = [(1,6),(7,13),(14,20),(21,26),(27,32),(33,39),(40,45),(46,51),(52,58),(59,66),(67,74)]
# Actual caption bounds, not interpolated step times. Every row matches a frozen untimed span.
PICTURES = [(1,6,3),(7,13,4),(14,20,5),(21,26,6),(27,32,7),(33,36,8),(37,39,9),
            (40,42,14),(43,45,15),(46,51,10),(52,54,11),(55,58,12),(59,66,13),(67,74,9)]
NOTE = 'TRAINING ONLY - Unit app walkthrough note on this fictional draft. No actual hours, work, expense, or payment claim.'
ENGINE = 'Engine 51 (TRAINING Engine 51)'
BODEN = 'Wallace Boden (TRAINING Boden)'
WARNINGS = ['A long shift has no break recorded. — '+BODEN, 'A long shift has no break recorded. — '+ENGINE]
F42_TEXT = 'The F-42 is drafted from submitted time reports and checked against the CAL OES portal rules. Submission stays a manual, audited step on the web.'
REFERENCES = {
 1:{'Deployments':'Deployments','Open':'Open'},
 2:{'TRAINING ONLY — Academy field operations':'TRAINING ONLY, Academy field operations'},
 3:{'TRAINING-ACAD-OPS':'reference'},
 7:{'Time':'Time','Date':'Date'},8:{'Crew: Engine 51 (TRAINING Engine 51)':'crew','Reports this day':'Reports this day'},
 9:{'10/26/2026':'October twenty-sixth'},10:{'Draft · 16 h':'Draft report'},
 14:{'From':'From'},15:{'To':'To','Unpaid break (min)':'Unpaid break','Agency supplied meals':'agency supplied meals','Agency supplied accommodation':'accommodation'},
 16:{ENGINE:'unit',BODEN:'Boden'},17:{'Total 16 h':'sixteen hours'},
 19:{'Apply to crew':'Apply to crew','Add entry':'Add entry'},
 21:{ENGINE:'Engine Fifty-One','Agency supplied accommodation':'allowance switches'},
 23:{NOTE:'no actual hours, work, expense, or payment claim'},
 27:{'Save entries':'Save entries'},28:{'Submit report':'Submit report','Signatures':'Signatures'},
 29:{'Not signed by the crew boss yet.':'crew boss has not signed','No agency signature recorded.':'no agency signature is recorded'},
 33:{WARNINGS[0]:'long-shift warning for each subject',WARNINGS[1]:'long-shift warning for each subject'},
 37:{NOTE:'same training note',ENGINE:'Engine Fifty-One'},38:{'Draft':'Draft'},
 40:{'Time':'Time','My time':'My time','This time is already on report #1 for this day.':'this time is already on report number one'},
 43:{'Whole deployment':'Whole deployment','Start time report':'Start time report'},
 46:{'Expenses':'Expenses','No expenses for this day.':'empty day','New expense':'New expense'},
 47:{'Amount (USD)':'Amount in U.S.'},48:{'Description':'Description','City':'City','Fuel':'Fuel'},
 49:{'Take photo':'Take photo','Choose photo':'Choose photo'},50:{'Add expense':'adding an expense'},
 52:{'Usage':'Usage',ENGINE:'selected resource','Incident':'phase','Start odometer':'Start odometer'},
 53:{'End odometer':'End odometer','Engine hours':'Engine hours','Fuel':'Fuel'},
 54:{'mi':'miles','gal':'gallons'},55:{'km':'kilometers','L':'liters'},58:{'Add reading':'Add reading'},
 59:{'F-42':'F-42','NeedsReview':'Needs Review'},60:{'8 errors · 2 warnings':'errors and two warnings'},
 61:{'Validate':'Validate','Draft F-42 from time reports':'Draft F-42 from time reports'},
 63:{F42_TEXT:'draft uses submitted time reports'},64:{F42_TEXT:'manual, audited step on the web'},
 67:{'Draft':'Draft',NOTE:'stored Draft note'},
}
METHOD = ('All 13 original-size JPEGs personally inspected against the frozen 11-paragraph script and actual 74-cue SRT. '
          'Hold screenshot 007 during Save entries, 008 for unresolved break warnings, then 009 at genuine cue 37 (126.420s) for the reopened note. '
          'Switch 014 to 015 at cue 43 (148.430s), and 011 to 012 at cue 55 (197.449s). '
          'Amount (USD) is spoken across cues 47–48 and the F-42 error statistic across cues 59–60; the corresponding real screen persists throughout each pair. '
          'No speech cue is split or timing estimated. Report submission, signatures, expense creation, usage readings, F-42 validation and portal acceptance are not inferred. '
          'Historical On Scene/sidebar incident context is incidental; no current response or hardware claim. '
          'This is source/caption correspondence review, not encoded-frame or browser playback approval.')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def prepare(root=ROOT):
    root=Path(root).resolve(); sources=root/'sources'
    sys.path.insert(0,str(root/'scripts'))
    from render_walkthrough import load_cues, words
    from verify_capture_evidence import _Validator, _normalized, instruction_scene_digest
    for rel,want in PINS.items():
        need(sha(sources/rel)==want,'Pinned source/media changed: '+str(rel))
    lesson_path=sources/BASE/(NAME+'.narrated-source.json');lesson=read(lesson_path)
    records=read(sources/BASE/'captures.reviewed.json')['screenshots'];qa=read(sources/'expansion/audio'/(NAME+'.actual.qa.json'))
    cues=load_cues(sources/'expansion/audio'/(NAME+'.srt'));raw=load_cues(sources/'expansion/audio'/(NAME+'-generated-20261028.raw.srt'))
    need(len(lesson['scenes'])==11 and len(records)==13 and len(cues)==len(raw)==74,'Actual scene/image/cue inventory changed.')
    expected=' '.join(s['narration'] for s in lesson['scenes'])
    need(len(expected.split())==677 and words(expected)==words(' '.join(c['text'] for c in cues)),'Corrected script differs from frozen677words.')
    need(all((x['start'],x['end'])==(y['start'],y['end']) for x,y in zip(cues,raw)),'Raw actual cue bounds changed.')
    need(qa.get('passed') is True and qa.get('issues')==[] and not qa.get('possible_speech_gaps'),'Actual full narration QA must pass.')
    need(qa['audio']['sha256']==AUDIO and qa['lesson']['sha256']==FROZEN and qa['lesson']['words']==677,'QA pins differ.')
    need(qa['audio']['full_decode']=='passed' and qa['audio']['sample_rate']==48000 and qa['audio']['decoded_samples']==12626826,'Full decoded audio inventory missing.')
    need(qa['audio']['duration_seconds']==263.058875,'Actual duration changed.')
    need(qa['signal_threshold_rms']>=.001 and qa['silent_raw_cues']==qa['silent_corrected_cues']==0,'Cue-energy gate missing/weakened.')
    for part,want in [('raw_captions',RAW),('corrected_captions',CAPTIONS)]:
        detail=qa[part];need(detail['sha256']==want and detail['cues']==74 and len(detail['energy'])==74,'Every measured cue is required.')
        for n,(level,cue) in enumerate(zip(detail['energy'],cues),1):
            need(level['cue']==n and abs(level['start']-cue['start'])<1e-9 and abs(level['end']-cue['end'])<1e-9 and level['samples']>0 and level['rms']>=qa['signal_threshold_rms'] and level['below_threshold'] is False,'Invalid measured cue: '+str(n))
    need(qa['corrected_captions']['exact_script'] is True,'Exact corrected script QA required.')
    by_id={r['id']:r for r in records};numbered={int(r['id'].split('-')[3]):r['id'] for r in records}
    validator=_Validator(sources)
    for row in records:
        need(row['app']=='Unit' and row['kind']=='application_screenshot' and row['eligible_for_lesson'] is True and row['capture_review']['passed'] is True,'Source is not an eligible actual Unit screenshot.')
        for f,d in [('file','sha256'),('dom_file','dom_sha256')]:need(sha(sources/row[f])==row[d],'Source pixel/DOM changed: '+row['id'])
        need(row['capture_review']['sha256']==row['sha256'],'Source review binds different pixels.')
        validator.asset(row,row['id'],image=True);validator.observations(row,row['id'])
    need(not validator.issues,'; '.join(validator.issues))
    assignments={}
    untimed=read(sources/BASE/'untimed-screen-sequence.json')['spans']
    need(len(untimed)==len(PICTURES)==14,'Expected14authored spans.')
    for (first,last,picture),span in zip(PICTURES,untimed):
        ident=numbered[picture]
        need(ident==span['capture_ref'],'Physical span image changed.')
        need(words(' '.join(c['text'] for c in cues[first-1:last]))==words(span['narration_exact']),'Actual cues cross an authored span: '+ident)
        for n in range(first,last+1):
            need(n not in assignments,'Duplicate actual-cue assignment.');assignments[n]=ident
    need(set(assignments)==set(range(1,75)),'Every actual cue needs exactly one source image.')
    now=datetime.now(timezone.utc).isoformat();scenes=[]
    for index,(authored,(first,last)) in enumerate(zip(lesson['scenes'],SCENE_RANGES)):
        need(words(' '.join(c['text'] for c in cues[first-1:last]))==words(authored['narration']),'Scene cue boundary differs: '+authored['id'])
        start=0 if index==0 else cues[first-1]['start'];end=qa['audio']['duration_seconds'] if index==10 else cues[SCENE_RANGES[index+1][0]-1]['start']
        screens=[];expanded=[];selected=assignments[first];screen_start=start
        for n in range(first,last+1):
            ident=assignments[n]
            if ident!=selected:
                screens.append({'screenshot_id':selected,'start':screen_start,'end':cues[n-1]['start']});selected=ident;screen_start=cues[n-1]['start']
            refs=REFERENCES.get(n,{})
            need(set(refs)<=set(by_id[ident]['visible_labels']),'Unseen control atcue'+str(n))
            entry=dict(cues[n-1],cue=n,screenshot_id=ident,required_labels=list(refs),spoken_references=refs,instructional=bool(refs))
            v=_Validator(sources);v.spoken_references(entry,{_normalized(x) for x in refs},'cue'+str(n),True);need(not v.issues,'; '.join(v.issues));expanded.append(entry)
        screens.append({'screenshot_id':selected,'start':screen_start,'end':end})
        visible={label for screen in screens for label in by_id[screen['screenshot_id']]['visible_labels']}
        need(set(authored['required_labels'])<=visible,'Scene visible-label coverage gap: '+authored['id'])
        need(all(screen['end']-screen['start']>=2 for screen in screens),'Unreadable source flash cut.')
        built={'id':authored['id'],'title':authored['title'],'kind':'operational','start':start,'end':end,'visual_required_labels':authored['required_labels'],'screens':screens,'captions':expanded}
        review={'passed':True,'reviewer':'Codex actual original-JPEG/full74cue correspondence review','reviewed_at':now,'correspondence_reviewed':True,'no_unseen_controls':True,'mapping_sha256':instruction_scene_digest(built,by_id),'method':METHOD}
        scenes.append({'id':authored['id'],'start':start,'end':end,'screens':screens,'captions':[{k:e[k] for k in ['cue','screenshot_id','required_labels','spoken_references','instructional']} for e in expanded],'instruction_review':review})
    return {'root':root,'sources':sources,'lesson_path':lesson_path,'lesson':lesson,'records':records,'qa':qa,'cues':cues,'assignments':assignments,'scenes':scenes,'duration':263.058875}


def listen(context,path):
    need(path is not None,'Completed listening review is mandatory before a timed plan.')
    path=Path(path).resolve();need(path.is_relative_to(context['sources']),'Listening evidence must remain under sources.')
    need(sha(path)==LISTENING,'Listening review hash differs; obtain the actual user review, never invent one.')
    heard=read(path)
    need(heard.get('complete_natural_narration') is True and heard.get('audio_sha256')==AUDIO and heard.get('lesson_sha256')==FROZEN,'Listening review must bind complete actual audio and frozen source.')
    need(all(isinstance(heard.get(k),str) and heard[k].strip() for k in ['reviewer','reviewed_at','evidence']),'Completed real review metadata missing.')
    at=datetime.fromisoformat(heard['reviewed_at'].replace('Z','+00:00'));need(at.tzinfo is not None and at<=datetime.now(timezone.utc),'Invalid/future listening review time.')
    return heard


def repeat_decode(context,ffmpeg):
    need(ffmpeg is not None,'--ffmpeg required before writing the actual plan.')
    sys.path.insert(0,str(context['root']/'scripts'))
    from render_walkthrough import audio_duration
    import wave
    audio=context['sources']/'expansion/audio'/(NAME+'.m4a')
    with tempfile.TemporaryDirectory(prefix='unit-deployment-decode-') as temp:
        pcm=Path(temp)/'actual.wav';duration=audio_duration(str(ffmpeg),audio,pcm)
        with wave.open(str(pcm),'rb') as stream:
            need(stream.getnchannels()==1 and stream.getsampwidth()==2 and stream.getframerate()==48000 and stream.getnframes()==12626826,'Actual full decode sample inventory changed.')
    need(abs(duration-context['duration'])<1/48000,'Actual decoded duration changed.')
    need(sha(audio)==AUDIO,'Audio changed during actual decode.')


def build(context,heard):
    qa_file=Path('expansion/audio/'+NAME+'.actual.qa.json');now=datetime.now(timezone.utc).isoformat()
    return {'schema_version':1,'lesson_id':NAME,'duration_seconds':context['duration'],'instruction_mapping':'reviewed_scene_coverage','display_context':'TRAINING ONLY · fictional department',
      'narration':{'file':'expansion/audio/'+NAME+'.m4a','sha256':AUDIO,'kind':'approved_natural_narration','approval':{'reviewer':heard['reviewer'],'reviewed_at':heard['reviewed_at'],'sha256':AUDIO,'complete_natural_narration':True,'evidence':heard['evidence'],'qa_file':str(qa_file),'qa_sha256':QA}},
      'captions':{'file':'expansion/audio/'+NAME+'.srt','sha256':CAPTIONS,'kind':'speech_timed_srt','approval':{'reviewer':'Codex exact frozen677word/actual74cue correspondence','reviewed_at':now,'sha256':CAPTIONS,'audio_sha256':AUDIO,'speech_timing_reviewed':True,'method':'Every actual Descript cue boundary retained unchanged; full audio and all74raw/corrected cue energies passed QA. No estimated cuts or finer word timings.'}},
      'capture_manifests':[{'file':str(BASE/'captures.reviewed.json'),'sha256':MANIFEST}],
      'screenshot_reviews':{r['id']:{'reviewer':'Codex actual original-size13JPEG inspection and retained source review','reviewed_at':now,'sha256':r['sha256'],'application_visible':True,'labels_legible':True,'no_errors':True} for r in context['records']},
      'scenes':context['scenes'],'publishable':False,'limitations':context['lesson']['scope_limits']+['Encoded interval/cue readability and actual browser beginning/middle/end playback remain unreviewed.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-preflight',action='store_true')
    parser.add_argument('--write-correspondence',type=Path)
    parser.add_argument('--write-plan',type=Path)
    parser.add_argument('--listening-review',type=Path)
    parser.add_argument('--ffmpeg',type=Path)
    args=parser.parse_args();c=prepare()
    for dest in [args.write_correspondence,args.write_plan]:
        if dest:need(dest.resolve().is_relative_to(c['sources']/'expansion/plans') and not dest.exists(),'Use a NEW file under sources/expansion/plans; preserve all history.')
    if args.write_correspondence:
        doc={'kind':'actual-caption-source-correspondence-preparation','lesson_sha256':FROZEN,'audio_sha256':AUDIO,'captions_sha256':CAPTIONS,'qa_sha256':QA,'scenes':c['scenes'],'source_images':[{'id':r['id'],'file':r['file'],'sha256':r['sha256']} for r in c['records']],'rendered':False,'publication_approved':False,'method':METHOD}
        args.write_correspondence.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
    if args.write_plan:
        heard=listen(c,args.listening_review);repeat_decode(c,args.ffmpeg);plan=build(c,heard)
        with args.write_plan.open('x') as stream:stream.write(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
        from render_walkthrough import validate_inputs
        validated=validate_inputs(c['lesson_path'],args.write_plan,c['sources'])
        need(len(validated['cues'])==74,'Actual plan lost a speech cue.')
    print(json.dumps({'passed':True,'scenes':11,'actual_cues':74,'actual_sources':13,'screen_intervals':14,'duration':c['duration'],'correspondence_written':bool(args.write_correspondence),'plan_written':bool(args.write_plan),'rendered':False},indent=2))


if __name__=='__main__':main()
