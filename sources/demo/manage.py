#!/usr/bin/env python3
"""Manage this named, isolated Academy stack. No global Docker changes or deletion."""
from settings import load
import argparse, datetime, json, os, pathlib, re, shutil, subprocess, sys, time, urllib.request
ROOT=pathlib.Path(__file__).resolve().parent
PROFILE=load(); STACK=PROFILE['name']; WEB_PORT=PROFILE['ports']['web']
core_pointer=ROOT/'private/core-path.json'
core_default=json.loads(core_pointer.read_text())['path'] if core_pointer.exists() else str(ROOT/'checkout')
REPO=pathlib.Path(os.environ.get('RESGRID_CORE_PATH', core_default)).resolve()
DOCKER=shutil.which('docker')
if not DOCKER: raise SystemExit('Docker must be installed and available on PATH.')
SERVICES=['postgres','redis','rabbit','mail','billing','web','api','eventing','worker','loopback','gateway']
APPS=['billing','web','api','eventing','worker','loopback','gateway']
PROJECTS={'web':'Web/Resgrid.Web/Resgrid.Web.csproj','console':'Tools/Resgrid.Console/Resgrid.Console.csproj','api':'Web/Resgrid.Web.Services/Resgrid.Web.Services.csproj','eventing':'Web/Resgrid.Web.Eventing/Resgrid.Web.Eventing.csproj','worker':'Workers/Resgrid.Workers.Console/Resgrid.Workers.Console.csproj'}
def run(args,**kw):
 return subprocess.run(args,check=True,text=True,**kw)
def docker(*args,**kw): return run([DOCKER,*args],**kw)
def compose(*args,**kw): return docker('compose','--project-name',STACK,'--env-file',str(ROOT/'.env'),'-f',str(ROOT/'compose.yaml'),*args,**kw)
def start(names):
 env=dict(os.environ); env['PATH']=str(pathlib.Path(DOCKER).parent)+os.pathsep+env.get('PATH','')
 run([sys.executable,str(ROOT/'start_containers.py'),*names],env=env)
def sql(query,db='resgrid_academy'):
 return docker('exec','-i',STACK+'-postgres-1','psql','-v','ON_ERROR_STOP=1','-U','academy','-d',db,'-At',input=query,capture_output=True).stdout.strip()
def prepare():
 run([sys.executable,str(ROOT/'prepare.py')]);run([sys.executable,str(ROOT/'prepare_tls.py')])
def health():
 states={}
 for service in SERVICES:
  raw=docker('inspect',f'{STACK}-{service}-1','--format','{{json .State}}',capture_output=True).stdout
  s=json.loads(raw); states[service]={'running':s['Running'],'started_at':s['StartedAt'],'health':s.get('Health',{}).get('Status')}
 endpoints={}
 for name,path in [('web','/'),('api','/api/v4/Health/GetCurrent'),('eventing','/academy-eventing-health/GetCurrent')]:
  try:
   with urllib.request.urlopen('http://127.0.0.1:'+str(WEB_PORT)+path,timeout=15) as response:
    item={'status':response.status}
    if name!='web':item['body']=json.loads(response.read())
    endpoints[name]=item
  except Exception as e:endpoints[name]={'error':str(e)}
 query='''SELECT json_build_object(
 'department',(SELECT name FROM departments WHERE departmentid=51),
 'members',(SELECT count(*) FROM departmentmembers WHERE departmentid=51 AND isdeleted=false),
 'units',(SELECT count(*) FROM units WHERE departmentid=51),
 'active_calls',(SELECT count(*) FROM calls WHERE departmentid=51 AND state=0 AND isdeleted=false),
 'closed_calls',(SELECT count(*) FROM calls WHERE departmentid=51 AND state=1 AND isdeleted=false),
 'trainings',(SELECT count(*) FROM trainings WHERE departmentid=51),
 'calendar_events',(SELECT count(*) FROM calendaritems WHERE departmentid=51 AND isv2schedule=true),
 'deployments',(SELECT count(*) FROM deployments WHERE departmentid=51 AND isdeleted=false),
 'record_drafts',(SELECT count(*) FROM rmsoperationalrecords WHERE departmentid=51 AND finalizedon IS NULL),
 'submitted_checklists',(SELECT count(*) FROM checklistcompletions WHERE departmentid=51 AND submittedon IS NOT NULL),
 'inventory_imports',(SELECT count(*) FROM inventoryoperations WHERE departmentid=51 AND requestid='00000000-0000-0000-0000-000000000001' AND state=2),
 'migration_version',(SELECT max("Version") FROM "VersionInfo"));'''
 fixtures=json.loads(sql(query))
 internal=docker('network','inspect',STACK+'_training','--format','{{.Internal}}',capture_output=True).stdout.strip()=='true'
 recent={}
 observation_since=max(states[s]['started_at'] for s in ['web','api','eventing','worker','loopback'])
 for service in ['web','api','eventing','worker']:
  p=subprocess.run([DOCKER,'logs','--since',observation_since,f'{STACK}-{service}-1'],capture_output=True,text=True,check=True)
  recent[service]=len(re.findall(r'(?im)^.*(?:fail:|Unhandled exception|Error creating queue|Exception occurred)',p.stdout+p.stderr))
 report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'services':states,'endpoints':endpoints,'fixtures':fixtures,'application_network_internal':internal,'recent_error_lines':recent,'recent_log_observation_since':observation_since,
 'limits':['Web authentication verified separately through the browser.','Eventing health backend booleans are hardcoded false in this checkout; HTTP 200 verifies endpoint liveness.','Mobile OIDC on local HTTP, outbound notifications, PTT, ADP, NERIS submission, finance transactions, and external integrations are not verified.','Feature overrides and billing entitlements are isolated training fixtures; no production release guarantee.']}
 report['passed']=all(x['running'] for x in states.values()) and all(x.get('status')==200 for x in endpoints.values()) and internal and fixtures['members']==14 and fixtures['units']==6
 (ROOT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:report[k] for k in ['passed','fixtures','application_network_internal','recent_error_lines']},indent=2))
 if not report['passed']:raise SystemExit('Stack health checks failed; see validation.json.')
