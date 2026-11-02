"""Extract actual cue frames and pixel metrics; never infer visual approval.

Requires Pillow only when run, plus the explicitly supplied FFmpeg executable.
The source screenshots, master, captions and original23 PNGs remain untouched.
Footer sheets are QA reading aids, not application-capture evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
SOURCES=ROOT/'sources'
TAKE=SOURCES/'expansion/rendered/app-unit-call-lifecycle-native-take-01'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ffmpeg',required=True);p.add_argument('--master-sha256',required=True);args=p.parse_args();master_sha=args.master_sha256
    assert __debug__, 'Do not disable retained extraction guards.'
    assert len(master_sha)==64 and all(c in '0123456789abcdef' for c in master_sha)
    from PIL import Image,ImageChops,ImageDraw,ImageStat
    sys.path.insert(0,str(ROOT/'scripts'))
    from render_walkthrough import load_cues
    master=TAKE/'app-unit-call-lifecycle-native.mp4';assert sha(master)==master_sha
    assembly=json.loads((TAKE/'assembly.json').read_text());evidence=json.loads((TAKE/'evidence.pending.json').read_text())
    assert len(assembly['rendered_segments']) == 23 and len(evidence['screenshots']) == 23
    shots={row['id']:row for row in evidence['screenshots']};cues=load_cues(TAKE/'app-unit-call-lifecycle-native.srt');assert len(cues)==88
    output=TAKE/'frame-qa';assert not output.exists(),'Preserve retained frame extraction; choose a versioned script/output.'
    output.mkdir();numbers=[round((cue['start']+cue['end'])/2*30) for cue in cues];assert len(set(numbers))==88
    select='+'.join('eq(n\\,'+str(n)+')' for n in numbers)
    subprocess.run([args.ffmpeg,'-nostdin','-v','error','-i',str(master),'-vf','select='+select,'-fps_mode','vfr','-frames:v','88','-q:v','2',str(output/'cue-%04d.jpg')],check=True)
    rows=[]
    for index,(cue,n) in enumerate(zip(cues,numbers),1):
        path=output/f'cue-{index:04}.jpg';image=Image.open(path).convert('RGB');assert image.size==(1920,1080)
        actual=n/30;assert cue['start']<=actual<cue['end']
        segment=next(s for s in assembly['rendered_segments'] if s['start']<=actual<s['end'])
        layout=assembly['screenshots'][segment['screenshot_id']]['layout'];assert layout['cropped'] is False
        row={'cue':index,'file':str(path.relative_to(SOURCES)),'sha256':sha(path),'width':1920,'height':1080,
            'actual_frame_number':n,'actual_time':actual,'requested_midpoint':(cue['start']+cue['end'])/2,
            'caption_text':cue['text'],'source_id':segment['screenshot_id'],'video_sha256':master_sha,'visual_review_status':'pending_personal_inspection'}
        rows.append(row)
    metrics=[]
    for segment in assembly['rendered_segments']:
        row=shots[segment['screenshot_id']];source=Image.open(SOURCES/row['file']).convert('RGB')
        layout=assembly['screenshots'][segment['screenshot_id']]['layout'];frame=Image.open(SOURCES/segment['frame']['file']).convert('RGB')
        assert source.size==(row['width'],row['height']) and frame.size==(1920,1080)
        box=(layout['x'],layout['y'],layout['x']+layout['width'],layout['y']+layout['height'])
        delta=ImageChops.difference(source.resize((layout['width'],layout['height']),Image.Resampling.LANCZOS),frame.crop(box))
        metrics.append({'frame':segment['frame']['file'],'frame_sha256':sha(SOURCES/segment['frame']['file']),'source_id':segment['screenshot_id'],'source_sha256':sha(SOURCES/row['file']),
            'fitted_region':layout,'native_binding':segment['frame']['native_binding'],'mean_absolute_error_per_channel':ImageStat.Stat(delta).mean,'mean_absolute_error_255':sum(ImageStat.Stat(delta).mean)/3,
            'method':'Entire intact fitted image versus source resizedLANCZOS; normal H264 color/compression differences, not an OCR or semantic success test.'})
    sheets=[]
    for start in range(0,len(rows),6):
        group=rows[start:start+6];sheet=Image.new('RGB',(1920,160*len(group)),(30,38,50));draw=ImageDraw.Draw(sheet)
        for offset,row in enumerate(group):
            draw.text((16,offset*160+8),f"Cue{row['cue']:03} | actual encoded frame{row['actual_frame_number']} at{row['actual_time']:.6f}s",fill='white')
            frame=Image.open(SOURCES/row['file']).convert('RGB');sheet.paste(frame.crop((0,960,1920,1080)),(0,offset*160+40))
        path=output/f'caption-sheet-{start//6+1:02}.png';sheet.save(path)
        sheets.append({'file':str(path.relative_to(SOURCES)),'sha256':sha(path),'cues':[r['cue'] for r in group],'kind':'QA_only_unscaled_encoded_caption_footer_strips'})
    document={'kind':'actual_native_Unit_call_encoded_frame_qa_inputs','video_sha256':master_sha,'actual_interval_frames':len(assembly['rendered_segments']),'actual_cue_frames':88,'cue_frames':rows,'pixel_comparisons':metrics,'caption_reading_sheets':sheets,
        'visual_approval_inferred':False,'browser_playback_inferred':False,'publication_approved':False}
    path=output/'extraction-and-pixel-metrics.json';path.write_text(json.dumps(document,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed_extraction':True,'intervals':len(assembly['rendered_segments']),'cues':88,'caption_sheets':len(sheets),'visual_review':'pending','metrics_sha256':sha(path),'max_image_mae_255':max(r['mean_absolute_error_255'] for r in metrics)}))

if __name__=='__main__':main()
