"""Prepare authentic-screen storyboards; assemble only when approved audio is local."""
import argparse, array, datetime, hashlib, html, json, math, re, subprocess, sys, textwrap
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE/'deep-dive'
CAPTURES=BASE/'captures/deep-dive'
sys.path.insert(0,str(BASE/'production/descript'))
from align_captions import align, parse_srt, seconds
COMPOSITIONS={key:(None,value['duration_seconds']) for key,value in json.loads((ROOT/'audio/sources.json').read_text()).items()}
PROJECT=''

def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def run(args):return subprocess.run(args,capture_output=True,check=True)
def font(size,bold=False):
    from fonts import font as installed_font
    return installed_font(size,bold)

def frame(lesson,scene,capture,index,total,path):
    from PIL import Image, ImageDraw
    im=Image.new('RGB',(1920,1080),'#102335');d=ImageDraw.Draw(im)
    d.text((32,18),'RESGRID ACADEMY  /  CONFIGURATION AND OPERATIONS',font=font(21,True),fill='#99cbd8')
    for n,line in enumerate(textwrap.wrap(scene['title'],width=63)):
        d.text((32,55+46*n),line,font=font(38,True),fill='white')
    source=Image.open(CAPTURES/capture).convert('RGB')
    # Preserve the normal browser viewport and its aspect ratio. Never stretch UI pixels.
    source.thumbnail((1180,864),Image.Resampling.LANCZOS)
    x=32+(1180-source.width)//2;y=154+(864-source.height)//2
    im.paste(source,(x,y));d.rectangle((x-1,y-1,x+source.width,y+source.height),outline='#82a4b8',width=2)
    d.rounded_rectangle((1240,154,1888,1018),radius=16,fill='#203d51')
    d.text((1270,183),'WHAT TO CHECK',font=font(23,True),fill='#91dfc5')
    checks=scene.get('checks') or [scene['title'],'Save, inspect the retained value and record any behavior still awaiting verification.']
    at=248
    for check in checks:
        for line in textwrap.wrap(check,width=35,break_long_words=False):
            d.text((1270,at),line,font=font(29,True),fill='white');at+=40
        at+=28
    d.text((1270,850),'Firehouse 51: fictional training data',font=font(24),fill='#c2d5df')
    d.text((1270,900),'Adapt the workflow to your sector.',font=font(24),fill='#c2d5df')
    d.text((1270,955),f'{index+1:02} / {total:02}  •  Actual application capture',font=font(22),fill='#91dfc5')
    d.text((32,1044),'RESGRID ACADEMY  •  LEARN. CONFIGURE. APPLY.  •  FICTIONAL DEPARTMENT EXAMPLES',font=font(18),fill='#a7c0d1')
    im.save(path)

