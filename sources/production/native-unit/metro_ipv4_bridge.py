#!/usr/bin/env python3
"""Owned IPv4 loopback -> existing IPv6-only Metro, with stream hashes only.

No app API/database behavior, synthetic UI, auth/TLS change, cloud or body log.
It forwards real packager responses and retains only digest/size/type/timestamps.
An observed response is NOT proof its JS executed. No runtime bundle is saved.
"""
from datetime import datetime, timezone
import hashlib
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import select
import socket
import threading
import uuid

BASE = Path('/Users/shawn/Documents/dev/Core/artifacts/academy-expansion-20261025/native-unit-20261028')
RECEIPTS = BASE / 'metro-stream-receipts'
LOCK = threading.Lock()


def now(): return datetime.now(timezone.utc).isoformat()


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    def log_message(self, *_): pass
    def do_GET(self): self.forward()
    def do_HEAD(self): self.forward()
    def do_POST(self): self.forward()
    def forward(self):
        if not self.path.startswith('/') or '\r' in self.path or '\n' in self.path:
            self.send_error(400); return
        if self.headers.get('Upgrade', '').lower() == 'websocket':
            self.websocket(); return
        connection = http.client.HTTPConnection('::1', 19113, timeout=120)
        started = now(); count = 0; digest = hashlib.sha256(); completed = False; status = None; content_type = ''; encoding = ''; failure = None
        try:
            headers = {key: value for key, value in self.headers.items() if key.lower() not in ('connection', 'proxy-connection', 'transfer-encoding')}
            # Normal HTTP negotiation; response body identity is unchanged JS/asset bytes.
            headers['Accept-Encoding'] = 'identity'
            length = int(self.headers.get('Content-Length', '0'))
            if length > 16 * 1024 * 1024: self.send_error(413); return
            body = self.rfile.read(length) if length else None
            connection.request(self.command, self.path, body=body, headers=headers)
            response = connection.getresponse(); status = response.status; content_type = response.getheader('Content-Type', ''); encoding = response.getheader('Content-Encoding', 'identity')
            self.send_response(status)
            for key, value in response.getheaders():
                if key.lower() not in ('connection', 'transfer-encoding', 'server', 'date'): self.send_header(key, value)
            self.send_header('Connection', 'close'); self.end_headers()
            if self.command != 'HEAD':
                while True:
                    data = response.read(64 * 1024)
                    if not data: break
                    digest.update(data); count += len(data); self.wfile.write(data)
            completed = True
        except Exception as error:
            failure = type(error).__name__
        finally:
            self.close_connection = True; connection.close()
            category = 'entry_bundle' if '/entry.bundle' in self.path else 'lazy_or_other_bundle' if '.bundle' in self.path else 'manifest_or_asset'
            receipt = {'kind': 'actual_local_metro_response_stream', 'started_at': started, 'finished_at': now(), 'method': self.command,
                       'request_target_sha256': hashlib.sha256(self.path.encode()).hexdigest(), 'resource_category': category, 'status': status,
                       'content_type': content_type, 'content_encoding': encoding, 'hash_stage': 'decoded_response_body' if encoding == 'identity' else 'encoded_response_body', 'stream_sha256': digest.hexdigest(),
                       'byte_length': count, 'completed': completed, 'failure_type': failure, 'body_saved': False, 'body_or_query_logged': False,
                       'source_kind': 'real_metro_forwarded_without_content_rewrite', 'source': 'IPv6-only owned Metro19113',
                       'client_identity': 'not_authenticated_by_transport', 'executed_or_loaded_identity_proven': False,
                       'coverage_limits': 'One observed HTTP response only; lazy chunks/actual foreground execution need separate correlation/review.'}
            RECEIPTS.mkdir(exist_ok=True)
            with LOCK: (RECEIPTS / (str(uuid.uuid4()) + '.json')).write_text(json.dumps(receipt, indent=2)+'\n')

    def websocket(self):
        # Real native devtools require normal Upgrade framing. Relay bytes only:
        # no decoding/inspection/storage/logging of headers, frames or app data.
        started = now(); counters = [0, 0]; failure = None
        upstream = None
        try:
            upstream = socket.create_connection(('::1', 19113), timeout=120)
            upstream.settimeout(None)
            headers = ''.join(key + ': ' + value + '\r\n' for key, value in self.headers.items() if key.lower() != 'proxy-connection')
            upstream.sendall((self.command + ' ' + self.path + ' ' + self.request_version + '\r\n' + headers + '\r\n').encode('latin-1'))
            peers = (self.connection, upstream)
            while True:
                ready, _, _ = select.select(peers, [], [], 1)
                if not ready: continue
                for peer in ready:
                    data = peer.recv(64 * 1024)
                    if not data: return
                    index = 0 if peer is self.connection else 1
                    peers[1 - index].sendall(data); counters[index] += len(data)
        except Exception as error:
            failure = type(error).__name__
        finally:
            if upstream is not None: upstream.close()
            self.close_connection = True
            receipt = {'kind': 'normal_local_metro_websocket_transport', 'started_at': started, 'finished_at': now(),
                       'bytes_client_to_metro': counters[0], 'bytes_metro_to_client': counters[1], 'failure_type': failure,
                       'headers_or_frames_retained': False, 'request_query_logged': False, 'app_data_decoded': False,
                       'executed_or_loaded_identity_proven': False}
            RECEIPTS.mkdir(exist_ok=True)
            with LOCK: (RECEIPTS / (str(uuid.uuid4()) + '.json')).write_text(json.dumps(receipt, indent=2)+'\n')


def main():
    session = json.loads((BASE / 'session.json').read_text())
    if session.get('owner') != 'academy_training' or not session.get('dedicated') or session.get('user_session_reused') is not False:
        raise ValueError('Owned session guard failed')
    server = ThreadingHTTPServer(('127.0.0.1', 19113), Handler)
    print('Owned IPv4 Metro bridge127.0.0.1:19113 -> [::1]:19113; response hashes only.', flush=True)
    server.serve_forever()


if __name__ == '__main__': main()
