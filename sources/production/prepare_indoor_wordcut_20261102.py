"""Split one action/readback caption at an observed existing speech-word boundary."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];S=R/'sources';sys.path.insert(0,str(R/'scripts'))
from render_walkthrough import load_cues,words
N='core-custom-map-floor-regions';A=S/'expansion/audio';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def timestamp(seconds):
 t=round(seconds*1000);return f'{t//3600000:02}:{t//60000%60:02}:{t//1000%60:02},{t%1000:03}'
raw=A/(N+'.actual.raw.srt');p=S/'demo/private/core-custom-map-floor-regions-word-timing-20261102.private.json';d=json.loads(p.read_text());current=d['after_query_srt']['content'][0]['text'];assert current.strip()==raw.read_text().strip(),'Read-only timing query changed exported transcript.'
proof=d['result']['structuredContent']['result']['agent_response'];assert '| Save, | 46.26 | 47.10 |' in proof and '| then | 47.10 | 47.32 |' in proof
old=load_cues(raw);c=old[14];assert c['start']==45.86 and c['end']==50.599 and c['text'].startswith('Select Save, then check')
new=[*old[:14],dict(start=c['start'],end=47.1,text='Select Save,'),dict(start=47.1,end=c['end'],text=c['text'][len('Select Save, '):]),*old[15:]]
assert words(' '.join(x['text'] for x in new))==words(' '.join(x['text'] for x in old))
out=A/(N+'.wordcut.input.srt');assert not out.exists();out.write_text('\n\n'.join(f'{i}\n{timestamp(x["start"])} --> {timestamp(x["end"])}\n{x["text"]}' for i,x in enumerate(new,1))+'\n\n')
public={'original_raw_srt_sha256':sha(raw),'derived_srt_sha256':sha(out),'original_cues':71,'derived_cues':72,'source_cue':15,'word_boundary_seconds':47.1,'observed_words':[{'word':'Select','start':45.86,'end':46.26},{'word':'Save,','start':46.26,'end':47.1},{'word':'then','start':47.1,'end':47.32}], 'method':'Existing Descript transcript word alignment, queried read-only. Original exported transcript rechecked unchanged; all other cue boundaries and every script word retained. Not an inferred even text split.','speech_audio_unchanged':True,'project_media_duration_unchanged':255.76,'complete_word_timing_proof_sha256':sha(p),'review_scope':'Numeric timing extraction, not a hearing or final video review.'}
q=A/(N+'.wordcut.provenance.json');assert not q.exists();q.write_text(json.dumps(public,indent=2)+'\n');print({'derived_cues':len(new),'cut_seconds':47.1,'audio_unchanged':True})
