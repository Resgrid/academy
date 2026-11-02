"""Read-only verification of the held Billing source candidate.

This helper has no write mode and performs no browser, application, DB, Descript,
financial, canonical, readiness, site, target or Git action. It verifies actual
raw/reviewed source identities, exact word/screen correspondence and cited source
hashes. Parent approval, a later freeze and any media qualification are separate.
"""
import argparse,hashlib,importlib.util,json,re,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
SOURCES=ROOT/'sources';CORE=ROOT.parents[2]
BASE=Path('expansion/plans/core-customer-billing-review-source-candidate-20261029')
PINS={'captures/expansion/core-customer-billing-review-20261029/manifest.json': '536b818fd75257956d00b63f8b22c91c0601dcbe3a527a20a73c73ef83d591a4', 'captures/expansion/core-customer-billing-review-chrome-20261029/manifest.json': 'b00967b2fc09932ff58bf3414a9b6210af3985350e1fe013308b1e1e21352bf0', 'expansion/audits/core-customer-billing-review-source-candidate-preflight-20261029.json': '1837c7024de8a795b1643639daddb66a323c2c4adea50c05f9d28057a41ef320', 'expansion/plans/core-customer-billing-review-script-handoff-20261029/compact-correspondence.json': 'c27da251dff7e964acfc8ff5643242d504e2b6bef2eee2cc162c313d41670a2e', 'expansion/plans/core-customer-billing-review-source-candidate-20261029/candidate.json': 'ba6214c9fec32991c1a04e795045bbe9749289d86ffc63813bd231d92d47aec5', 'expansion/plans/core-customer-billing-review-source-candidate-20261029/captures.reviewed.json': 'bac6713c2ff2c68405633128b7747916cfaf7cd07c0f3e6caf25fcacb9c08272', 'expansion/plans/core-customer-billing-review-source-candidate-20261029/contact-sheet.jpg': '049800f2aa76e93b5b021b927a6fabf81ffa6a86ed8690881033cda40636985f', 'expansion/plans/core-customer-billing-review-source-candidate-20261029/narration.txt': '61750a55fb747edbc8cd327f934cb0fdc502ac37659e2073c9acc812625872d5', 'expansion/plans/core-customer-billing-review-source-candidate-20261029/scenario.replay.json': '0fa0b0db8d12d56c53d1fa25cd29a4069c3f0ba642667756782b23698ce3fdee', 'expansion/plans/core-customer-billing-review-source-candidate-20261029/screen-sequence.json': '8a712f69894c819bc55be102398354cf33f86a24a3283267991151dee6e17671', 'expansion/plans/core-customer-billing-review-source-candidate-20261029/source/Core/Web/Resgrid.Web/Areas/User/Views/Contacts/Index.cshtml': 'c70abc02d673d5fb4d7bbad3b22ce4374af3cb20224141c3f0c755c1d45cf5cc', 'expansion/plans/core-customer-billing-review-source-candidate-20261029/source/Core/Web/Resgrid.Web/Areas/User/Views/Invoicing/EditRateCard.cshtml': '9994050e60b08fe50ee326d8e326e51da92d514cea4e6d752a26f68e16f62fa7', 'expansion/plans/core-customer-billing-review-source-candidate-20261029/source-correspondence.json': '5a6bb70c6b0dc78e5e01f81c1ef329993d24b8abbec985a562f2edbbc7511a88', 'expansion/plans/core-customer-billing-review-source-candidate-20261029/source-evidence.json': '6cce63c92aa8d34084d78f24197c5bfc9fb5de4f9fff237b98a0d578fb4aeaf0', 'expansion/plans/core-customer-billing-review-source-candidate-20261029/source-hashes.json': '47bae8c4a168348001f255cb2d727e7d1880c83ace2622e725d948783363feff', 'expansion/plans/core-customer-billing-review-source-candidate-20261029/source-review.json': 'ed4366bd2dce938273b332ad5332452148a17dbc35923d2421f1f5ae452618ef', 'expansion/plans/core-customer-billing-review-source-candidate-20261029/source-trace-links.json': 'a52cdf7c507cd571cbcd51f83444379be8602cbe2263202d235c68ccd6c15145', 'production/freeze_core_certification_administration_20261028.py': '3383b1bfa075c00a43c2a7925b0e10e3cfde5ec65f82b7efc3937bb842feb7e2'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(sources=SOURCES,core=CORE):
 sys.path.insert(0,str(ROOT/'scripts'))
 from verify_capture_evidence import _image_dimensions,visible_controls_digest
 from expansion_site import lesson_content_digest
 for p,h in PINS.items():assert sha(sources/p)==h,'Changed retained input: '+p
 lesson=json.loads((sources/BASE/'candidate.json').read_text())
 captures=json.loads((sources/BASE/'captures.reviewed.json').read_text())
 sequence=json.loads((sources/BASE/'screen-sequence.json').read_text())
 narration=(sources/BASE/'narration.txt').read_text()
 source=json.loads((sources/BASE/'source-evidence.json').read_text())
 raw=[]
 for m in captures['raw_manifests']:
  assert sha(sources/m['file'])==m['sha256']
  raw+=json.loads((sources/m['file']).read_text())
 assert len(raw)==16 and len(captures['screenshots'])==15
 assert [x['id'][:3]for x in captures['rejected_sources']]==['015']
 originals={r['id']:r for r in raw}
 for r in raw:
  assert sha(sources/r['file'])==r['sha256'] and sha(sources/r['dom_file'])==r['dom_sha256'],r['id']
  assert _image_dimensions(sources/r['file'])==(r['width'],r['height'])
 for r in captures['screenshots']:
  for k in ['file','sha256','dom_file','dom_sha256','provenance']:assert r[k]==originals[r['id']][k]
  assert r['eligible_for_lesson'] and r['capture_review']['passed']
  assert r['capture_review']['sha256']==r['sha256']
  assert r['capture_review']['controls_sha256']==visible_controls_digest(r['visible_controls'])
  assert all('BillingEmail'not in x for x in r['visible_labels'])
 assert len(source['files'])==20
 for r in source['files']:
  assert sha(sources/r['snapshot_file'])==r['sha256'],'Changed snapshot: '+r['file']
  assert sha(core/r['file'])==r['sha256'],'Cited Core file differs: '+r['file']
 g=sources/'production/freeze_core_certification_administration_20261028.py'
 spec=importlib.util.spec_from_file_location('retained_billing_correspondence',g);guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
 guard.verify_correspondence(lesson,sequence,captures,narration)
 for x in sequence['scenes']:assert x['narration']==' '.join(s['narration_span']for s in x['screens'])
 assert len(lesson['scenes'])==11 and len(lesson['sector_examples'])==6
 assert sum(len(x['screens'])for x in sequence['scenes'])==19
 assert len(re.findall(r"\b[\w]+(?:['’\-][\w]+)*\b",narration))==843
 assert lesson['candidate_only']is True and lesson['export_ready']is False and lesson['parent_full_script_review_pending']is True
 scenario=json.loads((sources/BASE/'scenario.replay.json').read_text())
 assert scenario['actual_mutations']==[] and all(x['write']is False for x in scenario['safe_UI_steps'])
 return {'passed':True,'source_only':True,'read_only':True,'words':843,'scenes':11,'untimed_spans':19,
 'raw_pairs_preserved':16,'accepted_images':15,'source_files':20,'candidate_sha256':sha(sources/BASE/'candidate.json'),
 'narration_sha256':sha(sources/BASE/'narration.txt'),'authoring_sha256':lesson_content_digest(lesson),
 'parent_script_review_pending':True,'frozen_or_media_qualified':False}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sources',type=Path,default=SOURCES);p.add_argument('--core-source',type=Path,default=CORE)
 a=p.parse_args();print(json.dumps(verify(a.sources.resolve(),a.core_source.resolve()),indent=2))
if __name__=='__main__':main()
