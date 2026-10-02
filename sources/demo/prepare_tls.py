"""Generate dedicated container TLS material; never installs host trust or disables verification."""
import base64,json,pathlib,shutil,subprocess
ROOT=pathlib.Path(__file__).resolve().parent;P=ROOT/'private';P.mkdir(exist_ok=True)
openssl=shutil.which('openssl') or '/usr/bin/openssl'
def run(*args):subprocess.run([openssl,*args],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
if not (P/'api-tls.pfx').exists():
 run('req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(P/'academy-ca.key'),'-out',str(P/'academy-ca.crt'),'-days','365','-subj','/CN=Resgrid Academy Container CA')
 run('req','-newkey','rsa:2048','-nodes','-keyout',str(P/'api-tls.key'),'-out',str(P/'api-tls.csr'),'-subj','/CN=api')
 (P/'api-tls.ext').write_text('subjectAltName=DNS:api\nbasicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth\n')
 run('x509','-req','-in',str(P/'api-tls.csr'),'-CA',str(P/'academy-ca.crt'),'-CAkey',str(P/'academy-ca.key'),'-CAcreateserial','-out',str(P/'api-tls.crt'),'-days','365','-extfile',str(P/'api-tls.ext'))
 run('pkcs12','-export','-out',str(P/'api-tls.pfx'),'-inkey',str(P/'api-tls.key'),'-in',str(P/'api-tls.crt'),'-certfile',str(P/'academy-ca.crt'),'-passout','pass:')
credentials_path=P/'credentials.json'
credentials=json.loads(credentials_path.read_text())
for kind, usage in [('encryption','keyEncipherment'),('signing','digitalSignature')]:
 key='oidc_'+kind+'_cert'
 if key not in credentials:
  prefix=P/('oidc-'+kind)
  run('req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(prefix.with_suffix('.key')),'-out',str(prefix.with_suffix('.crt')),'-days','1825','-subj','/CN=Resgrid Academy '+kind,'-addext','keyUsage=critical,'+usage)
  run('pkcs12','-export','-out',str(prefix.with_suffix('.pfx')),'-inkey',str(prefix.with_suffix('.key')),'-in',str(prefix.with_suffix('.crt')),'-passout','pass:')
  credentials[key]=base64.b64encode(prefix.with_suffix('.pfx').read_bytes()).decode('ascii')
credentials_path.write_text(json.dumps(credentials,indent=2)+'\n')
credentials_path.chmod(0o600)
for file in P.glob('*.key'):file.chmod(0o600)
(P/'api-tls.pfx').chmod(0o644)
print('Dedicated Academy container TLS certificate ready; host trust unchanged.')