def prepare(lesson,manifest,refresh_pages=False):
    ident=lesson['id'];out=ROOT/'review'/ident;out.mkdir(parents=True,exist_ok=True)
    prior=json.loads((out/'preparation.json').read_text()) if (out/'preparation.json').exists() else {}
    shots=[];missing=[]
    for i,s in enumerate(lesson['scenes']):
        for j,c in enumerate(s['captures']):
            if c not in manifest or not (CAPTURES/c).is_file():missing.append(c);continue
            output=out/f'{i+1:02}-{j+1:02}.jpg'
            if not refresh_pages: frame(lesson,s,c,i,len(lesson['scenes']),output)
            elif not output.is_file(): raise ValueError('Render the storyboard frame first: '+output.name)
            shots.append(dict(scene=i,capture=c,frame=str(output.relative_to(ROOT)),
                sha256=hashlib.sha256((CAPTURES/c).read_bytes()).hexdigest(),
                observed_url=manifest[c]['url'],observation=manifest[c]['note']))
    if missing:raise ValueError(f'{ident}: missing authentic captures {missing}')
    fingerprint=hashlib.sha256((json.dumps(lesson,sort_keys=True)+json.dumps([s['sha256'] for s in shots])+(ROOT/f'{ident}-raw.srt').read_text()).encode()).hexdigest()
    audit=dict(id=ident,title=lesson['title'],source_captures=len(shots),scenes=len(lesson['scenes']),
        source_fingerprint=fingerprint,narration='script ready; audio export pending',video='not assembled',
        human_listening_review='pending',browser_playback_review='pending')
    if ident in COMPOSITIONS:
        comp,duration=COMPOSITIONS[ident]
        raw=(ROOT/f'{ident}-raw.srt').read_text()
        srt,alignment=align(dict(lesson=ident,scenes=lesson['scenes']),raw,media_duration=duration)
        excessive=[c for c in alignment['text_changes'] if c['operation'] in ('delete','insert') and max(len(c['script'].split()),len(c['transcription'].split()))>3]
        if excessive or alignment['match_ratio']<.9 or alignment['layout_review']:
            raise ValueError(f'{ident}: transcript needs editorial review: {excessive or alignment}')
        caption=srt.replace('Rez grid','Resgrid')
        (out/'captions.srt').write_text(caption)
        (out/'captions.vtt').write_text('WEBVTT\n\n'+re.sub(r'\d\d:\d\d:\d\d,\d{3}',lambda m:m.group().replace(',','.'),caption))
        # Use original script cue assignments to locate scene boundaries, then brand the display captions.
        cue_words=[]
        for c in parse_srt(srt):cue_words.extend([seconds(c['start'])]*len(c['text'].split()))
        pos=0;starts=[]
        for s in lesson['scenes']:
            starts.append(0 if not starts else cue_words[pos]);pos+=len(s['narration'].split())
        for i,shot in enumerate(shots):
            group=[x for x in shots if x['scene']==shot['scene']]
            a=starts[shot['scene']];b=starts[shot['scene']+1] if shot['scene']+1<len(starts) else duration+1.2
            shot['start']=a+(b-a)*group.index(shot)/len(group)
            shot['end']=a+(b-a)*(group.index(shot)+1)/len(group)
        chapters=[dict(title=s['title'],start=starts[i],end=starts[i+1] if i+1<len(starts) else duration+1.2) for i,s in enumerate(lesson['scenes'])]
        dump(out/'chapters.json',chapters);dump(out/'caption-alignment.json',alignment)
        exported=(ROOT/'audio'/f'{ident}.m4a').is_file()
        audit.update(narration='Warm Lulu narration exported locally' if exported else 'Warm Lulu generated in Descript; audio export pending',
            duration_seconds=duration,script_match_ratio=alignment['match_ratio'],caption_cues=alignment['cues'],
            caption_layout='passed',complete_script_alignment='passed',audio_signal_validation='awaiting approved local export')
    video=ROOT/'media'/f'{ident}.mp4'
    audio=ROOT/'audio'/f'{ident}.m4a'
    if prior.get('source_fingerprint')==fingerprint and video.exists() and audio.exists() and prior.get('sha256')==hashlib.sha256(video.read_bytes()).hexdigest() and prior.get('audio_sha256')==hashlib.sha256(audio.read_bytes()).hexdigest():
        for key in ('video','audio_signal_validation','silent_speech_cues','minimum_cue_rms','output_loudness','full_decode','sha256','audio_sha256','audio_duration_seconds'):
            if key in prior:audit[key]=prior[key]
        browser=out/'browser-playback.json'
        if browser.exists():
            proof=json.loads(browser.read_text())
            if proof.get('sha256')==audit['sha256'] and proof.get('status')=='passed' and {r['position'] for r in proof.get('checks',[])}=={'beginning','middle','end'}:
                audit.update(browser_playback_review='passed',video='assembled and browser playback verified')
    dump(out/'storyboard.json',shots);dump(out/'preparation.json',audit)
    sections=[]
    for i,s in enumerate(lesson['scenes']):
        images=''.join(f'<figure><a href="../../../captures/deep-dive/{html.escape(c)}"><img src="{i+1:02}-{j+1:02}.jpg" alt="Authentic app capture: {html.escape(s["title"])}"></a><figcaption>{html.escape(s["title"])} — actual application state.</figcaption></figure>' for j,c in enumerate(s['captures']))
        sections.append(f'<section id="scene-{i+1}"><p class="eyebrow">Scene {i+1}</p><h2>{html.escape(s["title"])}</h2>{images}<details><summary>Read the narration</summary><p>{html.escape(s["narration"].replace("Rez grid","Resgrid"))}</p></details></section>')
    sectors=''.join(f'<dt>{html.escape(k)}</dt><dd>{html.escape(v)}</dd>' for k,v in lesson.get('cross_sector_examples',{}).items())
    limitations=''.join(f'<li>{html.escape(v)}</li>' for v in lesson.get('limitations',[]))
    editor=f'<a href="{audit["editor_url"]}">Open Warm Lulu narration in Descript</a>' if 'editor_url' in audit else ''
    player=''
    if audit['video'].startswith('assembled'):
        version=audit['sha256'][:16]
        controls=''.join(f'<button type="button" data-start="{c["start"]}">{html.escape(c["title"])}</button>' for c in chapters)
        player=f'<section class="watch"><video id="lesson-video" controls playsinline preload="metadata" poster="01-01.jpg" src="../../media/{ident}.mp4?v={version}"><track kind="captions" label="English" srclang="en" src="captions.vtt?v={version}" default></video><p>Warm Lulu · {round(audit["duration_seconds"]/60,1)} minutes · Guided cuts between real Resgrid screens</p><div class="play-controls"><button type="button" data-start="0">Start</button><button type="button" data-start="{audit["duration_seconds"]/2}">Middle</button><button type="button" data-start="{audit["duration_seconds"]-18}">Closing practice</button></div><details><summary>Choose a chapter</summary><div class="play-controls">{controls}</div></details><a href="../../media/{ident}.mp4?v={version}" download>Download video</a> · <a href="captions.srt" download>Download captions</a><p id="player-message" role="status"></p></section><script>const player=document.getElementById("lesson-video");document.querySelectorAll("button[data-start]").forEach(b=>b.addEventListener("click",()=>{{player.currentTime=Number(b.dataset.start);player.play().catch(()=>{{document.getElementById("player-message").textContent="Press the video play button to continue."}})}}));player.addEventListener("error",()=>{{document.getElementById("player-message").textContent="Video could not load. Open this page through the Academy preview server and try again."}});</script>'
    state=audit['video'] if player else 'Review storyboard; detailed video assembly pending'
    page=f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(lesson["title"])}</title>{STYLE}<main><a href="../../">← Detailed walkthroughs</a><p class="eyebrow">Actual application walkthrough</p><h1>{html.escape(lesson["title"])}</h1><p class="scope">{html.escape(audit["narration"])}. {html.escape(state)}. Human listening review remains pending.</p>{player}{editor}<nav>'+''.join(f'<a href="#scene-{i+1}">{i+1}. {html.escape(s["title"])}</a>' for i,s in enumerate(lesson['scenes']))+'</nav>'+''.join(sections)+f'<section><h2>Adapt to your department</h2><dl>{sectors}</dl></section><section><h2>What this exercise has not proved</h2><ul>{limitations}</ul></section></main></html>'
    (out/'index.html').write_text(page)
    return audit

