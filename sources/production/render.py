"""Render illustrated training drafts. Needs Pillow, ffmpeg, and macOS say.

Audio must be built with access to the macOS speech service. The lesson catalog
stays editable in course.json; this renderer never signs in or changes Resgrid.
"""
import argparse
import concurrent.futures
import json
import math
import re
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parents[1]
W,H = 1920,1080
BG=(12,21,34); WHITE=(242,246,251); MUTED=(164,180,199)
RED=(239,80,72); CARD=(22,36,53); EDGE=(41,61,82)
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'

def font(size,bold=False):
    from fonts import font as installed_font
    return installed_font(size,bold)

def wrap(draw,text,size,width,bold=False):
    f=font(size,bold); lines=[];line=''
    for word in text.split():
        new=(line+' '+word).strip()
        if draw.textlength(new,font=f)>width and line:lines.append(line);line=word
        else:line=new
    if line:lines.append(line)
    return lines

def write(draw,text,xy,size,width,color=WHITE,bold=False,gap=12,max_height=None):
    while True:
        lines=wrap(draw,text,size,width,bold)
        if max_height is None or len(lines)*(size+gap)<=max_height or size<=24:break
        size-=2
    x,y=xy
    for line in lines:draw.text((x,y),line,font=font(size,bold),fill=color);y+=size+gap
    return y

def image_for(module,s,index,total,path):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H;d.line((0,y,W,y),fill=(int(12+5*t),int(21+6*t),int(34+8*t)))
    # Sparse grid gives structure without obscuring content.
    for x in range(100,W,160):d.line((x,130,x,H-100),fill=(20,32,47),width=1)
    for y in range(180,H-100,160):d.line((80,y,W-80,y),fill=(20,32,47),width=1)
    d.rounded_rectangle((80,58,135,113),radius=13,fill=RED)
    d.line((96,72,96,101),fill=WHITE,width=6);d.line((96,73,118,73),fill=WHITE,width=6)
    d.line((96,87,113,87),fill=WHITE,width=5);d.line((109,87,120,102),fill=WHITE,width=5)
    d.text((157,66),'RESGRID',font=font(38,True),fill=WHITE)
    d.text((359,70),'ACADEMY',font=font(29),fill=MUTED)
    d.text((1250,72),f'{module["id"].split("-")[0]}  /  '+module['area'].upper(),font=font(26,True),fill=MUTED)
    d.line((80,145,1840,145),fill=EDGE,width=2)
    tag=s.get('tag',{'title':'LESSON OVERVIEW','workflow':'GUIDED SCENARIO','verify':'CHECK THE RESULT','exercise':'PRACTICE TASK','scenario':'DEPARTMENT VALUE'}.get(s['kind'],'FEATURE LESSON'))
    d.text((82,185),tag.upper(),font=font(24,True),fill=RED)
    write(d,s['title'],(78,245),64,1710,bold=True,max_height=160)
    body=s['body']; n=len(body)
    top=460;bottom=945
    if s['kind']=='workflow' and n==3:
        width=540
        for i,text in enumerate(body):
            x=80+i*605
            d.rounded_rectangle((x,top,x+width,bottom),radius=24,fill=CARD,outline=EDGE,width=2)
            d.text((x+34,top+34),f'0{i+1}',font=font(78,True),fill=RED)
            write(d,text,(x+34,top+165),38,width-68,max_height=230)
            if i<2:
                ax=x+width+19;ay=top+240
                d.line((ax,ay,ax+33,ay),fill=RED,width=4)
                d.line((ax+22,ay-10,ax+33,ay,ax+22,ay+10),fill=RED,width=4)
    else:
        gap=18;height=(bottom-top-(n-1)*gap)//n
        labels={'feature':['WHAT IT DOES','HOW TO PREPARE'], 'scenario':['EXAMPLE DEPARTMENT','WHY IT HELPS'],
                'verify':['VERIFICATION','COMMON ISSUE'], 'exercise':['YOUR TASK','FOLLOW-UP']}.get(s['kind'],[])
        for i,text in enumerate(body):
            y=top+i*(height+gap)
            d.rounded_rectangle((80,y,1840,y+height),radius=20,fill=CARD,outline=EDGE,width=2)
            d.rounded_rectangle((105,y+28,156,y+79),radius=12,fill=(65,40,48))
            d.text((122,y+38),str(i+1),font=font(25,True),fill=RED)
            offset=30
            if i<len(labels):
                d.text((183,y+25),labels[i],font=font(21,True),fill=MUTED);offset=67
            write(d,text,(183,y+offset),38 if n<=2 else 33,1610,max_height=height-offset-20)
    d.line((80,986,1840,986),fill=EDGE,width=2)
    d.text((80,1016),'ILLUSTRATED DRAFT  •  LIVE SCREEN WALKTHROUGH PENDING',font=font(20),fill=MUTED)
    d.text((1590,1016),f'SCENE {index+1:02} / {total:02}',font=font(20),fill=MUTED)
    im.save(path)

def call(args,**kw):
    r=subprocess.run(args,capture_output=True,text=True,**kw)
    if r.returncode:raise RuntimeError(' '.join(map(str,args[:5]))+'\n'+r.stderr[-3000:])
    return r

def duration(ffmpeg,path):
    r=subprocess.run([ffmpeg,'-hide_banner','-i',str(path)],capture_output=True,text=True)
    match=re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)',r.stderr)
    if not match:raise RuntimeError('No audio duration: '+str(path))
    h,m,s=map(float,match.groups());return h*3600+m*60+s

