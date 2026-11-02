"""Propose Workforce screen/caption correspondence from genuine service timings.

Read-only by default. --write-proposed writes a NEW source-only proposal and
fully decodes the retained audio to audit the separately derived126 captions.
It never writes a renderer plan, approval, canonical lesson or website.
"""
import argparse
from copy import deepcopy
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
NAME = 'core-workforce-foundations-unapproved-time'
BASE = Path('expansion/plans') / (NAME + '-capture-freeze-20261029')
AUDIO = Path('expansion/audio') / (NAME + '.m4a')
RAW = Path('expansion/audio') / (NAME + '-generated-20261029.raw.srt')
TEXT = Path('expansion/audio') / (NAME + '-generated-20261029.raw.txt')
ANCHORS = Path('expansion/audio') / (NAME + '-generated-20261029.one-second.txt')
CORRECTED = Path('expansion/audio') / (NAME + '.srt')
QA = Path('expansion/audio') / (NAME + '.actual.qa.json')
FROZEN = '4982c376b8f3a844ae56f2c5dc369d3d16f6d4bdd0c18573cdfaff1826a01129'
OUT = SOURCES / 'expansion/plans' / (NAME + '-take-01-proposed-20261029')
UTILITY = SOURCES / 'production/qa_core_certification_proposed_captions_20261028.py'
PINS = {
    BASE / (NAME + '.narrated-source.json'): FROZEN,
    BASE / 'captures.reviewed.json': '6e92cc0b9f37162b41c55cad70255283bb34d7bdd7830ae917797406be38269f',
    BASE / 'screen-sequence.untimed.json': '57692a1bc25cafde251202d71fcc43c1e4c467f207f75cd3a938b451e6eb8c24',
    BASE / 'source-freeze.json': '52f6ff61f30fbb225f541b1d65a56d78eb0defc2b2e1b77a1ad91189152bb6dc',
    AUDIO: '1ca64012e1af4a15c726ba0aeaf3aef37219655750fbd95be2f566fe03c13d80',
    RAW: '4699063aa44bbec308bee9c430c3e2f6951f980dcd0d619bd8d936d2b21ec866',
    TEXT: '441620d66cab672f41d431fff5bd0018514589f8c6394af2e1d9583631cd6ece',
    ANCHORS: '65f8ce594082a5493130ee8fb10a94853e48882cc0149d8a1e2fec136788fd5c',
    CORRECTED: '6450b6484587fd7260f47ea1a3d6485a639185c96690278c3f65a3404b4a0796',
    QA: '4ea78a855b912eac961b813636e88d4d02de699893940673d0708c854b2d9212',
}
UTILITY_SHA = '6c24c31946717f27f06a6829e32846dbb2420fc894f5d980b245d3a8b9441594'
# Actual raw cue starts. Repeated screenshots across chapter boundaries are
# intentional: the same saved worker/period is the next launcher's context.
STARTS = {1:2,9:4,13:5,14:4,17:5,22:6,23:7,25:8,27:10,33:11,
          38:12,39:13,41:14,44:15,46:16,49:16,50:17,58:18,62:19,
          65:20,66:21,67:20,68:22,70:23,75:24,80:25,82:26,84:27,
          92:28,93:29,100:30,108:31,111:32,113:33,116:41}
