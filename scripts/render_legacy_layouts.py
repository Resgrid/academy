"""Render all seven original detailed lessons and their wider source storyboards.

Rendering never grants playback approval. The regular build still requires fresh,
hash-bound real-browser evidence for each changed master before learner export.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'sources/production'))
import deep_dive


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ffmpeg',required=True);p.add_argument('--workers',type=int,default=2);a=p.parse_args()
    manifest={r['file']:r for r in json.loads((deep_dive.CAPTURES/'manifest.json').read_text())}
    lessons=[json.loads(p.read_text()) for p in sorted((deep_dive.ROOT/'lessons').glob('*.json'))]
    for lesson in lessons:deep_dive.prepare(lesson,manifest)
    def one(lesson):
        deep_dive.render(lesson,a.ffmpeg)
        deep_dive.prepare(lesson,manifest,refresh_pages=True)
        print('Rendered:',lesson['id'],flush=True)
    with ThreadPoolExecutor(max_workers=a.workers) as pool:list(pool.map(one,lessons))


if __name__=='__main__':main()
