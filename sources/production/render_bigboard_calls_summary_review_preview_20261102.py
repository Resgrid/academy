"""Render local review previews from verified audio and genuine Root screen maps.

These are explicitly unqualified previews, stored only under ignored _reports/.
This does not call, bypass or change the final renderer's narration approval gate.
No listening approval, final input plan, publication evidence, canonical lesson,
site change, share artifact or Git mutation is created. Default checks only.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'sources'
FF='/private/tmp/academy-video-runtime/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def preview(key,render=False,ffmpeg=FF):
 source=load('preview_calls_summary_correspondence',S/'production/prepare_bigboard_calls_summary_complete_20261102.py')
 gate=load('preview_calls_summary_root_pins',S/'production/assemble_bigboard_calls_summary_take_01_20261102.py')
 source.prepare(key,False)
 c=source.CFG[key];name=c['name'];P=Path('expansion/plans')/(name+'-complete-correspondence-20261102')
 for file,digest in gate.PINS[key].items():
  if sha(S/P/file)!=digest:raise ValueError('Changed actual Root review/proposal: '+file)
 data=read(S/P/'correspondence.proposed.json');root_review=read(S/P/'root-complete-correspondence-review.json')
 if not root_review['complete_cue_correspondence_reviewed'] or root_review['human_listening_claim'] is not False:raise ValueError('Missing genuine correspondence review')
 output=ROOT/'_reports/review-previews'/(name+'-take-01')
 if not render:return {'lesson_id':name,'verified_audio_and_root_mapping':True,'local_preview_only':True,'output':str(output),'rendered':False,'publishable':False}
 if output.exists():raise ValueError('Preserve the existing preview; no overwrite.')
 sys.path.insert(0,str(ROOT/'scripts'))
 from render_walkthrough import layout,load_cues,timeline,make_frame,find_font,audio_duration,check_audio_duration,run,ffmetadata,probe_output,stamp,FPS
 from PIL import Image,ImageDraw,ImageFont
 import numpy as np
 lesson=read(S/data['lesson_file']);manifest=read(S/P/'captures.source-relative.json')
 rows={r['id']:r for r in manifest['screenshots']}
 recipe={'lesson':lesson,'plan':{'display_context':'TRAINING ONLY · fictional department'},
         'scenes':deepcopy(data['scenes']),'cues':load_cues(S/data['captions_file']),
         'duration':data['duration_seconds'],'screenshots':{id:{'metadata':r,'path':S/r['file'],'layout':layout(r['width'],r['height'])} for id,r in rows.items()}}
 font=find_font();entries=timeline(recipe);source_files=[S/data['lesson_file'],S/data['audio_file'],S/data['captions_file'],S/data['qa_file'],*(S/r['file'] for r in rows.values())]
 fingerprints={str(p.relative_to(S)):sha(p) for p in source_files}
 with tempfile.TemporaryDirectory(prefix='academy-local-review-preview-') as directory:
  work=Path(directory);staging=work/'output';staging.mkdir();wav=work/'narration.wav'
  duration=audio_duration(ffmpeg,S/data['audio_file'],wav);check_audio_duration(duration,recipe['duration'])
  listing=[]
  for index,entry in enumerate(entries):
   frame=work/f'screen-{index:05}.png';make_frame(recipe,entry,frame,font)
   listing.extend(["file '"+frame.as_posix().replace("'","'\\''")+"'",'option framerate 1000',f"duration {entry['end']-entry['start']:.9f}"])
  listing.extend([listing[-3],'option framerate 1000']);concat=work/'screens.txt';concat.write_text('\n'.join(listing)+'\n')
  srt=staging/(name+'.srt');shutil.copyfile(S/data['captions_file'],srt)
  vtt=staging/(name+'.vtt');vtt.write_text('WEBVTT\n\n'+''.join(f"{stamp(cue['start'])} --> {stamp(cue['end'])}\n{cue['text']}\n\n" for cue in recipe['cues']))
  chapters=[{k:scene[k] for k in ['id','title','start','end']} for scene in recipe['scenes']]
  metadata=work/'chapters.ffmetadata';metadata.write_text(ffmetadata(chapters,lesson['title']))
  movie=staging/(name+'.mp4')
  run([ffmpeg,'-nostdin','-v','error','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(wav),'-i',str(srt),'-f','ffmetadata','-i',str(metadata),'-map','0:v:0','-map','1:a:0','-map','2:0','-map_metadata','3','-map_chapters','3','-t',str(duration),'-vf',f'fps={FPS}','-r',str(FPS),'-c:v','libx264','-preset','veryfast','-tune','stillimage','-crf','18','-threads','2','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-c:s','mov_text','-metadata:s:s:0','language=eng','-movflags','+faststart',str(movie)],'local_preview.encode')
  decoded=run([ffmpeg,'-nostdin','-v','error','-nostats','-i',str(movie),'-map','0:v:0','-map','0:a:0','-progress','pipe:1','-f','null','-'],'local_preview.full_decode')
  counts=re.findall(r'^frame=(\d+)\s*$',decoded.stdout,re.MULTILINE);frames=int(counts[-1]) if counts else 0
  if abs(frames-duration*FPS)>1.01:raise ValueError('Incomplete decoded video frame coverage')
  info=probe_output(ffmpeg,movie,duration);out_audio=audio_duration(ffmpeg,movie,work/'encoded-audio.wav')
  if not duration-1/48000<=out_audio<=duration+.1:raise ValueError('Incomplete or padded output audio')
  poster=staging/(name+'.jpg');run([ffmpeg,'-nostdin','-v','error','-y','-i',str(movie),'-frames:v','1','-update','1',str(poster)],'local_preview.poster')
  frame_dir=staging/'frames';frame_dir.mkdir();checks=[]
  for index,hold in enumerate(data['holds'],1):
   cue=recipe['cues'][hold['first_cue']-1];at=round(((cue['start']+cue['end'])/2)*FPS)/FPS
   path=frame_dir/f'hold-{index:03}.jpg';run([ffmpeg,'-nostdin','-v','error','-y','-ss',f'{at:.9f}','-i',str(movie),'-frames:v','1','-q:v','2','-update','1',str(path)],'local_preview.frame')
   selected=recipe['screenshots'][hold['screenshot_id']];box=selected['layout']
   actual=Image.open(path).convert('RGB').crop((box['x'],box['y'],box['x']+box['width'],box['y']+box['height']))
   expected=Image.open(selected['path']).convert('RGB').resize((box['width'],box['height']),Image.Resampling.LANCZOS)
   error=float(np.abs(np.asarray(actual,dtype=np.int16)-np.asarray(expected,dtype=np.int16)).mean())
   if error>=4:raise ValueError('Encoded preview application pixels differ from source')
   checks.append({'hold':index,'scene_id':hold['scene_id'],'screenshot_id':hold['screenshot_id'],'time':at,'file':str(path.relative_to(staging)),'sha256':sha(path),'application_pixel_mae_0_255':round(error,4),'source_sha256':selected['metadata']['sha256']})
  sheets=[];lf=ImageFont.truetype(str(font),19)
  for first in range(0,len(checks),4):
   canvas=Image.new('RGB',(1920,1152),'#dbeafe');draw=ImageDraw.Draw(canvas)
   for j,item in enumerate(checks[first:first+4]):
    x=(j%2)*960;y=(j//2)*576;draw.text((x+8,y+7),f"Hold{item['hold']:02} · scene{item['scene_id']} · {item['screenshot_id'][:55]}",font=lf,fill='#111827')
    picture=Image.open(staging/item['file']).convert('RGB');picture.thumbnail((960,540),Image.Resampling.LANCZOS);canvas.paste(picture,(x,y+36))
   path=staging/f'actual-frames-{len(sheets)+1:02}.jpg';canvas.save(path,quality=95);sheets.append(path.name)
  if any(sha(S/path)!=digest for path,digest in fingerprints.items()):raise ValueError('Source changed during preview rendering')
  report={'kind':'local_review_preview_not_publication_evidence','created_at':datetime.now(timezone.utc).isoformat(),'lesson_id':name,'publishable':False,'genuine_listening_review':'pending User response','final_encoded_caption_and_browser_qualification':'not claimed','source_audio_sha256':data['audio_sha256'],'source_qa_sha256':data['qa_sha256'],'root_correspondence_review_sha256':gate.PINS[key]['root-complete-correspondence-review.json'],'video_sha256':sha(movie),'video_bytes':movie.stat().st_size,'duration_seconds':duration,'full_av_decode':'passed','decoded_video_frames':frames,'decoded_output_audio_seconds':out_audio,'actual_media':info,'source_hashes':fingerprints,'caption_cues':len(recipe['cues']),'actual_screen_holds':len(checks),'numerical_source_pixel_checks':checks,'actual_frame_contact_sheets':sheets,'visual_frame_review':'pending actual inspection','canonical_or_site_changes':0,'git_mutations':0}
  (staging/'preview.json').write_text(json.dumps(report,indent=2)+'\n');output.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(staging,output)
 return {'lesson_id':name,'local_preview_only':True,'video':str(output/(name+'.mp4')),'video_sha256':report['video_sha256'],'duration_seconds':duration,'actual_screens':len(checks),'full_av_decode':'passed','publishable':False}


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('lesson',choices=['calls']);parser.add_argument('--render',action='store_true');parser.add_argument('--ffmpeg',default=FF);args=parser.parse_args();print(json.dumps(preview(args.lesson,args.render,args.ffmpeg),indent=2))