STYLE='''<style>body{font:17px/1.65 system-ui;background:#edf2f6;color:#142e43;margin:0}main{max-width:1080px;margin:auto;padding:28px}h1{line-height:1.2;font-size:38px}a{color:#146471}section{background:white;padding:24px;border:1px solid #cbd9e3;border-radius:14px;margin:24px 0}h2{line-height:1.3}figure{margin:20px 0}img{width:100%;height:auto;border:1px solid #b4c9d7;border-radius:8px}figcaption{color:#50687a;font-size:15px}summary{cursor:pointer;font-weight:700}dt{font-weight:700;margin-top:18px}dd{margin-left:0}nav{display:grid;gap:8px;margin:24px 0}.scope{background:#d9eee7;border-radius:12px;padding:20px}.eyebrow{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:#456c7b}.card{background:white;border:1px solid #cbd9e3;border-radius:14px;padding:24px;margin:16px 0}.muted{color:#526c80}</style>'''
STYLE+='<style>video{width:100%;aspect-ratio:16/9;background:#102335;border-radius:8px}video::cue{background:rgba(0,0,0,.82);color:white}.play-controls{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}button{font:inherit;border:1px solid #9eb8c9;border-radius:8px;background:#e6f1f5;padding:9px 14px;cursor:pointer}.watch{padding:16px}</style>'

