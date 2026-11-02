"""Retain proposed99 Training cues and full actual-audio QA without approval.

Three cuts use genuine service whole-second word markers. The short raw69 tail
is coalesced with adjacent raw70 on the same catalog image, ending at raw70's
actual end. Original97 cues/audio/frozen source/scaffold remain unchanged.
No listening review, renderer plan, canonical readiness or publication is made.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import textwrap
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
SOURCES=ROOT/'sources'
NAME='core-training-administration'
AUTHOR=SOURCES/'production/author_core_training_administration_take_01.py'
DIRECTORY=SOURCES/'expansion/plans/core-training-administration-take-01-proposed-derived-20261028'
AUDIO=SOURCES/'expansion/audio'/ (NAME+'.m4a')
ORIGINAL_QA=SOURCES/'expansion/audio'/ (NAME+'.actual.qa.json')
CORRECTED97=SOURCES/'expansion/audio'/ (NAME+'.srt')
PINS={AUTHOR:'a7616f347beaaaf70050d14266b04b8ad9df24670c7b6d5a451a053a5ab1323a',
      AUDIO:'88b193010ee569682b28a56e69e76e6c1225b04a4e5b94c3665e8385c652b6a3',
      ORIGINAL_QA:'816072238731fa36b596192bf7f9ebb4b047be419a1a16d2d9ba0ecb204428e1',
      CORRECTED97:'65709fd026ed456cee7bd30d6f270c3dd3ab7c229c1aad7675aed35099dfa0aa'}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def encoded(x):return (json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()
def stamp(seconds):
    value=round(seconds*1000)
    return f'{value//3600000:02}:{value//60000%60:02}:{value//1000%60:02},{value%1000:03}'

def prepare():
    for path,digest in PINS.items():assert sha(path)==digest,'Changed actual input: '+path.name
    spec=importlib.util.spec_from_file_location('frozen_training_actual_source',AUTHOR);author=importlib.util.module_from_spec(spec);spec.loader.exec_module(author)
    source=author.prepare();raw=source['raw_cue_correspondence'];assert len(raw)==97
    corrected=author.load_cues(CORRECTED97)
    for a,b in zip(raw,corrected):assert (a['start'],a['end'],author.words(a['text']))==(b['start'],b['end'],author.words(b['text']))
    qa=json.loads(ORIGINAL_QA.read_text());assert qa['passed'] and not qa['issues'] and not qa['possible_speech_gaps']
    assert qa['audio']['full_decode']=='passed' and qa['audio']['sha256']==PINS[AUDIO]
    assert qa['lesson']['sha256']==author.FROZEN and qa['raw_captions']['sha256']==author.RAW
    assert qa['raw_captions']['cues']==qa['corrected_captions']['cues']==97 and qa['silent_raw_cues']==qa['silent_corrected_cues']==0
    manifest=json.loads((SOURCES/author.BASE/(NAME+'.captures.reviewed.json')).read_text());rows={int(r['id'][:3]):r for r in manifest['screenshots']}
    anchors,_=author.service_anchors((SOURCES/author.ANCHORS_FILE).read_text());splits={s['cue']:s for s in author.SPLITS}
    expanded=[];operations=[]
    for number,cue in enumerate(raw,1):
        if number==70:continue
        if number not in splits:
            expanded.append({k:cue[k] for k in ['start','end','text','screenshot_id','required_labels','spoken_references']}|{'raw_cues':[number]})
            continue
        split=splits[number];proven=author.check_anchor(split,raw,anchors);at=float(split['at_seconds'])
        for side in ['before','after']:
            text=split[side+'_text'];refs=split[side+'_references'];origins=[number]
            start=cue['start'] if side=='before' else at
            end=at if side=='before' else cue['end']
            if number==69 and side=='after':
                following=raw[69]
                assert following['raw_cue']==70 and following['screenshot_id']==rows[16]['id']
                assert author.words(text)+author.words(following['text'])==author.words('returned catalog. For Boden, this exercise now shows Training Complete.')
                text=text+' '+following['text'];end=following['end'];origins=[69,70]
                refs={'Trainings':'catalog','Training Complete':'Training Complete'}
            row=rows[split[side]];author.references({'text':text},refs,row)
            expanded.append({'start':start,'end':end,'text':text,'screenshot_id':row['id'],'required_labels':list(refs),'spoken_references':refs,'raw_cues':origins})
        operations.append({'raw_cue':number,'service_marker_seconds':at,'global_word_offset':proven['global_word_offset'],'before_text':split['before_text'],'after_text':split['after_text'],'precision':'Genuine whole-second service marker, not interpolated or millisecond word precision.'})
    for index,entry in enumerate(expanded,1):entry.update(cue=index,instructional=bool(entry['required_labels']))
    assert len(expanded)==99 and author.words(' '.join(c['text'] for c in expanded))==author.words(' '.join(c['text'] for c in raw))
    merged=next(c for c in expanded if c['raw_cues']==[69,70]);assert merged['start']==233.0 and merged['end']==237.719
    assert len(merged['text'].split())==10 and round(merged['end']-merged['start'],3)==4.719
    scenes=[]
    for index,old in enumerate(source['scene_ranges']):
        entries=[c for c in expanded if old['first_raw_cue']<=c['raw_cues'][0]<=old['last_raw_cue']]
        first=0 if index==0 else entries[0]['start'];last=qa['audio']['duration_seconds'] if index==9 else raw[source['scene_ranges'][index+1]['first_raw_cue']-1]['start']
        spans=[];active=entries[0]['screenshot_id'];opening=first
        for entry in entries:
            if entry['screenshot_id']!=active:
                spans.append({'capture_ref':active,'actual_start':opening,'actual_end':entry['start']});active=entry['screenshot_id'];opening=entry['start']
        spans.append({'capture_ref':active,'actual_start':opening,'actual_end':last})
        scenes.append(dict(old,derived_cues=[c['cue'] for c in entries],source_spans=spans))
    blocks=[]
    for c in expanded:
        lines=textwrap.wrap(c['text'],width=42,break_on_hyphens=False,break_long_words=False)
        if len(lines)>2:lines=textwrap.wrap(c['text'],width=48,break_on_hyphens=False,break_long_words=False)
        assert len(lines)<=2,'Retain real boundaries; review actual layout rather than guess a cut.'
        blocks.append(f"{c['cue']}\n{stamp(c['start'])} --> {stamp(c['end'])}\n"+'\n'.join(lines))
    proposed={'kind':'proposed_training_actual_audio_source_caption_correspondence','lesson_id':NAME,'source_frozen_sha256':author.FROZEN,'original_raw_cues':97,'proposed_derived_cues':99,
      'audio':{'file':str(AUDIO.relative_to(SOURCES)),'sha256':PINS[AUDIO],'original_full_decode_duration_seconds':qa['audio']['duration_seconds']},
      'genuine_service_anchor_cuts':operations,'coalescence':{'raw_cue_tail':69,'adjacent_raw_cue':70,'same_actual_catalog_image':rows[16]['id'],'old_tail_seconds':0.750,'derived_readable_span_seconds':4.719,'words':10,'derived_text':merged['text'],'start_source':'Actual service233second word marker before returned.','end_source':'Unchanged raw70actualend237.719.','intervening_actual_speech_gap_seconds':round(raw[69]['start']-raw[68]['end'],3),'gap_note':'The caption remains readable across the actual0.420second gap; no speech or word time is inserted.'},
      'scenes':scenes,'cue_correspondence':expanded,'listening_approval':'Pending actual full lesson-specific user listening review; not inferred from technical checks.',
      'renderer_plan_created':False,'narration_approved':False,'canonical_ready':False,'publication_approved':False,
      'limits':source['limitations'][:-1]+['The0.750second tail is replaced only by coalescing adjacent actual words on the same catalog image; final source word order is unchanged.','Original97raw/correctedcaptions and original97cueQA remain immutable. This is a proposed99cue derivative and separateQA, not a final approved renderer plan.']}
    return author,proposed,'\n\n'.join(blocks)+'\n',qa

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write-proposed',action='store_true');p.add_argument('--ffmpeg',type=Path);args=p.parse_args()
    author,proposed,text,original=prepare()
    if args.write_proposed:
        assert args.ffmpeg and not DIRECTORY.exists(),'Provide FFmpeg and a NEW derivative directory; retain every earlier input.'
        DIRECTORY.mkdir(parents=True)
        derived=DIRECTORY/(NAME+'.derived99.srt');checked=DIRECTORY/(NAME+'.derived99.corrected.srt');report=DIRECTORY/(NAME+'.derived99.actual.qa.json')
        derived.write_text(text)
        sys.path.insert(0,str(ROOT/'scripts'));from qa_narration import audit
        result=audit(SOURCES/author.BASE/(NAME+'.narrated-source.json'),AUDIO,derived,checked,report,str(args.ffmpeg),author.FROZEN)
        assert result['passed'] and not result['alignment']['text_changes'] and result['silent_raw_cues']==result['silent_corrected_cues']==0
        assert result['audio']['decoded_samples']==original['audio']['decoded_samples'] and result['audio']['duration_seconds']==original['audio']['duration_seconds']
        assert len(author.load_cues(checked))==99
        # Clarify the generic QA tool's field names without changing any signal,
        # threshold, alignment result or pass/fail decision.
        result['method']='Complete actual M4A decode to mono48kHz16bitPCM; every proposed99input and corrected speech cue measured; exact unchanged frozen words. Three added boundaries are genuine service whole-second markers; raw69tail and raw70 are coalesced on one actual catalog image to raw70actualend.'
        result['derived_caption_provenance']={'original_raw97_file':author.RAW_FILE.as_posix(),'original_raw97_sha256':author.RAW,'original_actual97_qa_sha256':PINS[ORIGINAL_QA],'raw_captions_field_denotes':'Proposed derived99input, not the original97service export.','originals_preserved':True,'coalescence':proposed['coalescence'],'service_anchor_cuts':proposed['genuine_service_anchor_cuts']}
        report.write_bytes(encoded(result))
        proposed['derived_audio_qa']={'file':str(report.relative_to(SOURCES)),'sha256':sha(report),'passed':True,'full_decode':'passed','silent_cues':0}
        proposed['derived_captions']={'file':str(checked.relative_to(SOURCES)),'sha256':sha(checked)}
        mapping=DIRECTORY/'correspondence.proposed.json';mapping.write_bytes(encoded(proposed))
        provenance={'kind':'training_actual_audio_proposed99caption_derivation_qa_only','created_at':datetime.now(timezone.utc).isoformat(),'source_frozen_sha256':author.FROZEN,
          'pinned_original_inputs':[{'file':str(path.relative_to(SOURCES)),'sha256':digest} for path,digest in PINS.items()],
          'raw97_preserved':{'file':author.RAW_FILE.as_posix(),'sha256':author.RAW},'genuine_one_second_export':{'file':author.ANCHORS_FILE.as_posix(),'sha256':author.ANCHORS},
          'derived_input':{'file':str(derived.relative_to(SOURCES)),'sha256':sha(derived)},'derived_corrected':{'file':str(checked.relative_to(SOURCES)),'sha256':sha(checked)},
          'actual_qa':{'file':str(report.relative_to(SOURCES)),'sha256':sha(report)},'proposed_correspondence':{'file':str(mapping.relative_to(SOURCES)),'sha256':sha(mapping)},
          'coalescence':proposed['coalescence'],'genuine_service_anchor_cuts':proposed['genuine_service_anchor_cuts'],'speech_energy_qa':'Full decode passed;0silent derived cues; energy does not establish subjective naturalness or word recognition.',
          'listening_approved':False,'renderer_plan_created':False,'video_rendered':False,'publication_approved':False}
        (DIRECTORY/'provenance.json').write_bytes(encoded(provenance))
        print(json.dumps({'passed_proposed99_qa':True,'actual_audio_seconds':result['audio']['duration_seconds'],'decoded_samples':result['audio']['decoded_samples'],'derived_cues':99,'silent_cues':0,'minimum_cue_rms':result['minimum_raw_cue_rms'],'listening_approved':False,'renderer_plan_created':False}))
    else:print(json.dumps({'source_preflight':True,'actual_raw_cues':97,'proposed_cues':99,'coalesced_caption_seconds':4.719,'listening_approved':False,'renderer_plan_created':False,'files_written':False}))

if __name__=='__main__':main()
