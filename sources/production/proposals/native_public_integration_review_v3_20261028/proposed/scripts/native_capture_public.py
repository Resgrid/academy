"""UNADOPTED PROPOSAL: self-contained reviewed Unit native-source package.

No SDK, installed app, npm, key, development bundle, browser, network or private
root is used here. Rehashes public PNG/receipts/source snapshots and measures
DPR-aware geometry. It checks named review bindings; it cannot authenticate
pixels, a reviewer, transport clients, lazy loads or executed JavaScript.
Source validation is not video/publication approval. Historical v1/v2 unchanged.
"""
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import struct
import uuid
import zlib

SCHEMA = 'academy.reviewed-native-public-package.proposal.v3'
BUNDLE = 'com.resgrid.unit.development'
HEX = re.compile(r'[0-9a-f]{64}\Z')
REV = re.compile(r'[0-9a-f]{40}\Z')
LIMITS = {
 'review_is_not_cryptographic_pixel_authentication': True,
 'transport_client_identity': 'not_authenticated_by_transport',
 'loaded_or_executed_identity': 'unresolved',
 'complete_lazy_execution_graph': 'unresolved',
 'real_hardware_or_gps_success_claimed': False,
}
REVIEW_CHECKS = ('application_visible','full_viewport_unmodified','no_blocking_error',
 'literal_labels_reviewed','controls_legible','normal_ui_correspondence_reviewed',
 'foreground_and_installed_source_correspondence_reviewed','no_private_values_visible','no_intervening_geometry_or_device_change')
SOURCE_EXTENSIONS = {'.json','.lock','.css','.ts','.tsx','.js','.jsx','.m','.mm','.h','.swift','.patch','.md','.yml','.yaml','.pbxproj','.plist'}
SECRET = re.compile(rb'(?:\b(?:pk|sk)\.[A-Za-z0-9_-]{12,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{10,}\.)')
FORBIDDEN_SOURCE = re.compile(r'(?:^|/)(?:\.env[^/]*|private|node_modules|\.git)(?:/|$)|\.(?:bundle|hbc|map|ipa|dylib|a|so)\Z',re.I)
UI_METHODS = {'human_simulator_ui','xcuitest','maestro','appium_xcuitest'}
UI_ACTIONS = {'tap','scroll','select','type_text','sensitive_typing_redacted','observe_screen','wait_for_visible','permission_denied'}