REBALANCE = [
    {'raw_cues':[12,13], 'at_seconds':43,
     'before_text':'Tax identifiers, addresses, and',
     'after_text':'filing contacts stay empty in this clean practice profile.',
     'before':4,'after':5,
     'reason':'Tax/address fields precede the lower filing-contact fields. Both original adjacent cues meet without a gap.'},
    {'raw_cues':[22,23], 'at_seconds':77,
     'before_text':'The Saved message confirms the response,',
     'after_text':'and the fresh employer view retains the training name.',
     'before':6,'after':7,
     'reason':'The actual Saved response precedes the separate fresh employer readback. Original cue23 would otherwise leave an unreadable subsecond fragment.'},
    {'raw_cues':[65,66], 'at_seconds':227,
     'before_text':'After saving, the one-day Volunteer period',
     'after_text':'appears, and its reopened form retains the selected defaults.',
     'before':20,'after':21,
     'reason':'The saved period row precedes the reopened defaults form. The reopened form itself shows Volunteer and both dates; no later form is shown before the original Save cue.'},
]
# Keys are exact readable UI observations; values are the corresponding spoken
# references, including explicitly reviewed natural aliases.
REFS = {
 1:{'Workforce':'Workforce'},3:{'Workforce':'Workforce','Overview':'Overview'},4:{'No employer profile yet.':'no employer profile'},
 9:{'Employer':'Employer','Employer profile':'Employer profile'},10:{'Legal name *':'Legal name'},11:{'TRAINING ONLY - Community coordination services':'Community coordination services'},
 12:{'FEIN':'Tax identifiers','EDD address':'addresses'},13:{'Filing contact name':'filing contacts'},
 14:{'Coverage is declared by you, never determined by Resgrid.':'blue protection notice'},
 17:{'Coverage status':'Coverage status'},18:{'Not declared':'Not declared'},19:{'US employees':'headcounts','Part of an integrated enterprise':'Part of an integrated enterprise'},
 21:{'Save':'Save'},22:{'Saved.':'Saved message'},23:{'TRAINING ONLY - Community coordination services':'training name'},
 25:{'Establishments':'Establishments','Add establishment':'Add establishment'},27:{'Code *':'Code','Name *':'Name'},28:{'TRN-COMM-28':'TRN-COMM-28','State':'State','IL':'IL'},
 29:{'Major activity':'Major activity'},30:{'Street address':'address','NAICS':'industry-code fields'},31:{'Code *':'code'},
 34:{'Active from':'Active from','10/28/2026':'October twenty-eighth, twenty twenty-six'},35:{'Active to':'Active to','America/Chicago':'America slash Chicago','Time zone':'Time zone'},
 36:{'Headquarters':'Headquarters','Reported in the prior year':'Reported in the prior year'},37:{'Save':'Save'},
 38:{'TRAINING ONLY - Community coordination base':'training base','IL':'IL','Active':'Active','Yes':'Yes'},39:{'Edit establishment':'reopened establishment','Time zone':'time zone'},
 41:{'Workers':'Workers'},42:{'Add worker':'Add worker','Member':'Member'},43:{'External worker key':'worker key','Display label':'Display label'},44:{'Member':'member'},
 45:{'Matthew Casey':'Casey','Add worker':'Add worker'},46:{'Worker':'Worker','Active':'Active','No employment periods yet.':'no employment periods yet'},
 49:{'Add employment':'Add employment'},50:{'Worker kind':'Worker kind','Volunteer':'Volunteer'},51:{'Start *':'Start','End':'End','10/28/2026':'October twenty-eighth'},
 53:{'Employment type':'Employment type','Exemption':'Exemption','Unknown':'Unknown'},56:{'Member: Matthew Casey':'person','Start *':'both dates'},
 58:{'Default establishment':'Default establishment'},59:{'TRAINING ONLY - Community response navigator':'Community response navigator','Personnel role':'Personnel role'},
 60:{'Personnel role':'role field'},62:{'Labor contractor':'Labor contractor','Affiliate':'Affiliate'},63:{'Save':'Save','Add employment':'employment panel'},64:{'Save':'Save'},
 65:{'Volunteer':'Volunteer'},66:{'Edit employment':'reopened form','Default establishment':'selected defaults'},
 67:{'Add assignment':'Add assignment'},68:{'Establishment':'establishment'},69:{'Work location':'location','US':'US','CA':'CA'},70:{'IL':'IL'},
 71:{'Effective *':'Effective','Expires':'Expires'},72:{'Job title':'job title','TRAINING ONLY - Coordination exercise':'ONLY Coordination exercise','Work mode':'Work mode','Non-remote':'Non-remote'},
 73:{'Work location':'location','Establishment':'establishment'},75:{'CRD job category':'CRD job category','SOC code':'SOC','Cal OES MARS classification':'Cal OES'},
 76:{'Cal OES MARS classification':'MARS classification'},77:{'Mapping provenance':'Mapping provenance'},79:{'Save':'Save'},
 80:{'TRAINING ONLY - Coordination exercise':'coordination exercise','Establishment':'training'},81:{'Non-remote':'Non-remote'},82:{'Edit assignment':'reopened assignment','IL':'IL'},
 84:{'Work entries':'Work entries'},85:{'09/28/2026':'two date controls'},86:{'10/28/2026':'October twenty-eighth'},87:{'No work entries in this window.':'No entries are listed yet'},89:{'Add work entry':'Add work entry'},
 92:{'Worker *':'Worker','Matthew Casey':'Matthew Casey','Date *':'Date','10/28/2026':'October twenty-eighth'},93:{'Hours *':'Hours','2':'two','Hours type':'Hours type','Regular':'Regular'},
 94:{'Establishment':'training establishment','Work mode':'Work mode','Non-remote':'Non-remote'},95:{'Country':'Country','State / province':'State slash province','US':'US','IL':'IL'},
 101:{'Call #':'Call number','Deployment id':'Deployment id'},103:{'Approved payroll cost':'Approved payroll cost','Approved':'Approved'},104:{'External source':'External source','External id':'External id'},
 107:{'Save':'Save'},108:{'Matthew Casey':'Casey','2.00':'two','Regular':'Regular','Establishment':'training establishment'},109:{'Academy software exercise':'Academy software exercise','Context':'Context'},110:{'Approved':'Approved','No':'No'},
 111:{'Edit work entry':'Edit work entry','Worker *':'worker','Date *':'date'},112:{'Hours *':'hours','IL':'Illinois'},113:{'Approved':'Approved','Approved payroll cost':'payroll-cost box'},
 116:{'Overview':'Overview'},117:{'Establishments: 1 · Workers: 1 · Employments: 1':'One establishment, one worker, and one employment'},118:{'Coverage status: Not declared':'Not declared','Resource profiles: 0 · Cost runs: 0':'no resource profiles or cost runs'},
}
SUPPLEMENTS = {
 4:['Coverage is declared by you, never determined by Resgrid.'],
 17:['Member: Matthew Casey'],
}
SUPPLEMENT_REVIEWED_AT = '2026-10-29T05:09:25Z'  # Actual binding clock after the retained image re-views.

