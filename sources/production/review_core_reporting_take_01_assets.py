"""Extract actual encoded Reporting cue frames and compare exact source/caption pixels.

Numerical pass is not visual or browser-playback approval. No frozen source,
caption, audio or master is modified. Run only after actual take01 encoding.
"""
import hashlib,json,math,subprocess,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'sources';O=S/'expansion/rendered/core-reporting-fundamentals-take-01'
sys.path.insert(0,str(ROOT/'scripts'))
from render_walkthrough import validate_inputs,make_frame,find_font
FF='/private/tmp/academy-video-runtime/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
recipe=validate_inputs(S/'expansion/plans/core-reporting-fundamentals-capture-freeze-20261029/core-reporting-fundamentals.narrated-source.json',S/'expansion/plans/core-reporting-fundamentals-take-01-final-inputs-20261029/plan.json',S)
assert not (O/'frame-source-comparison.json').exists() and not (O/'cue-frame-check.json').exists(), 'Preserve previous numerical review reports.'
assembly=json.loads((O/'assembly.json').read_text());video=O/'core-reporting-fundamentals.mp4';vh=sha(video);assert vh==assembly['outputs']['video']['sha256']
assert len(assembly['rendered_segments'])==27 and len(recipe['cues'])==115
review=O/'review';review.mkdir(exist_ok=True);cuefolder=review/'cue-midpoints';cuefolder.mkdir(exist_ok=True)
font=find_font();label_font=ImageFont.truetype(str(font),19)
intervals=[]
for i,seg in enumerate(assembly['rendered_segments'],1):
 im=Image.open(S/seg['frame']['file']).convert('RGB');source=recipe['screenshots'][seg['screenshot_id']];box=source['layout']
 raw=Image.open(source['path']).convert('RGB').resize((box['width'],box['height']),Image.Resampling.LANCZOS)
 actual=im.crop((box['x'],box['y'],box['x']+box['width'],box['y']+box['height']))
 mae=float(np.abs(np.asarray(actual,dtype=np.int16)-np.asarray(raw,dtype=np.int16)).mean())
 assert mae<4.0,(i,mae)
 intervals.append({'interval':i,'scene_id':seg['scene_id'],'screenshot_id':seg['screenshot_id'],'frame':seg['frame']['file'],'sha256':sha(S/seg['frame']['file']),'source_sha256':source['metadata']['sha256'],'video_sha256':vh,'application_mean_absolute_pixel_error_0_255':round(mae,4),'full_source_rect_intact':box})
frames=[]
for scene in recipe['scenes']:
 for cue in scene['captions']:
  n=cue['cue'];at=round(((cue['start']+cue['end'])/2)*30)/30;assert cue['start']<=at<cue['end']
  out=cuefolder/f'cue-{n:04}.jpg'
  if not out.exists():
   subprocess.run([FF,'-nostdin','-v','error','-y','-ss',f'{at:.9f}','-i',str(video),'-frames:v','1','-q:v','2','-update','1',str(out)],check=True,capture_output=True)
  expected=review/'expected.png'
  make_frame(recipe,{'scene_id':scene['id'],'title':scene['title'],'screenshot_id':cue['screenshot_id'],'start':cue['start'],'end':cue['end'],'caption':cue['text']},expected,font)
  a=np.asarray(Image.open(out).convert('RGB'),dtype=np.int16);b=np.asarray(Image.open(expected).convert('RGB'),dtype=np.int16)
  error=np.abs(a-b);mae=float(error.mean());capmask=(b[960:,:,:].max(axis=2)>180);cap=float(error[960:,:,:][capmask].mean()) if capmask.any() else 0
  assert mae<4.0 and cap<12.0,(n,mae,cap)
  frames.append({'cue':n,'time':at,'frame_number':round(at*30),'file':out.relative_to(S).as_posix(),'sha256':sha(out),'video_sha256':vh,'scene_id':scene['id'],'screenshot_id':cue['screenshot_id'],'caption_text':cue['text'],'required_labels':cue['required_labels'],'full_frame_mean_absolute_error_0_255':round(mae,4),'caption_foreground_mean_absolute_error_0_255':round(cap,4),'inside_actual_cue':True})
