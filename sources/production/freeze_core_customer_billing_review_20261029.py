"""Freeze the accepted read-only Billing lesson source without editing history.

Default/--check reads only. --freeze creates the one new source-only package and
refuses existing output. The candidate's learner words and metadata bytes are
preserved exactly; a new receipt and freeze manifest record the later actual
parent acceptance. No browser/DB/Descript/audio/media/canonical/site/target/Git.
"""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];SOURCES=ROOT/'sources';CORE=ROOT.parents[2]
NAME='core-customer-billing-review'
BASE=Path('expansion/plans/core-customer-billing-review-source-candidate-20261029')
HANDOFF=Path('expansion/plans/core-customer-billing-review-script-handoff-20261029')
FREEZE=Path('expansion/plans/core-customer-billing-review-capture-freeze-20261029')
PINS={'expansion/plans/core-customer-billing-review-script-handoff-20261029/accepted-script-review.json': '3c8f9e942f5bcf2b81a65d4e890565dfda0976246d637d6d91f2956bffaae95e', 'production/verify_core_customer_billing_review_source_20261029.py': 'a2555afa7b6dc9c04c93be40679b8f75bc17794db2ca451d34310dc2edcc856f', 'production/freeze_core_certification_administration_20261028.py': '3383b1bfa075c00a43c2a7925b0e10e3cfde5ec65f82b7efc3937bb842feb7e2'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def encoded(x):return(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()
def module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def prepare(sources=SOURCES,core=CORE):
 for p,h in PINS.items():assert sha(sources/p)==h,'Changed accepted input: '+p
 verify=module(sources/'production/verify_core_customer_billing_review_source_20261029.py','retained_billing_source_verifier')
 checked=verify.verify(sources,core);assert checked['passed']and checked['words']==843
 review=json.loads((sources/HANDOFF/'accepted-script-review.json').read_text())
 assert review['accepted']is True and review['freeze_authorized']is True
 assert review['human_full_audio_listening_approved']is False and review['publication_approved']is False
 assert sha(sources/BASE/'narration.txt')==review['narration']['sha256']
 assert sha(sources/BASE/'candidate.json')==review['candidate']['sha256']
 assert sha(sources/HANDOFF/'compact-correspondence.json')==review['ordered_source_map']['sha256']
 guard=module(sources/'production/freeze_core_certification_administration_20261028.py','retained_billing_new_only_guard')
 copies={NAME+'.narrated-source.json':'candidate.json',NAME+'.captures.reviewed.json':'captures.reviewed.json',NAME+'.screen-sequence.json':'screen-sequence.json',
 'narration.txt':'narration.txt','scenario.replay.json':'scenario.replay.json','source-correspondence.json':'source-correspondence.json',
 'source-evidence.json':'source-evidence.json','source-review.json':'source-review.json','source-trace-links.json':'source-trace-links.json'}
 outputs={name:(sources/BASE/original).read_bytes()for name,original in copies.items()}
 outputs['accepted-script-review.json']=(sources/HANDOFF/'accepted-script-review.json').read_bytes()
 outputs['compact-correspondence.json']=(sources/HANDOFF/'compact-correspondence.json').read_bytes()
 source=json.loads((sources/BASE/'source-evidence.json').read_text())
 outputs['source-hashes.json']=encoded({'schema_version':1,'id':NAME,'status':'Frozen source-only input with actual parent full-script and control-map acceptance; no audio/timing/media/publication qualification',
 'words':843,'scenes':11,'untimed_spans':19,'six_sectors':6,'reviewed_images':15,'raw_pairs_preserved':16,'source_file_pins':20,
 'narrated_source_sha256':checked['candidate_sha256'],'narration_sha256':checked['narration_sha256'],'authoring_sha256':checked['authoring_sha256'],
 'Core_HEAD':source['Core_HEAD'],'source_identity_not_binary_attestation':True,'parent_script_review_accepted':True,'human_full_audio_listening_approved':False,
 'candidate_metadata_history':'Candidate bytes retain their earlier pending-review flags; the separate hash-bound accepted receipt records the later acceptance. No learner words or source order changed.',
 'recipe':{'file':'production/'+Path(__file__).name,'sha256':sha(__file__)},'input_pins':[{'file':p,'sha256':h}for p,h in PINS.items()],
 'full_input_inventory_in_pinned_verifier':True,'outputs':[{'file':n,'sha256':hashlib.sha256(b).hexdigest()}for n,b in outputs.items()],
 'write_boundary':'Default/--check reads only. --freeze creates only the named new source package and refuses existing output.'})
 return outputs,guard

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sources',type=Path,default=SOURCES);p.add_argument('--core-source',type=Path,default=CORE)
 p.add_argument('--check',action='store_true');p.add_argument('--freeze',action='store_true');a=p.parse_args();out,g=prepare(a.sources.resolve(),a.core_source.resolve());dest=a.sources/FREEZE
 if a.freeze:g.write_new_package(dest,out)
 elif dest.exists():
  assert {x.name for x in dest.iterdir()}==set(out),'Frozen inventory changed.'
  for n,b in out.items():assert(dest/n).read_bytes()==b,'Frozen bytes changed: '+n
 print(json.dumps({'passed':True,'source_only':True,'files_written':a.freeze,'words':843,'scenes':11,'untimed_spans':19,'reviewed_images':15,
 'narrated_source_sha256':hashlib.sha256(out[NAME+'.narrated-source.json']).hexdigest(),'narration_sha256':hashlib.sha256(out['narration.txt']).hexdigest(),
 'source_freeze_sha256':hashlib.sha256(out['source-hashes.json']).hexdigest(),'parent_script_accepted':True,'audio_or_video_qualified':False},indent=2))
if __name__=='__main__':main()
