#!/usr/bin/env python3
"""Install a versioned walkthrough player with accessible chapter controls."""
import hashlib
import html
import json
from pathlib import Path


def install_player(root):
    page = root / 'index.html'
    movie = root / 'firehouse51-walkthrough.mp4'
    version = hashlib.sha256(movie.read_bytes()).hexdigest()[:16]
    chapters = json.loads((root / 'firehouse51-walkthrough.chapters.json').read_text())
    buttons = []
    for chapter in chapters:
        start = chapter['start']
        stamp = f'{int(start)//60}:{int(start)%60:02}'
        title = html.escape(chapter['title'])
        buttons.append(f'<button type="button" data-start="{start}">{stamp} {title}</button>')
    block = f'''<!-- captured-player:start -->
<section class="walkthrough-player" aria-label="Firehouse 51 video player">
<style>.walkthrough-player video{{display:block;width:100%;aspect-ratio:16/9;object-fit:contain;background:#101d2d;border-radius:8px}}.walkthrough-chapters{{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0}}.walkthrough-player button{{font:inherit;font-size:14px;padding:8px 12px;border:1px solid #a7b9c8;background:white;color:#173044;border-radius:6px;cursor:pointer}}.walkthrough-player button:hover,.walkthrough-player button:focus-visible{{background:#deebf5}}.walkthrough-player [role=status]{{font-size:14px;color:#8c202a}}</style>
<video id="walkthrough-video" controls playsinline preload="auto" poster="firehouse51-walkthrough-poster.jpg?v={version}" src="firehouse51-walkthrough.mp4?v={version}">
<track kind="captions" label="English" srclang="en" src="firehouse51-walkthrough.vtt?v={version}" default>
</video>
<nav class="walkthrough-chapters" aria-label="Walkthrough chapters">{''.join(buttons)}</nav>
<p><a href="firehouse51-walkthrough.mp4?v={version}" download="firehouse51-walkthrough.mp4">Download MP4</a> · <a href="firehouse51-walkthrough.srt">Editable captions</a> · <a href="firehouse51-walkthrough.chapters.json">Chapters</a> · <button type="button" id="walkthrough-reload">Reload video</button></p>
<p id="walkthrough-status" role="status"></p>
<script>(()=>{{const player=document.getElementById('walkthrough-video'),status=document.getElementById('walkthrough-status');const start=()=>player.play().catch(()=>{{status.textContent='Press the video play control to continue.'}});document.querySelectorAll('.walkthrough-chapters button').forEach(button=>button.addEventListener('click',()=>{{status.textContent='';player.currentTime=Number(button.dataset.start);player.scrollIntoView({{block:'center',behavior:'instant'}});start()}}));document.getElementById('walkthrough-reload').addEventListener('click',()=>{{const at=player.currentTime;status.textContent='';player.addEventListener('loadedmetadata',()=>{{player.currentTime=Math.min(at,player.duration);start()}},{{once:true}});player.src='firehouse51-walkthrough.mp4?v={version}&reload='+Date.now();player.load()}});player.addEventListener('error',()=>{{status.textContent='The video could not load. Use Reload video to try again.'}})}})();</script>
</section>
<!-- captured-player:end -->'''
    content = page.read_text()
    if '<!-- captured-player:start -->' in content:
        before, rest = content.split('<!-- captured-player:start -->', 1)
        _, after = rest.split('<!-- captured-player:end -->', 1)
    else:
        before, rest = content.split('<video ', 1)
        _, after = rest.split('Chapters</a></p>', 1)
    page.write_text(before + block + after)
    return version


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1] / 'captures/firehouse51'
    print(install_player(root))
