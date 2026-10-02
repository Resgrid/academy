#!/usr/bin/env python3
"""Prepare only the isolated Academy stack's local configuration."""
import json, secrets
from pathlib import Path
from settings import load

ROOT = Path(__file__).resolve().parent
private = ROOT / 'private'
private.mkdir(exist_ok=True, mode=0o700)
private.chmod(0o700)
profile = load()
(private / 'stack.json').write_text(json.dumps(profile, indent=2) + '\n')
(private / 'stack.json').chmod(0o600)
base_url = 'http://127.0.0.1:' + str(profile['ports']['web'])
credentials_path = private / 'credentials.json'
if credentials_path.exists():
    credentials = json.loads(credentials_path.read_text())
else:
    credentials = {'database': secrets.token_hex(20), 'rabbit': secrets.token_hex(20),
                   'demo_password': 'Training51!' + secrets.token_hex(4),
                   'encryption': secrets.token_hex(16), 'salt': secrets.token_hex(16),
                   'jwt': secrets.token_hex(32), 'links': secrets.token_hex(24)}
    credentials_path.write_text(json.dumps(credentials, indent=2))
    credentials_path.chmod(0o600)
env = {'ACADEMY_STACK_NAME': profile['name'], 'ACADEMY_DB_PASSWORD': credentials['database'], 'ACADEMY_RABBIT_PASSWORD': credentials['rabbit']}
env.update({'ACADEMY_' + key.upper() + '_PORT': str(port) for key, port in profile['ports'].items()})
(ROOT / '.env').write_text(''.join(key + '=' + value + '\n' for key, value in env.items()))
(ROOT / '.env').chmod(0o600)
connection = f"Host=postgres;Port=5432;Database=resgrid_academy;Username=academy;Password={credentials['database']}"
config = {
    'DataConfig.DatabaseType': '1', 'DataConfig.DocDatabaseType': '1',
    'DataConfig.ConnectionString': connection, 'DataConfig.CoreConnectionString': connection,
    'DataConfig.DocumentConnectionString': connection.replace('Database=resgrid_academy;', 'Database=resgrid_academy_docs;'),
    'CacheConfig.RedisConnectionString': 'redis:6379,abortConnect=false,syncTimeout=10000',
    'SystemBehaviorConfig.Environment': '3', 'SystemBehaviorConfig.IsAzure': 'false',
    'SystemBehaviorConfig.ResgridBaseUrl': base_url,
    'SystemBehaviorConfig.ResgridApiBaseUrl': base_url,
    'SystemBehaviorConfig.ResgridEventingBaseUrl': base_url,
    'SystemBehaviorConfig.CacheEnabled': 'false',
    'SystemBehaviorConfig.DoNotBroadcast': 'true',
    'SystemBehaviorConfig.ServiceBusType': '1',
    'SystemBehaviorConfig.OutboundEmailType': '1',
    'SystemBehaviorConfig.LocationName': 'Academy Training',
    'SystemBehaviorConfig.LoginPageNotice': 'LOCAL TRAINING SYSTEM — fictional Firehouse 51 demo data',
    'SystemBehaviorConfig.ApiTokenEncryptionPassphrase': credentials['links'],
    'SystemBehaviorConfig.ExternalLinkUrlParamPassphrase': credentials['links'],
    'SystemBehaviorConfig.ExternalAudioUrlParamPasshprase': credentials['links'],
    'ServiceBusConfig.RabbitHostname': 'rabbit',
    'ServiceBusConfig.RabbitUsername': 'academy',
    'ServiceBusConfig.RabbbitPassword': credentials['rabbit'],
    'ServiceBusConfig.RabbbitExchange': '',
    'OutboundEmailServerConfig.Host': 'mail', 'OutboundEmailServerConfig.Port': '1025',
    'OutboundEmailServerConfig.EnableSsl': 'false',
    'OutboundEmailServerConfig.FromMail': 'training@firehouse51.example',
    'OutboundEmailServerConfig.ToMail': 'admin@firehouse51.example',
    'SecurityConfig.EncryptionKey': credentials['encryption'],
    'SecurityConfig.EncryptionSaltValue': credentials['salt'],
    'JwtConfig.Key': credentials['jwt'],
    'JwtConfig.EventsClientSecret': credentials['jwt'],
    'FeatureFlagsConfig.TrackEvaluations': 'false',
    'OidcConfig.DatabaseType': '1',
    'OidcConfig.ConnectionString': connection.replace('Database=resgrid_academy;', 'Database=resgrid_academy_oidc;'),
    'ApiConfig.CorsAllowedOrigins': base_url + ',http://localhost:' + str(profile['ports']['web']),
    'SystemBehaviorConfig.BillingApiBaseUrl': 'http://billing:8090',
    'ApiConfig.BackendInternalApikey': credentials['jwt'],
    'WorkerConfig.DatabaseType': '1',
    'WorkerConfig.WorkerDbConnectionString': connection.replace('Database=resgrid_academy;', 'Database=resgrid_academy_workers;'),
    'WorkerConfig.PayloadKey': credentials['encryption'],
}
if 'oidc_encryption_cert' in credentials:
    config['OidcConfig.EncryptionCert'] = credentials['oidc_encryption_cert']
    config['OidcConfig.SigningCert'] = credentials['oidc_signing_cert']
(private / 'ResgridConfig.json').write_text(json.dumps(config, indent=2))
# Container process needs to read this mounted file; only this isolated config is mounted.
(private / 'ResgridConfig.json').chmod(0o644)
eventing_config=dict(config)
eventing_config['SystemBehaviorConfig.ResgridApiBaseUrl']='https://api:8443'
(private / 'EventingConfig.json').write_text(json.dumps(eventing_config,indent=2))
(private / 'EventingConfig.json').chmod(0o644)
for component in ('web', 'console', 'api', 'eventing', 'worker'):
    output = ROOT / 'publish' / component
    if output.exists():
        (output / 'appsettings.json').write_text(json.dumps({
            'AppOptions': {'ConfigPath': '/config/ResgridConfig.json'},
            'Logging': {'LogLevel': {'Default': 'Warning', 'Microsoft.Hosting.Lifetime': 'Information'}},
            'AllowedHosts': '*'
        }, indent=2))
print('Prepared dedicated Academy configuration; credentials kept in private/credentials.json.')

(private / 'loopback.conf').write_text((ROOT / 'loopback.conf').read_text().replace('127.0.0.1:18767', '127.0.0.1:' + str(profile['ports']['web'])))
