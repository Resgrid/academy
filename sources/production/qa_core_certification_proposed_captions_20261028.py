"""Propose Certification screen/caption correspondence; never approve or render.

Default is read-only. --write-proposed requires a NEW output directory and
decodes the entire actual M4A for separate per-derived-cue PCM measurements.
Raw113 captions, audio, frozen source, and original QA remain unchanged.
Whole-second Descript anchors are not millisecond word-time estimates.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import textwrap

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
NAME = 'core-certification-administration'
BASE = Path('expansion/plans/core-certification-administration-capture-freeze-20261028')
DIRECTORY = SOURCES / 'expansion/plans/core-certification-administration-take-01-proposed-derived-20261028'
AUDIO = Path('expansion/audio') / (NAME + '.m4a')
RAW = Path('expansion/audio') / (NAME + '-generated-20261028.raw.srt')
CORRECTED = Path('expansion/audio') / (NAME + '.srt')
TEXT = Path('expansion/audio') / (NAME + '-generated-20261028.raw.txt')
ANCHORS = Path('expansion/audio') / (NAME + '-generated-20261028.one-second.txt')
ORIGINAL_QA = Path('expansion/audio') / (NAME + '.actual.qa.json')
FROZEN = 'f141a244ebd9ce37263cfc04e6a0415a6c8febcdf7aa738a3ad2214ddbcbf06d'
PINS = {
    BASE / (NAME + '.narrated-source.json'): FROZEN,
    BASE / (NAME + '.captures.reviewed.json'): '032953a6cc969b85f6dd2ca8ede133c72f80b1410c6e5b44d8cb46fc63a4fc68',
    BASE / (NAME + '.screen-sequence.json'): '8337c73c3bbe486b0c91bd1adf2e9c767166f3bdcb38d5914759f1dc064e7a50',
    RAW: '50a1828f81efdf5116bdff0e971ba2442cd481f378d01962872b9c8a82a84954',
    TEXT: '9638121af66cfe91d40f5974d8fb9415262583adf5627e7c6a575ad902fcec14',
    ANCHORS: '22c71dbc18d79c05974a862dff29d455129eb640a43820893dd30e91d85dcbc7',
    CORRECTED: 'a0c4969231d5c37294ee8a2d992e6d5c361684be72a65e9a158cc79fe1749f55',
    AUDIO: 'ebb6146147c09c83a08b558affa27db660551936bfc3d92ad525e9aca65324f3',
    ORIGINAL_QA: '33c33779e1de9b96a50f7a6427c9d90039c888957083a8191a36e3d03ae676c4',
}
SCREEN_STARTS = {1:1,5:2,10:1,11:7,14:8,20:7,21:9,22:10,30:11,
                 36:12,39:13,40:14,41:15,48:16,56:17,58:18,61:19,
                 63:20,68:20,69:21,75:21,76:22,78:23,81:24,85:22,
                 86:3,88:4,89:5,90:6,91:26,95:28,101:27,103:20,107:28}
SPLITS = [
    {'raw_cue':35, 'at_seconds':122,
     'before_text':'Use Save,', 'after_text':'then read the returned catalog row.',
     'before':11, 'after':12, 'before_references':{'Save':'Save'},
     'after_references':{'Certification types':'returned catalog row'},
     'reason':'Actual Save control remains on011 until the genuine marker before then;012 then pictures the returned catalog.'},
    {'raw_cue':88, 'at_seconds':308,
     'before_text':'Warn only permits role changes with warnings;', 'after_text':'Enforce can block',
     'before':4, 'after':5,
     'before_references':{'Warn only – allow role changes, show warnings, notify':'Warn only'},
     'after_references':{'Enforce':'Enforce'},
     'reason':'004 contains the actual Warn only selection;005 contains the actual Enforce prefix/help, both unsaved inspections.'},
]
REFS = {
 1:{'Certifications':'Certifications'},4:{'Pending verification':'pending verification'},
 5:{'Wallace Boden':'Boden','Pending verification':'pending record'},
 10:{'Certification types':'Certification types'},
 11:{'Code':'code','Applies to':'scope','Validity':'validity'},
 12:{'Records':'record count','Requirements':'requirement count'},13:{'Template gallery':'Template gallery'},
 14:{'SAR':'SAR'},17:{'Cancel':'Cancel'},20:{'New type':'New type'},
 21:{'Type':'Enter Training Only'},22:{'Type':'Type'},23:{'Code':'code','TRN-REVIEW-20261028':'TRN-REVIEW-20261028'},
 26:{'Category':'Category','Other':'Other','Applies to':'Applies to','Person':'Person'},
 27:{'Issuing authority':'Issuing authority'},28:{'Description':'Description'},
 30:{'Default validity (months)':'Default validity','12':'twelve months','Never expires':'Never expires'},
 31:{'Credit hours per renewal':'Credit hours per renewal'},
 32:{'Requires supervisor verification':'Requires supervisor verification','Active':'Active'},
 33:{'New records stay pending until someone with manage rights signs them off.':'new records remain pending'},
 36:{'Code':'code','Person':'Person','12 months':'twelve months'},
 37:{'Records':'Records','Requirements':'Requirements','0':'zero'},
 39:{'Add Certification':'Add Certification'},40:{'Member':'Member'},41:{'Matthew Casey':'Matthew Casey','Type':'type'},
 44:{'Issued on':'Issued on','Expires on':'Expires on'},48:{'Name':'Name'},
 49:{'Number':'number','DEMO-CASEY-REVIEW-20261028':'DEMO-CASEY-REVIEW'},
 50:{'Valid Area':'Valid Area','Issued by':'Issued by'},52:{'Issued on':'issue'},53:{'Expires on':'expiry'},
 54:{'File':'File'},55:{'Save':'Save'},
 56:{'Saved.':'Saved','Pending verification':'pending records','2':'two'},
 58:{'Matthew Casey':'Casey’s'},
 59:{'Member':'member','Type':'type','Number':'number','Expires on':'expiry','Verify':'Verify'},
 60:{'Verify':'button'},61:{'Active':'Active','Verified by':'Verified by'},62:{'Wallace Boden':'Boden'},
 63:{'Active':'status','Verified by':'reviewer'},68:{'Matthew Casey':'Matthew Casey’s'},
 69:{'Name':'name','Type':'type','Expires on':'expiry','Status':'status'},
 70:{'Firefighter qualification':'Firefighter qualification'},71:{'Active':'Active'},
 75:{'Certification types':'Certification types'},76:{'Records':'Record','Requirements':'Requirements','1':'one','0':'zero'},
 77:{'Edit':'Edit'},78:{'Applies to':'Applies to','Person':'Person'},79:{'Code':'Code'},
 81:{'Default validity (months)':'twelve months','Requires supervisor verification':'verification'},
 82:{'Requires supervisor verification':'required','Active':'Active'},85:{'Settings':'Settings'},
 86:{'Off – requirements are informational only':'Off','Grace period (days)':'thirty days','Treat records pending verification as valid for role requirements':'pending records'},
 89:{'Enforce':'unqualified role additions','Grace period (days)':'grace'},
 90:{'Off – requirements are informational only':'Off','Save':'Save'},91:{'Off – requirements are informational only':'Off','Notifications':'notifications'},
 92:{'Notify the holder directly':'holder','Send department administrators a nightly digest':'administrator-digest'},
 93:{'60,30,14,7,1':'sixty, thirty, fourteen, seven, and one'},
 95:{'Group':'Group','Truck 81':'Truck 81'},96:{'Matthew Casey':'Casey’s','TRN-REVIEW-20261028':'training code'},
 97:{'Pending verification':'Pending verification'},99:{'Export CSV':'Export CSV'},100:{'Compliance report':'Compliance report'},
 101:{'Matthew Casey':'Casey’s row','TRN-REVIEW-20261028':'training column','2027-10-28':'expiry','Active':'Active'},
}

sys.path.insert(0, str(ROOT / 'scripts'))
from render_walkthrough import load_cues, words
from verify_capture_evidence import _Validator, _normalized, _image_dimensions

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encoded(value): return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
def stamp(seconds):
    ms=round(seconds*1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'

def service_anchors(text):
    parts=re.split(r'\[(\d{2}):(\d{2}):(\d{2})\]',text)
    assert len(parts)>4 and not words(parts[0]),'Require genuine timestamp export.'
    anchors=[];offset=0
    for i in range(1,len(parts),4):
        anchors.append((int(parts[i])*3600+int(parts[i+1])*60+int(parts[i+2]),offset))
        offset+=len(words(parts[i+3]))
    return anchors,words(re.sub(r'\[\d{2}:\d{2}:\d{2}\]','',text))

def references(text,refs,row):
    assert set(refs)<=set(row['visible_labels']),(row['id'],set(refs)-set(row['visible_labels']))
    validator=_Validator(SOURCES)
    validator.spoken_references({'text':text,'spoken_references':refs},{_normalized(x) for x in refs},'proposed',True)
    assert not validator.issues,validator.issues

def check_anchor(split,cues,anchors):
    number=split['raw_cue'];cue=cues[number-1]
    assert words(split['before_text'])+words(split['after_text'])==words(cue['text'])
    offset=sum(len(words(c['text'])) for c in cues[:number-1])+len(words(split['before_text']))
    assert (split['at_seconds'],offset) in anchors,'No guessed or interpolated word boundary.'
    assert min(split['at_seconds']-cue['start'],cue['end']-split['at_seconds'])>=1.0,'Review and coalesce unreadable captions on the same image.'
    return dict(split,global_word_offset=offset,precision='Genuine service whole-second marker; not millisecond word precision.')

def prepare():
    for path,digest in PINS.items():assert sha(SOURCES/path)==digest,'Changed retained input: '+str(path)
    lesson=json.loads((SOURCES/BASE/(NAME+'.narrated-source.json')).read_text())
    manifest=json.loads((SOURCES/BASE/(NAME+'.captures.reviewed.json')).read_text())
    sequence=json.loads((SOURCES/BASE/(NAME+'.screen-sequence.json')).read_text())
    raw=load_cues(SOURCES/RAW);corrected=load_cues(SOURCES/CORRECTED)
    assert len(raw)==len(corrected)==113 and len(lesson['scenes'])==12
    for a,b in zip(raw,corrected):assert (a['start'],a['end'],words(a['text']))==(b['start'],b['end'],words(b['text']))
    all_words=words(' '.join(s['narration'] for s in lesson['scenes']))
    anchors,anchor_words=service_anchors((SOURCES/ANCHORS).read_text())
    assert all_words==words((SOURCES/TEXT).read_text())==words(' '.join(c['text'] for c in raw))==anchor_words
    assert len(all_words)==966
    qa=json.loads((SOURCES/ORIGINAL_QA).read_text())
    assert qa['passed'] and not qa['issues'] and not qa['possible_speech_gaps']
    assert qa['audio']['sha256']==PINS[AUDIO] and qa['audio']['full_decode']=='passed'
    assert qa['lesson']['sha256']==FROZEN and qa['silent_raw_cues']==qa['silent_corrected_cues']==0
    rows={int(r['id'][:3]):r for r in manifest['screenshots']};assert len(rows)==27 and 25 not in rows
    for row in rows.values():
        assert row['eligible_for_lesson'] and row['capture_review']['passed']
        assert sha(SOURCES/row['file'])==row['sha256'] and sha(SOURCES/row['dom_file'])==row['dom_sha256']
        assert _image_dimensions(SOURCES/row['file'])==(1434,773)
    source_map=[];current=None
    for number,cue in enumerate(raw,1):
        current=SCREEN_STARTS.get(number,current);assert current in rows
        refs=REFS.get(number,{})
        if number not in (35,88):references(cue['text'],refs,rows[current])
        source_map.append(dict(cue,raw_cue=number,screenshot_id=rows[current]['id'],required_labels=list(refs),spoken_references=refs))
    operations=[check_anchor(s,raw,anchors) for s in SPLITS];splits={s['raw_cue']:s for s in SPLITS}
    expanded=[]
    for number,cue in enumerate(source_map,1):
        if number==55:continue
        if number in splits:
            split=splits[number]
            for side in ['before','after']:
                text=split[side+'_text'];refs=split[side+'_references'];row=rows[split[side]]
                references(text,refs,row)
                expanded.append({'start':cue['start'] if side=='before' else float(split['at_seconds']),
                    'end':float(split['at_seconds']) if side=='before' else cue['end'],
                    'text':text,'screenshot_id':row['id'],'required_labels':list(refs),
                    'spoken_references':refs,'raw_cues':[number]})
        else:
            out={k:cue[k] for k in ['start','end','text','screenshot_id','required_labels','spoken_references']};out['raw_cues']=[number]
            if number==54:
                follow=source_map[54];assert follow['screenshot_id']==cue['screenshot_id']
                out.update(end=follow['end'],text=cue['text']+' '+follow['text'],raw_cues=[54,55],
                           required_labels=['File','Save'],spoken_references={'File':'File','Save':'Save'})
                references(out['text'],out['spoken_references'],rows[16])
            expanded.append(out)
    assert len(expanded)==114 and words(' '.join(c['text'] for c in expanded))==all_words
    for index,cue in enumerate(expanded,1):cue.update(cue=index,instructional=bool(cue['required_labels']))
    scenes=[];cursor=0;raw_position=0
    for index,(scene,frozen_scene) in enumerate(zip(lesson['scenes'],sequence['scenes'])):
        assert scene['id']==frozen_scene['scene_id'] and words(scene['narration'])==words(frozen_scene['narration'])
        count=len(words(scene['narration']));start=raw_position
        while raw_position<len(raw) and cursor<count:cursor+=len(words(raw[raw_position]['text']));raw_position+=1
        assert cursor==count;cursor=0
        entries=[c for c in expanded if start+1<=c['raw_cues'][0]<=raw_position]
        allowed=[s['capture_id'] for s in frozen_scene['screens']]
        selected=list(dict.fromkeys(c['screenshot_id'] for c in entries))
        assert selected==allowed,(scene['id'],selected,allowed)
        union={label for r in rows.values() if r['id'] in selected for label in r['visible_labels']}
        assert set(scene['required_labels'])<=union,(scene['id'],set(scene['required_labels'])-union)
        begin=0.0 if index==0 else entries[0]['start'];end=qa['audio']['duration_seconds'] if index==11 else raw[raw_position]['start']
        spans=[];active=entries[0]['screenshot_id'];opening=begin
        for c in entries:
            if c['screenshot_id']!=active:
                spans.append({'capture_ref':active,'actual_start':opening,'actual_end':c['start']});active=c['screenshot_id'];opening=c['start']
        spans.append({'capture_ref':active,'actual_start':opening,'actual_end':end})
        scenes.append({'scene_id':scene['id'],'first_raw_cue':start+1,'last_raw_cue':raw_position,
                       'derived_cues':[c['cue'] for c in entries],'required_labels':scene['required_labels'],
                       'source_spans':spans,'source_limits':scene['source_limits']})
    blocks=[];readability=[]
    for c in expanded:
        lines=textwrap.wrap(c['text'],width=42,break_on_hyphens=False,break_long_words=False)
        if len(lines)>2:lines=textwrap.wrap(c['text'],width=48,break_on_hyphens=False,break_long_words=False)
        assert len(lines)<=2,'Read actual text; do not invent a split to fit captions.'
        duration=c['end']-c['start'];cps=len(c['text'])/duration
        assert duration>=1.0 and cps<=22.0,(c['cue'],duration,cps)
        readability.append({'cue':c['cue'],'duration_seconds':round(duration,3),'characters_per_second':round(cps,3),'lines':len(lines)})
        blocks.append(f"{c['cue']}\n{stamp(c['start'])} --> {stamp(c['end'])}\n"+'\n'.join(lines))
    coalescence={'raw_cues':[54,55],'same_actual_image':rows[16]['id'],'raw55_seconds':round(raw[54]['end']-raw[54]['start'],3),
                 'start':raw[53]['start'],'end':raw[54]['end'],'derived_seconds':round(raw[54]['end']-raw[53]['start'],3),
                 'text':next(c['text'] for c in expanded if c['raw_cues']==[54,55]),
                 'method':'Adjacent unchanged words retained from raw54 and raw55 on the same prepared File/Save form. Caption ends at genuine raw55 end; no inserted words or inferred word time.'}
    out={'schema_version':1,'lesson_id':NAME,'status':'PROPOSED actual-audio source/caption plan only; full user listening PENDING',
         'source_frozen_sha256':FROZEN,'renderer_normalized_words':966,'space_delimited_source_words':956,
         'original_raw_cues':113,'proposed_derived_cues':114,'reviewed_actual_sources':27,
         'screen_intervals':sum(len(s['source_spans']) for s in scenes),'actual_audio_seconds':qa['audio']['duration_seconds'],
         'genuine_service_anchor_cuts':operations,'coalescence':coalescence,'scenes':scenes,
         'raw_cue_correspondence':source_map,'cue_correspondence':expanded,'readability':readability,
         'timing_method':'Original cue boundaries plus exact exported whole-second word anchors122/308 only. Images hold through actual gaps until the next observed boundary; these holds are not speech-time interpolation.',
         'listening_approved':False,'renderer_plan_created':False,'video_rendered':False,'publication_approved':False,
         'coverage_limits':['Frozen historical zero-requirement/code-editable state remains historical; later Personnel requirement exercise is separate.',
             '005 supports Enforce prefix and actual help, not the clipped full selected option.',
             '025 wrong-foreground diagnostic remains excluded;027 is the actual HTML report.',
             'No template applied, CSV downloaded, renewal/credits/revocation, role removal, policy save or notification delivery demonstrated.',
             'All27source originals were reviewed during source curation;004/005/011/012 original1434x773 were independently re-viewed for these timing cuts. No encoded frames exist or were reviewed here.',
             'No human listening or subjective naturalness approval is inferred from exact text or PCM energy.']}
    return out,'\n\n'.join(blocks)+'\n',qa

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write-proposed',action='store_true');p.add_argument('--ffmpeg',type=Path);a=p.parse_args()
    proposed,text,original=prepare()
    if a.write_proposed:
        assert a.ffmpeg and a.ffmpeg.is_file() and not DIRECTORY.exists(),'Use real FFmpeg and a NEW output directory.'
        DIRECTORY.mkdir(parents=True)
        derived=DIRECTORY/(NAME+'.derived114.srt');corrected=DIRECTORY/(NAME+'.derived114.corrected.srt');report=DIRECTORY/(NAME+'.derived114.actual.qa.json')
        derived.write_text(text)
        from qa_narration import audit
        result=audit(SOURCES/BASE/(NAME+'.narrated-source.json'),SOURCES/AUDIO,derived,corrected,report,str(a.ffmpeg),FROZEN)
        assert result['passed'] and not result['alignment']['text_changes'] and result['silent_raw_cues']==result['silent_corrected_cues']==0
        assert result['audio']['decoded_samples']==original['audio']['decoded_samples'] and result['audio']['duration_seconds']==original['audio']['duration_seconds']
        assert len(load_cues(corrected))==114
        result['derived_caption_provenance']={'original_service_raw_cues':113,'original_service_raw_file':RAW.as_posix(),'original_service_raw_sha256':PINS[RAW],
            'original_actual_qa_sha256':PINS[ORIGINAL_QA],'raw_captions_field_denotes':'Separate proposed derived114input, not original113service export.',
            'whole_second_cuts':proposed['genuine_service_anchor_cuts'],'coalescence':proposed['coalescence'],'all_originals_preserved':True,'human_listening_approved':False}
        report.write_bytes(encoded(result))
        proposed['derived_audio_qa']={'file':str(report.relative_to(SOURCES)),'sha256':sha(report),'passed':True,'silent_cues':0,'minimum_cue_rms':result['minimum_raw_cue_rms']}
        proposed['derived_captions']={'file':str(corrected.relative_to(SOURCES)),'sha256':sha(corrected)}
        mapping=DIRECTORY/'correspondence.proposed.json';mapping.write_bytes(encoded(proposed))
        provenance={'schema_version':1,'kind':'source_only_certification_actual_audio_proposed114_derivation','created_at':datetime.now(timezone.utc).isoformat(),
            'source_frozen_sha256':FROZEN,'inputs':[{'file':p.as_posix(),'sha256':h} for p,h in PINS.items()],
            'recipe':{'file':str(Path(__file__).relative_to(SOURCES)),'sha256':sha(__file__)},
            'outputs':[{'file':str(p.relative_to(SOURCES)),'sha256':sha(p)} for p in [derived,corrected,report,mapping]],
            'complete_audio_decode':True,'derived_cues':114,'silent_cues':0,'speech_energy_is_not_listening_review':True,
            'listening_approved':False,'renderer_plan_created':False,'video_rendered':False,'canonical_or_ready_changed':False}
        (DIRECTORY/'provenance.json').write_bytes(encoded(provenance))
    print(json.dumps({'source_preflight':True,'scenes':12,'raw_cues':113,'proposed_cues':114,'sources':27,
        'screen_intervals':proposed['screen_intervals'],'whole_second_cuts':[122,308],
        'minimum_caption_seconds':min(c['duration_seconds'] for c in proposed['readability']),
        'maximum_caption_cps':max(c['characters_per_second'] for c in proposed['readability']),
        'derived_complete_pcm_qa_run':a.write_proposed,'listening_approved':False,'renderer_plan_created':False,'files_written':a.write_proposed}))

if __name__=='__main__':main()