def render(lesson,ffmpeg):
    ident=lesson['id'];out=ROOT/'review'/ident
    audio=ROOT/'audio'/f'{ident}.m4a'
    if not audio.is_file():raise ValueError(f'{ident}: approved local audio export required before assembly')
    audit=json.loads((out/'preparation.json').read_text());duration=audit['duration_seconds']
    decoded=run([ffmpeg,'-v','error','-i',str(audio),'-map','0:a:0','-ar','16000','-ac','1','-f','f32le','-'])
    samples=array.array('f');samples.frombytes(decoded.stdout)
    if sys.byteorder!='little':samples.byteswap()
    rms=[]
    for i,c in enumerate(parse_srt((ROOT/f'{ident}-raw.srt').read_text())):
        clip=samples[int(seconds(c['start'])*16000):int(seconds(c['end'])*16000)]
        level=math.sqrt(sum(v*v for v in clip)/len(clip)) if clip else 0
        if level<.001:raise ValueError(f'{ident}: silent speech cue {i+1}')
        rms.append(level)
    actual=len(samples)/16000
    if abs(actual-duration)>.25:raise ValueError(f'{ident}: audio duration {actual} differs from composition {duration}')
    shots=json.loads((out/'storyboard.json').read_text());chapters=json.loads((out/'chapters.json').read_text())
    work=BASE/'build/deep-dive'/ident;work.mkdir(parents=True,exist_ok=True)
    listing=''.join(f"file '{ROOT/s['frame']}'\nduration {s['end']-s['start']:.6f}\n" for s in shots)+f"file '{ROOT/shots[-1]['frame']}'\n"
    (work/'visuals.txt').write_text(listing)
    metadata=';FFMETADATA1\ntitle='+lesson['title']+'\ncomment=Resgrid Academy configuration walkthrough; fictional department examples\n'
    for c in chapters:metadata+=f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(c['start']*1000)}\nEND={round(c['end']*1000)}\ntitle={c['title']}\n"
    (work/'chapters.txt').write_text(metadata);temp=work/'assembling.mp4'
    run([ffmpeg,'-y','-v','error','-f','concat','-safe','0','-i',str(work/'visuals.txt'),'-i',str(audio),'-i',str(out/'captions.srt'),'-f','ffmetadata','-i',str(work/'chapters.txt'),'-map','0:v:0','-map','1:a:0','-map','2:0','-map_metadata','3','-map_chapters','3','-r','30','-t',str(duration+1.2),'-c:v','libx264','-preset','veryfast','-tune','stillimage','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000','-af','loudnorm=I=-16:TP=-1.5:LRA=7,apad=pad_dur=1.2','-c:s','mov_text','-metadata:s:s:0','language=eng','-movflags','+faststart',str(temp)])
    run([ffmpeg,'-v','error','-i',str(temp),'-map','0:v:0','-map','0:a:0','-f','null','-'])
    measured=run([ffmpeg,'-hide_banner','-i',str(temp),'-af','loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json','-f','null','-']).stderr.decode()
    match=re.search(r'\{\s*"input_i".*?\}',measured,re.S)
    if not match:raise ValueError('Loudness measurement missing')
    loud=json.loads(match.group())
    if not (-18<=float(loud['input_i'])<=-14 and float(loud['input_tp'])<=-.8):raise ValueError('Output loudness outside target range')
    media=ROOT/'media';media.mkdir(exist_ok=True);video=media/f'{ident}.mp4'
    temp.replace(video)
    audit.update(video='assembled; browser playback review required',audio_signal_validation='passed',silent_speech_cues=0,
        minimum_cue_rms=min(rms),output_loudness=loud,full_decode='passed',sha256=hashlib.sha256(video.read_bytes()).hexdigest(),
        audio_sha256=hashlib.sha256(audio.read_bytes()).hexdigest(),audio_duration_seconds=actual)
    dump(out/'preparation.json',audit)
    print(json.dumps(audit))
    return audit

