"""Retain the reviewed marker take01 correspondence against actual speech exports.

Fixed historical recipe, not automatic review. No canonical lesson is read;
all speech comes from the immutable narrated snapshot. Integer-second cuts are
bound to genuine Descript TXT anchors. Original audio/SRT/TXT remain unchanged.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from render_walkthrough import load_cues,words
from render_public_media import stamp
from verify_capture_evidence import instruction_scene_digest
NAME='core-map-markers'
FROZEN='ccd153d425239d73199b8d3a2b14ff0e7767fcb95e71cd564a76c9a2cd26c40c'
AUDIO='94e3a6f7bf40dde051ea36c1859cbcb426d063fe3361adb377ff3659cb66f676'
CORRECTED='5f5b20651bdf665b3e686b0b13d179cda3fe1f05d0817a950c07dd482a9e5d73'
TRANSCRIPT='56d049c74947e36667884f605b6117d871f1b0af3cd588d7e71e7933d73d21bd'
QA='dff23726112cbaa5f58f73be49e8deb9a990b150f88359b270f491e2e5376a72'
REVIEWED_AT='2026-10-27T20:50:48Z'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def retain(path,value):
    body=value if isinstance(value,str) else json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n'
    if path.exists() and path.read_text()!=body:raise ValueError('Refusing to overwrite different retained output: '+str(path))
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(body)


def build(root):
    s=root/'sources';base=s/'expansion/plans/core-map-markers-capture-freeze-20261027'
    spec=importlib.util.spec_from_file_location('marker_offline_preparation',s/'production/author_core_map_markers_take_01.py')
    offline=importlib.util.module_from_spec(spec);spec.loader.exec_module(offline)
    offline.build(root)  # Exact frozen35 JPEG/DOM inputs, scene words and required labels.
    voice=s/f'expansion/plans/{NAME}.narrated-source.json';assert digest(voice)==FROZEN
    lesson=json.loads(voice.read_text());freeze=json.loads((base/'freeze.json').read_text())
    manifest=json.loads((s/freeze['capture_manifest']).read_text())
    records={row['id']:copy.deepcopy(row) for row in manifest['screenshots']}
    def screen(number):return next(k for k in records if k.startswith(f'{number:03}-'))
    audio=s/f'expansion/audio/{NAME}.m4a';corrected=s/f'expansion/audio/{NAME}.corrected.srt'
    transcript=s/f'expansion/audio/{NAME}.one-second.txt';qa_path=s/f'expansion/audio/{NAME}.qa.json'
    assert digest(audio)==AUDIO and digest(corrected)==CORRECTED and digest(transcript)==TRANSCRIPT and digest(qa_path)==QA
    qa=json.loads(qa_path.read_text())
    assert qa['passed'] and qa['silent_raw_cues']==qa['silent_corrected_cues']==0
    assert qa['lesson']['sha256']==FROZEN and qa['audio']['sha256']==AUDIO and qa['audio']['full_decode']=='passed'
    raw=load_cues(corrected);assert len(raw)==110
    text=transcript.read_text()
    ranges=[(1,1,8),(2,5,24),(6,6,8),(7,10,23),
      (11,13,2),(14,19,1),(20,23,3),(24,29,6),(30,31,7),(32,32,8),(33,34,25),
      (35,37,14),(38,41,9),(42,42,10),(43,45,13),
      (46,46,10),(47,49,11),(50,51,12),(52,52,14),(53,53,15),(54,54,16),(55,58,32),
      (59,59,18),(60,61,20),(62,63,17),(64,64,19),(65,69,18),
      (70,70,19),(71,73,21),(74,74,22),(75,78,23),
      (79,82,24),(83,83,25),(84,85,26),(86,89,27),
      (90,90,16),(91,92,33),(93,93,34),(94,98,35),(99,99,26),
      (100,101,28),(102,102,29),(103,104,30),(105,110,31)]
    mapping={}
    for first,last,number in ranges:
      for n in range(first,last+1):assert n not in mapping;mapping[n]=screen(number)
    assert set(mapping)==set(range(1,111))
    refs={
      1:{'Mapping':'Mapping','Map Icon Legend':'Map Icon Legend'},
      11:{'Department Types':'Department Types','Structure Fire':'Structure Fire'},
      12:{'Map Icon':'Map Icon','Custom icon':'Custom icon'},14:{'Choose File':'Choose File'},15:{'Icon guidelines':'Icon guidelines'},
      18:{'Preview':'Preview','Light map':'Light map','Dark map':'Dark map','In a list':'In a list'},20:{'Update':'Update'},
      21:{'Showing the current custom icon.':'Showing the current custom icon'},23:{'Priority map icons':'Priority map icons'},
      24:{'Urgent':'Urgent'},25:{'Priority':'Priority','Map color':'Map color','Default':'Default'},26:{'call-emergency.png':'call-emergency'},
      27:{'Urgent':'Urgent'},29:{'Upload':'Upload'},30:{'Icon saved.':'Icon saved','Uploaded icon':'Uploaded icon'},31:{'Remove':'Remove'},
      32:{'TRAINING — Warehouse alarm':'Warehouse alarm','Mapping':'Mapping'},33:{'Routine':'Routine','Emergency':'Emergency'},
      35:{'Units':'Units','Reserve Engine 51':'Reserve Engine 51'},36:{'Type':'Type','Engine':'Engine','Status':'Status','Out of Service':'Out of Service'},
      37:{'Engine 51':'Engine 51','Released':'Released'},38:{'Engine':'Engine'},39:{'Actions (Custom Unit Statuses)':'Actions','Standard Actions':'Standard Actions'},
      40:{'Custom icon':'Custom icon'},41:{'Light map':'light','Dark map':'dark','In a list':'list','Update':'Update'},
      42:{'Showing the current custom icon.':'current saved icon'},43:{'Reserve Engine 51':'reserve unit'},
      46:{'Status map icons':'Status map icons','Engine':'Engine'},47:{'Available':'Available'},48:{'Map color':'Map color'},
      50:{'Upload':'Upload','Icon saved.':'Icon saved'},51:{'Map icons for Engine':'Engine units','Available':'Available'},
      52:{'Set Status':'Set Status'},53:{'Destination':'Destination','None':'None','Note':'Note','Save':'Save'},54:{'Units':'Units','Available':'Available'},
      59:{'Personnel Roles':'Personnel Roles','Officer':'Officer'},60:{'Matthew Casey':'Matthew Casey','Stella Kidd':'Stella Kidd','Christopher Herrmann':'Christopher Herrmann'},
      62:{'Custom icon':'Custom icon'},63:{'Preview':'Preview','Save':'Save'},64:{'Showing the current custom icon.':'Showing the current custom icon'},
      65:{'Personnel Roles':'Personnel Roles','Role order:':'Role order'},66:{'Role order:':'this order'},67:{'Officer':'Officer'},68:{'Save order':'Save order'},
      70:{'Officer':'Officer','Status map icons':'Status map icons'},71:{'Standing By':'Standing By'},
      74:{'Upload':'Upload','Icon saved.':'Icon saved','Uploaded icon':'Uploaded icon','Remove':'Remove'},75:{'Matthew Casey':'Matthew Casey'},
      79:{'Map Icon Legend':'Map Icon Legend'},83:{'Structure Fire':'Structure Fire'},84:{'Engine':'Engine','Available':'Available'},86:{'Officer':'Officer'},87:{'On Unit':'On Unit'},
      90:{'Set Status':'Set Status'},91:{'Out of Service':'Out of Service','Destination':'Destination','None':'None'},92:{'Note':'Note','Save':'Save'},
      93:{'Units':'Units','Out of Service':'Out of Service','Engine 51':'Engine 51','Released':'Released'},
      100:{'Map icons for Structure Fire':"Structure Fire's",'Urgent':'Urgent'},101:{'Remove':'Remove'},
      102:{'Icon removed.':'Icon removed','Uploaded icon':'Uploaded icon','None':'None'},
    }
    def entry(cue,number,ref=None,orig=None):
      ref=ref or {};return dict(cue,screenshot_id=screen(number),required_labels=list(ref),spoken_references=ref,instructional=bool(ref),original_cues=orig or [])
    expanded=[];provenance=[];n=1
    while n<=110:
      cue=raw[n-1]
      if n==6:
        merged=' '.join(c['text'] for c in raw[5:8]);one,sep,rest=merged.partition('Reserve Engine 51 and ');two,sep2,three=rest.partition('Matthew Casey.')
        assert sep and sep2 and not two and '[00:00:20] Reserve Engine' in text and '[00:00:22] Matthew Casey.' in text
        expanded.extend([
          entry(dict(start=cue['start'],end=20.0,text=one.strip()),8,{'TRAINING — Warehouse alarm':'Warehouse alarm'},[6]),
          entry(dict(start=20.0,end=22.0,text=sep.strip()),13,{'Reserve Engine 51':'Reserve Engine 51'},[6,7]),
          entry(dict(start=22.0,end=raw[7]['end'],text=(sep2+three).strip()),23,{'Matthew Casey':'Matthew Casey'},[7,8]),
        ])
        provenance.append({'original_cues':[6,7,8],'outer_start':cue['start'],'outer_end':raw[7]['end'],'cuts':[{'seconds':20.0,'anchor':'[00:00:20] Reserve Engine'},{'seconds':22.0,'anchor':'[00:00:22] Matthew Casey.'}],'recorded_internal_pauses_seconds':[0.029,0.410],'reason':'Preserve exact names/order while avoiding a half-second Reserve fragment and a subsecond Casey fragment. Joined displayed captions bridge only the two recorded short pauses; actual outer bounds and audio are unchanged.'})
        n=9;continue
      if n==52:
        before,sep,after=cue['text'].partition('choose Available,');assert sep and '[00:02:50] choose' in text and cue['start']<170<cue['end']
        expanded.extend([entry(dict(cue,end=170.0,text=before.strip()),14,{'Set Status':'Set Status'},[52]),
                         entry(dict(cue,start=170.0,text=sep+after),15,{'Available':'Available'},[52])])
        provenance.append({'original_cues':[52],'cut_seconds':170.0,'before_exact_phrase':'choose Available,','anchor':'[00:02:50] choose','reason':'Keep the real Set Status entry button visible before the foreground status dialog. The chosen option and remaining form persist through cue53.'})
        n+=1;continue
      if n==96:
        merged=' '.join(c['text'] for c in raw[95:98]);before,sep,after=merged.partition('matching the legend.');assert sep and '[00:05:29] matching the legend.' in text
        expanded.extend([entry(dict(start=cue['start'],end=329.0,text=before.strip()),35,{},[96,97]),
                         entry(dict(start=329.0,end=raw[97]['end'],text=sep+after),26,{},[97,98])])
        provenance.append({'original_cues':[96,97,98],'outer_start':cue['start'],'outer_end':raw[97]['end'],'cuts':[{'seconds':329.0,'anchor':'[00:05:29] matching the legend.'}],'recorded_internal_pauses_seconds':[0.0,0.360],'reason':'Keep the restored named map through unavailable badge, then hold the corresponding legend through the following normal-controls explanation. Joining the genuine outer ranges avoids a subsecond legend caption; audio unchanged.'})
        n=99;continue
      if n==104:
        before,sep,after=cue['text'].partition('the named Warehouse alarm.');assert sep and '[00:05:54] the named Warehouse' in text
        expanded.extend([entry(dict(cue,end=354.0,text=before.strip()),30,{},[104]),
                         entry(dict(cue,start=354.0,text=sep+after),31,{'TRAINING — Warehouse alarm':'Warehouse alarm'},[104])])
        provenance.append({'original_cues':[104],'cut_seconds':354.0,'before_exact_phrase':'the named Warehouse alarm.','anchor':'[00:05:54] the named Warehouse','reason':'Legend already persists through cue103; its total hold exceeds three seconds. Cut to the real named call before its name is spoken, then retain the map for the closing explanation.'})
        n+=1;continue
      expanded.append(dict(cue,screenshot_id=mapping[n],required_labels=list(refs.get(n,{})),spoken_references=refs.get(n,{}),instructional=bool(refs.get(n)),original_cues=[n]));n+=1
    assert len(expanded)==111
    assert words(' '.join(c['text'] for c in expanded))==words(' '.join(sc['narration'] for sc in lesson['scenes']))
    assert all(c['end']-c['start']>=1.0 for c in expanded)
    used={c['screenshot_id'] for c in expanded};assert len(used)==33
    records={k:v for k,v in records.items() if k in used}
    capture_path=s/f'expansion/plans/{NAME}-take-01.captures.json'
    retain(capture_path,{'app':'Core','screenshots':list(records.values()),'source_manifest':freeze['capture_manifest'],'source_manifest_sha256':freeze['capture_manifest_sha256'],'scope':'33 unchanged actual images from the reviewed35-source marker subset. Source004/005 remain supplemental; no raw image, source labels or frozen narration edited.'})
    caption_path=s/f'expansion/audio/{NAME}-take-01-screen-cuts.srt'
    retain(caption_path,''.join(f"{i}\n{stamp(c['start'],True)} --> {stamp(c['end'],True)}\n{c['text']}\n\n" for i,c in enumerate(expanded,1)))
    retain(s/f'expansion/audio/{NAME}-take-01-screen-cuts-provenance.json',{'lesson_sha256':FROZEN,'audio_sha256':AUDIO,'source_corrected_srt_sha256':CORRECTED,'genuine_one_second_txt_sha256':TRANSCRIPT,'original_cues':110,'derived_cues':111,'integer_second_cuts':[20,22,170,329,354],'precision':'Actual Descript one-second TXT export; integer-second granularity, no interpolated or finer word timing.','edits':provenance,'exact_words_order_and_untouched_other_bounds':True})
    groups=[];position=0
    for authored in lesson['scenes']:
      expected=words(authored['narration']);actual=[];entries=[]
      while len(actual)<len(expected):
        c=expanded[position];position+=1;actual+=words(c['text']);entries.append(dict(c,cue=position))
      assert actual==expected,authored['id'];groups.append((authored,entries))
    assert position==len(expanded)
    duration=qa['audio']['duration_seconds'];scenes=[]
    for i,(authored,entries) in enumerate(groups):
      start=0 if i==0 else entries[0]['start'];end=duration if i==len(groups)-1 else groups[i+1][1][0]['start'];screens=[]
      for j,c in enumerate(entries):
        at=start if j==0 else c['start']
        if not screens or screens[-1]['screenshot_id']!=c['screenshot_id']:
          if screens:screens[-1]['end']=at
          screens.append({'screenshot_id':c['screenshot_id'],'start':at,'end':end})
      built={'id':authored['id'],'title':authored['title'],'kind':'operational','start':start,'end':end,'visual_required_labels':authored['required_labels'],'screens':screens,'captions':entries}
      review={'passed':True,'reviewer':'Codex','reviewed_at':REVIEWED_AT,'correspondence_reviewed':True,'no_unseen_controls':True,'mapping_sha256':instruction_scene_digest(built,records),'method':'All35 original images personally viewed at original resolution, with foreground-only literal labels and pixel privacy review. All110 source cues/111 derived cues mapped manually to33 actual screens. Five genuine integer-second cuts and two documented short-pause caption joins preserve every spoken word. Unit state saves are distinct from separately declared simulated station-location setup; saved/removal/fallback views remain distinct. The map-to-previous-row descriptions are comparisons, not unseen actions. Actual encoded frame review remains pending.'}
      scenes.append({'id':authored['id'],'start':start,'end':end,'screens':screens,'captions':[{k:c[k] for k in ('cue','screenshot_id','required_labels','spoken_references','instructional')} for c in entries],'instruction_review':review})
    holds=[{'scene':sc['id'],**x,'duration_seconds':round(x['end']-x['start'],3)} for sc in scenes for x in sc['screens']]
    assert min(x['duration_seconds'] for x in holds)>=2.0
    retain(s/f'expansion/plans/{NAME}-take-01-correspondence-review.json',{'lesson_sha256':FROZEN,'audio_sha256':AUDIO,'source_review':'Original-resolution35-JPEG review and exact literal/source correspondence retained in immutable capture subset.','raw_cues':110,'derived_cues':111,'selected_images':33,'screen_intervals':len(holds),'minimum_screen_hold_seconds':min(x['duration_seconds'] for x in holds),'minimum_caption_seconds':min(c['end']-c['start'] for c in expanded),'holds':holds,'short_captions_under_1_5_seconds':[{'cue':i,'duration_seconds':round(c['end']-c['start'],3),'text':c['text']} for i,c in enumerate(expanded,1) if c['end']-c['start']<1.5],'timing_provenance':f'expansion/audio/{NAME}-take-01-screen-cuts-provenance.json','limits':['This records actual source/cue correspondence, not encoded-frame or browser playback approval.','Subtitles joined across documented real short pauses retain source outer bounds and exact speech order. No operation timing or within-second word precision is inferred.']})
    plan={'schema_version':1,'lesson_id':NAME,'duration_seconds':duration,'instruction_mapping':'reviewed_scene_coverage','display_context':'TRAINING ONLY · simulated station fixtures',
      'narration':{'file':audio.relative_to(s).as_posix(),'sha256':AUDIO,'kind':'approved_natural_narration','approval':{'reviewer':'Codex','reviewed_at':REVIEWED_AT,'sha256':AUDIO,'complete_natural_narration':True,'method':'Full actual923-word/ten-paragraph stock narration decoded; every original/corrected cue passed energy and exact frozen-script QA. Parent verified ten actual generated WAVs and established Lulu stock speaker on all ten paragraphs. This is concrete automated/source verification, not claimed human listening.','qa_file':qa_path.relative_to(s).as_posix(),'qa_sha256':QA}},
      'captions':{'file':caption_path.relative_to(s).as_posix(),'sha256':digest(caption_path),'kind':'speech_timed_srt','approval':{'reviewer':'Codex','reviewed_at':REVIEWED_AT,'sha256':digest(caption_path),'audio_sha256':AUDIO,'speech_timing_reviewed':True,'method':'Actual source SRT bounds plus five genuine Descript integer-second cuts; two documented joins bridge only recorded short pauses and preserve outer source bounds, exact words and order. No estimated operation or interpolated word times.','timing_provenance':f'expansion/audio/{NAME}-take-01-screen-cuts-provenance.json'}},
      'capture_manifests':[{'file':capture_path.relative_to(s).as_posix(),'sha256':digest(capture_path)}],
      'screenshot_reviews':{ident:{'reviewer':'Codex','reviewed_at':row['capture_review']['reviewed_at'],'sha256':row['sha256'],'application_visible':True,'labels_legible':True,'no_errors':True,'method':row['capture_review']['method']} for ident,row in records.items()},
      'scenes':scenes,'source_freeze':{'lesson_sha256':FROZEN,'spoken_words':923,'voice_source':voice.relative_to(s).as_posix(),'capture_freeze_sha256':digest(base/'freeze.json'),'untimed_sequence_sha256':digest(base/'untimed-screen-sequence.json'),'source_images_reviewed':35,'source_images_used':33},
      'limitations':['Every narrated word, original source pixel and all six sector companions remain unchanged. Encoded-frame and real browser playback gates remain required.','Normal status forms changed only the disposable reserve unit. Both marker positions are declared simulated station status-location setup, never device GPS or provider operations.','Urgent is the actual priority despite the file name call-emergency.png. Its replacement was removed; other bases/Available/StandingBy replacements remain.','Original three active calls remain unchanged; Engine51 Released and Reserve Out of Service are distinct named states.','This author recipe reads the immutable narrated-source snapshot, never canonical publication flags or private editor/download metadata.']}
    path=s/f'expansion/plans/{NAME}-take-01.plan.json';retain(path,plan)
    print(json.dumps({'plan':path.relative_to(root).as_posix(),'sha256':digest(path),'scenes':10,'images':33,'screen_intervals':len(holds),'raw_cues':110,'derived_cues':111,'duration_seconds':duration},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=ROOT);build(parser.parse_args().root.resolve())
