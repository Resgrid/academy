"""Prepare Billing/Shifts take02 screen/caption proposals from retained real cues.

Default read-only; --write-proposed writes NEW source-only proposal folders.
No listening receipt, final renderer plan, assembly, canonical, site, target,
browser, Descript, database or Git operation is implemented here.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sys
import textwrap

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
S=ROOT/'sources'
CONFIG={'billing': {'name': 'core-customer-billing-review', 'base': 'expansion/plans/core-customer-billing-review-capture-freeze-20261029', 'audio': 'expansion/audio/core-customer-billing-review-take-02.m4a', 'raw': 'expansion/audio/core-customer-billing-review-take-02-generated-20261029.raw.srt', 'corrected': 'expansion/audio/core-customer-billing-review-take-02.actual.corrected.srt', 'text': 'expansion/audio/core-customer-billing-review-take-02-generated-20261029.txt', 'qa': 'expansion/audio/core-customer-billing-review-take-02.actual.qa.json', 'words': 843, 'images': 15, 'cues': 102, 'out': 'expansion/plans/core-customer-billing-review-take-02-proposed-20261030', 'pins': {'expansion/plans/core-customer-billing-review-capture-freeze-20261029/core-customer-billing-review.narrated-source.json': 'ba6214c9fec32991c1a04e795045bbe9749289d86ffc63813bd231d92d47aec5', 'expansion/plans/core-customer-billing-review-capture-freeze-20261029/core-customer-billing-review.captures.reviewed.json': 'bac6713c2ff2c68405633128b7747916cfaf7cd07c0f3e6caf25fcacb9c08272', 'expansion/plans/core-customer-billing-review-capture-freeze-20261029/core-customer-billing-review.screen-sequence.json': '8a712f69894c819bc55be102398354cf33f86a24a3283267991151dee6e17671', 'expansion/plans/core-customer-billing-review-capture-freeze-20261029/source-hashes.json': '156a39f694333d6cbd55b648bd6a63af89595f3a4f94a7a4514afbc5fa42ed39', 'expansion/plans/core-customer-billing-review-capture-freeze-20261029/narration.txt': '61750a55fb747edbc8cd327f934cb0fdc502ac37659e2073c9acc812625872d5', 'expansion/audio/core-customer-billing-review-take-02.m4a': '6901b4714284e31cc1966502d0070955615c066a37bbb113283fe034ec2d2418', 'expansion/audio/core-customer-billing-review-take-02-generated-20261029.raw.srt': 'b3b9af3442fcfbeb78ac5515d3cd6203569b1bc11a5fda80905381aaff389c37', 'expansion/audio/core-customer-billing-review-take-02.actual.corrected.srt': 'fa3ddf836a2c008e2eda4e5fc631864be27b836c54c9b102a709e3e4dff44666', 'expansion/audio/core-customer-billing-review-take-02-generated-20261029.txt': '301a6e0f95d20436414254bedafd3fb06280a1f1be771dc8df56004dfb3133ca', 'expansion/audio/core-customer-billing-review-take-02.actual.qa.json': 'c40c5235e2315449b41b0adaf6eadf2d367e9d3428a987898ccabbdd11907269', 'expansion/plans/core-customer-billing-review-capture-freeze-20261029/source-evidence.json': '6cce63c92aa8d34084d78f24197c5bfc9fb5de4f9fff237b98a0d578fb4aeaf0', 'expansion/plans/core-customer-billing-review-capture-freeze-20261029/accepted-script-review.json': '3c8f9e942f5bcf2b81a65d4e890565dfda0976246d637d6d91f2956bffaae95e', 'expansion/plans/core-customer-billing-review-capture-freeze-20261029/compact-correspondence.json': 'c27da251dff7e964acfc8ff5643242d504e2b6bef2eee2cc162c313d41670a2e'}, 'notes': ['All source images and DOM bytes are retained unchanged. The proposal does not requalify video or certify current live state.', 'Full decode and original per-cue signal QA passed. Actual User full-listening approval remains pending; no listening receipt is written.', 'All19 source-span cuts coincide with real102-cue boundaries. Original cue6 exceeds22 characters/second; proposed cues5+6 are coalesced on unchanged image001, retaining both real endpoints. Derived count101; no finer timestamp export or interpolation is necessary.', 'BillingEmail remains outside the demonstrated profile viewports. No value is read or copied. Every financial/provider/subscription form remains inspection-only.', 'Legacy amounts and counters are historical training data and are not current commercial pricing or capacity guidance.']}, 'shifts': {'name': 'core-shifts-administration', 'base': 'expansion/plans/core-shifts-administration-capture-freeze-20261028-v2', 'audio': 'expansion/audio/core-shifts-administration-take-02.m4a', 'raw': 'expansion/audio/core-shifts-administration-take-02-generated-20261029.raw.srt', 'corrected': 'expansion/audio/core-shifts-administration-take-02.actual.corrected.srt', 'text': 'expansion/audio/core-shifts-administration-take-02-generated-20261029.txt', 'qa': 'expansion/audio/core-shifts-administration-take-02.actual.qa.json', 'words': 996, 'images': 24, 'cues': 116, 'out': 'expansion/plans/core-shifts-administration-take-02-proposed-20261030', 'anchors': 'expansion/audio/core-shifts-administration-take-02-generated-20261030.one-second.txt', 'pins': {'expansion/plans/core-shifts-administration-capture-freeze-20261028-v2/core-shifts-administration.narrated-source.json': '0ef135425762b54c1f772c932d5d89d5f21ea561d4d7a8ad50bd97d31f0772a4', 'expansion/plans/core-shifts-administration-capture-freeze-20261028-v2/core-shifts-administration.captures.reviewed.json': 'bc0f4791680591af2eaceb92e56072b026b41f9566a67e16444740fd7908d3bb', 'expansion/plans/core-shifts-administration-capture-freeze-20261028-v2/core-shifts-administration.screen-sequence.json': '3235f8f614d206f509a63e000e0165fa2d80e9bd7555bf10a95053c94402d099', 'expansion/plans/core-shifts-administration-capture-freeze-20261028-v2/source-hashes.json': '78587e801bdbb4fe6816511ab7ae6efad635e06926ef2ea72463582831f1105e', 'expansion/plans/core-shifts-administration-capture-freeze-20261028-v2/narration.txt': '452ef598618505fec7af0ff0bf447457b8855df554fa3067c5dad6d42aeb5d1f', 'expansion/audio/core-shifts-administration-take-02.m4a': '92ab9cdb5bc11785df8ea0f88761d7660e87b3fe6f9095420d893fae106b930e', 'expansion/audio/core-shifts-administration-take-02-generated-20261029.raw.srt': '7556d218b61b0370381c1039468718f4d7b17d7072aa2917bef0469fd13eaf55', 'expansion/audio/core-shifts-administration-take-02.actual.corrected.srt': '2c9ddfa4d270020d046f24292bb0e74ff58b4dd8d2c59a81903546144071adf1', 'expansion/audio/core-shifts-administration-take-02-generated-20261029.txt': '20cac49c0ecff528074356c3b6ca321d689bf1cb3ec6c5bd9fc1662d531c9e0c', 'expansion/audio/core-shifts-administration-take-02.actual.qa.json': '8d6138ae7b5ef061c41b120dab31feb671bd0276544b519fe4e7c1c8054157d9', 'expansion/audio/core-shifts-administration-take-02-generated-20261030.one-second.txt': 'c2bcf12070799d0e2b01b60840fd4985566cf0613629704cc6e56aacf072054f'}, 'notes': ['All source images and DOM bytes are retained unchanged. The proposal does not requalify video or certify current live state.', 'Full decode and original per-cue signal QA passed. Actual User full-listening approval remains pending; no listening receipt is written.', 'Seven screen transitions use exact offsets in the genuine service one-second word-group transcript. Marker37 begins open New Shift;167 returned row;190 to check;247 and one required;266 selected;269 day detail;311 waiting signups.', 'The New Shift tail shorter than1second is merged forward with the next actual cue on image002. The and one tail shorter than1second is merged forward with the next actual cue on image019. Words/order are unchanged; merge ends are genuine raw-cue endpoints.', 'Result list022 already shows both Edit Details and Edit Calendar before cue80. Details023 then covers setting/time review; marker266 switches to selected dates024 and marker269 to day detail026. This avoids a short calendar flash while preserving literal source order. Root must review this proposed correspondence.', 'At the policy comparison, baseline001 begins at raw cue92 (checkbox on an individual shift), before the actual Open Approvals phrase in93; source039 begins at genuine marker311 waiting signups. The earlier screenshot017 demonstrated the individual approval checkbox. This is a contextual comparison, not another checkbox operation.', 'Short assigned-start and verify-launcher subspans repeat the same source image continuously from the preceding scene. No short new-image flash is introduced; chapter headings change at frozen scene boundaries.', 'Specific View Calendar widget failures and the incomplete Static Shift exercise remain excluded. No attendance, qualifications, apparatus-crew assignment, delivered notification, approved signup or trade is demonstrated.']}}
SHIFTS={'schedules': [('Shifts brings', '001-shifts-baseline', ['Recurring Group Shifts', 'Add Static Shift', 'Your Shifts', 'On Duty Now', 'Approvals', 'Shift Staffing'])], 'assigned-start': [('Choose Add Recurring', '001-shifts-baseline', ['Add Recurring Group Shift']), ('open New Shift.', '002-assigned-start-prepared', ['New Shift', 'Name', 'Code', 'TRN28A', 'Assignment Type', 'Assigned', 'Color', 'Signups and trades need supervisor approval', 'Next'])], 'manual-days': [('Schedule gives', '004-assigned-schedule-corrected', ['Schedule >', 'Start Time', '09:00', 'End Time', '11:00', 'NOVEMBER 2026', '4', 'Slots >'])], 'minimums': [('In Slots,', '005-assigned-group-role-prepared', ['Add Group to Shift', 'Shift Group', 'Firehouse 51', 'Add Role to Group', 'Shift Role', 'Officer', 'Roles Count', '1', 'Next'])], 'assigned-person': [('Personnel separates', '006-assigned-personnel-prepared', ['Personnel >', 'Non-Group Personnel', 'Firehouse 51', 'Matthew Casey', 'Next'])], 'finish': [('The Finish stage', '007-assigned-finish-review', ['Finish', 'Click the finish button below to create your new shift.']), ('returned row in', '008-assigned-created-list', ['Recurring Group Shifts', 'TRAINING ONLY - Coverage authoring 20261028', 'Assigned', 'Manual', 'Groups', 'Personnel', '1', 'View Calendar', 'Edit Details', 'Edit Calendar', 'Edit Groups'])], 'verify': [('Reopen Edit Details', '008-assigned-created-list', ['Edit Details']), ('to check the stored', '009-assigned-details-reopened', ['Edit Shift Details', 'Name', 'Code', 'TRN28A', 'Color', '#93c5fd', 'Start Time', '09:00', 'End Time', '11:00']), ('Casey remains', '010-assigned-member-reopened', ['Firehouse 51', 'Matthew Casey']), ('In the shared calendar,', '013-assigned-calendar-date-context', ['Calendar', 'November 2026', '04']), ('Its day detail', '014-assigned-day-saved', ['4 Nov 2026', 'Upcoming', '11/04/2026 0900', '11/04/2026 1100', 'Required', 'Needed', 'Officer', '1', '0']), ('roster lists Casey', '015-assigned-roster-saved', ['Roster', 'Matthew Casey', 'Assigned', 'Fully staffed', 'Required', 'Needed', 'Officer', '1', '0'])], 'signup': [('For a signup schedule,', '017-signup-approval-start', ['Code', 'TRN28S', 'Assignment Type', 'Signup', 'Signups and trades need supervisor approval']), ('Select November', '018-signup-dates-prepared', ['NOVEMBER 2026', '5', '6', 'Start Time', '09:00', 'End Time', '11:00']), ('and one required Officer', '019-signup-group-role-prepared', ['Firehouse 51', 'Shift Role', 'Officer', 'Roles Count', '1']), ('Leave every Personnel', '020-signup-no-preassigned-members', ['Personnel >', 'Non-Group Personnel', 'Firehouse 51']), ('Review Finish', '021-signup-finish-before-save', ['Finish', 'Click the finish button below to create your new shift.'])], 'signup-result': [('The saved row', '022-signup-created-approval-row', ['Approval required', 'Edit Details', 'Edit Calendar']), ('Reopen its details', '023-signup-details-reopened', ['Edit Shift Details', 'TRN28S', 'Signups and trades need supervisor approval', 'Start Time', '09:00', 'End Time', '11:00']), ('selected dates.', '024-signup-dates-reopened', ['Edit Shift Calendar', 'NOVEMBER 2026', '5', '6']), ('day detail is', '026-signup-day-stable-empty', ['Shift Day Detail', 'Signup', 'Upcoming', 'Open slots: 1', 'Officer', 'Required', 'Needed', '1', 'Roster', 'Nobody is on this day yet.', 'Your Status', 'You are not on this shift day.', 'Signup for Shift with Firehouse 51'])], 'policy': [('Department Shift Settings', '016-multiple-group-policy-readonly', ['Shift Signup Settings', 'Allow Signups For Multiple Groups', 'Allow a member to sign up for multiple shift groups. Review overlaps and local coverage rules separately.']), ('checkbox on an individual shift.', '001-shifts-baseline', ['Approvals']), ('waiting signups and trades', '039-approvals-current-empty', ['Shift Approvals', 'No sign-ups are waiting for approval.', 'No trades are waiting for approval.', 'Sign-ups and trades waiting for approval in the groups you supervise. Nobody is on duty for a pending request until it is approved.'])], 'current-duty': [('On Duty Now shows', '040-current-on-duty-readonly', ['On Duty Now', 'A Shift — Firehouse 51', 'Wallace Boden', 'Christopher Herrmann', 'Refresh', 'On duty as of 10/28/2026 1653. This page refreshes every minute.'])], 'adapt': [('Chicago Fire can', '001-shifts-baseline', ['Recurring Group Shifts']), ('In every setting,', '014-assigned-day-saved', ['Required', 'Needed', 'Roster'])]}


def require(condition,message):
    if not condition:raise ValueError(message)


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
def norm(text):return ' '.join(text.split())


def cues(path):
    out=[]
    def seconds(t):
        h,m,s,ms=map(int,re.split('[:,]',t));return h*3600+m*60+s+ms/1000
    for block in Path(path).read_text().strip().split('\n\n'):
        lines=block.splitlines();a,b=lines[1].split(' --> ')
        out.append({'cue':int(lines[0]),'start':seconds(a),'end':seconds(b),'text':' '.join(lines[2:])})
    require([x['cue']for x in out]==list(range(1,len(out)+1)),'Nonsequential service cues.')
    require(all(x['end']>x['start']for x in out),'Nonpositive service cue.')
    return out


def service_anchors(text):
    ms=list(re.finditer(r'\[(\d\d):(\d\d):(\d\d)\]',text));require(ms and not text[:ms[0].start()].strip(),'Missing actual service timestamp markers.')
    entries=[];words=[]
    for i,m in enumerate(ms):
        at=sum(int(x)*k for x,k in zip(m.groups(),[3600,60,1]));end=ms[i+1].start()if i+1<len(ms)else len(text)
        require(not entries or at>entries[-1]['seconds'],'Out-of-order service markers.')
        portion=text[m.end():end].split();entries.append({'seconds':at,'word_offset':len(words),'actual_service_text':' '.join(portion)});words+=portion
    return words,entries


def verify_asset(row):
    require(row.get('accepted',True) is not False and row.get('eligible_for_lesson',True) is not False,'Rejected source cannot enter proposal.')
    for field,digest in [('file','sha256'),('dom_file','dom_sha256')]:
        if row.get(field):require(sha(S/row[field])==row[digest],'Changed source pair: '+row[field])


def partition(text,starts):
    positions=[]
    for prefix,capture,labels in starts:
        found=[m.start()for m in re.finditer(re.escape(prefix),text)]
        require(len(found)==1,'Ambiguous or missing exact source span: '+prefix)
        positions.append((found[0],capture,labels))
    require(positions[0][0]==0 and [x[0]for x in positions]==sorted(x[0]for x in positions),'Source span order changed.')
    return [{'capture_id':capture,'required_labels':labels,'narration_span':text[start:positions[i+1][0]if i+1<len(positions)else len(text)].strip()}for i,(start,capture,labels)in enumerate(positions)]


def boundary(offset,actual,anchors,last_word):
    if offset==last_word:return {'seconds':None,'basis':'decoded_audio_end'}
    for c in actual:
        if offset==c['word_start']:return {'seconds':c['start'],'basis':'unchanged_actual_SRT_cue_start','raw_cue':c['cue']}
    for c in actual:
        if c['word_start']<offset<c['word_end']:
            found=[a for a in anchors if a['word_offset']==offset]
            if not found:return {'seconds':None,'basis':'MISSING_genuine_service_word_boundary','raw_cue':c['cue'],'raw_start':c['start'],'raw_end':c['end'],'words_before_cut':' '.join(c['text'].split()[:offset-c['word_start']]),'words_after_cut':' '.join(c['text'].split()[offset-c['word_start']:])}
            require(len(found)==1,'Ambiguous actual service marker.')
            a=found[0];require(c['start']<a['seconds']<c['end'],'Service marker outside containing raw cue.')
            return {'seconds':a['seconds'],'basis':'genuine_service_whole_second_word_group','raw_cue':c['cue'],'actual_service_text':a['actual_service_text'],'precision':'Whole-second service marker; no millisecond word precision or interpolation.'}
    raise ValueError('Unassigned exact spoken offset.')


def propose(alias):
    cfg=CONFIG[alias];name=cfg['name'];base=Path(cfg['base'])
    for path,digest in cfg['pins'].items():require(sha(S/path)==digest,'Changed retained input: '+path)
    lesson=json.loads((S/base/(name+'.narrated-source.json')).read_text());manifest=json.loads((S/base/(name+'.captures.reviewed.json')).read_text());held=json.loads((S/base/'source-hashes.json').read_text())
    dependencies=[]
    for row in held.get('input_files',held.get('input_pins',[])):
        require(sha(S/row['file'])==row['sha256'],'Changed freeze dependency: '+row['file']);dependencies.append(row)
    trace=held.get('source_evidence',{'file':(base/'source-evidence.json').as_posix()})
    if trace.get('sha256'):require(sha(S/trace['file'])==trace['sha256'],'Changed source trace.')
    trace_doc=json.loads((S/trace['file']).read_text())
    for row in trace_doc['files']:
        require(sha(S/row['snapshot_file'])==row['sha256'],'Changed retained source snapshot.');dependencies.append({'file':row['snapshot_file'],'sha256':row['sha256']})
    rows={row['id']:row for row in manifest['screenshots']};require(len(rows)==cfg['images'],'Source count changed.')
    for row in rows.values():verify_asset(row)
    raw=cues(S/cfg['raw']);actual=cues(S/cfg['corrected']);require(len(raw)==len(actual)==cfg['cues'],'Caption count changed.')
    require([(c['start'],c['end'])for c in raw]==[(c['start'],c['end'])for c in actual],'Corrected captions changed genuine raw timing.')
    script=norm(' '.join(sc['narration']for sc in lesson['scenes']));require(script==norm((S/base/'narration.txt').read_text())==norm((S/cfg['text']).read_text())==norm(' '.join(x['text']for x in actual)),'Spoken words changed.')
    anchors=[]
    if cfg.get('anchors'):
        words,anchors=service_anchors((S/cfg['anchors']).read_text());require(words==script.split(),'Service marker transcript does not match exact frozen words.')
    qa=json.loads((S/cfg['qa']).read_text());require(qa['passed'] and not qa['issues'] and not qa['alignment']['text_changes']and qa['silent_raw_cues']==qa['silent_corrected_cues']==0,'Actual audio QA failed.')
    require(qa['lesson']['sha256']==cfg['pins'][(base/(name+'.narrated-source.json')).as_posix()] and qa['audio']['sha256']==cfg['pins'][cfg['audio']]and qa['audio']['full_decode']=='passed','Audio/source QA identity changed.')
    count=0
    for c in actual:c['word_start']=count;count+=len(c['text'].split());c['word_end']=count
    require(count==len(script.split())==cfg['words'],'Word-count mismatch.')
    sequence=json.loads((S/base/(name+'.screen-sequence.json')).read_text());spans=[];offset=0
    for scene,old in zip(lesson['scenes'],sequence['scenes']):
        require(scene['id']==old['scene_id'],'Frozen scene order changed.')
        screens=old['screens']if alias=='billing'else partition(scene['narration'],SHIFTS[scene['id']])
        require(norm(' '.join(x['narration_span']for x in screens))==norm(scene['narration']),'Screens omit or reorder words.')
        for x in screens:
            row=rows[x['capture_id']];require(x['capture_id']in scene['capture_refs'],'Unfrozen source scene link.')
            require(set(x['required_labels'])<=set(row['visible_labels']),'Missing source literal label.')
            end=offset+len(x['narration_span'].split());start_info=boundary(offset,actual,anchors,count);end_info=boundary(end,actual,anchors,count)
            spans.append({'span':len(spans)+1,'scene_id':scene['id'],'title':scene['title'],'capture_id':row['id'],'source_file':row['file'],'source_sha256':row['sha256'],'word_start':offset,'word_end':end,'start':start_info,'end':end_info,'required_labels':x['required_labels'],'exact_narration':norm(x['narration_span'])});offset=end
    require(offset==count,'Unmapped speech remains.')
    missing=[{'span':x['span'],'scene_id':x['scene_id'],'capture_id':x['capture_id'],**x['start']}for x in spans if x['start']['seconds']is None]
    derived=[];splits=[]
    if not missing:
        for c in actual:
            cuts=[x['word_start']for x in spans if c['word_start']<x['word_start']<c['word_end']]
            points=[c['word_start']]+cuts+[c['word_end']]
            for a,b in zip(points,points[1:]):
                span=next(x for x in spans if x['word_start']<=a<x['word_end']);start=c['start']if a==c['word_start']else boundary(a,actual,anchors,count)['seconds'];end=c['end']if b==c['word_end']else boundary(b,actual,anchors,count)['seconds']
                derived.append({'start':start,'end':end,'text':' '.join(c['text'].split()[a-c['word_start']:b-c['word_start']]),'raw_cues':[c['cue']],'word_start':a,'word_end':b,'scene_id':span['scene_id'],'screenshot_id':span['capture_id'],'source_sha256':span['source_sha256']})
            for cut in cuts:splits.append({'raw_cue':c['cue'],'word_offset':cut,**boundary(cut,actual,anchors,count)})
    merges=[]
    if alias=='billing' and derived:
        # Raw cue6 is only1.279s and22.674 characters/second. Its exact
        # adjacent cue5 uses the same screenshot; keep the complete sentence
        # through actual cue6's endpoint rather than inventing a new timestamp.
        i=next(i for i,c in enumerate(derived)if c['raw_cues']==[5]);x,y=derived[i:i+2]
        require(y['raw_cues']==[6]and x['screenshot_id']==y['screenshot_id']and x['scene_id']==y['scene_id']and x['word_end']==y['word_start'],'Billing sentence merge inputs changed.')
        combined=dict(x,end=y['end'],text=x['text']+' '+y['text'],raw_cues=[5,6],word_end=y['word_end'])
        merges.append({'raw_cues':[5,6],'start':combined['start'],'end':combined['end'],'text':combined['text'],'same_screenshot_id':x['screenshot_id'],'basis':'Exact adjacent sentence words on the same image; retain actual cue5 start and actual cue6 end to resolve original cue6 reading speed. No estimated time.'})
        derived[i:i+2]=[combined]
    # Only tiny derived pieces are merged, retaining exact words and the real
    # neighboring endpoint. Never merge across screenshots or scene changes.
    while derived and any(x['end']-x['start']<1.0 for x in derived):
        i=next(i for i,x in enumerate(derived)if x['end']-x['start']<1.0);x=derived[i]
        require(i+1<len(derived),'No genuine next cue for short caption.')
        y=derived[i+1];require(x['screenshot_id']==y['screenshot_id']and x['scene_id']==y['scene_id']and x['word_end']==y['word_start'],'Short caption needs new review; cannot merge different screens.')
        merged=dict(x,end=y['end'],text=x['text']+' '+y['text'],raw_cues=list(dict.fromkeys(x['raw_cues']+y['raw_cues'])),word_end=y['word_end'])
        merges.append({'raw_cues':merged['raw_cues'],'start':merged['start'],'end':merged['end'],'text':merged['text'],'same_screenshot_id':x['screenshot_id'],'basis':'Exact adjacent words, same actual image and scene; first real boundary through next real raw-cue endpoint. No resynthesis or timing interpolation.'});derived[i:i+2]=[merged]
    layout=[]
    for i,c in enumerate(derived,1):
        c['cue']=i;seconds=c['end']-c['start'];lines=textwrap.wrap(c['text'],48,break_long_words=False,break_on_hyphens=False);cps=len(c['text'])/seconds
        layout.append({'cue':i,'duration_seconds':round(seconds,3),'characters_per_second':round(cps,3),'proposed_lines':lines,'needs_review':seconds<1 or cps>22 or len(lines)>2})
    require(not derived or norm(' '.join(x['text']for x in derived))==script,'Derived captions changed words.')
    for x in spans:
        if x['end']['basis']=='decoded_audio_end':x['end']['seconds']=qa['audio']['duration_seconds'];x['end']['basis']='actual_full_PCM_decode_duration'
        if x['start']['seconds']is not None and x['end']['seconds']is not None:x['proposed_hold_seconds']=round(x['end']['seconds']-x['start']['seconds'],6)
    short=[{'span':x['span'],'capture_id':x['capture_id'],'seconds':x['proposed_hold_seconds'],'repeated_previous_source':i>0 and spans[i-1]['capture_id']==x['capture_id']}for i,x in enumerate(spans)if x.get('proposed_hold_seconds',99)<3]
    notes=cfg['notes']
    result={'kind':'PROPOSED actual take02 cue-to-screen correspondence; not final renderer inputs','lesson_id':name,'take':'02','frozen_source_sha256':cfg['pins'][(base/(name+'.narrated-source.json')).as_posix()],'audio_sha256':cfg['pins'][cfg['audio']],'decoded_duration_seconds':qa['audio']['duration_seconds'],'source_images':len(rows),'scenes':len(lesson['scenes']),'spoken_words':count,'raw_cues':len(raw),'proposed_derived_cues':len(derived),'source_spans':spans,'cue_correspondence':derived,'caption_layout':layout,'genuine_service_cuts':splits,'adjacent_same_image_caption_merges':merges,'missing_anchors':missing,'short_source_subspans':short,'limits_and_editorial_choices':notes,'genuine_marker_precision':'Service markers describe whole-second word groups. No millisecond word precision, interpolation or word-recognition claim.','audio_qa_passed':True,'complete_User_listening_approved':False,'parent_timing_review_pending':True,'final_renderer_plan_created':False,'assembly_render_canonical_site_target_browser_Descript_or_Git_operation':False}
    dependency_rows=[{'file':p,'sha256':h}for p,h in cfg['pins'].items()]+dependencies
    for row in rows.values():
        dependency_rows.extend({'file':row[f],'sha256':row[h]}for f,h in [('file','sha256'),('dom_file','dom_sha256')]if row.get(f))
    return result,dependency_rows


def srt(captions):
    def stamp(s):
        ms=round(s*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);sec,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{sec:02},{ms:03}'
    return ''.join(f"{x['cue']}\n{stamp(x['start'])} --> {stamp(x['end'])}\n{x['text']}\n\n"for x in captions).encode()


def outputs(alias):
    result,deps=propose(alias)
    screens=['PROPOSED source mapping; human listening/timing review pending. No final assembly.']
    for x in result['source_spans']:screens.append(f"{x['span']:02} | {x['scene_id']} | {x['start']['seconds']} -> {x['end']['seconds']} | {x['capture_id']}\nLabels: {json.dumps(x['required_labels'],ensure_ascii=False)}\n{x['exact_narration']}")
    captions=[f"{x['cue']:03} | {x['start']:.3f} -> {x['end']:.3f} | {x['screenshot_id']} | {x['text']}"for x in result['cue_correspondence']]
    readiness={'lesson_id':result['lesson_id'],'status':'PROPOSED source-only; human full listening and Root timing approval pending','raw_cues':result['raw_cues'],'derived_cues':result['proposed_derived_cues'],'source_spans':len(result['source_spans']),'missing_anchors':result['missing_anchors'],'caption_layout_flags':[x for x in result['caption_layout']if x['needs_review']],'short_source_subspans':result['short_source_subspans'],'full_PCM_derived_cue_QA':'pending separate actual measurement','actual_User_listening_receipt':'pending; not created or inferred','final_plan_or_render_or_ready':False,'choices_for_Root_review':result['limits_and_editorial_choices']}
    files={'correspondence.proposed.json':encoded(result),'input-pins.json':encoded({'files':deps}),'ordered-screens.compact.txt':('\n\n'.join(screens)+'\n').encode(),'cue-screen.compact.txt':('\n'.join(captions)+'\n').encode(),'readiness.proposed.json':encoded(readiness),'caption-derivation.json':encoded({'raw_cues_preserved':True,'raw_cue_count':result['raw_cues'],'proposed_derived_count':result['proposed_derived_cues'],'genuine_service_cuts':result['genuine_service_cuts'],'same_image_merges':result['adjacent_same_image_caption_merges'],'text_changes':False,'interpolated_times':False,'missing_anchors':result['missing_anchors'],'complete_User_listening_approved':False})}
    if result['cue_correspondence']:files['captions.proposed.srt']=srt(result['cue_correspondence'])
    return result,files


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--lesson',choices=['billing','shifts','all'],default='all');p.add_argument('--write-proposed',action='store_true');a=p.parse_args(argv)
    aliases=['billing','shifts']if a.lesson=='all'else[a.lesson];prepared=[(alias,*outputs(alias))for alias in aliases]
    if a.write_proposed:
        require(all(not (S/CONFIG[alias]['out']).exists()and not(S/CONFIG[alias]['out']).is_symlink()for alias,_,_ in prepared),'New-only proposal refuses existing output; preserve history.')
        for alias,_,files in prepared:
            folder=S/CONFIG[alias]['out'];folder.mkdir()
            for name,body in files.items():
                with (folder/name).open('xb')as f:f.write(body)
    print(json.dumps([{'lesson':result['lesson_id'],'raw_cues':result['raw_cues'],'proposed_cues':result['proposed_derived_cues'],'source_spans':len(result['source_spans']),'service_cuts':len(result['genuine_service_cuts']),'same_image_merges':len(result['adjacent_same_image_caption_merges']),'missing_anchors':len(result['missing_anchors']),'caption_layout_flags':sum(x['needs_review']for x in result['caption_layout']),'short_source_subspans':result['short_source_subspans'],'written':a.write_proposed,'final_plan_or_render':False}for _,result,_ in prepared],indent=2))


if __name__=='__main__':main()
