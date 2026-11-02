"""Propose Personnel actual-source caption timing; never assemble or render.

Default is read-only. --write-proposed requires a NEW directory and real FFmpeg
to decode the complete approved audio and measure every derived cue. Only the
genuine service whole-second markers below may split words. The original112
actualv2service cues, audio, frozen learner words and reviewed source pairs are retained.
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
NAME = 'core-personnel-administration'
BASE = Path('expansion/plans') / (NAME + '-capture-freeze-20261028')
DIRECTORY = SOURCES / 'expansion/plans/core-personnel-administration-take-01-proposed-derived-20261028-v2'
AUDIO = Path('expansion/audio') / (NAME + '.m4a')
RAW = Path('expansion/audio') / (NAME + '-generated-20261028-v2.raw.srt')
CORRECTED = Path('expansion/audio') / (NAME + '.srt')
TEXT = Path('expansion/audio') / (NAME + '-generated-20261028-v2.raw.txt')
ANCHORS = Path('expansion/audio') / (NAME + '-generated-20261028-v2.one-second.txt')
ORIGINAL_QA = Path('expansion/audio') / (NAME + '.actual.qa.json')
LISTENING = Path('expansion/audio') / (NAME + '.listening-review.json')
FROZEN = 'e044a6466848e9b8c14c7a3b8711cabad0c87c1e9b48c7f7e74476b09b0598b8'
PINS = {
    Path('expansion/plans/core-personnel-administration-capture-freeze-20261028/core-personnel-administration.narrated-source.json'): 'e044a6466848e9b8c14c7a3b8711cabad0c87c1e9b48c7f7e74476b09b0598b8',
    Path('expansion/plans/core-personnel-administration-capture-freeze-20261028/core-personnel-administration.captures.reviewed.json'): 'b06bbf5c331541b5fd20a4f520c0edc750f7bd50f04af4df2e65895dc8cb66d0',
    Path('expansion/plans/core-personnel-administration-capture-freeze-20261028/core-personnel-administration.screen-sequence.json'): 'c2e476a5f078a8aee72b6e41f70a21b443d97df7f52fa70db68c72e8e09153b3',
    Path('expansion/plans/core-personnel-administration-capture-freeze-20261028/source-hashes.json'): '770c4d93254de9170db090fa392f844166326b38df7da2604f4d5868a7f247b5',
    Path('expansion/plans/core-personnel-administration-capture-freeze-20261028/source-evidence.json'): '72c6786690ea7ca38f0228b0ba9a0a97bab1a356c79e66e0d37282fa94d20292',
    Path('expansion/audio/core-personnel-administration-generated-20261028-v2.raw.srt'): 'f2d115e7e7031dca0e9b6f11c86a764065a521e54eb8739b5f2770ed3f813dcc',
    Path('expansion/audio/core-personnel-administration-generated-20261028-v2.raw.txt'): 'ebb2be3f66e3ff26384d47fd935e3d0ff545114ef87c8e38d8705a94ab33d884',
    Path('expansion/audio/core-personnel-administration-generated-20261028-v2.one-second.txt'): '38575cf18c30c5087e16381b5cc4e0361b960a59a8951701bda0b92ff8726874',
    Path('expansion/audio/core-personnel-administration.srt'): '934e6f7c4b68b077133c5ecff4dcdc3f1732c26ab110ac52d9c521e947b9e8ef',
    Path('expansion/audio/core-personnel-administration.m4a'): '13e0fa5d0dc5cb4cc2782e27ccfc058d18557addf0997b26887666c30954d32d',
    Path('expansion/audio/core-personnel-administration.actual.qa.json'): 'd916c8b8323b84772d67d9ede23a851d097c67ae295f4406107f800e826651ae',
    Path('expansion/audio/core-personnel-administration.listening-review.json'): '025a4cd0d6c4729f2a824739f79d6a805fcfd7dd789dea616693a0aeae33f25b',
}
UTILITY = SOURCES / 'production/qa_core_certification_proposed_captions_20261028.py'
UTILITY_SHA = '6c24c31946717f27f06a6829e32846dbb2420fc894f5d980b245d3a8b9441594'
SCREEN_STARTS = {1: 1,
 6: 2,
 11: 2,
 12: 3,
 13: 4,
 20: 5,
 23: 5,
 24: 6,
 25: 6,
 26: 16,
 28: 6,
 29: 7,
 32: 8,
 34: 8,
 35: 10,
 37: 10,
 39: 11,
 41: 11,
 42: 12,
 47: 10,
 48: 13,
 51: 14,
 54: 15,
 57: 1,
 58: 19,
 65: 19,
 66: 20,
 67: 21,
 73: 21,
 74: 22,
 78: 23,
 84: 23,
 85: 24,
 87: 25,
 93: 23,
 94: 28,
 95: 28,
 96: 28,
 97: 27,
 102: 28,
 105: 23}
SPLITS = [{'raw_cue': 23,
  'at_seconds': 72,
  'before_text': 'Use Save, then',
  'after_text': 'find the new role at the end of the catalog.',
  'before': 5,
  'after': 6,
  'before_references': {'Save': 'Save'},
  'after_references': {'TRAINING ONLY - Community response navigator': 'new role'},
  'reason': 'Actual Save control precedes the returned new role catalog row.'},
 {'raw_cue': 25,
  'at_seconds': 82,
  'before_text': 'Choose View on the new row to read its',
  'after_text': 'stored name and full description.',
  'before': 6,
  'after': 16,
  'before_references': {'View': 'View'},
  'after_references': {'TRAINING ONLY - Community response navigator': 'stored name',
                       'Fictional Academy role for community paramedicine and mental health response coordination. Software training only; no professional qualification or system administration privilege.': 'description'},
  'reason': 'Actual new-row View control is retained before the fresh stored name/description.'},
 {'raw_cue': 34,
  'at_seconds': 112,
  'before_text': 'Save, then',
  'after_text': 'reopen the page and read the same single row.',
  'before': 8,
  'after': 9,
  'before_references': {'Save': 'Save'},
  'after_references': {'Saved.': 'single row'},
  'reason': 'Prepared requirement Save precedes actual Saved readback009; fresh leave/reopen010 begins on '
            'next original cue35.'},
 {'raw_cue': 95,
  'at_seconds': 314,
  'before_text': 'Choose its View control to see',
  'after_text': 'Casey listed under the stored description.',
  'before': 28,
  'after': 26,
  'before_references': {'View': 'View'},
  'after_references': {'Matthew Casey': 'Casey',
                       'Fictional Academy role for community paramedicine and mental health response coordination. Software training only; no professional qualification or system administration privilege.': 'stored '
                                                                                                                                                                                                               'description'},
  'reason': 'Saved role catalog View precedes its stored Casey member list.'},
 {'raw_cue': 96,
  'at_seconds': 319,
  'before_text': 'Open Required certifications from that role’s',
  'after_text': 'row to inspect Member eligibility.',
  'before': 28,
  'after': 27,
  'before_references': {'Required certifications': 'Required certifications'},
  'after_references': {'Member eligibility': 'Member eligibility'},
  'reason': 'Return to actual catalog Required certifications launcher before member eligibility readback.'}]
REFS = {1: {'Personnel': 'Personnel', 'Roles': 'roles', 'Staffing': 'staffing'},
 2: {'Status': 'status', 'State': 'administrative state'},
 3: {'Matthew Casey': 'Casey', 'Officer': 'Officer'},
 4: {'On Shift': 'On Shift', 'Standing By': 'Standing By', 'Admin': 'Admin'},
 5: {'Manage Roles': 'Manage Roles'},
 6: {'Description': 'description', 'Users In Role': 'member count'},
 7: {'Role order:': 'role order'},
 11: {'Add Role': 'Add Role'},
 12: {'Name': 'Name'},
 13: {'Description': 'Description'},
 15: {'Description': 'description'},
 17: {'Custom icon': 'Custom icon', 'No file chosen': 'remains empty'},
 20: {'Preview': 'previews', 'Light map': 'light', 'Dark map': 'dark'},
 21: {'In a list': 'list'},
 22: {'No file chosen': 'No custom file'},
 24: {'Users In Role': 'Users In Role', '0': 'zero'},
 28: {'Required certifications': 'Required certifications'},
 29: {'Enforcement is off: these requirements are informational until a department administrator turns on Warn only or Enforce in Settings': 'Off',
      'Member eligibility': 'Member eligibility'},
 30: {'This role has no members.': 'no members'},
 31: {'Add requirement': 'Add requirement'},
 32: {'Type': 'type', 'Mandatory': 'Mandatory', 'Any-of group': 'Any-of'},
 33: {'Any-of group': 'group blank',
      'Allow trainee': 'Allow trainee',
      'Grace override (days)': 'Grace override',
      '7': 'seven'},
 35: {'7': 'seven-day'},
 37: {'Certification types': 'Certification types'},
 39: {'TRN-REVIEW-20261028': 'complete code'},
 40: {'Records': 'record', 'Requirements': 'requirement', '1': 'one'},
 41: {'Edit': 'Edit'},
 42: {'Code': 'Code', 'A role requirement references this type, so its code can no longer change.': 'help'},
 44: {'Applies to': 'Applies to', 'Person': 'Person'},
 47: {'Add requirement': 'add a second'},
 48: {'Driver / operator': 'type'},
 49: {'Mandatory': 'Mandatory', 'Any-of group': 'group fields'},
 51: {'Any-of group': 'group number', '1': 'one'},
 53: {'Save': 'Save'},
 54: {'Any-of group': 'blank group', '7': 'seven-day'},
 57: {'Edit': 'Edit', 'Matthew Casey': 'Casey'},
 58: {'Roles': 'Roles', 'Officer': 'Officer'},
 60: {'Group': 'Group', 'Truck 81': 'Truck 81', 'Is Group Admin?': 'Is Group Admin'},
 65: {'Roles': 'Roles'},
 66: {'Community': 'Community', 'Officer': 'Officer'},
 67: {'Roles': 'selection'},
 68: {'Officer': 'Officer', 'TRAINING ONLY - Community response navigator': 'Community Response Navigator'},
 69: {'Officer': 'names', 'TRAINING ONLY - Community response navigator': 'names'},
 73: {'Roles': 'profile controls'},
 74: {'Department Admin': 'Department Admin', 'Disable User': 'Disable User'},
 75: {'Hide User': 'Hide User'},
 77: {'Save': 'Save'},
 78: {'Personnel': 'Personnel', 'Search:': 'search', 'Matthew Casey': 'Matthew Casey'},
 79: {'Officer': 'Officer', 'TRAINING ONLY - Community response navigator': 'coordination role'},
 80: {'Staffing': 'Staffing', 'On Shift': 'On Shift', 'Status': 'status', 'Standing By': 'Standing By'},
 81: {'Admin': 'Admin'},
 84: {'Edit': 'Edit'},
 85: {'Roles': 'role chips', 'Officer': 'Both', 'TRAINING ONLY - Community response navigator': 'Both'},
 86: {'Truck 81': 'Truck 81', 'Is Group Admin?': 'Is Group Admin'},
 87: {'Department Admin': 'Department Admin', 'Disable User': 'Disable'},
 88: {'Hide User': 'Hide User'},
 93: {'Manage Roles': 'Manage Roles'},
 94: {'Users In Role': 'member', '1': 'one'},
 97: {'Matthew Casey': 'Casey', 'Qualified': 'Qualified'},
 98: {'Enforcement is off: these requirements are informational until a department administrator turns on Warn only or Enforce in Settings': 'Off'},
 100: {'Member eligibility': 'software result'},
 102: {'TRAINING ONLY - Community response navigator': 'exercise coordination role'}}

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encoded(value): return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()

def utility():
    assert sha(UTILITY)==UTILITY_SHA,'Retain exact timing/reference utility; no silent rule changes.'
    spec=importlib.util.spec_from_file_location('retained_personnel_timing_utility',UTILITY)
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
    assert len(evidence['files'])==26
    for row in evidence['files']:
        assert row['repo']=='Core' and sha(ROOT.parents[2]/row['path'])==row['sha256'],'Changed cited Core source: '+row['path']
    raw=load_cues(SOURCES/RAW);corrected=load_cues(SOURCES/CORRECTED)
    assert len(raw)==len(corrected)==112 and len(lesson['scenes'])==12
    for a,b in zip(raw,corrected): assert (a['start'],a['end'],words(a['text']))==(b['start'],b['end'],words(b['text']))
    all_words=words(' '.join(s['narration'] for s in lesson['scenes']))
    anchors,anchor_words=helper.service_anchors((SOURCES/ANCHORS).read_text())
    assert len(all_words)==932
    assert all_words==words((SOURCES/TEXT).read_text())==words(' '.join(c['text'] for c in raw))==anchor_words
    qa=json.loads((SOURCES/ORIGINAL_QA).read_text());heard=json.loads((SOURCES/LISTENING).read_text())
    assert qa['passed'] and not qa['issues'] and not qa['possible_speech_gaps']
    assert qa['audio']['sha256']==PINS[AUDIO] and qa['audio']['full_decode']=='passed'
    assert qa['lesson']['sha256']==FROZEN and qa['silent_raw_cues']==qa['silent_corrected_cues']==0
    assert heard['complete_natural_narration'] is True and heard['lesson_sha256']==FROZEN and heard['audio_sha256']==PINS[AUDIO]
    assert heard['reviewer'] and heard['evidence']
    assert datetime.fromisoformat(heard['reviewed_at'].replace('Z','+00:00'))<=datetime.now(timezone.utc)
    rows={int(r['id'][:3]):r for r in manifest['screenshots']}
    assert len(rows)==26 and not {17,18}&set(rows)
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
        if number==76:continue
        if number in splits:
            split=splits[number]
            for side in ['before','after']:
                text=split[side+'_text'];refs=split[side+'_references'];row=rows[split[side]]
                helper.references(text,refs,row)
                expanded.append({'start':cue['start'] if side=='before' else float(split['at_seconds']),
                    'end':float(split['at_seconds']) if side=='before' else (raw[95]['start'] if number==95 else cue['end']),
                    'text':text,'screenshot_id':row['id'],'required_labels':list(refs),'spoken_references':refs,'raw_cues':[number]})
        else:
            out={k:cue[k] for k in ['start','end','text','screenshot_id','required_labels','spoken_references']}
            out['raw_cues']=[number]
            if number==75:
                follow=source_map[75];assert follow['screenshot_id']==cue['screenshot_id']
                out.update(end=follow['end'],text=cue['text']+' '+follow['text'],raw_cues=[75,76])
                helper.references(out['text'],out['spoken_references'],rows[22])
            expanded.append(out)
    assert len(expanded)==116 and words(' '.join(c['text'] for c in expanded))==all_words
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
        assert selected==list(dict.fromkeys(allowed)),(scene['id'],selected,allowed)
        union={label for r in rows.values() if r['id'] in selected for label in r['visible_labels']}
        assert set(scene['required_labels'])<=union,(scene['id'],set(scene['required_labels'])-union)
        assert any(c['instructional'] for c in entries),'Operational scene requires actual spoken field correspondence.'
        begin=0.0 if index==0 else entries[0]['start']
        end=qa['audio']['duration_seconds'] if index==11 else raw[raw_position]['start']
        spans=[];active=entries[0]['screenshot_id'];opening=begin
        for c in entries:
            if c['screenshot_id']!=active:
                spans.append({'capture_ref':active,'actual_start':opening,'actual_end':c['start']});active=c['screenshot_id'];opening=c['start']
        spans.append({'capture_ref':active,'actual_start':opening,'actual_end':end})
        assert [s['capture_ref'] for s in spans]==allowed,(scene['id'],spans,allowed)
        scenes.append({'scene_id':scene['id'],'first_raw_cue':start+1,'last_raw_cue':raw_position,
                       'derived_cues':[c['cue'] for c in entries],'required_labels':scene['required_labels'],
                       'source_spans':spans,'source_limits':scene['source_limits']})
    assert raw_position==112
    blocks=[];readability=[]
    for c in expanded:
        lines=textwrap.wrap(c['text'],width=42,break_on_hyphens=False,break_long_words=False)
        if len(lines)>2:lines=textwrap.wrap(c['text'],width=48,break_on_hyphens=False,break_long_words=False)
        assert len(lines)<=2,'Read actual text; do not invent a caption split.'
        duration=c['end']-c['start'];cps=len(c['text'])/duration
        assert duration>=1.0 and cps<=22.0,(c['cue'],duration,cps)
        readability.append({'cue':c['cue'],'raw_cues':c['raw_cues'],'duration_seconds':round(duration,3),'characters_per_second':round(cps,3),'lines':len(lines)})
        blocks.append(f"{c['cue']}\n{helper.stamp(c['start'])} --> {helper.stamp(c['end'])}\n"+'\n'.join(lines))
    coalescence={'raw_cues':[75,76],'same_actual_image':rows[22]['id'],'raw76_seconds':round(raw[75]['end']-raw[75]['start'],3),'start':raw[74]['start'],'end':raw[75]['end'],'derived_seconds':round(raw[75]['end']-raw[74]['start'],3),'text':next(c['text'] for c in expanded if c['raw_cues']==[75,76]),'method':'Adjacent unchanged words retain raw75 plus raw76 on the same unchanged admin-flags screenshot022, ending at genuine raw76 end254.380. No invented words or interpolated timing.'}
    out={'schema_version':1,'lesson_id':NAME,'status':'PROPOSED actual-audio source/caption plan for parent timing read; no final assembly/render',
         'source_frozen_sha256':FROZEN,'renderer_normalized_words':932,'space_delimited_source_words':926,
         'original_raw_cues':112,'proposed_derived_cues':116,'reviewed_actual_sources':26,
         'screen_intervals':sum(len(s['source_spans']) for s in scenes),'actual_audio_seconds':qa['audio']['duration_seconds'],
         'genuine_service_anchor_cuts':operations,'coalescence':coalescence,'caption_gap_hold':{'raw_cue':95,'derived_start':314.0,'original_raw_end':raw[94]['end'],'observed_next_raw_cue':96,'observed_next_raw_start':raw[95]['start'],'derived_end':raw[95]['start'],'actual_gap_seconds':round(raw[95]['start']-raw[94]['end'],3),'image':rows[26]['id'],'method':'Hold unchanged caption across the actual inter-cue gap to next genuine cue start. No speech word boundary is moved or estimated.'},'scenes':scenes,
         'raw_cue_correspondence':source_map,'cue_correspondence':expanded,'readability':readability,
         'timing_method':'Original actualv2service cue boundaries plus exact exported whole-second markers72/82/112/314/319 only. Original75/76same-image caption coalescence uses genuine raw76end. Whole-second markers are not millisecond word times; no interpolation.',
         'listening_approved':True,'listening_review_file':LISTENING.as_posix(),'listening_review_sha256':PINS[LISTENING],
         'parent_timing_review_pending':True,'renderer_plan_created':False,'video_rendered':False,'publication_approved':False,
         'explicit_timing_choices':['Raw23keeps Save005 before catalog006 at genuine72.',
             'Raw25keeps View006 until genuine82 before stored name/description016.',
             'Raw34keeps requirement Save008 before actualSaved009 at112; fresh reopened010 begins at real raw35start114.980.',
             'Raw95shows View028 before stored Casey026at314. Its final caption holds across the actual0.451second gap to the observed next raw96start316.320 so42characters are readable in2.320seconds rather than1.869seconds. No word boundary is moved or interpolated. Raw96returns028Requiredcertifications launcher before eligibility027at319.',
             'Raw75/76coalescence replaces the unreadable0.950second tail with a2.900second exact-word caption on the same actual022admin-flags screen.'],
         'coverage_limits':['017/018narrow unusable role-member picker remain excluded. The actual profile Roles workflow019–025is used instead.',
             'Narrow requirement type label is not claimed in full; actual011catalog/012typeCode supply identity.',
             '013/014are unsaved separate/group1comparisons;015freshreload restores the single saved rule. No saved OR-set claim.',
             'Casey already has Officer, GroupTruck81, GroupAdmin and DeptAdmin before the exercise; only the additional role is saved. Preserve35-field before/after audit separately.',
             'Qualified is a software result for one fictional requirement while global enforcementOff remains visible; no blocking/removal, clinical/legal authorization or qualification claim.',
             '020search result last line is clipped; only actualCommunity query/Officer are bound. Prepared021shows both complete role chips.',
             'All28originalimages were reviewed during curation; proposed timing needs separate control-first cut review before final inputs. No encoded frame or browser playback is claimed here.']}
    return out,'\n\n'.join(blocks)+'\n',qa

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write-proposed',action='store_true');p.add_argument('--ffmpeg',type=Path);a=p.parse_args()
    proposed,text,original=prepare()
    if a.write_proposed:
        assert a.ffmpeg and a.ffmpeg.is_file() and not DIRECTORY.exists(),'Use actual FFmpeg and a NEW output directory.'
        DIRECTORY.mkdir(parents=True)
        derived=DIRECTORY/(NAME+'.derived116.srt');corrected=DIRECTORY/(NAME+'.derived116.corrected.srt');report=DIRECTORY/(NAME+'.derived116.actual.qa.json')
        derived.write_text(text)
        sys.path.insert(0,str(SOURCES/'production'))
        from qa_narration import audit
        result=audit(SOURCES/BASE/(NAME+'.narrated-source.json'),SOURCES/AUDIO,derived,corrected,report,str(a.ffmpeg),FROZEN)
        assert result['passed'] and not result['alignment']['text_changes'] and result['silent_raw_cues']==result['silent_corrected_cues']==0
        assert result['audio']['decoded_samples']==original['audio']['decoded_samples'] and result['audio']['duration_seconds']==original['audio']['duration_seconds']
        from render_walkthrough import load_cues
        assert len(load_cues(corrected))==116
        result['derived_caption_provenance']={'original_service_raw_cues':112,'original_service_raw_file':RAW.as_posix(),'original_service_raw_sha256':PINS[RAW],
            'original_actual_qa_sha256':PINS[ORIGINAL_QA],'raw_captions_field_denotes':'Separate proposed derived116input, not the original112actualv2service export.',
            'whole_second_cuts':proposed['genuine_service_anchor_cuts'],'coalescence':proposed['coalescence'],'caption_gap_hold':proposed['caption_gap_hold'],'all_originals_preserved':True,
            'human_listening_review_file':LISTENING.as_posix(),'human_listening_review_sha256':PINS[LISTENING]}
        report.write_bytes(encoded(result))
        proposed['derived_audio_qa']={'file':str(report.relative_to(SOURCES)),'sha256':sha(report),'passed':True,'silent_cues':0,'minimum_cue_rms':result['minimum_raw_cue_rms']}
        proposed['derived_captions']={'file':str(corrected.relative_to(SOURCES)),'sha256':sha(corrected)}
        mapping=DIRECTORY/'correspondence.proposed.json';mapping.write_bytes(encoded(proposed))
        compact=DIRECTORY/'cue-screen-correspondence.txt'
        compact.write_text('\n'.join(f"{c['cue']:03} raw{c['raw_cues'][0]:03} {c['start']:.3f}–{c['end']:.3f} {c['screenshot_id']} | {c['text']}" for c in proposed['cue_correspondence'])+'\n')
        provenance={'schema_version':1,'kind':'source_only_personnel_actual_audio_proposed116_derivation','created_at':datetime.now(timezone.utc).isoformat(),
            'source_frozen_sha256':FROZEN,'inputs':[{'file':p.as_posix(),'sha256':h} for p,h in PINS.items()],
            'recipe':{'file':str(Path(__file__).relative_to(SOURCES)),'sha256':sha(__file__)},
            'utility':{'file':str(UTILITY.relative_to(SOURCES)),'sha256':UTILITY_SHA},
            'outputs':[{'file':str(p.relative_to(SOURCES)),'sha256':sha(p)} for p in [derived,corrected,report,mapping,compact]],
            'metadata_revision':{'prior_proposed_package':'expansion/plans/core-personnel-administration-take-01-proposed-derived-20261028','reason':'Correct prior QA metadata descriptor original123 to actual112v2service export and explicitly bind the real inter-cue caption hold; prior words/timing/audio/source files remain preserved.'},'complete_audio_decode':True,'derived_cues':116,'silent_cues':0,'speech_energy_is_not_listening_review':True,
            'listening_approved':True,'parent_timing_review_pending':True,'renderer_plan_created':False,'video_rendered':False,'canonical_or_ready_changed':False}
        (DIRECTORY/'provenance.json').write_bytes(encoded(provenance))
    print(json.dumps({'source_preflight':True,'scenes':12,'raw_cues':112,'proposed_cues':116,'sources':26,
        'intervals':proposed['screen_intervals'],'minimum_caption_seconds':min(r['duration_seconds'] for r in proposed['readability']),
        'maximum_caption_cps':max(r['characters_per_second'] for r in proposed['readability']),
        'files_written':a.write_proposed,'listening_approved':True,'timing_review_pending':True,'rendered':False,'canonical_ready':False}))

if __name__=='__main__':main()
