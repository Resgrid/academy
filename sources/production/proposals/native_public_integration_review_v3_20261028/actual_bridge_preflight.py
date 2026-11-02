#!/usr/bin/env python3
"""Read-only actual frozen-source bridge findings; NEVER emits passed reviews.

Uses public retained JSON/PNG only. No SDK/private app/npm/source root reads,
network, browser, native runtime, API, canonical or readiness changes. --output
may save one NEW findings document inside this proposal, never a source package.
"""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import struct
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
S=ROOT/'sources'
sys.path.insert(0,str(HERE/'proposed/scripts'))
import native_capture_public as native
FREEZE='expansion/plans/app-unit-inventory-native-counts-capture-freeze-20261028'
FREEZE_SHA='421693c5a83525b284e3073eb10f6778680ecfbb62f46a5f1638b458f20376ac'
PARENT_REVIEW='expansion/audits/unit-native-parent-source-review-20261028.json'
PARENT_SHA='34cced0b67e8f76c5c7a9de333588d2b2bc4f2529c0c2feb7b2c1023f2f8389a'

def read(p):return native.unique_json(p.read_text())
def when(s):return datetime.fromisoformat(s.replace('Z','+00:00'))
def ref(p):return {'file':p.relative_to(S).as_posix(),'sha256':native.sha(p)}
def source_file(name,expected=None):
 p=(S/name).resolve()
 if not p.is_relative_to(S.resolve()) or not p.is_file():raise ValueError('Required public asset missing or outside sources.')
 if expected and native.sha(p)!=expected:raise ValueError('Retained public asset hash differs: '+name)
 return p

