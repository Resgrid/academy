"""Retain the manually reviewed Call/Dispatch take01 correspondence.

This is a historical authoring recipe, not an automatic visual reviewer. Source
images were inspected on 2026-10-27; rerunning preserves that review timestamp.
Changed narration, timing, source provenance or pixels require a new review/take.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from render_walkthrough import load_cues, words
from render_public_media import stamp
from verify_capture_evidence import instruction_scene_digest

NAME = 'core-call-dispatch-settings'
REVIEWED_AT = '2026-10-27T16:01:44Z'
FROZEN = '33c09d43e37180c77a93e81b20027e4bf8cec484fe9eceece0bb692b7d9df6d4'
INPUTS = {
    'expansion/plans/core-call-dispatch-settings.captures.json': '87126cc20e01aa194b6f80693d4a10facb623585efef0e7745b6d0f93b309a4e',
    'expansion/plans/core-nearest-dispatch.captures.json': '5773ee4f60600257e8cc90e62196a6f218e8a378d451b64664df95676ef67f0c',
    'captures/expansion/core-call-settings-supplement-20261027/manifest.json': 'bdaa094f1810784e41f0c4a92400914c1995d547a668378be2ae3bece3dabc4c',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def retain(path, body):
    if path.exists() and path.read_text() != body:
        raise ValueError('Refusing to replace a different existing authoring output: ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)


def json_body(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'


def build(root):
    assets = root / 'sources'
    lesson_path = assets / 'expansion/plans/core-call-dispatch-settings.narrated-source.json'
    assert digest(lesson_path) == FROZEN
    lesson = json.loads(lesson_path.read_text())
    canonical = json.loads((assets / 'expansion/lessons/core-call-dispatch-settings.json').read_text())
    assert canonical['scenes'] == lesson['scenes'], 'Authored scenes changed; review a new take.'
    audio = assets / 'expansion/audio/core-call-dispatch-settings.m4a'
    assert digest(audio) == '3b48162a659fd475b5924dced0c52c3c9386ef65eebd074fb27906f09cbc10d3'
    qa_path = assets / 'expansion/audio/core-call-dispatch-settings-qa.json'
    qa = json.loads(qa_path.read_text())
    assert qa['passed'] and qa['silent_raw_cues'] == 0
    assert qa['lesson']['sha256'] == FROZEN
    source_srt = assets / 'expansion/audio/core-call-dispatch-settings-corrected.srt'
    raw = load_cues(source_srt)
    assert len(raw) == 112
    transcript_path = assets / 'expansion/audio/core-call-dispatch-settings-one-second.txt'
    transcript = transcript_path.read_text()
    assert re.search(r'\[00:04:47\]\s+station\b', transcript)
    assert re.search(r'\[00:05:29\]\s+corresponding\b', transcript)

    records = {}
    for name, expected in INPUTS.items():
        path = assets / name
        assert digest(path) == expected, 'Source capture manifest changed: ' + name
        doc = json.loads(path.read_text())
        for row in doc if isinstance(doc, list) else doc.get('screenshots', doc.get('captures', [])):
            if row['id'] in records:
                assert row['sha256'] == records[row['id']]['sha256']
            records[row['id']] = copy.deepcopy(row)

    # Literal text subsets read from actual pictured viewports. Broad older DOM
    # inventories remain unchanged in INPUTS; offscreen text is not reused here.
    literal = {
        'core-config-037-call-settings-import-prune-readonly': ['Call Settings', 'Dispatch Import Email', 'Prune (Auto Close) Calls', 'Minutes to keep call open', 'Email Type', 'GENERIC'],
        'core-config-038-call-number-format-preserved': ['Call Numbering', 'Call number pattern', 'Sequence digits'],
        'core-config-039-call-number-next-after-responder': ['Call number pattern', 'Sequence digits', 'Numbering year starts', 'January', 'Next call number', 'Raise next sequence to', 'Update'],
        'core-config-040-dispatch-group-settings-readonly': ['Call & Dispatch Settings', 'Group Dispatch Settings', 'Use Shift for Group Dispatch', 'Set Status for Shift Personnel On Dispatch', 'Person Call Dispatch Status', 'Person Call Release Status'],
        'core-config-048-group-scope-roles-readonly': ['Group-Scoped Dispatch', 'Scope Dispatch to Group Areas', 'Department-Wide Dispatch Roles'],
        'core-nearest-group-boundary-editor': ['Group Boundary', 'Name', 'Firehouse 51', 'District Color', 'Geofence'],
        'core-config-041-dispatch-unit-settings-readonly': ['Unit Dispatch Settings', 'Also Dispatch To Assigned Personnel', 'Also Dispatch To Entire Group', 'Unit Call Dispatch Status', 'Unit Call Release Status'],
        'core-config-049-unit-release-status-rules': ['Unit Dispatch Settings', 'Also Dispatch To Assigned Personnel', 'Also Dispatch To Entire Group', 'Unit Call Dispatch Status', 'Unit Call Release Status', 'Personnel on Unit Set Unit Status', 'Hold to set status'],
        'core-config-057-engine-type-icon-baseline': ['Edit Unit Type', 'Unit Type Name', 'Engine', 'Actions (Custom Unit Statuses)', 'Standard Actions'],
        'core-config-042-dispatch-close-timer-run-card-settings': ['Close call when last unit clears', 'Check-In Timer Settings', 'Auto-Enable Check-In Timers for New Calls', 'Run Cards & Automatic Dispatch', 'Automatic resource selection mode', 'Closest Unit Response', 'Automatically dispatch recommended resources'],
        'core-config-043-dispatch-closest-tuning-readonly': ['Rest period (minutes)', 'Minimum unit staffing to dispatch', 'Enable move-up / backfill recommendations', 'Closest Unit Response Tuning', 'Maximum unit location age (seconds)', 'Maximum personnel location age (seconds)', 'Maximum response radius (meters)', 'Include stale locations', 'Order by driving ETA'],
        'core-config-050-turnout-waiting-call-readonly': ['Closest Unit Response Tuning', 'Maximum unit location age (seconds)', 'Maximum personnel location age (seconds)', 'Maximum response radius (meters)', 'Include stale locations', 'Order by driving ETA', 'ETA shortlist size', 'In-quarters turnout (seconds)', 'Mobile turnout (seconds)', 'Personnel turnout (seconds)'],
        'core-config-051-response-code-options-empty': ['Dispatch freed units to calls awaiting them', 'Automatic dispatch limit (seconds, 0 = none)', 'Response codes', 'Code', 'Name', 'Colour', 'Retired', 'Show codes to crews (unit push and field apps)', 'Add code'],
        'core-nearest-near-turnout-with-officer-crew': ['Unit', 'Status', 'ETA', 'Position', 'Shift Coverage', 'Role Mix', 'Engine 51', 'Reserve Engine 51', 'Out of Service'],
        'core-config-047-default-timers-empty-preserved': ['Station Coverage Minimums', 'Save', 'Default Timer Configurations', 'Target Type', 'Unit Type', 'Duration (minutes)', 'Warning Threshold (minutes)', 'Enabled', 'Active States', 'Add New Default Timer'],
        'core-config-069-investigation-personnel-timer-override': ['Add Timer Config', 'Call Type / Priority Overrides', 'Investigation', 'Personnel', '60', '5', 'Yes', 'All', 'Add New Override'],
        'core-responder-eligible-boden-timer': ['Check-In Timers', 'Wallace Boden', 'Check In', 'Show Check-In History'],
        'core-config-046-station-coverage-empty-baseline': ['Station Coverage Minimums', 'Station', 'Unit Type / Role', 'Minimum Available', 'Radius (meters, closest-unit mode)', 'Save'],
        'core-config-044-new-call-visible-required-fields': ['New Call Form Fields', 'Visible', 'Required', 'Address', 'GPS Coordinates', 'what3words', 'Plus Code', 'Destination'],
        'core-config-045-new-call-lower-field-rules': ['Note', 'Reporter Name', 'Reporter Contact Info', 'External Call ID', 'Incident ID', 'Reference ID', 'Protocols', 'Linked Call', 'Scheduled Dispatch', 'Dispatch Recipients', 'Save', 'Cancel'],
        'core-nearest-saved-call-dispatched-resources': ['Dispatched', 'Engine 51', 'Christopher Herrmann', '26-4'],
        'core-nearest-training-close-without-notification': ['Close Call', 'Completed Type', 'Closed', 'Send Notification', 'Completed Notes'],
        'core-nearest-training-call-closed-history': ['View Call', 'Closed', '26-4', 'Completed Notes:'],
        'core-nearest-unit-staffing-saved-officer': ['Unit Staffing', 'Engine 51', 'Officer / Team Lead', 'Christopher Herrmann', 'Fully Staffed', 'Save', 'Cancel'],
        'core-nearest-new-call-basics': ['New Call', 'Name', 'Priority', 'Routine', 'Type', 'Rescue'],
        'core-call-settings-call-level-timer-flag': ['Check-In Timers', 'Enable Check-In Timers', 'ReDispatch', 'Notify Cancelled', 'Update'],
        'core-call-settings-current-shift-roster': ['On Duty Now', 'A Shift — Firehouse 51', 'Firehouse 51', 'Command', 'Truck 81', 'Squad 3', 'Ambulance 61', 'Engine 51', 'Christopher Herrmann'],
        'core-call-settings-unit-status-history': ['Events for Engine 51', 'State', 'Destination', 'Timestamp', 'Note', 'Responding', 'Released'],
    }
    selected = {}
    for ident, labels in literal.items():
        row = records[ident]
        assert digest(assets / row['file']) == row['sha256']
        row['visible_labels'] = labels
        row['viewport_review'] = {'reviewer': 'Codex', 'reviewed_at': REVIEWED_AT, 'sha256': row['sha256'], 'method': 'Original genuine screenshots reviewed in full-size QA sheets; supplemental flag/roster/history and reused staffing/call forms also viewed individually at original resolution. Only literal viewport text retained; raw manifests remain unchanged.'}
        selected[ident] = row
    capture_path = assets / 'expansion/plans/core-call-dispatch-settings-take-01.captures.json'
    retain(capture_path, json_body({'app': 'Core', 'screenshots': list(selected.values()), 'source_manifests': INPUTS, 'reviewed_at': REVIEWED_AT, 'scope': 'Viewport text subsets, unchanged original images; historical training states and separate current read-only examples.'}))

    def config(number):
        return next(k for k in selected if k.startswith('core-config-' + number + '-'))

    # Explicit screenshot choices for every unchanged original speech cue.
    ranges = [
        (1,9,config('037')), (10,11,config('038')), (12,14,config('039')), (15,16,config('037')),
        (17,24,config('040')), (25,26,'core-call-settings-current-shift-roster'),
        (27,33,config('048')), (34,34,'core-nearest-group-boundary-editor'), (35,36,'core-nearest-near-turnout-with-officer-crew'),
        (37,39,config('041')), (40,45,config('049')), (46,46,config('057')), (47,48,'core-nearest-unit-staffing-saved-officer'),
        (49,57,config('049')), (58,59,config('042')), (60,64,config('043')), (65,66,config('050')),
        (67,70,config('051')), (71,71,'core-nearest-near-turnout-with-officer-crew'),
        (72,72,config('042')), (73,73,config('047')), (74,76,config('069')), (77,77,'core-call-settings-call-level-timer-flag'),
        (78,79,'core-responder-eligible-boden-timer'), (80,80,config('069')), (81,82,config('046')),
        (83,85,config('044')), (86,87,config('045')), (88,89,config('044')), (90,90,config('045')), (91,91,'core-nearest-new-call-basics'),
        (92,94,'core-nearest-saved-call-dispatched-resources'), (95,96,'core-nearest-training-close-without-notification'),
        (97,97,'core-nearest-training-call-closed-history'), (98,100,config('049')), (101,101,'core-call-settings-unit-status-history'),
        (102,106,config('042')), (107,107,'core-nearest-training-call-closed-history'), (108,108,'core-nearest-unit-staffing-saved-officer'),
        (109,110,'core-call-settings-current-shift-roster'), (111,111,'core-nearest-near-turnout-with-officer-crew'), (112,112,'core-call-settings-unit-status-history'),
    ]
    screen_for = {}
    for first, last, ident in ranges:
        for number in range(first,last+1):
            assert number not in screen_for
            screen_for[number] = ident
    assert set(screen_for) == set(range(1,113))

    # Exact visible labels and explicitly reviewed natural speech references.
    refs = {
        1: {'Call Settings':'Call Settings'}, 2: {'Dispatch Import Email':'Dispatch Import Email'}, 4: {'Email Type':'Email Type','GENERIC':'Generic'},
        6: {'Prune (Auto Close) Calls':'Prune (Auto Close) Calls','Minutes to keep call open':'Minutes to keep call open'},
        10: {'Call Numbering':'Call Numbering'}, 11: {'Call number pattern':'saved pattern','Sequence digits':'sequence digits'}, 12: {'Next call number':'Next call number'},
        17: {'Call & Dispatch Settings':'Call & Dispatch Settings'}, 18: {'Use Shift for Group Dispatch':'Use Shift for Group Dispatch'},
        20: {'Set Status for Shift Personnel On Dispatch':'Set Status for Shift Personnel On Dispatch'},
        23: {'Person Call Dispatch Status':'Person Call status controls','Person Call Release Status':'Person Call status controls'},
        25: {'On Duty Now':'actual roster'}, 27: {'Group-Scoped Dispatch':'Group-Scoped Dispatch'}, 28: {'Scope Dispatch to Group Areas':'Scope Dispatch to Group Areas'},
        30: {'Department-Wide Dispatch Roles':'Department-Wide Dispatch'}, 34: {'Group Boundary':'Group Boundary'},
        36: {'Status':'status','Position':'position'}, 37: {'Also Dispatch To Assigned Personnel':'Also Dispatch To Assigned Personnel','Also Dispatch To Entire Group':'Also Dispatch To Entire Group'},
        40: {'Unit Call Dispatch Status':'Unit Call Dispatch Status','Unit Call Release Status':'Unit Call Release Status'},
        46: {'Actions (Custom Unit Statuses)':'Standard Actions'}, 47: {'Unit Staffing':'crew assignments'},
        49: {'Personnel on Unit Set Unit Status':'Personnel on Unit Set Unit Status'}, 52: {'Hold to set status':'Hold to set status'},
        58: {'Run Cards & Automatic Dispatch':'Run Cards & Automatic Dispatch','Closest Unit Response':'Closest Unit Response'},
        60: {'Rest period (minutes)':'Rest period'}, 61: {'Minimum unit staffing to dispatch':'staffing checks configured seats','Enable move-up / backfill recommendations':'move-up'},
        63: {'Closest Unit Response Tuning':'Closest Unit Response Tuning','Maximum unit location age (seconds)':'1800-second location ages','Maximum personnel location age (seconds)':'1800-second location ages'},
        64: {'Maximum response radius (meters)':'radius limit','Include stale locations':'stale locations excluded','Order by driving ETA':'routed ETA off'},
        65: {'ETA shortlist size':'shortlist'}, 66: {'In-quarters turnout (seconds)':'Station turnout','Mobile turnout (seconds)':'mobile','Personnel turnout (seconds)':'personnel turnout'},
        67: {'Dispatch freed units to calls awaiting them':'Freed-unit automatic dispatch','Automatic dispatch limit (seconds, 0 = none)':'its limit'},
        69: {'Response codes':'Response codes','Name':'name','Colour':'colour','Retired':'retirement','Show codes to crews (unit push and field apps)':'crew-display'},
        72: {'Auto-Enable Check-In Timers for New Calls':'Auto-Enable Check-In Timers for New Calls'}, 73: {'Default Timer Configurations':'Default Timer Configurations'},
        74: {'Call Type / Priority Overrides':'override','Investigation':'Investigation','Personnel':'Personnel','60':'60 minutes','5':'warning five'},
        77: {'Enable Check-In Timers':'own timer flag'}, 78: {'Check-In Timers':'timer','Wallace Boden':'Boden'},
        81: {'Station Coverage Minimums':'Station Coverage Minimums'}, 82: {'Station':'station','Unit Type / Role':'target','Minimum Available':'count','Radius (meters, closest-unit mode)':'radius'},
        83: {'New Call Form Fields':'New Call Form Fields','Visible':'Visible','Required':'Required'}, 88: {'Plus Code':'Plus Code'}, 89: {'GPS Coordinates':'GPS Coordinates'},
        93: {'Dispatched':'Dispatched','Engine 51':'Engine 51','Christopher Herrmann':'Christopher Herrmann'},
        95: {'Close Call':'Close Call','Completed Type':'Completed Type','Completed Notes':'training notes'}, 96: {'Send Notification':'Send Notification'},
        97: {'Closed':'Closed'}, 98: {'Unit Call Release Status':'Release policy'}, 101: {'Events for Engine 51':'status history'},
        102: {'Close call when last unit clears':'Close call when last unit clears'}, 107: {'Closed':'manual closure'},
        108: {'Unit Staffing':'station crews'}, 109: {'On Duty Now':'rosters'}, 112: {'Events for Engine 51':'status history'},
    }
    expanded = []
    provenance = []
    for number, cue in enumerate(raw,1):
        pieces = [(cue['start'],cue['end'],cue['text'],screen_for[number],refs.get(number,{}))]
        if number in (80,90):
            when, phrase, second, first_refs, second_refs = (
                (287.0,'station coverage',config('046'),{'Add Timer Config':'Add controls'},{'Save':'Save'})
                if number == 80 else
                (329.0,'corresponding call form','core-nearest-new-call-basics',{}, {'New Call':'corresponding call form'})
            )
            before, separator, after = cue['text'].partition(phrase)
            assert separator and cue['start'] < when < cue['end']
            pieces = [(cue['start'],when,before.strip(),screen_for[number],first_refs),(when,cue['end'],separator+after,second,second_refs)]
            provenance.append({'original_cue':number,'cut_seconds':when,'before_exact_phrase':phrase,'measurement':'Genuine Descript TXT one-second anchor; declared1second granularity, no interpolated word timing.'})
        for start,end,text,ident,references in pieces:
            expanded.append({'start':start,'end':end,'text':text,'screenshot_id':ident,'required_labels':list(references),'spoken_references':references,'instructional':bool(references),'original_cue':number})
    assert len(expanded) == 114
    assert words(' '.join(c['text'] for c in expanded)) == words(' '.join(s['narration'] for s in lesson['scenes']))
    srt = ''.join(f"{i}\n{stamp(c['start'],True)} --> {stamp(c['end'],True)}\n{c['text']}\n\n" for i,c in enumerate(expanded,1))
    caption_path = assets / 'expansion/audio/core-call-dispatch-settings-screen-cuts.srt'
    retain(caption_path,srt)
    retain(assets / 'expansion/audio/core-call-dispatch-settings-screen-cuts-provenance.json',json_body({'lesson_sha256':FROZEN,'source_corrected_srt_sha256':digest(source_srt),'genuine_one_second_txt_sha256':digest(transcript_path),'raw_cues':112,'derived_cues':114,'splits':provenance,'audio_sha256':digest(audio),'no_speech_words_or_original_outer_cue_bounds_changed':True}))

    groups=[];position=0
    for authored in lesson['scenes']:
        expected=words(authored['narration']);actual=[];entries=[]
        while len(actual)<len(expected):
            cue=expanded[position];actual+=words(cue['text']);position+=1;entries.append(dict(cue,cue=position))
        assert actual==expected,authored['id']
        groups.append((authored,entries))
    duration=qa['audio']['duration_seconds'];scenes=[]
    for index,(authored,entries) in enumerate(groups):
        start=0 if index==0 else entries[0]['start'];end=duration if index==len(groups)-1 else groups[index+1][1][0]['start']
        screens=[]
        for number,cue in enumerate(entries):
            at=start if number==0 else cue['start']
            if not screens or screens[-1]['screenshot_id']!=cue['screenshot_id']:
                if screens:screens[-1]['end']=at
                screens.append({'screenshot_id':cue['screenshot_id'],'start':at,'end':end})
        built={'id':authored['id'],'title':authored['title'],'kind':'operational','start':start,'end':end,'visual_required_labels':authored['required_labels'],'screens':screens,'captions':entries}
        review={'passed':True,'reviewer':'Codex','reviewed_at':REVIEWED_AT,'correspondence_reviewed':True,'no_unseen_controls':True,'mapping_sha256':instruction_scene_digest(built,selected),'method':'Manual exact-cue/viewport correspondence reviewed against29 genuine images. Actual roster, call-level flag and status-history pages supplement settings. Two genuine1second transcript anchors split compound form instructions; no estimated word timing or outcome inferred.'}
        scenes.append({'id':authored['id'],'start':start,'end':end,'screens':screens,'captions':[{k:c[k] for k in ('cue','screenshot_id','required_labels','spoken_references','instructional')} for c in entries],'instruction_review':review})
    review_audio={'reviewer':'Codex','reviewed_at':REVIEWED_AT,'sha256':digest(audio),'complete_natural_narration':True,'method':'Established natural stock voice, complete generated11paragraph media, fullPCM decode/exact939word script and all112measured source cues passed. No human listening or pronunciation review is claimed.','qa_file':'expansion/audio/core-call-dispatch-settings-qa.json','qa_sha256':digest(qa_path)}
    plan={'schema_version':1,'lesson_id':NAME,'duration_seconds':duration,'instruction_mapping':'reviewed_scene_coverage','display_context':'TRAINING ONLY · fictional department',
          'narration':{'file':'expansion/audio/core-call-dispatch-settings.m4a','sha256':digest(audio),'kind':'approved_natural_narration','approval':review_audio},
          'captions':{'file':str(caption_path.relative_to(assets)),'sha256':digest(caption_path),'kind':'speech_timed_srt','approval':{'reviewer':'Codex','reviewed_at':REVIEWED_AT,'sha256':digest(caption_path),'audio_sha256':digest(audio),'speech_timing_reviewed':True,'method':'Original112actual speech cue boundaries retained except two documented genuine integer-second splits into114cues. Exact frozen words and order preserved; derivative signal/layout checks required before render.','timing_provenance':'expansion/audio/core-call-dispatch-settings-screen-cuts-provenance.json'}},
          'capture_manifests':[{'file':str(capture_path.relative_to(assets)),'sha256':digest(capture_path)}],
          'screenshot_reviews':{ident:{'reviewer':'Codex','reviewed_at':REVIEWED_AT,'sha256':row['sha256'],'application_visible':True,'labels_legible':True,'no_errors':True,'method':row['viewport_review']['method']} for ident,row in selected.items()},
          'scenes':scenes,'source_freeze':{'lesson_sha256':FROZEN,'spoken_words':939,'voice_source':'expansion/plans/core-call-dispatch-settings.narrated-source.json','original24_photo_manifest_sha256':INPUTS['expansion/plans/core-call-dispatch-settings.captures.json']},
          'limitations':['Source settings remain as recorded; optional group/native/automatic-close branches are conditional policy explanations, not claimed executions.','Roster and saved per-call flag were viewed read-only on2026-10-27. The flag remains stored on the nowclosed51009; its earlier active timer image is historical and does not prove an active timer after close.','Unit event history contains multiple training incidents, including currentResponding after51009. Its old location-map marker is not currentGPS proof or a claim of Released.','Engine FullyStaffed means one configured seat occupied; no physical crew readiness or qualifications established.','No provider/device receipt, external import, realGPS, consent attestation or new notification send was performed by this lesson.','Actual encoded interval/cue review and independent browser playback remain required before publication.']}
    path=assets / 'expansion/plans/core-call-dispatch-settings-take-01.plan.json';retain(path,json_body(plan))
    print(json.dumps({'plan':str(path.relative_to(root)),'sha256':digest(path),'scenes':len(scenes),'screen_intervals':sum(len(s['screens']) for s in scenes),'selected_images':len(selected),'cues':len(expanded),'duration_seconds':duration}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=ROOT)
    build(parser.parse_args().root.resolve())
