"""Pin the actual record, stock, reversal, ledger and retained-evidence screens."""
from pathlib import Path
import hashlib,json
S=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
name='core-record-inventory-consume-reverse'
base=S/'expansion/plans'/f'{name}-source-20261102-v2'
cfg=dict(name=name,source_folder=base.name,source_sha256=sha(base/'lesson.candidate.json'),captures_sha256=sha(base/'captures.reviewed.json'),audio_sha256=sha(S/'expansion/audio'/f'{name}.m4a'),captions_sha256=sha(S/'expansion/audio'/f'{name}.actual.corrected.srt'),qa_sha256=sha(S/'expansion/audio'/f'{name}.actual.qa.json'),cues=84,scene_apps={},supporting_applications=[],additional_labels={},
 context_notes=['All selected original screenshots were personally reviewed by Root.','The record remains a Draft throughout.','Positive recorded usage consumes stock; the later negative usage entry is a full explicit reversal.','The reversal ledger has positive Adjust2 while the record retains negative usage2.','Current and superseded Draft evidence are distinct retained snapshots; no manifest download or controlled-item witness execution is claimed.'],
 spans=[['01',1,7,3],['02',8,14,5],['03',15,24,4],['04',25,33,6],['05',34,37,7],['05',38,41,8],['06',42,42,7],['06',43,50,9],['07',51,54,10],['07',55,58,11],['08',59,59,10],['08',60,65,12],['09',66,66,3],['09',67,73,13],['10',74,80,13],['10',81,84,4]],
 refs={1:{'Work\nDraft':'Work draft'},2:{'External ID':'External I D','TRAIN-INV-20261102':'training inventory reference','Location':'location'},3:{'Narrative':'narrative'},4:{'Draft':'Draft'},5:{'Inventory usage':'Inventory usage'},6:{},7:{},
 8:{'Inventory':'Inventory','On hand':'On hand'},9:{'Academy training batteries':'Academy training batteries','Items':'Items','Filter':'Filter'},10:{'Station':'Station','14.000000':'fourteen','Unit':'Unit','5.000000':'five','Personnel':'Personnel','0.000000':'zero'},11:{},12:{'Station':'Station'},13:{},14:{},
 15:{'Inventory usage':'Inventory usage','Recorded usage':'Recorded usage'},16:{},17:{},18:{},19:{'Usage type':'Usage type','Used':'Used'},20:{'Existing consumption transaction ID (optional)':'Existing consumption transaction I D'},21:{},22:{},23:{},24:{},
 25:{'New consumption':'New consumption','Academy training batteries (packs)':'Academy training batteries'},26:{'Academy training batteries (packs)':'packs'},27:{'Station':'Station','Source location':'Source location','Academy training batteries · ACADEMY-LOT-A':'Academy Lot A','Lots':'Lots'},28:{'Assets':'Assets'},29:{'2':'two','Amount':'Amount','Note':'Note'},30:{},31:{},32:{'Station':'Station'},33:{'Save usage':'Save usage'},
 34:{'Usage saved and supporting evidence captured.':'Usage saved and supporting evidence captured'},35:{'Recorded usage':'Recorded usage','Used':'Used','+2 packs':'plus two packs'},36:{'Note':'note','Ledger entry':'Ledger entry'},37:{},38:{'On hand':'On hand','Station':'Station','12.000000':'twelve'},39:{'Unit':'Unit','5.000000':'five'},40:{},41:{},
 42:{'Reverse usage':'Reverse usage'},43:{},44:{'Reason for correction':'Reason for correction'},45:{},46:{'Existing witnessed reversal transaction ID (optional)':'optional witnessed reversal transaction I D'},47:{},48:{'Reverse usage':'Reverse usage'},49:{},50:{},
 51:{'+2 packs':'plus-two-pack','Reversed':'Reversed'},52:{'-2 packs':'minus two packs'},53:{'Reverses usage 45dfb3b4-4882-41e7-bb2e-1303b463aed1':'reference to the original usage'},54:{},55:{'On hand':'On hand','Station':'Station','14.000000':'fourteen'},56:{'Unit':'Unit','5.000000':'five','Personnel':'Personnel','0.000000':'zero'},57:{},58:{},
 59:{'Ledger entry':'Ledger entry'},60:{'Adjust':'Adjust','Academy training batteries':'training batteries','Station':'Station'},61:{'2.000000':'two'},62:{},63:{},64:{},65:{},
 66:{'Supporting evidence':'Supporting evidence'},67:{'Current Draft capture':'current Draft capture','2 inventory usage entries':'two inventory usage entries'},68:{'Superseded Draft capture':'Superseded'},69:{'Captured on':'captured time','Source version':'source version','Checksum':'Checksum'},70:{},71:{},72:{'Draft capture':'draft'},73:{},
 74:{},75:{},76:{},77:{},78:{},79:{},80:{},81:{},82:{},83:{},84:{}})
out=S/'production/record_inventory_complete_inputs_20261102.json'
assert not out.exists()
out.write_text(json.dumps({'inventory':cfg},indent=2,ensure_ascii=False)+'\n')
t=(S/'production/prepare_deployment_complete_20261102.py').read_text().replace("CONFIG_FILE=S/'production/deployment_complete_inputs_20261102.json'","CONFIG_FILE=S/'production/record_inventory_complete_inputs_20261102.json'").replace('3406a0544f3d8b9c339c9ee8de8a23ecc4265c7c19ee07fb0de2ef7438824c1e',sha(out))
dest=S/'production/prepare_record_inventory_complete_20261102.py'
assert not dest.exists()
dest.write_text(t)
print(json.dumps({'config':out.name,'review_inferred':False}))