def main():
    p=argparse.ArgumentParser();p.add_argument('--render');p.add_argument('--ffmpeg');p.add_argument('--refresh-pages',action='store_true');args=p.parse_args()
    course=json.loads((ROOT/'course.json').read_text());manifest={r['file']:r for r in json.loads((CAPTURES/'manifest.json').read_text())}
    # Some early captures preceded the shared manifest. Recover only verifiable file metadata;
    # never invent browser content, capture times, or successful save observations.
    recovered=[]
    for shot in sorted(CAPTURES.glob('*.jpg')):
        if shot.name in manifest:continue
        paired=shot.with_suffix('.txt')
        url=re.search(r'URL: "([^"]+)"',paired.read_text()) if paired.is_file() else None
        if not url:raise ValueError('Capture has no paired browser observation: '+shot.name)
        manifest[shot.name]=dict(file=shot.name,ui_text=paired.name,url=url.group(1),topic='setup-wizard',
            captured_at=datetime.datetime.fromtimestamp(shot.stat().st_mtime,datetime.timezone.utc).isoformat(),
            note='Authentic browser capture; URL recovered from the paired accessibility export.',
            metadata_recovery='URL from paired AX file; timestamp from screenshot file modification time')
        recovered.append(shot.name)
    if recovered:
        dump(CAPTURES/'manifest.json',sorted(manifest.values(),key=lambda r:r['file']))
        dump(ROOT/'capture-metadata-recovery.json',dict(files=recovered,method='Paired AX URL and screenshot file modification time; no new captures or outcome claims'))
    audits=[]
    for file in sorted((ROOT/'lessons').glob('*.json')):
        lesson=json.loads(file.read_text());audits.append(prepare(lesson,manifest,args.refresh_pages))
        if args.render==lesson['id']:
            if not args.ffmpeg:raise ValueError('--ffmpeg required')
            render(lesson,args.ffmpeg)
            audits[-1]=prepare(lesson,manifest)
    receipts=json.loads((ROOT/'private-preview-receipts.json').read_text())['previews'] if (ROOT/'private-preview-receipts.json').exists() else []
    previews={r['id']:r['share_url'] for r in receipts if r['access_level']=='private'}
    cards=''
    for l in audits:
        watch=l['video'].startswith('assembled')
        label='Watch video and choose chapters' if watch else 'Review actual screens and narration'
        state=f'{round(l["duration_seconds"]/60,1)} minutes · Real Resgrid screens · English captions' if watch else l['narration']
        preview=f' · <a href="{html.escape(previews[l["id"]])}">Private Descript audio</a>' if l['id'] in previews else ''
        cards+=f'<article class="card"><p class="eyebrow">{html.escape(l["id"])}</p><h2>{html.escape(l["title"])}</h2><p>{html.escape(state)}</p><a href="review/{l["id"]}/">{label} →</a>{preview}</article>'
    pending=[l for l in course['lessons'] if l['id'] not in {a['id'] for a in audits}]
    pending_html=''.join(f'<li>{html.escape(l["title"])} — capture and detailed narration pending</li>' for l in pending)
    assembled=sum(a['video'].startswith('assembled') for a in audits);verified=sum(a['browser_playback_review']=='passed' for a in audits)
    for l in course['lessons']:
        a=next((a for a in audits if a['id']==l['id']),None)
        if a:l['status']='video-verified' if a['browser_playback_review']=='passed' else 'video-assembled' if a['video'].startswith('assembled') else 'captured-scripted'
    dump(ROOT/'course.json',course)
    (ROOT/'index.html').write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Resgrid detailed walkthroughs</title>{STYLE}<main><a href="../">← Academy library</a><p class="eyebrow">Detailed walkthroughs</p><h1>Configuration, behavior and department impact</h1><p class="scope">{len(audits)} captured and scripted walkthroughs; {len(COMPOSITIONS)} Warm Lulu narrations generated; {assembled} videos assembled; {verified} browser playback checks passed. Each walkthrough includes examples for community response, search and rescue, security, wildland contractors and industrial teams. Human listening review remains pending.</p><p><a href="sectors.html">Browse examples for your department</a> · <a href="../captures/firehouse51/">Watch the introductory captured walkthrough</a></p>{cards}<section><h2>Remaining detailed production</h2><ul>{pending_html}</ul></section></main></html>')
    dump(ROOT/'preparation-validation.json',dict(status='passed',captured_scripted_walkthroughs=len(audits),generated_narrations=len(COMPOSITIONS),
        remaining_detailed_captures=len(pending),assembled_detailed_videos=assembled,completed_detailed_videos=verified,lessons=audits,
        limits=['Subjective naturalness needs human listening review','Remaining detailed workflows and other clients still require verification']))
    print(json.dumps(dict(captured_scripted=len(audits),generated_narrations=len(COMPOSITIONS),remaining=len(pending),script_matches=[a.get('script_match_ratio') for a in audits])))
if __name__=='__main__':main()
