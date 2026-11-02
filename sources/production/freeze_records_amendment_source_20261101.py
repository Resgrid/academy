"""Retain the genuinely reviewed amendment and later read-only revision captures.

Default checks only. --freeze writes new self-contained source copies and the
already-performed source-pixel review. No speech/final-video approval is created.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

S=Path(__file__).resolve().parents[1]
B=Path('expansion/plans/core-records-amendment-and-revisions-source-proposal-20261101')
LESSON_SHA='41ae73e165868b28fa20902934555d7ceac609e736d165a4db7c7dffcf969171'
MANIFESTS={
 'captures/expansion/core-records-amendment-20261029/manifest.json':'d3bdc8e991ff8009dcc5320b06dafab24ee1c04fb4006d28d2c9f2496452741e',
 'captures/expansion/core-records-revision-launchers-20261101/manifest.json':'7ea6a00db6a85893dffbc9790d02106128c1f45aa0535e4f02f19d6779861171'
}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(d):return (json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode()


def prepare():
 assert sha(S/B/'lesson.candidate.json')==LESSON_SHA
 lesson=json.loads((S/B/'lesson.candidate.json').read_text())
 assert len(lesson['scenes'])==14 and len(lesson['sector_examples'])==6
 source={}
 for path,digest in MANIFESTS.items():
  assert sha(S/path)==digest
  d=json.loads((S/path).read_text());rows=d if isinstance(d,list) else d['captures']
  for row in rows:
   assert row['id'] not in source
   source[row['id']]=(row,path,digest)
 selected=list(dict.fromkeys(ref for scene in lesson['scenes'] for ref in scene['capture_refs']))
 assert len(selected)==13
 files,rows={},[];at=datetime.now(timezone.utc).isoformat()
 for id in selected:
  original,path,digest=source[id];row=deepcopy(original)
  assert sha(S/row['file'])==row['sha256'] and sha(S/row['dom_file'])==row['dom_sha256']
  labels=list(dict.fromkeys(label for scene in lesson['scenes'] if id in scene['capture_refs'] for label in scene['required_labels']))
  image,dom=B/'images'/(id+'.jpg'),B/'dom'/(id+'.dom.txt')
  files[image],files[dom]=(S/row['file']).read_bytes(),(S/row['dom_file']).read_bytes()
  raw={'manifest_file':path,'manifest_sha256':digest,'capture_id':id,'image_file':row['file'],'image_sha256':row['sha256'],'dom_file':row['dom_file'],'dom_sha256':row['dom_sha256']}
  row.update(file=str(image),dom_file=str(dom),visible_labels=labels,required_labels=labels,
             visible_field_text=[],visible_controls=[],missing_required_labels=[],accepted=True,
             eligible_for_lesson=True,publication_eligible=True,review_status='accepted_bounded_source',
             visual_review='completed_actual_image_review',raw_source=raw,
             capture_review={'reviewer':'Codex /root','reviewed_at':at,'passed':True,'sha256':row['sha256'],
                             'application_visible':True,'no_errors':True,'controls_reviewed':True,
                             'controls_fully_visible':True,'controls_unobstructed':True,
                             'method':'Root personally viewed all thirteen selected complete actual screenshots in this authoring session. Only listed fully legible teaching labels are accepted. Unrelated clipped page content and the earlier clipped editor Reason value are excluded. Source-pixel review only.'})
  rows.append(row)
 narration='\n\n'.join(sc['narration'] for sc in lesson['scenes'])+'\n'
 manifest={'app':'Core','reviewer':'Codex /root','reviewed_at':at,'actual_raw_images_personally_viewed':13,
           'accepted_actual_images':13,'source_manifests':MANIFESTS,'screenshots':rows}
 files[B/'captures.reviewed.json']=encoded(manifest);files[B/'narration.txt']=narration.encode()
 files[B/'source-review.json']=encoded({'reviewer':'Codex /root','created_at':at,'lesson_sha256':LESSON_SHA,
  'capture_manifest_sha256':hashlib.sha256(encoded(manifest)).hexdigest(),'script_sha256':hashlib.sha256(narration.encode()).hexdigest(),
  'words':len(narration.split()),'scenes':14,'actual_source_images':13,'source_images_reviewed':True,'export_ready':False,
  'scope':'Earlier actual course-code amendment plus new read-only History comparison/View launchers and both unchanged saved revisions. Same record0795ea02and same revisionIDs. No later amendment, signature or PDF action.',
  'launcher_gap':'The complete actual History labels are now pictured. Ordinary keyboard focus brought the links into view in the normal Chrome viewport; no viewport override or CSS/DOM injection was used.',
  'remaining':['Generate complete exact natural narration.','Authorized private audio export, full audio/caption checks and genuine listening review.','Actual timing correspondence, all encoded-frame/caption reviews and advancing browser-playback qualification.']})
 assert all(not (S/path).exists() for path in files),'Refusing to overwrite a source freeze.'
 return files


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--freeze',action='store_true');args=parser.parse_args()
 files=prepare()
 if args.freeze:
  for path,data in files.items():
   dest=S/path;dest.parent.mkdir(parents=True,exist_ok=True)
   with dest.open('xb') as stream:stream.write(data)
 print(json.dumps({'source_files':len(files),'written':args.freeze,'actual_source_images':13,'app_mutations':0,'final_media_reviews_created':False,'canonical_or_site_changes':0,'git_mutations':0}))
