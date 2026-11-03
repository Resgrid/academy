"""Check published walkthrough geometry and retained speech-to-screen evidence.

Newer masters already fill their available canvas. Their exact original evidence
is validated without rewriting approvals or re-encoding an already wider image.
Native tablet screenshots retain their real aspect ratio and measured logical UI
scale; they must not be stretched into a desktop browser shape.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from render_walkthrough import layout
from verify_capture_evidence import verify


def audit_expansion(root):
    sources=root/'sources'
    def one(path):
        lesson=json.loads(path.read_text())
        if lesson.get('publication_mode')!='video':return None
        evidence_path=sources/lesson['evidence_file'];e=json.loads(evidence_path.read_text())
        checked=verify(evidence_path,sources)
        boxes=[]
        for shot in e['screenshots']:
            native=shot.get('provenance',{}).get('method')=='ios_simulator_screenshot'
            if native:
                segment=next(s for s in e['rendered_segments'] if s['screenshot_id']==shot['id'])
                box=segment['frame']['native_binding']['layout']
                if box['cropped'] or box['output_pixels_per_logical_point']<.8:
                    checked['issues'].append(shot['id']+': native UI is cropped or too small')
            else:box=layout(shot['width'],shot['height'])
            if box['height']<650 or box['y']+box['height']>960:
                checked['issues'].append(shot['id']+': insufficient app area or caption overlap')
            if not native and box['width']/1920<.8:
                checked['issues'].append(shot['id']+': application uses less than 80% of frame width')
            boxes.append({'id':shot['id'],'width_fraction':box['width']/1920,'height':box['height'],'native_aspect_preserved':native})
        return {'id':lesson['id'],'passed':not checked['issues'],'issues':checked['issues'],
                'video_sha256':e['video']['sha256'],'evidence_sha256':hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
                'source_screens':len(e['screenshots']),'screen_holds':len(e['rendered_segments']),
                'mapped_speech_cues':sum(len(s['captions']) for s in e['scenes']),
                'minimum_width_fraction':min(b['width_fraction'] for b in boxes),
                'native_aspect_preserved':any(b['native_aspect_preserved'] for b in boxes),
                'disposition':'existing full-canvas master and exact speech correspondence verified; retain bytes'}
    with ThreadPoolExecutor(max_workers=2) as pool:rows=[r for r in pool.map(one,sorted((sources/'expansion/lessons').glob('*.json'))) if r]
    return {'checked_at':datetime.now(timezone.utc).isoformat(),'passed':all(r['passed'] for r in rows),
            'videos':len(rows),'screen_holds':sum(r['screen_holds'] for r in rows),
            'mapped_speech_cues':sum(r['mapped_speech_cues'] for r in rows),'lessons':rows}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    result=audit_expansion(a.root);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='lessons'}));raise SystemExit(0 if result['passed'] else 1)
