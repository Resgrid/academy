"""Temporarily allow normal invitation delivery inside the isolated Academy stack.

This affects only a restarted web process. The worker, API and eventing process
are left running with their existing suppression setting. Restore immediately
after the normal UI invitation retry. Private full configurations stay ignored.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,time,urllib.request

DEMO=Path(__file__).resolve().parents[1]
PRIVATE=DEMO/'private'
STACK='resgrid-academy-oct25'
KEY='SystemBehaviorConfig.DoNotBroadcast'
CONFIG=PRIVATE/'ResgridConfig.json'
BACKUP=PRIVATE/'ResgridConfig.before-invitation-20261102.private.json'
STATE=PRIVATE/'invitation-delivery-20261102.private.json'

def docker(*args):
    return subprocess.run(['docker',*args],check=True,capture_output=True,text=True).stdout.strip()

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def ensure_mailpit_smtp_compat():
    # The pinned Core SMTP sender currently uses SmtpClient's default port25.
    # Forward only within the existing isolated Mailpit container. Its inbox and
    # the normal1025listener stay intact; no host port is opened or image fetched.
    container=STACK+'-mail-1'
    probe=['docker','exec',container,'/bin/busybox','nc','-z','-w','1','127.0.0.1','25']
    if subprocess.run(probe,capture_output=True).returncode==0:return
    docker('exec','-d',container,'/bin/busybox','nc','-lk','-p','25','-e','/bin/busybox','nc','127.0.0.1','1025')
    for _ in range(5):
        if subprocess.run(probe,capture_output=True).returncode==0:return
        time.sleep(.2)
    raise RuntimeError('Mailpit SMTP compatibility listener did not start.')

def stage_and_restart():
    helper=STACK+'-asset-stage'
    mounts=json.loads(docker('inspect',helper,'--format','{{json .Mounts}}'))
    assert any(m.get('Name')==STACK+'_config' and m.get('Destination')=='/mnt/config' and m.get('RW') is True for m in mounts)
    docker('start',helper)
    docker('cp',str(CONFIG),helper+':/mnt/config/ResgridConfig.json')
    docker('restart',STACK+'-web-1')
    deadline=time.monotonic()+45
    while time.monotonic()<deadline:
        try:
            # Readiness only: inspect the status, never consume account/page data.
            with urllib.request.urlopen('http://127.0.0.1:18967/Account/LogOn',timeout=2) as response:
                if response.status==200:return
        except (OSError,urllib.error.URLError):
            pass
        time.sleep(1)
    raise RuntimeError('The isolated training web process did not become ready.')

def main(action):
    assert docker('network','inspect',STACK+'_training','--format','{{.Internal}}')=='true'
    current=json.loads(CONFIG.read_text())
    assert current['OutboundEmailServerConfig.Host']=='mail'
    assert str(current['OutboundEmailServerConfig.Port'])=='1025'
    assert str(current['OutboundEmailServerConfig.EnableSsl']).lower()=='false'
    assert str(current['SystemBehaviorConfig.OutboundEmailType'])=='1'
    if action=='arm':
        assert str(current[KEY]).lower()=='true'
        ensure_mailpit_smtp_compat()
        if BACKUP.exists() or STATE.exists():
            assert BACKUP.exists() and STATE.exists()
            prior=json.loads(STATE.read_text())
            assert prior['restored'] and sha(CONFIG)==sha(BACKUP)==prior['original_sha256'],'Restore or inspect the earlier exercise first.'
        else:
            BACKUP.write_bytes(CONFIG.read_bytes())
        current[KEY]='false'
        CONFIG.write_text(json.dumps(current,indent=2)+'\n')
        STATE.write_text(json.dumps({'original_sha256':sha(BACKUP),'temporary_sha256':sha(CONFIG),'restored':False},indent=2)+'\n')
        try:stage_and_restart()
        except BaseException:
            CONFIG.write_bytes(BACKUP.read_bytes())
            stage_and_restart()
            raise
        print('Training web delivery enabled for the approved local invitation. Restore after the normal UI retry.')
    else:
        state=json.loads(STATE.read_text())
        assert sha(BACKUP)==state['original_sha256']
        assert sha(CONFIG) in [state['temporary_sha256'],state['original_sha256']],'Configuration changed; inspect before restoring.'
        CONFIG.write_bytes(BACKUP.read_bytes())
        stage_and_restart()
        state['restored']=True
        STATE.write_text(json.dumps(state,indent=2)+'\n')
        print('Original suppressed web configuration restored byte-for-byte. Other services were not restarted.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['arm','restore']);main(p.parse_args().action)
