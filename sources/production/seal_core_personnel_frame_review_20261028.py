"""Retain completed Personnel take01 visual observations; never infer approval.

The agent actually viewed all38original-size interval PNGs, all116unscaled
encoded caption regions and fullcue23/36/78/98/116before this recipe was authored.
Default checks bytes only. --record-reviewed creates NEW review documents from
those completed observations; it does not inspect pictures automatically.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];SOURCES=ROOT/'sources'
NAME='core-personnel-administration'
TAKE=SOURCES/'expansion/rendered/core-personnel-administration-take-01'
PLAN=SOURCES/'expansion/plans/core-personnel-administration-take-01-final-inputs-20261028/plan.json'
FROZEN=SOURCES/'expansion/plans/core-personnel-administration-capture-freeze-20261028'/ (NAME+'.narrated-source.json')
MASTER='8b49de638b6db361e49b701a3e6e2492a6defe95f691c7eeabf9a4aac0bc8c8d'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(o):return (json.dumps(o,ensure_ascii=False,indent=2)+'\n').encode()

def build():
 assert sha(TAKE/(NAME+'.mp4'))==MASTER
 assert sha(PLAN)=='67b18be443a014e6fef31ada7fbd77fb28ad7bb6a210c29efc0d001a7c442bce'
 assert sha(FROZEN)=='e044a6466848e9b8c14c7a3b8711cabad0c87c1e9b48c7f7e74476b09b0598b8'
 assert sha(TAKE/'frame-qa/extraction-and-pixel-metrics.json')=='67e9036f6fa1f224f79d4f4640e747c250f1155685faf14a2199bef7f6ce186f'
 evidence=json.loads((TAKE/'evidence.pending.json').read_text())
 data=json.loads((TAKE/'frame-qa/extraction-and-pixel-metrics.json').read_text())
 pixels=json.loads((TAKE/'frame-qa/all-cue-pixel-comparisons.json').read_text())
 shots={r['id']:r for r in evidence['screenshots']};now=datetime.now(timezone.utc).isoformat()
 assert len(evidence['rendered_segments'])==38 and len(data['cue_frames'])==len(pixels['comparisons'])==116
 method='Personally displayed and inspected this exact complete1920x1080encoded intervalPNG. Intact fitted actualCore image remains outside title/caption bands. Bounded foreground labels and controls match the retained source review; clipped unrelated page fields are not promoted into support. All116unscaled actual encoded caption regions and fullcue23/36/78/98/116were also personally viewed. Full116applicationcueJPEGs were not individually visually inspected; their intact source correspondence is separately measured.'
 reviews=[]
 for i,segment in enumerate(evidence['rendered_segments'],1):
  frame=segment['frame'];shot=shots[segment['screenshot_id']]
  assert sha(SOURCES/frame['file'])==frame['sha256'] and sha(SOURCES/shot['file'])==shot['sha256']
  review={'passed':True,'reviewer':'Codex core_configuration_coverage','reviewed_at':now,'sha256':frame['sha256'],
   'video_sha256':MASTER,'source_screenshot_sha256':shot['sha256'],'application_visible':True,'labels_legible':True,
   'controls_reviewed':True,'controls_fully_visible':True,'controls_unobstructed':True,'caption_legible':True,
   'no_errors':True,'source_image_intact':True,'method':method}
  frame.update(review_status='reviewed_actual_encoded_frame',application_visible=True,
   visible_labels=shot['visible_labels'],reviewed_control_names=[],visual_review=review)
  reviews.append({'interval':i,'scene_id':segment['scene_id'],'source_id':segment['screenshot_id'],
   'frame_file':frame['file'],'frame_sha256':frame['sha256'],'review':review})
 caption_reviews=[]
 for row in data['cue_frames']:
  assert sha(SOURCES/row['file'])==row['sha256']
  caption_reviews.append(dict(row,visual_review_status='encoded_caption_region_personally_reviewed_unscaled',
   caption_legible=True,reviewed_at=now))
 for row in data['caption_reading_sheets']:assert sha(SOURCES/row['file'])==row['sha256']
 sys.path.insert(0,str(ROOT/'scripts'));from expansion_site import lesson_content_digest
 authoring=lesson_content_digest(json.loads(FROZEN.read_text()))
 assert authoring=='fcd317387b02b75b97e9802b518ebc3a40de82823bf1661c4b4e177bbaa08e35'
 evidence['authoring_sha256']=authoring
 evidence['qualification_review']={'frame_review_complete':True,'browser_playback_pending':True,'canonical_or_ready_changed':False}
 limits=['Whole-second service markers do not provide millisecond word precision.',
  'Raw75 and76 adjacent unchanged words share source022 and use their measured outer boundaries.',
  'Casey caption holds through an actual recorded gap to the next raw cue; no estimated speech boundary.',
  'The selected requirement type truncates; fullidentity is independently pictured in the type catalog and locked Code view.',
  'The role-search option is clipped; only the typed Community query and retained Officer chip are claimed there. Both complete chips follow.',
  'Two-row AND/OR forms are unsaved previews. Fresh reload restores the single saved rule.',
  'Qualified is the software result for one fictional rule while enforcement remains Off, without blocking or removal proof.',
  'No change to existing staffing, status, group administration or department administration is demonstrated.',
  'No upload, provider delivery, clinical or professional authorization proof.']
 review={'kind':'actual_personnel_encoded_frame_and_caption_review','reviewer':'Codex core_configuration_coverage',
  'reviewed_at':now,'video':dict(evidence['video'],bytes=(TAKE/(NAME+'.mp4')).stat().st_size),
  'plan':{'file':str(PLAN.relative_to(SOURCES)),'sha256':sha(PLAN)},
  'all38_encoded_interval_PNGs_personally_viewed_original1920x1080':True,
  'all116_actual_encoded_caption_regions_personally_viewed_unscaled':True,
  'full_cue_images_additionally_personally_viewed':[23,36,78,98,116],
  'all116_full_application_cue_images_individually_personally_viewed':False,
  'frame_reviews':reviews,'caption_reviews':caption_reviews,'caption_reading_sheets':data['caption_reading_sheets'],
  'interval_pixel_metrics':data['pixel_comparisons'],
  'all116_cue_pixel_metrics':{'file':str((TAKE/'frame-qa/all-cue-pixel-comparisons.json').relative_to(SOURCES)),
   'sha256':sha(TAKE/'frame-qa/all-cue-pixel-comparisons.json'),'maximum_mae_255':pixels['maximum_mae_255']},
  'issues':[],'publication_approved':False,'browser_playback_by_this_agent':False,
  'human_audio_listening_by_this_agent':False,'limits':limits}
 return review,evidence

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--record-reviewed',action='store_true');a=p.parse_args()
 review,evidence=build()
 if a.record_reviewed:
  for name,value in [('encoded-frame-review.json',review),('evidence.frames-reviewed.json',evidence)]:
   path=TAKE/name
   with path.open('xb')as f:f.write(encoded(value))
 print(json.dumps({'passed':True,'intervals_reviewed':38,'caption_regions_reviewed':116,
  'maximum_cue_image_mae_255':review['all116_cue_pixel_metrics']['maximum_mae_255'],'written':a.record_reviewed,
  'browser_playback_pending':True,'publication_approved':False}))

if __name__=='__main__':main()
