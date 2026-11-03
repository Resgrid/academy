"""Replace small prepared-form images with reviewed actual wide UI replays.

The complete approved narration is unchanged. This does not create another
member, alter old freezes, or infer any encoded-frame/playback approval.
"""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json
S=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
name='core-member-creation-access';old=S/'expansion/plans'/(name+'-source-20261102');out=S/'expansion/plans'/(name+'-source-20261102-v2')
assert not out.exists()
raw=S/'captures/expansion/core-member-invitations-20261102';rows=json.loads((raw/'manifest.json').read_text());by={int(x['id'][:3]):x for x in rows};replacements={6:32,7:33,8:33,9:31,10:31}
l=json.loads((old/'lesson.candidate.json').read_text());m=json.loads((old/'captures.reviewed.json').read_text());old_screens={int(x['id'][:3]):x for x in m['screenshots']};selected=[]
for scene in l['scenes']:
 scene['capture_refs']=list(dict.fromkeys(by[replacements.get(int(ref[:3]),int(ref[:3]))]['id'] for ref in scene['capture_refs']))
 selected.extend(int(ref[:3]) for ref in scene['capture_refs'])
now=datetime.now(timezone.utc).isoformat();screens=[]
for n in sorted(set(selected)):
 row=deepcopy(by[n] if n in {31,32,33} else old_screens[n]);assert sha(S/row['file'])==row['sha256'];assert row['width']>=960 and row['height']>=540
 dom=raw/(row['id']+'.txt');row.update(dom_file=dom.relative_to(S).as_posix(),dom_sha256=sha(dom),eligible_for_lesson=True,review_status='actual_source_contact_sheet_reviewed',capture_review={'reviewer':'Root','passed':True,'reviewed_at':now,'sha256':row['sha256'],'method':'Root personally inspected the unchanged original and readable source contact sheet. New031–033 are unsaved prepared-form replays with masked passwords; no duplicate account was submitted. Saved/disabled/restored outcomes remain original recordings.'});screens.append(row)
l['scope_limits'].append('Sources031–033 replay the prepared fields in a readable landscape browser; no duplicate was submitted. Original successful member creation and saved state changes are independently retained.')
original=json.loads((old/'lesson.candidate.json').read_text());assert [x['narration'] for x in l['scenes']]==[x['narration'] for x in original['scenes']]
out.mkdir();(out/'raw-manifest.snapshot.json').write_bytes((raw/'manifest.json').read_bytes());manifest={'schema_version':1,'id':name,'screenshots':screens,'raw_manifest':{'file':(out/'raw-manifest.snapshot.json').relative_to(S).as_posix(),'sha256':sha(out/'raw-manifest.snapshot.json')},'excluded_sources':[{'id':r['id'],'sha256':r['sha256'],'reason':'Outside this bounded source selection; small original prepared-form images are replaced with the actual wide replays.'} for r in rows if int(r['id'][:3]) not in set(selected)]}
for file,obj in [('lesson.candidate.json',l),('captures.reviewed.json',manifest),('source-review.json',{'reviewer':'Root','reviewed_at':now,'actual_images_reviewed':[r['id'] for r in screens],'source_pixels_unchanged':True,'final_video_approval_inferred':False,'previous_source':old.relative_to(S).as_posix(),'narration_unchanged':True})]:
 (out/file).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
(out/'narration.txt').write_bytes((old/'narration.txt').read_bytes())
print(json.dumps({'lesson':name,'screens':len(screens),'narration_unchanged':True,'source':out.name}))
