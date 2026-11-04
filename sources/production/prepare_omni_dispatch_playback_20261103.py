"""Serve only the rendered media and a normal UI for reviewing it locally."""
import argparse
import html
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
parser = argparse.ArgumentParser()
parser.add_argument('lesson')
args = parser.parse_args()
source = S/'expansion/rendered'/f'{args.lesson}-take-01'
e = json.loads((source/'evidence.pending.json').read_text())
out = ROOT/'_reports/omni-dispatch-20261103'/args.lesson
out.mkdir(parents=True, exist_ok=True)
movie = S/e['video']['file']
captions = S/e['video']['captions']['file']
for media in (movie,captions):
    shutil.copyfile(media,out/media.name)
duration = e['video']['duration_seconds']
buttons = []
for position, ratio in [('beginning',.06),('middle',.50),('end',.91)]:
    target = duration*ratio
    cues = [c for sc in e['scenes'] for c in sc['captions'] if c['end']-c['start'] > 1.5]
    cue = min(cues,key=lambda c:abs(c['start']-target))
    buttons.append(f'<button data-seek="{cue["start"]+.05}">{position}</button>')
(out/'index.html').write_text(f'''<!doctype html>
<html lang="en"><meta charset="utf-8"><link rel="icon" href="data:,"><title>Omni Dispatch playback review</title>
<body style="font:16px system-ui;color:#f8fafc;background:#111827;margin:16px">
<h1 style="font-size:20px;margin:0 0 8px">{html.escape(args.lesson)}</h1>
{''.join(buttons)}
<video controls preload="auto" src="{movie.name}?v={e['video']['sha256']}" style="display:block;margin-top:8px;width:auto;height:auto;max-width:100%;max-height:calc(100vh - 130px)">
<track kind="captions" label="English" srclang="en" src="{captions.name}">
</video>
<button id="observe">Observe playback</button><output id="observation" hidden></output>
<script>
const video = document.querySelector('video');
document.querySelector('#observe').addEventListener('click', () => {{
  const b = video.getBoundingClientRect();
  const t = video.textTracks[0];
  document.querySelector('#observation').textContent = JSON.stringify({{
    current_src:video.currentSrc, video_width:video.videoWidth, video_height:video.videoHeight,
    duration_seconds:video.duration, current_time:video.currentTime, paused:video.paused, ended:video.ended,
    ready_state:video.readyState, network_state:video.networkState, media_error:video.error?.code ?? null,
    captions:{{mode:t.mode, text:Array.from(t.activeCues ?? []).map(c => c.text).join(' ')}},
    screen:{{top:b.top,bottom:b.bottom,viewport_height:document.documentElement.clientHeight}}
  }});
}});
for (const button of document.querySelectorAll('[data-seek]')) {{
  button.addEventListener('click', () => {{
    video.textTracks[0].mode = 'showing';
    video.currentTime = Number(button.dataset.seek);
    video.play();
  }});
}}
</script>
</body></html>''')
