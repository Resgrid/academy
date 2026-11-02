"""Prepare an untimed27-span review without changing the held634-word candidate."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'sources'
BASE=Path('expansion/plans/app-dispatch-map-and-site-reference-candidate-20261029')
OUT=S/'expansion/plans/app-dispatch-map-and-site-reference-27span-proposed-20261029'
NAME='app-dispatch-map-and-site-reference'
PINS={NAME+'.candidate.json':'5b08b842e0efd9ca37114732cb8e43002f8b31b1059da18f3611a8d8b509c4dd','narration.txt':'5e8db2a4fd8fcfa4f168c0c0dace29fcfa41841ab2ffa838400674b06cb62994','captures.reviewed.json':'30ff227e9108944854f9759fdea6151d22b552bceb814ce3039e86215251834f','screen-sequence.untimed.json':'b3374ef074b73ff1326e1b486805327262be9fdd97ed2d73c31610a6ebfe620e'}
# Each new span starts at this exact existing narration phrase. No time is assigned.
CUTS={
'01':[(2,None,['☰','Active Calls','Units','Map','Personnel','Notes']),(3,'Map, POIs, Protocols, and Contacts',['Menu','Map','POIs','Protocols','Contacts'])],
'02':[(4,None,['Chicago','🗂️']),(5,'Map Layers. Academy',['Map Layers','Academy Staging','Hide All']),(6,'and inspect',['Academy Staging','✕']),(7,'The blue staging point',['Chicago','🗂️']),(6,'Show All to restore',['Show All','Academy Staging']),(8,'These controls',['Chicago'])],
'03':[(3,None,['Menu','POIs']),(9,'The list starts',['All types','Name (A-Z)','Search POIs...']),(10,'Select Academy Staging',['Academy Staging','Search POIs...']),(11,'The existing Academy',['Staging','Academy Staging Point'])],
'04':[(11,None,['Academy Staging Point','Academy Staging','DESTINATION','TRAINING ONLY - 1000 Training Avenue','Fictional exercise assembly point. No real deployment or access approval.'])],
'05':[(3,None,['Menu','Protocols']),(13,'Here the page',['No protocols found','No protocols have been created for your department yet.'])],
'06':[(3,None,['Menu','Contacts']),(14,'Enter Warehouse',['Search contacts...','Training Warehouse (fictional)']),(15,'Training Warehouse, marked fictional.',['Warehouse','Training Warehouse (fictional)']),(16,'Contact Details keeps',['Contact Details','Company','Contact Information','Email','Office Phone'])],
'07':[(16,None,['Contact Details','Notes']),(17,'this warehouse',['No notes found for this contact','Pre-Plan']),(18,'explicitly says',['No pre-incident plan has been recorded for this contact.','Files']),(19,'says that no files',['No files have been attached to this contact.','Calls']),(20,'opens Related calls',['Related calls','No related calls','Calls linked to this contact, plus calls at any occupancy this contact is linked to.'])],
'08':[(24,None,['Menu','Settings']),(21,'App Info identifies',['App Info','App Name','Version','Environment']),(22,'Scrolling reveals',['Preferences','Theme','Language','Keep Alive','Support'])],
}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encoded(value):return(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
def prepare():
 for name,digest in PINS.items():assert sha(S/BASE/name)==digest,'Changed held candidate input: '+name
 lesson=json.loads((S/BASE/(NAME+'.candidate.json')).read_text());manifest=json.loads((S/BASE/'captures.reviewed.json').read_text());seq=json.loads((S/BASE/'screen-sequence.untimed.json').read_text())
 rows={int(r['id'][:3]):r for r in manifest['screenshots']};spans=[]
 supplement={'kind':'actual_literal_glyph_finding_pending_freeze_binding','source_ids':[rows[n]['id'] for n in [5,6]],'source_image_hashes':{rows[n]['id']:rows[n]['sha256'] for n in [5,6]},'literal_label':'✕','spoken_alias':'close the panel','reviewer':'Codex dispatch_ic_coverage','binding_recorded_at':'2026-10-29T06:10:39Z','cited_original_image_review_completed_at':'2026-10-29T05:55:50Z','observation':'The real foreground top-right layer-panel close glyph is visibly readable in005 and006 and is also present as literal text in the retained raw DOM/label metadata. It was omitted from the narrowed reviewed subset. This is a literal glyph observation, not an invented accessible name Close.','new_pixel_inspection_claimed':False,'raw_candidate_or_manifest_modified':False,'parent_acceptance_into_frozen_subset_pending':True}
 for scene,source_seq in zip(lesson['scenes'],seq['scenes']):
  text=scene['narration'];cuts=CUTS[scene['id']];starts=[0]
  for _,phrase,_ in cuts[1:]:
   assert text.count(phrase)==1,(scene['id'],phrase);starts.append(text.index(phrase))
  assert starts==sorted(starts)
  source_ids=[];pieces=[]
  for index,(number,phrase,required) in enumerate(cuts):
   segment=text[starts[index]:starts[index+1] if index+1<len(starts) else len(text)].strip();assert segment
   row=rows[number];available=set(row['visible_labels'])|({'✕'} if number in [5,6] else set())
   assert set(required)<=available,(scene['id'],number,set(required)-available)
   assert sha(S/row['file'])==row['sha256']
   source_ids.append(row['id']);pieces.append(segment)
   spans.append({'span':len(spans)+1,'scene_id':scene['id'],'scene_title':scene['title'],'source_id':row['id'],'source_file':row['file'],'source_sha256':row['sha256'],'exact_spoken_segment':segment,'required_pixel_controls_or_context':required,'supplement_needed':['✕'] if '✕' in required else [],'timing':None,'timing_rule':'Later bind real approved speech cues or genuine service markers; no timing/hold/operation precision is assigned here.'})
  assert source_ids==[x['capture_ref'] for x in source_seq['screens']]
  assert ' '.join(pieces)==text,'Every existing spoken character/word/order must be retained.'
 assert len(spans)==27 and len(' '.join(x['exact_spoken_segment'] for x in spans).split())==634
 report={'kind':'PROPOSED_27span_exact_spoken_Dispatch_source_correspondence','lesson_id':NAME,'candidate_file':str(BASE/(NAME+'.candidate.json')),'candidate_sha256':PINS[NAME+'.candidate.json'],'narration_sha256':PINS['narration.txt'],'scenes':8,'spoken_words':634,'source_images':21,'untimed_spans':spans,'one_actual_literal_supplement':supplement,'root_review_pending':True,'known_value_audit_pending':True,'narration_frozen':False,'timing_assigned':False,'audio_created':False,'publication_approved':False,'explicit_constraints':['Source006 is intentionally reused after full-map007: the layer was still Off when the panel was actually reopened. It provides the visible Show All control before008 restored-map result. No persistence/record change is invented.','Contact-tab names are spoken on the readable preceding unselected-control image; the following image provides only its genuinely readable empty-state result.','The displayed POI search input still shows its placeholder in010 while the instruction is given;011 provides the entered Staging/result readback.','POI detail012 and popup023 remain rejected; their invisible AX names/address fields never satisfy the map.','No reader should interpret the glyph supplement as an authenticated accessible name or a new button operation; the actual close action is separately in the normal UI ledger.']}
 compact='\n\n'.join(f"{x['span']:02} SCENE{x['scene_id']} {x['source_id']}\nPIXELS: {', '.join(x['required_pixel_controls_or_context'])}\nSPOKEN: {x['exact_spoken_segment']}" for x in spans)+'\n'
 return report,compact,supplement

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write-proposed',action='store_true');a=p.parse_args();report,compact,supplement=prepare()
 if a.write_proposed:
  assert not OUT.exists(),'Use NEW-only review paths.';OUT.mkdir(parents=True)
  (OUT/'ordered27span.proposed.json').write_bytes(encoded(report));(OUT/'ordered27span.compact.txt').write_text(compact);(OUT/'literal-glyph-supplement.proposed.json').write_bytes(encoded(supplement))
  (OUT/'provenance.json').write_bytes(encoded({'recipe_sha256':sha(__file__),'held_inputs':PINS,'new_files':{p.name:sha(p) for p in sorted(OUT.iterdir())},'candidate_raw_freeze_audio_or_timing_changed':False,'root_review_pending':True}))
 print(json.dumps({'passed':True,'scenes':8,'spans':27,'words':634,'literal_supplement':'005/006 ✕ only, pending parent binding','written':a.write_proposed,'frozen_or_timed':False}))
if __name__=='__main__':main()