def stage():
 for v in ['web-publish','console-publish','config','gateway-config']:
  docker('volume','create',STACK+'_'+v,capture_output=True)
 name=STACK+'-asset-stage'
 existing=subprocess.run([DOCKER,'inspect',name],capture_output=True).returncode==0
 if not existing:
  docker('create','--name',name,'--network',STACK+'_training','-v',STACK+'_web-publish:/mnt/web','-v',STACK+'_console-publish:/mnt/console','-v',STACK+'_config:/mnt/config','-v',STACK+'_gateway-config:/mnt/nginx','redis:7-alpine','sleep','3600',capture_output=True)
 start([name])
 docker('cp',str(ROOT/'publish/web')+'/.',name+':/mnt/web')
 docker('cp',str(ROOT/'publish/console')+'/.',name+':/mnt/console')
 for service in ['api','eventing','worker','billing']:
  docker('exec',name,'mkdir','-p','/mnt/web/_services/'+service)
  docker('cp',str(ROOT/'publish'/service)+'/.',name+':/mnt/web/_services/'+service)
 docker('cp',str(ROOT/'private/ResgridConfig.json'),name+':/mnt/config/ResgridConfig.json')
 docker('cp',str(ROOT/'nginx.conf'),name+':/mnt/nginx/default.conf')
 for file in ['api-tls.pfx','academy-ca.crt','EventingConfig.json']:
  docker('cp',str(ROOT/'private'/file),name+':/mnt/config/'+file)
 docker('cp',str(ROOT/'private/loopback.conf'),name+':/mnt/config/loopback.conf')
 print('Staged only Academy named volumes. Start applications after staging.')
def build():
 (ROOT/'logs').mkdir(exist_ok=True)
 for component,project in PROJECTS.items():
  with (ROOT/'logs'/('build-'+component+'.log')).open('w') as log:
   run(['dotnet','publish',str(REPO/project),'-c','Docker','--no-restore','--disable-build-servers','-m:1','-p:UseSharedCompilation=false','-p:SKIP_LIBMAN_RESTORE=1','-p:EnableDefaultCompressionFormats=false','-p:EnableDefaultCompressedItems=false','-p:DisableBuildCompression=true','-o',str(ROOT/'publish'/component)],stdout=log,stderr=subprocess.STDOUT)
  print('Published '+component,flush=True)
 # Restore only the two files pinned by this checkout's libman.json.
 import tarfile
 with tarfile.open(ROOT/'vendor/deltablot-dropzone-7.3.1.tgz') as archive:
  for name in ['dropzone.css','min/dropzone.min.js']:
   target=ROOT/'publish/web/wwwroot/lib/deltablot/dropzone/dist'/name
   target.parent.mkdir(parents=True,exist_ok=True)
   target.write_bytes(archive.extractfile('package/dist/'+name).read())
 target=ROOT/'publish/billing';target.mkdir(parents=True,exist_ok=True)
 shutil.copy2(ROOT/'billing_fixture.py',target/'billing_fixture.py')
 prepare()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['start','stop','status','health','build','stage','seed']);a=p.parse_args()
 if a.action=='start':compose('create',*SERVICES);start([STACK+'-'+s+'-1' for s in SERVICES]);health()
 elif a.action=='stop':compose('stop',*APPS)
 elif a.action=='status':docker('ps','-a','--filter','label=com.docker.compose.project='+STACK,'--format','{{.Names}} {{.Status}}')
 elif a.action=='health':health()
 elif a.action=='build':build()
 elif a.action=='stage':prepare();stage()
 elif a.action=='seed':
  run([sys.executable,str(ROOT/'seed.py')]);result=sql((ROOT/'private/seed.sql').read_text());print('Baseline seed applied only to resgrid_academy.')
if __name__=='__main__':main()