(review/'expected.png').unlink(missing_ok=True)
def sheets(rows,folder,prefix,frame_path,label):
 folder.mkdir(exist_ok=True);paths=[]
 for start in range(0,len(rows),4):
  im=Image.new('RGB',(1920,1152),'#cbd5e1');draw=ImageDraw.Draw(im)
  for j,row in enumerate(rows[start:start+4]):
   x=(j%2)*960;y=(j//2)*576
   draw.text((x+8,y+7),label(row),font=label_font,fill='#111827')
   picture=Image.open(frame_path(row)).convert('RGB');picture.thumbnail((960,540),Image.Resampling.LANCZOS);im.paste(picture,(x,y+36))
  p=folder/f'{prefix}-{len(paths)+1:02}.jpg';im.save(p,quality=95);paths.append(p.relative_to(S).as_posix())
 return paths
isheets=sheets(intervals,review/'interval-contact-sheets','frames',lambda row:S/row['frame'],lambda row:f"Interval{row['interval']:02} · scene{row['scene_id']} · {row['screenshot_id'][:58]}")
csheets=sheets(frames,review/'cue-contact-sheets','cues',lambda row:S/row['file'],lambda row:f"Cue{row['cue']:03} · {row['time']:.3f}s · {row['screenshot_id'][:54]}")
# Full-width actual caption strips aid literal-text inspection without reducing text.
stripfolder=review/'caption-strips';stripfolder.mkdir(exist_ok=True);strips=[]
for start in range(0,len(frames),6):
 im=Image.new('RGB',(1920,1056),'#dbeafe');draw=ImageDraw.Draw(im)
 for j,row in enumerate(frames[start:start+6]):
  y=j*176;draw.text((10,y+5),f"Cue{row['cue']:03} · {row['time']:.3f}s · {row['screenshot_id']}",font=label_font,fill='#111827')
  actual=Image.open(S/row['file']).convert('RGB');im.paste(actual.crop((0,940,1920,1080)),(0,y+36))
 p=stripfolder/f'captions-{len(strips)+1:02}.jpg';im.save(p,quality=97);strips.append(p.relative_to(S).as_posix())
ireport={'passed':True,'method':'Numerical comparison only: actual encoded interval PNG full application rectangle against exact raw source resized using unchanged renderer layout. Does not constitute visual review.','video_sha256':vh,'intervals_checked':len(intervals),'maximum_application_mean_absolute_pixel_error_0_255':max(row['application_mean_absolute_pixel_error_0_255'] for row in intervals),'frames':intervals,'contact_sheets':isheets}
creport={'passed':True,'method':'Numerical comparison only: actual encoded30fps cue-midpoint JPEG against exact full-source/burned-caption composition. Actual SRT midpoints, no speech interpolation or automatic visual approval.','video_sha256':vh,'cues_checked':len(frames),'maximum_full_frame_mean_absolute_error_0_255':max(row['full_frame_mean_absolute_error_0_255'] for row in frames),'maximum_caption_foreground_mean_absolute_error_0_255':max(row['caption_foreground_mean_absolute_error_0_255'] for row in frames),'frames':frames,'contact_sheets':csheets,'full_width_caption_strips':strips}
(O/'frame-source-comparison.json').write_text(json.dumps(ireport,indent=2)+'\n');(O/'cue-frame-check.json').write_text(json.dumps(creport,indent=2)+'\n')
print(json.dumps({'video_sha256':vh,'intervals':len(intervals),'cues':len(frames),'interval_contact_sheets':len(isheets),'cue_contact_sheets':len(csheets),'full_width_caption_strips':len(strips),'max_app_mae':ireport['maximum_application_mean_absolute_pixel_error_0_255'],'max_full_frame_mae':creport['maximum_full_frame_mean_absolute_error_0_255'],'max_caption_mae':creport['maximum_caption_foreground_mean_absolute_error_0_255'],'visual_review':'pending actual inspection'},indent=2))
