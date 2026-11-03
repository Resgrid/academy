"""Replace the stale closing hold with Root's inspected current saved summary.

The first render is preserved and never qualified. Script, audio, speech timings
and genuine User listening approval are unchanged. No encoded review is made.
"""
from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];S=R/'sources';sys.path.insert(0,str(R/'scripts'))
from verify_capture_evidence import instruction_scene_digest
from render_walkthrough import validate_inputs
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def put(p,d):
    assert not p.exists(),str(p)
    p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
name='core-deployment-time-expenses';now=datetime.now(timezone.utc).isoformat()
old=S/'expansion/plans'/f'{name}-complete-correspondence-20261102'
dest=old.with_name(old.name+'-v2');assert not dest.exists();dest.mkdir()
raw=S/'captures/expansion/core-deployment-administration-20261102/manifest.json'
row=deepcopy(next(r for r in read(raw) if r['id']=='033-current-draft-report-and-saved-expense-summary'))
assert sha(S/row['file'])==row['sha256']
dom=(S/row['file']).with_suffix('.txt')
row.update(dom_file=dom.relative_to(S).as_posix(),dom_sha256=sha(dom),eligible_for_lesson=True,review_status='actual_source_personally_reviewed',capture_review={'reviewer':'Root','reviewed_at':now,'passed':True,'sha256':row['sha256'],'method':'Root personally inspected the unchanged actual original capture033, showing3.5personnel hours,24.50USDexpenses and report2Draft together.'})
snapshot=dest/'raw-manifest.snapshot.json';snapshot.write_bytes(raw.read_bytes())
m=read(old/'captures.source-relative.json');m['screenshots'].append(row);m['raw_manifest']={'file':snapshot.relative_to(S).as_posix(),'sha256':sha(snapshot)};put(dest/'captures.source-relative.json',m)
d=read(old/'correspondence.proposed.json');newid=row['id'];scene=d['scenes'][-1]
assert scene['id']=='09' and scene['screens'][-1]['screenshot_id'].startswith('022-')
scene['screens'][-1]['screenshot_id']=newid
for c in scene['captions']:
    if c['cue']>=79:c['screenshot_id']=newid
d['holds'][-1]['screenshot_id']=newid
for c in d['cues']:
    if c['cue']>=79:c['screenshot_id']=newid
rows={r['id']:r for r in m['screenshots']};scene['proposed_mapping_sha256']=instruction_scene_digest(scene,rows)
d['source_images']=len(rows);d['distinct_source_images']=len({r['sha256'] for r in rows.values()})
d['context_notes'].append('The original take01 closing source022 showed the pre-expense0.00summary. Take02 uses personally inspected current source033 with24.50USDand the saved Draft report.')
put(dest/'correspondence.proposed.json',d)
l=read(old/'lesson.learner-projection.proposed.json');l['scenes'][-1]['capture_refs']=list(dict.fromkeys(h['screenshot_id'] for h in d['holds'] if h['scene_id']=='09'));put(dest/'lesson.learner-projection.proposed.json',l)
(dest/'caption-layout-measurements.json').write_bytes((old/'caption-layout-measurements.json').read_bytes())
root=read(old/'root-complete-correspondence-review.json');root.update(reviewed_at=now,correspondence_sha256=sha(dest/'correspondence.proposed.json'),learner_projection_sha256=sha(dest/'lesson.learner-projection.proposed.json'),method='Root retained the actual complete80-cue review and personally inspected the new closing screenshot033. Only cues79–80change from the stale pre-expense source022 to the current3.5personnel-hour/24.50USD/Draft summary. Script, audio, cue times and all other reviewed holds are unchanged.');put(dest/'root-complete-correspondence-review.json',root)
oldinputs=S/'expansion/plans'/f'{name}-take-01-final-inputs-20261102';newinputs=S/'expansion/plans'/f'{name}-take-02-final-inputs-20261102';assert not newinputs.exists();newinputs.mkdir()
put(newinputs/'captures.reviewed.json',m);(newinputs/'captions.actual.corrected.srt').write_bytes((oldinputs/'captions.actual.corrected.srt').read_bytes())
plan=read(oldinputs/'plan.json');plan['capture_manifests']=[{'file':(newinputs/'captures.reviewed.json').relative_to(S).as_posix(),'sha256':sha(newinputs/'captures.reviewed.json')}]
plan['captions']['file']=(newinputs/'captions.actual.corrected.srt').relative_to(S).as_posix()
plan['screenshot_reviews'][newid]={'reviewer':'Root','reviewed_at':now,'sha256':row['sha256'],'application_visible':True,'labels_legible':True,'no_errors':True}
reviewfile=dest/'root-complete-correspondence-review.json';plan['parent_correspondence_review']={'file':reviewfile.relative_to(S).as_posix(),'sha256':sha(reviewfile)}
reviewed=[]
for item,ps in zip(d['scenes'],plan['scenes']):
    sc=deepcopy(item);digest=sc.pop('proposed_mapping_sha256');assert instruction_scene_digest(sc,rows)==digest
    sc['instruction_review']={'reviewer':'Codex /root','reviewed_at':now,'passed':True,'correspondence_reviewed':True,'no_unseen_controls':True,'mapping_sha256':digest,'evidence_file':reviewfile.relative_to(S).as_posix(),'evidence_sha256':sha(reviewfile)}
    ps['screens']=deepcopy(sc['screens']);ps['captions']=[{k:c[k] for k in ['cue','screenshot_id','required_labels','spoken_references','instructional']} for c in sc['captions']];ps['instruction_review']=sc['instruction_review'];reviewed.append(sc)
put(newinputs/'scenes.reviewed.json',reviewed);put(newinputs/'plan.json',plan)
validate_inputs(S/d['lesson_file'],newinputs/'plan.json',S)
put(S/'expansion/rendered'/f'{name}-take-01/rejected-closing-frame-20261102.json',{'reviewer':'Root','reviewed_at':now,'qualified':False,'reason':'Final closing hold used historical source022with0.00expenses after the saved24.50expense. Replaced by actual source033in take02.','narration_and_captions_changed':False})
put(newinputs/'provenance.json',{'strict_renderer_inputs_passed':True,'replacement_source_id':newid,'replacement_source_sha256':row['sha256'],'original_master_preserved':True,'narration_unchanged':True,'genuine_User_listening_receipt_unchanged':True,'final_frame_and_playback_reviews_pending':True})
print(json.dumps({'take02_inputs_passed':True,'holds':len(d['holds']),'cues':len(d['cues']),'source_screens':len(rows)}))
