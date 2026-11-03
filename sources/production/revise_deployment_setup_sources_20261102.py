"""Retain the original source freeze and add the separately captured real Cancel control."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime, timezone
import hashlib,json
S=Path(__file__).resolve().parents[1];n='core-deployment-setup-roster'
old=S/'expansion/plans'/(n+'-source-20261102');out=old.with_name(old.name+'-v2')
assert not out.exists();out.mkdir()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
l=read(old/'lesson.candidate.json');l['scenes'][4]['capture_refs'].append('026-reopened-settings-agency-identifiers-and-cancel');put(out/'lesson.candidate.json',l)
(out/'narration.txt').write_bytes((old/'narration.txt').read_bytes())
raw=S/'captures/expansion/core-deployment-administration-20261102';snap=out/'raw-manifest.snapshot.json';snap.write_bytes((raw/'manifest.json').read_bytes());data=read(snap)
r=deepcopy(next(x for x in data if x['id'].startswith('026-')));dom=raw/(r['id']+'.txt');assert sha(S/r['file'])==r['sha256']
r.update(dom_file=dom.relative_to(S).as_posix(),dom_sha256=sha(dom),eligible_for_lesson=True,review_status='original_actual_screenshot_personally_reviewed',capture_review={'reviewer':'Root','passed':True,'reviewed_at':datetime.now(timezone.utc).isoformat(),'sha256':r['sha256'],'method':'Root personally inspected this original real Edit screenshot and its complete unobstructed Cancel and Save controls before normal Cancel. Source pixels are unchanged.'})
m=read(old/'captures.reviewed.json');m['screenshots'].append(r);m['raw_manifest']={'file':snap.relative_to(S).as_posix(),'sha256':sha(snap)};m['visual_only_revision']={'previous_source':old.relative_to(S).as_posix(),'previous_source_sha256':sha(old/'lesson.candidate.json'),'narration_unchanged':True,'audio_generation_unchanged':True,'reason':'Add the actual lower Edit viewport so the spoken Cancel step shows its own complete control.'};put(out/'captures.reviewed.json',m)
put(out/'source-review.json',{'reviewer':'Root','reviewed_at':datetime.now(timezone.utc).isoformat(),'retained_original_review_file':(old/'source-review.json').relative_to(S).as_posix(),'retained_original_review_sha256':sha(old/'source-review.json'),'new_original_image_personally_viewed':r['id'],'source_pixels_unchanged':True,'narration_unchanged':True,'final_video_review_inferred':False})
# Check source label coverage now, without inventing per-cue correspondence or audio approval.
import sys;sys.path.insert(0,str(S.parent/'scripts'));from verify_capture_evidence import _Validator,_normalized
rows={x['id']:x for x in m['screenshots']};v=_Validator(S);observed={k:v.observations(row,k) for k,row in rows.items()};assert not v.issues,v.issues
for scene in l['scenes']:
 missing={_normalized(x) for x in scene['required_labels']}-set().union(*(observed[k] for k in scene['capture_refs']))
 assert not missing,(scene['id'],missing)
print(json.dumps({'source_v2':out.relative_to(S).as_posix(),'source_images':len(rows),'all_scene_control_coverage':True,'narration_unchanged':True,'final_audio_and_video_reviews':'pending'}))
