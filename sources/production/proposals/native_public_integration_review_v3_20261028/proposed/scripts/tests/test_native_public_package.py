"""Synthetic parser fixtures ONLY. No app screenshot, audio or review is genuine."""
import copy
import hashlib
import json
from pathlib import Path
import plistlib
import shutil
import struct
import sys
import tempfile
import unittest
import zlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import native_capture_public as n
from native_capture_review import inspect_private_context, installed_mach_o_inventory, validate_private_context
from verify_capture_evidence import verify_document
import expansion_site as exporter
import render_walkthrough as renderer
import test_walkthrough_render as browser_fixture


def png(w,h):
 def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+b'\x12\x34\x56'*w)*h))+chunk(b'IEND',b'')


class Fixture:
 def __init__(self,root,private):
  self.root=Path(root).resolve();self.private=Path(private).resolve();self.sid='11111111-1111-4111-8111-111111111111';self.udid='22222222-2222-4222-8222-222222222222'
  self.app=self.private/'app';self.source=self.private/'source';self.deps=self.private/'deps'
  for p in [self.root,self.app,self.source,self.deps]:p.mkdir(parents=True,exist_ok=True)
  (self.app/'Unit').write_bytes(b'\xcf\xfa\xed\xfe'+b'synthetic Mach-O fixture only')
  (self.app/'Info.plist').write_bytes(plistlib.dumps({'CFBundleExecutable':'Unit','CFBundleIdentifier':n.BUNDLE,'DTSDKName':'iphonesimulator27.1'}))
  (self.app/'Unit.debug.dylib').write_bytes(b'\xcf\xfa\xed\xfe'+b'synthetic debug native code')
  (self.app/'Frameworks/Native.framework').mkdir(parents=True)
  (self.app/'Frameworks/Native.framework/Native').write_bytes(b'\xca\xfe\xba\xbe'+b'synthetic framework native code')
  self.macho=installed_mach_o_inventory(self.app)
  self.snapshots=[]
  for original,body in [('package.json','{"name":"synthetic-fixture"}'),('ios/Podfile.lock','PODS:\n  - Synthetic (1.0)\n'),('src/app/count.tsx','// synthetic parser fixture, not app source\n')]:
   p=self.source/original;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(body)
   self.snapshots.append({'namespace':'source','original_path':original,'snapshot':self.asset('snapshots/'+original,body.encode())})
  self.manifest={'base_source_revision':'a'*40,'snapshots':self.snapshots}
  self.creation={'id':self.sid,'udid':self.udid,'device_type':'Synthetic iPad fixture','os_version':'27.0','created_at':'2026-10-25T11:50:00Z','method':'new_dedicated_simulator'}
  self.geometry={'session_id':self.sid,'udid':self.udid,'measured_at':'2026-10-25T11:59:59Z','method':'xcuitest_frame_and_uiscreen_scale','orientation':'landscape_left','dpr':2,'screen_points':{'width':1366,'height':1024},'app_viewport_points':{'x':0,'y':0,'width':1366,'height':1024},'pixel_width':2732,'pixel_height':2048}
  self.ui={'session_id':self.sid,'udid':self.udid,'bundle_id':n.BUNDLE,'method':'xcuitest','geometry_events':[],'actions':[{'id':'a1','at':'2026-10-25T11:59:57Z','kind':'tap','control':'Count','observation':'Synthetic parser action only.'},{'id':'a2','at':'2026-10-25T11:59:59Z','kind':'observe_screen','control':'Inventory','observation':'Synthetic parser observation only.'}]}
  self.original_ui={'kind':'synthetic_redacted_normal_ui_ledger','entries':[{'kind':a['kind'],'control':a['control'],'at':a['at']} for a in self.ui['actions']]}
  for a,row in zip(self.ui['actions'],self.original_ui['entries']):a['source_entry_sha256']=n.digest(row)
  self.identity={'reviewer':'Synthetic named reviewer, parser fixture only','reviewed_at':'2026-10-25T12:00:10Z','method':'Synthetic review structure, never actual review.','binding_sha256':'','session_id':self.sid,'udid':self.udid,'foreground_bundle_id':n.BUNDLE,'observation_at':'2026-10-25T11:59:58Z','snapshot_manifest_sha256':'','correspondence_scope':'prior_capture_binary600','recording_session':None,'additional_binary_confirmations':[],'findings':'Synthetic installed context fixture only; no app operation claim.'}
  self.stream={'original_receipt_sha256':'d'*64,'kind':'actual_local_metro_response_stream','started_at':'2026-10-25T11:58:00Z','finished_at':'2026-10-25T11:58:01Z','method':'GET','request_target_sha256':'b'*64,'resource_category':'entry_bundle','status':200,'content_type':'multipart/mixed; boundary="synthetic-fixture"','content_encoding':'identity','hash_stage':'decoded_response_body','stream_sha256':'c'*64,'byte_length':1234,'completed':True,'failure_type':None,'body_saved':False,'body_or_query_logged':False,'source_kind':'real_metro_forwarded_without_content_rewrite','source':'Synthetic local packager context only','client_identity':'not_authenticated_by_transport','executed_or_loaded_identity_proven':False,'coverage_limits':'No authenticated app client or executed identity.'}
  self.ledger={'kind':'actual_served_packager_stream_receipts_not_execution_proof','source_only':True,'native_client_authenticated':False,'loaded_or_executed_identity_proven':False,'lazy_load_set_complete':False,'bodies_urls_queries_headers_frames_retained':False,'known_host_manifest_probe_present':True,'entries':[self.stream]}
  self.runtime_review={'reviewer':'Synthetic named reviewer, parser fixture only','reviewed_at':'2026-10-25T12:00:20Z','method':'Synthetic observed served response metadata review only.','binding_sha256':'','session_id':self.sid,'udid':self.udid,'build_identity_sha256':'','observed_entry_sha256':[],'findings':'Entry-only served bytes; authenticated client, executed graph and lazy coverage unresolved.'}
  self.d={'schema':n.SCHEMA,'app':'Unit','kind':'application_screenshot','session':{k:v for k,v in self.creation.items() if k!='method'},
   'build':{'mode':'development_metro','base_source_revision':'a'*40,'bundle_id':n.BUNDLE,'native_sdk':'iphonesimulator27.1','installed_binary_sha256':n.sha(self.app/'Unit'),'installed_info_plist_sha256':n.sha(self.app/'Info.plist')},
   'capture':{'image':self.asset('raw/native.png',png(2732,2048)),'width':2732,'height':2048,'captured_at':'2026-10-25T12:00:00Z','method':'ios_simulator_screenshot','session_id':self.sid,'udid':self.udid,'foreground_bundle_id':n.BUNDLE,'simctl_method':'xcrun_simctl_io_explicit_udid_screenshot_png'},
   'runtime':{'coverage':'served_response_metadata_only','transport_client_identity':'not_authenticated_by_transport','loaded_or_executed_identity':'unresolved','complete_lazy_execution_graph':'unresolved','lazy':True},
   'observations':{'visible_labels':['Inventory','Count','Completed'],'required_labels':['Count','Inventory']},'limitations':dict(n.LIMITS)}
  self.seal()
 def asset(self,name,body):
  p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(body);return {'file':name,'sha256':hashlib.sha256(body).hexdigest()}
 def json(self,name,d):return self.asset(name,json.dumps(d,sort_keys=True).encode())
 def seal(self):
  d=self.d;d['session']['creation_receipt']=self.json('receipts/creation.json',self.creation)
  d['session']['creation_source']=self.json('receipts/original-creation.json',{'session_id':self.sid,'udid':self.udid,'created_at':self.creation['created_at'],'device_type':self.creation['device_type'],'os_version':self.creation['os_version'],'creation_exit_code':0,'other_devices_included':False,'dedicated':True,'user_session_reused':False,'creation_command':['xcrun','simctl','create','Synthetic own device']})
  b=d['build'];b['installed_mach_o_inventory']=self.json('receipts/macho.json',{'schema':'academy.installed-mach-o-digests.v1','bundle_id':n.BUNDLE,'files':self.macho,'inventory_sha256':n.digest(self.macho)});b['snapshot_manifest']=self.json('receipts/sources.json',self.manifest)
  self.identity['snapshot_manifest_sha256']=b['snapshot_manifest']['sha256'];self.identity['binding_sha256']=n.installed_review_digest(b,self.identity);b['installed_correspondence']=self.json('receipts/installed.json',self.identity)
  d['capture']['display']=self.json('receipts/geometry.json',self.geometry);self.ui['source_ledger']=self.json('receipts/original-ui.json',self.original_ui);d['normal_ui']=self.json('receipts/ui.json',self.ui)
  d['runtime']['served_ledger']=self.json('receipts/served-ledger.json',self.ledger)
  d['runtime']['selected_streams']=[{'entry_index':0,'entry_sha256':n.digest(self.stream),'association_method':'reviewed_capture_context_only_not_authenticated','build_identity_sha256':n.build_digest(b)}]
  self.runtime_review['observed_entry_sha256']=[n.digest(self.stream)]
  self.runtime_review['binding_sha256']=n.digest({k:v for k,v in d['runtime'].items() if k!='review_receipt'});self.runtime_review['build_identity_sha256']=n.build_digest(b)
  d['runtime']['review_receipt']=self.json('receipts/runtime-review.json',self.runtime_review)
  d['review']={'reviewer':'Synthetic named reviewer, parser fixture only','reviewed_at':getattr(self,'pixel_review_at','2026-10-25T12:00:30Z'),'method':'Synthetic test receipt, never actual pixel review.','binding_sha256':n.review_digest(d),'checks':{k:True for k in n.REVIEW_CHECKS},'findings':'Synthetic parser fixture only. No genuine pixel or UI review performed.'}
  self.ref=self.json('receipts/package.json',d)
  cap=d['capture'];self.row={'id':'native-count','app':'Unit','kind':'application_screenshot','file':cap['image']['file'],'sha256':cap['image']['sha256'],'width':2732,'height':2048,'provenance':{'method':cap['method'],'captured_at':cap['captured_at']},**d['observations'],'native_review_package':self.ref}
 def report(self):return n.validate_native_source(self.row,self.root,'Unit')
 def evidence(self):
  video={**self.asset('video/master.mp4',b'synthetic identity only, not media'),'duration_seconds':30,'width':1920,'height':1080,'assembled_at':'2026-10-25T12:01:00Z'}
  caption='Select Count to review Inventory.';video['captions']=self.asset('video/master.vtt',('WEBVTT\n\n00:00.000 --> 00:30.000\n'+caption+'\n').encode())
  frame={**self.asset('proof/frame.png',png(1920,1080)),'width':1920,'height':1080,'time':15,'video_sha256':video['sha256'],'application_visible':True,'visible_labels':['Inventory','Count'],'caption_text':caption,'native_binding':self.report()['native_binding']}
  frame['native_frame_review']={'reviewer':'Synthetic named reviewer, parser fixture only','reviewed_at':'2026-10-25T12:02:00Z','method':'Synthetic frame review test only.','binding_sha256':n.digest({'frame_sha256':frame['sha256'],'video_sha256':video['sha256'],'source_binding_sha256':n.digest(frame['native_binding']),'visible_labels':frame['visible_labels'],'caption_text':caption}),'checks':{k:True for k in ['application_visible','raw_full_viewport_visible','controls_legible','caption_text_verified','no_blocking_error','no_private_values_visible']},'findings':'Synthetic test only, never real encoded review.'}
  proofs=[]
  for pos,t in [('beginning',2),('middle',15),('end',28)]:
   proofs.append({'position':pos,'video_sha256':video['sha256'],'url':'http://localhost:8000/master/','current_src':'http://localhost:8000/master.mp4','captured_at':'2026-10-25T12:03:00Z','previous_time':t-.5,'current_time':t,'duration_seconds':30,'video_width':1920,'video_height':1080,'ready_state':4,'network_state':1,'paused':False,'ended':False,'media_error':None,'console_errors':[],'captions':{'mode':'showing','text':caption},'screenshot':{**self.asset('proof/'+pos+'.png',png(1280,720)),'width':1280,'height':720}})
  return {'schema_version':1,'lesson_id':'synthetic-native-count','primary_app':'Unit','video':video,'screenshots':[self.row],'scenes':[{'id':'count','kind':'operational','start':0,'end':30,'screens':[{'screenshot_id':'native-count','start':0,'end':30}],'captions':[{'start':0,'end':30,'text':caption,'screenshot_id':'native-count','required_labels':['Inventory','Count']}]}],'rendered_segments':[{'scene_id':'count','screenshot_id':'native-count','start':0,'end':30,'frame':frame}],'browser_playback':proofs}


class NativePublicProposalTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.base=Path(self.tmp.name);self.f=Fixture(self.base/'public',self.base/'private')
 def reject(self,word):
  with self.assertRaisesRegex((ValueError,OSError),word):self.f.report()
 def test_public_offline_package_valid_without_any_private_build_or_dependencies(self):
  shutil.rmtree(self.f.private);r=self.f.report();self.assertTrue(r['source_review_validated']);self.assertFalse(r['publishable']);self.assertFalse(r['executed_identity_proven']);self.assertTrue(all(p.is_relative_to(self.f.root) for p in r['dependencies']))
 def test_private_context_checks_actual_binary_plist_source_and_locks(self):
  r=validate_private_context(self.f.d,self.f.root,self.f.app,self.f.source,self.f.deps);self.assertTrue(r['private_context_matches_review_candidate']);self.assertFalse(r['review_flags_generated']);self.assertEqual(len(r['installed_mach_o_files']),3);json.dumps(r)
  (self.f.app/'Unit').write_bytes(b'\xcf\xfa\xed\xfechanged')
  with self.assertRaisesRegex(ValueError,'installed binary/plist changed'):validate_private_context(self.f.d,self.f.root,self.f.app,self.f.source,self.f.deps)
 def test_changed_debug_dylib_rejected_with_launcher_and_plist_unchanged(self):
  (self.f.app/'Unit.debug.dylib').write_bytes(b'\xcf\xfa\xed\xfechanged-debug-code')
  with self.assertRaisesRegex(ValueError,'Mach-O inventory differs'):inspect_private_context(self.f.d,self.f.root,self.f.app,self.f.source,self.f.deps)
 def test_added_and_missing_native_code_files_rejected(self):
  p=self.f.app/'Frameworks/Native.framework/Native';original=p.read_bytes();p.unlink()
  with self.assertRaisesRegex(ValueError,'Mach-O inventory differs'):inspect_private_context(self.f.d,self.f.root,self.f.app,self.f.source,self.f.deps)
  p.write_bytes(original);(self.f.app/'Added.debug.dylib').write_bytes(b'\xcf\xfa\xed\xfenew-code')
  with self.assertRaisesRegex(ValueError,'Mach-O inventory differs'):inspect_private_context(self.f.d,self.f.root,self.f.app,self.f.source,self.f.deps)
 def test_public_macho_inventory_digest_and_sorted_paths_bound(self):
  self.f.macho.reverse();self.f.seal();self.reject('sorted, unique')
 def test_legitimate_css_source_snapshot_keeps_secret_checks(self):
  p=self.f.source/'src/theme-tokens.css';p.write_text(':root { --space: 4px; }')
  self.f.snapshots.append({'namespace':'source','original_path':'src/theme-tokens.css','snapshot':self.f.asset('snapshots/src/theme-tokens.css',p.read_bytes())});self.f.seal();self.assertTrue(self.f.report()['source_review_validated'])
 def test_css_has_no_private_key_body_exemption(self):
  body=b':root { --fixture: "s'+b'k.'+b'B'*24+b'"; }'
  self.f.snapshots.append({'namespace':'source','original_path':'src/theme-tokens.css','snapshot':self.f.asset('snapshots/src/theme-tokens.css',body)});self.f.seal();self.reject('key/token/private-key body')
 def test_hashing_does_not_use_python311_file_digest(self):
  from unittest.mock import patch
  with patch.object(hashlib,'file_digest',side_effect=AssertionError('Python3.10 unavailable API'),create=True):self.assertTrue(self.f.report()['source_review_validated'])
 def test_private_preflight_of_unreviewed_draft_does_not_generate_approval(self):
  draft=copy.deepcopy(self.f.d);draft.pop('review');r=inspect_private_context(draft,self.f.root,self.f.app,self.f.source,self.f.deps);self.assertTrue(r['private_context_matches_review_candidate']);self.assertTrue(r['review_still_required']);self.assertFalse(r['publishable'])
  with self.assertRaises(ValueError):n.validate_public_package(draft,self.f.root)
 def recording_fixture(self,binary_after_capture=False):
  f=self.f;first='2026-10-25T11:59:30Z';last='2026-10-25T12:00:00Z';f.identity['reviewed_at']='2026-10-25T12:00:40Z';f.pixel_review_at='2026-10-25T12:00:50Z'
  if binary_after_capture:first='2026-10-25T12:00:00Z';last='2026-10-25T12:00:30Z';f.identity['observation_at']='2026-10-25T12:00:10Z'
  f.capture_members={'native_sources':[{'id':'first','file':f.d['capture']['image']['file'],'sha256':f.d['capture']['image']['sha256'],'captured_at':first},{'id':'last','file':f.d['capture']['image']['file'],'sha256':f.d['capture']['image']['sha256'],'captured_at':last}]}
  f.identity['correspondence_scope']='reviewed_recording_session'
  f.identity['reviewed_at']='2026-10-25T12:01:10Z';f.pixel_review_at='2026-10-25T12:01:20Z'
  f.instrumentation={'kind':'honest_native_capture_session_test_driver_event_context','recorded_at':'2026-10-25T12:00:40Z','capture_interval':{'first':first,'last':last},'events':[],'managed_product_source_or_native_code_modified_in_interval':False,'literal_no_build_or_install_attestation_satisfied':False,'target_app_reinstall_events_not_independently_observed':True,'same_target_reinstall_possible_during_xcode_test_startup':True}
  driver=f.asset('receipts/latest-driver.swift',b'// synthetic postcapture driver only')
  f.product_context={'observed_at':'2026-10-25T12:00:40Z','managed_source_files_compared':3,'differences':[],'difference_scope':'Synthetic unchanged product source fixture.','exact_historical_build09_build10_driver_source_snapshots_retained':False,'historical_driver_source_hashes_not_reconstructed_or_invented':True,'latest_retained_count_driver_source':{'public_file':driver['file'],'sha256':driver['sha256'],'compiled_as_build_ios_11_after_final_capture':True}}
  f.initial={'metadata':{'verified_at':f.identity['observation_at'],'bundle_id':n.BUNDLE,'simulator_udid':f.udid,'different_files':[]}}
  f.fresh={'observed_at':'2026-10-25T12:01:00Z','bundle_id':n.BUNDLE,'simulator_udid':f.udid,'mach_o_files':[dict(row,observed_sha256=row['sha256'],observed_bytes=row['bytes']) for row in f.macho]}
  f.identity['recording_session']={'started_at':first,'ended_at':last,'capture_manifest':f.json('receipts/session-captures.json',f.capture_members),'same_device_udid':f.udid,'bundle_id':n.BUNDLE,'base_source_revision':f.d['build']['base_source_revision'],'installed_mach_o_inventory_sha256':f.d['build']['installed_mach_o_inventory']['sha256'],'full_normal_ui_ledger_sha256':f.ui['source_ledger']['sha256'],'product_managed_native_source_unchanged':True,'product_binary_observations':[f.json('receipts/initial-product.json',f.initial),f.json('receipts/fresh-product.json',f.fresh)],'instrumentation_event_ledger':f.json('receipts/instrumentation.json',f.instrumentation),'product_source_context':f.json('receipts/product-context.json',f.product_context),'installation_continuity_claimed':False,'continuous_execution_identity_proven':False};f.seal();return f

 def test_reviewed_recording_session_preserves_signed_actual_binary_offsets(self):
  f=self.recording_fixture();r=f.report();self.assertEqual(r['native_binding']['installed_correspondence_offsets']['binary_observation_to_capture_seconds'],2)
  f=self.recording_fixture(True);r=f.report();self.assertEqual(r['native_binding']['installed_correspondence_offsets']['binary_observation_to_capture_seconds'],-10)
 def test_recording_session_over_onehour_rejected(self):
  f=self.recording_fixture();f.identity['recording_session']['started_at']='2026-10-25T10:00:00Z';f.seal();self.reject('at most1hour')
 def test_recording_session_wrong_device_rejected(self):
  f=self.recording_fixture();f.identity['recording_session']['same_device_udid']='44444444-4444-4444-8444-444444444444';f.seal();self.reject('device/source/bundle/Mach-O')
 def test_recording_session_cannot_omit_actual_binary_check_or_capture(self):
  f=self.recording_fixture();f.identity['observation_at']='2026-10-25T11:59:00Z';f.seal();self.reject('inside recording session')
 def test_recording_session_must_use_actual_first_last_manifest_bounds(self):
  f=self.recording_fixture();f.identity['recording_session']['started_at']='2026-10-25T11:59:31Z';f.instrumentation['capture_interval']['first']='2026-10-25T11:59:31Z';f.identity['recording_session']['instrumentation_event_ledger']=f.json('receipts/instrumentation.json',f.instrumentation);f.seal();self.reject('actual first/last')
 def test_recording_session_requires_explicit_named_nochange_review(self):
  f=self.recording_fixture();f.identity['recording_session']['product_managed_native_source_unchanged']=False;f.seal();self.reject('product managed/native source unchanged')
 def test_recorded_install_change_rejected_even_if_context_claims_no_change(self):
  f=self.recording_fixture();f.original_ui['entries'].append({'request':{'action':'install_app'},'response':{'at':'2026-10-25T11:59:45Z'}});f.seal();f.identity['recording_session']['full_normal_ui_ledger_sha256']=f.ui['source_ledger']['sha256'];f.seal();self.reject('undeclared or product-changing')
 def test_recording_session_full_ledger_hash_required(self):
  f=self.recording_fixture();f.identity['recording_session']['full_normal_ui_ledger_sha256']='0'*64;f.seal();self.reject('FULL normal UI ledger')
 def test_declared_instrumentation_only_build_keeps_explicit_reinstall_limits(self):
  f=self.recording_fixture();f.instrumentation['events']=[{'name':'synthetic-testdriver','started_at':'2026-10-25T11:59:40Z','finished_at':'2026-10-25T11:59:50Z','command_category':['xcodebuild','build-for-testing'],'private_command_receipt_sha256':'a'*64,'sanitized_log_sha256':'b'*64}];f.identity['recording_session']['instrumentation_event_ledger']=f.json('receipts/instrumentation.json',f.instrumentation);f.seal();r=f.report();self.assertFalse(r['native_binding']['installed_correspondence_offsets']['installation_continuity_claimed'])
 def test_changed_product_hash_rejected_despite_context_review(self):
  f=self.recording_fixture();f.fresh['mach_o_files'][0]['observed_sha256']='0'*64;f.identity['recording_session']['product_binary_observations'][1]=f.json('receipts/fresh-product.json',f.fresh);f.seal();self.reject('changed/missing/added actual product')
 def test_changed_managed_product_source_rejected(self):
  f=self.recording_fixture();f.product_context['differences']=[{'source_file':'src/app/count.tsx','prepared_sha256':'a'*64,'observed_sha256':'b'*64}];f.identity['recording_session']['product_source_context']=f.json('receipts/product-context.json',f.product_context);f.seal();self.reject('changed/unknown product managed source')
 def test_private_source_mismatch_does_not_change_public_snapshot_identity(self):
  (self.f.source/'src/app/count.tsx').write_text('changed')
  with self.assertRaisesRegex(ValueError,'actual source/lock/module differs'):validate_private_context(self.f.d,self.f.root,self.f.app,self.f.source,self.f.deps)
  self.assertTrue(self.f.report()['source_review_validated'])
 def test_true_dpr2_full_fit_records_both_units_without_cropping(self):
  fit=self.f.report()['layout'];self.assertLess(fit['raw_pixel_scale'],.75);self.assertEqual(fit['output_pixels_per_logical_point'],fit['raw_pixel_scale']*2);self.assertGreaterEqual(fit['output_pixels_per_logical_point'],.75);self.assertFalse(fit['cropped']);self.assertGreaterEqual(fit['width'],1100);self.assertGreaterEqual(fit['height'],650)
 def test_wrong_dpr_even_resealed_rejected(self):
  self.f.geometry['dpr']=1;self.f.seal();self.reject('DPR/logical/raw')
 def test_wrong_measured_pixel_dimension_even_resealed_rejected(self):
  self.f.geometry['pixel_width']=2700;self.f.seal();self.reject('wrong device/raw pixels')
 def test_portrait_is_not_rotated_or_relabelled(self):
  self.f.geometry['orientation']='portrait';self.f.seal();self.reject('landscape')
 def test_small_logical_viewport_and_partial_app_window_rejected(self):
  self.f.geometry['app_viewport_points']['width']=900;self.f.seal();self.reject('landscape geometry|full-viewport|too small')
 def test_wrong_method_rejected(self):
  self.f.d['capture']['method']='browser_screenshot';self.f.seal();self.reject('native provenance')
 def test_source_cannot_relabel_native_as_browser(self):
  self.f.row['provenance']['method']='browser_screenshot';self.reject('native provenance')
 def test_unknown_build_branch_rejected_even_new_review(self):
  self.f.d['build']['mode']='release_unreviewed';self.f.seal();self.reject('unknown build')
 def test_missing_real_binary_digest_rejected(self):
  self.f.d['build']['installed_binary_sha256']='';self.f.seal();self.reject('actual digest')
 def test_stale_installed_source_review_digest_rejected(self):
  self.f.d['build']['base_source_revision']='b'*40;self.f.d['review']['binding_sha256']=n.review_digest(self.f.d);self.f.ref=self.f.json('receipts/package.json',self.f.d);self.f.row['native_review_package']=self.f.ref;self.reject('stale source snapshot revision')
 def test_review_digest_not_arbitrary_passed_flag(self):
  self.f.d['review']['binding_sha256']='0'*64;self.f.ref=self.f.json('receipts/package.json',self.f.d);self.f.row['native_review_package']=self.f.ref;self.reject('binding digest differs')
 def test_extra_self_approval_fields_rejected(self):
  for field in ['publishable','passed','native_approved','native_roots','publication_ready','export_ready']:
   with self.subTest(field=field):
    row=copy.deepcopy(self.f.row);row[field]=True
    with self.assertRaisesRegex(ValueError,'self-approve'):n.validate_native_source(row,self.f.root,'Unit')
 def test_missing_specific_pixel_review_check_rejected(self):
  self.f.d['review']['checks']['controls_legible']=False;self.f.ref=self.f.json('receipts/package.json',self.f.d);self.f.row['native_review_package']=self.f.ref;self.reject('explicit full-viewport')
 def test_changed_raw_png_hash_rejected(self):
  (self.f.root/'raw/native.png').write_bytes(png(2048,2732));self.reject('hash differs')
 def test_png_crc_tamper_rejected_even_with_new_ref(self):
  p=self.f.root/'raw/native.png';data=bytearray(p.read_bytes());data[-15]^=1;self.f.d['capture']['image']=self.f.asset('raw/native.png',bytes(data));self.f.seal();self.reject('CRC')
 def test_missing_public_source_asset_rejected(self):
  (self.f.root/'snapshots/src/app/count.tsx').unlink();self.reject('asset missing/unreadable')
 def test_source_snapshot_symlink_escape_rejected(self):
  p=self.f.root/'snapshots/src/app/count.tsx';p.unlink();p.symlink_to(self.f.source/'src/app/count.tsx');self.reject('symlink escape')
 def test_no_raw_key_bearing_runtime_body_retained(self):
  self.f.stream['body_saved']=True;self.f.seal();self.reject('body retention')
 def test_unknown_extra_stream_body_field_rejected(self):
  self.f.stream['body']='synthetic payload';self.f.seal();self.reject('body/header/URL/query/frame')
 def test_source_snapshot_key_pattern_rejected_without_printing_value(self):
  self.f.snapshots[2]['snapshot']=self.f.asset('snapshots/src/app/count.tsx',b'const fixture = "p'+b'k.'+b'A'*24+b'";');self.f.seal();self.reject('key/token/private-key body')
 def test_missing_stream_hash_rejected(self):
  self.f.stream['stream_sha256']='';self.f.seal();self.reject('stream hash missing')
 def test_served_entry_only_is_truthful_and_never_complete_execution(self):
  self.assertEqual(len(self.f.d['runtime']['selected_streams']),1);self.assertTrue(self.f.report()['source_review_validated']);self.assertFalse(self.f.report()['executed_identity_proven'])
  self.f.d['runtime']['complete_lazy_execution_graph']='complete';self.f.seal();self.reject('authenticated load/execution assertion')
 def test_fabricated_authenticated_execution_claim_rejected(self):
  self.f.stream['executed_or_loaded_identity_proven']=True;self.f.seal();self.reject('invented execution proof')
 def test_stale_geometry_and_installed_observation_rejected(self):
  self.f.geometry['measured_at']='2026-10-25T11:58:59Z';self.f.seal();self.reject('60s bound')
 def test_actual_geometry_age_is_retained_under_explicit60s_bound(self):
  self.f.geometry['measured_at']='2026-10-25T11:59:09Z';self.f.seal();r=self.f.report();self.assertEqual(r['layout']['geometry_observation_age_seconds'],51)
 def test_intervening_rotate_or_device_switch_cannot_keep_old_geometry(self):
  for kind in ['rotate','switch_device','resize','change_window']:
   event={'at':'2026-10-25T11:59:59.500Z','kind':kind,'udid':self.f.udid};self.f.original_ui['entries'].append(dict(event));event['source_entry_sha256']=n.digest(event);self.f.ui['geometry_events']=[event];self.f.seal();self.reject('intervening geometry/device')
 def test_guard_age_is_preserved_and_over60s_rejected(self):
  self.f.ui['actions'][-1]['at']='2026-10-25T11:59:09Z';self.f.ui['actions'][0]['at']='2026-10-25T11:59:08Z';self.f.seal();self.assertEqual(self.f.report()['layout']['normal_ui_guard_age_seconds'],51)
  self.f.ui['actions'][-1]['at']='2026-10-25T11:58:59Z';self.f.ui['actions'][0]['at']='2026-10-25T11:58:58Z';self.f.seal();self.reject('guard exceeds explicit60s')
 def test_omitting_intervening_geometry_event_from_review_subset_still_fails(self):
  self.f.original_ui['entries'].append({'request':{'action':'landscape'},'response':{'at':'2026-10-25T11:59:59.500Z'}});self.f.ui['geometry_events']=[];self.f.seal();self.reject('retained original ledger')
 def test_pixel_review_cannot_predate_bound_component_reviews(self):
  self.f.d['review']['reviewed_at']='2026-10-25T12:00:15Z';self.f.row['native_review_package']=self.f.json('receipts/package.json',self.f.d);self.reject('predates reviewed observations')
 def test_hidden_state_write_not_normal_ui(self):
  self.f.ui['actions'][0]['kind']='api_write';self.f.seal();self.reject('not normal UI')
 def test_foreground_other_app_rejected(self):
  self.f.d['capture']['foreground_bundle_id']='other.app';self.f.seal();self.reject('foreground identity')
 def test_literal_labels_are_hash_bound_no_dom_or_icons(self):
  self.f.row['visible_labels'].append('Invented');self.reject('labels differ')
 def test_full_synthetic_evidence_offline_and_later_frame_review_required(self):
  e=self.f.evidence();shutil.rmtree(self.f.private);self.assertTrue(verify_document(e,self.f.root)['passed'])
  e['rendered_segments'][0]['frame']['native_frame_review']=None;self.assertFalse(verify_document(e,self.f.root)['passed'])
 def test_native_frame_hash_caption_geometry_or_labels_changes_fail(self):
  original=self.f.evidence()
  for key,value in [('native_binding',{}),('caption_text','Changed'),('visible_labels',['Invented'])]:
   e=copy.deepcopy(original);e['rendered_segments'][0]['frame'][key]=value;self.assertFalse(verify_document(e,self.f.root)['passed'])
 def test_browser_playback_and_authoring_digest_still_required_offline(self):
  e=self.f.evidence();e['browser_playback']=[];self.assertFalse(verify_document(e,self.f.root)['passed'])
 def test_public_screenshot_branch_accepts_true_native_without_roots(self):
  e=self.f.evidence();shutil.rmtree(self.f.private);self.assertEqual(exporter._screenshots(e,self.f.root,'Unit')['native-count']['provenance']['method'],'ios_simulator_screenshot')
 def test_native_source_primary_other_app_cannot_supply_controls(self):
  with self.assertRaisesRegex(ValueError,'Unit primary identity'):n.validate_native_source(self.f.row,self.f.root,'IC')
 def native_lesson(self,e):
  lesson={'id':'synthetic-native-count','title':'Synthetic native parser fixture','app':'Unit','audience':['Synthetic reviewer'],'summary':'Synthetic public parser fixture only.','prerequisites':['No app or physical outcome is represented.'],'scenes':[{'id':'count','title':'Synthetic Count','narration':'Select Count to review Inventory.','practice':'Synthetic parser exercise only.','required_labels':['Count','Inventory']}],'sector_examples':[{'sector':x,'scenario':'Synthetic '+x+' parser fixture only.'} for x in exporter.SECTORS],'publication_mode':'video','export_ready':True,'evidence_file':'evidence.json'}
  e['authoring_sha256']=exporter.lesson_content_digest(lesson);self.f.json('evidence.json',e);return lesson
 def test_public_prepare_passes_offline_without_sdk_binary_or_npm(self):
  e=self.f.evidence();lesson=self.native_lesson(e);shutil.rmtree(self.f.private)
  public=exporter._prepare(lesson,self.f.root);self.assertEqual(public['mode'],'video')
 def test_offline_site_exports_unchanged_png_and_portable_native_video_links(self):
  e=self.f.evidence();lesson=self.native_lesson(e);folder=self.f.root/'expansion/lessons';folder.mkdir(parents=True);(folder/'synthetic-native-count.json').write_text(json.dumps(lesson));shutil.rmtree(self.f.private)
  out=self.base/'export';cards=exporter.write_expansion_site(out,self.f.root);self.assertEqual(len(cards),1)
  images=list(out.rglob('*.png'));self.assertTrue(images);self.assertTrue(any(n.sha(p)==self.f.row['sha256'] for p in images))
  page=(out/'walkthroughs/synthetic-native-count/index.html').read_text();self.assertNotIn('localhost',page);self.assertNotIn('file://',page);self.assertNotIn('/Users/',page)
 def test_public_canonical_digest_still_rejects_changed_learner_content(self):
  e=self.f.evidence();lesson=self.native_lesson(e);lesson['scenes'][0]['practice']='Changed current learner practice.'
  with self.assertRaisesRegex(exporter.PublicationError,'authoring|current|content'):
   exporter._prepare(lesson,self.f.root)
 def test_dom_icon_metadata_cannot_be_promoted_to_native_labels(self):
  for field,value in [('dom_file','fake.txt'),('visible_controls',[{'accessible_name':'Count'}]),('visible_field_text',['Count'])]:
   row=copy.deepcopy(self.f.row);row[field]=value
   with self.assertRaisesRegex(ValueError,'browser|DOM|literal'):n.validate_native_source(row,self.f.root,'Unit')
 def test_stream_stale_review_context_is_rejected(self):
  self.f.d['runtime']['selected_streams'][0]['build_identity_sha256']='0'*64;self.f.d['review']['binding_sha256']=n.review_digest(self.f.d);self.f.row['native_review_package']=self.f.json('receipts/package.json',self.f.d);self.reject('context stale/wrong')
 def test_review_timestamp_before_source_observation_is_rejected(self):
  self.f.d['review']['reviewed_at']='2026-10-25T11:59:00Z';self.f.ref=self.f.json('receipts/package.json',self.f.d);self.f.row['native_review_package']=self.f.ref;self.reject('predates reviewed observations')
 def test_renderer_synthetic_input_only_is_dpr_aware_and_creates_no_review(self):
  factory=browser_fixture.WalkthroughContractTests(methodName='runTest');factory.setUp();self.addCleanup(factory.doCleanups)
  f=Fixture(factory.root,self.base/'renderer-private');factory.capture=dict(f.row,id='draft-screen');factory.lesson['app']='Unit';factory.lesson['scenes'][0]['required_labels']=['Inventory','Count'];factory.lesson['scenes'][0]['narration']='Select Count to review Inventory.'
  (factory.root/'voice.srt').write_text('1\n00:00:00,000 --> 00:00:01,000\nSelect Count to review Inventory.\n\n');factory.plan['captions']['sha256']=renderer._hash(factory.root/'voice.srt');factory.plan['captions']['approval']['sha256']=factory.plan['captions']['sha256'];factory.plan['scenes'][0]['captions'][0]['required_labels']=['Inventory','Count'];factory.plan['screenshot_reviews']['draft-screen']=factory.approval(factory.capture['sha256'],application_visible=True,labels_legible=True,no_errors=True);factory.plan['screenshot_reviews']['draft-screen']['reviewed_at']='2026-10-25T12:00:40Z'
  factory.save();shutil.rmtree(f.private);recipe=renderer.validate_inputs(factory.lesson_path,factory.plan_path,factory.root);shot=recipe['screenshots']['draft-screen'];self.assertLess(shot['layout']['scale'],.75);self.assertIn('native_binding',shot);self.assertNotIn('native_frame_review',shot)
if __name__=='__main__':unittest.main()
