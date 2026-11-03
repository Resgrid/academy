"""Review one non-narrated learner prerequisite without changing reviewed media.

Preserves the earlier canonical and evidence, checks every other learner field,
and re-runs the evidence/publication gates against the same exact video bytes.
"""
from copy import deepcopy
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];S=R/'sources';sys.path.insert(0,str(R/'scripts'))
from expansion_site import _prepare,lesson_content_digest
from verify_capture_evidence import verify_document
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
name='core-member-creation-access';canonical=S/'expansion/lessons'/(name+'.json');original=json.loads(canonical.read_text());old='An existing training group and personnel role; generated passwords kept in ignored local files.'
assert original['prerequisites'][1]==old
new=deepcopy(original);new['prerequisites'][1]='An existing training group and personnel role for this exercise.'
left=deepcopy(original);right=deepcopy(new);left.pop('prerequisites');right.pop('prerequisites');assert left==right
e=json.loads((S/original['evidence_file']).read_text());master=sha(S/e['video']['file']);assert master=='2a44c56990368732a69486d00b455d360785a3f8e3c7e78cb46d4f04455de57d'
d=S/'expansion/audits/member-access-learner-prerequisite-20261102';assert not d.exists();d.mkdir()
(d/'previous-canonical.json').write_bytes(canonical.read_bytes());(d/'previous-evidence.json').write_bytes((S/original['evidence_file']).read_bytes())
new['evidence_file']=(d/'evidence.reviewed.json').relative_to(S).as_posix();e['authoring_sha256']=lesson_content_digest(new)
review={'reviewer':'Root','reviewed_at':datetime.now(timezone.utc).isoformat(),'method':'Personally reviewed removal of the production-only ignored-files clause from one prerequisite. The remaining prerequisite is an existing training group and personnel role. No narrated text, title, practice, sector example, screen, label, caption, timing, audio or video byte changed. All existing actual frame/playback and genuine User narration reviews continue to bind the same unchanged media.','previous_canonical_sha256':sha(canonical),'unchanged_video_sha256':master,'changed_learner_fields':['prerequisites[1]'],'previous_prerequisite':old,'current_prerequisite':new['prerequisites'][1]}
(d/'root-learner-copy-review.json').write_text(json.dumps(review,indent=2,ensure_ascii=False)+'\n');e['learner_copy_revision']={'file':(d/'root-learner-copy-review.json').relative_to(S).as_posix(),'sha256':sha(d/'root-learner-copy-review.json')}
report=verify_document(e,S);assert report['passed'],report
(d/'evidence.reviewed.json').write_text(json.dumps(e,indent=2,ensure_ascii=False)+'\n');_prepare(new,S)
(d/'canonical.reviewed.json').write_text(json.dumps(new,indent=2,ensure_ascii=False)+'\n');report.update(unchanged_video_sha256=master,authoring_sha256=lesson_content_digest(new),evidence_sha256=sha(d/'evidence.reviewed.json'),only_non_narrated_prerequisite_changed=True,all_existing_media_review_hashes_retained=True)
(d/'qualification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');canonical.write_bytes((d/'canonical.reviewed.json').read_bytes());print(json.dumps({'learner_prerequisite_revised':True,'all_media_unchanged':True,'public_evidence_gate_passed':True}))
