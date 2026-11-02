"""Freeze the accepted initial Training-record entry sources without editing history.

Default/--check reads only; --freeze creates the one new named package and
refuses existing output. Preserve candidate bytes, all19raw pairs and the first
finalization/revision1 boundary. Later amendment is a separate source checkpoint.
No browser, DB, Descript, audio, canonical, readiness, site, target or Git action.
"""
import argparse,hashlib,importlib.util,json,re,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];SOURCES=ROOT/'sources';CORE=ROOT.parents[2]
NAME='core-records-training-entry'
BASE=Path('expansion/plans/core-records-training-entry-source-candidate-20261029')
ACCEPT=Path('expansion/plans/core-records-training-entry-script-acceptance-20261029/accepted-script-review.json')
FREEZE=Path('expansion/plans/core-records-training-entry-capture-freeze-20261029')
PINS={'captures/expansion/core-records-training-entry-20261029/manifest.json': 'd8de7d8d1755034c7f195322136eff150fb5cab5c0a5d9ecabeb901934264bc0', 'expansion/audits/core-records-training-entry-source-candidate-preflight-20261029.json': 'e0a33c6348c75ad594ff14a054d0c514448172ab114b984874b4d49380994273', 'expansion/plans/core-records-training-entry-handout-20261029/academy-record-entry-handout.txt': 'b249a108a0968c63d7dfe4505de08722642a02c8d2eca26fb276972f04055c2d', 'expansion/plans/core-records-training-entry-script-acceptance-20261029/accepted-script-review.json': 'ad3d7c42ce7d7cc10d22f88910a90b450184f53d571c0a849bb78be9a0a46c3d', 'expansion/plans/core-records-training-entry-source-candidate-20261029/actual-operation-log.json': 'c333b93d483398db954e0692b483bacb54076041984ee32e508746f8992ec597', 'expansion/plans/core-records-training-entry-source-candidate-20261029/candidate.json': 'e3df33c2315187e211c0e5c83f8ea0468c22cb549230c0cb752d736853ad9bc5', 'expansion/plans/core-records-training-entry-source-candidate-20261029/capture-checklist.json': 'ff42b605807252fc7f6dbe61120328b2332fb5302311f5737ac55e7cd3cf3fcf', 'expansion/plans/core-records-training-entry-source-candidate-20261029/captures.reviewed.json': '5b68213bc9d30836bd390af797042554b0f024fa2e40aebc8c93b47ffdc2509f', 'expansion/plans/core-records-training-entry-source-candidate-20261029/compact-correspondence.json': 'b32e5c8452a81e0aad9ba8d3b68df72f367511c481914f3be1e1b8bcaa7d5005', 'expansion/plans/core-records-training-entry-source-candidate-20261029/contact-sheet.jpg': 'cb51bbbff32cd9a70fa1ba34551f680bb88d2af38e304403964a0c5a1d2ff8ba', 'expansion/plans/core-records-training-entry-source-candidate-20261029/narration.txt': '42de87f24123001c5cc1344d9fad1c9cbd59546f2f27789197f698d82f506e3e', 'expansion/plans/core-records-training-entry-source-candidate-20261029/scenario.replay.json': '9ca34946dad55afb2566bd8ac517233ca9ad89e033e174d7c40347285c4fd950', 'expansion/plans/core-records-training-entry-source-candidate-20261029/screen-sequence.json': 'c3737fab6be3a420d64b9b0a284f41078325c02881d0a47d927964eb23adf08a', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Core/Resgrid.Framework/RecordNarrativeFormatter.cs': 'dacc4a55fd0fd1a9ea99b9ae60a4b82eecf3e655ae04489d2c4d840a967a41c9', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Core/Resgrid.Localization/Areas/User/Records/Records.en.resx': '4fb5859729af6e159ef61a21eb5a9b877dfe76b5f86c2b7f617e0cdbabbaf012', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Core/Resgrid.Model/Records/RmsDefinitionKeys.cs': '1f85da59debb8dda04890b23eee2b92cf53949aeb691fa7c309562833a7917f0', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Core/Resgrid.Model/Records/RmsEnums.cs': 'e54c004becf4e9f08b062a9f9c6f780c1e296135b4fe09f108560403d9d368cf', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Core/Resgrid.Model/Records/RmsEvidenceArtifact.cs': '2a460b9508b8088f9a271c96925decc2348de3738afddb1bc94903097f3b4dd5', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Core/Resgrid.Model/Records/RmsLifecycle.cs': '6c3224468deb5bd2c0b66e3772ac5403366b77e0375cd303689ab35bf74918ae', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Core/Resgrid.Model/Records/RmsOperationalRecordDetail.cs': 'f9d5611981d31ff53be5f4b59912bdcddb971251ace59f0fa5f7117f0e222764', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Core/Resgrid.Model/Records/RmsRevision.cs': '8e19c999989ea2be7321790a689e089f98075a85d5e51e318bfc1eeee553bb32', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Core/Resgrid.Services/Records/RecordAttachmentHygiene.cs': 'a86e2bec0e3e4f92c85643cc9f83991edf4ecb302e4c08127b0227ae960b86c7', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Core/Resgrid.Services/Records/RecordSnapshotSerializer.cs': 'f3cf131a080cfa639c0e6225d9a512aaa6706f77b7eeb8e04dc1b58511efab78', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Core/Resgrid.Services/Records/RecordsAuthorizationService.cs': 'd67e3ae6e972631f720e06b92a684ca73a1afcd559b04ca198833db90a6ce922', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Core/Resgrid.Services/Records/RecordsDocumentService.cs': '7e661aa66ced75e0a319913de5f6b8749cf2f7d553a81e016e5d86592a91030a', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Core/Resgrid.Services/Records/RecordsLifecycleAuthority.cs': 'e506ff630f98fdb5f1962e3c81d4e4621409b82f610ef4fdba8d61628fe11a30', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Core/Resgrid.Services/Records/RecordsNumberingService.cs': '04f97c9b4b5013661a0d86bbc5d19bf86ebf57f9f14281444bef58e9974c9542', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Core/Resgrid.Services/Records/RecordsProtectionService.cs': '334374d0203e8356c723fe68c3d26d477cc45401e0118c6ced9ed8465520575c', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Core/Resgrid.Services/Records/RecordsService.cs': 'ef743169e47e0726a181353fb9af69341bb390764c4d95ef89e61725c0fcd28d', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Web/Resgrid.Web/Areas/User/Controllers/RecordDocumentsController.cs': '9f99ecf76ffb0d39fd9ea8b196c6b1f0a49b894f7430380372acd0ca2cffc79d', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Web/Resgrid.Web/Areas/User/Controllers/RecordsController.cs': '7fe5dcb35ba6c27c44bd4f4cb7b664cea9d19b1cef973c2ab2070cdb9d37a767', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Web/Resgrid.Web/Areas/User/Models/Records/RecordsViewModels.cs': '532f7e8e87c5eb8fe4fd24287d7016163ab3fd4bd6eb35f5688217f8e1fbbf50', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Web/Resgrid.Web/Areas/User/Views/Records/Details.cshtml': '7577b9dfe177af5d8487e7f98a3f3756c5d82302e0846b97cd59a31b91293e05', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Web/Resgrid.Web/Areas/User/Views/Records/Edit.cshtml': 'a6f777b6f949805fcf95580171bdf58fcefc4e01b47124aaf7da4b50340770e8', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Web/Resgrid.Web/Areas/User/Views/Records/Index.cshtml': '88d9e21f6b190f254d50c80ed13e259dbb65c2b621c9aec362c04f9e8cef8f79', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Web/Resgrid.Web/Helpers/RecordsLifecycleClaims.cs': '17a48f7e42e6d89d20e65d24767f5e6bdecaaea3d10b05ca1d48bce40160e6cf', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source/Core/Web/Resgrid.Web/wwwroot/js/record-authoring.js': '9e9809c42552333193de00d2509311f65ba8de90781c111b836f3602528477db', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source-evidence.json': '83462d04ab81ce95883c78e32366bc678e218423c3677cf1fb68e1f4f805ec47', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source-hashes.json': 'd2bebdf8758d4bdba20462be4ee45d6d7565aa7d2e0d62e37b693145e75883dc', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source-review.json': '42225f08b7f0f1da3e5e7c3341e55c6ee957c5ea811f83e8fc636a5c064e1e4a', 'expansion/plans/core-records-training-entry-source-candidate-20261029/source-trace.json': '4381c791bb0dc7bf3ebefc354be145dfcc6dbbb6d1ad08dd3439c45ea9465f77', 'production/freeze_core_certification_administration_20261028.py': '3383b1bfa075c00a43c2a7925b0e10e3cfde5ec65f82b7efc3937bb842feb7e2'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def encoded(x):return(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()
def prepare(sources=SOURCES,core=CORE):
 sys.path.insert(0,str(ROOT/'scripts'))
 from expansion_site import lesson_content_digest
 from verify_capture_evidence import _image_dimensions,visible_controls_digest
 for p,h in PINS.items():assert sha(sources/p)==h,'Changed retained input: '+p
 lesson=json.loads((sources/BASE/'candidate.json').read_text())
 seq=json.loads((sources/BASE/'screen-sequence.json').read_text())
 captures=json.loads((sources/BASE/'captures.reviewed.json').read_text())
 narration=(sources/BASE/'narration.txt').read_text()
 source=json.loads((sources/BASE/'source-evidence.json').read_text())
 review=json.loads((sources/ACCEPT).read_text());assert review['accepted']is True and review['freeze_authorized']is True
 assert review['human_full_audio_listening_approved']is False and review['private_export_approved']is False
 assert review['narration']['sha256']==sha(sources/BASE/'narration.txt') and review['candidate']['sha256']==sha(sources/BASE/'candidate.json')
 assert review['compact_map']['sha256']==sha(sources/BASE/'compact-correspondence.json')
 raw=[]
 for x in captures['raw_manifests']:
  assert sha(sources/x['file'])==x['sha256'];raw+=json.loads((sources/x['file']).read_text())
 assert len(raw)==19 and len(captures['screenshots'])==16
 assert {x['id'][:3]for x in captures['rejected_sources']}=={'005','008','018'}
 originals={r['id']:r for r in raw}
 for r in raw:
  assert sha(sources/r['file'])==r['sha256']and sha(sources/r['dom_file'])==r['dom_sha256'],r['id']
  assert _image_dimensions(sources/r['file'])==(1434,773)
 for r in captures['screenshots']:
  for k in ['file','sha256','dom_file','dom_sha256','provenance']:assert r[k]==originals[r['id']][k]
  assert r['eligible_for_lesson']and r['capture_review']['passed']and r['capture_review']['sha256']==r['sha256']
  assert r['capture_review']['controls_sha256']==visible_controls_digest(r['visible_controls'])
 assert len(source['files'])==24
 for r in source['files']:
  assert sha(sources/r['snapshot_file'])==r['sha256'],'Changed retained snapshot: '+r['file']
  assert sha(core/r['file'])==r['sha256'],'Cited Core file differs: '+r['file']
 g=sources/'production/freeze_core_certification_administration_20261028.py';sp=importlib.util.spec_from_file_location('retained_record_source_guard',g);guard=importlib.util.module_from_spec(sp);sp.loader.exec_module(guard)
 guard.verify_correspondence(lesson,seq,captures,narration)
 for x in seq['scenes']:assert x['narration']==' '.join(y['narration_span']for y in x['screens'])
 assert len(lesson['scenes'])==12 and len(lesson['sector_examples'])==6 and sum(len(x['screens'])for x in seq['scenes'])==20
 assert len(re.findall(r"\b[\w]+(?:['’\-][\w]+)*\b",narration))==956
 assert lesson['export_ready']is False and lesson['publication_approved']is False
 scenario=json.loads((sources/BASE/'scenario.replay.json').read_text());record=scenario['retained_actual_record']
 assert record['definition_key']=='system.training'and record['id']=='0795ea02-2d42-4940-8d1a-d95094281f75'
 assert record['issued_number']=='TRN-2026-0002'and record['draft_reference']=='D-YXS93'
 assert record['participants']==[]and record['unit_time_rows']==[]
 a=scenario['attachment'];assert a['classification_value']==0 and a['bytes']==358 and sha(sources/a['file'])==a['sha256']
 copies={NAME+'.narrated-source.json':'candidate.json',NAME+'.captures.reviewed.json':'captures.reviewed.json',NAME+'.screen-sequence.json':'screen-sequence.json',
 'narration.txt':'narration.txt','compact-correspondence.json':'compact-correspondence.json','scenario.replay.json':'scenario.replay.json',
 'source-evidence.json':'source-evidence.json','source-review.json':'source-review.json','source-trace.json':'source-trace.json',
 'capture-checklist.json':'capture-checklist.json','actual-operation-log.json':'actual-operation-log.json'}
 outputs={n:(sources/BASE/original).read_bytes()for n,original in copies.items()};outputs['accepted-script-review.json']=(sources/ACCEPT).read_bytes()
 outputs['source-hashes.json']=encoded({'schema_version':1,'id':NAME,'status':'Accepted immutable source-only initial-entry freeze; no audio/timing/media/publication qualification',
 'words':956,'scenes':12,'untimed_spans':20,'six_sectors':6,'raw_pairs_preserved':19,'accepted_sources':16,'cited_source_files':24,
 'narrated_source_sha256':sha(sources/BASE/'candidate.json'),'narration_sha256':sha(sources/BASE/'narration.txt'),'authoring_sha256':lesson_content_digest(lesson),
 'Core_HEAD':source['Core_HEAD'],'source_identity_not_binary_attestation':True,'parent_script_and_map_accepted':True,
 'candidate_metadata_preserved':'Candidate retains original pending-review flags; this new freeze manifest/accepted receipt records the later genuine acceptance without changing words or source order.',
 'first_finalization_historical_boundary_preserved':True,'human_full_audio_listening_approved':False,'private_export_approved':False,
 'input_pins':[{'file':p,'sha256':h}for p,h in PINS.items()],
 'outputs':[{'file':n,'sha256':hashlib.sha256(b).hexdigest()}for n,b in outputs.items()],
 'recipe':{'file':'production/'+Path(__file__).name,'sha256':sha(__file__)},
 'write_boundary':'Default/--check is read-only. --freeze creates the named new-only package and refuses existing output.'})
 return outputs,guard

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sources',type=Path,default=SOURCES);p.add_argument('--core-source',type=Path,default=CORE);p.add_argument('--check',action='store_true');p.add_argument('--freeze',action='store_true');a=p.parse_args();out,g=prepare(a.sources.resolve(),a.core_source.resolve());dest=a.sources/FREEZE
 if a.freeze:g.write_new_package(dest,out)
 elif dest.exists():
  assert {p.name for p in dest.iterdir()}==set(out),'Frozen inventory differs.'
  for n,b in out.items():assert(dest/n).read_bytes()==b,'Changed frozen file: '+n
 print(json.dumps({'passed':True,'source_only':True,'files_written':a.freeze,'words':956,'scenes':12,'untimed_spans':20,'images':16,
 'narrated_source_sha256':hashlib.sha256(out[NAME+'.narrated-source.json']).hexdigest(),'narration_sha256':hashlib.sha256(out['narration.txt']).hexdigest(),
 'source_freeze_sha256':hashlib.sha256(out['source-hashes.json']).hexdigest(),'parent_script_accepted':True,'audio_or_video_qualified':False},indent=2))
if __name__=='__main__':main()
