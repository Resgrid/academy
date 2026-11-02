#!/usr/bin/env python3
"""Create the isolated import bucket using stdlib SigV4; never print credentials.

Run inside the training network with /config/ResgridConfig.json mounted.
"""
import datetime
import hashlib
import hmac
import json
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def signature_request(config, now):
    endpoint = config['ImportConfig.S3Endpoint'].rstrip('/')
    if endpoint != 'http://object-store:9000':
        raise ValueError('Only the isolated object-store endpoint is supported.')
    access = config['ImportConfig.S3AccessKey']
    secret = config['ImportConfig.S3SecretKey']
    stamp, day = now.strftime('%Y%m%dT%H%M%SZ'), now.strftime('%Y%m%d')
    body_hash = hashlib.sha256(b'').hexdigest()
    host, path = urlsplit(endpoint).netloc, '/resgrid-imports'
    headers = {'Host': host, 'x-amz-content-sha256': body_hash, 'x-amz-date': stamp}
    signed = 'host;x-amz-content-sha256;x-amz-date'
    canonical_headers = ''.join(k.lower() + ':' + headers[k] + '\n' for k in headers)
    canonical = '\n'.join(['PUT', path, '', canonical_headers, signed, body_hash])
    scope = day + '/us-east-1/s3/aws4_request'
    message = '\n'.join(['AWS4-HMAC-SHA256', stamp, scope, hashlib.sha256(canonical.encode()).hexdigest()])
    key = ('AWS4' + secret).encode()
    for part in (day, 'us-east-1', 's3', 'aws4_request'):
        key = hmac.new(key, part.encode(), hashlib.sha256).digest()
    digest = hmac.new(key, message.encode(), hashlib.sha256).hexdigest()
    headers['Authorization'] = 'AWS4-HMAC-SHA256 Credential=' + access + '/' + scope + ', SignedHeaders=' + signed + ', Signature=' + digest
    return Request(endpoint + path, data=b'', method='PUT', headers=headers)


def main():
    config = json.loads(Path('/config/ResgridConfig.json').read_text())
    for attempt in range(30):
        try:
            with urlopen(signature_request(config, datetime.datetime.now(datetime.timezone.utc)), timeout=5) as response:
                if response.status not in (200, 201, 204):
                    raise ValueError('Unexpected object-store status.')
            print('Isolated import bucket ready.')
            return
        except HTTPError as exc:
            # An existing bucket is safe only when it belongs to this configured account.
            if exc.code == 409 and b'BucketAlreadyOwnedByYou' in exc.read(4096):
                print('Isolated import bucket already exists; objects preserved.')
                return
            raise RuntimeError('Object-store initialization refused: HTTP ' + str(exc.code)) from None
        except URLError:
            if attempt == 29:
                raise RuntimeError('The isolated object-store did not become ready.') from None
            time.sleep(1)


if __name__ == '__main__':
    main()