def digest(value):
 return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def unique_json(text):
 def pairs(items):
  result={}
  for k,v in items:
   if k in result: raise ValueError('duplicate JSON key')
   result[k]=v
  return result
 return json.loads(text,object_pairs_hook=pairs,parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def build_digest(build):
 return digest({k:v for k,v in build.items() if k!='installed_correspondence'})


def review_digest(package):
 return digest({k:v for k,v in package.items() if k!='review'})


def need(ok,message):
 if not ok: raise ValueError('native public package: '+message)


def obj(value,keys,field):
 need(isinstance(value,dict) and set(value)==set(keys.split()),field+' requires exact declared fields; self-approval/URL/private-root/body additions are forbidden')
 return value


def text(value,field):
 need(isinstance(value,str) and value.strip() and len(value)<=4000,field+' must contain specific nonempty text')
 need(not re.search(r'(?i)(?:https?://|file://|/Users/|/private/|access_token=|api_key=|password=)',value),field+' must not expose a private URL/path/credential')
 return value


def when(value,field,now):
 text(value,field)
 try: at=datetime.fromisoformat(value.replace('Z','+00:00'))
 except ValueError as e:raise ValueError(field+' requires ISO timestamp') from e
 need(at.tzinfo is not None and at<=now,field+' must have timezone and not be future')
 return at


def sha(path):
 result=hashlib.sha256()
 with path.open('rb') as stream:
  for block in iter(lambda:stream.read(1024*1024),b''):result.update(block)
 return result.hexdigest()


def identifier(value,field):
 try:need(isinstance(value,str) and str(uuid.UUID(value)).lower()==value.lower(),field+' requires explicit UUID')
 except (ValueError,AttributeError) as e:raise ValueError(field+' requires explicit UUID') from e


def validate_mach_o_inventory(inventory,bundle_id):
 obj(inventory,'schema bundle_id files inventory_sha256','Mach-O digest inventory')
 need(inventory['schema']=='academy.installed-mach-o-digests.v1' and inventory['bundle_id']==bundle_id,'Mach-O inventory app identity differs')
 rows=inventory['files'];need(isinstance(rows,list) and rows,'complete installed Mach-O digest inventory required')
 names=[]
 for row in rows:
  obj(row,'file sha256 bytes','Mach-O inventory row');name=text(row['file'],'Mach-O relative file')
  need(not PurePosixPath(name).is_absolute() and '\\' not in name and all(x not in ('','.','..') for x in name.split('/')),'Mach-O file path must be app-relative')
  need(isinstance(row['sha256'],str) and HEX.fullmatch(row['sha256']) and type(row['bytes']) is int and row['bytes']>=4,'actual Mach-O digest/size missing')
  names.append(name)
 need(names==sorted(set(names)) and inventory['inventory_sha256']==digest(rows),'Mach-O inventory must be sorted, unique and hash-bound')
 return rows


def installed_review_digest(build,identity):
 fields=('session_id','udid','foreground_bundle_id','observation_at','snapshot_manifest_sha256','correspondence_scope','recording_session','additional_binary_confirmations')
 return digest({'build_identity_sha256':build_digest(build),**{k:identity.get(k) for k in fields}})


class PublicCheck:
 def __init__(self,root,now=None):
  self.root=Path(root).resolve();self.now=now or datetime.now(timezone.utc);self.dependencies=[]
 def asset(self,ref,field,kind='json'):
  obj(ref,'file sha256',field);name=text(ref['file'],field+'.file')
  need(not PurePosixPath(name).is_absolute() and '\\' not in name and all(x not in ('','.','..') for x in name.split('/')),field+' must be confined relative POSIX path')
  need(not FORBIDDEN_SOURCE.search(name),field+' cannot retain private/npm/binary/development-bundle assets')
  p=(self.root/name).resolve()
  need(p.is_relative_to(self.root) and p.is_file(),field+' asset missing/unreadable or symlink escape')
  need(isinstance(ref['sha256'],str) and HEX.fullmatch(ref['sha256']) and sha(p)==ref['sha256'],field+' hash differs')
  need(p.stat().st_size<=128*1024*1024,field+' unexpectedly large')
  self.dependencies.append(p)
  if kind!='png':
   data=p.read_bytes();need(not SECRET.search(data),field+' appears to retain a key/token/private-key body')
   need(not data.startswith((b'\xcf\xfa\xed\xfe',b'\xca\xfe\xba\xbe',b'\xfe\xed\xfa\xcf')),field+' cannot retain an executable')
   try:decoded=data.decode('utf-8')
   except UnicodeError as e:raise ValueError(field+' must be nonsecret source or JSON text, never binary/runtime body') from e
   if kind=='json':return unique_json(decoded)
   need(p.suffix in SOURCE_EXTENSIONS or p.name in {'Podfile','Podfile.lock','yarn.lock'},field+' is not an allowed public source snapshot')
  return p
 def png(self,path):
  data=path.read_bytes();need(data[:8]==b'\x89PNG\r\n\x1a\n','raw native screenshot must be unchanged PNG')
  pos=8;types=[];size=None
  while pos<len(data):
   need(pos+12<=len(data),'truncated PNG chunk');n=struct.unpack('>I',data[pos:pos+4])[0];kind=data[pos+4:pos+8];end=pos+12+n
   need(end<=len(data),'truncated PNG payload');body=data[pos+8:pos+8+n];crc=struct.unpack('>I',data[pos+8+n:end])[0]
   need(zlib.crc32(kind+body)&0xffffffff==crc,'PNG CRC differs')
   if kind==b'IHDR':need(not types and n==13,'invalid PNG header');size=struct.unpack('>II',body[:8])
   types.append(kind);pos=end
   if kind==b'IEND':need(n==0 and end==len(data),'PNG has trailing or invalid end bytes');break
  need(size and b'IDAT' in types and types[-1]==b'IEND' and types.count(b'IHDR')==1,'PNG incomplete')
  need(all(320<=v<=16384 for v in size),'native PNG dimensions unsuitable')
  return size
 def named_review(self,r,keys,field,earliest,binding):
  obj(r,keys,field);text(r['reviewer'],field+'.reviewer')
  need(r['reviewer'].casefold() not in {'unknown','automatic','none','test','passed'},field+' must name actual reviewer')
  need(when(r['reviewed_at'],field+'.reviewed_at',self.now)>=earliest,field+' predates reviewed observations')
  need(r['binding_sha256']==binding,field+' binding digest differs')
  text(r['method'],field+'.method')

 def validate(self,d):
  obj(d,'schema app kind session build capture normal_ui runtime observations limitations review','package')
  need(d['schema']==SCHEMA and d['app']=='Unit' and d['kind']=='application_screenshot','explicit Unit native application identity required')
  need(d['limitations']==LIMITS,'honest pixel/transport/execution/hardware limitations required')
  session=obj(d['session'],'id udid device_type os_version created_at creation_receipt creation_source','session')
  identifier(session['id'],'session.id');identifier(session['udid'],'session.udid')
  created=when(session['created_at'],'session.created_at',self.now);text(session['device_type'],'device_type');text(session['os_version'],'os_version')
  receipt=self.asset(session['creation_receipt'],'session.creation_receipt')
  need(receipt=={k:session[k] for k in ('id','udid','device_type','os_version','created_at')}|{'method':'new_dedicated_simulator'},'dedicated device creation receipt differs')
  original_creation=self.asset(session['creation_source'],'own-device-only actual creation source')
  need(isinstance(original_creation,dict) and all(original_creation.get(k)==session[k] for k in ['udid','created_at','device_type','os_version']) and original_creation.get('session_id')==session['id'],'own creation source identity/time differs')
  need(original_creation.get('creation_exit_code')==0 and original_creation.get('other_devices_included') is False and original_creation.get('user_session_reused') is False and original_creation.get('dedicated') is True,'actual dedicated own-device creation evidence required')
  command=original_creation.get('creation_command');need(isinstance(command,list) and len(command)>=3 and command[:3]==['xcrun','simctl','create'],'retain actual own-device creation method without other-device inventory')
  b=obj(d['build'],'mode base_source_revision bundle_id native_sdk installed_binary_sha256 installed_info_plist_sha256 installed_mach_o_inventory snapshot_manifest installed_correspondence','build')
  need(b['mode']=='development_metro' and b['bundle_id']==BUNDLE,'unknown build mode/bundle; only reviewed Unit development_metro branch proposed')
  need(isinstance(b['base_source_revision'],str) and REV.fullmatch(b['base_source_revision']),'source Git revision missing')
  need(isinstance(b['native_sdk'],str) and re.fullmatch(r'iphonesimulator\d+\.\d+',b['native_sdk']),'native SDK identity missing')
  for k in ('installed_binary_sha256','installed_info_plist_sha256'):need(isinstance(b[k],str) and HEX.fullmatch(b[k]),k+' requires actual digest, no binary retained')
  mach_o_files=validate_mach_o_inventory(self.asset(b['installed_mach_o_inventory'],'complete installed Mach-O inventory'),b['bundle_id'])
  manifest=self.asset(b['snapshot_manifest'],'build.snapshot_manifest')
  obj(manifest,'base_source_revision snapshots','source manifest');need(manifest['base_source_revision']==b['base_source_revision'],'stale source snapshot revision')
  need(isinstance(manifest['snapshots'],list) and len(manifest['snapshots'])>=3,'source, app package and Pod lock snapshots required')
  names=set()
  for row in manifest['snapshots']:
   obj(row,'namespace original_path snapshot','source snapshot')
   need(row['namespace'] in {'source','dependencies'},'source namespace unsupported');name=text(row['original_path'],'source original_path')
   need(not PurePosixPath(name).is_absolute() and '\\' not in name and all(x not in ('','.','..') for x in name.split('/')),'source path must be relative')
   need(not FORBIDDEN_SOURCE.search(name) and (row['namespace'],name) not in names,'private source path or duplicate snapshot')
   names.add((row['namespace'],name));self.asset(row['snapshot'],'public source snapshot','source')
  need({('source','package.json'),('source','ios/Podfile.lock')}<=names and any(n.startswith('src/') for ns,n in names if ns=='source'),'app package, Pod lock and actual app screen source snapshots required')
  identity=self.asset(b['installed_correspondence'],'build.installed_correspondence')
  self.named_review(identity,'reviewer reviewed_at method binding_sha256 session_id udid foreground_bundle_id observation_at snapshot_manifest_sha256 correspondence_scope recording_session additional_binary_confirmations findings','installed correspondence',created,installed_review_digest(b,identity))
  need(identity['session_id']==session['id'] and identity['udid']==session['udid'] and identity['foreground_bundle_id']==BUNDLE and identity['snapshot_manifest_sha256']==b['snapshot_manifest']['sha256'],'installed correspondence wrong device/app/source')
  observed=when(identity['observation_at'],'installed correspondence observation',self.now)
  need(created<=observed<=when(identity['reviewed_at'],'installed correspondence review',self.now),'installed correspondence chronology differs');text(identity['findings'],'installed correspondence findings')
  cap=obj(d['capture'],'image width height captured_at method session_id udid foreground_bundle_id simctl_method display','capture')
  at=when(cap['captured_at'],'capture.captured_at',self.now)
  need(cap['method']=='ios_simulator_screenshot' and cap['simctl_method']=='xcrun_simctl_io_explicit_udid_screenshot_png','actual explicit-device simctl screenshot method required')
  need(cap['session_id']==session['id'] and cap['udid']==session['udid'] and cap['foreground_bundle_id']==BUNDLE,'capture session/foreground identity differs')
  correspondence_offsets={'binary_observation_to_capture_seconds':(at-observed).total_seconds()}
  mode=identity['correspondence_scope']
  need(isinstance(identity['additional_binary_confirmations'],list),'additional actual binary confirmations must be explicit references')
  for reference in identity['additional_binary_confirmations']:self.asset(reference,'separate actual binary confirmation')
  recording=identity['recording_session']
  if mode=='prior_capture_binary600':
   need(recording is None and observed<=at and (at-observed).total_seconds()<=600,'installed correspondence prior binary observation exceeds600s or follows capture')
  else:
   need(mode=='reviewed_recording_session','unknown installed correspondence scope')
   obj(recording,'started_at ended_at capture_manifest same_device_udid bundle_id base_source_revision installed_mach_o_inventory_sha256 full_normal_ui_ledger_sha256 product_managed_native_source_unchanged product_binary_observations instrumentation_event_ledger product_source_context installation_continuity_claimed continuous_execution_identity_proven','reviewed recording session')
   start=when(recording['started_at'],'recording session start',self.now);end=when(recording['ended_at'],'recording session end',self.now)
   need(start<=end and (end-start).total_seconds()<=3600,'recording session must be bounded to at most1hour')
   need(start<=at<=end and start<=observed<=end,'capture and actual binary comparison must lie inside recording session')
   need(when(identity['reviewed_at'],'context review time',self.now)>=end,'context review must cover the completed recording session')
   need(recording['same_device_udid']==session['udid'] and recording['bundle_id']==b['bundle_id'] and recording['base_source_revision']==b['base_source_revision'] and recording['installed_mach_o_inventory_sha256']==b['installed_mach_o_inventory']['sha256'],'recording session device/source/bundle/Mach-O identity differs')
   need(recording['product_managed_native_source_unchanged'] is True,'named context review must confirm product managed/native source unchanged')
   need(recording['installation_continuity_claimed'] is False and recording['continuous_execution_identity_proven'] is False,'recording review must not claim uninterrupted installation or continuous execution')
   events=self.asset(recording['instrumentation_event_ledger'],'actual instrumentation event/source review')
   need(isinstance(events,dict) and events.get('kind')=='honest_native_capture_session_test_driver_event_context' and events.get('capture_interval')=={'first':recording['started_at'],'last':recording['ended_at']},'instrumentation review must retain actual recording interval')
   need(events.get('managed_product_source_or_native_code_modified_in_interval') is False and events.get('literal_no_build_or_install_attestation_satisfied') is False and events.get('target_app_reinstall_events_not_independently_observed') is True and events.get('same_target_reinstall_possible_during_xcode_test_startup') is True,'declare instrumentation-only changes and possible identical-target reinstall honestly')
   need(isinstance(events.get('events'),list),'actual instrumentation events required')
   declared_events=set()
   for event in events['events']:
    need(isinstance(event,dict) and event.get('command_category') in [['xcodebuild','build-for-testing'],['xcodebuild','test-without-building']],'unknown/product-changing instrumentation event')
    event_start=when(event.get('started_at'),'testdriver event start',self.now);event_end=when(event.get('finished_at'),'testdriver event end',self.now)
    need(event_start<=event_end and all(isinstance(event.get(k),str) and HEX.fullmatch(event[k]) for k in ['private_command_receipt_sha256','sanitized_log_sha256']),'event times or retained command/log hashes missing')
    declared_events.add((event_start,event_end,tuple(event['command_category'])))
   product_context=self.asset(recording['product_source_context'],'actual managed product/driver source review')
   need(isinstance(product_context,dict) and product_context.get('managed_source_files_compared',0)>0,'actual managed-source comparison required')
   need(product_context.get('exact_historical_build09_build10_driver_source_snapshots_retained') is False and product_context.get('historical_driver_source_hashes_not_reconstructed_or_invented') is True,'missing historical driver digests must remain explicit; never reconstruct them')
   latest=product_context.get('latest_retained_count_driver_source')
   need(isinstance(latest,dict) and latest.get('compiled_as_build_ios_11_after_final_capture') is True,'retain actual postcapture latest driver scope')
   self.asset({'file':latest.get('public_file'),'sha256':latest.get('sha256')},'retained latest instrumentation source','source')
   differences=product_context.get('differences');need(isinstance(differences,list),'managed-source differences must be explicit')
   need(all(isinstance(row,dict) and row.get('source_file')=='app.config.ts' and all(isinstance(row.get(k),str) and HEX.fullmatch(row[k]) for k in ['prepared_sha256','observed_sha256']) for row in differences),'changed/unknown product managed source rejected')
   text(product_context.get('difference_scope'),'reviewed app.config Android-only exception')
   expected={row['file']:(row['sha256'],row['bytes']) for row in mach_o_files};observation_times=[]
   need(isinstance(recording['product_binary_observations'],list) and len(recording['product_binary_observations'])>=2,'both actual product-code comparisons required')
   for reference in recording['product_binary_observations']:
    raw=self.asset(reference,'actual product-code comparison');record=raw.get('metadata',raw) if isinstance(raw,dict) else {}
    if 'verified_at' in record:
     compared=when(record['verified_at'],'actual initial binary comparison',self.now)
     need(record.get('bundle_id')==b['bundle_id'] and record.get('simulator_udid')==session['udid'],'initial product comparison wrong device/app')
     need(isinstance(record.get('different_files'),list) and not set(record['different_files'])&set(expected) and set(record['different_files'])<={'EXConstants.bundle/app.config'},'actual initial product native code differs')
    else:
     compared=when(record.get('observed_at'),'actual fresh binary confirmation',self.now)
     need(record.get('bundle_id')==b['bundle_id'] and record.get('simulator_udid')==session['udid'],'fresh product comparison wrong device/app')
     measured=record.get('mach_o_files');need(isinstance(measured,list),'fresh actual Mach-O rows missing')
     actual={row.get('file'):(row.get('observed_sha256'),row.get('observed_bytes')) for row in measured if isinstance(row,dict)}
     need(actual==expected and len(measured)==len(expected),'changed/missing/added actual product native code')
    observation_times.append(compared)
   need(observed in observation_times and any(t>=end for t in observation_times),'preserve initial actual binary observation and separate post-recording confirmation')
   need(when(identity['reviewed_at'],'context review time',self.now)>=max(observation_times+[when(events.get('recorded_at'),'event review time',self.now),when(product_context.get('observed_at'),'product source review time',self.now)]),'context review predates actual event/source/binary confirmations')
   correspondence_offsets.update(installation_continuity_claimed=False,continuous_execution_identity_proven=False,historical_build09_build10_driver_digests_retained=False,instrumentation_events_declared=len(events['events']))
   captures=self.asset(recording['capture_manifest'],'recording session original capture manifest')
   need(isinstance(captures,dict) and isinstance(captures.get('native_sources'),list) and captures['native_sources'],'recording session must retain original native capture bounds')
   times=[when(row.get('captured_at'),'recording member captured_at',self.now) for row in captures['native_sources']]
   need(start==min(times) and end==max(times),'recording session bounds differ from actual first/last capture timestamps')
   need(any(row.get('file')==cap['image']['file'] and row.get('sha256')==cap['image']['sha256'] and row.get('captured_at')==cap['captured_at'] for row in captures['native_sources']),'current PNG is absent from reviewed recording session manifest')
   correspondence_offsets.update(recording_session_duration_seconds=(end-start).total_seconds(),recording_start_to_binary_observation_seconds=(observed-start).total_seconds(),binary_observation_to_recording_end_seconds=(end-observed).total_seconds(),recording_start_to_capture_seconds=(at-start).total_seconds(),capture_to_recording_end_seconds=(end-at).total_seconds())
  need(type(cap['width']) is int and type(cap['height']) is int,'raw physical dimensions must be integer pixels')
  image=self.asset(cap['image'],'capture.image','png');need(self.png(image)==(cap['width'],cap['height']),'actual PNG dimensions disagree')
  display=self.asset(cap['display'],'capture.display')
  obj(display,'session_id udid measured_at method orientation dpr screen_points app_viewport_points pixel_width pixel_height','display')
  need(display['session_id']==session['id'] and display['udid']==session['udid'] and (display['pixel_width'],display['pixel_height'])==(cap['width'],cap['height']),'geometry has wrong device/raw pixels')
  need(display['method'] in {'xcuitest_frame_and_uiscreen_scale','native_screen_window_geometry_review'},'actual native geometry measurement required')
  measured=when(display['measured_at'],'geometry measured_at',self.now)
  geometry_age=(at-measured).total_seconds()
  need(created<=measured<=at and geometry_age<=60,'native geometry observation exceeds explicit60s bound')
  need(display['orientation'] in {'landscape_left','landscape_right'},'measured native landscape required; do not rotate portrait')
  dpr=display['dpr'];need(type(dpr) in (int,float) and math.isfinite(dpr) and dpr in (1,2,3),'native measured DPR invalid')
  sp=obj(display['screen_points'],'width height','screen_points');vp=obj(display['app_viewport_points'],'x y width height','app_viewport_points')
  for x in list(sp.values())+list(vp.values()):need(type(x) in (int,float) and math.isfinite(x) and x>=0,'point geometry invalid')
  need(sp['width']>sp['height']>0 and vp['width']>vp['height']>0,'landscape geometry axes disagree')
  need(sp['width']*dpr==cap['width'] and sp['height']*dpr==cap['height'],'DPR/logical/raw pixel dimensions disagree')
  need(vp=={'x':0,'y':0,'width':sp['width'],'height':sp['height']},'full-viewport app screenshot required; no partial/multiwindow fit')
  need(vp['width']>=960 and vp['height']>=540,'logical UI viewport too small')
  ui=self.asset(d['normal_ui'],'normal_ui')
  obj(ui,'session_id udid bundle_id method source_ledger actions geometry_events','normal UI ledger')
  original_ui=self.asset(ui['source_ledger'],'original redacted normal UI ledger')
  need(isinstance(original_ui,dict) and isinstance(original_ui.get('entries'),list) and original_ui['entries'],'retained original normal UI ledger entries required')
  original_action_hashes={digest(x) for x in original_ui['entries']}
  if mode=='reviewed_recording_session':
   need(recording['full_normal_ui_ledger_sha256']==ui['source_ledger']['sha256'],'recording session must bind the original FULL normal UI ledger')
   forbidden_changes={'install','install_app','uninstall','uninstall_app','rebuild','build','build-for-testing','test-without-building','change_source','source_edit','change_native_code'}
   for original in original_ui['entries']:
    if not isinstance(original,dict):continue
    request=original.get('request',{});request=request if isinstance(request,dict) else {}
    action=request.get('action',original.get('kind'));response=original.get('response',{});response=response if isinstance(response,dict) else {}
    if isinstance(action,str) and action.casefold() in forbidden_changes:
     changed=when(response.get('at',original.get('at')),'recorded install/source/build change',self.now)
     if start<=changed<=end:
      need(action.casefold() in {'build-for-testing','test-without-building'} and any(a<=changed<=z for a,z,category in declared_events),'undeclared or product-changing event exists in full recording ledger')
  geometry_actions={'landscape','portrait','rotate','set_orientation','setorientation','resize','switch_device','select_device','change_window'}
  for original in original_ui['entries']:
   if not isinstance(original,dict):continue
   request=original.get('request',{});request=request if isinstance(request,dict) else {}
   action=request.get('action',original.get('kind'))
   if isinstance(action,str) and action.casefold() in geometry_actions:
    response=original.get('response',{});response=response if isinstance(response,dict) else {}
    event_time=when(response.get('at',original.get('at')),'original geometry/device event time',self.now)
    need(not measured<event_time<=at,'intervening geometry/device action exists in retained original ledger')
  need(ui['session_id']==session['id'] and ui['udid']==session['udid'] and ui['bundle_id']==BUNDLE and ui['method'] in UI_METHODS,'wrong native normal-UI ledger identity/method')
  need(isinstance(ui['actions'],list) and ui['actions'],'nonempty normal-UI action ledger required')
  prior=created
  for a in ui['actions']:
   obj(a,'id at kind control observation source_entry_sha256','normal UI action');need(a['source_entry_sha256'] in original_action_hashes,'normal UI action lacks retained source entry binding');text(a['id'],'action id');text(a['control'],'control');text(a['observation'],'observation')
   need(a['kind'] in UI_ACTIONS,'hidden write/launch hook/automatic permission grant is not normal UI')
   t=when(a['at'],'action time',self.now);need(prior<=t<=at,'normal UI chronology differs');prior=t
  guard_age=(at-prior).total_seconds()
  need(ui['actions'][-1]['kind']=='observe_screen' and guard_age<=60,'normal-UI capture guard exceeds explicit60s bound')
  need(isinstance(ui['geometry_events'],list),'retained geometry/device event observations required')
  for event in ui['geometry_events']:
   obj(event,'at kind udid source_entry_sha256','geometry/device event')
   need(event['kind'] in {'rotate','resize','switch_device','change_window'} and event['source_entry_sha256'] in original_action_hashes,'geometry/device event lacks actual source binding')
   identifier(event['udid'],'geometry event device')
   event_at=when(event['at'],'geometry event time',self.now)
   need(not measured<event_at<=at,'intervening geometry/device switch invalidates measured geometry')
  runtime=obj(d['runtime'],'coverage transport_client_identity loaded_or_executed_identity complete_lazy_execution_graph lazy served_ledger selected_streams review_receipt','runtime')
  need(runtime['coverage']=='served_response_metadata_only' and runtime['transport_client_identity']=='not_authenticated_by_transport' and runtime['loaded_or_executed_identity']=='unresolved' and runtime['complete_lazy_execution_graph']=='unresolved' and type(runtime['lazy']) is bool,'served bytes must not become an authenticated load/execution assertion')
  ledger=self.asset(runtime['served_ledger'],'original retained served metadata ledger')
  obj(ledger,'kind source_only native_client_authenticated loaded_or_executed_identity_proven lazy_load_set_complete bodies_urls_queries_headers_frames_retained known_host_manifest_probe_present entries','served ledger')
  need(ledger['kind']=='actual_served_packager_stream_receipts_not_execution_proof' and ledger['source_only'] is True and ledger['native_client_authenticated'] is False and ledger['loaded_or_executed_identity_proven'] is False and ledger['lazy_load_set_complete'] is False and ledger['bodies_urls_queries_headers_frames_retained'] is False and type(ledger['known_host_manifest_probe_present']) is bool,'retain original served metadata limits; no claimed app client/execution/bundle body')
  def no_payload(value):
   if isinstance(value,dict):
    need(not {str(k).casefold() for k in value}&{'body','raw_body','payload','headers','url','query','frames','bundle','data','raw_bundle','access_token','token','password'},'runtime ledger must not retain key-bearing body/header/URL/query/frame payloads')
    for child in value.values():no_payload(child)
   elif isinstance(value,list):
    for child in value:no_payload(child)
  no_payload(ledger)
  need(isinstance(ledger['entries'],list) and ledger['entries'],'original served ledger must retain its observations')
  need(isinstance(runtime['selected_streams'],list) and runtime['selected_streams'],'actual served response observations required')
  ids=[]
  for association in runtime['selected_streams']:
   obj(association,'entry_index entry_sha256 association_method build_identity_sha256','served measurement review association')
   i=association['entry_index'];need(type(i) is int and 0<=i<len(ledger['entries']),'served observation index invalid')
   r=ledger['entries'][i]
   need(association['entry_sha256']==digest(r) and association['entry_sha256'] not in ids,'selected original served observation changed/duplicated');ids.append(association['entry_sha256'])
   need(association['association_method']=='reviewed_capture_context_only_not_authenticated' and association['build_identity_sha256']==build_digest(b),'served observation review context stale/wrong; no authenticated device linkage')
   need(isinstance(r,dict) and r.get('kind')=='actual_local_metro_response_stream' and r.get('method')=='GET' and r.get('resource_category') in {'entry_bundle','lazy_chunk','script_segment'},'selected observation is not an actual served script response')
   need(r.get('hash_stage')=='decoded_response_body' and r.get('source_kind')=='real_metro_forwarded_without_content_rewrite','unknown response measurement stage/source')
   need(all(isinstance(r.get(k),str) and HEX.fullmatch(r[k]) for k in ['stream_sha256','request_target_sha256','original_receipt_sha256']),'stream hash missing')
   need(type(r.get('byte_length')) is int and 0<r['byte_length']<=256*1024*1024 and type(r.get('status')) is int and r['status']==200 and r.get('completed') is True,'incomplete/empty/failed served response')
   need(r.get('body_saved') is False and r.get('body_or_query_logged') is False and r.get('client_identity')=='not_authenticated_by_transport' and r.get('executed_or_loaded_identity_proven') is False,'key-bearing body retention or invented execution proof forbidden')
   content=text(r.get('content_type'),'actual HTTP response content_type')
   need(content.split(';',1)[0].strip() in {'multipart/mixed','application/javascript','text/javascript','application/octet-stream'},'unknown HTTP served response content type')
   need(r.get('content_encoding') in {'identity','gzip','deflate','br'},'unknown measured response encoding')
   start=when(r.get('started_at'),'stream started',self.now);end=when(r.get('finished_at'),'stream finished',self.now);need(created<=start<=end<=at,'stream chronology outside session/capture')
  rr=self.asset(runtime['review_receipt'],'runtime.review_receipt')
  runtime_binding=digest({k:v for k,v in runtime.items() if k!='review_receipt'})
  self.named_review(rr,'reviewer reviewed_at method binding_sha256 session_id udid build_identity_sha256 observed_entry_sha256 findings','served-byte review',at,runtime_binding)
  need(rr['session_id']==session['id'] and rr['udid']==session['udid'] and rr['build_identity_sha256']==build_digest(b) and rr['observed_entry_sha256']==ids,'runtime review scope/identity differs')
  text(rr['findings'],'runtime review findings')
  obs=obj(d['observations'],'visible_labels required_labels','observations')
  for k in obs:
   need(isinstance(obs[k],list) and obs[k] and len(obs[k])==len(set(obs[k])),'literal label observations must be nonempty unique lists')
   for label in obs[k]:text(label,'literal label')
  need(set(obs['required_labels'])<=set(obs['visible_labels']),'required native label is not observed')
  review=d['review'];self.named_review(review,'reviewer reviewed_at method binding_sha256 checks findings','native pixel/source review',max(at,when(identity['reviewed_at'],'installed review time',self.now),when(rr['reviewed_at'],'runtime review time',self.now)),review_digest(d))
  need(set(review['checks'])==set(REVIEW_CHECKS) and all(review['checks'][k] is True for k in REVIEW_CHECKS),'explicit full-viewport/source/normal-UI/privacy review findings required')
  text(review['findings'],'pixel/source review findings')
  scale=min(1920/cap['width'],912/cap['height']);logical=scale*dpr
  width=round(cap['width']*scale);height=round(cap['height']*scale)
  need(.75<=logical<=2 and width>=1100 and height>=650,'DPR-aware fitted logical UI is too small/large to read')
  fit={'x':(1920-width)//2,'y':48+(912-height)//2,'width':width,'height':height,'scale':scale,'raw_pixel_scale':scale,'output_pixels_per_logical_point':logical,'measured_native_dpr':dpr,'geometry_observation_age_seconds':geometry_age,'normal_ui_guard_age_seconds':guard_age,'cropped':False}
  binding={'package_digest':review_digest(d),'review_digest':digest(review),'source_png_sha256':cap['image']['sha256'],'source_identity_sha256':build_digest(b),'geometry_sha256':cap['display']['sha256'],'normal_ui_sha256':d['normal_ui']['sha256'],'installed_correspondence_scope':mode,'installed_correspondence_offsets':correspondence_offsets,'runtime_review_sha256':runtime['review_receipt']['sha256'],'layout':fit}
  return {'source_review_validated':True,'proposal_only':True,'publishable':False,'pixel_authenticity_proven':False,'executed_identity_proven':False,'layout':fit,'native_binding':binding,'dependencies':list(dict.fromkeys(self.dependencies)),'limitations':LIMITS}


def validate_public_package(package,asset_root,now=None):
 """Read-only source package check. No trusted private roots or cached pass flags."""
 return PublicCheck(asset_root,now).validate(package)


def validate_native_source(row,asset_root,primary_app):
 need(primary_app=='Unit' and row.get('app')=='Unit','native source must have explicit Unit primary identity')
 need(not {'url','dom_file','dom_sha256','publishable','native_context','native_roots','native_approved','passed','publication_ready','export_ready','integration_approved','source_review_validated','valid_traceability'}&set(row),'native cannot self-approve or be relabeled as browser')
 need(row.get('kind')=='application_screenshot' and row.get('visible_controls',[])==[] and row.get('visible_field_text',[])==[],'literal native labels only; DOM/icon names unsupported')
 provenance=obj(row.get('provenance'),'method captured_at','native provenance');need(provenance['method']=='ios_simulator_screenshot','true native provenance method required')
 check=PublicCheck(asset_root);package=check.asset(row.get('native_review_package'),'native review package');result=check.validate(package)
 cap=package['capture'];obs=package['observations']
 need(row.get('file')==cap['image']['file'] and row.get('sha256')==cap['image']['sha256'] and (row.get('width'),row.get('height'))==(cap['width'],cap['height']) and provenance['captured_at']==cap['captured_at'],'screenshot row differs from reviewed native PNG/capture')
 need(row.get('visible_labels')==obs['visible_labels'] and row.get('required_labels')==obs['required_labels'],'literal native labels differ from bound review package')
 result['native_binding']['package_file_sha256']=row['native_review_package']['sha256']
 result['dependencies']=list(dict.fromkeys(check.dependencies))
 return result


def verify_native_frame(frame,video_hash,source_report,assembled_at):
 """Validate a separately recorded real rendered-frame review; never generate one."""
 expected=source_report['native_binding'];need(frame.get('native_binding')==expected,'native frame lost source/geometry/review binding')
 need(frame.get('reviewed_control_names',[])==[],'native icon accessible names unsupported')
 r=frame.get('native_frame_review');obj(r,'reviewer reviewed_at method binding_sha256 checks findings','native encoded-frame review')
 binding=digest({'frame_sha256':frame.get('sha256'),'video_sha256':video_hash,'source_binding_sha256':digest(expected),'visible_labels':frame.get('visible_labels'),'caption_text':frame.get('caption_text')})
 check=PublicCheck('.');check.named_review(r,'reviewer reviewed_at method binding_sha256 checks findings','native encoded-frame review',when(assembled_at,'assembled_at',check.now),binding)
 checks={'application_visible','raw_full_viewport_visible','controls_legible','caption_text_verified','no_blocking_error','no_private_values_visible'}
 need(set(r['checks'])==checks and all(r['checks'][k] is True for k in checks),'actual native full-frame/caption/control/privacy review incomplete')
 text(r['findings'],'frame review findings')