def stamp(secs,comma=False):
    ms=round(secs*1000);h=ms//3600000;ms%=3600000;m=ms//60000;ms%=60000;s=ms//1000;ms%=1000
    return f'{h:02}:{m:02}:{s:02}{"," if comma else "."}{ms:03}'

def main():
    p=argparse.ArgumentParser();p.add_argument('--ffmpeg',required=True);p.add_argument('--audio-only',action='store_true')
    p.add_argument('--voice',default='Samantha');p.add_argument('--rate',type=int,default=148)
    p.add_argument('--lesson',action='append');p.add_argument('--workers',type=int,default=3)
    args=p.parse_args();data=json.loads((BASE/'course.json').read_text())
    lessons=[m for m in data['lessons'] if not args.lesson or m['id'] in args.lesson]
    for m in lessons:
        b=BASE/'build'/m['id'];b.mkdir(parents=True,exist_ok=True)
        for i,s in enumerate(m['scenes']):
            prefix=b/f'{i:02}';txt=prefix.with_suffix('.txt');audio=prefix.with_suffix('.aiff')
            # Pronunciation spelling is only used for synthesis; scripts retain the product name.
            txt.write_text(s['narration'].replace('Resgrid','Rez grid'))
            if args.audio_only:
                if not audio.exists() or duration(args.ffmpeg,audio)<1:
                    call(['/usr/bin/say','-v',args.voice,'-r',str(args.rate),'-o',str(audio),'-f',str(txt)])
                s['duration']=duration(args.ffmpeg,audio)
                if s['duration']<1:raise RuntimeError('Speech service produced empty audio; run audio-only with speech access.')
            else:
                image_for(m,s,i,len(m['scenes']),prefix.with_suffix('.png'))
        print(('Audio ready: ' if args.audio_only else 'Artwork ready: ')+m['id'],flush=True)
    if args.audio_only:
        (BASE/'build'/'audio-ready.json').write_text(json.dumps({'voice':args.voice,'rate':args.rate,'lessons':[m['id'] for m in lessons]},indent=2))
        return
    def render_module(m):
        b=BASE/'build'/m['id']; offset=0;captions=[];chapters=[]
        for i,s in enumerate(m['scenes']):
            prefix=b/f'{i:02}';audio=prefix.with_suffix('.aiff');video=prefix.with_suffix('.mp4')
            dur=duration(args.ffmpeg,audio)+0.6
            s['start_seconds']=offset;s['duration_seconds']=dur
            chapters.append({'title':s['title'],'start':offset,'end':offset+dur})
            if not video.exists():
                vf='fps=30,fade=t=in:st=0:d=0.22,drawbox=x=80:y=986:w=1760:h=4:color=0x293D52:t=fill'
                call([args.ffmpeg,'-hide_banner','-loglevel','error','-y','-loop','1','-framerate','2','-i',str(prefix.with_suffix('.png')),
                      '-i',str(audio),'-vf',vf,'-af','apad=pad_dur=0.6','-t',f'{dur:.3f}',
                      '-c:v','libx264','-preset','ultrafast','-tune','stillimage','-crf','22','-pix_fmt','yuv420p',
                      '-c:a','aac','-b:a','128k','-ar','48000',str(video)])
            words=s['narration'].split();chunks=[' '.join(words[j:j+13]) for j in range(0,len(words),13)]
            speaking=dur-0.6;pos=offset
            for chunk in chunks:
                end=pos+speaking*len(chunk.split())/len(words)
                captions.append((pos,end,chunk));pos=end
            offset+=dur
        vtt='WEBVTT\n\nNOTE Draft cue timing follows measured scene audio and word count. Review spoken word alignment before publication.\n\n'
        srt=''
        for i,(start,end,words) in enumerate(captions,1):
            vtt+=f'{stamp(start)} --> {stamp(end)}\n{words}\n\n'
            srt+=f'{i}\n{stamp(start,True)} --> {stamp(end,True)}\n{words}\n\n'
        (BASE/'media'/(m['id']+'.vtt')).write_text(vtt)
        subtitle=BASE/'media'/(m['id']+'.srt');subtitle.write_text(srt)
        (BASE/'media'/(m['id']+'.chapters.json')).write_text(json.dumps(chapters,indent=2))
        metadata=';FFMETADATA1\ntitle='+m['title']+'\ncomment=Illustrated training draft; live walkthrough pending\n'
        for c in chapters:
            metadata+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(c["start"]*1000)}\nEND={round(c["end"]*1000)}\ntitle={c["title"].replace("=","-")}\n'
        meta=b/'chapters.txt';meta.write_text(metadata)
        listing=b/'concat.txt';listing.write_text(''.join(f"file '{(b / f'{i:02}.mp4').as_posix()}'\n" for i in range(len(m['scenes']))))
        result=BASE/'media'/(m['id']+'.mp4')
        call([args.ffmpeg,'-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listing),
              '-i',str(subtitle),'-f','ffmetadata','-i',str(meta),'-map','0:v:0','-map','0:a:0','-map','1:0',
              '-map_metadata','2','-map_chapters','2','-c:v','copy','-c:a','copy','-c:s','mov_text',
              '-metadata:s:s:0','language=eng','-movflags','+faststart',str(result)])
        m['video']='media/'+result.name;m['duration_seconds']=round(duration(args.ffmpeg,result),2)
        m['subtitle']='media/'+m['id']+'.vtt';m['poster']='media/'+m['id']+'.jpg'
        Image.open(b/'00.png').resize((960,540)).save(BASE/m['poster'],quality=88)
        print(f'Rendered: {m["id"]} ({m["duration_seconds"]:.0f}s)',flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(render_module,lessons))
    (BASE/'course.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    print('Rendering complete.',flush=True)

if __name__=='__main__':main()
