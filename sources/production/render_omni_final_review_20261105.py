"""Rebuild the local Omni IC and Dispatch review player from retained lesson media."""
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
import subprocess
import textwrap
import tempfile
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageOps

root = Path(__file__).resolve().parents[1]
output = root/'expansion/rendered/omni-final-review-20261105'
output.mkdir(parents=True,exist_ok=True)
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
titles = {
    'historical-call': 'Create a historical call in Core and find it in Omni Dispatch',
    'callback-record': 'Create and finalize a built-in Callback record',
    'live-chat': 'Send and acknowledge a training chat message',
}
page = ['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Academy follow-up walkthroughs</title><style>body{font:17px system-ui;background:#141c29;color:#f5f7fa;margin:2rem auto;max-width:65rem;padding:0 1rem}video{display:block;width:100%;max-height:68vh;background:#101722;object-fit:contain}a{color:#afd0ff}section{margin:2.5rem 0}</style><main><h1>Academy follow-up walkthroughs</h1><p>Review copies from the fictional Firehouse 51 department. Recorded Resgrid screens and local neural narration.</p>']

def seconds(stamp):
    h,m,s = stamp.replace(',','.').split(':')
    return float(h)*3600+float(m)*60+float(s)

def run(*args):
    return subprocess.run([ffmpeg,'-nostdin','-v','error',*args],capture_output=True,check=True)

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def normalized_capture(path):
    with Image.open(path) as screenshot:
        return ImageOps.pad(screenshot.convert('RGB'), (1280, 720), color='#101722')

for key,title in titles.items():
    folder = root/'expansion/plans'/f'omni-{key}-source-20261105'
    if not folder.is_dir():
        continue
    shots = json.loads((folder/'paragraph-screens.json').read_text())
    data = json.loads((folder/'narration.timing.json').read_text())
    cues = (folder/'narration.local.srt').read_text().strip().split('\n\n')
    assert len(data['starts']) == len(shots)
    assert ' '.join(cue.split('\n',2)[2] for cue in cues).split() == (folder/'narration.txt').read_text().split()
    hold_starts = [seconds(cues[i-1].splitlines()[1].split(' --> ')[0]) for i in data['starts']]
    holds = list(zip(shots,hold_starts,[*hold_starts[1:], data['duration']]))
    expected = []
    for shot,start,end in holds:
        name, _ = shot
        captures = root/'captures/expansion/omni-final-20261105'
        p = captures/f'{name}.jpg'
        row = next(item for item in json.loads((captures/'manifest.json').read_text()) if item['id']==name)
        assert digest(p) == row['sha256']
        expected.append({'shot':name,'start':start,'end':end,'sha256':row['sha256'],'file':p.relative_to(root).as_posix()})
    movie = output/f'{key}.mp4'
    with tempfile.TemporaryDirectory(prefix='academy-omni-review-') as temporary:
        # Encode every capture as a fixed-length clip. Concatenating timed
        # single images can drop a hold at a decoder or filter discontinuity.
        lines = []
        for index, hold in enumerate(expected):
            still = Path(temporary)/f'{index:03}.png'
            normalized_capture(root/hold['file']).save(still)
            clip = Path(temporary)/f'{index:03}.mp4'
            frames = round(hold['end'] * 25) - round(hold['start'] * 25)
            run('-y','-loop','1','-framerate','25','-i',str(still),
                '-vf','format=yuv420p','-frames:v',str(frames),'-an',
                '-c:v','libx264','-preset','veryfast','-tune','stillimage',
                '-crf','18','-threads','2',str(clip))
            lines.append(f"file '{clip}'")
        concat = Path(temporary)/'screen-holds.txt'
        concat.write_text('\n'.join(lines)+'\n')
        run('-y','-f','concat','-safe','0','-i',str(concat),'-i',str(folder/'narration.local.m4a'),
            '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','128k',
            '-t',str(data['duration']),'-movflags','+faststart',str(movie))
    run('-xerror','-i',str(movie),'-map','0:v:0','-map','0:a:0','-f','null','-')
    for hold in expected:
        middle = (hold['start']+hold['end'])/2
        frame = run('-ss',str(middle),'-i',str(movie),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-').stdout
        rgb = np.asarray(normalized_capture(root/hold['file']),dtype=np.float32)
        decoded = np.frombuffer(frame,dtype=np.uint8).reshape(rgb.shape)
        hold['pixel_mae'] = round(float(np.abs(rgb-decoded).mean()),3)
        assert hold['pixel_mae'] < 5,hold
    (folder/'encoded-frame-check.json').write_text(json.dumps({'video_sha256':digest(movie),
        'complete_decode':True,'caption_cues':len(cues),'duration':data['duration'],'frames':expected},indent=2)+'\n')
    vtt = []
    for cue in cues:
        i,t,line = cue.split('\n',2)
        vtt.append(t.replace(',','.')+'\n'+'\n'.join(textwrap.wrap(line,width=53)))
    (output/f'{key}.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(vtt)+'\n')
    review_buttons = []
    for name, ratio in (('Beginning', .06), ('Middle', .50), ('End', .91)):
        target = data['duration'] * ratio
        times = [cue.splitlines()[1].split(' --> ') for cue in cues]
        start, stop = min(times, key=lambda t: abs(seconds(t[0])-target))
        review_buttons.append(f'<button data-seek="{seconds(start)+.06}">{name}</button>')
    page.append(f'<section id="{key}"><h2>{escape(title)}</h2>{" ".join(review_buttons)}<video controls preload="metadata" playsinline src="{key}.mp4"><track kind="captions" src="{key}.vtt" srclang="en" label="English"></video></section>')
    (output/'index.html').write_text('\n'.join([*page,"""</main><script>
for (const video of document.querySelectorAll('video')) {
  const cue = video.textTracks[0];
  const status = document.createElement('output');
  status.hidden = true;
  video.after(status);
  const observe = () => {
    status.value = JSON.stringify({
      time: video.currentTime, duration: video.duration, paused: video.paused,
      ready: video.readyState, error: video.error?.code ?? null,
      captions: cue.mode, active: Array.from(cue.activeCues ?? []).map(item => item.text)
    });
  };
  video.addEventListener('timeupdate', observe);
  video.addEventListener('seeked', observe);
  cue.addEventListener('cuechange', observe);
}
for (const button of document.querySelectorAll('[data-seek]')) {
  button.addEventListener('click', () => {
    const section = button.closest('section');
    const video = section.querySelector('video');
    section.scrollIntoView({block:'start'});
    for (const other of document.querySelectorAll('video')) if (other !== video) other.pause();
    video.textTracks[0].mode = 'showing';
    video.currentTime = Number(button.dataset.seek);
    video.play();
  });
}
</script>"""])+'\n')
    print(key,round(data['duration'],1),len(cues),len(holds),max(h['pixel_mae'] for h in expected),flush=True)
