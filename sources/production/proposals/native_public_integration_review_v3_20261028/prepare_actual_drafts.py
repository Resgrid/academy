#!/usr/bin/env python3
"""Prepare actual, explicitly UNREVIEWED native bridge drafts from retained sources.

Default reads/checks only. --write creates a NEW proposal-local draft directory.
No passed pixel/source/context review is authored; reviewer/check fields are null.
No app, UI, SDK, private binary, auth, backend, canonical or site writes occur.
"""
import argparse,copy,json,hashlib,sys
from pathlib import Path
from datetime import datetime
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];S=ROOT/'sources'
sys.path.insert(0,str(HERE/'proposed/scripts'))
import native_capture_public as n
from actual_bridge_preflight import findings,source_file,FREEZE,FREEZE_SHA
OUT=HERE/'actual-drafts'
ADD='expansion/audits/unit-native-context-addendum-20261028/'
PINS={ADD+'fresh-installed-macho-confirmation.json':'b0f3c0e3c28f24331de11ea0ef48882fc89dfdb5eeac3383384b9d0e0f4bd922',ADD+'own-device-creation.json':'b678e2c8398a05505f3525b52f2b20e74c0e7e8f1105b28737a4f0ceca31c520',ADD+'css-snapshot-receipt.json':'c38a9f447a05074d77c88c48eb704995077744a5b798e722a5b8421d0c3af3ab',ADD+'test-driver-events-context.json':'5824b50535f5e3a218bec5fb19aacb17fb75198dc42dbedc20d396cbcd8d27ec',ADD+'product-source-and-driver-context.json':'ccbe872e83460766f3127a553bd4e205150631b8793009fee3fdec5104d96272'}
def read(p):return n.unique_json(p.read_text())
def timestamp(s):return datetime.fromisoformat(s.replace('Z','+00:00'))
def plan():
 actual=findings();base=source_file(FREEZE+'/source-freeze.json',FREEZE_SHA).parent;freeze=read(base/'source-freeze.json');files={};originals={}
 def ref_existing(p):return {'file':p.relative_to(S).as_posix(),'sha256':n.sha(p)}
 def put(name,body):
  data=body if isinstance(body,bytes) else (json.dumps(body,indent=2,ensure_ascii=False)+'\n').encode();files[name]=data;return {'file':(OUT/name).relative_to(S).as_posix(),'sha256':hashlib.sha256(data).hexdigest()}
 def retained(name,p):
  originals[name]=ref_existing(p);return put('retained/'+name,p.read_bytes())
 def mapped(original):
  r=freeze['public_package_path_map'][original];return source_file(r['file'],r['sha256'])
 extras={}
 for rel,digest in PINS.items():extras[Path(rel).name]=retained(Path(rel).name,source_file(rel,digest))
 own=read(source_file(ADD+'own-device-creation.json',PINS[ADD+'own-device-creation.json']));ctx=read(mapped('captures/expansion/unit-native-20261028/review/capture-runtime-review-20261028.json'));session=ctx['actual_session']
 for key in ['udid','created_at','device_type','os_version']:assert own[key]==session[key]
 assert own['creation_exit_code']==0 and own['other_devices_included'] is False and own['dedicated'] is True
 creation={'id':session['session_id'],'udid':session['udid'],'device_type':session['device_type'],'os_version':session['os_version'],'created_at':session['created_at'],'method':'new_dedicated_simulator'}
 creation_ref=put('normalized/creation.json',creation)
 inventory=actual['reported_installed_macho_inventory_candidate'];inventory_ref=put('normalized/installed-macho-inventory.json',inventory)
 build_raw=read(mapped('production/native-unit/reports/native-build-identity-20261028.json'))['metadata'];baseline=read(mapped('production/native-unit/reports/source-preparation.json'))['metadata']
 snapshots=[{'namespace':'source','original_path':row['original_path'],'snapshot':row['retained_snapshot']} for row in actual['retained_source_snapshots']]
 snapshots.append({'namespace':'source','original_path':'ios/Podfile.lock','snapshot':ref_existing(mapped('production/native-unit/reports/owned-native-Podfile.lock'))})
 css=read(source_file(ADD+'css-snapshot-receipt.json',PINS[ADD+'css-snapshot-receipt.json']))
 for row in css['files']:
  assert row['matches_pinned_archive'] is True
  p=source_file(row['public_snapshot'],row['sha256']);data=p.read_bytes();assert not n.SECRET.search(data)
  snap=put('snapshots/'+row['source_file'],data);snapshots.append({'namespace':'source','original_path':row['source_file'],'snapshot':snap})
 snapshot_ref=put('normalized/source-snapshots.json',{'base_source_revision':baseline['revision'],'snapshots':snapshots})
 primary=next(x for x in inventory['files'] if x['file']==build_raw['executable'])
 build={'mode':'development_metro','base_source_revision':baseline['revision'],'bundle_id':build_raw['bundle_id'],'native_sdk':build_raw['sdk'],'installed_binary_sha256':primary['sha256'],'installed_info_plist_sha256':build_raw['info_plist_sha256'],'installed_mach_o_inventory':inventory_ref,'snapshot_manifest':snapshot_ref}
 initial_ref=ref_existing(mapped('production/native-unit/reports/native-installed-binary-comparison-20261028.json'))
 product=read(source_file(ADD+'product-source-and-driver-context.json',PINS[ADD+'product-source-and-driver-context.json']));latest=product['latest_retained_count_driver_source'];driver=source_file(latest['public_file'],latest['sha256']);driver_ref=put('retained/latest-count-driver.swift',driver.read_bytes());product['latest_retained_count_driver_source']['public_file']=driver_ref['file'];product_ref=put('normalized/product-source-context.json',product)
 parent_ref=retained('parent-source-review.json',source_file('expansion/audits/unit-native-parent-source-review-20261028.json','34cced0b67e8f76c5c7a9de333588d2b2bc4f2529c0c2feb7b2c1023f2f8389a'))
 owner_ref=ref_existing(mapped('captures/expansion/unit-native-20261028/review/pixel-review-20261028-v2.json'))
 ui_ref=ref_existing(mapped('captures/expansion/unit-native-20261028/review/normal-ui-action-ledger-20261028.json'));ui=read(S/ui_ref['file']);served_ref=ref_existing(mapped('captures/expansion/unit-native-20261028/review/served-stream-ledger-20261028.json'));served=read(S/served_ref['file'])
 manifest=read(base/'captures.reviewed.json');members=manifest['native_sources'];first=min(x['captured_at'] for x in members);last=max(x['captured_at'] for x in members);capture_manifest_ref=ref_existing(base/'captures.reviewed.json');binary_at=actual['actual_installed_binary_comparison']['verified_at'];by_id={x['id']:x for x in members}
 entries=[]
 for fact in actual['captures']:
  row=by_id[fact['id']];at=fact['captured_at'];metadata=read(source_file(row['metadata_file'],row['metadata_sha256']));ax=metadata['native_accessibility_observation'];guard=ax['result'];assert guard['device_orientation']==3
  display={'session_id':session['session_id'],'udid':session['udid'],'measured_at':ax['at'],'method':'xcuitest_frame_and_uiscreen_scale','orientation':'landscape_left','dpr':guard['screen_scale'],'screen_points':{'width':guard['app_frame_points']['width'],'height':guard['app_frame_points']['height']},'app_viewport_points':guard['app_frame_points'],'pixel_width':row['width'],'pixel_height':row['height']};geometry_ref=put('normalized/'+row['id']+'.geometry.json',display)
  guard_entry=next(e for e in ui['entries'] if e['response'].get('id')==ax.get('id') and e['response'].get('at')==ax.get('at'))
  geometry_events=[{'at':e['response']['at'],'kind':'rotate','udid':session['udid'],'source_entry_sha256':n.digest(e)} for e in ui['entries'] if e['request'].get('action') in {'landscape','portrait','rotate'} and e.get('response',{}).get('at')]
  normal={'session_id':session['session_id'],'udid':session['udid'],'bundle_id':build['bundle_id'],'method':'xcuitest','source_ledger':ui_ref,'actions':[{'id':ax['id'],'at':ax['at'],'kind':'observe_screen','control':guard['bundle_id'],'observation':'Recorded native capture_guard supplies foreground/frame context only. Current literal controls are preserved from existing actual PNG pixel reviews; no new AX or UI observation is invented.','source_entry_sha256':n.digest(guard_entry)}],'geometry_events':geometry_events};normal_ref=put('normalized/'+row['id']+'.normal-ui.json',normal)
  scope={'started_at':first,'ended_at':last,'capture_manifest':capture_manifest_ref,'same_device_udid':session['udid'],'bundle_id':build['bundle_id'],'base_source_revision':baseline['revision'],'installed_mach_o_inventory_sha256':inventory_ref['sha256'],'full_normal_ui_ledger_sha256':ui_ref['sha256'],'product_managed_native_source_unchanged':None,'product_binary_observations':[initial_ref,extras['fresh-installed-macho-confirmation.json']],'instrumentation_event_ledger':extras['test-driver-events-context.json'],'product_source_context':product_ref,'installation_continuity_claimed':False,'continuous_execution_identity_proven':False}
  identity={'reviewer':None,'reviewed_at':None,'method':None,'binding_sha256':None,'session_id':session['session_id'],'udid':session['udid'],'foreground_bundle_id':build['bundle_id'],'observation_at':binary_at,'snapshot_manifest_sha256':snapshot_ref['sha256'],'correspondence_scope':'reviewed_recording_session','recording_session':scope,'additional_binary_confirmations':[extras['fresh-installed-macho-confirmation.json']],'findings':None}
  identity['binding_sha256']=n.installed_review_digest(build,identity);identity_ref=put('normalized/'+row['id']+'.installed-context.DRAFT.json',identity)
  b=copy.deepcopy(build);b['installed_correspondence']=identity_ref
  selected=[{'entry_index':r['entry_index'],'entry_sha256':r['entry_sha256'],'association_method':'reviewed_capture_context_only_not_authenticated','build_identity_sha256':n.build_digest(b)} for r in fact['possible_prior_served_measurements']]
  rt={'coverage':'served_response_metadata_only','transport_client_identity':'not_authenticated_by_transport','loaded_or_executed_identity':'unresolved','complete_lazy_execution_graph':'unresolved','lazy':True,'served_ledger':served_ref,'selected_streams':selected}
  rr={'reviewer':None,'reviewed_at':None,'method':None,'binding_sha256':n.digest(rt),'session_id':session['session_id'],'udid':session['udid'],'build_identity_sha256':n.build_digest(b),'observed_entry_sha256':[r['entry_sha256'] for r in selected],'findings':None};rt['review_receipt']=put('normalized/'+row['id']+'.runtime-review.DRAFT.json',rr)
  d={'schema':n.SCHEMA,'app':'Unit','kind':'application_screenshot','session':{'id':session['session_id'],'udid':session['udid'],'device_type':session['device_type'],'os_version':session['os_version'],'created_at':session['created_at'],'creation_receipt':creation_ref,'creation_source':extras['own-device-creation.json']},'build':b,'capture':{'image':{'file':row['file'],'sha256':row['sha256']},'width':row['width'],'height':row['height'],'captured_at':at,'method':metadata['provenance']['method'],'session_id':session['session_id'],'udid':session['udid'],'foreground_bundle_id':guard['bundle_id'],'simctl_method':'xcrun_simctl_io_explicit_udid_screenshot_png','display':geometry_ref},'normal_ui':normal_ref,'runtime':rt,'observations':{'visible_labels':row['manual_visible_labels'],'required_labels':row['manual_visible_labels']},'limitations':copy.deepcopy(n.LIMITS)}
  d['review']={'reviewer':None,'reviewed_at':None,'method':None,'binding_sha256':n.review_digest(d),'checks':{k:None for k in n.REVIEW_CHECKS},'findings':None}
  package_ref=put('packages/'+row['id']+'.DRAFT.json',d)
  entries.append({'id':row['id'],'package':package_ref,'image':d['capture']['image'],'existing_owner_pixel_review':owner_ref,'existing_parent_pixel_review':parent_ref,'source_native_metadata':{'file':row['metadata_file'],'sha256':row['metadata_sha256']},'missing_review_fields':['installed-context reviewer/reviewed_at/method/findings and actual product-source attestation','runtime-review reviewer/reviewed_at/method/findings','source-review reviewer/reviewed_at/method/findings and genuine explicit checks'],'product_source_attestation_pending':True,'new_passed_review_generated':False,'actual_binary_to_capture_seconds':fact['binary_observation_to_capture_seconds'],'actual_guard_age_seconds':fact['geometry_and_guard_age_seconds']})
 index={'kind':'actual_native_DRAFT_bridge_only','proposal_only':True,'publishable':False,'new_passed_review_generated':False,'immutable_source_freeze':{'file':FREEZE+'/source-freeze.json','sha256':FREEZE_SHA},'normalization_scope':'Only public relative paths, exact metadata field names and immutable geometry/guard/source/measurement facts were normalized. All reviewer/check fields remain null. Original ledgers, images, sidecars and reviews remain unchanged.','original_addenda':originals,'original_owner_pixel_review':owner_ref,'retained_parent_pixel_review':parent_ref,'recording_session':{'first':first,'last':last,'duration_seconds':(timestamp(last)-timestamp(first)).total_seconds(),'actual_initial_binary_observation':binary_at,'actual_fresh_confirmation':read(source_file(ADD+'fresh-installed-macho-confirmation.json',PINS[ADD+'fresh-installed-macho-confirmation.json']))['observed_at']},'packages':entries,'pending_root_review':'Review exact normalized bindings, original/root/owner PNG observations, named context review of actual product-code/source consistency with declared instrumentation changes, missing historical driver digests and possible identical-app reinstalls. No uninterrupted-install or execution claim. Final review metadata must come from the real reviewer, never this builder.'}
 put('bridge-index.DRAFT.json',index)
 return files,index

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args();files,index=plan()
 if args.write:
  if OUT.exists():raise ValueError('Preserve existing draft history; output already exists.')
  for name,data in files.items():p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 print(json.dumps({'proposal_only':True,'publishable':False,'drafts_written':args.write,'packages':len(index['packages']),'source_snapshots':16,'new_passed_review_generated':False,'output_files':len(files),'recording_session':index['recording_session']},indent=2))
if __name__=='__main__':main()