def findings():
 b=source_file(FREEZE+'/source-freeze.json',FREEZE_SHA).parent
 freeze=read(b/'source-freeze.json')
 for name,digest in freeze['freeze_files'].items():
  p=(b/name).resolve()
  if not p.is_relative_to(b) or not p.is_file() or native.sha(p)!=digest:raise ValueError('Frozen file missing or changed: '+name)
 mapping=freeze['public_package_path_map']
 def mapped(original):
  r=mapping[original];return source_file(r['file'],r['sha256'])
 cap_manifest=read(b/'captures.reviewed.json');rows=cap_manifest['native_sources']
 runtime_path=mapped('captures/expansion/unit-native-20261028/review/capture-runtime-review-20261028.json');runtime=read(runtime_path)
 ui_path=mapped('captures/expansion/unit-native-20261028/review/normal-ui-action-ledger-20261028.json');ui=read(ui_path)
 served_path=mapped('captures/expansion/unit-native-20261028/review/served-stream-ledger-20261028.json');served=read(served_path)
 # Compare original public ledgers with their immutable copies, never private ledgers.
 originals=[]
 for original in ['captures/expansion/unit-native-20261028/review/normal-ui-action-ledger-20261028.json','captures/expansion/unit-native-20261028/review/served-stream-ledger-20261028.json']:
  originals.append(ref(source_file(original,mapping[original]['sha256'])))
 build_path=mapped('production/native-unit/reports/native-build-identity-20261028.json');build=read(build_path)['metadata']
 compare_path=mapped('production/native-unit/reports/native-installed-binary-comparison-20261028.json');comparison=read(compare_path)['metadata']
 prep_path=mapped('production/native-unit/reports/source-preparation.json');prepared=read(prep_path)['metadata']
 context_path=mapped('captures/expansion/unit-native-20261028/review/public-context-inputs-20261028.json');context=read(context_path)
 parent_path=source_file(PARENT_REVIEW,PARENT_SHA);parent=read(parent_path);parent_hashes={r['sha256'] for r in parent['source_images']}
 binary_at=when(comparison['verified_at'])
 macho=sorted(build['mach_o_files'],key=lambda x:x['file'])
 inventory={'schema':'academy.installed-mach-o-digests.v1','bundle_id':build['bundle_id'],'files':macho,'inventory_sha256':native.digest(macho)}
 native.validate_mach_o_inventory(inventory,build['bundle_id'])
 captures=[]
 for row in rows:
  image=source_file(row['file'],row['sha256']);metadata=source_file(row['metadata_file'],row['metadata_sha256']);m=read(metadata);prov=m['provenance'];ax=m['native_accessibility_observation'];guard=ax['result'];at=when(prov['captured_at']);observed=when(ax['at'])
  with image.open('rb') as stream:header=stream.read(24)
  if header[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError('Frozen source is not PNG.')
  dims=struct.unpack('>II',header[16:24]);points=guard['app_frame_points'];dpr=guard['screen_scale']
  matches=[entry for entry in ui['entries'] if isinstance(entry.get('response'),dict) and entry['response'].get('id')==ax.get('id') and entry['response'].get('at')==ax.get('at')]
  geom_changes=[]
  for entry in ui['entries']:
   action=entry.get('request',{}).get('action');time=entry.get('response',{}).get('at')
   if action in {'landscape','portrait','rotate','resize','switch_device','change_window'} and time and observed<when(time)<=at:geom_changes.append(native.digest(entry))
  eligible_streams=[]
  for i,entry in enumerate(served['entries']):
   if entry.get('kind')=='actual_local_metro_response_stream' and entry.get('resource_category') in {'entry_bundle','lazy_chunk','script_segment'} and entry.get('status')==200 and entry.get('completed') is True and entry.get('finished_at') and when(entry['finished_at'])<=at:
    eligible_streams.append({'entry_index':i,'entry_sha256':native.digest(entry),'stream_sha256':entry['stream_sha256'],'original_receipt_sha256':entry['original_receipt_sha256'],'content_type':entry['content_type'],'byte_length':entry['byte_length'],'association':'Possible reviewed capture-context association only; actual client/load/execution identity remains unresolved.'})
  binary_delta=(at-binary_at).total_seconds();age=(at-observed).total_seconds()
  command=prov.get('command',[]);tokens=command if isinstance(command,list) else command.split()
  captures.append({'id':row['id'],'image':ref(image),'native_metadata':ref(metadata),'captured_at':prov['captured_at'],'original_method':prov['method'],'simctl_method_tokens_observed':all(x in tokens for x in ['simctl','io','screenshot']) and prov.get('simulator_udid') in tokens,'capture_exit_code':prov.get('exit_code'),'actual_physical_pixels':{'width':dims[0],'height':dims[1]},'actual_native_points':points,'actual_dpr':dpr,'actual_orientation_code':guard['device_orientation'],'guard_bundle_id':guard['bundle_id'],'guard_native_state':guard['state'],'guard_observed_at':ax['at'],'geometry_and_guard_age_seconds':age,'within_agreed60seconds':0<=age<=60,'geometry_event_entry_digests_between_guard_and_png':geom_changes,'normal_ui_guard_source_matches':len(matches),'normal_ui_guard_source_entry_sha256':native.digest(matches[0]) if len(matches)==1 else None,'actual_binary_verified_at':comparison['verified_at'],'binary_observation_to_capture_seconds':binary_delta,'satisfies_current_prior_binary600seconds':0<=binary_delta<=600,'owner_literal_pixel_observations':{'source':ref(b/'captures.reviewed.json'),'manual_visible_labels':row['manual_visible_labels'],'review_scope':row['review_scope'],'review_note':row['review_note'],'new_bridge_review_not_authored':True},'same_png_in_existing_parent14image_review':row['sha256'] in parent_hashes,'possible_prior_served_measurements':eligible_streams,'new_native_package_emitted':False,'new_passed_review_emitted':False})
 css=[r for r in prepared['prepared_source_files'] if r.get('source_file','').endswith('.css')]
 snapshot_rows=[{'original_path':r['unit_source_file'],'retained_snapshot':ref(mapped(r['file']))} for r in context['source_snapshots']]
 gaps=[{'code':'BINARY_OBSERVATION_CHRONOLOGY','scope':'13 of14 selected images','finding':'Two PNGs precede the actual binary check, one follows it within600seconds, and eleven follow it by more than600seconds. Foreground guard times are separate and cannot replace the actual binary observation timestamp.','requires_parent_decision_or_additional_genuine_evidence':True},
 {'code':'DEDICATED_CREATION_RECEIPT_NOT_IN_FREEZE','finding':'The named public runtime review retains actual dedicated-session fields. The actual own-device creation command/exit receipt is private and not in this immutable freeze. No fresh or backdated receipt is manufactured.','next_step':'Parent may request a separate own-device-only reviewed public addendum; do not copy the broader existing-device inventory.'},
 {'code':'CSS_BODIES_NOT_IN_TWELVE_SOURCE_SNAPSHOTS','finding':'Prepared source inventory lists global.css, theme-tokens.css and global.web.css hashes, but the retained12source snapshots contain noCSSbodies. Revised proposal permits legitimate.csswithunchangedsecretchecks.','next_step':'Decide which styling source bodies are required for the declared native source correspondence; any addendum must retain actual bytes/hashes without rewriting freeze.'},
 {'code':'UNREVIEWED_SCHEMA_NORMALIZATION','finding':'Actual source rows, original action methods, geometry receipts and public source context do not already have the proposal canonical schema. Any future bridge must preserve source-entry hashes and real observations. No new source/pixel/installed review binding has been generated.'}]
 driver=S/'production/native-unit/AcademyUnitDriver.swift'
 return {'kind':'unreviewed_actual_native_schema_bridge_findings','proposal_only':True,'publishable':False,'native_package_created':False,'passed_pixel_source_reviews_created':False,'production_gate_adopted':False,'frozen_source':ref(b/'source-freeze.json'),'frozen_files_rehashed':len(freeze['freeze_files']),'selected_capture_count':len(captures),'existing_parent_source_review':ref(parent_path),'existing_runtime_review':ref(runtime_path),'original_public_ledgers_rehashed':originals,'frozen_normal_ui_ledger':ref(ui_path),'frozen_served_ledger':ref(served_path),'actual_session_from_existing_review':runtime['actual_session'],'reported_installed_macho_inventory_candidate':inventory,'inventory_origin':ref(build_path),'actual_installed_binary_comparison':{'source':ref(compare_path),'verified_at':comparison['verified_at'],'full_bundle_bytes_equal':comparison['build_matches_installed_all_files'],'different_files':comparison['different_files'],'execution_identity_proven':comparison['actual_executed_js_identity_proven']},'reported_source_revision':prepared['revision'],'retained_source_snapshots':snapshot_rows,'prepared_css_hash_records':css,'native_orientation_source':ref(driver) if driver.is_file() else None,'orientation_mapping_scope':'Capture owner identifies XCUIDevice.shared.orientation.rawValue as UIDeviceOrientation; .landscapeLeft is observed raw3. Proposed bridge retains raw code and the public driver source reference, not a guessed timestamp.','captures':captures,'findings':gaps,'next_step':'Parent reviews concrete chronology/schema findings before any source package, new human-review binding or gate adoption. No SDK/private app/dependency paths are public rebuild requirements.'}

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path);args=parser.parse_args();result=findings()
 if args.output:
  p=args.output.resolve()
  if not p.is_relative_to(HERE) or p.exists():raise ValueError('Write only one NEW findings file inside this proposal.')
  p.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'proposal_only':True,'publishable':False,'source_freeze_sha256':result['frozen_source']['sha256'],'frozen_files_rehashed':result['frozen_files_rehashed'],'captures':len(result['captures']),'current_binary600s_satisfied':sum(x['satisfies_current_prior_binary600seconds'] for x in result['captures']),'guard60s_satisfied':sum(x['within_agreed60seconds'] for x in result['captures']),'new_passed_reviews_emitted':False,'findings':[r['code'] for r in result['findings']],'output':args.output.name if args.output else None},indent=2))
if __name__=='__main__':main()