def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()

def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()

def utility():
    assert sha(UTILITY)==UTILITY_SHA,'Changed retained caption utility.'
    sys.path.insert(0,str(ROOT/'scripts'))
    spec=importlib.util.spec_from_file_location('workforce_caption_utility',UTILITY)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def rebalance(cues,anchors,changes):
    """Repartition two adjoining cues at an actual service word marker only."""
    from render_walkthrough import words
    out=deepcopy(cues);receipts=[]
    for change in changes:
        a,b=change['raw_cues'];assert b==a+1
        before,after=out[a-1],out[b-1]
        assert before['end']==after['start'],'No joining unrecorded or intervening pauses.'
        joined=words(before['text']+' '+after['text'])
        assert words(change['before_text'])+words(change['after_text'])==joined,'Changed spoken words.'
        offset=sum(len(words(c['text'])) for c in cues[:a-1])+len(words(change['before_text']))
        assert (change['at_seconds'],offset) in anchors,'Missing genuine whole-second word marker.'
        cut=float(change['at_seconds'])
        assert min(cut-before['start'],after['end']-cut)>=1.0,'Unreadable derived caption.'
        end=after['end'];before.update(end=cut,text=change['before_text']);after.update(start=cut,end=end,text=change['after_text'])
        receipts.append(dict(change,global_word_offset=offset,precision='Genuine Descript one-second TXT marker only; no millisecond word precision.'))
    assert len(out)==len(cues) and words(' '.join(c['text'] for c in out))==words(' '.join(c['text'] for c in cues))
    return out,receipts

