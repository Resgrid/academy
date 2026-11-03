"""Decode every revised legacy screen hold and compare it with its source frame.

This is technical frame/timing evidence. It does not grant natural-voice listening
approval or replace the actual browser playback and visual layout checks.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ffmpeg',required=True);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    from PIL import Image,ImageChops,ImageStat
    root=a.root;sources=root/'sources';review=root/'_reports/all-video-layout/encoded';review.mkdir(parents=True,exist_ok=True)
    jobs=[];lessons={}
    for file in sorted((sources/'deep-dive/lessons').glob('*.json')):
        lesson=json.loads(file.read_text());ident=lesson['id'];folder=sources/'deep-dive/review'/ident
        prep=json.loads((folder/'preparation.json').read_text());shots=json.loads((folder/'storyboard.json').read_text());movie=sources/'deep-dive/media'/f'{ident}.mp4'
        assert sha(movie)==prep['sha256'];lessons[ident]={'folder':folder,'video_sha256':prep['sha256'],'holds':[]}
        for i,s in enumerate(shots):jobs.append((ident,i,movie,sources/'deep-dive'/s['frame'],s['capture'],s['start'],s['end']))
    folder=sources/'captures/firehouse51';ident='firehouse51-introduction';movie=folder/'firehouse51-walkthrough.mp4';v=json.loads((folder/'video-validation.json').read_text());shots=json.loads((folder/'storyboard.json').read_text());lessons[ident]={'folder':folder,'video_sha256':sha(movie),'holds':[]}
    for i,s in enumerate(shots):jobs.append((ident,i,movie,sources/'build/firehouse51'/f'{i:02}.png',s[1],s[0],shots[i+1][0] if i+1<len(shots) else v['duration_seconds']))
    def one(job):
        ident,i,movie,expected,capture,start,end=job;at=(start+end)/2
        target=review/ident/f'{i+1:03}.jpg';target.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run([a.ffmpeg,'-nostdin','-v','error','-y','-ss',str(at),'-i',str(movie),'-frames:v','1','-q:v','2',str(target)],check=True,capture_output=True)
        if not target.is_file():raise ValueError(f'{ident}: missing frame at {at}s')
        with Image.open(expected) as source,Image.open(target) as actual:
            assert actual.size==(1920,1080)
            difference=ImageChops.difference(source.convert('RGB').resize((480,270)),actual.convert('RGB').resize((480,270)))
            error=sum(ImageStat.Stat(difference).mean)/3
        if error>4:raise ValueError(f'{ident}/{i}: wrong or damaged screen at {at}s (mean pixel error {error})')
        return ident,{'index':i+1,'start':start,'end':end,'sampled_at':at,'source_capture':capture,'source_frame_sha256':sha(expected),'decoded_frame':target.relative_to(root).as_posix(),'decoded_frame_sha256':sha(target),'mean_pixel_error_255':round(error,4),'passed':True}
    with ThreadPoolExecutor(max_workers=3) as pool:
        for ident,row in pool.map(one,jobs):lessons[ident]['holds'].append(row)
    for ident,row in lessons.items():
        folder=row.pop('folder');row.update(lesson_id=ident,checked_at=datetime.now(timezone.utc).isoformat(),passed=True,method='Actual frame decoded at the midpoint of every supplied speech-timed hold; entire image compared against its rendered source frame. Original source views separately visually inspected. No hearing approval inferred.')
        (folder/'layout-frame-review.json').write_text(json.dumps(row,indent=2)+'\n')
        print(ident,len(row['holds']),'actual encoded holds checked')
    print('All',len(jobs),'revised screen holds decoded and matched their exact source views.')


if __name__=='__main__':main()
