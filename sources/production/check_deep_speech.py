"""Independently transcribe actual exported speech; disclose ASR review limits."""
import argparse, difflib, hashlib, json, re, subprocess
from pathlib import Path

BASE=Path(__file__).resolve().parents[1];ROOT=BASE/'deep-dive'
def normalize(s):
    s=re.sub(r'rez\s+grid','resgrid',s,flags=re.I)
    return re.sub(r'[^a-z0-9]','',s.lower())
def main():
    p=argparse.ArgumentParser();p.add_argument('--ffmpeg',required=True);p.add_argument('--whisper',required=True);p.add_argument('--model',required=True);p.add_argument('lessons',nargs='+');args=p.parse_args()
    results=[]
    for ident in args.lessons:
        work=BASE/'build/deep-dive'/ident;work.mkdir(parents=True,exist_ok=True)
        wav=work/'actual-speech.wav';out=work/'actual-speech'
        subprocess.run([args.ffmpeg,'-v','error','-y','-i',str(ROOT/'audio'/f'{ident}.m4a'),'-ar','16000','-ac','1',str(wav)],capture_output=True,check=True)
        subprocess.run([args.whisper,'-m',args.model,'-f',str(wav),'--no-gpu','-t','4','-nt','-mc','0','-otxt','-of',str(out)],capture_output=True,check=True)
        heard=out.with_suffix('.txt').read_text()
        lesson=json.loads((ROOT/'lessons'/f'{ident}.json').read_text())
        reference=' '.join(s['narration'] for s in lesson['scenes'])
        matcher=difflib.SequenceMatcher(None,normalize(heard),normalize(reference),autojunk=False)
        ratio=matcher.ratio()
        report=dict(id=ident,audio_transcription=heard,normalized_character_match=round(ratio,4),
            audio_sha256=hashlib.sha256((ROOT/'audio'/f'{ident}.m4a').read_bytes()).hexdigest(),
            method='Complete exported audio transcribed with local Whisper base.en, previous context disabled; no reference script prompt supplied',
            status='passed intelligibility check' if ratio>=.97 else 'editorial comparison required',
            limits=['ASR can misrecognize proper names and abbreviations','Not a human naturalness or per-word caption-timing review'])
        (ROOT/'review'/ident/'independent-speech-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        results.append({k:v for k,v in report.items() if k!='audio_transcription'})
        print(json.dumps(results[-1]),flush=True)
    aggregate=ROOT/'independent-speech-validation.json'
    prior=json.loads(aggregate.read_text()).get('lessons',[]) if aggregate.exists() else []
    merged={r['id']:r for r in prior+results}
    aggregate.write_text(json.dumps(dict(lessons=[merged[k] for k in sorted(merged)],human_naturalness_review='pending'),indent=2)+'\n')
if __name__=='__main__':main()
