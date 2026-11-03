"""Pin the actual return arrow, saved file and HTML manifest to complete speech."""
from pathlib import Path
import hashlib,json
S=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
name='core-deployment-equipment-files-manifest';base=S/'expansion/plans'/f'{name}-source-20261102'
cfg=dict(name=name,source_folder=base.name,source_sha256=sha(base/'lesson.candidate.json'),captures_sha256=sha(base/'captures.reviewed.json'),audio_sha256=sha(S/'expansion/audio'/f'{name}.m4a'),captions_sha256=sha(S/'expansion/audio'/f'{name}.actual.corrected.srt'),qa_sha256=sha(S/'expansion/audio'/f'{name}.actual.qa.json'),cues=44,scene_apps={},supporting_applications=[],
    additional_labels={'030-deployment-handover-file-prepared':['Choose File']},
    context_notes=['Source010 has the actual DOM-titled Return arrow and its full visible bounds, separately personally reviewed.','Return changes this free-text deployment assignment; no inventory stock movement is claimed.','The uploaded handover file is verified by its saved row only; its download is not claimed.','The actual manifest is HTML, not a successful licensed PDF export.','Choose File is native file-input text personally read from source030 pixels.'],
    spans=[['01',1,6,10],['02',7,7,10],['02',8,13,29],['03',14,20,30],['04',21,28,31],['05',29,29,31],['05',30,36,32],['06',37,41,32],['06',42,42,31],['06',43,44,32]],
    refs={1:{'Roster':'Roster','Demo radio kit':'Demo radio kit','Equipment':'Equipment'},2:{'Unit':'Unit','Issued':'Issued'},3:{'Issued':'Issued'},4:{'Return':'Return'},5:{},6:{'Equipment':'equipment row'},
          7:{'Return':'Return','Demo radio kit':'Demo radio kit'},8:{'No equipment rostered.':'No equipment rostered'},9:{'CS-VAN-1':'C S van one','Crew':'Crew','1':'one'},10:{'Matthew Casey':'Matthew Casey'},11:{'Unit':'unit'},12:{'Equipment':'equipment assignment'},13:{},
          14:{'Files':'Files'},15:{'Receipt':'Receipt'},16:{'Other':'Other'},17:{'Name':'Name','Choose File':'Choose File'},18:{},19:{'Upload':'Upload'},20:{'Other':'file category'},
          21:{'Upload':'Upload','Saved.':'Saved'},22:{'TRAINING ONLY - Community support handover':'community support handover','Other':'Other','Type':'Type'},23:{'deployment-handover-20261102.txt':'text filename','Added':'Added'},24:{'Receipt':'Receipt'},25:{'File name':'filename','Name':'display name'},26:{},27:{},28:{},
          29:{'View manifest':'View manifest'},30:{'Firehouse 51 — Training Department — Deployment Manifest':'deployment manifest'},31:{'TRAINING ONLY - Community support deployment · Planned':'Planned','Incident #':'agency references','Window':'window'},32:{'Units':'Units','CS-VAN-1':'C S van one','Crew':'crew'},33:{'Personnel':'Personnel','Matthew Casey':'Casey','CS-1':'C S one'},34:{'Seat':'Seat','Certification':'Certification'},35:{'Personnel':'people','Units':'assignments'},36:{'Firehouse 51 — Training Department — Deployment Manifest':'manifest'},
          37:{},38:{},39:{},40:{'Units':'resources'},41:{},42:{'Files':'attach'},43:{'Unit':'unit','Personnel':'personnel'},44:{}})
out=S/'production/deployment_handover_complete_inputs_20261102.json';assert not out.exists();out.write_text(json.dumps({'handover':cfg},indent=2,ensure_ascii=False)+'\n')
t=(S/'production/prepare_compensation_static_complete_20261102.py').read_text().replace("CONFIG_FILE=S/'production/compensation_static_complete_inputs_20261102.json'","CONFIG_FILE=S/'production/deployment_handover_complete_inputs_20261102.json'").replace('1a121260516198301157f3879f76a1003ece42767daa3355e5b61e5fb24ace61',sha(out))
dest=S/'production/prepare_deployment_handover_complete_20261102.py';assert not dest.exists();dest.write_text(t)
print(json.dumps({'config':out.name,'review_inferred':False}))
