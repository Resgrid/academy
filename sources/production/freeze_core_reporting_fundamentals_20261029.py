"""Verify/freeze the actual Reporting sources for root script review.

Default/--check reads only. --freeze creates only the new named package and
refuses existing output. This is an untimed source freeze, not parent script,
voice, listening, video or publication approval. No application/browser/DB,
canonical lesson, readiness, website, target or Git writes.
"""
import argparse,csv,hashlib,importlib.util,json,re,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
SOURCES=ROOT/'sources'
CORE=ROOT.parents[2]
NAME='core-reporting-fundamentals'
BASE=Path('expansion/plans/core-reporting-fundamentals-source-review-20261029')
FREEZE=Path('expansion/plans/core-reporting-fundamentals-capture-freeze-20261029')
GUARDS='production/freeze_core_certification_administration_20261028.py'
PINS={'expansion/plans/core-reporting-fundamentals-source-review-20261029/candidate.json': '9df3ae7d5998b85bf989e744e70aee5f8d93bb1212497def4631aaf661411fd7', 'expansion/plans/core-reporting-fundamentals-source-review-20261029/captures.reviewed.json': '9d823a5338d207ca99e334c48f8d1e5ef3c38b2d72894c4667e5ded98419193c', 'expansion/plans/core-reporting-fundamentals-source-review-20261029/contact-sheet.jpg': 'bf7ff678caf55db7686b880d7ffbcad303afab0de9495c550b1a74f3975526f7', 'expansion/plans/core-reporting-fundamentals-source-review-20261029/narration.txt': '3d129124f4b22379aee8f6f92148e0e6f5a03a119a7336fbf9a12883b65cd1af', 'expansion/plans/core-reporting-fundamentals-source-review-20261029/scenario.json': '614bbfab1c47cc84f6397e00573e069f0578bb0ff7db40a8d13f47930786385a', 'expansion/plans/core-reporting-fundamentals-source-review-20261029/screen-sequence.json': '250d5d801da0b2d8a2e2928b04b6edcfc17fa635428623d76747bad165e0d60a', 'expansion/plans/core-reporting-fundamentals-source-review-20261029/source/Core/Core/Resgrid.Model/Reporting/CallGroupAssigner.cs': '5b640db3629a9c6fd17b9d07479ddefec8affab90589db8a782fb811f4f2630e', 'expansion/plans/core-reporting-fundamentals-source-review-20261029/source/Core/Core/Resgrid.Model/Reporting/ReportPeriods.cs': '03b9180bde3b1d77eab13fe89d13beffe0b20c0299f31b437f6f0603e4a9301e', 'expansion/plans/core-reporting-fundamentals-source-review-20261029/source/Core/Web/Resgrid.Web/Areas/User/Models/Reports/Calls/CallSummaryView.cs': '9bad7012e0bb29725b4e598b1d711fe123cea3366a7130def842d692ec6d5e28', 'expansion/plans/core-reporting-fundamentals-source-review-20261029/source-correspondence.json': '5e53667ac760e539b4ba63a681d7f6a9c902953eddb54abbf7ca58e60aa69a0c', 'expansion/plans/core-reporting-fundamentals-source-review-20261029/source-evidence.json': 'c316d730d2c07eae93c0281e7714191d744eac50bfdd8d7015c4d80ef87ada90', 'expansion/plans/core-reporting-fundamentals-source-review-20261029/source-hashes.json': '7966a90ef2bb65500c994a804e6cdbf50865a2c13ab6318724b3863b652b021e', 'expansion/plans/core-reporting-fundamentals-source-review-20261029/source-review.json': 'c8d0fc6a35885d5c3bc94df8e59e934e3e6bbbe6242f90606e15bd53fc6843dc', 'expansion/plans/core-reporting-fundamentals-source-review-20261029/source-trace-links.json': 'db8c08857d9a5c7a61a592ef3b2d2341e6e447800586a2fbdb97e512defcf6b4', 'captures/expansion/core-reporting-fundamentals-20261029/manifest.json': 'a3afd7601d090c736d042c984f12e921c2fcc42d60bb4c5de359d8ee002e5cdd', 'captures/expansion/core-reporting-fundamentals-chrome-20261029/manifest.json': 'b83e8557c9dbfc89cde1d8556ba8a592abc0d89aa7a8290c6bb0188d8468ebe5', 'expansion/plans/core-reporting-actual-exports-20261029/call-unit-times.csv': 'c978b3ad5fa32c5b264486eb06a0a385dc4e1aa9db71bb861843aab8ca3792c6', 'expansion/plans/core-reporting-actual-exports-20261029/download.receipt.json': 'd50ba686cc1378fd1161b95941417a1fb009e206b31675e6d6dca1f276031723', 'production/freeze_core_certification_administration_20261028.py': '3383b1bfa075c00a43c2a7925b0e10e3cfde5ec65f82b7efc3937bb842feb7e2', 'expansion/audits/core-reporting-fundamentals-source-candidate-preflight-20261029.json': 'c89b9a0b0157fec4e722710b38023eac81c45da088b4e64a09f5bc040b124c18', 'expansion/audits/core-records-definition-partial-source-review-20261029.json': 'c5ab8fd7d800edbb1c40c2351d870957a5c7b7974f05001ec5ab870be8d22019'}
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
def prepare(sources=SOURCES,core_source=CORE):
 sys.path.insert(0,str(ROOT/'scripts'))
 from expansion_site import lesson_content_digest
 from verify_capture_evidence import _image_dimensions,visible_controls_digest
 for path,digest in PINS.items():assert sha(sources/path)==digest,'Changed retained input: '+path
 spec=importlib.util.spec_from_file_location('retained_reporting_freeze_guards',sources/GUARDS)
 guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
 lesson=json.loads((sources/BASE/'candidate.json').read_text())
 captures=json.loads((sources/BASE/'captures.reviewed.json').read_text())
 sequence=json.loads((sources/BASE/'screen-sequence.json').read_text())
 source=json.loads((sources/BASE/'source-evidence.json').read_text())
 narration=(sources/BASE/'narration.txt').read_text()
 raw=[]
 for manifest in captures['raw_manifests']:
  assert sha(sources/manifest['file'])==manifest['sha256']
  raw+=json.loads((sources/manifest['file']).read_text())
 assert len(raw)==27 and len(captures['screenshots'])==23
 assert {r['id'][:3]for r in captures['rejected_sources']}=={'004','005','013','026'}
 originals={r['id']:r for r in raw}
 for r in raw:
  assert sha(sources/r['file'])==r['sha256'] and sha(sources/r['dom_file'])==r['dom_sha256'],r['id']
  assert _image_dimensions(sources/r['file'])==(r['width'],r['height'])
 for r in captures['screenshots']:
  original=originals[r['id']]
  for key in ['file','sha256','dom_file','dom_sha256','provenance']:
   assert r[key]==original[key],'Changed actual capture identity.'
  assert r['eligible_for_lesson'] and r['capture_review']['passed']
  assert r['capture_review']['sha256']==r['sha256']
  assert r['capture_review']['controls_sha256']==visible_controls_digest(r['visible_controls'])
 assert len(source['files'])==13
 for r in source['files']:
  assert sha(sources/r['snapshot_file'])==r['sha256'],'Changed retained source snapshot: '+r['file']
  assert sha(core_source/r['file'])==r['sha256'],'Cited Core source differs: '+r['file']
 guard.verify_correspondence(lesson,sequence,captures,narration)
 for row in sequence['scenes']:
  assert row['narration']==' '.join(x['narration_span']for x in row['screens']),'Untimed span words changed.'
 assert len(lesson['scenes'])==13 and len(lesson['sector_examples'])==6
 assert sum(len(x['screens'])for x in sequence['scenes'])==27
 words=len(re.findall(r"\b[\w]+(?:['’\-][\w]+)*\b",narration));assert words==1023
 assert lesson['export_ready']is False and lesson['publication_approved']is False and lesson['parent_full_script_review_pending']is True
 scenario=json.loads((sources/BASE/'scenario.json').read_text())
 assert all(x['mutation']is False for x in scenario['steps'])
 assert scenario['steps'][1]['actual_observed']['calls']==15
 assert scenario['steps'][3]['actual_observed']['calls']==5 and scenario['steps'][4]['actual_observed']['calls']==16
 assert scenario['steps'][3]['parameters']['start']==scenario['steps'][4]['parameters']['start']
 assert scenario['steps'][3]['parameters']['end']==scenario['steps'][4]['parameters']['end']
 export=Path('expansion/plans/core-reporting-actual-exports-20261029')
 csv_path=sources/export/'call-unit-times.csv'
 data=list(csv.DictReader(csv_path.open(encoding='utf-8-sig',newline='')))
 assert len(data)==13 and len({x['Call Number']for x in data})==12
 assert sorted({x['Linked By']for x in data})==['DispatchOnly','Explicit']
 copies={NAME+'.narrated-source.json':'candidate.json',NAME+'.captures.reviewed.json':'captures.reviewed.json',
 NAME+'.screen-sequence.json':'screen-sequence.json','narration.txt':'narration.txt','scenario.json':'scenario.json',
 'source-correspondence.json':'source-correspondence.json','source-review.json':'source-review.json',
 'source-evidence.json':'source-evidence.json','source-trace-links.json':'source-trace-links.json'}
 outputs={name:(sources/BASE/original).read_bytes()for name,original in copies.items()}
 outputs['script-review-status.json']=encoded({'kind':'frozen_source_for_parent_full_script_review',
 'parent_requested_source_freeze':True,'parent_full_script_review_pending':True,
 'parent_full_script_review_approved':False,'human_full_audio_listening_review':False,
 'independent_original_pixel_review':{'images':27,'accepted':23,'excluded':4,'reviewer':'Codex /root/core_configuration_coverage'},
 'exact_narration_sha256':PINS[(BASE/'narration.txt').as_posix()],
 'limits':'No parent full script or human listening review is inferred. No audio/timing/video/canonical/public readiness is created.'})
 outputs['source-hashes.json']=encoded({'schema_version':1,'id':NAME,
 'status':'Untimed source-only Reporting freeze for root full-script read; no media/publication approval',
 'spoken_words':1023,'scenes':13,'six_sectors':6,'raw_pairs_preserved':27,'accepted_sources':23,'untimed_spans':27,
 'cited_Core_file_pins':13,'candidate_sha256':PINS[(BASE/'candidate.json').as_posix()],
 'narration_sha256':PINS[(BASE/'narration.txt').as_posix()],
 'authoring_sha256':lesson_content_digest(lesson),'Core_HEAD':source['Core_HEAD'],
 'source_identity_not_binary_attestation':True,'parent_script_review_accepted':False,
 'full_human_audio_listening_review':False,
 'actual_export':{'file':(export/'call-unit-times.csv').as_posix(),'sha256':sha(csv_path),'bytes':2699,'unit_rows':13,'distinct_calls':12},
 'input_files':[{'file':p,'sha256':h}for p,h in PINS.items()],
 'outputs':[{'file':name,'sha256':hashlib.sha256(data).hexdigest()}for name,data in outputs.items()],
 'recipe':{'file':'production/'+Path(__file__).name,'sha256':sha(__file__)},
 'write_boundary':'Default/--check is read-only. --freeze creates only this new named source package and refuses an existing destination.'})
 return outputs,guard

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--sources',type=Path,default=SOURCES)
 p.add_argument('--core-source',type=Path,default=CORE)
 p.add_argument('--check',action='store_true',help='Read-only pre/post-freeze verification (default).')
 p.add_argument('--freeze',action='store_true',help='Create only the new named source-only package; refuse existing output.')
 args=p.parse_args();outputs,guard=prepare(args.sources.resolve(),args.core_source.resolve())
 destination=args.sources/FREEZE
 if args.freeze:guard.write_new_package(destination,outputs)
 elif destination.exists():
  assert {x.name for x in destination.iterdir()}==set(outputs),'Frozen file inventory changed.'
  for name,data in outputs.items():assert (destination/name).read_bytes()==data,'Changed frozen output: '+name
 print(json.dumps({'passed':True,'source_only':True,'files_written':args.freeze,'scenes':13,'words':1023,
 'source_images':23,'raw_pairs_preserved':27,'untimed_spans':27,'source_files':13,
 'narrated_source_sha256':hashlib.sha256(outputs[NAME+'.narrated-source.json']).hexdigest(),
 'source_freeze_sha256':hashlib.sha256(outputs['source-hashes.json']).hexdigest(),
 'parent_script_approval_pending':True,'canonical_or_ready_changed':False},indent=2))
if __name__=='__main__':main()
