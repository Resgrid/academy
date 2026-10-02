#!/usr/bin/env python3
"""Assemble an explicitly labeled guided-cut video from authentic CUA captures."""
import argparse,array,hashlib,json,math,re,subprocess,sys,textwrap
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'production/descript'))
from align_captions import align,parse_srt,seconds
from update_captured_player import install_player
ROOT=BASE/'captures/firehouse51'; WORK=BASE/'build/firehouse51';WORK.mkdir(parents=True,exist_ok=True)
SHOTS=json.loads((ROOT/'storyboard.json').read_text())
CHAPTERS=[(item['title'],item['start']) for item in json.loads((ROOT/'firehouse51-walkthrough.chapters.json').read_text())]
def run(args):return subprocess.run(args,capture_output=True,text=True,check=True)
def font(size,bold=False):
    from fonts import font as installed_font
    return installed_font(size,bold)

def frame(i,shot):
 start,file,title,notes=shot
 image=Image.new('RGB',(1920,1080),'#101d2d');d=ImageDraw.Draw(image)
 d.text((30,17),'RESGRID ACADEMY  /  FIREHOUSE 51',font=font(20,True),fill='#86b5da')
 d.text((30,52),title,font=font(40,True),fill='white')
 capture=Image.open(ROOT/file).convert('RGB');capture.thumbnail((1568,882),Image.Resampling.LANCZOS)
 # Source is 1280x720. Keep its complete UI; this master frames rather than invents pixels or actions.
 capture=capture.resize((1568,882),Image.Resampling.LANCZOS)
 image.paste(capture,(24,136));d.rectangle((23,135,1593,1019),outline='#3f607c',width=2)
 d.rounded_rectangle((1620,136,1896,1018),radius=16,fill='#192f46')
 d.text((1640,165),'OBSERVE',font=font(21,True),fill='#82d9c0')
 y=230
 for n in notes:
  for line in textwrap.wrap(n,width=17,break_long_words=False):
   d.text((1640,y),line,font=font(26,True),fill='white');y+=36
  y+=32
 d.text((30,1041),'ACTUAL APPLICATION CAPTURES  •  GUIDED CUTS  •  FICTIONAL LOCAL TRAINING DATA',font=font(19),fill='#a8bfd4')
 d.text((1640,920),f'{i+1:02} / {len(SHOTS):02}',font=font(25,True),fill='#82d9c0')
 output=WORK/f'{i:02}.png';image.save(output);return output

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--ffmpeg',required=True);parser.add_argument('--validate-only',action='store_true');a=parser.parse_args();ff=a.ffmpeg
 audio=ROOT/'narration.m4a'
 info=subprocess.run([ff,'-hide_banner','-i',str(audio)],capture_output=True,text=True).stderr
 match=re.search(r'Duration: (\d+):(\d+):(\d+(?:\.\d+)?)',info);duration=int(match[1])*3600+int(match[2])*60+float(match[3])
 script=json.loads((ROOT/'narration-script.json').read_text());brief={'lesson':'firehouse51-walkthrough','scenes':[{'title':CHAPTERS[i][0],'narration':p} for i,p in enumerate(script)]}
 srt,audit=align(brief,(ROOT/'narration-raw.srt').read_text(),media_duration=duration)
 cues=parse_srt(srt)
 decoded=subprocess.run([ff,'-v','error','-i',str(audio),'-map','0:a:0','-ar','16000','-ac','1','-f','f32le','-'],capture_output=True,check=True)
 samples=array.array('f');samples.frombytes(decoded.stdout);levels=[]
 for i,c in enumerate(cues):
  clip=samples[int(seconds(c['start'])*16000):int(seconds(c['end'])*16000)]
  rms=math.sqrt(sum(v*v for v in clip)/len(clip)) if clip else 0
  if rms<.001:raise ValueError(f'Silent narration cue {i+1}')
  levels.append(rms)
 if any(x['operation'] in ('delete','insert') and len(x.get('script',x.get('transcription','')).split())>3 for x in audit['text_changes']):raise ValueError('Unexpected script mismatch')
 # Branding spelling in visible captions; the source narration retains its phonetic form.
 srt=srt.replace('Rez grid','Resgrid')
 subtitle=ROOT/'firehouse51-walkthrough.srt';subtitle.write_text(srt)
 (ROOT/'firehouse51-walkthrough.vtt').write_text('WEBVTT\n\n'+re.sub(r'\d\d:\d\d:\d\d,\d{3}',lambda m:m.group().replace(',','.'),srt))
 total=duration+1.2
 chapters=[{'title':title,'start':start,'end':CHAPTERS[i+1][1] if i+1<len(CHAPTERS) else total} for i,(title,start) in enumerate(CHAPTERS)]
 (ROOT/'firehouse51-walkthrough.chapters.json').write_text(json.dumps(chapters,indent=2)+'\n')
 listing=''
 for i,shot in enumerate(SHOTS):
  output=frame(i,shot);end=SHOTS[i+1][0] if i+1<len(SHOTS) else total
  listing+=f"file '{output}'\nduration {end-shot[0]:.6f}\n"
 listing+=f"file '{output}'\n";(WORK/'visuals.txt').write_text(listing)
 metadata=';FFMETADATA1\ntitle=Firehouse 51 — captured Resgrid walkthrough\ncomment=Actual UI still captures; guided cuts; Warm Lulu stock narration; synthetic department\n'
 for c in chapters:metadata+=f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(c['start']*1000)}\nEND={round(c['end']*1000)}\ntitle={c['title']}\n"
 (WORK/'chapters.txt').write_text(metadata)
 video=ROOT/'firehouse51-walkthrough.mp4'
 published_video=video
 # Never expose a partially written movie to an open browser player.
 if not a.validate_only:
  video=WORK/'firehouse51-walkthrough.rendering.mp4'
  run([ff,'-y','-v','error','-f','concat','-safe','0','-i',str(WORK/'visuals.txt'),'-i',str(audio),'-i',str(subtitle),'-f','ffmetadata','-i',str(WORK/'chapters.txt'),'-map','0:v:0','-map','1:a:0','-map','2:0','-map_metadata','3','-map_chapters','3','-r','30','-t',str(total),'-c:v','libx264','-preset','fast','-tune','stillimage','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000','-af','loudnorm=I=-16:TP=-1.5:LRA=7,apad=pad_dur=1.2','-c:s','mov_text','-metadata:s:s:0','language=eng','-movflags','+faststart',str(video)])
 info=subprocess.run([ff,'-hide_banner','-i',str(video)],capture_output=True,text=True).stderr
 for prop in ['1920x1080','30 fps','48000 Hz','Subtitle: mov_text','Chapters:']:
  if prop not in info:raise ValueError('Missing output property '+prop)
 run([ff,'-v','error','-i',str(video),'-map','0:v:0','-map','0:a:0','-f','null','-'])
 loud=run([ff,'-hide_banner','-i',str(video),'-af','loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json','-f','null','-']).stderr
 measurements=json.JSONDecoder().raw_decode(loud[loud.rfind('{'):])[0]
 if not a.validate_only:
  video.replace(published_video)
  run([ff,'-y','-v','error','-ss','1','-i',str(published_video),'-frames:v','1','-q:v','2',str(ROOT/'firehouse51-walkthrough-poster.jpg')])
  install_player(ROOT)
 report={'passed':True,'voice':'Warm Lulu','voice_library_id':'itMkRQx56fOF4CJe1D0C','duration_seconds':total,'ui_source_dimensions':'1280x720','output':'1920x1080 / 30fps / H.264 / AAC 48kHz / embedded English captions','source_type':'Actual browser UI captures; guided cuts between real states; not continuous pointer recording','shots':len(SHOTS),'chapters':len(chapters),'caption_cues':len(cues),'silent_cues':0,'minimum_cue_rms':min(levels),'full_video_decode':'passed','audio_measurements':measurements,'human_listening_review':'pending','script_alignment':audit,'sources':[{'file':s[1],'sha256':hashlib.sha256((ROOT/s[1]).read_bytes()).hexdigest(),'start_seconds':s[0]} for s in SHOTS]}
 (ROOT/'video-validation.json').write_text(json.dumps(report,indent=2)+'\n')
 (ROOT/'storyboard.json').write_text(json.dumps(SHOTS,indent=2)+'\n')
 print(json.dumps({k:report[k] for k in ['passed','duration_seconds','shots','caption_cues','silent_cues','audio_measurements']},indent=2),flush=True)
if __name__=='__main__':main()