def prepare():
    helper=utility()
    from render_walkthrough import load_cues,words
    from verify_capture_evidence import _image_dimensions
    for path,digest in PINS.items():assert sha(SOURCES/path)==digest,'Changed frozen/audio input: '+str(path)
    lesson=json.loads((SOURCES/BASE/(NAME+'.narrated-source.json')).read_text())
    freeze=json.loads((SOURCES/BASE/'source-freeze.json').read_text())
    for path,digest in freeze['freeze_files'].items():assert sha(SOURCES/BASE/path)==digest,'Changed frozen asset: '+path
    original_manifest=json.loads((SOURCES/BASE/'captures.reviewed.json').read_text());manifest=deepcopy(original_manifest)
    rows={int(r['id'][:3]):r for r in manifest['screenshots']}
    assert len(rows)==31 and len(lesson['scenes'])==15
    supplemental=[]
    for number,row in rows.items():
        assert row['eligible_for_lesson'] and row['capture_review']['passed']
        assert sha(SOURCES/row['file'])==row['sha256'] and sha(SOURCES/row['dom_file'])==row['dom_sha256']
        assert _image_dimensions(SOURCES/row['file'])==(1434,773)
        if number in SUPPLEMENTS:
            extra=SUPPLEMENTS[number];assert not set(extra)&set(row['visible_labels'])
            receipt={'source_id':row['id'],'image_sha256':row['sha256'],'reviewer':'Codex dispatch_ic_coverage','reviewed_at':SUPPLEMENT_REVIEWED_AT,'literal_labels_added':extra,
                'method':'Personally re-viewed exact retained JPEG through view_image while preparing this cue plan.004 blue notice first sentence and017 left Member: Matthew Casey are readable and unobstructed. Tool display review only; no100-percent manual pixel inspection or fresh application operation is asserted.',
                'frozen_image_dom_geometry_time_and_prior_review_unchanged':True,'parent_timing_review_pending':True}
            row['visible_labels']+=extra;row['supplemental_literal_review']=receipt;supplemental.append(receipt)
    raw=load_cues(SOURCES/RAW);corrected=load_cues(SOURCES/CORRECTED);assert len(raw)==len(corrected)==126
    for a,b in zip(raw,corrected):assert (a['start'],a['end'],words(a['text']))==(b['start'],b['end'],words(b['text']))
    all_words=words(' '.join(s['narration'] for s in lesson['scenes']))
    anchors,anchor_words=helper.service_anchors((SOURCES/ANCHORS).read_text())
    assert all_words==anchor_words==words((SOURCES/TEXT).read_text())==words(' '.join(c['text'] for c in raw))
    qa=json.loads((SOURCES/QA).read_text());assert qa['passed'] and not qa['issues'] and not qa['possible_speech_gaps']
    assert qa['lesson']['sha256']==FROZEN and qa['audio']['sha256']==PINS[AUDIO] and qa['audio']['full_decode']=='passed'
    assert qa['silent_raw_cues']==qa['silent_corrected_cues']==0
    derived,receipts=rebalance(corrected,anchors,REBALANCE)
    current=None;entries=[]
    for number,cue in enumerate(derived,1):
        current=STARTS.get(number,current);assert current in rows
        refs=REFS.get(number,{})
        try:
            helper.references(cue['text'],refs,rows[current])
        except AssertionError as error:
            raise AssertionError(f'Cue {number}, image {current}: {error}') from error
        entries.append(dict(cue,cue=number,raw_cues=next((x['raw_cues'] for x in REBALANCE if number in x['raw_cues']),[number]),screenshot_id=rows[current]['id'],required_labels=list(refs),spoken_references=refs,instructional=bool(refs)))
    scenes=[];position=0
    sequence=json.loads((SOURCES/BASE/'screen-sequence.untimed.json').read_text())
    for index,scene in enumerate(lesson['scenes']):
        begin=position;count=len(words(scene['narration']));used=0
        while position<len(raw) and used<count:used+=len(words(raw[position]['text']));position+=1
        assert used==count,'Caption crossed frozen chapter boundary.'
        selected=entries[begin:position];unique=list(dict.fromkeys(c['screenshot_id'] for c in selected))
        allowed=list(dict.fromkeys(s['source_id'] for s in sequence['spans'] if s['scene_id']==scene['id']))
        assert unique==allowed,(scene['id'],unique,allowed)
        union={v for row in rows.values() if row['id'] in unique for v in row['visible_labels']}
        assert set(scene['required_labels'])<=union,(scene['id'],set(scene['required_labels'])-union)
        start=0.0 if index==0 else selected[0]['start'];end=qa['audio']['duration_seconds'] if index==14 else raw[position]['start']
        spans=[];active=selected[0]['screenshot_id'];opening=start
        for c in selected:
            if c['screenshot_id']!=active:
                spans.append({'capture_ref':active,'actual_start':opening,'actual_end':c['start']});active=c['screenshot_id'];opening=c['start']
        spans.append({'capture_ref':active,'actual_start':opening,'actual_end':end})
        scenes.append({'scene_id':scene['id'],'title':scene['title'],'first_raw_cue':begin+1,'last_raw_cue':position,'required_labels':scene['required_labels'],'source_spans':spans,'cue_numbers':[c['cue'] for c in selected]})
    assert position==126
    blocks=[];readability=[]
    for cue in entries:
        lines=textwrap.wrap(cue['text'],width=42,break_long_words=False,break_on_hyphens=False)
        if len(lines)>2:lines=textwrap.wrap(cue['text'],width=48,break_long_words=False,break_on_hyphens=False)
        assert len(lines)<=2,'Review actual caption wording; never interpolate a split.'
        duration=cue['end']-cue['start'];cps=len(cue['text'])/duration
        # This original two-word cue is971ms; the actual Workers screen holds
        # nearly8s. Keep its genuine boundary rather than inventing more speech.
        original_short=(cue['cue']==41 and cue['text']=='Open Workers.' and abs(duration-.971)<.000001)
        assert (duration>=1.0 or original_short) and cps<=22.0,(cue['cue'],duration,cps)
        readability.append({'cue':cue['cue'],'duration_seconds':round(duration,3),'characters_per_second':round(cps,3),'lines':len(lines)})
        blocks.append(f"{cue['cue']}\n{helper.stamp(cue['start'])} --> {helper.stamp(cue['end'])}\n"+'\n'.join(lines))
    holds=[s for scene in scenes for s in scene['source_spans']]
    assert min(s['actual_end']-s['actual_start'] for s in holds)>=2.0
    proposal={'kind':'PROPOSED actual-audio Workforce screen/caption correspondence','lesson_id':NAME,'frozen_lesson_sha256':FROZEN,'audio_sha256':PINS[AUDIO],'raw_cue_count':126,'proposed_derived_cue_count':126,'scenes':scenes,'cue_correspondence':entries,'genuine_service_anchor_rebalances':receipts,'readability':readability,'source_images':31,'screen_intervals':len(holds),'minimum_screen_hold_seconds':min(s['actual_end']-s['actual_start'] for s in holds),'actual_duration_seconds':qa['audio']['duration_seconds'],'supplemental_literal_reviews':supplemental,'source_manifest':{'original_file':str(BASE/'captures.reviewed.json'),'original_sha256':PINS[BASE/'captures.reviewed.json'],'frozen_raw_image_dom_bytes_unchanged':True},'explicit_timing_choices':['004 returns at raw14 so the actual blue protection notice is visible.005 supplies the lower filing contacts at real43s.','Saved employer response006 precedes fresh readback007 at real77s.','019 starts at raw62, making Affiliate and the right-hand employment Save visible before they are described;018 Save remains offscreen and is never substituted.','Saved employment020 precedes fresh edit021 at real227s.021 itself visibly contains Volunteer and both dates.','020 returns at raw67 for the actual Add assignment launcher; no job assignment is claimed before that point.','Work-entry028 supplies Worker/date before prepared029 Hours2/Regular/US/IL. No clipped full external references are claimed.','All screens hold through genuine service gaps to the next real boundary; no operation timing or subsecond word position is inferred.'],'listening_approval':'PENDING; separate exact source/audio-bound user review required before final assembly','parent_timing_review_pending':True,'renderer_plan_created':False,'rendered':False,'publication_approved':False}
    return proposal,'\n\n'.join(blocks)+'\n\n',manifest

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write-proposed',action='store_true');parser.add_argument('--ffmpeg');args=parser.parse_args()
    proposed,captions,manifest=prepare()
    if args.write_proposed:
        assert args.ffmpeg and Path(args.ffmpeg).is_file(),'Actual full decode requires FFmpeg.'
        assert not OUT.exists(),'Use a NEW proposal directory; preserve history.'
        OUT.mkdir(parents=True)
        raw=OUT/(NAME+'.derived126.proposed.srt');raw.write_text(captions)
        sys.path.insert(0,str(ROOT/'scripts'));from qa_narration import audit
        corrected=OUT/(NAME+'.derived126.corrected.srt');report=OUT/(NAME+'.derived126.actual.qa.json')
        result=audit(SOURCES/BASE/(NAME+'.narrated-source.json'),SOURCES/AUDIO,raw,corrected,report,args.ffmpeg,FROZEN)
        assert result['passed'] and not result['issues'] and not result['alignment']['text_changes']
        assert result['silent_raw_cues']==result['silent_corrected_cues']==0
        assert result['audio']==json.loads((SOURCES/QA).read_text())['audio']
        proposed['derived_audio_qa']={'file':str(report.relative_to(SOURCES)),'sha256':sha(report),'passed':True,'silent_cues':0,'minimum_cue_rms':result['minimum_raw_cue_rms'],'method':'Full actual audio decode and every separately derived cue measured. Energy is not natural/full listening approval.'}
        (OUT/'captures.proposed.json').write_bytes(encoded(manifest));(OUT/'correspondence.proposed.json').write_bytes(encoded(proposed))
        (OUT/'cue-screen-correspondence.txt').write_text('\n'.join(f"{c['cue']:03} {c['start']:.3f}–{c['end']:.3f} {c['screenshot_id']} | {c['text']}" for c in proposed['cue_correspondence'])+'\n')
        (OUT/'provenance.json').write_bytes(encoded({'kind':'source_only_proposed_126cue_Workforce_timing','helper_sha256':sha(Path(__file__)),'input_hashes':{str(k):v for k,v in PINS.items()},'original_raw_cues_unchanged':True,'original_audio_frozen_narration_unchanged':True,'integer_second_word_marker_cuts':[43,77,227],'listening_review_pending':True,'parent_timing_review_pending':True,'renderer_plan_created':False,'canonical_or_ready_or_site_changed':False,'files':{p.name:sha(p) for p in sorted(OUT.iterdir())}}))
    print(json.dumps({'source_preflight':True,'scenes':15,'raw_cues':126,'proposed_cues':126,'sources':31,'intervals':proposed['screen_intervals'],'minimum_hold_seconds':proposed['minimum_screen_hold_seconds'],'files_written':args.write_proposed,'listening_pending':True,'parent_timing_review_pending':True,'rendered':False}))

if __name__=='__main__':main()
