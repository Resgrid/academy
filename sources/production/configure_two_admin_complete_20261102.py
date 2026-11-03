"""Bind the two completed narration exports to unchanged, reviewed UI captures."""
from pathlib import Path
import hashlib
import json

S = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
CONFIG = {}
for key, name, folder, count in [
    ('routes', 'core-route-activation-start', 'core-route-activation-start-source-20261102-v2', 71),
    ('weather', 'core-weather-alert-policy', 'core-weather-alert-policy-source-20261102', 66),
]:
    base = S/'expansion/plans'/folder
    audio = S/'expansion/audio'
    proposed = json.loads((base/'cue-map.proposed.json').read_text())
    manifest = json.loads((base/'captures.reviewed.json').read_text())
    number = lambda row: int(row['id'].split('-')[3]) if key == 'routes' else int(row['id'][:3])
    by_id = {row['id']: number(row) for row in manifest['screenshots']}
    CONFIG[key] = dict(name=name, source_folder=folder,
        source_sha256=sha(base/'lesson.candidate.json'), captures_sha256=sha(base/'captures.reviewed.json'),
        audio_sha256=sha(audio/(name+'.m4a')), captions_sha256=sha(audio/(name+'.actual.corrected.srt')),
        qa_sha256=sha(audio/(name+'.actual.qa.json')), cues=count, additional_labels={}, scene_apps={}, supporting_applications=[],
        spans=[[r['scene_id'], r['first_cue'], r['last_cue'], by_id[r['screenshot_id']]] for r in proposed['holds']],
        context_notes=proposed['notes'] + [
            'All original screenshots and actual generated speech cue boundaries are preserved.',
            'Prepared values, successful saves, fresh returned states and refused operations remain distinct.',
            'Full source audio decode, signal/caption checks passed; genuine listening and encoded/browser review are separate requirements.'])

CONFIG['routes']['refs'] = {
    1: {'Edit Route Plan':'Edit', 'Name':'Name', 'Description':'Description'},
    3: {'TRAINING ONLY - Community supply loop':'Community supply loop'},
    5: {'Unit':'Unit', '-- Assign at start time --':'Assign at start time', 'Status':'Status', 'Draft':'Draft'},
    9: {'Status':'Status', 'Active':'Active'}, 10: {'Save Changes':'Save Changes'},
    11: {'Active':'Active', 'TRAINING ONLY - Community supply loop':'Community supply loop'}, 12: {'Start':'Start'},
    16: {'Start':'Start'}, 17: {'Assign Unit':'Assign Unit'},
    19: {'TRAINING ONLY - Community van 20261028':'Community van'},
    22: {'Start Route Now':'Start Route Now'}, 23: {'Cancel':'Cancel'}, 24: {'Start Route Now':'Start Route Now'},
    25: {'InProgress':'In Progress', 'Instance Info':'Instance Info'}, 26: {'Unit':'unit', 'Started':'Started'},
    27: {'51008':'unit number'}, 28: {'51008':'fifty-one thousand eight'},
    29: {'Ended':'Ended', 'Progress':'Progress', '0 / 2':'zero of two'},
    32: {'Stop Timeline':'Stop Timeline'}, 33: {'Pending':'Pending'}, 34: {'0 / 2':'zero of two'},
    40: {'Routes':'Routes', 'In Progress':'In Progress'},
    41: {'TRAINING ONLY - Community supply loop':'Community supply loop', 'Unit':'unit number'},
    42: {'0 / 2':'zero-of-two'}, 43: {'View Details':'View Details'},
    44: {'InProgress':'In Progress', 'Started':'start time'},
    47: {'History':'History', 'TRAINING ONLY - Community supply loop':'Community supply loop'},
    48: {'Route History - TRAINING ONLY - Community supply loop':'Route History', 'Status':'Status', 'Unit':'Unit'},
    49: {'Started':'Started', 'Ended':'Ended', 'Stops':'Stops'}, 50: {'InProgress':'In Progress'},
    51: {'0 / 2':'zero of two'}, 52: {'Detail':'Detail'},
    55: {'TRAINING ONLY - Community van 20261028':'Community van'}, 57: {'Start Route Now':'Start Route Now'},
    58: {'Unit already has an active route instance.':'Unit already has an active route instance'},
    63: {'Cancel':'Cancel'}, 64: {'InProgress':'In Progress'}, 65: {'0 / 2':'zero of two'},
}
CONFIG['weather']['refs'] = {
    1: {'Weather Alerts':'Weather Alerts'}, 2: {'Settings':'Settings', 'View History':'View History'},
    3: {'No active weather alerts for your department.':'no active weather alerts'},
    4: {'Notification Settings':'Notification Settings'},
    9: {'Enable Weather Alerts':'Enable Weather Alerts', 'Minimum Severity to Display':'Minimum Severity to Display'},
    11: {'Severe':'Severe'}, 14: {'Minimum Severity to Display':'display threshold'},
    17: {'Auto-Message Severity Threshold':'Auto-Message Severity Threshold'},
    18: {'Extreme':'Extreme', 'Severe':'Severe', 'Moderate':'Moderate', 'Minor':'Minor', 'Unknown':'Unknown'},
    19: {'Enabled':'Enabled', 'Start Hour':'Start Hour', 'End Hour':'End Hour'},
    20: {'Enabled':'Enabled'}, 21: {'Extreme':'Extreme', '18':'eighteen', '6':'six'},
    24: {'0':'Zero', '24':'twenty-four'}, 25: {'Enabled':'Enabled'},
    26: {'Excluded Alert Events':'Excluded Alert Events'}, 29: {'TRAINING ONLY - Practice alert':'Practice alert'},
    34: {'Attach Weather Context to Calls':'Attach Weather Context to Calls'}, 41: {'Attach Weather Context to Calls':'option'},
    42: {'Save Settings':'Save Settings'}, 43: {'Minimum Severity to Display':'Minimum Severity to Display'},
    44: {'Severe':'Severe'}, 45: {'Enable Weather Alerts':'Enable Weather Alerts'},
    50: {'Save Settings':'Save Settings'}, 51: {'Settings saved successfully.':'Settings saved successfully'},
    52: {'Moderate':'Moderate'}, 53: {'Enable Weather Alerts':'Weather Alerts'},
    54: {'Enabled':'unchecked'}, 55: {'Start Hour':'hours', 'End Hour':'hours'},
    56: {'TRAINING ONLY - Practice alert':'fictional exclusion'},
    57: {'Attach Weather Context to Calls':'call-context control'},
    59: {'Alert Sources':'Alert Sources', 'No weather alert sources configured. Add a source to start receiving weather alerts.':'no weather alert sources are configured'},
}

destination = S/'production/two_admin_complete_inputs_20261102.json'
assert not destination.exists()
destination.write_text(json.dumps(CONFIG, indent=2, ensure_ascii=False)+'\n')
template = (S/'production/prepare_route_plan_stops_complete_20261102.py').read_text()
old = S/'production/route_plan_stops_complete_inputs_20261102.json'
template = template.replace(old.name, destination.name).replace(sha(old), sha(destination))
template = template.replace("numbered={int(row['id'][:3]):row for row in rows.values()}",
    "numbered={(int(row['id'].split('-')[3]) if name == 'core-route-activation-start' else int(row['id'][:3])):row for row in rows.values()}")
output = S/'production/prepare_two_admin_complete_20261102.py'
assert not output.exists()
output.write_text(template)
