"""Prepare exact speech-to-screen proposals, never approvals or final media.

Default is read-only. --prepare writes a new proposal directory. Every speech cue
and source hash is checked. The trade transition uses one genuine stored word
boundary; all other cuts use unchanged exported cue boundaries.
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
CONFIG = {
    'trade': {'id': 'app-responder-shift-trade-request-cancel',
              'base': 'expansion/plans/app-responder-shift-trade-request-cancel-source-proposal-20261101',
              'lesson_sha256': '922f6d54e7aaca8115fa71547dc6da063abe2988fc5725d09740e35172bc9d92',
              'manifest_sha256': '7383d224b26707e533f372c726b97b7ff188aae3a514e0f8a1209e7d93da0da7',
              'audio_sha256': '0846ea4dd8151d2d5500a1d749825e09338ae74b6f3298ba48563eb1ecd7a144',
              'caption_suffix': '.word-aligned-85.corrected.srt',
              'captions_sha256': '06357b29782d47ba11f1d6186a6794fb9d915b40d24180ba4b827111be9323d3',
              'qa_suffix': '.word-aligned-85.qa.json',
              'qa_sha256': 'cd264e4ef202e1f9ae03ff6df14b5d4232ac1bbc9c30738ef9ca0cdc77e91496',
              'cue_count': 85},
    'analytics': {'id': 'core-records-analytics-summary-workload',
                  'base': 'expansion/plans/core-records-analytics-summary-workload-source-proposal-20261101',
                  'lesson_sha256': 'e7d697afba265c7fa8194f8bd0cf101a89dbaff2299ac7d94f607aefc7c8c866',
                  'manifest_sha256': '128ec414ea1f66df5130b3d06d11bb2f1125065b9b87960f53689cf3309540e6',
                  'audio_sha256': '870142655ec2034c88a439c8aa878608a52fdd28de61aa8ae18e9d10f94966be',
                  'caption_suffix': '.actual.corrected.srt',
                  'captions_sha256': 'c5600b579bf797ca51db7e6834d26e20b154954dcaf0a8f43fe6c234e037d87b',
                  'qa_suffix': '.actual.qa.json',
                  'qa_sha256': '733f40321a0e80b6867f785e63bd1f240450912933f3af7cad8b233c101187be',
                  'cue_count': 111},
}
WARNING = 'Sign-ups and trades on this shift need supervisor approval.'
EXPLANATION = 'Choose who you would like to take this shift. Everyone you pick is asked, then you choose from their offers.'
NOTE = 'TRAINING ONLY - Practice reviewing and cancelling a shift trade request.'
TRADE_ORIGINAL_REFERENCES = {
    2: {'Community standby signup': 'Community standby signup', 'Sunday, November 1, 2026': 'Sunday, November'},
    3: {'8:00 AM – 12:00 PM': 'eight until noon'}, 4: {'You are on': 'You are on'},
    5: {WARNING: 'sign-ups and trades'}, 6: {WARNING: 'approval'}, 7: {'Request trade': 'Request trade'},
    11: {EXPLANATION: 'everyone you pick is asked'}, 12: {EXPLANATION: 'you choose from their offers'},
    14: {'Blake Gallo': 'Blake Gallo', 'Truck 81 · Firefighter': 'Truck eighty-one and Firefighter'},
    18: {'Blake Gallo': 'intended person'}, 19: {'Blake Gallo': 'Blake Gallo', 'Selected: 1': 'Selected, one'},
    20: {'Note': 'Note'}, 21: {NOTE: 'training exercise'}, 22: {NOTE: 'reviewing and cancelling a trade'},
    23: {'Note': 'note', 'Send request': 'Send request'}, 26: {'Send request': 'Send request'},
    27: {'You have asked colleagues to take this shift.': 'You have asked colleagues to take this shift'},
    28: {'Cancel trade request': 'Cancel trade request'}, 29: {'You are on': 'You are on', WARNING: 'supervisor-approval rule'},
    35: {'Trades': 'Trades'}, 36: {'In progress': 'In progress', 'Community standby signup': 'standby entry'},
    37: {'Outgoing': 'Outgoing', 'Open': 'Open', 'Note': 'Note'},
    38: {'Responses': 'Responses', 'Blake Gallo': 'Blake Gallo', 'No reply yet': 'No reply yet'},
    42: {'Cancel trade request': 'Cancel trade request'}, 43: {'Cancel this trade request?': 'Cancel this trade request'},
    45: {'Any offers you have received will be discarded.': 'any offers you have received will be discarded'},
    48: {'Cancel trade request': 'Cancel trade request'},
    49: {'Trades': 'Trades', 'No shift trades': 'No shift trades'}, 51: {'Trades': 'Trades'},
    55: {'Calendar': 'Calendar'}, 56: {'Sunday, November 1, 2026': 'Sunday, November first', 'Community standby signup': 'Community standby signup'},
    58: {'8:00 AM – 12:00 PM': 'eight-to-noon', 'You are on': 'You are on', 'Approval required': 'Approval'},
    59: {'Approval required': 'required label'}, 60: {'Community standby signup': 'matching card'},
    63: {'Community standby signup': 'same standby occurrence'}, 64: {'Request trade': 'Request trade'},
    65: {'You are on': 'You are on'}, 70: {'Roster': 'Roster'},
    71: {'Wallace Boden': 'Wallace Boden', 'Command': 'Command', 'Chief': 'Chief', 'Scheduled': 'Scheduled'},
    72: {'Engine 51': 'Engine', 'Squad 3': 'Squad'}, 82: {WARNING: 'required approval'},
}
TRADE_REFERENCES = {(n if n < 10 else n + 1): refs for n, refs in TRADE_ORIGINAL_REFERENCES.items()}
TRADE_REFERENCES.update({10: {'Request trade': 'Request trade'}, 11: {'Request a trade': 'Request a trade'}})
TRADE_SPANS = [('01',1,9,'001-'), ('02',10,10,'001-'), ('02',11,18,'002-'),
               ('03',19,26,'003-'), ('04',27,27,'003-'), ('04',28,35,'004-'),
               ('05',36,42,'005-'), ('06',43,43,'005-'), ('06',44,49,'006-'),
               ('07',50,55,'008-'), ('08',56,63,'011-'), ('09',64,70,'009-'),
               ('10',71,71,'009-'), ('10',72,77,'010-'), ('11',78,85,'009-')]
PRIOR = 'Prior period: 2026-05-03 - 2026-08-01'
CUSTOM = 'TRAINING ONLY - Community software exercise'
ANALYTICS_REFERENCES = {
    1: {'Records':'Records', 'Analytics':'Analytics'}, 2: {'Executive summary':'Executive summary'},
    3: {'From':'From', 'To':'To', 'Station / group':'Station slash group', 'Definition':'Definition'},
    4: {'From':'August second', 'To':'October thirty-first'},
    5: {'All station groups':'All station groups', 'All definitions':'All definitions'},
    6: {'Records read: 4':'Records read count'}, 11: {'Headline figures':'Headline figures', PRIOR:'prior-period'},
    13: {'Records finalized':'Records finalized', 'Personnel hours':'Personnel hours', 'Training hours':'Training hours'},
    14: {'Amendments':'Amendments'}, 15: {'Incident reports':'Incident reports', 'Unit responses':'unit responses', 'NERIS accepted':'NERIS counts', 'NERIS rejected':'NERIS counts'},
    17: {PRIOR:'prior period'},
    21: {'Lifecycle':'Lifecycle', 'Queues and obligations':'Queues and obligations', 'By month':'By month', 'By definition':'By definition'},
    22: {'Median hours to finalize':'Median hours to finalize'}, 25: {'Open drafts':'Open drafts', 'Awaiting review':'Awaiting review'},
    28: {'By month':'four October records'}, 29: {'Training':'Training', CUSTOM:'community software-exercise records'},
    30: {'Count':'counts', 'Hours':'hours', 'Share':'shares'},
    32: {'Training':'Training', 'Definition':'Definition'}, 33: {'Filter':'Filter'}, 34: {'Records read: 4':'Records read, four'},
    36: {'Station / group':'group', 'From':'dates', 'To':'dates'}, 37: {'Filter':'Filter'},
    40: {'Filter':'Filter'}, 41: {'Training':'Training', 'Records read: 2':'Records read is now two'},
    42: {'All station groups':'All station groups', 'From':'dates', 'To':'dates'},
    46: {'Headline figures':'headline figures'},
    47: {'Records finalized':'Records finalized', 'Training hours':'Training hours', 'Personnel hours':'Personnel'},
    48: {'Personnel hours':'hours remain zero point five', 'Training hours':'hours remain zero point five'},
    50: {'Training':'Training'}, 52: {'Amendments':'Amendments'},
    55: {'Station / group':'Station slash group', 'Engine 51':'Engine fifty-one'}, 56: {'Filter':'Filter', 'Training':'Training'},
    57: {'Records read: 0':'Records read, zero'},
    58: {'Station / group':'group', 'Definition':'definition', 'From':'dates', 'To':'dates'},
    63: {'Records finalized':'Records finalized', 'Training hours':'Training hours'}, 64: {'Amendments':'Amendments'},
    68: {'No finalized Records in this window.':'No finalized Records in this window'},
    71: {'All station groups':'All station groups', 'All definitions':'All definitions', 'Filter':'Filter'},
    72: {'Records read: 4':'four records'}, 77: {'Workload':'Workload'},
    78: {'From':'date', 'To':'date', 'Station / group':'group', 'Definition':'definition', 'Records read: 4':'Generated count'},
    79: {'Records read: 4':'four records', 'Record hours':'Record hours'}, 80: {'Personnel hours':'Personnel hours', 'Training hours':'Training hours'},
    85: {'By month':'By month', 'By definition':'By definition'}, 86: {'2026-10':'October', 'Count':'four records', 'Hours':'zero point five hours'},
    87: {'Training':'Training', 'Count':'two records', 'Hours':'zero point five'}, 88: {'Share':'fifty-percent share'},
    89: {CUSTOM:'community software-exercise definition', 'Share':'fifty-percent'}, 90: {'Hours':'zero recorded hours'},
    92: {'Count':'all three columns', 'Hours':'all three columns', 'Share':'all three columns'},
    94: {'Records by weekday and hour':'Records by weekday and hour', 'By person':'person', 'By unit':'unit'},
    95: {'By author':'author', 'By station group':'station-group panels'},
    97: {'By person':'By person', 'Matthew Casey':'Matthew Casey', 'Hours':'zero point five hours'},
    98: {'By author':'By author', 'Wallace Boden':'Wallace Boden'},
    99: {'By station group':'By station group', 'Command':'Command', 'Firehouse 51':'Firehouse fifty-one'},
    101: {'By unit':'unit panel', 'No finalized Records in this window.':'no finalized Records in this window'},
    110: {'From':'window', 'To':'window', 'Definition':'definition', 'Station / group':'group', 'Filter':'refresh the view'},
}


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text())
def need(ok, message):
    if not ok: raise ValueError(message)
def encoded(value): return (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode()


def prepare(key, write=False):
    c = CONFIG[key]; base = Path(c['base']); name = c['id']
    lesson_file, manifest_file = base/'lesson.candidate.json', base/'captures.reviewed.json'
    audio = Path('expansion/audio')/(name+'.m4a')
    captions, qa_file = Path('expansion/audio')/(name+c['caption_suffix']), Path('expansion/audio')/(name+c['qa_suffix'])
    for file, digest in [(lesson_file,c['lesson_sha256']), (manifest_file,c['manifest_sha256']),
                         (audio,c['audio_sha256']), (captions,c['captions_sha256']), (qa_file,c['qa_sha256'])]:
        need(sha(S/file)==digest, 'Changed verified input: '+str(file))
    sys.path.insert(0,str(ROOT/'scripts'))
    from render_walkthrough import load_cues, words, find_font, caption_wrap
    from verify_capture_evidence import _Validator, _normalized, instruction_scene_digest
    from expansion_site import lesson_content_digest
    from PIL import Image, ImageDraw, ImageFont
    lesson, manifest, qa = read(S/lesson_file), deepcopy(read(S/manifest_file)), read(S/qa_file)
    rows = {r['id']:r for r in manifest['screenshots']}
    if key == 'trade':
        extra = base/'additional-literal-observations-20261101.json'
        need(sha(S/extra)=='bd7ae5c996960af69256d28b571e4a7350b1d2fa95d3af7b9a187657f60518d5','Changed genuine additional pixel review')
        for obs in read(S/extra)['observations']:
            row = rows[obs['capture_id']];need(row['sha256']==obs['source_sha256'],'Changed reviewed pixels')
            row['visible_labels'] = list(dict.fromkeys([*row['visible_labels'],*obs['labels']]))
            row['additional_literal_review'] = {'file':str(extra),'sha256':sha(S/extra)}
        word_proof = Path('expansion/audio')/(name+'.word-boundary-provenance.json')
        need(sha(S/word_proof)=='f6018faa6c56ad05f32ef1ffd8ef3e7df6b2345a8f71be18899652c6ff07d7a9','Changed stored word timing provenance')
    else:
        extra = base/'additional-literal-observations-20261101.json'
        need(sha(S/extra)=='acf609dbdc707f4db4a929c2c5dd1b0cdce42efe136126a0417dee95b778b264','Changed genuine analytics pixel review')
        for obs in read(S/extra)['observations']:
            row=rows[obs['capture_id']];need(row['sha256']==obs['source_sha256'],'Changed reviewed analytics pixels')
            row['visible_labels']=list(dict.fromkeys([*row['visible_labels'],*obs['labels']]))
            row['additional_literal_review']={'file':str(extra),'sha256':sha(S/extra)}
    observed = {}
    for id,row in rows.items():
        need(sha(S/row['file'])==row['sha256'] and sha(S/row['dom_file'])==row['dom_sha256'],'Changed source image/DOM')
        v=_Validator(S); observed[id]=v.observations(row,id);need(not v.issues,json.dumps(v.issues))
    cues=load_cues(S/captions)
    need(len(cues)==c['cue_count'] and qa['passed'] and not qa['issues'] and qa['silent_corrected_cues']==0,'Incomplete audio QA')
    need(qa['audio']['sha256']==c['audio_sha256'] and qa['corrected_captions']['sha256']==c['captions_sha256'],'Measured media differ')
    duration=qa['audio']['duration_seconds']; spans=TRADE_SPANS if key=='trade' else []
    refs=TRADE_REFERENCES if key=='trade' else ANALYTICS_REFERENCES
    if key=='analytics':
        cursor=0
        for sc in lesson['scenes']:
            first=cursor+1; text=''
            while words(text)!=words(sc['narration']):
                need(cursor<len(cues),'Missing paragraph cues');text+=' '+cues[cursor]['text'];cursor+=1
                need(words(sc['narration'])[:len(words(text))]==words(text),'Paragraph crosses actual cue boundary')
            spans.append((sc['id'],first,cursor,sc['capture_refs'][0]))
    need([n for _,a,b,_ in spans for n in range(a,b+1)]==list(range(1,len(cues)+1)),'Incomplete actual cue map')
    holds,entries=[],[]
    for i,(scene,first,last,prefix) in enumerate(spans):
        matches=[id for id in rows if id.startswith(prefix)];need(len(matches)==1,'Ambiguous source capture')
        id=matches[0];start=0.0 if i==0 else cues[first-1]['start'];end=cues[spans[i+1][1]-1]['start'] if i+1<len(spans) else duration
        holds.append({'scene_id':scene,'screenshot_id':id,'start':start,'end':end,'first_cue':first,'last_cue':last})
        for n in range(first,last+1):
            cue=cues[n-1];aliases=refs.get(n,{})
            need(cue['start']>=start and cue['end']<=end,'Actual speech crosses screen hold')
            need({_normalized(label) for label in aliases}<=observed[id],f'Cue{n}: unseen literal label in {id}')
            entry=dict(cue,cue=n,scene_id=scene,screenshot_id=id,required_labels=list(aliases),spoken_references=aliases,instructional=bool(aliases))
            v=_Validator(S);v.spoken_references(entry,{_normalized(x) for x in aliases},f'cue{n}',True);need(not v.issues,json.dumps(v.issues))
            entries.append(entry)
    scenes=[]
    for sc in lesson['scenes']:
        selected=[h for h in holds if h['scene_id']==sc['id']];selected_cues=[{k:v for k,v in e.items() if k!='scene_id'} for e in entries if e['scene_id']==sc['id']]
        need(words(' '.join(e['text'] for e in selected_cues))==words(sc['narration']),'Changed complete paragraph')
        union=set().union(*(observed[h['screenshot_id']] for h in selected))
        need({_normalized(label) for label in sc['required_labels']}<=union,'Unseen scene requirements')
        need(any(e['required_labels'] for e in selected_cues),'Operational scene lacks a real UI reference')
        scene={'id':sc['id'],'title':sc['title'],'kind':'operational','start':selected[0]['start'],'end':selected[-1]['end'],
               'visual_required_labels':sc['required_labels'],'screens':[{k:h[k] for k in ['screenshot_id','start','end']} for h in selected],'captions':selected_cues}
        scene['proposed_mapping_sha256']=instruction_scene_digest(scene,rows);scenes.append(scene)
    learner=deepcopy(lesson);learner['scope_limits']=[x for x in learner['scope_limits'] if 'Source candidate only' not in x]
    need(lesson_content_digest(lesson)==lesson_content_digest(learner),'Learner prose changed')
    font=find_font();draw=ImageDraw.Draw(Image.new('RGB',(1920,1080)));tf=ImageFont.truetype(str(font),27);cf=ImageFont.truetype(str(font),30)
    geometry={'method':'Exact unchanged renderer font sizes and 1920x1080 geometry; measurement only, not encoded-frame review.', 'font_sha256':sha(font),'titles':[],'captions':[]}
    for sc in scenes:
        title='TRAINING ONLY · fictional department · '+sc['title'];width=draw.textbbox((0,0),title,font=tf)[2];need(width<=1856,'Title does not fit')
        geometry['titles'].append({'scene_id':sc['id'],'width_pixels':width,'fits':True})
    for cue in cues:
        lines=caption_wrap(draw,cue['text'],cf,1800);width=max(draw.textbbox((0,0),line,font=cf)[2] for line in lines)
        geometry['captions'].append({'cue':len(geometry['captions'])+1,'lines':lines,'maximum_width_pixels':width,'fits':True})
    proposal={'created_at':datetime.now(timezone.utc).isoformat(),'lesson_file':str(lesson_file),'lesson_sha256':c['lesson_sha256'],
              'audio_file':str(audio),'audio_sha256':c['audio_sha256'],'captions_file':str(captions),'captions_sha256':c['captions_sha256'],
              'qa_file':str(qa_file),'qa_sha256':c['qa_sha256'],'duration_seconds':duration,'scenes':scenes,'holds':holds,'cues':entries,
              'cue_count':len(cues),'source_images':len(rows),'holds_count':len(holds),'learner_content_sha256':lesson_content_digest(learner),
              'review_state':'proposal_only_no_review_or_hearing_approval_inferred'}
    if write:
        dest=S/'expansion/plans'/(name+'-complete-correspondence-20261101');need(not dest.exists(),'Preserve existing proposal');dest.mkdir()
        for file,data in [('captures.source-relative.json',manifest),('correspondence.proposed.json',proposal),('lesson.learner-projection.proposed.json',learner),('caption-layout-measurements.json',geometry)]:
            with (dest/file).open('xb') as f:f.write(encoded(data))
        compact='\n\n'.join(f"Cue{e['cue']:03} · scene{e['scene_id']} · {e['start']:.3f}–{e['end']:.3f} · {e['screenshot_id']}\n{e['text']}\nLiteral -> exact speech: {json.dumps(e['spoken_references'],ensure_ascii=False)}" for e in entries)+'\n'
        (dest/'cue-screen-correspondence.txt').open('x').write(compact)
    return {'passed':True,'lesson_id':name,'cues':len(cues),'scenes':len(scenes),'holds':len(holds),'source_images':len(rows),
            'duration_seconds':duration,'geometry_fits':True,'written':write,'actual_review_and_hearing':'not inferred'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('lesson',choices=CONFIG);parser.add_argument('--prepare',action='store_true');args=parser.parse_args()
    print(json.dumps(prepare(args.lesson,args.prepare),indent=2))
