"""Retain completed Groups take01 visual observations; never infer approval.

The agent actually viewed all44original-size interval PNGs, all132unscaled
encoded caption regions and fullcue27/78/103/132before this recipe was authored.
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
NAME='core-groups-units-administration'
TAKE=SOURCES/'expansion/rendered/core-groups-units-administration-take-01'
PLAN=SOURCES/'expansion/plans/core-groups-units-administration-take-01-final-inputs-20261028/plan.json'
FROZEN=SOURCES/'expansion/plans/core-groups-units-administration-capture-freeze-20261028'/ (NAME+'.narrated-source.json')
MASTER='1d2ca37950eb5d9a24c9f0ef1640c2c0e936be6bb20930db7918ed6031f95f6a'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(o):return (json.dumps(o,ensure_ascii=False,indent=2)+'\n').encode()

def build():
 assert sha(TAKE/(NAME+'.mp4'))==MASTER
 assert sha(PLAN)=='383acc572ab1c52f0d791bbcc44dea24506718aee35e2d4522196ff6be07f6e9'
 assert sha(FROZEN)=='56b13d11be889d0825950a2cb33c0453c51302872939788ee03c6d1fd7bfee5c'
 assert sha(TAKE/'frame-qa/extraction-and-pixel-metrics.json')=='ed879362bdceef18c22be28070df7c195494f5401d733fe4c23858adc9b01900'
 evidence=json.loads((TAKE/'evidence.pending.json').read_text())
 data=json.loads((TAKE/'frame-qa/extraction-and-pixel-metrics.json').read_text())
 pixels=json.loads((TAKE/'frame-qa/all-cue-pixel-comparisons.json').read_text())
 shots={r['id']:r for r in evidence['screenshots']};now=datetime.now(timezone.utc).isoformat()
 assert len(evidence['rendered_segments'])==44 and len(data['cue_frames'])==len(pixels['comparisons'])==132
 method='Personally displayed and inspected this exact complete1920x1080encoded intervalPNG. Intact fitted actualCore image remains outside title/caption bands. Bounded foreground labels and controls match the retained source review; clipped unrelated page fields are not promoted into support. All132unscaled actual encoded caption regions and fullcue27/78/103/132were also personally viewed. Full132applicationcueJPEGs were not individually visually inspected; their intact source correspondence is separately measured.'
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
 assert authoring=='26763b0acf144c20d21a0d8b48426e10341ecff39ac99718c780a7baad4c0b73'
 evidence['authoring_sha256']=authoring
 evidence['qualification_review']={'frame_review_complete':True,'browser_playback_pending':True,'canonical_or_ready_changed':False}
 limits=['Whole-second markers do not provide millisecond word precision.',
  'Raw72New/Unitcontrol-label split is explicit; no inferred finer boundary.',
  'Unit Types context begins over the preceding type link; New Unit Type action is pictured on the catalog.',
  'Closed Type and Station truncate; fullidentity uses the catalog and actual openStationdropdown.',
  'Templates and Staffing are previews/read-only; no applied template, crew assignment, eligibility filter or new status event.',
  'Illustrative typed station coordinates are not device location or arrival.',
  'No provider or printing delivery proof.']
 review={'kind':'actual_groups_units_encoded_frame_and_caption_review','reviewer':'Codex core_configuration_coverage',
  'reviewed_at':now,'video':dict(evidence['video'],bytes=(TAKE/(NAME+'.mp4')).stat().st_size),
  'plan':{'file':str(PLAN.relative_to(SOURCES)),'sha256':sha(PLAN)},
  'all44_encoded_interval_PNGs_personally_viewed_original1920x1080':True,
  'all132_actual_encoded_caption_regions_personally_viewed_unscaled':True,
  'full_cue_images_additionally_personally_viewed':[27,78,103,132],
  'all132_full_application_cue_images_individually_personally_viewed':False,
  'frame_reviews':reviews,'caption_reviews':caption_reviews,'caption_reading_sheets':data['caption_reading_sheets'],
  'interval_pixel_metrics':data['pixel_comparisons'],
  'all132_cue_pixel_metrics':{'file':str((TAKE/'frame-qa/all-cue-pixel-comparisons.json').relative_to(SOURCES)),
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
 print(json.dumps({'passed':True,'intervals_reviewed':44,'caption_regions_reviewed':132,
  'maximum_cue_image_mae_255':review['all132_cue_pixel_metrics']['maximum_mae_255'],'written':a.record_reviewed,
  'browser_playback_pending':True,'publication_approved':False}))

if __name__=='__main__':main()
