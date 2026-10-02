"""Normalize audio, validate media and references, and package the portable drafts."""
import argparse
import concurrent.futures
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path
from prepare import OUT, ROOT

def call(args):
    r=subprocess.run(args,capture_output=True,text=True)
    if r.returncode:raise RuntimeError(r.stderr[-3000:])
    return r

def main():
    p=argparse.ArgumentParser();p.add_argument('--ffmpeg',required=True);p.add_argument('--normalize',action='store_true');p.add_argument('--package',action='store_true');args=p.parse_args()
    course=json.loads((OUT/'course.json').read_text())
    if args.normalize:
        def normalize(m):
            path=OUT/m['video'];done=OUT/'build'/m['id']/'normalized.json'
            if done.exists():return
            temp=path.with_name(path.stem+'-normalized.mp4')
            call([args.ffmpeg,'-hide_banner','-loglevel','error','-y','-i',str(path),
                  '-map','0:v:0','-map','0:a:0','-map','0:s:0','-map_metadata','0','-map_chapters','0',
                  '-c:v','copy','-c:s','copy','-c:a','aac','-b:a','160k','-ar','48000',
                  '-af','loudnorm=I=-16:TP=-1.5:LRA=7','-movflags','+faststart',str(temp)])
            temp.replace(path);done.write_text(json.dumps({'target_lufs':-16,'target_true_peak_db':-1.5,'audio_sample_rate':48000}))
            print('Audio normalized:',m['id'],flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(normalize,course['lessons']))
    issues=[];media=[]
    for m in course['lessons']:
        path=OUT/m['video'];r=subprocess.run([args.ffmpeg,'-hide_banner','-i',str(path)],capture_output=True,text=True)
        info=r.stderr
        for needed in ['1920x1080','30 tbr','Video: h264','Audio: aac','Subtitle: mov_text','Chapters:']:
            if needed not in info:issues.append(m['id']+' missing '+needed)
        frame_rate=re.search(r'([0-9.]+) fps',info)
        if not frame_rate or abs(float(frame_rate.group(1))-30)>0.1:
            issues.append(m['id']+' unexpected average frame rate')
        for suffix in ['.mp4','.jpg','.vtt','.srt','.chapters.json']:
            if not (OUT/'media'/(m['id']+suffix)).is_file():issues.append(m['id']+' missing '+suffix)
        chapters=json.loads((OUT/'media'/(m['id']+'.chapters.json')).read_text())
        if len(chapters)!=len(m['scenes']):issues.append(m['id']+' chapter count')
        if m.get('voice')=='Warm Lulu':
            natural=OUT/'production/descript/natural'
            for asset in [natural/'audio'/(m['id']+'.m4a'),natural/'captions'/(m['id']+'-raw.srt'),natural/(m['id']+'-validation.json')]:
                if not asset.is_file():issues.append(m['id']+' missing natural narration source '+asset.name)
        # Decode short samples from start, midpoint, and end of every finished video.
        for at in [0,max(0,m['duration_seconds']/2),max(0,m['duration_seconds']-2)]:
            test=subprocess.run([args.ffmpeg,'-hide_banner','-loglevel','error','-ss',str(at),'-i',str(path),'-t','1','-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True,text=True)
            if test.returncode or test.stderr.strip():issues.append(m['id']+' sample decode: '+test.stderr[-500:])
        media.append({'lesson':m['id'],'duration_seconds':m['duration_seconds'],'bytes':path.stat().st_size,
                      'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'sample_decode':'passed',
                      'voice':m.get('voice','original local voice'),
                      'caption_timing':('Warm Lulu speech-timed cues; exact-script text; 0.45-second scene pauses; human listening review pending'
                           if m.get('voice')=='Warm Lulu' else 'Descript speech-timed cues; script-corrected text; human playback review pending'
                           if (OUT/'production/descript/captions/corrected'/(m['id']+'.srt')).exists()
                           else 'draft estimated cues; human alignment review pending')})
    for f in course['features']:
        if not (OUT/'scripts'/('feature-'+f['id']+'.txt')).exists():issues.append('Missing feature brief '+f['id'])
        source=ROOT/f['source']['path']
        if hashlib.sha256(source.read_bytes()).hexdigest()!=f['source']['sha256']:issues.append('Changed source '+f['id'])
    report={'result':'passed' if not issues else 'failed','issues':issues,'lessons':len(media),
            'total_minutes':round(sum(m['duration_seconds'] for m in course['lessons'])/60,1),
            'feature_briefs':len(course['features']),'settings':len(course['settings']),
            'checks':['All lesson media, subtitle, thumbnail, and chapter files present',
                      '1080p / 30 fps H.264 video, AAC audio, embedded English subtitle track',
                      'Start, midpoint, and end audio/video samples decoded for every video',
                      'Scene/chapter counts match editable course', 'Feature brief files and source hashes checked'],
            'limits':['Captured web UI guide available; remaining full feature, mobile and provider workflows unverified',
                      'Source-based instructions require deployed-release verification',
                      'Caption timing and terminology need human playback review',
                      'Warm Lulu is stock AI narration; subjective naturalness needs human listening review'],
            'voice_status':course.get('voice_status'),'media':media}
    (OUT/'production'/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    if issues:raise RuntimeError(json.dumps(issues))
    if args.package:
        with zipfile.ZipFile(OUT/'Resgrid-Academy-Drafts.zip','w',zipfile.ZIP_STORED) as z:
            for path in sorted(OUT.rglob('*')):
                rel=path.relative_to(OUT)
                if path.is_file() and path.suffix!='.zip' and 'build' not in rel.parts and 'local-stack' not in rel.parts and '__pycache__' not in rel.parts and not path.name.startswith(('00-start-lulu-pilot','qa-contact-')) and path.suffix != '.log' and rel.as_posix()!='production/package-audit.json':
                    z.write(path,Path('Resgrid-Academy')/rel)
    print(json.dumps({k:report[k] for k in ['result','lessons','total_minutes','feature_briefs','settings']},indent=2),flush=True)

if __name__=='__main__':main()
